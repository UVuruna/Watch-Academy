"""Pure computation core: time/sun/year/moon -> dial angles and state.

Zero Qt, zero file I/O, zero datetime.now() — callers inject "now" and
pre-extracted data, so every function is deterministic and testable
headless (and reusable outside the desktop widget).
"""
