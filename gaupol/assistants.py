# Copyright (C) 2007-2008,2010 Osmo Salomaa
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

"""Assistant to guide through multiple text correction tasks."""

from __future__ import division

import aeidon
import gaupol
import glib
import gtk
import os
import pango
import sys
_ = aeidon.i18n._

__all__ = ("TextAssistant", "TextAssistantPage")


class TextAssistantPage(gtk.VBox):

    """Baseclass for pages of :class:`TextAssistant`.

   :ivar description: One-line description used in the introduction page
   :ivar handle: Unique unlocalized name for internal references
   :ivar page_title: Short string used as configuration page title
   :ivar page_type: A GTK+ assistant page type constant
   :ivar title: Short title used in the introduction page

    Of these attributes, :attr:`description`, :attr:`handle` and :attr:`title`
    are only required for pages of type :attr:`gtk.ASSISTANT_PAGE_CONTENT`.
    """

    def __init__(self, assistant):
        """Initialize a :class:`TextAssistantPage` object."""
        gtk.VBox.__init__(self)
        self.assistant = assistant
        self.description = None
        self.handle = None
        self.page_title = None
        self.page_type = None
        self.title = None
        self.set_border_width(12)


class BuilderPage(TextAssistantPage):

    """Baseclass for pages of :class:`TextAssistant` built with GtkBuilder."""

    _widgets = ()

    def __init__(self, assistant, basename):
        """Initialize a :class:`BuilderPage` object."""
        TextAssistantPage.__init__(self, assistant)
        ui_file_path = os.path.join(aeidon.DATA_DIR,
                                    "ui",
                                    "text-assistant",
                                    basename)

        self._builder = gtk.Builder()
        self._builder.set_translation_domain("gaupol")
        self._builder.add_from_file(ui_file_path)
        self._builder.connect_signals(self)
        self._set_attributes(self._widgets)
        self._builder.get_object("vbox").reparent(self)

    def _set_attributes(self, widgets):
        """Assign all names in `widgets` as attributes of `self`."""
        for name in widgets:
            widget = self._builder.get_object(name)
            setattr(self, "_%s" % name, widget)


class IntroductionPage(BuilderPage):

    """Page for listing all text correction tasks."""

    _widgets = ("all_radio",
                "current_radio",
                "main_radio",
                "selected_radio",
                "tran_radio",
                "tree_view")

    def __init__(self, assistant):
        """Initialize a :class:`IntroductionPage` object."""
        BuilderPage.__init__(self, assistant, "intro-page.ui")
        self.page_title = _("Select Tasks and Target")
        self.page_type = gtk.ASSISTANT_PAGE_INTRO
        self._init_tree_view()
        self._init_values()

    def _init_tree_view(self):
        """Initialize the tree view of tasks."""
        store = gtk.ListStore(object, bool, str)
        self._tree_view.set_model(store)
        selection = self._tree_view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        renderer = gtk.CellRendererToggle()
        renderer.props.activatable = True
        renderer.props.xpad = 6
        renderer.connect("toggled", self._on_tree_view_cell_toggled)
        column = gtk.TreeViewColumn("", renderer, active=1)
        self._tree_view.append_column(column)
        renderer = gtk.CellRendererText()
        renderer.props.ellipsize = pango.ELLIPSIZE_END
        column = gtk.TreeViewColumn("", renderer, markup=2)
        self._tree_view.append_column(column)

    def _init_values(self):
        """Initialize default values for widgets."""
        target = gaupol.conf.text_assistant.target
        self._all_radio.set_active(target == gaupol.targets.ALL)
        self._current_radio.set_active(target == gaupol.targets.CURRENT)
        self._selected_radio.set_active(target == gaupol.targets.SELECTED)
        field = gaupol.conf.text_assistant.field
        self._main_radio.set_active(field == gaupol.fields.MAIN_TEXT)
        self._tran_radio.set_active(field == gaupol.fields.TRAN_TEXT)

    def _on_all_radio_toggled(self, *args):
        """Save the selected target."""
        gaupol.conf.text_assistant.target = self.get_target()

    def _on_current_radio_toggled(self, *args):
        """Save the selected target."""
        gaupol.conf.text_assistant.target = self.get_target()

    def _on_main_radio_toggled(self, *args):
        """Save the selected field."""
        gaupol.conf.text_assistant.field = self.get_field()

    def _on_selected_radio_toggled(self, *args):
        """Save the selected target."""
        gaupol.conf.text_assistant.target = self.get_target()

    def _on_tran_radio_toggled(self, *args):
        """Save the selected field."""
        gaupol.conf.text_assistant.field = self.get_field()

    def _on_tree_view_cell_toggled(self, renderer, row):
        """Toggle and save task check button value."""
        store = self._tree_view.get_model()
        store[row][1] = not store[row][1]
        store[row][0].props.visible = store[row][1]
        pages = [x.handle for x in self.get_selected_pages()]
        gaupol.conf.text_assistant.pages = pages

    def get_field(self):
        """Return the selected field."""
        if self._main_radio.get_active():
            return gaupol.fields.MAIN_TEXT
        if self._tran_radio.get_active():
            return gaupol.fields.TRAN_TEXT
        raise ValueError("Invalid field radio state")

    def get_selected_pages(self):
        """Return selected content pages."""
        store = self._tree_view.get_model()
        return [x[0] for x in store if x[1]]

    def get_target(self):
        """Return the selected target."""
        if self._selected_radio.get_active():
            return gaupol.targets.SELECTED
        if self._current_radio.get_active():
            return gaupol.targets.CURRENT
        if self._all_radio.get_active():
            return gaupol.targets.ALL
        raise ValueError("Invalid target radio state")

    def populate_tree_view(self, content_pages):
        """Populate the tree view with tasks from `content_pages`."""
        self._tree_view.get_model().clear()
        store = self._tree_view.get_model()
        pages = gaupol.conf.text_assistant.pages
        for page in content_pages:
            title = glib.markup_escape_text(page.title)
            description = glib.markup_escape_text(page.description)
            markup = "<b>%s</b>\n%s" % (title, description)
            page.props.visible = (page.handle in pages)
            store.append((page, page.handle in pages, markup))
        self._tree_view.get_selection().unselect_all()


