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


import sketchdlg
from Tkinter import Frame
from Tkinter import BOTTOM, X, BOTH, TOP, CENTER
from tkext import UpdatedButton, CommandButton

from Sketch import _

from sketchdlg import CommandPanel


class CurvePanel(CommandPanel):

    title = _("Curve")

    def __init__(self, master, main_window, doc):
        CommandPanel.__init__(self, master, main_window, doc,
                              name = 'curvedlg')

    def build_dlg(self):
        names = (('ContAngle', 'CloseNodes', 'OpenNodes'),
                 ('ContSmooth', 'InsertNodes', 'DeleteNodes'),
                 ('ContSymmetrical', 'SegmentsToLines', 'SegmentsToCurve'))

        top = self.top
        frame = Frame(top)
        frame.pack(side = TOP, expand = 1, fill = BOTH)

        # XXX This dialog should have its own ObjectCommand objects
        cmds = self.main_window.canvas.commands.PolyBezierEditor
        for i in range(len(names)):
            for j in range(len(names[i])):
                button = CommandButton(frame, getattr(cmds, names[i][j]),
                                       highlightthickness = 0)
                button.grid(column = j, row = i)

        frame = Frame(top)
        frame.pack(side = BOTTOM, expand = 0, fill = X)

        button = UpdatedButton(frame, text = _("Close"),
                               command = self.close_dlg)
        button.pack(anchor = CENTER)


