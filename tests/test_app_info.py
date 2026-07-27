"""Pins the Session 22 renaming decision baked into the pre-M7 installer
metadata seed (`setup/app_info.json`): the product is named Watch Academy
everywhere it is marketed, while DOMY stays the dial's own name and the
on-disk/binary identity (CUBE.md §The Name; ROADMAP.md M7)."""

import json
from pathlib import Path

APP_INFO_PATH = Path(__file__).resolve().parent.parent / "setup" / "app_info.json"


def test_app_info_names_watch_academy_but_keeps_domy_binaries():
    info = json.loads(APP_INFO_PATH.read_text(encoding="utf-8"))

    assert info["name"] == "Watch Academy"
    assert "Watch Academy" in info["description"]
    assert "DOMY" in info["description"]

    # DOMY remains the dial's own name — the disk/binary identity is
    # untouched by the marketing rename (repo, folder, mutex, exe).
    assert info["exe_name"] == "DOMYWatch.exe"
    assert info["installer_name"] == "DOMYWatch_Setup.exe"