class LocalePage(BuilderPage):

    """Page with script, language and coutry based pattern selection."""

    __metaclass__ = gaupol.ContractualGObject
    _ui_file_basename = NotImplementedError

    _widgets = ("country_combo",
                "country_label",
                "language_combo",
                "language_label",
                "script_combo",
                "script_label",
                "tree_view")

    def __init__(self, assistant):
        """Initialize a :class:`LocalePage` object."""
        BuilderPage.__init__(self, assistant, self._ui_file_basename)
        self.conf = None
        self._init_attributes()
        self._init_tree_view()
        self._init_combo_boxes()
        self._init_values()

    def _filter_patterns(self, patterns):
        """Return a subset of `patterns` to show."""
        return patterns

    def _get_country_ensure(self, value):
        if value is not None:
            assert aeidon.countries.is_valid(value)

    def _get_country(self):
        """Return the selected country or ``None``."""
        if not self._country_combo.props.sensitive: return None
        index = self._country_combo.get_active()
        if index < 0: return None
        store = self._country_combo.get_model()
        value = store[index][0]
        return (None if value == "other" else value)

    def _get_language_ensure(self, value):
        if value is not None:
            assert aeidon.languages.is_valid(value)

    def _get_language(self):
        """Return the selected language or ``None``."""
        if not self._language_combo.props.sensitive: return None
        index = self._language_combo.get_active()
        if index < 0: return None
        store = self._language_combo.get_model()
        value = store[index][0]
        return (None if value == "other" else value)

    def _get_script_ensure(self, value):
        if value is not None:
            assert aeidon.scripts.is_valid(value)

    def _get_script(self):
        """Return the selected script or ``None``."""
        if not self._script_combo.props.sensitive: return None
        index = self._script_combo.get_active()
        if index < 0: return None
        store = self._script_combo.get_model()
        value = store[index][0]
        return (None if value == "other" else value)

    def _init_attributes(self):
        """Initialize values of page attributes."""
        raise NotImplementedError

    def _init_combo(self, combo_box):
        """Initialize `combo_box` and populate with `items`."""
        store = gtk.ListStore(str, str)
        combo_box.set_model(store)
        renderer = gtk.CellRendererText()
        combo_box.pack_start(renderer, True)
        combo_box.add_attribute(renderer, "text", 1)
        combo_box.set_row_separator_func(gaupol.util.separate_combo)

    def _init_combo_boxes(self):
        """Initialize and populate combo boxes."""
        self._init_combo(self._script_combo)
        self._init_combo(self._language_combo)
        self._init_combo(self._country_combo)
        self._populate_script_combo()
        self._populate_language_combo()
        self._populate_country_combo()

    def _init_tree_view(self):
        """Initialize the tree view of individual corrections."""
        store = gtk.ListStore(object, bool, bool, str)
        store_filter = store.filter_new()
        store_filter.set_visible_column(1)
        self._tree_view.set_model(store_filter)
        selection = self._tree_view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        renderer = gtk.CellRendererToggle()
        renderer.props.activatable = True
        renderer.props.xpad = 6
        renderer.connect("toggled", self._on_tree_view_cell_toggled)
        column = gtk.TreeViewColumn("", renderer, active=2)
        self._tree_view.append_column(column)
        renderer = gtk.CellRendererText()
        renderer.props.ellipsize = pango.ELLIPSIZE_END
        column = gtk.TreeViewColumn("", renderer, markup=3)
        self._tree_view.append_column(column)

    def _init_values(self):
        """Initialize default values for widgets."""
        pass

    def _on_country_combo_changed(self, combo_box):
        """Populate the tree view with a subset patterns."""
        self.conf.country = self._get_country() or ""
        self._populate_tree_view()

    def _on_language_combo_changed(self, combo_box):
        """Populate the tree view with a subset patterns."""
        language = self._get_language()
        sensitive = (language is not None)
        self._populate_country_combo()
        self._country_combo.set_sensitive(sensitive)
        self._country_label.set_sensitive(sensitive)
        self.conf.language = language or ""
        self._populate_tree_view()

    def _on_script_combo_changed(self, combo_box):
        """Populate the tree view with a subset patterns."""
        script = self._get_script()
        sensitive = (script is not None)
        self._populate_language_combo()
        self._language_combo.set_sensitive(sensitive)
        self._language_label.set_sensitive(sensitive)
        language = self._get_language()
        sensitive = (sensitive and (language is not None))
        self._populate_country_combo()
        self._country_combo.set_sensitive(sensitive)
        self._country_label.set_sensitive(sensitive)
        self.conf.script = script or ""
        self._populate_tree_view()

    def _on_tree_view_cell_toggled(self, renderer, path):
        """Toggle the check button value."""
        store_filter = self._tree_view.get_model()
        store = store_filter.get_model()
        row = store_filter.convert_path_to_child_path(path)[0]
        name = store[row][0].get_name(False)
        enabled = not store[row][2]
        for i in range(len(store)):
            # Toggle all patterns with the same name.
            if store[i][0].get_name(False) == name:
                store[i][0].enabled = enabled
                store[i][2] = enabled

    def _populate_combo(self, combo_box, items, active):
        """Populate `combo_box` with `items`."""
        store = combo_box.get_model()
        combo_box.set_model(None)
        store.clear()
        for code, name in items:
            store.append((code, name))
        if len(store) > 0:
            store.append((gaupol.COMBO_SEPARATOR, ""))
        store.append(("other", _("Other")))
        combo_box.set_active(len(store) - 1)
        for i in range(len(store)):
            if (store[i][0] == active) and active:
                combo_box.set_active(i)
        combo_box.set_model(store)

    def _populate_country_combo(self):
        """Populate the country combo box."""
        script = self._get_script()
        language = self._get_language()
        codes = self._manager.get_countries(script, language)
        names = map(aeidon.countries.code_to_name, codes)
        items = [(codes[i], names[i]) for i in range(len(codes))]
        items.sort(key=lambda x: x[1])
        self._populate_combo(self._country_combo, items, self.conf.country)

    def _populate_language_combo(self):
        """Populate the language combo box."""
        script = self._get_script()
        codes = self._manager.get_languages(script)
        names = map(aeidon.languages.code_to_name, codes)
        items = [(codes[i], names[i]) for i in range(len(codes))]
        items.sort(key=lambda x: x[1])
        self._populate_combo(self._language_combo, items, self.conf.language)

    def _populate_script_combo(self):
        """Populate the script combo box."""
        codes = self._manager.get_scripts()
        names = map(aeidon.scripts.code_to_name, codes)
        items = [(codes[i], names[i]) for i in range(len(codes))]
        items.sort(key=lambda x: x[1])
        self._populate_combo(self._script_combo, items, self.conf.script)

    def _populate_tree_view(self):
        """Populate the tree view with a subset patterns."""
        store_filter = self._tree_view.get_model()
        store = store_filter.get_model()
        store.clear()
        patterns = self._manager.get_patterns(self._get_script(),
                                              self._get_language(),
                                              self._get_country())

        patterns = self._filter_patterns(patterns)
        names_entered = set(())
        for pattern in patterns:
            name = pattern.get_name()
            visible = not (name in names_entered)
            names_entered.add(name)
            name = glib.markup_escape_text(name)
            description = pattern.get_description()
            description = glib.markup_escape_text(description)
            markup = "<b>%s</b>\n%s" % (name, description)
            store.append((pattern, visible, pattern.enabled, markup))
        self._tree_view.get_selection().unselect_all()

    def correct_texts(self, project, indices, doc):
        """Correct texts in `project`."""
        raise NotImplementedError


