"""The demo app loads and handles the command flow (models are loaded only when needed)."""

import pytest
from streamlit.testing.v1 import AppTest

from smart_parking.commands.adapters import weights_present
from smart_parking.common.config import load_config


@pytest.mark.skipif(not weights_present(load_config().commands, ["gliner-small-v2.1"]),
                    reason="Model C weights not downloaded")  # fmt: skip
def test_command_accept_updates_the_permit_table():
    at = AppTest.from_file("src/smart_parking/app.py", default_timeout=300)
    at.run()
    assert not at.exception
    at.text_input[0].set_value("allow car 33044")
    at.button[0].click().run()
    assert at.info[0].value == "Allow car 33044 in either bay permanently (no end time)?"
    next(b for b in at.button if b.label == "Accept").click().run()
    assert at.dataframe[0].value.to_dict("records") == [
        {"car number": "33044", "allowed until": "permanent"}
    ]
