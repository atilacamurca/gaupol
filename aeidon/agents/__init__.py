# Copyright (C) 2006-2007,2009 Osmo Salomaa
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

"""Data editing extension delegates of :class:`aeidon.Project`."""

from .clipboard import ClipboardAgent
from .edit      import EditAgent
from .format    import FormatAgent
from .open      import OpenAgent
from .position  import PositionAgent
from .preview   import PreviewAgent
from .register  import RegisterAgent
from .save      import SaveAgent
from .search    import SearchAgent
from .set       import SetAgent
from .text      import TextAgent
from .util      import UtilityAgent

__all__ = tuple(filter(lambda x: x.endswith("Agent"), dir()))