class CapitalizationPage(LocalePage):

    """Page for capitalizing texts in subtitles."""

    _ui_file_basename = "capitalization-page.ui"

    def _init_attributes(self):
        """Initialize values of page attributes."""
        self._manager = aeidon.PatternManager("capitalization")
        self.conf = gaupol.conf.capitalization
        self.description = _("Capitalize texts written in lower case")
        self.handle = "capitalization"
        self.page_title = _("Select Capitalization Patterns")
        self.page_type = gtk.ASSISTANT_PAGE_CONTENT
        self.title = _("Capitalize texts")

    def correct_texts(self, project, indices, doc):
        """Correct texts in `project`."""
        codes = (self._get_script(),
                 self._get_language(),
                 self._get_country())

        self._manager.save_config(*codes)
        patterns = self._manager.get_patterns(*codes)
        project.capitalize(indices, doc, patterns)


class CommonErrorPage(LocalePage):

    """Page for correcting common human and OCR errors."""

    _ui_file_basename = "common-error-page.ui"
    _widgets = ("human_check", "ocr_check") + LocalePage._widgets

    def _init_attributes(self):
        """Initialize values of page attributes."""
        self._manager = aeidon.PatternManager("common-error")
        self.conf = gaupol.conf.common_error
        self.description = _("Correct common errors made by humans "
                             "or image recognition software")

        self.handle = "common-error"
        self.page_title = _("Select Common Error Patterns")
        self.page_type = gtk.ASSISTANT_PAGE_CONTENT
        self.title = _("Correct common errors")

    def _filter_patterns(self, patterns):
        """Return a subset of `patterns` to show."""
        def use_pattern(pattern):
            classes = set(pattern.get_field_list("Classes"))
            return(bool(classes.intersection(set(self.conf.classes))))
        return filter(use_pattern, patterns)

    def _init_values(self):
        """Initialize default values for widgets."""
        self._human_check.set_active("Human" in self.conf.classes)
        self._ocr_check.set_active("OCR" in self.conf.classes)

    def _on_human_check_toggled(self, check_button):
        """Populate the tree view with a subset patterns."""
        if check_button.get_active():
            self.conf.classes.append("Human")
            self.conf.classes = sorted(set(self.conf.classes))
        elif "Human" in self.conf.classes:
            self.conf.classes.remove("Human")
        self._populate_tree_view()

    def _on_ocr_check_toggled(self, check_button):
        """Populate the tree view with a subset patterns."""
        if check_button.get_active():
            self.conf.classes.append("OCR")
            self.conf.classes = sorted(set(self.conf.classes))
        elif "OCR" in self.conf.classes:
            self.conf.classes.remove("OCR")
        self._populate_tree_view()

    def correct_texts(self, project, indices, doc):
        """Correct texts in `project`."""
        codes = (self._get_script(),
                 self._get_language(),
                 self._get_country())

        self._manager.save_config(*codes)
        patterns = self._manager.get_patterns(*codes)
        project.correct_common_errors(indices, doc, patterns)


