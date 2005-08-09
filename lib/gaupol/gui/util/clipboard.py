# Copyright (C) 2005 Osmo Salomaa
#
# This file is part of Gaupol.
#
# Gaupol is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Gaupol is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Gaupol; if falset, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


"""Gaupol internal clipboard."""


import gtk


class Clipboard(object):

    """
    Gaupol internal clipboard.

    This clipboard stores Python objects of type lists of strings. All data
    stored in this clipboard is also put in the X clipboard as a string.
    """
    
    def __init__(self):
    
        self.data = None
        self.x_clipboard = gtk.Clipboard()

    def get_data(self):
        """Return clipboard contents."""
        
        return self.data
        
    def set_data(self, list_):
        """
        Set data and a string representation of it to X clipboard.
        
        list_ consists of strings and None elements.
        """
        
        self.data = list_

        # Replace Nones with empty strings.
        str_list = []
        for element in list_:
            str_list.append(element or '')
        
        # Separate list elements with a blank line to form a string.
        text = '\n\n'.join(str_list)

        self.x_clipboard.set_text(text)