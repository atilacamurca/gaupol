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


"""GTK user interface initialization."""

# pylint: disable-msg=W0612


import atexit
import os
import re
import sys


def _check_dependencies():
    """Check existance and versions of dependencies."""

    if sys.version_info[:3] < (2, 5, 0):
        print "Python 2.5 or greater is required to run Gaupol."
        raise SystemExit(1)

    try:
        import gtk
        if gtk.pygtk_version < (2, 10, 0):
            raise ImportError
    except ImportError:
        print "PyGTK 2.10.0 or greater is required to run Gaupol."
        raise SystemExit(1)

    try:
        import gtk.glade
    except ImportError:
        print "Glade support in PyGTK is required to run Gaupol."
        raise SystemExit(1)

    try:
        import enchant
    except ImportError:
        print "PyEnchant not found;"
        print "spell-checking not possible."

    try:
        import chardet
    except ImportError:
        print "Universal Encoding Detector not found;"
        print "character encoding auto-detection not possible."

def _list_encodings():
    """List all available character encodings."""

    import gaupol
    if gaupol.util.chardet_available():
        print "auto"
    for item in gaupol.encodings.get_valid_encodings():
        print item[0]

def _move_eggs():
    """Move eggs to sys.path so that they are importable."""

    try:
        import enchant
        return
    except Exception:
        pass
    try:
        import pkg_resources
        pkg_resources.require("pyenchant")
    except Exception:
        pass

def _parse_args(args):
    """Parse and return options and arguments."""

    import optparse
    from gaupol.i18n import _

    parser = optparse.OptionParser(
        formatter=optparse.IndentedHelpFormatter(2, 42),
        usage=_("gaupol [OPTION...] [FILE...] [+NUM]"),)

    parser.add_option(
        "-c", "--config-file",
        action="store",
        type="string",
        metavar=_("FILE"),
        dest="config_file",
        default=None,
        help=_("set the configuration file used"),)

    parser.add_option(
        "-d", "--debug",
        action="store_true",
        dest="debug",
        default=False,
        help=_("enable additional run-time checks"),)

    parser.add_option(
        "-e", "--encoding",
        action="store",
        type="string",
        metavar=_("ENCODING"),
        dest="encoding",
        default=None,
        help=_("set the encoding used to open files"),)

    parser.add_option(
        "--list-encodings",
        action="store_true",
        dest="list_encodings",
        default=False,
        help=_("list all available character encodings"),)

    parser.add_option(
        "-t", "--translation-file",
        action="store",
        type="string",
        metavar=_("FILE"),
        dest="translation_file",
        default=None,
        help=_("open translation file"),)

    parser.add_option(
        "--version",
        action="store_true",
        dest="version",
        default=False,
        help=_("show version number and exit"),)

    parser.add_option(
        "-v", "--video-file",
        action="store",
        type="string",
        metavar=_("FILE"),
        dest="video_file",
        default=None,
        help=_("select video file"),)

    return parser.parse_args(args)

def _prepare_config_file(path):
    """Set the configuration file to use."""

    import gaupol.gtk
    if path is None:
        path = os.path.join(gaupol.PROFILE_DIR, "gaupol.gtk.conf")
    gaupol.gtk.conf.config_file = os.path.abspath(path)
    gaupol.gtk.conf.read()
    atexit.register(gaupol.gtk.conf.write)

def _prepare_debug(debug):
    """Enable or disable debugging checks."""

    import gaupol
    gaupol.check_contracts = debug

def _prepare_ui():
    """Prepare user interface stuff."""

    import gaupol
    import gobject
    import gtk.glade
    from gaupol.gtk.dialogs import debug
    gtk.glade.bindtextdomain("gaupol", gaupol.LOCALE_DIR)
    gtk.glade.textdomain("gaupol")
    gobject.threads_init()
    rc_file = os.path.join(gaupol.DATA_DIR, "gtkrc")
    gtk.rc_add_default_file(rc_file)
    sys.excepthook = debug.show

def _show_version():
    """Show the version number."""

    import gaupol
    print "gaupol %s" % gaupol.__version__

def _start(opts, args):
    """Start application and open files given as arguments."""

    # FIX:
    import gaupol.gtk
    application = gaupol.gtk.Application()
    jump_row = None
    re_jump = re.compile(r"\+\d*")
    for arg in (x for x in args if re_jump.match(x) is not None):
        jump_row = (max(0, int(arg[1:]) - 1) if arg[1:] else -1)
        args.remove(arg)
    paths = [os.path.abspath(x) for x in args]
    #application.open_main_files(paths, opts.encoding)
    page = application.get_current_page()
    if (page is not None) and opts.translation_file:
        path = os.path.abspath(opts.translation_file)
        application.open_translation_file(path, opts.encoding)
    if (page is not None) and opts.video_file:
        path = os.path.abspath(opts.video_file)
        page.project.video_path = path
    if (page is not None) and (jump_row is not None):
        page.view.set_focus(jump_row)
    import gtk
    gtk.main()

def main(args):
    """Parse arguments and start application."""

    _move_eggs()
    _check_dependencies()
    opts, args = _parse_args(args)
    if opts.list_encodings:
        return _list_encodings()
    if opts.version:
        return _show_version()
    _prepare_debug(opts.debug)
    _prepare_config_file(opts.config_file)
    _prepare_ui()
    _start(opts, args)
