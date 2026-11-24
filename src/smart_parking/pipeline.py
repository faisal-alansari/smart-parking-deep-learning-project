"""The full system on new inputs: photos, videos and typed owner commands (step 5).

`Pipeline` loads Models A, B and C once and times every stage. Two uses:

`just run-folder <dir>`: every input in a folder, in time order. The folder holds
- `bays.yaml`: `boxes: {left: [x0, y0, x1, y1], right: [...]}` (fractions of the frame),
  drawn once for the camera, like the night photo set;
- photos (.jpg, .jpeg, .png, .heic; time from EXIF, else the file time);
- videos (.mov, .mp4; one frame every `--every` seconds; start time from the file);
- `commands.txt`: one owner command per line, `2026-11-22 09:05 | allow car 12345 until 6 pm`.
Each proposed permit change is shown to the owner, who answers y/n in the terminal
(`--yes` accepts all, for unattended runs). Results go to outputs/loop/local/runs/<dir>/
(local only: they show plates): every decision, a timeline per video with one decision per
car's stay (`smart_parking.stays`), and the time per stage.

`just video-night-1`: the owner's night video against its truth (configs/local_video_night_1.yaml).
"""

import argparse
import json
import subprocess
import tempfile
import time
from collections import defaultdict
from collections.abc import Iterator
from datetime import datetime, timedelta
from pathlib import Path

import numpy as np
import pandas as pd
import yaml
from loguru import logger
from PIL import Image, ImageOps

from smart_parking.commands.owner import handle
from smart_parking.commands.schema import Action, ParsedCommand, PermitTable
from smart_parking.common.config import load_config
from smart_parking.common.log import setup_logging
from smart_parking.decision import gate_plate, occupancy_decision
from smart_parking.loop import TZ, _md, bay_status, true_status
from smart_parking.output import (
    GUIDANCE,
    BayDecision,
    CommandResult,
    InputProblem,
    RunResult,
    guidance,
)
from smart_parking.plates.reader import PlateRead, read_plates
from smart_parking.stays import SETTLE_READS, BayTracker, stay_status
from smart_parking.trust.ood import ViewGuard

PHOTOS = {".jpg", ".jpeg", ".png", ".heic"}
VIDEOS = {".mov", ".mp4", ".m4v"}
RUNS = Path("outputs/runs")
STAGES = {
    "V": "camera check (one frame)",
    "A": "A occupancy (one frame, both bays)",
    "B": "B plate read (one occupied bay)",
    "T": "permit table check (one bay)",
    "C": "C command (one command)",
}


