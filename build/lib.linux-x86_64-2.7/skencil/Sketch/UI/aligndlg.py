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
#	Dialog for aligning objects
#

from Tkinter import Frame, Radiobutton, IntVar, StringVar
from Tkinter import BOTH, LEFT, TOP, X, Y

from Sketch.const import SELECTION
from Sketch import _
from tkext import UpdatedButton, UpdatedCheckbutton, UpdatedRadiobutton
from sketchdlg import CommandPanel
import skpixmaps
pixmaps = skpixmaps.PixmapTk

def make_button(*args, **kw):
    bitmap = kw.get('bitmap')
    if bitmap is not None:
        bitmap = pixmaps.load_image(bitmap)
        if type(bitmap) == type(""):
            kw['bitmap'] = bitmap
        else:
            del kw['bitmap']
            kw['image'] = bitmap
    return apply(Radiobutton, args, kw)

class AlignPanel(CommandPanel):

    title = _("Align")

    def __init__(self, master, canvas, doc):
        CommandPanel.__init__(self, master, canvas, doc)

    def build_dlg(self):
        top = self.top

        framey = Frame(top)
        framey.pack(side = LEFT, expand = 1, fill = Y, padx = 2, pady = 2)
        framex = Frame(top)
        framex.pack(side = TOP, expand = 1, fill = X, padx = 2, pady = 2,
                    anchor = 'n')

        x_pixmaps = [pixmaps.AlignLeft, pixmaps.AlignCenterX,
                     pixmaps.AlignRight]
        y_pixmaps = [pixmaps.AlignTop, pixmaps.AlignCenterY,
                     pixmaps.AlignBottom]
        self.var_x = IntVar(top)
        self.var_x.set(0)
        self.value_x = 0
        self.var_y = IntVar(top)
        self.var_y.set(0)
        self.value_y = 0

        for i in range(1, 4):
            button = make_button(framex, bitmap = x_pixmaps[i - 1],
                                 value = i, variable = self.var_x,
                                 command = self.set_x)
            button.pack(side = LEFT, padx = 1, pady = 1,
                        ipadx = 1, ipady = 1)
            button = make_button(framey, bitmap = y_pixmaps[i - 1],
                                 value = i, variable = self.var_y,
                                 command = self.set_y)
            button.pack(side = TOP, padx = 1, pady = 1,
                        ipadx = 1, ipady = 1)

        button_frame = Frame(top)
        button_frame.pack(expand = 1, fill = BOTH)
        button_frame.rowconfigure(3, minsize = 5)

        apply_button = UpdatedButton(button_frame, text = _("Apply"),
                                     command = self.apply,
                                     sensitivecb = self.can_apply)
        apply_button.grid(row = 4, column = 0, #columnspan= 2,
                          sticky = 'ew')
        self.Subscribe(SELECTION, apply_button.Update)

        #button = UpdatedButton(button_frame, text = _("Reset"),
        #		       command = self.reset)
        #button.grid(column = 0, row = 4, sticky = 'ew')

        button = UpdatedButton(button_frame, text = _("Close"),
                               command = self.close_dlg)
        button.grid(column = 1, row = 4, sticky = 'ew')

        self.var_reference = StringVar(top)
        self.var_reference.set('selection')
        radio = UpdatedRadiobutton(button_frame, value = 'selection',
                                   text = _("Relative To Selection"),
                                   variable = self.var_reference,
                                   command = apply_button.Update)
        radio.grid(row = 0, column = 0, columnspan = 2, sticky = 'ew')
        radio = UpdatedRadiobutton(button_frame, value = 'lowermost',
                                   text = _("Relative To Lowermost"),
                                   variable = self.var_reference,
                                   command = apply_button.Update)
        radio.grid(row = 1, column = 0, columnspan = 2, sticky = 'ew')
        radio = UpdatedRadiobutton(button_frame, value = 'page',
                                   text = _("Relative To Page"),
                                   variable = self.var_reference,
                                   command = apply_button.Update)
        radio.grid(row = 2, column = 0, columnspan = 2, sticky = 'ew')


    def init_from_doc(self):
        self.issue(SELECTION)

    def set_x(self):
        value = self.var_x.get()
        if value == self.value_x:
            self.var_x.set(0)
            self.value_x = 0
        else:
            self.value_x = value

    def set_y(self):
        value = self.var_y.get()
        if value == self.value_y:
            self.var_y.set(0)
            self.value_y = 0
        else:
            self.value_y = value

    def apply(self):
        x = self.var_x.get()
        y = self.var_y.get()
        reference = self.var_reference.get()
        self.document.AlignSelection(x, y, reference = reference)

    def reset(self):
        self.var_x.set(0)
        self.var_y.set(0)

    def can_apply(self):
        if self.document.CountSelected() > 1:
            return 1
        reference = self.var_reference.get()
        return reference == 'page' and self.doc_has_selection()

