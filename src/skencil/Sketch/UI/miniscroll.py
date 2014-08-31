# Sketch - A Python-based interactive drawing program
# Copyright (C) 1998 by Bernhard Herzog
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

from types import TupleType

import pax

from Tkinter import IntVar, X, Y, LEFT, RIGHT, E
from tkext import PyWidget, MyEntry

from Sketch.const import COMMAND
from Sketch import Publisher, const

cursors = (const.CurUp, const.CurUpDown, const.CurDown)

class MiniScroller(PyWidget, Publisher):

    def __init__(self, master=None, min = None, max = None, step = 1,
                 variable = None, command = None, args = (), **kw):
        if not kw.has_key('width'):
            kw['width'] = 8
        apply(PyWidget.__init__, (self, master), kw)
        self.SetRange(min, max, step)
        self.variable = variable
        self.state = 0		# 1: up; 2: drag; 3: down
        self.rect_y = 0
        self.start = 0
        self.start_number = min
        if command:
            self.set_command(command, args)
        self.bind('<Motion>', self.MotionEvent)
        self.bind('<ButtonPress-1>', self.ButtonPressEvent)
        self.bind('<ButtonRelease-1>', self.ButtonReleaseEvent)

    def ResizedMethod(self, width, height):
        button_height = 4
        rect_y = (height - button_height) / 2
        self.top_poly = [(-1, rect_y), (width / 2, -1), (width, rect_y)]
        y = button_height + rect_y
        self.bot_poly = [(-1, y), (width, y), (width / 2, height)]
        self.rect_y = rect_y

    def SetRange(self, min, max, step = 1):
        self.min = min
        self.max = max
        self.step = step

    def set_command(self, command, args):
        if type(args) != TupleType:
            args = (args,)
        apply(self.Subscribe, (COMMAND, command,) + args)

    def invoke(self):
        self.issue(COMMAND)

    def RedrawMethod(self, region):
        button_height = 4
        win = self.tkwin
        width = win.width
        border = self.tkborder

        border.Draw3DRectangle(win, 0, self.rect_y, width, button_height, 2,
                               pax.TK_RELIEF_RAISED)
        border.Draw3DPolygon(win, self.top_poly, -2, pax.TK_RELIEF_SUNKEN)
        border.Draw3DPolygon(win, self.bot_poly, -2, pax.TK_RELIEF_SUNKEN)

    def y_to_state(self, y):
        if y < self.rect_y:
            return 1
        elif y < self.rect_y + 4:
            return 2
        else:
            return 3

    def set_variable(self, y):
        if self.variable:
            number = self.start_number + self.step * (self.start - y)
            if self.min is not None and number < self.min:
                number = self.min
            if self.max is not None and number > self.max:
                number = self.max
            self.variable.set(number)

    def MotionEvent(self, event):
        if self.state == 0:
            self['cursor'] = cursors[self.y_to_state(event.y) - 1]
        elif self.state == 2:
            self.set_variable(event.y)

    def ButtonPressEvent(self, event):
        self.state = self.y_to_state(event.y)
        self.start = event.y
        if self.variable:
            self.start_number = self.variable.get()

    def ButtonReleaseEvent(self, event):
        state = self.state
        if state == 1:
            self.set_variable(self.start - 1)
        elif state == 2:
            self.set_variable(event.y)
        elif state == 3:
            self.set_variable(self.start + 1)
        if state != 0:
            self.invoke()
        self.state = 0



def create_mini_entry(top, master, command, vartype = IntVar,
                      min = 0, max = None, step = 1, scroll_pad = 2):
    var_number = vartype(top)
    entry = MyEntry(master, textvariable = var_number, justify = RIGHT,
                    width = 6, command = command)
    entry.pack(side = LEFT, expand = 1, fill = X, anchor = E)
    scroll = MiniScroller(master, variable = var_number, min = min, max = max,
                          step = step)
    scroll.pack(side = LEFT, fill = Y, pady = scroll_pad)
    scroll.Subscribe(COMMAND, command)
    return var_number