class HearingImpairedPage(LocalePage):

    """Page for removing hearing impaired parts from subtitles."""

    _ui_file_basename = "hearing-impaired-page.ui"

    def _init_attributes(self):
        """Initialize values of page attributes."""
        self._manager = aeidon.PatternManager("hearing-impaired")
        self.conf = gaupol.conf.hearing_impaired
        self.description = _("Remove explanatory texts meant "
                             "for the hearing impaired")

        self.handle = "hearing-impaired"
        self.page_title = _("Select Hearing Impaired Patterns")
        self.page_type = gtk.ASSISTANT_PAGE_CONTENT
        self.title = _("Remove hearing impaired texts")

    def correct_texts(self, project, indices, doc):
        """Correct texts in `project`."""
        codes = (self._get_script(),
                 self._get_language(),
                 self._get_country())

        self._manager.save_config(*codes)
        patterns = self._manager.get_patterns(*codes)
        project.remove_hearing_impaired(indices, doc, patterns)


class JoinSplitWordsPage(BuilderPage):

    """Page for joining or splitting words based on spell-check suggestions."""

    __metaclass__ = gaupol.ContractualGObject
    _widgets = ("language_button", "join_check", "split_check")

    def __init___require(self, assistant):
        assert aeidon.util.enchant_available()

    def __init__(self, assistant):
        """Initialize a JoinSplitWordsPage object."""
        BuilderPage.__init__(self, assistant, "join-split-page.ui")
        self.description = _("Use spell-check suggestions to fix whitespace "
                             "detection errors of image recognition software")

        self.handle = "join-split-words"
        self.page_title = _("Set Options for Joining and Splitting Words")
        self.page_type = gtk.ASSISTANT_PAGE_CONTENT
        self.title = _("Join or Split Words")
        self._init_values()

    def _init_values(self):
        """Initialize default values for widgets."""
        language = gaupol.conf.spell_check.language
        try: label = aeidon.locales.code_to_name(language)
        except LookupError: label = self._language_button.get_label()
        self._set_language_button_label(label)
        self._join_check.set_active(gaupol.conf.join_split_words.join)
        self._split_check.set_active(gaupol.conf.join_split_words.split)

    def _on_join_check_toggled(self, check_button, *args):
        """Save value of join option."""
        gaupol.conf.join_split_words.join = check_button.get_active()

    def _on_language_button_clicked(self, button, *args):
        """Show a language dialog and update `button` label."""
        gaupol.util.set_cursor_busy(self.assistant)
        dialog = gaupol.LanguageDialog(self.assistant, False)
        gaupol.util.set_cursor_normal(self.assistant)
        gaupol.util.flash_dialog(dialog)
        language = gaupol.conf.spell_check.language
        try: label = aeidon.locales.code_to_name(language)
        except LookupError: label = self._language_button.get_label()
        self._set_language_button_label(label)

    def _on_split_check_toggled(self, check_button, *args):
        """Save value of split option."""
        gaupol.conf.join_split_words.split = check_button.get_active()

    def _set_language_button_label(self, text):
        """Set `text` as the language button label."""
        hbox = self._language_button.get_child()
        label = hbox.get_children()[0]
        label.set_text(text)

    def _show_error_dialog(self, message):
        """Show an error dialog after failing to load dictionary."""
        language = gaupol.conf.spell_check.language
        try: name = aeidon.locales.code_to_name(language)
        except LookupError: name = language
        title = _('Failed to load dictionary for language "%s"') % name
        dialog = gaupol.ErrorDialog(self.parent, title, message)
        dialog.add_button(gtk.STOCK_OK, gtk.RESPONSE_OK)
        gaupol.util.flash_dialog(dialog)

    def correct_texts(self, project, indices, doc):
        """Correct texts in `project`."""
        import enchant
        language = gaupol.conf.spell_check.language
        if gaupol.conf.join_split_words.join:
            try: project.spell_check_join_words(indices, doc, language)
            except enchant.Error as message:
                return self._show_error_dialog(message)
        if gaupol.conf.join_split_words.split:
            try: project.spell_check_split_words(indices, doc, language)
            except enchant.Error as message:
                return self._show_error_dialog(message)


