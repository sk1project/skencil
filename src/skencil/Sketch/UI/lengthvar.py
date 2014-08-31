# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999 by Bernhard Herzog
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


# A (Tkinter-) variable holding a length, i. e. a number and a unit.
# This is implemented with two Tkinter variable, a DoubleVar and a
# StringVar. The DoubleVar can be used for a Tk Entry widget and the
# StringVar, describing the unit, can be used for an OptionMenu.
# Internally the length is always represented as a length in PSpoint
# units (1/72 inch).
#
# XXX: This needs a cleaner reimplementation

from types import TupleType

from Sketch import config
from Sketch.Lib.units import unit_dict, unit_names

from Tkinter import TclError, StringVar, DoubleVar
from Tkinter import LEFT, RIGHT, X, Y, E, W
from tkext import MyEntry, MyOptionMenu
from miniscroll import MiniScroller


class LengthVar:

    def __init__(self, length, unit, number_var = None, unit_var = None,
                 command = None, args = (),
                 precision = 2):
        self.length = length
        self.number_var = number_var
        self.unit = unit
        self.precision = 2
        self.unit_var = unit_var
        self.callback = command
        if type(args) != TupleType:
            args = (args,)
        self.args = args
        self.set_vars()

    def __del__(self):
        pass

    def set_vars(self):
        number = self.length / unit_dict[self.unit]
        if self.number_var:
            self.number_var.set(round(number, self.precision))
        if self.unit_var:
            self.unit_var.set(self.unit)

    def get(self):
        try:
            number = self.number_var.get()
            self.length = number * unit_dict[self.unit]
        except TclError:
            pass
        return self.length

    def set(self, length):
        self.length = length
        self.set_vars()

    def UpdateUnit(self, unit = None):
        if unit is None:
            self.unit = self.unit_var.get()
        else:
            self.unit = unit
        self.set_vars()

    def UpdateNumber(self, number = None):
        try:
            number = self.number_var.get()
        except TclError:
            pass
        self.length = number * unit_dict[self.unit]
        self.set_vars()
        self.call_callback()

    def Factor(self):
        return unit_dict[self.unit]

    def UnitName(self):
        return self.unit

    def call_callback(self):
        if self.callback:
            apply(self.callback, (self.length,) + self.args)




def create_unit_menu(master, command, variable = None,
                     **options):
    optmenu = MyOptionMenu(master, unit_names, command = command,
                           variable = variable)
    optmenu.configure(options)
    return optmenu

def create_length_widgets(top, master, command):
    var_number = DoubleVar(top)
    var_unit = StringVar(top)
    var_length = LengthVar(1.0, config.preferences.default_unit, var_number,
                           var_unit, command = command)
    entry = MyEntry(master, textvariable = var_number, justify = RIGHT,
                    width = 6, command = var_length.UpdateNumber)
    scroll = MiniScroller(master, variable = var_number, min = 0, max = None,
                          step = 1)
    optmenu = create_unit_menu(master, var_length.UpdateUnit,
                               variable = var_unit, indicatoron = 0, width = 3)
    return var_length, entry, scroll, optmenu



def create_length_entry(top, master, command, scroll_pad = 2):
    var, entry, scroll, optmenu = create_length_widgets(top, master, command)
    entry.pack(side = LEFT, expand = 1, fill = X, anchor = E)
    scroll.pack(side = LEFT, fill = Y, pady = scroll_pad)
    optmenu.pack(side = LEFT, expand = 1, fill = X, anchor = W)
    return var
