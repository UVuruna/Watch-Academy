"""Suite-wide wiring. ONE concern lives here: every test that runs
under a Qt application measures with REAL glyphs, never tofu — see
``tests/offscreen_fonts.py`` for the root cause and the proof. The
fixture is function-scoped so it also catches an application created
by an EARLIER module's fixture (apps are process-wide and module
fixtures never tear them down), and it is a cheap no-op once fonts
exist."""

import pytest

from tests.offscreen_fonts import provision


@pytest.fixture(autouse=True)
def _real_fonts_under_offscreen():
    provision()
    yield