class LineBreakPage(LocalePage):

    """Page for breaking text into lines."""

    _ui_file_basename = "line-break-page.ui"

    def _init_attributes(self):
        """Initialize values of page attributes."""
        self._manager = aeidon.PatternManager("line-break")
        self.conf = gaupol.conf.line_break
        self.description = _("Break text into lines of defined length")
        self.handle = "line-break"
        self.page_title = _("Select Line-Break Patterns")
        self.page_type = gtk.ASSISTANT_PAGE_CONTENT
        self.title = _("Break lines")

    @property
    def _max_skip_length(self):
        """Return the maximum line length to skip."""
        if self.conf.use_skip_max_length:
            return self.conf.skip_max_length
        return sys.maxint

    @property
    def _max_skip_lines(self):
        """Return the maximum amount of lines to skip."""
        if self.conf.use_skip_max_lines:
            return self.conf.skip_max_lines
        return sys.maxint

    def correct_texts(self, project, indices, doc):
        """Correct texts in `project`."""
        codes = (self._get_script(),
                 self._get_language(),
                 self._get_country())

        self._manager.save_config(*codes)
        patterns = self._manager.get_patterns(*codes)
        length_func = gaupol.ruler.get_length_function(self.conf.length_unit)
        project.break_lines(indices=indices,
                            doc=doc,
                            patterns=patterns,
                            length_func=length_func,
                            max_length=self.conf.max_length,
                            max_lines=self.conf.max_lines,
                            max_deviation=self.conf.max_deviation,
                            skip=(self.conf.use_skip_max_length or
                                  self.conf.use_skip_max_lines),

                            max_skip_length=self._max_skip_length,
                            max_skip_lines=self._max_skip_lines)


class LineBreakOptionsPage(BuilderPage):

    """Page for editing line-break options."""

    _widgets = ("max_length_spin",
                "max_lines_spin",
                "max_skip_length_spin",
                "max_skip_lines_spin",
                "skip_length_check",
                "skip_lines_check",
                "skip_unit_combo",
                "unit_combo")

    def __init__(self, assistant):
        """Initialize a LineBreakOptionsPage object."""
        BuilderPage.__init__(self, assistant, "line-break-opts-page.ui")
        self.conf = gaupol.conf.line_break
        self.page_title = _("Set Line-Break Options")
        self.page_type = gtk.ASSISTANT_PAGE_CONTENT
        self._init_unit_combo(self._unit_combo)
        self._init_unit_combo(self._skip_unit_combo)
        self._init_values()

    def _init_unit_combo(self, combo_box):
        """Initialize line length unit `combo_box`."""
        store = gtk.ListStore(str)
        combo_box.set_model(store)
        for label in (x.label for x in gaupol.length_units):
            store.append((label,))
        renderer = gtk.CellRendererText()
        combo_box.pack_start(renderer, True)
        combo_box.add_attribute(renderer, "text", 0)

    def _init_values(self):
        """Initialize default values for widgets."""
        self._max_length_spin.set_value(self.conf.max_length)
        self._max_lines_spin.set_value(self.conf.max_lines)
        self._max_skip_length_spin.set_value(self.conf.skip_max_length)
        self._max_skip_lines_spin.set_value(self.conf.skip_max_lines)
        self._skip_length_check.set_active(self.conf.use_skip_max_length)
        self._skip_lines_check.set_active(self.conf.use_skip_max_lines)
        self._skip_unit_combo.set_active(self.conf.length_unit)
        self._unit_combo.set_active(self.conf.length_unit)

    def _on_max_length_spin_value_changed(self, spin_button):
        """Save maximum line length value."""
        self.conf.max_length = spin_button.get_value_as_int()

    def _on_max_lines_spin_value_changed(self, spin_button):
        """Save maximum line amount value."""
        self.conf.max_lines = spin_button.get_value_as_int()

    def _on_max_skip_length_spin_value_changed(self, spin_button):
        """Save maximum line length to skip value."""
        self.conf.skip_max_length = spin_button.get_value_as_int()

    def _on_max_skip_lines_spin_value_changed(self, spin_button):
        """Save maximum line amount to skip value."""
        self.conf.skip_max_lines = spin_button.get_value_as_int()

    def _on_skip_length_check_toggled(self, check_button):
        """Save skip by line length value."""
        use_skip = check_button.get_active()
        self.conf.use_skip_max_length = use_skip
        self._max_skip_length_spin.set_sensitive(use_skip)
        self._skip_unit_combo.set_sensitive(use_skip)

    def _on_skip_lines_check_toggled(self, check_button):
        """Save skip by line amount value."""
        use_skip = check_button.get_active()
        self.conf.use_skip_max_lines = use_skip
        self._max_skip_lines_spin.set_sensitive(use_skip)

    def _on_skip_unit_combo_changed(self, combo_box):
        """Save and sync length unit value of `combo_box."""
        index = combo_box.get_active()
        length_unit = gaupol.length_units[index]
        self.conf.length_unit = length_unit
        self._unit_combo.set_active(index)

    def _on_unit_combo_changed(self, combo_box):
        """Save and sync length unit value of `combo_box."""
        index = combo_box.get_active()
        length_unit = gaupol.length_units[index]
        self.conf.length_unit = length_unit
        self._skip_unit_combo.set_active(index)


