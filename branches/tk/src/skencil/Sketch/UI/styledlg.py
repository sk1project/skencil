# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2000, 2002 by Bernhard Herzog
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
#	A Dialog for managing dynamic styles
#

from string import atoi

import Sketch
from Sketch import _, config
from Sketch.const import STYLE, SELECTION, COMMAND
from Sketch.warn import pdebug
from Sketch.Graphics.properties import property_names, property_titles, \
     property_types, FillProperty, LineProperty, FontProperty
from Tkinter import Button, Scrollbar, Frame, Checkbutton, Label, StringVar, \
     IntVar
from Tkinter import RIGHT, BOTTOM, X, Y, BOTH, LEFT, TOP, W, DISABLED, NORMAL,\
     END
from tkext import UpdatedButton, UpdatedListbox, MyEntry, MessageDialog

import skpixmaps
pixmaps = skpixmaps.PixmapTk

from sketchdlg import PropertyPanel, SKModal

class StylePanel(PropertyPanel):

    title = _("Styles")
    receivers = PropertyPanel.receivers[:]

    def __init__(self, master, main_window, doc):
        PropertyPanel.__init__(self, master, main_window, doc,
                               name = 'styledlg')

    def build_dlg(self):
        top = self.top

        button = UpdatedButton(top, text = _("Close"), name = 'close',
                               command = self.close_dlg)
        button.pack(side = BOTTOM, expand = 0, fill = X)
        button = UpdatedButton(top, text = _("Apply"),
                               command = self.apply_style,
                               sensitivecb = self.can_apply)
        button.pack(side = BOTTOM, expand = 0, fill = X)
        self.Subscribe(SELECTION, button.Update)

        button = UpdatedButton(top, text = _("Delete"),
                               command = self.remove_style,
                               sensitivecb = self.can_remove)
        button.pack(side = BOTTOM, expand = 0, fill = X)

        list_frame = Frame(top)
        list_frame.pack(side = TOP, expand = 1, fill = BOTH)

        sb_vert = Scrollbar(list_frame, takefocus = 0)
        sb_vert.pack(side = RIGHT, fill = Y)
        styles = UpdatedListbox(list_frame, name = 'list')
        styles.pack(expand = 1, fill = BOTH)
        styles.Subscribe(COMMAND, self.apply_style)
        sb_vert['command'] = (styles, 'yview')
        styles['yscrollcommand'] = (sb_vert, 'set')
        self.styles = styles

    def init_from_doc(self):
        self.styles_changed()
        self.Update()
        self.issue(SELECTION)

    def Update(self):
        self.styles.select_clear(0, END)
        properties = self.document.CurrentProperties()
        for name in properties.DynamicStyleNames():
            idx = self.style_names.index(name)
            self.styles.select_set(idx)
            self.styles.see(idx)

    receivers.append((STYLE, 'styles_changed'))
    def styles_changed(self):
        self.style_names = self.document.GetStyleNames()
        self.styles.SetList(self.style_names)
        self.Update()

    can_apply = PropertyPanel.doc_has_selection

    def apply_style(self):
        sel = self.styles.curselection()
        if sel:
            index = atoi(sel[0])
            self.document.AddStyle(self.style_names[index])

    def can_remove(self):
        len(self.styles.curselection()) == 1

    def remove_style(self):
        sel = self.styles.curselection()
        if sel:
            index = atoi(sel[0])
            self.document.RemoveDynamicStyle(self.style_names[index])


