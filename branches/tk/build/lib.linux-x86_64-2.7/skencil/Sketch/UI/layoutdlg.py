# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2000 by Bernhard Herzog
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

from Sketch import _, config
from Sketch.const import LAYOUT
from Sketch.Graphics.papersize import Papersize, PapersizesList
from Sketch.Graphics.pagelayout import PageLayout, Portrait, Landscape

from Tkinter import Frame, Label, StringVar, IntVar, DoubleVar
from Tkinter import RIGHT, BOTTOM, X, BOTH, LEFT, TOP, W, E, DISABLED, NORMAL
from tkext import UpdatedButton, MyEntry, MyOptionMenu, UpdatedRadiobutton

from lengthvar import LengthVar, create_unit_menu
from sketchdlg import SketchPanel


USER_SPECIFIC = '<User Specific>'

class LayoutPanel(SketchPanel):

    title = _("Layout")
    class_name = 'SKLayout'
    receivers = SketchPanel.receivers[:]

    def __init__(self, master, main_window, doc):
        SketchPanel.__init__(self, master, main_window, doc,
                             name = 'layoutdlg')

    def build_dlg(self):
        top = self.top

        format_frame = Frame(top)
        format_frame.pack(side = TOP, expand = 1, fill = X,
                          padx = 4, pady = 4)
        format_label = Label(format_frame, text = _("Paper format:"))
        format_label.pack(side = LEFT, expand = 1, fill = X)

        format_names = map(lambda t: t[0], PapersizesList)
        format_names.append(USER_SPECIFIC)
        self.var_format_name = StringVar(top)
        format_menu = MyOptionMenu(format_frame, format_names,
                                   variable = self.var_format_name,
                                   command = self.choose_format)
        format_menu.configure(width = max(map(len, format_names)))
        format_menu.pack(side = RIGHT, expand = 1, fill = X)

        orientation_frame = Frame(top)
        orientation_frame.pack(side = TOP, expand = 1, fill = X)
        self.var_orientation = IntVar(top)
        radio = UpdatedRadiobutton(orientation_frame, text = _("Portrait"),
                                   variable = self.var_orientation,
                                   value = Portrait,
                                   command = self.choose_orientation)
        radio.pack(side = LEFT, expand = 1, fill = X)
        radio = UpdatedRadiobutton(orientation_frame, text = _("Landscape"),
                                   variable = self.var_orientation,
                                   value = Landscape,
                                   command = self.choose_orientation)
        radio.pack(side = RIGHT, expand = 1, fill = X)

        size_frame = Frame(top)
        size_frame.pack(side = TOP, fill = X, expand = 1, padx = 4, pady = 4)
        var_width_number = DoubleVar(top)
        var_height_number = DoubleVar(top)
        var_width_unit = StringVar(top)
        var_height_unit = StringVar(top)
        unit = config.preferences.default_unit
        self.var_width = LengthVar(10, unit, var_width_number, var_width_unit)
        self.var_height = LengthVar(10, unit,var_height_number,var_height_unit)
        label = Label(size_frame, text = _("Page size:"))
        label.pack(side = TOP, anchor = W)
        label = Label(size_frame, text = _("Width"))
        label.pack(side = LEFT, anchor = E)
        self.widthentry = MyEntry(size_frame, textvariable = var_width_number,
                                  command = self.var_width.UpdateNumber,
                                  width = 6)
        self.widthentry.pack(side = LEFT, expand = 1, fill = X, anchor = E)
        label = Label(size_frame, text = _("Height"))
        label.pack(side = LEFT, anchor = E)
        self.heightentry = MyEntry(size_frame, textvariable =var_height_number,
                                   command = self.var_height.UpdateNumber,
                                   width = 6)
        self.heightentry.pack(side = LEFT, expand = 1, fill = X, anchor = E)

        def CallBoth(arg, x = self.var_width, y = self.var_height):
            x.UpdateUnit(arg)
            y.UpdateUnit(arg)

        optmenu = create_unit_menu(size_frame, CallBoth,
                                   variable = var_width_unit,
                                   indicatoron = 0, width = 3)
        optmenu.pack(side = LEFT, expand = 1, fill = X, anchor = W)



        button_frame = Frame(top)
        button_frame.pack(side = BOTTOM, fill = BOTH, expand = 1,
                          padx = 4, pady = 4)
        button = UpdatedButton(button_frame, text = _("Apply"),
                               command = self.apply_settings)
        button.pack(side = LEFT, expand = 1)
        button = UpdatedButton(button_frame, text = _("Close"),
                               command = self.close_dlg)
        button.pack(side = RIGHT, expand = 1)


    def init_from_doc(self):
        self.Update()

    def update_size_from_name(self, formatname):
        width, height = Papersize[formatname]
        if self.var_orientation.get() == Landscape:
            width, height = height, width
        self.update_size(width, height)

    def update_size(self, width, height):
        self.var_width.set(width)
        self.var_height.set(height)

    receivers.append((LAYOUT, 'Update'))
    def Update(self):
        layout = self.document.Layout()
        formatname = layout.FormatName()
        self.var_orientation.set(layout.Orientation())
        if formatname and formatname != USER_SPECIFIC:
            self.update_size_from_name(formatname)
        else:
            formatname = USER_SPECIFIC
            self.update_size(layout.Width(), layout.Height())
        self.var_format_name.set(formatname)
        self.set_entry_sensitivity()

    def set_entry_sensitivity(self):
        formatname = self.var_format_name.get()
        if formatname != USER_SPECIFIC:
            self.widthentry.config(state = DISABLED)
            self.heightentry.config(state = DISABLED)
        else:
            self.widthentry.config(state = NORMAL)
            self.heightentry.config(state = NORMAL)

    def choose_format(self, formatname):
        self.var_format_name.set(formatname)
        if formatname != USER_SPECIFIC:
            self.update_size_from_name(formatname)
        self.set_entry_sensitivity()

    def choose_orientation(self):
        name = self.var_format_name.get()
        if name != USER_SPECIFIC:
            self.update_size_from_name(name)

    def apply_settings(self):
        formatname = self.var_format_name.get()
        if formatname == USER_SPECIFIC:
            layout = PageLayout(width = self.var_width.get(),
                                height = self.var_height.get(),
                                orientation = self.var_orientation.get())
        else:
            layout = PageLayout(formatname,
                                orientation = self.var_orientation.get())
        self.document.SetLayout(layout)