class ProgressPage(BuilderPage):

    """Page for showing progress of text corrections."""

    _widgets = ("message_label",
                "progress_bar",
                "status_label",
                "task_label")

    def __init__(self, assistant):
        """Initialize a :class:`ProgressPage` object."""
        BuilderPage.__init__(self, assistant, "progress-page.ui")
        self._current_task = None
        self._total_tasks = None
        self.page_title = _("Correcting Texts")
        self.page_type = gtk.ASSISTANT_PAGE_PROGRESS
        self._init_values()

    def _init_values(self):
        """Initalize default values for widgets."""
        message = _("Each task is now being run on each project.")
        self._message_label.set_text(message)
        self.reset(100)

    def bump_progress(self, n_tasks=1):
        """Bump the current progress by `n_tasks`."""
        self.set_progress(self._current_task + n_tasks)

    def reset(self, total, clear_text=False):
        """Set `total` as the amount of tasks to be run."""
        self._current_task = 0
        self._total_tasks = total
        self.set_progress(0, total)
        self.set_project_name("")
        self.set_task_name("")
        if clear_text:
            self._progress_bar.set_text("")
        gaupol.util.iterate_main()

    def set_progress(self, current, total=None):
        """Set current as the task progress status."""
        total = total or self._total_tasks
        fraction = (current / total if total > 0 else 0)
        self._progress_bar.set_fraction(fraction)
        text = _("%(current)d of %(total)d tasks complete")
        self._progress_bar.set_text(text % locals())
        self._current_task = current
        self._total_tasks = total
        gaupol.util.iterate_main()

    def set_project_name(self, name):
        """Set `name` as the currently checked project."""
        text = _("Project: %s") % name
        text = glib.markup_escape_text(text)
        self._status_label.set_markup("<i>%s</i>" % text)
        gaupol.util.iterate_main()

    def set_task_name(self, name):
        """Set `name` as the currently performed task."""
        text = _("Task: %s") % name
        text = glib.markup_escape_text(text)
        self._task_label.set_markup("<i>%s</i>" % text)
        gaupol.util.iterate_main()


