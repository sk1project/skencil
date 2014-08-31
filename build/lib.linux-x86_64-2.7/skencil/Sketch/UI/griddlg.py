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
#	Dialog for grid settings
#

from Tkinter import Frame, Label
from Tkinter import BOTTOM, BOTH, TOP, X, E

from Sketch.const import GRID
from Sketch import _

from sketchdlg import SketchPanel
from lengthvar import create_length_entry


class GridPanel(SketchPanel):

    title = _("Grid")
    receivers = SketchPanel.receivers[:]

    def __init__(self, master, canvas, doc):
        SketchPanel.__init__(self, master, canvas, doc)

    def build_dlg(self):
        top = self.top

        button_frame = self.create_std_buttons(top)
        button_frame.pack(side = BOTTOM, fill = BOTH, expand = 1)

        do_apply = self.do_apply

        frame = Frame(top)
        frame.pack(side = TOP, fill = X, expand = 1, ipady = 2)

        label = Label(frame, text = _("Origin:"), anchor = E)
        label.grid(row = 0, column = 0, sticky = 'E')
        f = Frame(frame)
        self.var_xorig = create_length_entry(top, f, do_apply)
        f.grid(row = 0, column = 1)
        label = Label(frame, text = ',', width = 1)
        label.grid(row = 0, column = 2)
        f = Frame(frame)
        self.var_yorig = create_length_entry(top, f, do_apply)
        f.grid(row = 0, column = 3)

        label = Label(frame, text = _("Widths:"), anchor = E)
        label.grid(row = 1, column = 0, sticky = 'E')
        f = Frame(frame)
        self.var_xwidth = create_length_entry(top, f, do_apply)
        f.grid(row = 1, column = 1)
        label = Label(frame, text = 'x', width = 1)
        label.grid(row = 1, column = 2)
        f = Frame(frame)
        self.var_ywidth = create_length_entry(top, f, do_apply)
        f.grid(row = 1, column = 3)

    def init_from_doc(self):
        xorig, yorig, xwidth, ywidth = self.document.Grid().Geometry()
        self.var_xorig.set(xorig)
        self.var_yorig.set(yorig)
        self.var_xwidth.set(xwidth)
        self.var_ywidth.set(ywidth)

    receivers.append((GRID, 'init_from_doc'))

    def do_apply(self, *rest):
        self.document.SetGridGeometry((self.var_xorig.get(),
                                       self.var_yorig.get(),
                                       self.var_xwidth.get(),
                                       self.var_ywidth.get()))


