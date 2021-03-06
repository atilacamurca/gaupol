# Copyright (C) 2005-2009 Osmo Salomaa
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

"""Subtitle files of all formats."""

import aeidon

aeidon.util.install_module("files", lambda: None)

from .ssa        import SubStationAlpha
from .ass        import AdvSubStationAlpha
from .microdvd   import MicroDVD
from .mpl2       import MPL2
from .mpsub      import MPsub
from .subrip     import SubRip
from .subviewer2 import SubViewer2
from .tmplayer   import TMPlayer

__all__ = aeidon.util.get_all(dir(), r"^[A-Z]")


def add(cls):
    """Add a new :class:`aeidon.SubtitleFile` class."""
    globals()[cls.__name__] = cls
    globals()["__all__"] = tuple(set(__all__ + (cls.__name__,)))

def new(format, path, encoding, newline=None):
    """Return a new :class:`aeidon.SubtitleFile` instance given `format`."""
    for cls in map(eval, __all__):
        if cls.format == format:
            return cls(path, encoding, newline)
    raise ValueError("Format %s not found" % repr(format))