class ConfirmationPage(BuilderPage):

    """Page to confirm changes made after performing all tasks."""

    _widgets = ("mark_all_button",
                "preview_button",
                "remove_check",
                "tree_view",
                "unmark_all_button")

    def __init__(self, assistant):
        """Initialize a :class:`ConfirmationPage` object."""
        BuilderPage.__init__(self, assistant, "confirmation-page.ui")
        self.application = None
        self.conf = gaupol.conf.text_assistant
        self.doc = None
        self.page_title = _("Confirm Changes")
        self.page_type = gtk.ASSISTANT_PAGE_CONFIRM
        self._init_tree_view()
        self._init_values()

    def _add_text_column(self, index, title):
        """Add a multiline text column to the tree view."""
        renderer = gaupol.MultilineCellRenderer()
        renderer.set_show_lengths(True)
        renderer.props.editable = (index == 4)
        renderer.props.ellipsize = pango.ELLIPSIZE_END
        renderer.props.font = gaupol.util.get_font()
        renderer.props.yalign = 0
        column = gtk.TreeViewColumn(title, renderer, text=index)
        column.set_resizable(True)
        column.props.expand = True
        self._tree_view.append_column(column)

    def _can_preview(self):
        """Return ``True`` if preview is possible."""
        row = self._get_selected_row()
        if row is None: return False
        page = self._tree_view.get_model()[row][0]
        if page is None: return False
        return all((page.project.video_path, page.project.main_file))

    def _get_selected_row(self):
        """Return the selected row in the tree view or ``None``."""
        selection = self._tree_view.get_selection()
        store, itr = selection.get_selected()
        if itr is None: return None
        return store.get_path(itr)[0]

    def _init_tree_view(self):
        """Initialize the tree view of corrections."""
        # page, index, accept, original tex, new text
        store = gtk.ListStore(object, int, bool, str, str)
        self._tree_view.set_model(store)
        selection = self._tree_view.get_selection()
        selection.set_mode(gtk.SELECTION_SINGLE)
        selection.connect("changed", self._on_tree_view_selection_changed)
        renderer = gtk.CellRendererToggle()
        renderer.props.activatable = True
        renderer.props.xpad = 6
        renderer.connect("toggled", self._on_tree_view_cell_toggled)
        column = gtk.TreeViewColumn(_("Accept"), renderer, active=2)
        column.set_resizable(True)
        self._tree_view.append_column(column)
        self._add_text_column(3, _("Original Text"))
        self._add_text_column(4, _("Corrected Text"))
        column = self._tree_view.get_column(2)
        renderer = column.get_cell_renderers()[0]
        renderer.connect("edited", self._on_tree_view_cell_edited)

    def _init_values(self):
        """Initialize default values for widgets."""
        self._remove_check.set_active(self.conf.remove_blank)
        self._preview_button.set_sensitive(False)

    def _on_mark_all_button_clicked(self, *args):
        """Set all accept column values to ``True``."""
        store = self._tree_view.get_model()
        for i in range(len(store)):
            store[i][2] = True

    def _on_preview_button_clicked(self, *args):
        """Preview original text in a video player."""
        row = self._get_selected_row()
        page = self._tree_view.get_model()[row][0]
        index = self._tree_view.get_model()[row][1]
        position = page.project.subtitles[index].start
        self.application.preview(page, position, self.doc)

    def _on_remove_check_toggled(self, check_button):
        """Save remove blank subtitles value."""
        self.conf.remove_blank = check_button.get_active()

    def _on_tree_view_cell_edited(self, renderer, row, text):
        """Edit text in the corrected text column."""
        store = self._tree_view.get_model()
        store[row][4] = unicode(text)

    def _on_tree_view_cell_toggled(self, renderer, row):
        """Toggle accept column value."""
        store = self._tree_view.get_model()
        store[row][2] = not store[row][2]

    def _on_tree_view_selection_changed(self, *args):
        """Update preview button sensitivity."""
        self._preview_button.set_sensitive(self._can_preview())

    def _on_unmark_all_button_clicked(self, *args):
        """Set all accept column values to ``False``."""
        store = self._tree_view.get_model()
        for i in range(len(store)):
            store[i][2] = False

    def get_confirmed_changes(self):
        """Return a sequence of changes marked as accepted."""
        changes = []
        store = self._tree_view.get_model()
        for row in (x for x in store if x[2]):
            page, index, accept, orig, new = row
            changes.append((page, index, orig, new))
        return tuple(changes)

    def populate_tree_view(self, changes):
        """Populate the tree view of changes to texts."""
        self._tree_view.get_model().clear()
        store = self._tree_view.get_model()
        for page, index, orig, new in changes:
            store.append((page, index, True, orig, new))
        self._tree_view.get_selection().unselect_all()


