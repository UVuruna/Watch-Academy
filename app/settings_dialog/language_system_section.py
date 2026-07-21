"""Language & System Section — `_LanguageSystemSectionMixin`: TWO nav
sections sharing one mixin (both small, simple pickers) — Language
(Language, Calendar eras groups) and System (System group).
Plain-Python mixin (no base class — composed onto `dialog.
SettingsDialog`'s `QDialog` shell, `research/REFACTOR_PLAN.md` §7).
See [Language & System Section](language_system_section.md) for the
full behavioral narrative.
"""

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
)

from config import constants


class _LanguageSystemSectionMixin:
    def _build_system_group(self) -> QGroupBox:
        """Start with Windows (owner spec 2026-07-12): a standard-user
        HKCU Run entry — the registry is the store, read live here and
        applied by the controller on OK. Plus the VISIBILITY Z mode
        (owner 2026-07-17, ROADMAP 15d): below all windows (default) or
        always on top."""
        from app import native

        tr = self._tr
        group = QGroupBox(tr("System"))
        form = QFormLayout(group)
        self._autostart_check = QCheckBox(tr("Start with Windows"))
        self._autostart_check.setChecked(native.autostart_enabled())
        form.addRow(self._autostart_check)
        self._z_mode_combo = QComboBox()
        for mode in constants.Z_MODES:
            self._z_mode_combo.addItem(tr(constants.Z_MODE_TITLES[mode]), mode)
        index = self._z_mode_combo.findData(self._settings.z_mode)
        if index >= 0:
            self._z_mode_combo.setCurrentIndex(index)
        form.addRow(tr("Visibility"), self._z_mode_combo)
        return group

    def _build_era_group(self) -> QGroupBox:
        """THE YEAR LINE (Session 16, owner amendment 2026-07-17): the
        Anno Lucis year always accompanies the official year — here the
        user picks the OFFICIAL labels (BCE/CE vs BC/AD), whether
        positive years carry the suffix (default bare), and the
        optional THIRD calendar on the line. Placed under Language —
        the documented call."""
        tr = self._tr
        group = QGroupBox(tr("Calendar eras"))
        form = QFormLayout(group)
        self._era_combo = QComboBox()
        for notation in constants.ERA_NOTATIONS:
            self._era_combo.addItem(
                constants.ERA_NOTATION_TITLES[notation], notation
            )
        index = self._era_combo.findData(self._settings.era_notation)
        if index >= 0:
            self._era_combo.setCurrentIndex(index)
        form.addRow(tr("Era labels"), self._era_combo)
        self._era_suffix_check = QCheckBox(
            tr("Write the era after positive years too (2026 CE)")
        )
        self._era_suffix_check.setChecked(self._settings.show_era_suffix)
        form.addRow("", self._era_suffix_check)
        self._third_era_combo = QComboBox()
        for era in constants.THIRD_ERAS:
            self._third_era_combo.addItem(
                tr(constants.THIRD_ERA_TITLES[era]), era
            )
            note = constants.THIRD_ERA_NOTES.get(era)
            if note:
                # Epoch fine print (owner amendment: tooltip ONLY).
                self._third_era_combo.setItemData(
                    self._third_era_combo.count() - 1, tr(note),
                    Qt.ItemDataRole.ToolTipRole,
                )
        index = self._third_era_combo.findData(self._settings.third_era)
        if index >= 0:
            self._third_era_combo.setCurrentIndex(index)
        form.addRow(tr("Third calendar"), self._third_era_combo)
        note = QLabel(
            tr(
                "Years in legends read as official · Anno Lucis (A.L. = "
                "CE + 4079, the measured light era) — the third "
                "calendar joins that line."
            )
        )
        note.setWordWrap(True)
        form.addRow(note)
        return group

    def autostart_selected(self) -> bool:
        return self._autostart_check.isChecked()

    def _build_language_group(self) -> QGroupBox:
        tr = self._tr
        group = QGroupBox(tr("Language"))
        row = QHBoxLayout(group)
        self._language_combo = QComboBox()
        # The ORIGINALS ride the top (owner spec 2026-07-11): English
        # and Serbian Latin ship hand-written in the app; everything
        # below the separator machine-translates on first pick.
        originals = [
            (code, constants.TRANSLATION_LANGUAGES[code])
            for code in constants.TRANSLATION_ORIGINALS
        ]
        rest = sorted(
            (
                (code, name)
                for code, name in constants.TRANSLATION_LANGUAGES.items()
                if code not in constants.TRANSLATION_ORIGINALS
            ),
            key=lambda item: item[1],
        )
        for code, name in originals:
            self._language_combo.addItem(
                tr("{name} — original").format(name=name), code
            )
        self._language_combo.insertSeparator(len(originals))
        for code, name in rest:
            self._language_combo.addItem(name, code)
        index = self._language_combo.findData(self._settings.language)
        if index >= 0:
            self._language_combo.setCurrentIndex(index)
        row.addWidget(self._language_combo)
        # One-click way back to the shipped originals (owner spec
        # 2026-07-11): jump the combo to English.
        default = QPushButton(tr("Default"))
        default.setToolTip(tr("Back to English — the shipped original texts"))
        default.clicked.connect(
            lambda: self._language_combo.setCurrentIndex(
                self._language_combo.findData("en")
            )
        )
        row.addWidget(default)
        note = QLabel(
            tr(
                "The originals above the line ship inside the app. Any "
                "other language translates itself in the background on "
                "first pick (internet needed once) and then works offline."
            )
        )
        note.setWordWrap(True)
        row.addWidget(note, stretch=1)
        return group
