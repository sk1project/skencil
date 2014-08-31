# Sketch - A Python-based interactive drawing program  
# Copyright (C) 1998, 1999, 2000, 2003 by Bernhard Herzog
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


import PIL.Image
from X import GXxor, ZPixmap

from colorsys import hsv_to_rgb, rgb_to_hsv

from Sketch.const import CHANGED, ConstraintMask

from Sketch import _sketch
from Sketch import CreateRGBColor, StandardColors, Trafo, SketchError, \
     Publisher, _
from Sketch.Graphics import color

from Tkinter import Frame, Button, Label, DoubleVar, IntVar
from Tkinter import TOP, BOTTOM, LEFT, RIGHT, X, BOTH
from tkext import PyWidget
from miniscroll import create_mini_entry
from sketchdlg import SKModal

import skpixmaps
pixmaps = skpixmaps.PixmapTk



class MyDoubleVar(DoubleVar):

    def __init__(self, master = None, precision = 3):
        self.precision = precision
        DoubleVar.__init__(self, master)

    def set(self, value):
        DoubleVar.set(self, round(value, self.precision))

    def set_precision(self, precision):
        self.precision = precision


class ColorSample(PyWidget):

    def __init__(self, master=None, color = None, **kw):
        apply(PyWidget.__init__, (self, master), kw)
        self.gc_initialized = 0
        if color is None:
            color = StandardColors.black
        self.color = color

    def MapMethod(self):
        if not self.gc_initialized:
            self.init_gc()
            self.gc_initialized = 1

    def init_gc(self):
        self.visual = color.skvisual
        self.set_color(self.color)

    def set_color(self, color):
        self.color = color
        self.tkwin.SetBackground(self.visual.get_pixel(self.color))
        self.UpdateWhenIdle()

    def SetColor(self, color):
        if self.color != color:
            self.set_color(color)

    def RedrawMethod(self, region = None):
        self.tkwin.ClearArea(0, 0, 0, 0, 0)

    def ResizedMethod(self, width, height):
        pass


class ImageView(PyWidget):

    # display a PIL Image

    def __init__(self, master, image, **kw):
        width, height = image.size
        if not kw.has_key('width'):
            kw["width"] = width
        if not kw.has_key('height'):
            kw["height"] = height
        apply(PyWidget.__init__, (self, master), kw)
        self.gc_initialized = 0
        self.image = image
        self.ximage = None

    def MapMethod(self):
        if not self.gc_initialized:
            self.init_gc()
            self.gc_initialized = 1

    def init_gc(self):
        self.gc = self.tkwin.GetGC()
        self.visual = color.skvisual
        w = self.tkwin
        width, height = self.image.size
        depth = self.visual.depth
        if depth > 16:
            bpl = 4 * width
        elif depth > 8:
            bpl = ((2 * width + 3) / 4) * 4
        elif depth == 8:
            bpl = ((width + 3) / 4) * 4
        else:
            raise SketchError('unsupported depth for images')
        self.ximage = w.CreateImage(depth, ZPixmap, 0, None, width, height,
                                    32, bpl)
        self.set_image(self.image)

    def set_image(self, image):
        self.image = image
        if self.ximage:
            ximage = self.ximage
            _sketch.copy_image_to_ximage(self.visual, image.im, ximage,
                                         0, 0, ximage.width, ximage.height)
            self.UpdateWhenIdle()

    def RedrawMethod(self, region = None):
        self.gc.PutImage(self.ximage, 0, 0, 0, 0,
                         self.ximage.width, self.ximage.height)

    def ResizedMethod(self, width, height):
        pass

