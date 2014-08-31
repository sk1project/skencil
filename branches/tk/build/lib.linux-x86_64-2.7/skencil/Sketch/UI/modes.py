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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307	USA

#
#	Classes:
#
#	WidgetWithModes
#
#		A mix-in class for widgets with several input modes.
#		Modes may be temporary or permanent.
#
#		Temporary modes are usually only active until the user
#		has pressed and released a mouse button. The zoom
#		command in the SketchCanvas class is implemented as a
#		temporary mode for example. When a temporary mode is
#		deactivated (probably because the user released the
#		mouse button or pressed ESC) the mode that was active
#		before is activated again.
#
#		The permanent modes are called `major modes' here and
#		require an explicit command from the user to switch to
#		another major mode. Examples are the selection mode and
#		the edit mode the SketchCanvas.
#
#		Temporary mode can even be nested: A user might select
#		the `Update From...' button in the FillStyle dialog
#		which activates the pick_object mode in the canvas
#		widget. While this mode is active, indicated by a
#		different cursor shape, she might also select the zoom
#		button in the tool bar to make the area where the object
#		she wants to pick is a little larger. When the zoom
#		command is complete the pick_object mode is
#		automatically activated again and the user can click on
#		the object whose fill style should be copied into the
#		fill style dialog.
#
#
#	Mode
#	MajorMode(Mode)
#	TemporaryMode(Mode)
#
#		These represent the modes of the widget. Each instance
#		basically provides callable objects (methods usually)
#		that are invoked when certain events occur.
#
#


def noop(*args, **kwargs):
    pass

class Mode:

    isMajorMode = 0
    isTemporaryMode = 0

    def __init__(self, enter, button_down, mouse_move, button_up,
                 exit = noop, cancel = noop,	 **rest):
        self.enter = enter
        self.button_down = button_down
        self.mouse_move = mouse_move
        self.button_up = button_up
        self.exit = exit
        self.cancel = cancel
        for key, value in rest.items():
            setattr(self, key, value)


class MajorMode(Mode):

    isMajorMode = 1



class TemporaryMode(Mode):

    isTemporaryMode = 1


class SketchModeError(Exception):
    pass

class WidgetWithModes:

    def __init__(self):
        self.mode_stack = ()
        self.mode = MajorMode(noop, noop, noop, noop, noop)

    def push_mode(self, mode):
        self.mode_stack = (self.mode, self.mode_stack)
        self.mode = mode

    def pop_mode(self):
        try:
            self.mode, self.mode_stack = self.mode_stack
        except ValueError:
            raise SketchModeError('mode stack empty')

    def exit_temporary_mode(self, cancel = 0):
        if self.mode.isTemporaryMode:
            if cancel:
                self.mode.cancel()
            self.pop_mode()

    def cancel_temporary_mode(self):
        self.exit_temporary_mode(1)

    def enter_mode(self, mode, *args):
        if mode.isMajorMode:
            # cancel all currently active temporary modes
            while self.mode.isTemporaryMode:
                self.cancel_temporary_mode()
            if not self.mode.isMajorMode or self.mode_stack != ():
                raise SketchModeError('mode stack corrupted')

            self.mode.exit()
            self.mode = mode
            apply(self.mode.enter, args)

        else:
            self.push_mode(mode)
            apply(self.mode.enter, args)

