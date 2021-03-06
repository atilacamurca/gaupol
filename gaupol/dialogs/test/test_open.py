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

import aeidon
import gaupol
import gtk
import os
import random

from .test_file import _TestFileDialog


class TestOpenDialog(_TestFileDialog):

    def setup_method(self, method):
        gaupol.conf.file.directory = os.getcwd()
        doc = aeidon.documents[random.randint(0, 1)]
        self.dialog = gaupol.OpenDialog(gtk.Window(), "test", doc)
        self.dialog.show()

    def test__on_response(self):
        self.dialog.response(gtk.RESPONSE_CANCEL)
