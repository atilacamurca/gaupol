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

"""Text markup for the Advanced Sub Station Alpha format."""

import aeidon

__all__ = ("AdvSubStationAlpha",)


# pylint: disable=E1101,W0232

class AdvSubStationAlpha(aeidon.tags.SubStationAlpha):

    """Text markup for the Advanced Sub Station Alpha format.

    In addition to the markup in Sub Station Alpha, Advanced Sub Station Alpha
    contains a whole lof of markup tags of which the following are of interest
    to us. The further complicated color tags that define numbered (?) colors
    and alpha channels are ignored. The reset tag is allowed a style definiton,
    e.g. ``{\\rDefault}`` to revert to style "Default".

     * ``{\\bWEIGHT}...{\\b0}``
     * ``{\\u1}........{\\u0}``
     * ``........{\\r[STYLE]}``
    """

    _closing_pattern = r"\{\\([biu])0\}"
    _opening_pattern = r"\{\\(?![biu]0)(b|i|u|c|fn|fs).*?\}"
    _reset_pattern = r"\{\\r.*?\}"
    format = aeidon.formats.ASS

    def _main_decode(self, text):
        """Return `text` with decodable markup decoded."""
        text = self._decode_b(text, r"\{\\b[1-9]\d*\}(.*?)\{\\b[0\\]\}", 1)
        text = self._decode_u(text, r"\{\\u1\}(.*?)\{\\u[0\\]\}", 1)
        return aeidon.tags.SubStationAlpha._main_decode(self, text)

    def underline(self, text, bounds=None):
        """Return underlined `text`."""
        a, z = bounds or (0, len(text))
        return "".join((text[:a], "{\\u1}%s{\\u0}" % text[a:z], text[z:]))
