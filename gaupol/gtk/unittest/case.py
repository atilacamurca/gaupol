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


"""Base class for GTK unit test cases."""


import gaupol.gtk
import gtk

from gaupol import unittest


class TestCase(unittest.TestCase):

    """Base class for GTK unit test cases."""

    def get_application(self):
        """Get a new application with two open pages."""

        if not hasattr(TestCase, "application"):
            TestCase.application = gaupol.gtk.Application()
        application = TestCase.application
        while application.pages:
            application.close(application.pages[0], False)
        application.add_new_page(self.get_page())
        application.add_new_page(self.get_page())
        return application

    def get_page(self):
        """Get a new page with two open documents."""

        page = gaupol.gtk.Page()
        page.project.open_main(self.get_subrip_path(), "ascii")
        page.project.open_translation(self.get_microdvd_path(), "ascii")
        return page

    def teardown_method(self, method):
        """Remove state set for executing tests in method."""

        while gtk.events_pending():
            gtk.main_iteration(block=False)
