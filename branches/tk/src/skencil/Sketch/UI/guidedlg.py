# Sketch - A Python-based interactive drawing program
# Copyright (C) 1998, 1999 by Bernhard Herzog
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
#	Edit the guide lines
#

from string import atoi

from Tkinter import Frame, Label, DoubleVar, StringVar, Scrollbar
from Tkinter import BOTTOM, BOTH, LEFT, RIGHT, TOP, X, Y, E, W

from Sketch.const import GUIDE_LINES, SELECTION
from Sketch import _, Point, config

from tkext import UpdatedButton, MyEntry, UpdatedListbox
from miniscroll import MiniScroller

from sketchdlg import SketchPanel
from lengthvar import LengthVar, create_unit_menu


class GuidePanel(SketchPanel):

    title = _("Guide Lines")
    receivers = SketchPanel.receivers[:]

    def __init__(self, master, canvas, doc):
        SketchPanel.__init__(self, master, canvas, doc, name = 'guidedlg')

    def build_dlg(self):
        top = self.top

        var_number = DoubleVar(top)
        var_unit = StringVar(top)
        self.var_pos = LengthVar(1.0, config.preferences.default_unit,
                                 var_number, var_unit, command = self.set_pos)
        pos_frame = Frame(top)
        pos_frame.pack(side = TOP, fill = X, expand = 0)
        self.var_label = StringVar(top)
        self.var_label.set('X:')
        label = Label(pos_frame, textvariable = self.var_label)
        label.pack(side = LEFT, expand = 1, anchor = E)
        entry = MyEntry(pos_frame, textvariable = var_number,
                        justify = RIGHT, width = 4,
                        command = self.var_pos.UpdateNumber)
        entry.pack(side = LEFT, expand = 1, fill = X, anchor = E)
        scroll = MiniScroller(pos_frame, variable = var_number,
                              min = 0, max = None, step = 1)
        scroll.pack(side = LEFT, fill = Y)
        optmenu = create_unit_menu(pos_frame, self.set_unit,
                                   variable = var_unit,
                                   indicatoron = 0, width = 3)
        optmenu.pack(side = LEFT, expand = 1, fill = X, anchor = W)

        list_frame = Frame(top)
        list_frame.pack(side = TOP, expand = 1, fill = BOTH)

        sb_vert = Scrollbar(list_frame, takefocus = 0)
        sb_vert.pack(side = RIGHT, fill = Y)
        guides = UpdatedListbox(list_frame, name = 'list')
        guides.pack(expand = 1, fill = BOTH)
        guides.Subscribe(SELECTION, self.select_guide)
        sb_vert['command'] = (guides, 'yview')
        guides['yscrollcommand'] = (sb_vert, 'set')
        self.guides = guides
        self.selected = None

        frame = Frame(top)
        frame.pack(side = BOTTOM, fill = X)
        button = UpdatedButton(frame, text = _("Add H"),
                               command = self.add_guide, args = 1)
        button.pack(side = LEFT)
        button = UpdatedButton(frame, text = _("Add V"),
                               command = self.add_guide, args = 0)
        button.pack(side = LEFT)
        button = UpdatedButton(frame, text = _("Delete"),
                               command = self.del_guide)
        button.pack(side = LEFT)
        button = UpdatedButton(frame, text = _("Close"),
                               command = self.close_dlg)
        button.pack(side = RIGHT)

    def set_unit(self, *rest):
        apply(self.var_pos.UpdateUnit, rest)
        self.update_list()

    receivers.append((GUIDE_LINES, 'init_from_doc'))
    def init_from_doc(self, *rest):
        self.guide_lines = self.document.GuideLines()
        self.guide_lines.reverse()
        self.update_list()

    def update_list(self):
        strings = []
        factor = self.var_pos.Factor()
        unit = self.var_pos.UnitName()
        if unit in ('in', 'cm'):
            prec = 2
        else:
            prec = 1
        for line in self.guide_lines:
            pos, horizontal = line.Coordinates()
            if horizontal:
                format = _("% 6.*f %s    horizontal")
            else:
                format = _("% 6.*f %s    vertical")
            strings.append(format % (prec, pos / factor, unit))
        self.guides.SetList(strings)
        self.select_index(self.selected)

    def select_index(self, index):
        if index is not None and index < len(self.guide_lines):
            self.guides.Select(index)
            self.select_guide()
        else:
            self.selected = None

    def set_pos(self, *rest):
        if self.selected is not None:
            self.document.MoveGuideLine(self.guide_lines[self.selected],
                                        self.var_pos.get())

    def select_guide(self, *rest):
        sel = self.guides.curselection()
        if sel:
            self.selected = atoi(sel[0])
            pos, horizontal = self.guide_lines[self.selected].Coordinates()
            self.var_pos.set(pos)
            if horizontal:
                self.var_label.set(_("Y:"))
            else:
                self.var_label.set(_("X:"))
        else:
            self.selected = None

    def del_guide(self, *rest):
        if self.selected is not None:
            line = self.guide_lines[self.selected]
            self.document.RemoveGuideLine(line)

    def add_guide(self, horizontal):
        length = len(self.guide_lines)
        self.document.AddGuideLine(Point(0, 0), horizontal)
        self.select_index(length)
