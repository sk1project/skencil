# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2001, 2002 by Bernhard Herzog
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

#
#       A dialog for specifying line properties
#

import operator

from X import LineDoubleDash

from Sketch.const import JoinMiter, JoinBevel, JoinRound,\
     CapButt, CapProjecting, CapRound
from Sketch.Lib import util
from Sketch import _, Trafo, SimpleGC, SolidPattern, EmptyPattern, \
     StandardDashes, StandardArrows, StandardColors


from Tkinter import Frame, Label, IntVar, LEFT, X, E, W, GROOVE
from tkext import ColorButton, UpdatedCheckbutton, MyOptionMenu2

from sketchdlg import StylePropertyPanel
from lengthvar import create_length_entry

import skpixmaps
pixmaps = skpixmaps.PixmapTk


def create_bitmap_image(tk, name, bitmap):
    data = util.xbm_string(bitmap)
    tk.call(('image', 'create', 'bitmap', name, '-foreground', 'black',
             '-data', data, '-maskdata', data))
    return name


_thickness = 3
_width = 90
def draw_dash_bitmap(gc, dashes):
    scale = float(_thickness)
    if dashes:
        dashes = map(operator.mul, dashes, [scale] * len(dashes))
        dashes = map(int, map(round, dashes))
        for idx in range(len(dashes)):
            length = dashes[idx]
            if length <= 0:
                dashes[idx] = 1
            elif length > 255:
                dashes[idx] = 255
    else:
        dashes = [_width + 10, 1]
    gc.SetDashes(dashes)
    gc.DrawLine(0, _thickness / 2, _width, _thickness / 2)

def create_dash_images(tk, tkwin, dashes):
    bitmap = tkwin.CreatePixmap(_width, _thickness, 1)
    gc = bitmap.CreateGC(foreground = 1, background = 0,
                         line_style = LineDoubleDash, line_width = _thickness)
    images = []
    for dash in dashes:
        draw_dash_bitmap(gc, dash)
        image = create_bitmap_image(tk, 'dash_' + `len(images)`, bitmap)
        images.append((image, dash))

    return gc, bitmap, images



_arrow_width = 31
_arrow_height = 25
_mirror = Trafo(-1, 0, 0, 1, 0, 0)


def draw_arrow_bitmap(gc, arrow, which = 2):
    gc.gc.foreground = 0
    gc.gc.FillRectangle(0, 0, _arrow_width + 1, _arrow_height + 1)
    gc.gc.foreground = 1
    y = _arrow_height / 2
    if which == 1:
        gc.PushTrafo()
        gc.Concat(_mirror)
    gc.DrawLineXY(0, 0, -1000, 0)
    if arrow is not None:
        arrow.Draw(gc)
    if which == 1:
        gc.PopTrafo()

def create_arrow_images(tk, tkwin, arrows):
    arrows = [None] + arrows
    bitmap = tkwin.CreatePixmap(_arrow_width, _arrow_height, 1)
    gc = SimpleGC()
    gc.init_gc(bitmap, foreground = 1, background = 0, line_width = 3)
    gc.Translate(_arrow_width / 2, _arrow_height / 2)
    gc.Scale(2)
    images1 = []
    for arrow in arrows:
        draw_arrow_bitmap(gc, arrow, 1)
        image = create_bitmap_image(tk, 'arrow1_' + `len(images1)`, bitmap)
        images1.append((image, arrow))
    images2 = []
    for arrow in arrows:
        draw_arrow_bitmap(gc, arrow, 2)
        image = create_bitmap_image(tk, 'arrow2_' + `len(images2)`, bitmap)
        images2.append((image, arrow))


    return gc, bitmap, images1, images2

