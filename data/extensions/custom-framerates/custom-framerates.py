# Copyright (C) 2011 Osmo Salomaa
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

"""Using custom, non-standard framerates."""

import aeidon
import gaupol
import gtk
import os
_ = aeidon.i18n._


class AddFramerateDialog(gaupol.BuilderDialog):

    """Dialog for entering a custom framerate value."""

    _widgets = ("spin_button",)

    def __init__(self, parent):
        """Initialize an :class:`AddFramerateDialog` object."""
        directory = os.path.abspath(os.path.dirname(__file__))
        ui_file_path = os.path.join(directory, "add-framerate-dialog.ui")
        gaupol.BuilderDialog.__init__(self, ui_file_path)
        self._dialog.set_transient_for(parent)
        self._dialog.set_default_response(gtk.RESPONSE_CLOSE)

    def _on_response(self, *args):
        """Update spin button before dispatching response."""
        self._spin_button.update()

    def get_framerate(self):
        """Return framerate entered in the spin button."""
        return float(self._spin_button.get_value())


class PreferencesDialog(gaupol.BuilderDialog):

    """Dialog for editing list of custom framerates."""

    _widgets = ("add_button", "remove_button", "tree_view")

    def __init__(self, framerates, parent):
        """Initialize a :class:`PreferencesDialog` object."""
        directory = os.path.abspath(os.path.dirname(__file__))
        ui_file_path = os.path.join(directory, "preferences-dialog.ui")
        gaupol.BuilderDialog.__init__(self, ui_file_path)
        self._init_tree_view(framerates)
        self._remove_button.set_sensitive(False)
        gaupol.util.scale_to_content(self._tree_view,
                                     min_nchar=20,
                                     min_nlines=12,
                                     max_nchar=80,
                                     max_nlines=16)

        self._dialog.set_transient_for(parent)
        self._dialog.set_default_response(gtk.RESPONSE_CLOSE)

    def _get_selected_rows(self):
        """Return a sequence of the selected rows."""
        rows = self._tree_view.get_selection().get_selected_rows()[1]
        return tuple(x[0] for x in rows)

    def _init_tree_view(self, framerates):
        """Initialize the tree view."""
        selection = self._tree_view.get_selection()
        selection.set_mode(gtk.SELECTION_MULTIPLE)
        selection.connect("changed", self._on_tree_view_selection_changed)
        store = gtk.ListStore(float)
        for framerate in framerates:
            store.append((framerate,))
        store.set_sort_column_id(0, gtk.SORT_ASCENDING)
        self._tree_view.set_model(store)
        renderer = gtk.CellRendererText()
        renderer.props.xalign = 1
        column = gtk.TreeViewColumn("", renderer, text=0)
        column.set_sort_column_id(0)
        def format_framerate(column, renderer, store, itr):
            renderer.props.text = "%.6f" % store.get_value(itr, 0)
        column.set_cell_data_func(renderer, format_framerate)
        self._tree_view.append_column(column)

    def _on_add_button_clicked(self, *args):
        """Add a new framerate."""
        dialog = AddFramerateDialog(self._dialog)
        response = gaupol.util.run_dialog(dialog)
        framerate = dialog.get_framerate()
        dialog.destroy()
        if response != gtk.RESPONSE_OK: return
        store = self._tree_view.get_model()
        store.append((framerate,))

    def _on_remove_button_clicked(self, *args):
        """Remove the selected framerate."""
        rows = self._get_selected_rows()
        store = self._tree_view.get_model()
        for row in reversed(sorted(rows)):
            store.remove(store.get_iter(row))
        if len(store) <= 0: return
        self._tree_view.set_cursor(max(row - 1, 0))

    def _on_tree_view_selection_changed(self, *args):
        """Set the remove button sensitivity."""
        selection = self._tree_view.get_selection()
        n = selection.count_selected_rows()
        self._remove_button.set_sensitive(n > 0)

    def get_framerates(self):
        """Return the defined custom framerates."""
        framerates = []
        store = self._tree_view.get_model()
        for i in range(len(store)):
            framerates.append(store[i][0])
        return(tuple(sorted(framerates)))


