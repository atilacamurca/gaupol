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

"""Miscellaneous functions and decorators."""

from __future__ import division

import aeidon
import gaupol
import glib
import gtk
import inspect
import pango
import sys
import traceback
import webbrowser


def char_to_px(nchar, font=None):
    """Convert characters to pixels."""
    if nchar < 0: return nchar
    label = gtk.Label("etaoin shrdlu")
    if font is not None:
        set_label_font(label, font)
    width = label.get_layout().get_pixel_size()[0]
    return int(round(nchar * (width / 13)))

def delay_add(delay, function, *args, **kwargs):
    """Call `function` with `args` and `kwargs` once after `delay` (ms).

    Return integer ID of the event source from :func:`glib.timeout_add`.
    """
    def call_function(*args, **kwargs):
        function(*args, **kwargs)
        return False
    return glib.timeout_add(delay, call_function, *args, **kwargs)

def document_to_text_field(doc):
    """Return :attr:`gaupol.fields` item corresponding to `doc`."""
    if doc == aeidon.documents.MAIN:
        return gaupol.fields.MAIN_TEXT
    if doc == aeidon.documents.TRAN:
        return gaupol.fields.TRAN_TEXT
    raise ValueError("Invalid document: %s" % repr(doc))

def flash_dialog(dialog):
    """Run `dialog`, destroy it and return response.

    This function is to be used always when a :class:`gtk.Dialog` is run so
    that unit tests can monkey-patch this function with one that returns a
    specified response without waiting for user input.
    """
    response = dialog.run()
    dialog.destroy()
    return response

def get_font():
    """Return custom font or blank string."""
    return (gaupol.conf.editor.custom_font if
            (gaupol.conf.editor.use_custom_font and
             gaupol.conf.editor.custom_font) else "")

def get_gst_version():
    """Return :mod:`gst` version number as string or ``None``."""
    try:
        import gst
        return ".".join(map(str, gst.version()))
    except Exception:
        return None

def get_preview_command():
    """Return command to use for lauching video player."""
    if gaupol.conf.preview.use_custom_command:
        return gaupol.conf.preview.custom_command
    if gaupol.conf.preview.force_utf_8:
        return gaupol.conf.preview.player.command_utf_8
    return gaupol.conf.preview.player.command

def get_pygst_version():
    """Return ``pygst`` version number as string or ``None``."""
    try:
        import gst
        return ".".join(map(str, gst.pygst_version))
    except Exception:
        return None

def get_text_view_size(text_view, font=""):
    """Return the width and height desired by `text_view`."""
    text_buffer = text_view.get_buffer()
    bounds = text_buffer.get_bounds()
    text = text_buffer.get_text(*bounds)
    label = gtk.Label(text)
    set_label_font(label, font)
    return label.size_request()

def get_tree_view_size(tree_view):
    """Return the width and height desired by `tree_view`."""
    scroller = tree_view.get_parent()
    policy = scroller.get_policy()
    scroller.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
    width, height = scroller.size_request()
    scroller.set_policy(*policy)
    return width, height

@aeidon.deco.once
def gst_available():
    """Return ``True`` if :mod:`gst` module is available."""
    try:
        import gst
        return True
    except Exception:
        return False

@aeidon.deco.once
def gtkspell_available():
    """Return ``True`` if :mod:`gtkspell` module is available."""
    try:
        import gtkspell
        return True
    except Exception:
        return False

def install_module(name, obj):
    """Install `obj`'s module into the :mod:`gaupol` namespace.

    Typical call is of form::

        gaupol.util.install_module("foo", lambda: None)
    """
    gaupol.__dict__[name] = inspect.getmodule(obj)

def iterate_main():
    """Iterate the GTK+ main loop while events are pending."""
    while gtk.events_pending():
        gtk.main_iteration()

def lines_to_px(nlines, font=None):
    """Convert lines to pixels."""
    if nlines < 0: return nlines
    label = gtk.Label("ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz")
    if font is not None:
        set_label_font(label, font)
    height = label.get_layout().get_pixel_size()[1]
    return int(round(nlines * height))

@aeidon.deco.once
def pocketsphinx_available():
    """Return ``True`` if `pocketsphinx` gstreamer plugin is available."""
    try:
        import gst
        return gst.plugin_load_by_name("pocketsphinx") is not None
    except Exception:
        return False

def prepare_text_view(text_view):
    """Set spell-check, line-length margin and font properties."""
    if gaupol.util.gtkspell_available() and gaupol.conf.spell_check.inline:
        import gtkspell
        spell = gtkspell.Spell(text_view)
        try: spell.set_language(gaupol.conf.spell_check.language)
        except Exception: spell.detach()

    connect = gaupol.conf.editor.connect
    def update_margin(section, value, text_view):
        if gaupol.conf.editor.show_lengths_edit:
            return gaupol.ruler.connect_text_view(text_view)
        return gaupol.ruler.disconnect_text_view(text_view)

    connect("notify::show_lengths_edit", update_margin, text_view)
    update_margin(None, None, text_view)
    def update_font(section, value, text_view):
        set_widget_font(text_view, get_font())

    connect("notify::use_custom_font", update_font, text_view)
    connect("notify::custom_font", update_font, text_view)
    update_font(None, None, text_view)
    def update_spacing(section, value, text_view):
        if gaupol.conf.editor.show_lengths_cell:
            return text_view.set_pixels_above_lines(2)
        return text_view.set_pixels_above_lines(0)

    connect("notify::show_lengths_cell", update_spacing, text_view)
    update_spacing(None, None, text_view)

