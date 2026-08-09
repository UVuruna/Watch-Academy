"""ALG-1 EXTREME STATE MATRIX - the DRIVING half of the Zubi v2 runtime
audit (rules/GUI.md -> Zubi v2). Companion to `layout_checks_qt.py`, which
MEASURES a window; this module MOVES it and asks that module to measure
again.

Why the two are separate files (THE STRUCTURE LAW, 2026-08-09): measuring
and driving are different responsibilities, and the picker driver below made
the single file cross the 1,000-line threshold. The split is by that
responsibility, not by line count - a check answers "is this window right as
it stands", a driver answers "is it still right after the user touches it".

WHAT IS DRIVEN. Numeric controls (slider, spin box) at minimum / current /
maximum; check boxes both ways; small enums (combo boxes) through every item;
and CHECKABLE BUTTON GROUPS - tile galleries and pill rows - by CLICKING each
member. That last kind is why this module exists: a gallery is the real
picker of an image-first program, a click REBUILDS the section under it, and
a `setChecked` would move the visual state without ever running that rebuild.
Before 2026-08-09 the matrix skipped them entirely (measured on this project:
28 undriven tiles on one page, 14 on another, 238 swatches on a third), so
the states a user reaches most often were the only ones never audited.
"""

from __future__ import annotations

from PySide6.QtWidgets import (QAbstractSlider, QCheckBox, QComboBox,
                               QDoubleSpinBox, QPushButton, QScrollBar,
                               QSpinBox, QToolButton, QWidget)

from layout_checks_qt import (ENUM_STATE_LIMIT, PICKER_STATE_LIMIT,
                              check_clipping, check_elision,
                              check_outside_window,
                              check_scroll_with_free_space, settle, walk)


def state_invariants(window: QWidget) -> list[str]:
    """What must hold in EVERY state - the default one and every extreme
    ALG-1 drives the window through."""
    return (check_clipping(window)
            + check_elision(window)
            + check_scroll_with_free_space(window)
            + check_outside_window(window))


def control_states(widget: QWidget):
    """(kind, values to visit, value to restore, setter) or None.

    QScrollBar is deliberately excluded: it is a subclass of QAbstractSlider
    but it is VIEW state, not a setting the user configures - driving it to
    its maximum only scrolls the view the scroll checks are already judging."""
    if isinstance(widget, QScrollBar):
        return None
    if isinstance(widget, (QAbstractSlider, QSpinBox, QDoubleSpinBox)):
        return ("value",
                [widget.minimum(), widget.value(), widget.maximum()],
                widget.value(), widget.setValue)
    if isinstance(widget, QCheckBox):
        return ("checked", [False, True], widget.isChecked(),
                widget.setChecked)
    if isinstance(widget, QComboBox) and 0 < widget.count() <= ENUM_STATE_LIMIT:
        return ("item", list(range(widget.count())), widget.currentIndex(),
                widget.setCurrentIndex)
    return None


def picker_group(widget: QWidget) -> list[QWidget] | None:
    """The CHECKABLE sibling buttons `widget` belongs to, when it is the
    FIRST of them - otherwise None, so one group is driven once.

    A tile gallery or a row of pills carries no value to set: the state IS
    which button is checked, and reaching it means CLICKING."""
    if not isinstance(widget, (QPushButton, QToolButton)):
        return None
    if not widget.isCheckable():
        return None
    parent = widget.parentWidget()
    if parent is None:
        return None
    siblings = [child for child in parent.children()
                if isinstance(child, (QPushButton, QToolButton))
                and child.isCheckable() and child.isVisible()]
    if len(siblings) < 2 or siblings[0] is not widget:
        return None
    return siblings


def _label(widget: QWidget) -> str:
    try:
        name = widget.objectName() or widget.accessibleName() or ""
        text = widget.text() if hasattr(widget, "text") else ""
    except RuntimeError:
        return "<deleted>"
    return f"{widget.__class__.__name__} '{name or text[:24] or '-'}'"


def _report(label: str, state: str, problem: str) -> str:
    return (f"ALG-1 EXTREME STATE MATRIX (rules/GUI.md -> Zubi v2) "
            f"{label} at {state}: {problem} - a state the user can reach "
            "must satisfy the same rules as the default one; fix the layout "
            "for the extreme, or narrow the control's range")


def _drive_values(window, widget, plan, invariants, baseline, seen, problems):
    kind, values, original, apply_value = plan
    label = _label(widget)
    try:
        for value in values:
            try:
                apply_value(value)
            except (RuntimeError, TypeError):
                break
            settle(window)
            for problem in invariants(window):
                key = (label, problem)
                if problem in baseline or key in seen:
                    continue
                seen.add(key)
                problems.append(_report(label, f"{kind}={value}", problem))
    finally:
        try:
            apply_value(original)
            settle(window)
        except (RuntimeError, TypeError):
            pass


def _drive_picker(window, group, invariants, baseline, seen, problems):
    """Click through a picker group, then click its original member back.

    A click can REBUILD the section - deleting the very buttons being
    driven - so every call is guarded and a dead group simply ends the run
    for that picker. That is not a failure: the rebuild is the state, and
    the invariants were already measured on it before the corpse appeared."""
    try:
        original = next((i for i, one in enumerate(group) if one.isChecked()),
                        None)
    except RuntimeError:
        return
    driven = group[:PICKER_STATE_LIMIT]
    for index, button in enumerate(driven):
        label = _label(button)
        try:
            button.click()
        except RuntimeError:
            break
        settle(window)
        for problem in invariants(window):
            key = (label, problem)
            if problem in baseline or key in seen:
                continue
            seen.add(key)
            problems.append(_report(label, f"picked #{index}", problem))
    if len(group) > PICKER_STATE_LIMIT:
        # NO SILENT CAP (rules/GUI.md): a bounded sweep says what it left.
        problems.append(
            f"ALG-1 COVERAGE NOTE (rules/GUI.md -> Zubi v2) {_label(group[0])}: "
            f"{len(group)} checkable siblings, only the first "
            f"{PICKER_STATE_LIMIT} were driven (PICKER_STATE_LIMIT) - the rest "
            "are UNAUDITED, not proven good")
    if original is not None:
        try:
            group[original].click()
            settle(window)
        except (RuntimeError, IndexError):
            pass


def check_extreme_states(window: QWidget, invariants=None) -> list[str]:
    """ALG-1 - "tested" without extremes is not tested.

    Every numeric control is visited at minimum / current / maximum, every
    check box in both states, every small enum through all its items, every
    checkable picker group through its members; after each change the window
    is re-settled (processEvents twice, so a signal handler's own layout work
    lands) and the invariants are re-run. Original values are restored
    afterwards, even when a handler raises.

    Only breakage the DEFAULT state does not already show is reported - the
    baseline belongs to the plain audit, and repeating it once per slider
    position would bury the new finding."""
    invariants = state_invariants if invariants is None else invariants
    baseline = set(invariants(window))
    problems: list[str] = []
    seen: set[tuple[str, str]] = set()
    for widget in list(walk(window)):
        try:
            plan = control_states(widget)
            group = picker_group(widget) if plan is None else None
        except RuntimeError:
            continue
        if plan is not None:
            _drive_values(window, widget, plan, invariants, baseline, seen,
                          problems)
        elif group is not None:
            _drive_picker(window, group, invariants, baseline, seen, problems)
    return problems