class ChooseComponent(ImageView, Publisher):

    def __init__(self, master, width, height, color = (0, 0, 0), **kw):
        image = PIL.Image.new('RGB', (width, height))
        apply(ImageView.__init__, (self, master, image), kw)
        self.set_color(color)
        self.drawn = 0
        self.dragging = 0
        self.drag_start = (0, 0, 0)
        self.update_pending = 1
        self.invgc = None
        self.bind('<ButtonPress>', self.ButtonPressEvent)
        self.bind('<Motion>', self.PointerMotionEvent)
        self.bind('<ButtonRelease>', self.ButtonReleaseEvent)

    def destroy(self):
        ImageView.destroy(self)
        Publisher.Destroy(self)

    def set_color(self, color):
        self.color = tuple(color)

    def init_gc(self):
        ImageView.init_gc(self)
        self.invgc = self.tkwin.GetGC(foreground = ~0,
                                      function = GXxor)
        self.tk.call(self._w, 'motionhints')
        self.show_mark()

    def ButtonPressEvent(self, event):
        if not self.dragging:
            self.drag_start = self.color
        self.dragging = self.dragging + 1
        self.move_to(self.win_to_color(event.x, event.y), event.state)

    def ButtonReleaseEvent(self, event):
        self.dragging = self.dragging - 1
        self.move_to(self.win_to_color(event.x, event.y), event.state)

    def PointerMotionEvent(self, event):
        if self.dragging:
            x, y = self.tkwin.QueryPointer()[4:6]
            self.move_to(self.win_to_color(x, y), event.state)

    #def moveto(self, x, y): #to be supplied by derived classes

    def hide_mark(self):
        if self.drawn:
            self.draw_mark()
            self.drawn = 0

    def show_mark(self):
        if not self.drawn and self.invgc:
            self.draw_mark()
            self.drawn = 1

    #def draw_mark(self):	# to be supplied by derived classes

    def UpdateWhenIdle(self):
        if not self.update_pending:
            self.update_pending = 1
            ImageView.UpdateWhenIdle(self)

    def RedrawMethod(self, region = None):
        if self.update_pending:
            self.update_ramp()
            self.update_pending = 0
        ImageView.RedrawMethod(self, region)
        if self.drawn:
            self.draw_mark()

    def RGBColor(self):
        return apply(CreateRGBColor, apply(hsv_to_rgb, self.color))

class ChooseRGBXY(ChooseComponent):

    def __init__(self, master, width, height, xcomp = 0, ycomp = 1,
                 color = (0, 0, 0), **kw):
        self.xcomp = xcomp
        self.ycomp = ycomp
        self.win_to_color = Trafo(1 / float(width - 1), 0,
                                  0, -1 / float(height - 1),
                                  0, 1)
        self.color_to_win = self.win_to_color.inverse()
        apply(ChooseComponent.__init__, (self, master, width, height, color),
              kw)

    def SetColor(self, color):
        color = apply(rgb_to_hsv, tuple(color))
        otheridx = 3 - self.xcomp - self.ycomp
        if color[otheridx] != self.color[otheridx]:
            self.UpdateWhenIdle()
        self.hide_mark()
        self.color = color
        self.show_mark()

    def update_ramp(self):
        _sketch.fill_hsv_xy(self.image.im, self.xcomp, self.ycomp, self.color)
        self.set_image(self.image)

    def move_to(self, p, state):
        x, y = p
        if state & ConstraintMask:
            sx = self.drag_start[self.xcomp]
            sy = self.drag_start[self.ycomp]
            if abs(sx - x) < abs(sy - y):
                x = sx
            else:
                y = sy
        if x < 0:	x = 0
        elif x >= 1.0:	x = 1.0
        if y < 0:	y = 0
        elif y >= 1.0:	y = 1.0

        color = list(self.color)
        color[self.xcomp] = x
        color[self.ycomp] = y
        self.hide_mark()
        self.color = tuple(color)
        self.show_mark()
        self.issue(CHANGED, self.RGBColor())

    def draw_mark(self):
        color = self.color
        w, h = self.image.size
        x, y = self.color_to_win(color[self.xcomp], color[self.ycomp])
        x = int(x)
        y = int(y)
        self.invgc.DrawLine(x, 0, x, h)
        self.invgc.DrawLine(0, y, w, y)


class ChooseRGBZ(ChooseComponent):

    def __init__(self, master, width, height, comp = 1, color = (0, 0, 0),
                 **kw):
        self.comp = comp
        self.win_to_color = Trafo(1, 0, 0, -1 / float(height - 1), 0, 1)
        self.color_to_win = self.win_to_color.inverse()
        apply(ChooseComponent.__init__, (self, master, width, height, color),
              kw)

    def SetColor(self, color):
        c = self.color;
        color = apply(rgb_to_hsv, tuple(color))
        if ((self.comp == 0 and (color[1] != c[1] or color[2] != c[2]))
            or (self.comp == 1 and (color[0] != c[0] or color[2] != c[2]))
            or (self.comp == 2 and (color[0] != c[0] or color[1] != c[1]))):
            self.hide_mark()
            self.color = color
            self.show_mark()
            self.UpdateWhenIdle()

    def update_ramp(self):
        _sketch.fill_hsv_z(self.image.im, self.comp, self.color)
        self.set_image(self.image)

    def move_to(self, p, state):
        y = p.y
        if y < 0:	y = 0
        elif y >= 1.0:	y = 1.0

        color = list(self.color)
        color[self.comp] = y
        self.hide_mark()
        self.color = tuple(color)
        self.show_mark()
        self.issue(CHANGED, self.RGBColor())

    def draw_mark(self):
        w, h = self.image.size
        x, y = self.color_to_win(0, self.color[self.comp])
        x = int(x)
        y = int(y)
        self.invgc.DrawLine(0, y, w, y)


