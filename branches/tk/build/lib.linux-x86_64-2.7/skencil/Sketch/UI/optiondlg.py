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


#
#	A dialog to change some values in config.py
#

from Sketch.config import preferences
from Sketch import _, config

from Tkinter import Toplevel, Frame, Label, Entry, IntVar, DoubleVar, StringVar
from Tkinter import GROOVE, TOP, BOTTOM, LEFT, RIGHT, E, W, X, BOTH, \
     NORMAL, DISABLED
from tkext import UpdatedButton, MyEntry, UpdatedCheckbutton
from lengthvar import LengthVar, create_unit_menu


class OptionDialog:

    def __init__(self, master, main_window):
        self.master = master
        self.main_window = main_window

        top = Toplevel(master)
        top.title(_("Global Options"))
        top.transient(master)
        top.protocol('WM_DELETE_WINDOW', self.close_dlg)

        top.geometry('%+d%+d' % (master.winfo_rootx() + 100,
                                 master.winfo_rooty() + 100))

        self.top = top
        self.build_dlg()

    def make_frame(self):
        frame = Frame(self.top, relief = GROOVE, bd = 2)
        frame.pack(side = TOP, expand = 1, fill = X, padx = 4, pady = 4)
        return frame

    def build_dlg(self):
        top = self.top

        #
        #	Undo
        #

        undo_frame = self.make_frame()
        label = Label(undo_frame, text = _("# Undo Levels:"), anchor = E)
        label.pack(side = LEFT, expand = 1, fill = X)

        self.var_undo = IntVar(top)
        self.undo_entry = Entry(undo_frame, textvariable = self.var_undo,
                                width = 4)
        self.undo_entry.pack(side = LEFT)
        self.var_unlimited = IntVar(top)
        check = UpdatedCheckbutton(undo_frame,
                                   text = _("unlimited"),
                                   variable = self.var_unlimited,
                                   command = self.unlimited_undo)
        check.pack(side = RIGHT, expand = 1, anchor = W)
        limit = preferences.undo_limit
        if limit == None:
            self.var_undo.set(10)
            self.var_unlimited.set(1)
        else:
            if limit < 0:
                limit = 0
            self.var_undo.set(limit)
            self.var_unlimited.set(0)


        #
        #	Duplication
        #

        off_frame = self.make_frame()
        var_off_x_number = DoubleVar(top)
        var_off_y_number = DoubleVar(top)
        var_off_x_unit = StringVar(top)
        var_off_y_unit = StringVar(top)
        x, y = preferences.duplicate_offset
        unit = config.preferences.default_unit
        self.var_off_x = LengthVar(x, unit, var_off_x_number, var_off_x_unit)
        self.var_off_y = LengthVar(y, unit, var_off_y_number, var_off_y_unit)
        label = Label(off_frame, text = _("Duplication Offset"))
        label.pack(side = TOP, anchor = W)
        label = Label(off_frame, text = _("Hor."))
        label.pack(side = LEFT, expand = 1, anchor = E)
        entry = MyEntry(off_frame, textvariable = var_off_x_number,
                        width = 6, command = self.var_off_x.UpdateNumber)
        entry.pack(side = LEFT, fill = X, anchor = E)
        label = Label(off_frame, text = _("Vert."))
        label.pack(side = LEFT, anchor = E)
        entry = MyEntry(off_frame, textvariable = var_off_y_number,
                        width = 6, command = self.var_off_y.UpdateNumber)
        entry.pack(side = LEFT, fill = X, anchor = E)

        def CallBoth(arg, x = self.var_off_x, y = self.var_off_y):
            x.UpdateUnit(arg)
            y.UpdateUnit(arg)

        optmenu = create_unit_menu(off_frame, CallBoth,
                                   variable = var_off_x_unit,
                                   indicatoron = 0, width = 3)
        optmenu.pack(side = LEFT, expand = 1, anchor = W)

        #
        #       Default Unit
        #

        self.default_unit = config.preferences.default_unit
        frame = self.make_frame()
        label = Label(frame, text = _("Default Unit"))
        label.pack(side = LEFT, expand = 1)
        menu = create_unit_menu(frame, self.set_unit, indicatoron = 0,
                                width = 3, text = self.default_unit)
        menu.pack(side = RIGHT, expand = 1)


        #
        #	Gradient Patterns
        #

        #self.var_steps = IntVar(top)
        #self.var_steps.set(preferences.gradient_steps)
        #frame = self.make_frame()
        #label = Label(frame, text = 'Gradient Steps')


        #
        #	Standard Buttons (OK, Cancel)
        #

        but_frame = Frame(top)
        but_frame.pack(side = BOTTOM, fill = BOTH, expand = 1,
                       padx = 4, pady = 4)
        button = UpdatedButton(but_frame, text = _("OK"), command = self.ok)
        button.pack(side = LEFT, expand = 1)
        button = UpdatedButton(but_frame, text = _("Cancel"),
                               command = self.close_dlg)
        button.pack(side = RIGHT, expand = 1)


    def unlimited_undo(self):
        unlimited = self.var_unlimited.get()
        if unlimited:
            self.undo_entry['state'] = DISABLED
        else:
            self.undo_entry['state'] = NORMAL

    def set_unit(self, unit):
        self.default_unit = unit

    def ok(self):
        # undo
        unlimited = self.var_unlimited.get()
        if unlimited:
            preferences.undo_limit = None
        else:
            preferences.undo_limit = self.var_undo.get()

        # offset
        x = self.var_off_x.get()
        y = self.var_off_y.get()
        preferences.duplicate_offset = (x, y)

        # default unit
        preferences.default_unit = self.default_unit

        #
        self.close_dlg()

    def close_dlg(self):
        self.main_window = None
        self.top.destroy()

    def deiconify_and_raise(self):
        self.top.deiconify()
        self.top.tkraise()