def raise_default(expression):
    """Raise :exc:`gaupol.Default` if expression evaluates to ``True``."""
    if expression:
        raise gaupol.Default

def run_dialog(dialog):
    """Run `dialog` and return response.

    This function is to be used always when a :class:`gtk.Dialog` is run so
    that unit tests can monkey patch this function with one that returns a
    specified response without waiting for user input.
    """
    return dialog.run()

def scale_to_content(container,
                     min_nchar=None,
                     min_nlines=None,
                     max_nchar=None,
                     max_nlines=None,
                     font=None):

    """Set `container`'s size by content, but limited by `min` and `max`."""
    # Vaguely account for possible scrollbars.
    bump = lambda x: x + 36
    if isinstance(container, gtk.TextView):
        width, height = map(bump, get_text_view_size(container))
    elif isinstance(container, gtk.TreeView):
        width, height = map(bump, get_tree_view_size(container))
    else:
        raise ValueError("Don't know what to do with container of type %s"
                         % repr(type(container)))

    if min_nchar is not None:
        min_width = char_to_px(min_nchar, font)
        width = max(width, min_width)
    if max_nchar is not None:
        max_width = char_to_px(max_nchar, font)
        width = min(width, max_width)
    if min_nlines is not None:
        min_height = lines_to_px(min_nlines, font)
        height = max(height, min_height)
    if max_nlines is not None:
        max_height = lines_to_px(max_nlines, font)
        height = min(height, max_height)
    container.set_size_request(width, height)

def scale_to_size(widget, nchar, nlines, font=None):
    """Set `widget`'s size to `nchar` and `nlines`."""
    widget.set_size_request(char_to_px(nchar, font),
                            lines_to_px(nlines, font))

def separate_combo(store, itr):
    """Separator function for combo box models."""
    return store.get_value(itr, 0) == gaupol.COMBO_SEPARATOR

def set_cursor_busy_require(window):
    assert hasattr(window, "window")

@aeidon.deco.contractual
def set_cursor_busy(window):
    """Set cursor busy when above window."""
    window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.WATCH))
    iterate_main()

def set_cursor_normal_require(window):
    assert hasattr(window, "window")

@aeidon.deco.contractual
def set_cursor_normal(window):
    """Set cursor normal when above window."""
    window.window.set_cursor(gtk.gdk.Cursor(gtk.gdk.LEFT_PTR))
    iterate_main()

def set_label_font(label, font):
    """Use `font` for `label`."""
    context = label.get_pango_context()
    font_desc = context.get_font_description()
    custom_font_desc = pango.FontDescription(font)
    font_desc.merge(custom_font_desc, True)
    attr = pango.AttrFontDesc(font_desc, 0, -1)
    attr_list = pango.AttrList()
    attr_list.insert(attr)
    label.set_attributes(attr_list)

def set_widget_font(widget, font):
    """Use `font` for `widget`."""
    context = widget.get_pango_context()
    font_desc = context.get_font_description()
    custom_font_desc = pango.FontDescription(font)
    font_desc.merge(custom_font_desc, True)
    widget.modify_font(font_desc)

def show_exception(exctype, value, tb):
    """Show exception traceback in :class:`gaupol.DebugDialog`.

    This function can be set as a :func:`sys.excepthook`.
    """
    traceback.print_exception(exctype, value, tb)
    if not isinstance(value, Exception): return
    try: # Avoid recursion.
        dialog = gaupol.DebugDialog()
        dialog.set_text(exctype, value, tb)
        response = dialog.run()
        dialog.destroy()
        if response == gtk.RESPONSE_NO:
            raise SystemExit(1)
    except Exception:
        traceback.print_exc()

def show_uri(uri):
    """Open `uri` in default application."""
    if sys.platform == "win32":
        if uri.startswith(("http://", "https://")):
            # gtk.show_uri (GTK+ 2.20) fails on Windows.
            # GError: No application is registered as handling this file
            return webbrowser.open(uri)
    return gtk.show_uri(None, uri, gtk.gdk.CURRENT_TIME)

def text_field_to_document(field):
    """Return :attr:`aeidon.documents` item corresponding to `field`."""
    if field == gaupol.fields.MAIN_TEXT:
        return aeidon.documents.MAIN
    if field == gaupol.fields.TRAN_TEXT:
        return aeidon.documents.TRAN
    raise ValueError("Invalid field: %s" % repr(field))