xyramp_size = (150, 150)
zramp_size = (15, 150)

class ChooseColorDlg(SKModal):

    title = _("Select Color")
    class_name = 'ColorDialog'

    def __init__(self, master, color, **kw):
        self.color = color
        self.orig_color = color
        apply(SKModal.__init__, (self, master), kw)

    def build_dlg(self):
        top = self.top

        frame = Frame(top)
        frame.pack(side = BOTTOM, fill = BOTH, expand = 1)
        button = Button(frame, text = _("OK"), command = self.ok)
        button.pack(side = LEFT, expand = 1)
        button = Button(frame, text = _("Cancel"), command = self.cancel)
        button.pack(side = RIGHT, expand = 1)

        self.label = Label(top)
        self.label.pack(side = BOTTOM)

        viewxy = ChooseRGBXY(top, xyramp_size[0], xyramp_size[1], 0, 1)
        viewxy.pack(side = LEFT)

        viewz = ChooseRGBZ(top, zramp_size[0], zramp_size[1], 2)
        viewz.pack(side = LEFT)

        frame1 = Frame(top)
        frame1.pack(side = RIGHT)

        frame = Frame(frame1)
        frame.pack(side = TOP)

        sample = ColorSample(frame, self.color, width = 30, height = 30)
        sample.pack(side = RIGHT)
        sample = ColorSample(frame, self.color, width = 30, height = 30)
        sample.pack(side = RIGHT)

        frame = Frame(frame1)
        frame.pack(side = TOP)
        label = Label(frame, text = "H")
        label.pack(side = LEFT)
        self.var1 = create_mini_entry(top, frame, self.component_changed,
                                      min = 0, max = 1.0, step = 0.01,
                                      vartype = MyDoubleVar)
        frame = Frame(frame1)
        frame.pack(side = TOP)
        label = Label(frame, text = "S")
        label.pack(side = LEFT)
        self.var2 = create_mini_entry(top, frame, self.component_changed,
                                      min = 0, max = 1.0, step = 0.01,
                                      vartype = MyDoubleVar)
        frame = Frame(frame1)
        frame.pack(side = TOP)
        label = Label(frame, text = "V")
        label.pack(side = LEFT)
        self.var3 = create_mini_entry(top, frame, self.component_changed,
                                      min = 0, max = 1.0, step = 0.01,
                                      vartype = MyDoubleVar)

        frame = Frame(frame1)
        frame.pack(side = TOP)
        label = Label(frame, text = "R")
        label.pack(side = LEFT)
        self.var4 = create_mini_entry(top, frame, self.rgb_component_changed,
                                      min = 0, max = 255, step = 1,
                                      vartype = IntVar)

        frame = Frame(frame1)
        frame.pack(side = TOP)
        label = Label(frame, text = "G")
        label.pack(side = LEFT)
        self.var5 = create_mini_entry(top, frame, self.rgb_component_changed,
                                      min = 0, max = 255, step = 1,
                                      vartype = IntVar)

        frame = Frame(frame1)
        frame.pack(side = TOP)
        label = Label(frame, text = "B")
        label.pack(side = LEFT)
        self.var6 = create_mini_entry(top, frame, self.rgb_component_changed,
                                      min = 0, max = 255, step = 1,
                                      vartype = IntVar)

        viewxy.Subscribe(CHANGED, self.color_changed)
        viewz.Subscribe(CHANGED, self.color_changed)
        self.viewxy = viewxy
        self.viewz = viewz
        self.sample = sample

        self.color_changed(self.color)

    def color_changed(self, color):
        self.label.configure(text = '%.3f %.3f %.3f' % tuple(color))
        self.viewxy.SetColor(color)
        self.viewz.SetColor(color)
        self.sample.SetColor(color)
        v1, v2, v3 = apply(rgb_to_hsv, tuple(color))
        self.var1.set(v1)
        self.var2.set(v2)
        self.var3.set(v3)
        self.var4.set(int(color[0]*255))
        self.var5.set(int(color[1]*255))
        self.var6.set(int(color[2]*255))
        self.color = color


    def component_changed(self, *rest):
        color = (self.var1.get(), self.var2.get(), self.var3.get())
        color = apply(CreateRGBColor, apply(hsv_to_rgb, color))
        self.color_changed(color)

    def rgb_component_changed(self, *rest):
        self.color_changed(CreateRGBColor(self.var4.get() / 255.0,
                                          self.var5.get() / 255.0,
                                          self.var6.get() / 255.0))



    def ok(self, *args):
        self.close_dlg(self.color)

def GetColor(master, color):
    dlg = ChooseColorDlg(master, color)
    return dlg.RunDialog()
