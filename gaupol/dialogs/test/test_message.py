# Copyright (C) 2005-2008 Osmo Salomaa
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

import gaupol
import gtk


class _TestMessageDialog(gaupol.TestCase):

    def run__dialog(self):
        # pylint: disable=E1101
        self.dialog.run()
        self.dialog.destroy()


class TestErrorDialog(_TestMessageDialog):

    def setup_method(self, method):
        self.dialog = gaupol.ErrorDialog(gtk.Window(), "test", "test")
        self.dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        self.dialog.show()


class TestInfoDialog(_TestMessageDialog):

    def setup_method(self, method):
        self.dialog = gaupol.InfoDialog(gtk.Window(), "test", "test")
        self.dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        self.dialog.show()


class TestQuestionDialog(_TestMessageDialog):

    def setup_method(self, method):
        self.dialog = gaupol.QuestionDialog(gtk.Window(), "test", "test")
        self.dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        self.dialog.show()


class TestWarningDialog(_TestMessageDialog):

    def setup_method(self, method):
        self.dialog = gaupol.WarningDialog(gtk.Window(), "test", "test")
        self.dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        self.dialog.show()
