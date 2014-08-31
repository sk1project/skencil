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
from Tkinter import Frame, Label, IntVar
from Tkinter import RIGHT, BOTTOM, X, Y, BOTH, LEFT, TOP, GROOVE, E,\
     DISABLED, NORMAL
from tkext import UpdatedButton, MyEntry

from miniscroll import MiniScroller

from sketchdlg import PropertyPanel
from Sketch.const import SELECTION

from Sketch.Graphics.blendgroup import BlendGroup, BlendInterpolation, \
     SelectStart, SelectEnd

from Sketch import _, config


class BlendPanel(PropertyPanel):

    title = _("Blend")
    def __init__(self, master, main_window, doc):
        PropertyPanel.__init__(self, master, main_window, doc,
                               name = 'blenddlg')

    def build_dlg(self):
        top = self.top

        button_frame = Frame(top)
        button_frame.pack(side = BOTTOM, fill = BOTH, expand = 1)

        self.update_buttons = []
        button = UpdatedButton(top, text = _("Apply"),
                               command = self.apply_blend,
                               sensitivecb = self.doc_can_blend)
        button.pack(in_ = button_frame, side = LEFT, expand = 1, fill = X)
        self.Subscribe(SELECTION, button.Update)

        button = UpdatedButton(top, text = _("Close"),
                               command = self.close_dlg)
        button.pack(in_ = button_frame, side = RIGHT, expand = 1, fill = X)

        steps_frame = Frame(top, relief = GROOVE, bd = 2)
        steps_frame.pack(side = TOP, fill = X, expand = 1)
        label = Label(steps_frame, text = _("Steps"))
        label.pack(side = LEFT, anchor = E)
        self.var_steps = IntVar(top)
        self.var_steps.set(config.preferences.blend_panel_default_steps)
        self.entry = MyEntry(steps_frame, name = 'steps',
                             textvariable = self.var_steps,
                             command = self.apply_blend)
        self.entry.pack(side = LEFT, expand = 1, fill = X, anchor = E)
        scroll = MiniScroller(steps_frame, variable = self.var_steps,
                              min = 2, max = None, step = 1)
        scroll.pack(side = LEFT, fill = Y)

        button = UpdatedButton(top, text = _("Select Start"),
                               sensitivecb = self.can_select,
                               command = self.select_control,
                               args = SelectStart)
        button.pack(side = BOTTOM, fill = X, expand = 1)
        self.Subscribe(SELECTION, button.Update)

        button = UpdatedButton(top, text = _("Select End"),
                               sensitivecb = self.can_select,
                               command = self.select_control,
                               args = SelectEnd)
        button.pack(side = BOTTOM, fill = X, expand = 1)
        self.Subscribe(SELECTION, button.Update)

    def doc_can_blend(self):
        return ((self.document.CanBlend() or self.current_obj_is_blend())
                and self.var_steps.get() >= 2)

    def current_obj_is_blend(self):
        object = self.document.CurrentObject()
        return (object is not None
                and (object.is_BlendInterpolation
                     or (object.is_Blend and object.NumObjects() == 3)))

    def current_object(self):
        # assume current_obj_is_blend() yields true
        object = self.document.CurrentObject()
        if object.is_Blend:
            # XXX reaching into object.objects is ugly
            object = object.objects[1]
        return object

    def init_from_doc(self):
        self.Update()
        self.issue(SELECTION)

    def Update(self):
        if self.current_obj_is_blend():
            steps = self.current_object().Steps()
            self.var_steps.set(steps)
            if self.doc_can_blend():
                self.entry['state'] = NORMAL
            else:
                self.entry['state'] = DISABLED

    def apply_blend(self, *args):
        steps = self.var_steps.get()
        if self.current_obj_is_blend() and steps >= 2:
            doc = self.document
            doc.BeginTransaction(_("Set %d Blend Steps") % steps)
            try:
                try:
                    doc.AddUndo(self.current_object().SetParameters(steps))
                except:
                    doc.AbortTransaction()
            finally:
                doc.EndTransaction()
        else:
            self.document.Blend(steps)

    def can_select(self):
        object = self.document.CurrentObject()
        return (object is not None
                and (object.parent.is_Blend or object.is_Blend))

    def select_control(self, which):
        object = self.document.CurrentObject()
        if object is not None:
            if object.is_Blend:
                # XXX reaching into object.objects is ugly
                if which == SelectStart:
                    child = object.objects[0]
                else:
                    child = object.objects[-1]
                self.document.SelectObject(child)
            elif object.parent.is_Blend:
                object.parent.SelectControl(object, which)