class LinePanel(StylePropertyPanel):

    title = _("Line Style")

    def __init__(self, master, main_window, doc):
        StylePropertyPanel.__init__(self, master, main_window, doc,
                                    name = 'linedlg')

    def build_dlg(self):
        top = self.top

        button_frame = self.create_std_buttons(top)
        button_frame.grid(row = 5, columnspan = 2, sticky = 'ew')

        color_frame = Frame(top, relief = GROOVE, bd = 2)
        color_frame.grid(row = 0, columnspan = 2, sticky = 'ew')
        label = Label(color_frame, text = _("Color"))
        label.pack(side = LEFT, expand = 1, anchor = E)
        self.color_but = ColorButton(color_frame, width = 3, height = 1,
                                     command = self.set_line_color)
        self.color_but.SetColor(StandardColors.black)
        self.color_but.pack(side = LEFT, expand = 1, anchor = W)
        self.var_color_none = IntVar(top)
        check = UpdatedCheckbutton(color_frame, text = _("None"),
                                   variable = self.var_color_none,
                                   command = self.do_apply)
        check.pack(side = LEFT, expand = 1)

        width_frame = Frame(top, relief = GROOVE, bd = 2)
        width_frame.grid(row = 1, columnspan = 2, sticky = 'ew')
        label = Label(width_frame, text = _("Width"))
        label.pack(side = LEFT, expand = 1, anchor = E)

        self.var_width = create_length_entry(top, width_frame,
                                             self.set_line_width,
                                             scroll_pad = 0)

        tkwin = self.main_window.canvas.tkwin
        gc, bitmap, dashlist = create_dash_images(self.top.tk, tkwin,
                                                  StandardDashes())
        self.opt_dash = MyOptionMenu2(top, dashlist, command = self.set_dash,
                                      entry_type = 'image',
                                      highlightthickness = 0)
        self.opt_dash.grid(row = 2, columnspan = 2, sticky = 'ew', ipady = 2)
        self.dash_gc = gc
        self.dash_bitmap = bitmap

        gc, bitmap, arrow1, arrow2 = create_arrow_images(self.top.tk, tkwin,
                                                         StandardArrows())
        self.opt_arrow1 = MyOptionMenu2(top, arrow1, command = self.set_arrow,
                                        args = 1, entry_type = 'image',
                                        highlightthickness = 0)
        self.opt_arrow1.grid(row = 3, column = 0, sticky = 'ew', ipady = 2)
        self.opt_arrow2 = MyOptionMenu2(top, arrow2, command = self.set_arrow,
                                        args = 2, entry_type = 'image',
                                        highlightthickness = 0)
        self.opt_arrow2.grid(row = 3, column = 1, sticky = 'ew', ipady = 2)
        self.arrow_gc = gc
        self.arrow_bitmap = bitmap

        self.opt_join = MyOptionMenu2(top, [(pixmaps.JoinMiter, JoinMiter),
                                            (pixmaps.JoinRound, JoinRound),
                                            (pixmaps.JoinBevel, JoinBevel)],
                                      command = self.set_line_join,
                                      entry_type = 'bitmap',
                                      highlightthickness = 0)
        self.opt_join.grid(row = 4, column = 0, sticky = 'ew')

        self.opt_cap = MyOptionMenu2(top,
                                     [(pixmaps.CapButt, CapButt),
                                      (pixmaps.CapRound, CapRound),
                                      (pixmaps.CapProjecting, CapProjecting)],
                                     command = self.set_line_cap,
                                     entry_type = 'bitmap',
                                     highlightthickness = 0)
        self.opt_cap.grid(row = 4, column = 1, sticky = 'ew')
        self.opt_cap.SetValue(None)


    def close_dlg(self):
        StylePropertyPanel.close_dlg(self)
        self.var_width = None

    def init_from_style(self, style):
        if style.HasLine():
            self.var_color_none.set(0)
            self.opt_join.SetValue(style.line_join)
            self.opt_cap.SetValue(style.line_cap)
            self.color_but.SetColor(style.line_pattern.Color())
            self.var_width.set(style.line_width)
            self.init_dash(style)
            self.init_arrow(style)
        else:
            self.var_color_none.set(1)

    def init_from_doc(self):
        self.Update()

    def Update(self):
        if self.document.HasSelection():
            properties = self.document.CurrentProperties()
            self.init_from_style(properties)

    def do_apply(self):
        kw = {}
        if not self.var_color_none.get():
            color = self.color_but.Color()
            kw["line_pattern"]  = SolidPattern(color)
            kw["line_width"] = self.var_width.get()
            kw["line_join"] = self.opt_join.GetValue()
            kw["line_cap"] = self.opt_cap.GetValue()
            kw["line_dashes"] = self.opt_dash.GetValue()
            kw["line_arrow1"] = self.opt_arrow1.GetValue()
            kw["line_arrow2"] = self.opt_arrow2.GetValue()
        else:
            kw["line_pattern"] = EmptyPattern
        self.set_properties(_("Set Outline"), 'line', kw)

    def set_line_join(self, *args):
        self.document.SetProperties(line_join = self.opt_join.GetValue(),
                                    if_type_present = 1)

    def set_line_cap(self, *args):
        self.document.SetProperties(line_cap = self.opt_cap.GetValue(),
                                    if_type_present = 1)

    def set_line_color(self):
        self.document.SetLineColor(self.color_but.Color())

    def set_line_width(self, *rest):
        self.document.SetProperties(line_width = self.var_width.get(),
                                    if_type_present = 1)

    def set_dash(self, *args):
        self.document.SetProperties(line_dashes = self.opt_dash.GetValue(),
                                    if_type_present = 1)

    def init_dash(self, style):
        dashes = style.line_dashes
        draw_dash_bitmap(self.dash_gc, dashes)
        dash_image = create_bitmap_image(self.top.tk, 'dash_image',
                                         self.dash_bitmap)
        self.opt_dash.SetValue(dashes, dash_image)

    def set_arrow(self, arrow, which):
        if which == 1:
            self.document.SetProperties(line_arrow1 = arrow,
                                        if_type_present = 1)
        else:
            self.document.SetProperties(line_arrow2 = arrow,
                                        if_type_present = 1)

    def init_arrow(self, style):
        arrow = style.line_arrow1
        draw_arrow_bitmap(self.arrow_gc, arrow, 1)
        arrow_image = create_bitmap_image(self.top.tk, 'arrow1_image',
                                          self.arrow_bitmap)
        self.opt_arrow1.SetValue(arrow, arrow_image)

        arrow = style.line_arrow2
        draw_arrow_bitmap(self.arrow_gc, arrow, 2)
        arrow_image = create_bitmap_image(self.top.tk, 'arrow2_image',
                                          self.arrow_bitmap)
        self.opt_arrow2.SetValue(arrow, arrow_image)

    def update_from_object_cb(self, obj):
        if obj is not None:
            self.init_from_style(obj.Properties())


