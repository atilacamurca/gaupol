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


class TestSaveAgent(gaupol.TestCase):

    def run__show_encoding_error_dialog(self):
        self.delegate._show_encoding_error_dialog("test", "ascii")

    def run__show_io_error_dialog(self):
        self.delegate._show_io_error_dialog("test", "test")

    def setup_method(self, method):
        self.application = self.new_application()
        self.delegate = self.application.save_main.im_self

    @aeidon.deco.monkey_patch(gaupol.util, "flash_dialog")
    def test__show_encoding_error_dialog(self):
        gaupol.util.flash_dialog = lambda *args: gtk.RESPONSE_OK
        self.delegate._show_encoding_error_dialog("test", "ascii")

    @aeidon.deco.monkey_patch(gaupol.util, "flash_dialog")
    def test__show_io_error_dialog(self):
        gaupol.util.flash_dialog = lambda *args: gtk.RESPONSE_OK
        self.delegate._show_io_error_dialog("test", "test")

    def test__on_save_all_documents_activate(self):
        self.application.get_action("save_all_documents").activate()

    def test__on_save_main_document_activate(self):
        self.application.get_action("save_main_document").activate()

    @aeidon.deco.monkey_patch(gaupol.SaveDialog, "get_filename")
    @aeidon.deco.monkey_patch(gaupol.util, "run_dialog")
    def test__on_save_main_document_as_activate(self):
        get_filename = lambda *args: self.new_subrip_file()
        gaupol.SaveDialog.get_filename = get_filename
        gaupol.util.run_dialog = lambda *args: gtk.RESPONSE_OK
        self.application.get_action("save_main_document_as").activate()

    def test__on_save_translation_document_activate(self):
        self.application.get_action("save_translation_document").activate()

    @aeidon.deco.monkey_patch(gaupol.SaveDialog, "get_filename")
    @aeidon.deco.monkey_patch(gaupol.util, "run_dialog")
    def test__on_save_translation_document_as_activate(self):
        get_filename = lambda *args: self.new_subrip_file()
        gaupol.SaveDialog.get_filename = get_filename
        gaupol.util.run_dialog = lambda *args: gtk.RESPONSE_OK
        self.application.get_action("save_translation_document_as").activate()

    def test_save_main(self):
        page = self.application.get_current_page()
        self.application.save_main(page)

    @aeidon.deco.monkey_patch(gaupol.util, "flash_dialog")
    def test_save_main__io_error(self):
        gaupol.util.flash_dialog = lambda *args: gtk.RESPONSE_OK
        page = self.application.get_current_page()
        os.chmod(page.project.main_file.path, 0000)
        self.raises(gaupol.Default, self.application.save_main, page)
        os.chmod(page.project.main_file.path, 0777)

    @aeidon.deco.monkey_patch(gaupol.util, "flash_dialog")
    def test_save_main__unicode_error(self):
        gaupol.util.flash_dialog = lambda *args: gtk.RESPONSE_OK
        page = self.application.get_current_page()
        page.project.main_file.encoding = "ascii"
        page.project.set_text(0, aeidon.documents.MAIN, "\303\266")
        self.raises(gaupol.Default, self.application.save_main, page)

    @aeidon.deco.monkey_patch(gaupol.SaveDialog, "get_filename")
    @aeidon.deco.monkey_patch(gaupol.util, "run_dialog")
    def test_save_main__untitled(self):
        get_filename = lambda *args: self.new_subrip_file()
        gaupol.SaveDialog.get_filename = get_filename
        gaupol.util.run_dialog = lambda *args: gtk.RESPONSE_OK
        self.application.get_action("new_project").activate()
        page = self.application.get_current_page()
        self.application.save_main(page)

    @aeidon.deco.monkey_patch(gaupol.SaveDialog, "get_filename")
    @aeidon.deco.monkey_patch(gaupol.util, "run_dialog")
    def test_save_main_as(self):
        get_filename = lambda *args: self.new_subrip_file()
        gaupol.SaveDialog.get_filename = get_filename
        gaupol.util.run_dialog = lambda *args: gtk.RESPONSE_OK
        page = self.application.get_current_page()
        self.application.save_main_as(page)

    @aeidon.deco.monkey_patch(gaupol.util, "run_dialog")
    def test_save_main_as__cancel(self):
        gaupol.util.run_dialog = lambda *args: gtk.RESPONSE_CANCEL
        page = self.application.get_current_page()
        self.raises(gaupol.Default, self.application.save_main_as, page)

    def test_save_translation(self):
        page = self.application.get_current_page()
        self.application.save_translation(page)

    @aeidon.deco.monkey_patch(gaupol.SaveDialog, "get_filename")
    @aeidon.deco.monkey_patch(gaupol.util, "run_dialog")
    def test_save_translation__untitled(self):
        get_filename = lambda *args: self.new_subrip_file()
        gaupol.SaveDialog.get_filename = get_filename
        gaupol.util.run_dialog = lambda *args: gtk.RESPONSE_OK
        self.application.get_action("new_project").activate()
        page = self.application.get_current_page()
        self.application.save_translation(page)

    @aeidon.deco.monkey_patch(gaupol.SaveDialog, "get_filename")
    @aeidon.deco.monkey_patch(gaupol.util, "run_dialog")
    def test_save_translation_as(self):
        get_filename = lambda *args: self.new_subrip_file()
        gaupol.SaveDialog.get_filename = get_filename
        gaupol.util.run_dialog = lambda *args: gtk.RESPONSE_OK
        page = self.application.get_current_page()
        self.application.save_translation_as(page)