class CreateStyleDlg(SKModal):

    title = _("Create Style")

    def __init__(self, master, object, style_names, **kw):
        self.object = object
        self.style_names = style_names
        apply(SKModal.__init__, (self, master), kw)

    def __del__(self):
        if __debug__:
            pdebug('__del__', '__del__', self)

    def build_dlg(self):
        top = self.top

        self.var_style_name = StringVar(top)
        entry_name = MyEntry(top, textvariable = self.var_style_name,
                             command = self.ok, width = 15)
        entry_name.pack(side = TOP, fill = X)

        properties = self.object.Properties()
        self.flags = {}
        for prop in property_names:
            type = property_types[prop]
            if type == FillProperty:
                state = self.object.has_fill and NORMAL or DISABLED
            elif type == LineProperty:
                state = self.object.has_line and NORMAL or DISABLED
            elif type == FontProperty:
                state = self.object.has_font and NORMAL or DISABLED
            else:
                # unknown property type!
                continue
            long, short = property_titles[prop]
            self.flags[prop] = var = IntVar(top)
            var.set(state == NORMAL)
            radio = Checkbutton(top, text = long, state = state,
                                variable = var)
            radio.pack(side = TOP, anchor = W)

        but_frame = Frame(top)
        but_frame.pack(side = TOP, fill = BOTH, expand = 1)

        button = Button(but_frame, text = _("OK"), command = self.ok)
        button.pack(side = LEFT, expand = 1)
        button = Button(but_frame, text = _("Cancel"), command = self.cancel)
        button.pack(side = RIGHT, expand = 1)

        entry_name.focus()

    def ok(self, *args):
        name = self.var_style_name.get()
        if not name:
            MessageDialog(self.top, title =_("Create Style"),
                          message = _("Please enter a style name."),
                          icon = 'info')
            return
        if name in self.style_names:
            MessageDialog(self.top, title =_("Create Style"),
                          message = _("The name `%(name)s' is already used.\n"
                                      "Please choose another one.") % locals(),
                          icon = 'info')
            return

        which_properties = []
        for prop, var in self.flags.items():
            if var.get():
                which_properties.append(prop)
        self.close_dlg((name, which_properties))


def GetStyleName(master, object, style_names):
    dlg = CreateStyleDlg(master, object, style_names)
    return dlg.RunDialog()






class SetDefaultPropertiesDlg(SKModal):

    title = _("Set Default Properties")

    def __init__(self, master, category):
        self.category = category
        SKModal.__init__(self, master, name = 'setdefaults')

    def build_dlg(self):
        top = self.top

        label = Label(top, name = 'label',
                      text = _("Please select the object categories whose "
                               "default properties you want to change"))
        label.pack(side = TOP, anchor = W)
        frame = Frame(top)
        frame.pack(side = TOP)
        self.var_graphics = IntVar(top)
        if self.category != 'font':
            self.var_graphics.set(1)
        button = Checkbutton(frame, text = _("Graphics Objects"),
                             state = (self.category == 'font'
                                      and DISABLED or NORMAL),
                             variable = self.var_graphics)
        button.pack(side = TOP, anchor = W)
        self.var_text = IntVar(top)
        if self.category == 'font':
            self.var_text.set(1)
        button = Checkbutton(frame, text = _("Text Objects"),
                             state = (self.category == 'line'
                                      and DISABLED or NORMAL),
                             variable = self.var_text)
        button.pack(side = TOP, anchor = W)

        but_frame = Frame(top)
        but_frame.pack(side = TOP, fill = BOTH, expand = 1)

        button = Button(but_frame, text = _("OK"), command = self.ok)
        button.pack(side = LEFT, expand = 1)
        button = Button(but_frame, text = _("Cancel"), command = self.cancel)
        button.pack(side = RIGHT, expand = 1)

    def ok(self, *args):
        which_properties = (self.var_graphics.get(),
                            self.var_text.get())
        self.close_dlg(which_properties)


def WhichDefaultStyles(master, category = 0):
    dlg = SetDefaultPropertiesDlg(master, category)
    return dlg.RunDialog()


def set_properties(master, document, title, category, kw):
    if document.HasSelection():
        document.BeginTransaction(title)
        try:
            apply(document.SetProperties, (), kw)
        finally:
            document.EndTransaction()
    else:
        if config.preferences.set_default_properties:
            # remove the if_type_present argument if present. The font
            # dialog uses it in a kludgy way to avoid setting the font
            # on a non-text object.
            if kw.has_key("if_type_present"):
                del kw["if_type_present"]
            which = WhichDefaultStyles(master, category = category)
            if which:
                if which[0]:
                    Sketch.Graphics.properties.set_graphics_defaults(kw)
                if which[1]:
                    Sketch.Graphics.properties.set_text_defaults(kw)
