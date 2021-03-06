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

import gaupol
import gtk


class TestEncodingDialog(gaupol.TestCase):

    def run__dialog(self):
        self.dialog.run()
        self.dialog.destroy()

    def setup_method(self, method):
        self.dialog = gaupol.EncodingDialog(gtk.Window())
        self.dialog.show()

    def test__on_tree_view_row_activated(self):
        column = self.dialog._tree_view.get_columns()[-1]
        self.dialog._tree_view.row_activated(1, column)

    def test_get_encoding(self):
        store = self.dialog._tree_view.get_model()
        selection = self.dialog._tree_view.get_selection()
        selection.select_path(10)
        name = self.dialog.get_encoding()
        assert name is not None


class TestMenuEncodingDialog(TestEncodingDialog):

    def setup_method(self, method):
        self.dialog = gaupol.MenuEncodingDialog(gtk.Window())
        self.dialog.show()

    def test__on_tree_view_cell_toggled(self):
        column = self.dialog._tree_view.get_columns()[-1]
        renderer = column.get_cell_renderers()[0]
        renderer.emit("toggled", 0)

    def test_get_visible_encodings(self):
        self.dialog.get_visible_encodings()