class Pipeline:
    """Models A, B and C loaded once; `times` collects milliseconds per stage."""

    def __init__(self, commands: bool = True, deploy: str | None = None) -> None:
        from smart_parking.occupancy import local_pilot as lp  # loads YOLO
        from smart_parking.occupancy.train import load_checkpoint, pick_device

        project = load_config()
        self.lp, self.size, self.device = lp, project.occupancy.input_size, pick_device()
        occ = project.occupancy
        self.deploy = deploy or occ.deploy
        self.seeds = [
            load_checkpoint(occ.checkpoint_dir / f"{self.deploy}_s{s}.pt", self.device)
            for s in occ.seeds
        ]
        plates = project.plates
        run = plates.run_dir / f"final_s{lp.PLATE_SEED}" / "summary.json"
        summary = json.loads(run.read_text())
        self.yolo = lp.YOLO(str(plates.checkpoint_dir / f"final_s{lp.PLATE_SEED}.pt"))
        self.imgsz, self.plate_threshold = summary["imgsz"], summary["threshold"]
        self.decide = None
        if commands:
            from smart_parking.commands.score import PARSERS

            self.decide = PARSERS["tiered"].load(project.commands).decide
        self.decision_cfg = project.decision
        if self.deploy != "adapted":  # the cost threshold was chosen for the adapted model
            self.decision_cfg = self.decision_cfg.model_copy(update={"occupancy_threshold": 0.5})
        self.times: dict[str, list[float]] = defaultdict(list)

    def _timed(self, stage: str, fn, *args):  # noqa: ANN001, ANN202
        start = time.perf_counter()
        out = fn(*args)
        self.times[STAGES[stage]].append((time.perf_counter() - start) * 1000)
        return out

    @staticmethod
    def _px(im: Image.Image, box: list[float]) -> tuple[int, int, int, int]:
        w, h = im.size
        return round(box[0] * w), round(box[1] * h), round(box[2] * w), round(box[3] * h)

    def occupancy(self, im: Image.Image, boxes: dict[str, list[float]]) -> dict[str, tuple]:
        """Model A: (occupied, unsure, mean probability) per bay, at the cost-chosen threshold."""
        from smart_parking.occupancy.train import predict, to_tensor

        crops = [
            np.asarray(im.crop(self._px(im, b)).resize((self.size, self.size), Image.BILINEAR))
            for b in boxes.values()
        ]
        x = to_tensor(np.stack(crops), self.device)
        probs = [predict(m, x, mean, std) for m, mean, std, _ in self.seeds]
        p, occupied, unsure = occupancy_decision(probs, self.decision_cfg)
        return {
            bay: (bool(o), bool(u), float(q))
            for bay, o, u, q in zip(boxes, occupied, unsure, p, strict=True)
        }

    def plate(self, im: Image.Image, box: list[float]) -> PlateRead | None:
        """Model B in the bay area, then the calibrated confidence gate."""
        return gate_plate(self.plate_raw(im, box), self.decision_cfg)

    def plate_raw(self, im: Image.Image, box: list[float]) -> PlateRead | None:
        """Model B in the bay area, as in the local photo checks (raw confidence, no gate)."""
        lp, (w, h) = self.lp, im.size
        bay = tuple(float(v) for v in self._px(im, box))
        area = lp.search_area(bay, w, h)
        reads = read_plates(lp._detect(self.yolo, im.crop(area), self.imgsz), self.plate_threshold)
        local = (bay[0] - area[0], bay[1] - area[1], bay[2] - area[0], bay[3] - area[1])
        return lp._check_size(lp._pick(reads, local), bay[2] - bay[0])

    def frame(
        self,
        im: Image.Image,
        boxes: dict,
        at: datetime,
        table: PermitTable,
        guard: ViewGuard | None = None,
        cached: dict[str, PlateRead] | None = None,
    ) -> list[dict]:
        """One photo or video frame: a status for each bay. A frame that does not look like this
        camera (`guard`) is not judged: both bays go to a person with the reason. A bay in
        `cached` reuses that settled plate read instead of running Model B again."""
        cached = cached or {}
        if guard is not None and (reason := self._timed("V", guard.check, im)):
            logger.bind(reason=reason).info("Camera check: asking a person ({})", reason)
            return [
                {
                    "bay": bay,
                    "occupied": -1,
                    "occupancy_p": None,
                    "status": "NEEDS_REVIEW",
                    "reason": reason,
                    "plate": "",
                    "plate_decision": "",
                    "read": None,
                }
                for bay in boxes
            ]
        occupancy = self._timed("A", self.occupancy, im, boxes)
        rows = []
        for bay, box in boxes.items():
            occupied, unsure, prob = occupancy[bay]
            if occupied and bay in cached:
                read = cached[bay]  # the stay's plate is settled: no need to read it again
            else:
                read = self._timed("B", self.plate, im, box) if occupied else None
            status = self._timed("T", bay_status, occupied, read, at, table)
            reason = "occupancy_unsure" if unsure else (read.reason or "") if read else ""
            if unsure:
                status = "NEEDS_REVIEW"  # Model A is unsure: a person looks
            elif status == "NEEDS_REVIEW" and not reason:
                reason = "no_plate_found"
            rows.append(
                {
                    "bay": bay,
                    "occupied": int(occupied),
                    "occupancy_p": round(prob, 3),
                    "status": status,
                    "reason": reason,
                    "plate": f"{read.emirate} {read.text}" if read else "",
                    "plate_decision": f"{read.decision} {read.reason or ''}".strip()
                    if read
                    else "",
                    "read": read,  # Model B's read itself (dropped before saving)
                }
            )
        return rows

    def command(self, text: str, now: datetime, table: PermitTable, review, feedback: Path) -> str:  # noqa: ANN001
        return self._timed("C", handle, text, now, self.decide, table, review, feedback)

    def timing(self) -> pd.DataFrame:
        rows = [
            {
                "stage": k,
                "calls": len(v),
                "mean ms": round(float(np.mean(v)), 1),
                "p95 ms": round(float(np.percentile(v, 95)), 1),
            }
            for k, v in self.times.items()
        ]
        return pd.DataFrame(rows)


