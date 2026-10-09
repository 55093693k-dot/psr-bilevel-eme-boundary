# -*- coding: utf-8 -*-
"""probe_gui_dialog.py — can the Resource Configuration dialog be opened from script?

The parallel-task count is a GUI-only setting (setresource fails in both products). This checks
whether any script command can at least bring the Resources dialog up on screen.
"""
from __future__ import annotations


def try_open(mode) -> dict:
    rec = {}
    for cmd in ("resourceconfig;", "resources;", "resource_config;", "openresource;",
                "?resource;", "?resources;", "resource;"):
        try:
            mode.eval(cmd)
            rec[cmd] = "OK"
        except Exception as exc:  # noqa: BLE001
            rec[cmd] = "FAIL:" + str(exc).splitlines()[0][:45]
    return rec
