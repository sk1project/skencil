# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2001 by Bernhard Herzog
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
#	A Dialog for selecting fonts
#

import string

from Tkinter import Scrollbar, Frame, Entry, Label, StringVar, DoubleVar
from Tkinter import Y, LEFT, W, FLAT, BOTH, RIGHT

from Sketch import config, _
from Sketch.Graphics import font, text, properties
from Sketch.const import SELECTION

from tkext import UpdatedListbox, MyEntry
from sketchdlg import StylePropertyPanel
from miniscroll import MiniScroller

std_sizes = (8, 9, 10, 12, 14, 18, 24, 36, 48, 72)


def get_from_list(item, list):
    # If item in list, return item, else try to find some standard items in
    # list. If that also fails return list[0]
    if item in list:
        return item
    return list[0]

class FontPanel(StylePropertyPanel):

    title = _("Fonts")

    def __init__(self, master, main_window, doc):
        self.family_to_fonts = font.make_family_to_fonts()
        self.families = self.family_to_fonts.keys()
        self.families.sort()
        StylePropertyPanel.__init__(self, master, main_window, doc,
                                    name = 'fontdlg')
        self.family_list.SetList(self.families)
        index = self.families.index(self.font_family)
        self.family_list.select_set(index)
        self.family_list.yview(index)

    def build_dlg(self):
        top = self.top

        buttons = self.create_std_buttons(top)
        buttons.grid(row = 3, column = 4, columnspan = 2, sticky = "news")

        self.sample_text = StringVar(top)
        self.sample_text.set(config.preferences.sample_text)
        self.sample = Entry(top, textvariable = self.sample_text,
                            relief = FLAT, bg = top['bg'],
                            width = len(config.preferences.sample_text))
        self.sample.grid(column = 0, row = 3, columnspan = 4, sticky = "news")
        # XXX: the background color of the sample text should be
        # configurable

        label = Label(top, text = _("Font Family:"), anchor = W)
        label.grid(column = 0, row = 0, columnspan = 2, sticky = "ew")
        sb_vert = Scrollbar(top, takefocus = 0)
        sb_vert.grid(column = 1, row = 1, rowspan = 2, sticky = "news")
        family_list = UpdatedListbox(top, name = 'families', height = 8)
        family_list.grid(column = 0, row = 1, rowspan = 2, sticky = "news")
        family_list.Subscribe(SELECTION, self.family_selected)
        sb_vert['command'] = (family_list, 'yview')
        family_list['yscrollcommand'] = (sb_vert, 'set')
        self.family_list = family_list

        label = Label(top, text = _("Font Style:"), anchor = W)
        label.grid(column = 2, row = 0, sticky = "ew")
        sb_vert = Scrollbar(top, takefocus = 0)
        sb_vert.grid(column = 3, row = 1, rowspan = 2, sticky = "news")
        self.font_attr_list = UpdatedListbox(top, name = 'weights', height = 4,
                                             width = 15)
        self.font_attr_list.grid(column = 2, row = 1, rowspan = 2,
                                 sticky = "news")
        self.font_attr_list.Subscribe(SELECTION, self.attr_selected)
        sb_vert['command'] = (self.font_attr_list, 'yview')
        self.font_attr_list['yscrollcommand'] = (sb_vert, 'set')

        label = Label(top, text = _("Size:"), anchor = W)
        label.grid(column = 4, row = 0, columnspan = 2, sticky = "ew")

        frame = Frame(top)
        frame.grid(column = 4, row = 1, columnspan = 2, sticky = 'ew')
        self.var_size = DoubleVar(top)
        scroll = MiniScroller(frame, variable = self.var_size,
                              min = 0.0, max = None, step = 1)
        scroll.pack(side = RIGHT, fill = Y)
        self.size_entry = MyEntry(frame, textvariable = self.var_size,
                                  width = 4, command = self.apply_size,
                                  justify = RIGHT)
        self.size_entry.pack(side = LEFT, expand = 1, fill = BOTH)

        sb_vert = Scrollbar(top, takefocus = 0)
        sb_vert.grid(column = 5, row = 2, sticky = "news")
        self.size_list = UpdatedListbox(top, name = 'sizes', width = 4,
                                        height = 5)
        self.size_list.grid(column = 4, row = 2, sticky = "news")
        self.size_list.Subscribe(SELECTION, self.size_selected)
        self.size_list.SetList(std_sizes)
        sb_vert['command'] = (self.size_list, 'yview')
        self.size_list['yscrollcommand'] = (sb_vert, 'set')

        top.columnconfigure(0, weight = 1000)
        top.columnconfigure(4, weight = 1)
        top.rowconfigure(2, weight = 1)

    def init_from_doc(self):
        object = self.document.CurrentObject()
        if object is not None and object.is_Text:
            self.update_from_object_cb(object)
        else:
            default = font.GetFont(config.preferences.default_font)
            self.font_family = default.family
            self.font_attr = default.font_attrs
            self.update_from_family()
            self.update_size(properties.default_text_style.font_size)

    def Update(self):
        self.update_from_object_cb(self.document.CurrentObject())

    def update_from_object_cb(self, obj):
        if obj is not None and obj.is_Text:
            font = obj.Font()
            self.font_family = font.family
            self.font_attr = font.font_attrs
            self.update_size(obj.FontSize())
            self.update_from_family()

    def do_apply(self):
        name = self.current_font_ps()
        if not name:
            if __debug__:
                pdebug(None, 'FontPanel.do_apply: no ps name!')
            return
        kw = {'font': font.GetFont(name),
              'font_size': self.var_size.get(),
              # set if_type_present to one to make sure that font
              # properties are only set on objects that can have font
              # properties. This is not ideal, but it works and needed
              # only simple changes to base.py
              'if_type_present': 1}
        self.set_properties(_("Set Font `%s'") % name, 'font', kw)

    def update_from_family(self, set_view = 1):
        index = self.families.index(self.font_family)
        self.family_list.Select(index, set_view)
        fonts = self.family_to_fonts[self.font_family]
        attrs = []
        for name in fonts:
            attrs.append(font.fontmap[name][1])

        attrs.sort()
        self.set_font_attrs(attrs)
        self.update_sample()

    def update_size(self, size):
        self.var_size.set(size)
        if size in std_sizes:
            self.size_list.Select(list(std_sizes).index(size), 1)
        else:
            self.size_list.SelectNone()

    def update_sample(self):
        xlfd = self.current_font_xlfd()
        if not xlfd:
            xlfd = 'fixed'
        self.sample['font'] = xlfd

    def set_font_attrs(self, attrs):
        self.font_attrs = attrs
        self.font_attr_list.SetList(attrs)
        self.font_attr = get_from_list(self.font_attr, attrs)
        self.font_attr_list.Select(attrs.index(self.font_attr), 1)

    def current_font_xlfd(self):
        fonts = self.family_to_fonts[self.font_family]
        for name in fonts:
            family, attrs, xlfd_start, encoding = font.fontmap[name]
            if attrs == self.font_attr:
                return font.xlfd_template % (xlfd_start, 24, encoding)
        return ''

    def current_font_ps(self):
        fonts = self.family_to_fonts[self.font_family]
        for name in fonts:
            family, attrs, xlfd_start, encoding = font.fontmap[name]
            if attrs == self.font_attr:
                return name
        return ''

    def family_selected(self):
        sel = self.family_list.curselection()
        if sel:
            index = string.atoi(sel[0])
            self.font_family = self.families[index]
            self.update_from_family(set_view = 0)

    def attr_selected(self):
        sel = self.font_attr_list.curselection()
        if sel:
            index = string.atoi(sel[0])
            self.font_attr = self.font_attrs[index]
            self.update_sample()

    def size_selected(self):
        sel = self.size_list.curselection()
        if sel:
            self.var_size.set(self.size_list.get(sel[0]))

    def apply_size(self, *args):
        if self.can_apply():
            size = self.var_size.get()
            self.document.CallObjectMethod(text.CommonText,
                                           _("Set Font Size %.1f") % size,
                                           'SetFontSize', size)

    def save_prefs(self):
        StylePropertyPanel.save_prefs(self)
        config.preferences.sample_text = self.sample_text.get()
