# Copyright (C) 2007 Osmo Salomaa
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


"""UI manager actions."""


import gaupol.gtk


def _get_actions():
    """Get all Action classes."""

    actions = []
    for module in _get_modules():
        names = set(x for x in dir(module) if x.endswith("Action"))
        names -= set(("Action", "ToggleAction", "RadioAction"))
        for value in (getattr(module, x) for x in names):
            globals()[value.__name__] = value
            actions.append(value.__name__)
    return gaupol.gtk.util.get_sorted_unique(actions)

def _get_modules():
    """Get all modules that define Actions."""

    from . import edit
    from . import file
    from . import format
    from . import help
    from . import position
    from . import search
    from . import spellcheck
    from . import view
    return locals().values()

__all__ = _get_actions()
