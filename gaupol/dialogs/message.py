# Copyright (C) 2005-2007,2010 Osmo Salomaa
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

"""Message dialog classes."""

import gtk

__all__ = ("ErrorDialog", "InfoDialog", "QuestionDialog", "WarningDialog")


class ErrorDialog(gtk.MessageDialog):

    """Base class for error dialogs."""

    def __init__(self, parent, title, message=None):
        """Initialize an :class:`ErrorDialog` object."""
        gtk.MessageDialog.__init__(self,
                                   parent=parent,
                                   flags=(gtk.DIALOG_MODAL |
                                          gtk.DIALOG_DESTROY_WITH_PARENT),

                                   type=gtk.MESSAGE_ERROR,
                                   buttons=gtk.BUTTONS_NONE,
                                   message_format=title)

        if message is not None:
            self.format_secondary_text(message)


class InfoDialog(gtk.MessageDialog):

    """Base class for info dialogs."""

    def __init__(self, parent, title, message=None):
        """Initialize an :class:`InfoDialog` object."""
        gtk.MessageDialog.__init__(self,
                                   parent=parent,
                                   flags=(gtk.DIALOG_MODAL |
                                          gtk.DIALOG_DESTROY_WITH_PARENT),


                                   type=gtk.MESSAGE_INFO,
                                   buttons=gtk.BUTTONS_NONE,
                                   message_format=title)

        if message is not None:
            self.format_secondary_text(message)


class QuestionDialog(gtk.MessageDialog):

    """Base class for question dialogs."""

    def __init__(self, parent, title, message=None):
        """Initialize a :class:`QuestionDialog` object."""
        gtk.MessageDialog.__init__(self,
                                   parent=parent,
                                   flags=(gtk.DIALOG_MODAL |
                                          gtk.DIALOG_DESTROY_WITH_PARENT),

                                   type=gtk.MESSAGE_QUESTION,
                                   buttons=gtk.BUTTONS_NONE,
                                   message_format=title)

        if message is not None:
            self.format_secondary_text(message)


class WarningDialog(gtk.MessageDialog):

    """Base class for warning dialogs."""

    def __init__(self, parent, title, message=None):
        """Initialize a :class:`WarningDialog` object."""
        gtk.MessageDialog.__init__(self,
                                   parent=parent,
                                   flags=(gtk.DIALOG_MODAL |
                                          gtk.DIALOG_DESTROY_WITH_PARENT),

                                   type=gtk.MESSAGE_WARNING,
                                   buttons=gtk.BUTTONS_NONE,
                                   message_format=title)

        if message is not None:
            self.format_secondary_text(message)