# --- Inputs ------------------------------------------------------------------------------


def open_photo(path: Path) -> Image.Image:
    if path.suffix.lower() == ".heic":  # macOS `sips` converts iPhone photos
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "photo.jpg"
            subprocess.run(
                ["sips", "-s", "format", "jpeg", str(path), "--out", str(out)],
                check=True,
                capture_output=True,
            )
            return ImageOps.exif_transpose(Image.open(out)).convert("RGB")
    return ImageOps.exif_transpose(Image.open(path)).convert("RGB")


def photo_taken(path: Path, im: Image.Image) -> datetime:
    stamp = im.getexif().get(306)
    if stamp:
        return datetime.strptime(stamp, "%Y:%m:%d %H:%M:%S").replace(tzinfo=TZ)
    return datetime.fromtimestamp(path.stat().st_mtime, TZ)


def video_start(path: Path) -> datetime:
    """Recording start: the file's creation date (macOS Spotlight), else its file time."""
    out = subprocess.run(
        ["mdls", "-raw", "-name", "kMDItemContentCreationDate", str(path)],
        capture_output=True,
        text=True,
        check=False,
    ).stdout
    try:
        return datetime.strptime(out.strip(), "%Y-%m-%d %H:%M:%S %z").astimezone(TZ)
    except ValueError:
        return datetime.fromtimestamp(path.stat().st_mtime, TZ)


def video_frames(path: Path, every: float) -> Iterator[tuple[float, Image.Image]]:
    """(seconds from the start, frame) every `every` seconds."""
    import cv2

    cap = cv2.VideoCapture(str(path))
    length = cap.get(cv2.CAP_PROP_FRAME_COUNT) / cap.get(cv2.CAP_PROP_FPS)
    t = 0.0
    while t < length:
        cap.set(cv2.CAP_PROP_POS_MSEC, t * 1000)
        ok, frame = cap.read()
        if not ok:
            break
        yield t, Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        t += every
    cap.release()


def timeline(rows: pd.DataFrame) -> pd.DataFrame:
    """Runs of the same status per bay: when each one started and ended."""
    out = []
    for bay, g in rows.groupby("bay", sort=False):
        runs = (g["status"] != g["status"].shift()).cumsum()
        for _, r in g.groupby(runs):
            out.append(
                {
                    "bay": bay,
                    "from": r["clock"].iloc[0],
                    "to": r["clock"].iloc[-1],
                    "frames": len(r),
                    "status": r["status"].iloc[0],
                }
            )
    return pd.DataFrame(out)


def clock(seconds: float) -> str:
    return f"{int(seconds // 60)}:{int(seconds % 60):02d}"


# --- Folder of new inputs ------------------------------------------------------------------


def ask_owner(question: str, change: ParsedCommand) -> ParsedCommand | None:
    answer = input(f"{question} [y/n] ").strip().lower()
    return change if answer.startswith("y") else None


def _boxes_ok(boxes: object) -> bool:
    try:
        return all(0 <= x0 < x1 <= 1 and 0 <= y0 < y1 <= 1 for x0, y0, x1, y1 in boxes.values())
    except AttributeError, TypeError, ValueError:
        return False


def _setup(folder: Path, problems: list[InputProblem]) -> tuple[dict, str, str, Path | None]:
    """(bay boxes, camera description, occupancy model, snapshot file) for this folder.

    No bays.yaml: the owner's camera (its boxes and snapshot, the adapted model). With bays.yaml:
    a camera set up from that file, judged by the public-data model (the adapted one only knows
    the owner's camera) unless it says `model: adapted`; its snapshot is `snapshot:` or the first
    photo or video frame."""
    path = folder / "bays.yaml"
    if not path.exists():
        return {}, "the owner's camera (default boxes and snapshot)", "adapted", None
    try:
        cfg = yaml.safe_load(path.read_text()) or {}
        boxes = {k: [float(v) for v in b] for k, b in cfg["boxes"].items()}
        if not _boxes_ok(boxes):
            raise ValueError("box values out of range")
    except Exception as err:  # noqa: BLE001  (any broken file gets the same guidance)
        problems.append(
            InputProblem(
                source="bays.yaml",
                reason="bad_bays_file",
                detail=str(err),
                guidance=GUIDANCE["bad_bays_file"],
            )
        )
        return {}, "the owner's camera (bays.yaml could not be used)", "adapted", None
    model = "adapted" if cfg.get("model") == "adapted" else "final"
    snap = folder / cfg["snapshot"] if cfg.get("snapshot") else None
    return boxes, "set up from bays.yaml", model, snap