class TextAssistant(gtk.Assistant):

    """Assistant to guide through multiple text correction tasks."""

    def __init__(self, parent, application):
        """Initialize a TextAssistant object."""
        gtk.Assistant.__init__(self)
        self._confirmation_page = ConfirmationPage(self)
        self._introduction_page = IntroductionPage(self)
        self._previous_page = None
        self._progress_page = ProgressPage(self)
        self.application = application
        self._init_properties()
        self._init_signal_handlers()
        self.resize(*gaupol.conf.text_assistant.size)
        if gaupol.conf.text_assistant.maximized:
            self.maximize()
        self.set_modal(True)
        self.set_position(gtk.WIN_POS_CENTER_ON_PARENT)
        self.set_transient_for(parent)

    def _copy_project(self, project):
        """Return a copy of `project` with some same properties."""
        copy = aeidon.Project(project.framerate)
        copy.main_file = project.main_file
        copy.tran_file = project.tran_file
        copy.subtitles = [x.copy() for x in project.subtitles]
        return copy

    def _correct_texts(self, assistant_pages):
        """Correct texts by all pages and present changes."""
        changes = []
        target = self._introduction_page.get_target()
        field = self._introduction_page.get_field()
        doc = gaupol.util.text_field_to_document(field)
        rows = self.application.get_target_rows(target)
        application_pages = self.application.get_target_pages(target)
        total = len(application_pages) * len(assistant_pages)
        self._progress_page.reset(total)
        for application_page in application_pages:
            name = application_page.get_main_basename()
            self._progress_page.set_project_name(name)
            project = application_page.project
            # Initialize a dummy project to apply corrections in
            # to be able to present those corrections for approval and
            # to finally be able to apply only approved corrections.
            dummy = self._copy_project(project)
            static_subtitles = dummy.subtitles[:]
            for page in assistant_pages:
                self._progress_page.set_task_name(page.title)
                page.correct_texts(dummy, rows, doc)
                self._progress_page.bump_progress()
            for i in range(len(static_subtitles)):
                orig = project.subtitles[i].get_text(doc)
                new = static_subtitles[i].get_text(doc)
                if orig == new: continue
                changes.append((application_page, i, orig, new))
        self._prepare_confirmation_page(doc, changes)
        self.set_current_page(self.get_current_page() + 1)

    def _init_properties(self):
        """Initialize assistant properties."""
        self.set_border_width(12)
        self.set_title(_("Correct Texts"))
        self.add_page(self._introduction_page)
        self.add_page(HearingImpairedPage(self))
        if aeidon.util.enchant_available():
            self.add_page(JoinSplitWordsPage(self))
        self.add_page(CommonErrorPage(self))
        self.add_page(CapitalizationPage(self))
        self.application.emit("text-assistant-request-pages", self)
        self.add_pages((LineBreakPage(self), LineBreakOptionsPage(self)))
        self.add_page(self._progress_page)
        self.add_page(self._confirmation_page)

    def _init_signal_handlers(self):
        """Initialize signal handlers."""
        aeidon.util.connect(self, self, "apply")
        aeidon.util.connect(self, self, "cancel")
        aeidon.util.connect(self, self, "close")
        aeidon.util.connect(self, self, "prepare")
        aeidon.util.connect(self, self, "window-state-event")

    def _on_apply(self, *args):
        """Apply accepted changes to projects."""
        gaupol.util.set_cursor_busy(self)
        edits = removals = 0
        changes = self._confirmation_page.get_confirmed_changes()
        target = self._introduction_page.get_target()
        application_pages = self.application.get_target_pages(target)
        field = self._introduction_page.get_field()
        doc = gaupol.util.text_field_to_document(field)
        description = _("Correcting texts")
        register = aeidon.registers.DO
        for page in application_pages:
            indices = [x[1] for x in changes if x[0] is page]
            texts = [x[3] for x in changes if x[0] is page]
            if indices and texts:
                page.project.replace_texts(indices, doc, texts)
                page.project.set_action_description(register, description)
                edits += len(indices)
            indices = [x for i, x in enumerate(indices) if not texts[i]]
            if indices and gaupol.conf.text_assistant.remove_blank:
                page.project.remove_subtitles(indices)
                page.project.group_actions(register, 2, description)
                removals += len(indices)
            page.view.columns_autosize()
        edits = edits - removals
        message = _("Edited %(edits)d and removed %(removals)d subtitles")
        self.application.flash_message(message % locals())
        gaupol.util.set_cursor_normal(self)

    def _on_cancel(self, *args):
        """Destroy assistant."""
        self._save_window_geometry()
        self.destroy()

    def _on_close(self, *args):
        """Destroy assistant."""
        self._save_window_geometry()
        self.destroy()

    def _on_prepare(self, assistant, page):
        """Prepare `page` to be shown next."""
        previous_page = self._previous_page
        self._previous_page = page
        if page is self._introduction_page:
            return self._prepare_introduction_page()
        pages = self._introduction_page.get_selected_pages()
        if page is self._progress_page:
            if previous_page is not self._confirmation_page:
                return self._prepare_progress_page(pages)

    def _on_window_state_event(self, window, event):
        """Save window maximization."""
        state = event.new_window_state
        maximized = bool(state & gtk.gdk.WINDOW_STATE_MAXIMIZED)
        gaupol.conf.text_assistant.maximized = maximized

    def _prepare_confirmation_page(self, doc, changes):
        """Present `changes` and activate confirmation page."""
        count = len(changes)
        title = aeidon.i18n.ngettext("Confirm %d Change",
                                     "Confirm %d Changes", count) % count

        self.set_page_title(self._confirmation_page, title)
        self._confirmation_page.application = self.application
        self._confirmation_page.doc = doc
        self._confirmation_page.populate_tree_view(changes)
        self.set_page_complete(self._progress_page, True)

    def _prepare_introduction_page(self):
        """Prepare introduction page content."""
        n = self.get_n_pages()
        pages = map(self.get_nth_page, range(n))
        pages.remove(self._introduction_page)
        pages.remove(self._progress_page)
        pages.remove(self._confirmation_page)
        pages = filter(lambda x: hasattr(x, "correct_texts"), pages)
        self._introduction_page.populate_tree_view(pages)

    def _prepare_progress_page(self, pages):
        """Prepare progress page for `pages`."""
        self._progress_page.reset(0, True)
        self.set_page_complete(self._progress_page, False)
        gaupol.util.delay_add(10, self._correct_texts, pages)

    def _save_window_geometry(self):
        """Save the geometry of the assistant window."""
        if not gaupol.conf.text_assistant.maximized:
            gaupol.conf.text_assistant.size = list(self.get_size())

    def add_page(self, page):
        """Add `page` and configure its properties."""
        page.show_all()
        self.append_page(page)
        self.set_page_type(page, page.page_type)
        self.set_page_title(page, page.page_title)
        if page.page_type != gtk.ASSISTANT_PAGE_PROGRESS:
            self.set_page_complete(page, True)

    def add_pages(self, pages):
        """Add associated `pages` and configure their properties.

        The first one of `pages` must have a "correct_texts" attribute.
        The visibilities of other pages are kept in sync with the first page.
        """
        map(self.add_page, pages)
        def on_notify_visible(page, prop, pages):
            for page in pages[1:]:
                page.props.visible = pages[0].props.visible
        pages[0].connect("notify::visible", on_notify_visible, pages)
