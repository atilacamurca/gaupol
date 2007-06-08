# Copyright (C) 2005-2007 Osmo Salomaa
#
# This file is part of Gaupol.
#
# Gaupol is free software; you can redistribute it and/or modify it under the
# terms of the GNU General Public License as published by the Free Software
# Foundation; either version 2 of the License, or (at your option) any later
# version.
#
# Gaupol is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR
# A PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# Gaupol; if not, write to the Free Software Foundation, Inc., 51 Franklin
# Street, Fifth Floor, Boston, MA 02110-1301, USA.


import gtk

from gaupol.gtk import unittest


class TestPositionAgent(unittest.TestCase):

    def setup_method(self, method):

        self.application = self.get_application()

    def test_on_shift_positions_activate(self):

        responder = iter((gtk.RESPONSE_CANCEL, gtk.RESPONSE_OK))
        respond = lambda *args: responder.next()
        self.application.flash_dialog = flash_dialog
        self.application.on_shift_positions_activate()
        self.application.on_shift_positions_activate()