def _evidence(im: Image.Image, box: list[float], path: Path) -> str:
    """Save the frame with the bay outlined, as evidence for the owner."""
    from PIL import ImageDraw

    w, h = im.size
    shot = im.copy()
    ImageDraw.Draw(shot).rectangle(
        (box[0] * w, box[1] * h, box[2] * w, box[3] * h),
        outline=(255, 64, 0),
        width=max(4, w // 200),
    )
    shot.thumbnail((960, 960))
    path.parent.mkdir(parents=True, exist_ok=True)
    shot.save(path, quality=85)
    return str(path)


def _decision(
    source: str, at: datetime, r: dict, stay: str, clock_: str | None, evidence: str | None
) -> BayDecision:
    read = r["read"]
    status = r["status"]
    shown = stay if clock_ else status
    return BayDecision(
        source=source,
        time=at,
        clock=clock_,
        bay=r["bay"],
        status=status,
        stay_status=stay,
        occupied=None if r["occupied"] == -1 else bool(r["occupied"]),
        occupancy_confidence=r["occupancy_p"],
        plate=f"{read.emirate or ''} {read.text}".strip() if read else None,
        plate_confidence=round(read.confidence, 3) if read else None,
        reason=r["reason"] or None,
        guidance=guidance(shown, r["reason"] or None),
        evidence=evidence,
    )


def run_folder(
    folder: Path,
    every: float,
    yes: bool,
    out_root: Path = RUNS,
    table: PermitTable | None = None,
    pipelines: dict[str, Pipeline] | None = None,
) -> RunResult:
    """Every input in a folder, in time order. Never crashes on bad input: each problem is
    returned as a structured record with guidance. `table` starts from an existing permit table
    (the demo app's); `pipelines` reuses loaded models, keyed by occupancy model."""
    problems: list[InputProblem] = []
    if not folder.is_dir():
        problems.append(
            InputProblem(
                source=str(folder),
                reason="empty_folder",
                detail="not a folder",
                guidance=GUIDANCE["empty_folder"],
            )
        )
        return RunResult(folder=str(folder), camera="", occupancy_model="", problems=problems)
    boxes, camera, model, snap_path = _setup(folder, problems)
    events: list[tuple[datetime, str, object]] = []
    commands_file = folder / "commands.txt"
    if commands_file.exists():
        for n, line in enumerate(commands_file.read_text().splitlines(), 1):
            if not line.strip() or line.lstrip().startswith("#"):
                continue
            try:
                when, text = line.split("|", 1)
                at = datetime.fromisoformat(when.strip()).replace(tzinfo=TZ)
                events.append((at, "command", text.strip()))
            except ValueError as err:
                problems.append(
                    InputProblem(
                        source=f"commands.txt line {n}",
                        reason="bad_command_line",
                        detail=str(err),
                        guidance=GUIDANCE["bad_command_line"],
                    )
                )
    for path in sorted(folder.iterdir()):
        ext = path.suffix.lower()
        if (
            path.name in ("commands.txt", "bays.yaml")
            or path.name.startswith(".")
            or path == snap_path
        ):
            continue
        try:
            if ext in PHOTOS:
                events.append((photo_taken(path, open_photo(path)), "photo", path))
            elif ext in VIDEOS:
                if not next(video_frames(path, every), None):
                    raise ValueError("no frames")
                events.append((video_start(path), "video", path))
            else:
                problems.append(
                    InputProblem(
                        source=path.name,
                        reason="unsupported_file",
                        guidance=GUIDANCE["unsupported_file"],
                    )
                )
        except Exception as err:  # noqa: BLE001  (a broken file must not stop the run)
            problems.append(
                InputProblem(
                    source=path.name,
                    reason="unreadable_file",
                    detail=str(err),
                    guidance=GUIDANCE["unreadable_file"],
                )
            )
    if not events:
        problems.append(
            InputProblem(
                source=folder.name, reason="empty_folder", guidance=GUIDANCE["empty_folder"]
            )
        )
    events.sort(key=lambda e: e[0])
    result = RunResult(folder=str(folder), camera=camera, occupancy_model=model, problems=problems)
    if not events:
        return result
    needs_c = any(kind == "command" for _, kind, _ in events)
    if pipelines is not None and model in pipelines:
        pipe = pipelines[model]
    else:
        pipe = Pipeline(commands=needs_c or pipelines is not None, deploy=model)
        if pipelines is not None:
            pipelines[model] = pipe
    if not boxes:  # the owner's camera
        guard = ViewGuard.owner_camera()
        boxes = guard.boxes
    else:
        first = (
            open_photo(snap_path)
            if snap_path
            else next(
                (
                    open_photo(i) if k == "photo" else next(video_frames(i, every))[1]
                    for _, k, i in events
                    if k != "command"
                ),
                None,
            )
        )
        guard = ViewGuard.from_snapshot(first, boxes) if first is not None else None
    table, out = table if table is not None else PermitTable(), out_root / folder.name
    out.mkdir(parents=True, exist_ok=True)
    feedback = out / "feedback.jsonl"
    review = (lambda q, c: c) if yes else ask_owner
    for at, kind, item in events:
        if kind == "command":
            reply = pipe.command(str(item), at, table, review, feedback)
            result.commands.append(CommandResult(time=at, command=str(item), reply=reply))
            logger.bind(command=item).info("Reply: {}", reply)
        elif kind == "photo":
            im = open_photo(item)
            for r in pipe.frame(im, boxes, at, table, guard):
                ev = (
                    _evidence(im, boxes[r["bay"]], out / "evidence" / f"{item.stem}_{r['bay']}.jpg")
                    if r["status"] != "EMPTY"
                    else None
                )
                result.decisions.append(_decision(item.name, at, r, r["status"], None, ev))
        else:
            trackers = {bay: BayTracker(settle_after=SETTLE_READS) for bay in boxes}
            last_read: dict[str, PlateRead] = {}
            last_stay = {bay: "EMPTY" for bay in boxes}
            for t, im in video_frames(item, every):
                when = at + timedelta(seconds=t)
                cached = {
                    b: last_read[b]
                    for b, tr in trackers.items()
                    if tr.occupied and not tr.needs_read and b in last_read
                }
                for r in pipe.frame(im, boxes, when, table, guard, cached):
                    read = r["read"]
                    if read is not None and read.decision == "READ":
                        last_read[r["bay"]] = read
                    clear = read.text if read and read.decision == "READ" else None
                    occupied, plate = trackers[r["bay"]].update(r["occupied"] == 1, clear)
                    stay = stay_status(occupied, plate, when, table)
                    ev = None
                    if stay != last_stay[r["bay"]] and stay != "EMPTY":  # a notification
                        name = f"{item.stem}_{r['bay']}_{clock(t).replace(':', '-')}.jpg"
                        ev = _evidence(im, boxes[r["bay"]], out / "evidence" / name)
                        logger.bind(bay=r["bay"], status=stay).info("Notify owner at {}", clock(t))
                    last_stay[r["bay"]] = stay
                    result.decisions.append(_decision(item.name, when, r, stay, clock(t), ev))
    _write_run(result, out, pipe)
    return result


def _write_run(result: RunResult, out: Path, pipe: Pipeline) -> None:
    """decisions.jsonl (validated records), decisions.csv and a readable summary.md."""
    (out / "result.json").write_text(result.model_dump_json(indent=2))
    rows = [d.model_dump(mode="json") for d in result.decisions]
    decisions = pd.DataFrame(rows)
    if rows:
        decisions.to_csv(out / "decisions.csv", index=False)
    parts = [
        f"# Run on folder `{result.folder}`\n",
        f"Camera: {result.camera}; occupancy model: {result.occupancy_model}. "
        f"{len(result.commands)} commands, {len(rows)} bay decisions, "
        f"{len(result.problems)} input problems. Everything: `result.json`.\n",
    ]
    if result.problems:
        parts += [
            "## Inputs that could not be used\n",
            _md(pd.DataFrame([p.model_dump() for p in result.problems])) + "\n",
        ]
    if result.commands:
        parts += [
            "## Commands\n",
            _md(pd.DataFrame([c.model_dump() for c in result.commands])) + "\n",
        ]
    if rows:
        counts = (
            decisions.groupby(["source", "bay"])["stay_status"].value_counts().unstack(fill_value=0)
        )
        parts += ["## Answers (one per stay for videos)\n", _md(counts.reset_index()) + "\n"]
        for src, g in decisions[decisions["clock"].notna()].groupby("source"):
            per_stay = timeline(g.assign(status=g["stay_status"]))
            parts += [f"## Timeline: {src} (one decision per stay)\n", _md(per_stay) + "\n"]
        need = decisions[decisions["evidence"].notna()]
        if len(need):
            parts += [
                "## Evidence frames (each notification)\n",
                _md(
                    need[
                        ["source", "clock", "bay", "stay_status", "plate", "reason", "evidence"]
                    ].fillna("")
                )
                + "\n",
            ]
    parts += ["## Time per stage\n", _md(pipe.timing()) + "\n"]
    (out / "summary.md").write_text("\n".join(parts))


# --- The owner's night video against its truth ----------------------------------------------


def in_any(t: float, spans: list[list[float]]) -> bool:
    return any(a <= t < b for a, b in spans)


def video_truth(cfg: dict, t: float) -> dict[str, str]:
    """True plate per occupied bay at second t ('' = empty). A car across both bays counts
    in both."""
    truth = {bay: "" for bay in cfg["boxes"]}
    for car in cfg["cars"]:
        if car["from"] <= t < car["to"]:
            for bay in truth if car["bay"] == "both" else [car["bay"]]:
                truth[bay] = car["plate"]
    return truth


def video_eval(cfg: dict) -> None:
    path = Path(cfg["video"])
    start = video_start(path)
    pipe = Pipeline(commands=False)
    guard = None  # the camera check, set up from the snapshot frame named in the config
    if "snapshot_s" in cfg:
        snap = next(im for t, im in video_frames(path, cfg["snapshot_s"]) if t >= cfg["snapshot_s"])
        guard = ViewGuard.from_snapshot(snap, cfg["boxes"])
    owner = PermitTable()  # the owner's own cars, on the permanent list
    for n in cfg["permanent"]:
        owner.apply(ParsedCommand(action=Action.ALLOW, number=n), confirm=lambda q: True)
    visitors = PermitTable()  # the same video with an empty table: the cars as visitors
    rows = []
    for t, im in video_frames(path, cfg["every_s"]):
        at = start + timedelta(seconds=t)
        truth = video_truth(cfg, t)
        for r in pipe.frame(im, cfg["boxes"], at, owner, guard):
            plate, read = truth[r["bay"]], r.pop("read")
            rows.append(
                {
                    "t": t,
                    "clock": clock(t),
                    **r,
                    "status_visitor": bay_status(bool(r["occupied"]), read, at, visitors),
                    "truth_occupied": int(bool(plate)),
                    "true_plate": plate,
                    "true_status": true_status(bool(plate), plate, at, owner),
                    "true_status_visitor": true_status(bool(plate), plate, at, visitors),
                    "moving": in_any(t, cfg["moving"]),
                    "slice": "car across both bays" if in_any(t, cfg["straddle"]) else "normal",
                }
            )
    d = pd.DataFrame(rows)
    out = Path("outputs/loop")
    (out / "local").mkdir(parents=True, exist_ok=True)
    d.to_csv(out / "local" / "video_night_1.csv", index=False)
    scored = d[~d["moving"]]
    (out / "local" / "video_night_1_timeline.md").write_text(
        "# Night video: status timeline per bay (LOCAL ONLY)\n\n" + _md(timeline(d)) + "\n"
    )
    (out / "video_night_1.md").write_text(video_report(d, scored, pipe, cfg))
    logger.info("Video: {} frames scored -> {}", scored["t"].nunique(), out / "video_night_1.md")


def _alerts(g: pd.DataFrame, col: str) -> int:
    """Separate alert episodes: switches into POTENTIALLY_UNAUTHORIZED."""
    s = g.sort_values("t")[col] == "POTENTIALLY_UNAUTHORIZED"
    return int((s & ~s.shift(fill_value=False)).sum())


def video_report(d: pd.DataFrame, scored: pd.DataFrame, pipe: Pipeline, cfg: dict) -> str:
    pu = "POTENTIALLY_UNAUTHORIZED"
    rows = {}
    for name, g in [("all", scored), *scored.groupby("slice")]:
        cars, empty = g[g.truth_occupied == 1], g[g.truth_occupied == 0]
        read = cars.plate.str.split().str[-1] == cars.true_plate
        visitor = cars.status_visitor
        rows[name] = {
            "bay checks (frames x bays)": len(g),
            "occupancy right": f"{(g.occupied == g.truth_occupied).mean():.0%}",
            "empty bay called occupied": f"{int(empty.occupied.sum())} of {len(empty)}",
            "parked car called empty": f"{int((cars.occupied == 0).sum())} of {len(cars)}",
            "plate read right (bays with a car)": f"{int(read.sum())} of {len(cars)}",
            "owner's cars: final answer right": f"{(g.status == g.true_status).mean():.0%}",
            "owner's cars: false alerts": int((g.status == pu).sum()),
            "as visitors: final answer right": (
                f"{(g.status_visitor == g.true_status_visitor).mean():.0%}"
            ),
            "as visitors: alerted / to a person / missed": f"{int((visitor == pu).sum())} / "
            f"{int((visitor == 'NEEDS_REVIEW').sum())} / {int((visitor == 'EMPTY').sum())}",
        }
    table = pd.DataFrame(rows)
    table.insert(0, "measure", table.index)
    statuses = pd.crosstab(scored["true_status"], scored["status"])
    statuses.insert(0, "truth \\ system", statuses.index)
    episodes = []
    for bay, g in d.groupby("bay"):
        s = g.sort_values("t")["status"]
        alerts = _alerts(g, "status")
        episodes.append(
            {
                "bay": bay,
                "status changes": int((s != s.shift()).sum() - 1),
                "false-alert episodes (owner's cars)": alerts,
            }
        )
    moving = d["t"].nunique() - scored["t"].nunique()
    return (
        "# Full loop on the owner's night video (fixed camera)\n\n"
        f"One 10-minute night video of the owner's two bays, one frame every {cfg['every_s']} s "
        f"({d['t'].nunique()} frames). The owner's two cars arrive and leave several times. "
        f"{moving} frames while a car is moving in or out are not scored. Twice the owner's car "
        "stands across both bays; it then counts as parked in both (its own column). Truth: "
        f"marked from the video by Claude, **{cfg.get('truth_status', 'pending the owner check')}"
        "**. Each car is scored twice: as the owner's car (on the permanent list, so the right "
        "answer is AUTHORIZED) and as a visitor (empty table, so the right answer is "
        "POTENTIALLY_UNAUTHORIZED). Counts only. One night, one spot: indicative only.\n\n"
        + _md(table)
        + "\n\n## Owner's cars: truth against the system (scored frames)\n\n"
        + _md(statuses)
        + "\n\n## Over time (all frames, moving ones included)\n\n"
        + _md(pd.DataFrame(episodes))
        + "\n\n## Time per stage (Mac, Apple GPU)\n\n"
        + _md(pipe.timing())
        + "\n"
    )


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--folder", type=Path)
    ap.add_argument("--every", type=float, default=2.0, help="seconds between video frames")
    ap.add_argument("--yes", action="store_true", help="accept every proposed change")
    ap.add_argument("--video-eval", type=Path, help="video truth config")
    args = ap.parse_args()
    setup_logging(load_config().logging)
    if args.folder:
        result = run_folder(args.folder, args.every, args.yes)
        for p in result.problems:
            logger.bind(problem=p.reason).warning("{}: {} ({})", p.source, p.guidance, p.detail)
        logger.info("Results -> {}", RUNS / args.folder.name)
    if args.video_eval:
        video_eval(yaml.safe_load(args.video_eval.read_text()))


if __name__ == "__main__":
    main()
