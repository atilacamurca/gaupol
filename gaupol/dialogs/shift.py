# Copyright (C) 2005-2008,2010 Osmo Salomaa
#
# This file is part of Gaupol.
#
# Gaupol is free software: you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# Gaupol is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE. See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaupol. If not, see <http://www.gnu.org/licenses/>.

"""Dialogs for shifting positions."""

import aeidon
import gaupol
import gtk
_ = aeidon.i18n._

__all__ = ("FrameShiftDialog", "TimeShiftDialog")


class PositionShiftDialog(gaupol.BuilderDialog):

    """Base class for dialogs for shifting positions."""

    _widgets = ("all_radio",
                "amount_spin",
                "current_radio",
                "preview_button",
                "selected_radio",
                "unit_label")

    def __init__(self, parent, application):
        """Initialize a :class:`PositionShiftDialog` object."""
        gaupol.BuilderDialog.__init__(self, "shift-dialog.ui")
        self.application = application
        self._init_widgets()
        self._init_values()
        self._dialog.set_transient_for(parent)
        self._dialog.set_default_response(gtk.RESPONSE_OK)

    def _get_preview_row(self):
        """Return row to start preview from."""
        target = self._get_target()
        page = self.application.get_current_page()
        rows = page.view.get_selected_rows()
        return (rows[0] if rows else 0)

    def _get_target(self):
        """Return the selected target."""
        if self._selected_radio.get_active():
            return gaupol.targets.SELECTED
        if self._current_radio.get_active():
            return gaupol.targets.CURRENT
        if self._all_radio.get_active():
            return gaupol.targets.ALL
        raise ValueError("Invalid target radio state")

    def _init_values(self):
        """Intialize default values for widgets."""
        target = gaupol.conf.position_shift.target
        self._selected_radio.set_active(target == gaupol.targets.SELECTED)
        self._current_radio.set_active(target == gaupol.targets.CURRENT)
        self._all_radio.set_active(target == gaupol.targets.ALL)
        page = self.application.get_current_page()
        rows = page.view.get_selected_rows()
        if (not rows) and (target == gaupol.targets.SELECTED):
            self._current_radio.set_active(True)
        self._selected_radio.set_sensitive(bool(rows))
        if page.project.video_path is None:
            self._preview_button.set_sensitive(False)
        if page.project.main_file is None:
            self._preview_button.set_sensitive(False)
        self._amount_spin.emit("value-changed")

    def _init_widgets(self):
        """Initialize widgets."""
        raise NotImplementedError

    def _on_amount_spin_value_changed(self, spin_button):
        """Set response sensitivity."""
        has_value = (spin_button.get_value() != 0.0)
        self.set_response_sensitive(gtk.RESPONSE_OK, has_value)

    def _on_preview_button_clicked(self, *args):
        """Preview shift changes with a video player."""
        page = self.application.get_current_page()
        target = self._get_target()
        rows = self.application.get_target_rows(target)
        self.application.preview_changes(page,
                                         self._get_preview_row(),
                                         aeidon.documents.MAIN,
                                         page.project.shift_positions,
                                         (rows, self._get_amount()))

    def _on_response(self, dialog, response):
        """Save target and shift positions."""
        gaupol.conf.position_shift.target = self._get_target()
        if response == gtk.RESPONSE_OK:
            self._shift_positions()

    def _shift_positions(self):
        """Shift positions in subtitles."""
        gaupol.util.set_cursor_busy(self)
        target = self._get_target()
        rows = self.application.get_target_rows(target)
        amount = self._get_amount()
        for page in self.application.get_target_pages(target):
            page.project.shift_positions(rows, amount)
        gaupol.util.set_cursor_normal(self)


class FrameShiftDialog(PositionShiftDialog):

    """Dialog for shifting frames."""

    __metaclass__ = aeidon.Contractual

    def _get_amount_ensure(self, value):
        assert isinstance(value, int)

    def _get_amount(self):
        """Return the amount of frames to shift."""
        return self._amount_spin.get_value_as_int()

    def _init_widgets(self):
        """Initialize widgets."""
        self._amount_spin.set_numeric(True)
        self._amount_spin.set_digits(0)
        self._amount_spin.set_increments(1, 10)
        self._amount_spin.set_range(-9999999, 9999999)
        self._amount_spin.set_value(0)
        self._unit_label.set_text(_("frames"))


class TimeShiftDialog(PositionShiftDialog):

    """Dialog for shifting times."""

    __metaclass__ = aeidon.Contractual

    def _get_amount_ensure(self, value):
        assert isinstance(value, float)

    def _get_amount(self):
        """Return the amount of seconds to shift."""
        return self._amount_spin.get_value()

    def _init_widgets(self):
        """Initialize widgets."""
        self._amount_spin.set_numeric(True)
        self._amount_spin.set_digits(3)
        self._amount_spin.set_increments(0.1, 1)
        self._amount_spin.set_range(-99999, 99999)
        self._amount_spin.set_value(0.000)
        self._unit_label.set_text(_("seconds"))
