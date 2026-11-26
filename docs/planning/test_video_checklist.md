# Final test video checklist (night 3, at most 20 minutes)

Goal: one short night video from the **same fixed camera spot as night video 2**, recorded alone,
that is used **only once**, as the final test of the whole system. Cars: the **BMW (AA 66705)**
and the **Tesla (O 33044)**. You drive one car at a time; the other waits out of view.

## Before you press record

- [ ] Night, dry weather, normal street lighting.
- [ ] Phone on the stick in the **same spot, height and angle as night video 2** (both bays fully
      in view, same framing). Landscape, 1× lens, no zoom, flash off.
- [ ] Do Not Disturb on; enough battery and storage for 20 minutes.
- [ ] Both bays **empty** when you start.
- [ ] Write down the **clock time** you press record (needed for the commands below).
- [ ] Do not touch or move the phone after recording starts (step 10 blocks the view without
      touching it).

## The events, in order (about 19 minutes)

Times are a guide; a minute early or late is fine. Keep each "parked" period at least as long as
written, because the system needs about 10–20 seconds to confirm a change.

| # | time | what you do | what it tests |
|---|---|---|---|
| 1 | 0:00–1:00 | Leave both bays empty; stay out of view | empty baseline, camera snapshot |
| 2 | 1:00–3:00 | **BMW reverses into the LEFT bay** normally; walk out of view. Parked ≥ 90 s | normal arrival, rear plate |
| 3 | 3:00–5:00 | **Tesla drives nose-in into the RIGHT bay**; walk out of view. Both parked ≥ 60 s | both occupied, front plate |
| 4 | 5:00–5:40 | **Stand in front of the Tesla's plate** for about 30 s, then walk away | plate hidden by a person |
| 5 | 5:40–7:00 | **BMW leaves.** Then **stand inside the empty LEFT bay** for about 30 s; walk away | departure, person in an empty bay |
| 6 | 7:00–8:00 | **Tesla leaves.** Both bays empty for about 30 s | departure, empty again |
| 7 | 8:00–10:00 | **BMW parks across BOTH bays** (over the middle line). Parked ≥ 90 s | car across both bays |
| 8 | 10:00–11:00 | BMW leaves. **Tesla pulls into the RIGHT bay, waits only about 20 s, then leaves** | quick in-and-out (should not alert) |
| 9 | 11:00–13:00 | **Tesla parks CROOKED in the RIGHT bay** (partly over the line). Parked ≥ 90 s | crooked car; permit expired (see commands) |
| 10 | 13:00–15:00 | **BMW parks nose-in in the LEFT bay; leave its headlights ON for 30 s**, then off. Both parked | glare, both occupied |
| 11 | 15:00–15:30 | **Hold a jacket or board in front of the camera for about 20 s** (do not touch the phone), then remove it | camera blocked, then recovers |
| 12 | 15:30–17:00 | Nothing happens; both cars stay parked | recovery after the block |
| 13 | 17:00–18:30 | **Tesla leaves**, then about 30 s later **BMW leaves** | departures |
| 14 | 18:30–19:30 | Both bays empty; stop recording before 20:00 | empty at the end |

Passing cars, other people or a car turning nearby are fine: keep them, they are realistic. Just
tell me roughly when they happened.

## Owner commands for this video (`commands.txt`)

Write these **before** you record, using the clock time you pressed record (T). Your own
wording is fine; keep the meaning.

```
<date> <T - 1 min> | allow car 66705
<date> <T - 1 min> | allow car 33044 until <T + 9 min>
<date> <T + 6 min> | what's the weather today
```

This makes the BMW always allowed, the Tesla allowed only for its first stay (steps 3–6), and
**not** allowed when it comes back crooked in step 9 (expected: POTENTIALLY_UNAUTHORIZED). The
third line is off-topic and should be refused.

## After recording (keep the test sealed)

- [ ] Copy the video, unedited, to `data/raw/video_test/` and `commands.txt` next to it.
- [ ] **Do not run any `just` recipe or the demo on it.** Do not trim or re-encode it.
- [ ] Tell Claude the start time, the video length and anything unexpected.
- [ ] Claude marks the truth (arrivals, departures, people, blocked view) from the frames, and you
      check it, **before any model sees the video**.
- [ ] The settings are frozen and committed; then the test is run **once** and reported as it
      comes out.

You are done when: one video of at most 20 minutes, all 14 steps done in order, the camera never
moved, and `commands.txt` written.