class CustomFrameratesExtension(gaupol.Extension):

    """Using custom, non-standard framerates."""

    def __init__(self):
        """Initialize a :class:`CustomFrameratesExtension` object."""
        self._action_group = None
        self._conf = None
        self._framerates = []
        self._uim_ids = []
        self.application = None

    def _clear_attributes(self):
        """Clear values of attributes."""
        self._action_group = None
        self._conf = None
        self._framerates = []
        self._uim_ids = []
        self.application = None

    def _add_framerates(self):
        """Add custom framerates and corresponding UI elements."""
        self._action_group = gtk.ActionGroup("custom-framerates")
        self.application.uim.insert_action_group(self._action_group, -1)
        tooltip = _("Calculate nonnative units with a framerate of %.3f fps")
        directory = os.path.abspath(os.path.dirname(__file__))
        ui_file_path = os.path.join(directory, "custom-framerates.ui.xml")
        ui_xml_template = open(ui_file_path, "r").read()
        self._framerates = []
        self._uim_ids = []
        for value in sorted(self._conf.framerates):
            name = "FPS_%s" % (("%.3f" % value).replace(".", "_"))
            if hasattr(aeidon.framerates, name):
                print "Framerate %.3f already exists!" % value
                continue
            setattr(aeidon.framerates, name, aeidon.EnumerationItem())
            framerate = getattr(aeidon.framerates, name)
            framerate.label = "%.3f fps" % value
            framerate.mpsub = "%.2f" % value
            framerate.value = float(value)
            self._framerates.append(framerate)
            action_name = name.replace("FPS", "show_framerate")
            action = gtk.RadioAction(name=action_name,
                                     label=framerate.label,
                                     tooltip=(tooltip % value),
                                     stock_id=None,
                                     value=int(framerate))

            group = "show_framerate_23_976"
            action.set_group(self.application.get_action(group))
            action.framerate = framerate
            self._action_group.add_action(action)
            ui_xml = ui_xml_template % (name.replace("FPS_", ""),
                                        action.get_name())

            uim_id = self.application.uim.add_ui_from_string(ui_xml)
            self._uim_ids.append(uim_id)
            gaupol.framerate_actions[framerate] = action.get_name()
            self.application.framerate_combo.append_text(action.get_label())
        self.application.uim.ensure_update()
        self.application.set_menu_notify_events("custom-framerates")

    def _remove_framerates(self):
        """Remove custom framerates and corresponding UI elements."""
        fallback = aeidon.framerates.FPS_23_976
        combo = self.application.framerate_combo
        store = self.application.framerate_combo.get_model()
        for framerate in reversed(self._framerates):
            if gaupol.conf.editor.framerate == framerate:
                gaupol.conf.editor.framerate = fallback
            if self.application.pages:
                ## Go through all application's pages and reset those set to
                ## the custom framerate back to the default framerate.
                orig_page = self.application.get_current_page()
                for page in self.application.pages:
                    self.application.set_current_page(page)
                    if page.project.framerate == framerate:
                        combo.set_active(fallback)
                self.application.set_current_page(orig_page)
            elif combo.get_active() == framerate:
                ## If no pages are open, but the framerate is set to the custom
                ## one, reset back to the default framerate, but without
                ## triggering callbacks that assume there are pages.
                callback = self.application._on_framerate_combo_changed
                combo.handler_block_by_func(callback)
                combo.set_active(fallback)
                combo.handler_unblock_by_func(callback)
                action = self.application.get_framerate_action(fallback)
                callback = self.application._on_show_framerate_23_976_changed
                action.handler_block_by_func(callback)
                action.set_active(True)
                action.handler_unblock_by_func(callback)
            ## Remove UI elements created for the custom framerate and finally
            ## remove the custom framerate from its enumeration.
            store.remove(store.get_iter(framerate))
            del gaupol.framerate_actions[framerate]
            name = "FPS_%s" % (("%.3f" % framerate.value).replace(".", "_"))
            delattr(aeidon.framerates, name)
        for uim_id in self._uim_ids:
            self.application.uim.remove_ui(uim_id)
        self.application.uim.remove_action_group(self._action_group)
        self.application.uim.ensure_update()

    def setup(self, application):
        """Setup extension for use with `application`."""
        gaupol.conf.register_extension("custom_framerates",
                                       {"framerates": [48.0]})

        self._conf = gaupol.conf.extensions.custom_framerates
        self.application = application
        self._add_framerates()

    def show_preferences_dialog(self, parent):
        """Show a dialog to edit list of custom framerates."""
        dialog = PreferencesDialog(self._conf.framerates, parent)
        gaupol.util.run_dialog(dialog)
        self._conf.framerates = list(dialog.get_framerates())
        dialog.destroy()
        self._remove_framerates()
        self._add_framerates()

    def teardown(self, application):
        """End use of extension with `application`."""
        self._remove_framerates()
        self._clear_attributes()
