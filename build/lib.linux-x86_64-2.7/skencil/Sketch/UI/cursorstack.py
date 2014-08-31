# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998 by Bernhard Herzog
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#
# Class CursorStack
#
# A mix-in class for widgets.
#
# When switching to a temporary mode like the zoom mode in SketchCanvas,
# it is a good idea to change the mouse pointer into, for instance, a
# magnifying glass, while the temporary mode is active. When the mode
# becomes inactive, i.e. when the previous mode is restored, the
# appropriate pointer has to be shown again.
#
# CursorStack provides methods for dealing with these things.
#

class CursorStack:

    def __init__(self, shape = None, function = None):
        self.cursor_stack = None
        self.cursor_function = self.set_handle_cursor
        self.cursor_shape = shape
        self.last_cursor = function

    def push_static_cursor(self, cursor):
        self.push_cursor_state()
        self.set_static_cursor(cursor)

    def set_static_cursor(self, cursor):
        self.cursor_function = None
        self.cursor_shape = cursor
        self.set_window_cursor(cursor)

    def push_active_cursor(self, function, standard_shape):
        self.push_cursor_state()
        self.set_active_cursor(function, standard_shape)

    def set_active_cursor(self, function, standard_shape):
        self.cursor_function = function
        self.cursor_shape = standard_shape
        if self.winfo_ismapped():
            x, y = self.tkwin.QueryPointer()[4:6]
            self.cursor_function(x, y)

    def push_cursor_state(self):
        self.cursor_stack = (self.cursor_shape, self.cursor_function,
                             self.cursor_stack)

    def pop_cursor_state(self):
        self.cursor_shape, self.cursor_function, self.cursor_stack \
            = self.cursor_stack
        if self.cursor_function:
            x, y = self.tkwin.QueryPointer()[4:6]
            self.cursor_function(x, y)
        else:
            self.set_window_cursor(self.cursor_shape)

    def set_window_cursor(self, cursor):
        if cursor != self.last_cursor:
            self['cursor'] = self.last_cursor = cursor
