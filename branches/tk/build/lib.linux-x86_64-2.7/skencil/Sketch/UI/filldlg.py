# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2003 by Bernhard Herzog
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
#	A dialog for specifying the fill style
#

import os
from math import atan2, sin, cos, pi

import X
Xconst = X
from Tkinter import Frame, Label, IntVar, DoubleVar, Radiobutton, StringVar
from Tkinter import RIGHT, BOTTOM, X, Y, LEFT, TOP, W, E, N
from tkext import UpdatedButton, UpdatedCheckbutton, ColorButton, MyEntry
from tkext import PyWidget

from Sketch import _, Publisher, GraphicsDevice, StandardColors, \
     EmptyFillStyle, EmptyLineStyle, \
     PropertyStack, SolidPattern, LinearGradient, ConicalGradient, \
     RadialGradient, HatchingPattern, EmptyPattern, ImageTilePattern, \
     CreateSimpleGradient, Point, Rect, Trafo, load_image, config
from Sketch.const import CHANGED, ConstraintMask, DROP_COLOR
from Sketch.warn import warn_tb, INTERNAL

from miniscroll import MiniScroller
from sketchdlg import StylePropertyPanel
from lengthvar import LengthVar, create_unit_menu
import gradientedit

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

class PatternSample(PyWidget):

    def __init__(self, master=None, **kw):
        apply(PyWidget.__init__, (self, master), kw)
        self.gc_initialized = 0
        self.gc = GraphicsDevice()
        self.pattern = EmptyPattern
        self.properties = PropertyStack()
        self.properties.AddStyle(EmptyLineStyle)
        self.properties.SetProperty(fill_pattern = self.pattern)
        self.gc.SetProperties(self.properties)
        self.fill_rect = None

    def MapMethod(self):
        self.fill_rect = Rect(0, 0, self.tkwin.width, self.tkwin.height)
        if not self.gc_initialized:
            self.init_gc()
            self.gc_initialized = 1

    def init_gc(self):
        self.gc.init_gc(self.tkwin)
        self.compute_trafo()

    def compute_trafo(self):
        height = self.tkwin.height
        doc_to_win = Trafo(1, 0, 0, -1, 0, height)
        win_to_doc = doc_to_win.inverse()
        self.gc.SetViewportTransform(1.0, doc_to_win, win_to_doc)
        self.fill_rect = Rect(0, 0, self.tkwin.width, self.tkwin.height)
        self.gc.SetProperties(self.properties, self.fill_rect)

    def SetPattern(self, pattern):
        if pattern != self.pattern:
            self.pattern = pattern
            self.UpdateWhenIdle()
            self.properties.SetProperty(fill_pattern = pattern)
            self.gc.SetProperties(self.properties, self.fill_rect)

    def RedrawMethod(self, region = None):
        win = self.tkwin
        self.gc.StartDblBuffer()
        self.gc.SetFillColor(StandardColors.white)
        self.gc.FillRectangle(0, 0, win.width, win.height)
        if self.properties.HasFill():
            self.gc.Rectangle(Trafo(win.width, 0, 0, win.height, 0, 0))
        else:
            self.gc.SetLineColor(StandardColors.black)
            self.gc.DrawLineXY(0, win.height, win.width, 0)
        self.gc.EndDblBuffer()

    def ResizedMethod(self, width, height):
        self.gc.WindowResized(width, height)
        self.UpdateWhenIdle()
        self.compute_trafo()


CENTER = 'center'
DIRECTION = 'direction'

class InteractiveSample(PatternSample, Publisher):

    allow_edit_center = 0
    allow_edit_dir = 0

    def __init__(self, master=None, **kw):
        apply(PatternSample.__init__, (self, master), kw)
        self.bind('<ButtonPress>', self.ButtonPressEvent)
        self.bind('<Motion>', self.PointerMotionEvent)
        self.bind('<ButtonRelease>', self.ButtonReleaseEvent)
        self.current_mode = 0	# 0: center, 1: direction
        self.current_pos = (0, 0)
        self.center = (0, 0)
        self.drawn = 0
        self.dragging = 0

    def destroy(self):
        Publisher.Destroy(self)
        PatternSample.destroy(self)

    def SetEditMode(self, center, direction):
        self.allow_edit_center = center
        self.allow_edit_dir = direction

    def SetCenter(self, pos):
        x, y = pos
        x =	 x  * self.tkwin.width
        y = (1 - y) * self.tkwin.height
        self.center = (x, y)

    def init_gc(self):
        PatternSample.init_gc(self)
        self.inv_gc = self.tkwin.CreateGC(foreground = ~0,
                                          function = Xconst.GXxor)

    def ButtonPressEvent(self, event):
        button = event.num
        if button == Xconst.Button1 and self.allow_edit_center:
            self.current_mode = 0
        elif self.allow_edit_dir:
            self.current_mode = 1
        else:
            return

        self.current_pos = (event.x, event.y, event.state & ConstraintMask)
        self.show_edit()
        self.dragging = 1

    def PointerMotionEvent(self, event):
        if self.dragging:
            self.hide_edit()
            self.current_pos = (event.x, event.y, event.state & ConstraintMask)
            self.show_edit()

    def ButtonReleaseEvent(self, event):
        if self.dragging:
            self.hide_edit()
            self.current_pos = (event.x, event.y, event.state & ConstraintMask)
            self.report_edit()
            self.dragging = 0

    def show_edit(self):
        if not self.drawn:
            self.draw_edit()
            self.drawn = 1

    def hide_edit(self):
        if self.drawn:
            self.draw_edit()
            self.drawn = 0

    def constrain_center(self, x, y):
        width = self.tkwin.width
        height = self.tkwin.height
        x = float(x) / width
        y = float(y) / height
        if   x < 0.25:	x = 0
        elif x < 0.75:	x = 0.5
        else:		x = 1.0

        if   y < 0.25:	y = 0
        elif y < 0.75:	y = 0.5
        else:		y = 1.0

        return (int(width * x), int(height * y))

    def draw_edit(self):
        x, y, constraint = self.current_pos
        if self.current_mode == 0:
            if constraint:
                x, y = self.constrain_center(x, y)
            self.inv_gc.DrawLine(0, y, self.tkwin.width, y)
            self.inv_gc.DrawLine(x, 0, x, self.tkwin.height)
        else:
            cx, cy = self.center

            angle = atan2(y - cy, x - cx) + 2 * pi
            if constraint:
                pi12 = pi / 12
                angle = pi12 * int(angle / pi12 + 0.5)

            x = cx + cos(angle) * 1000.0
            y = cy + sin(angle) * 1000.0

            self.inv_gc.DrawLine(int(cx), int(cy), int(x), int(y))

    def report_edit(self):
        x, y, constraint = self.current_pos
        if self.current_mode == 0:
            if constraint:
                x, y = self.constrain_center(x, y)
            x =	    float(x) / self.tkwin.width
            y = 1 - float(y) / self.tkwin.height
            self.issue(CENTER, (x, y))
        else:
            cx, cy = self.center

            angle = atan2(y - cy, x - cx) + 2 * pi
            if constraint:
                pi12 = pi / 12
                angle = pi12 * int(angle / pi12 + 0.5)

            self.issue(DIRECTION, (cos(angle), -sin(angle)) )

    def RedrawMethod(self, region):
        PatternSample.RedrawMethod(self, region)
        self.drawn = 0


class PatternFrame(Frame, Publisher):

    def __init__(self, master=None, **kw):
        apply(Frame.__init__, (self, master), kw)
        self.dialog = None
        self.pattern = EmptyPattern

    def SetPattern(self, pattern):
        self.pattern = pattern.Duplicate()	# should be Copy...

    def Pattern(self):
        return self.pattern

    def destroy(self):
        Publisher.Destroy(self)
        Frame.destroy(self)

    def SetCenter(self, center):
        pass

    def SetDirection(self, dir):
        pass

    def Center(self):
        return (0.5, 0.5)

    def EditModes(self):
        return (0, 0)


class SolidPatternFrame(PatternFrame):

    def __init__(self, master=None, **kw):
        apply(PatternFrame.__init__, (self, master), kw)

        label = Label(self, text = _("Color"))
        label.pack(side = LEFT, expand = 1, anchor = E)
        self.color_but = ColorButton(self, width = 3, height = 1,
                                     command = self.set_color)
        self.color_but.pack(side = LEFT, expand = 1, anchor = W)

        self.SetPattern(SolidPattern(StandardColors.black))

    def set_color(self):
        self.pattern = SolidPattern(self.__get_color())
        self.issue(CHANGED)

    def __get_color(self):
        return self.color_but.Color()

    def SetPattern(self, pattern):
        PatternFrame.SetPattern(self, pattern)
        self.color_but.SetColor(pattern.Color())


gradient_types = [LinearGradient, ConicalGradient, RadialGradient]

class GradientPatternFrame(PatternFrame):

    def __init__(self, master=None, **kw):
        apply(PatternFrame.__init__, (self, master), kw)

        gradient = CreateSimpleGradient(StandardColors.white,
                                        StandardColors.black)
        frame = Frame(self)
        frame.pack(side = TOP, fill = X)
        self.var_gradient_type = IntVar(self)
        for value, bitmap in [(0, 'linear'), (1, 'conical'), (2, 'radial')]:
            bitmap = getattr(pixmaps, 'gradient_' + bitmap)
            button = make_button(frame, bitmap = bitmap, value = value,
                                 variable = self.var_gradient_type,
                                 command = self.choose_type)
            button.pack(side = LEFT, fill = X, expand = 1)

        frame = Frame(self)
        frame.pack(side = TOP, expand = 1, fill = X)
        self.colors = [None, None]
        self.colors[0] = ColorButton(frame, height = 1,
                                     color = gradient.StartColor(),
                                     command = self.set_color, args = 0)
        self.colors[0].pack(side = LEFT, fill = X, expand = 1)
        self.colors[1] =  ColorButton(frame, height = 1,
                                      color = gradient.EndColor(),
                                      command = self.set_color, args = 1)
        self.colors[1].pack(side = LEFT, fill = X, expand = 1)

        self.var_border = DoubleVar(self)
        self.var_border.set(0.0)
        frame = Frame(self)
        frame.pack(side = TOP, fill = X, expand = 1)
        label = Label(frame, text = _("Border"))
        label.pack(side = LEFT, expand = 1, anchor = E)
        entry = MyEntry(frame, textvariable = self.var_border, width = 4,
                        justify = RIGHT, command = self.set_border)
        entry.pack(side = LEFT, expand = 1, fill = X)
        scroll = MiniScroller(frame, variable = self.var_border,
                              min = 0.0, max = 100.0, step = 1.0,
                              command = self.set_border)
        scroll.pack(side = LEFT, fill = Y)

        button = UpdatedButton(self, text = _("Edit Gradient"),
                               command = self.edit_gradient)
        button.pack(side = TOP, fill = X)

        pattern = LinearGradient(gradient)
        self.SetPattern(pattern)


    def set_color(self, idx):
        self.gradient = self.gradient.Duplicate()
        self.gradient.SetStartColor(self.__get_color(0))
        self.gradient.SetEndColor(self.__get_color(1))
        self.pattern = self.pattern.Duplicate()
        self.pattern.SetGradient(self.gradient)
        self.issue(CHANGED)

    def __get_color(self, idx):
        return self.colors[idx].Color()

    def choose_type(self):
        type = gradient_types[self.var_gradient_type.get()]
        self.pattern = type(duplicate = self.pattern)
        self.issue(CHANGED)

    def set_border(self, *rest):
        border = self.var_border.get() / 100.0
        if hasattr(self.pattern, 'SetBorder'):
            self.pattern = self.pattern.Duplicate()
            self.pattern.SetBorder(border)
            self.issue(CHANGED)

    def SetPattern(self, pattern):
        PatternFrame.SetPattern(self, pattern)
        self.gradient = gradient = pattern.Gradient().Duplicate()
        self.var_gradient_type.set(gradient_types.index(pattern.__class__))
        self.colors[0].SetColor(gradient.StartColor())
        self.colors[1].SetColor(gradient.EndColor())
        if hasattr(pattern, 'Border'):
            self.var_border.set(pattern.Border() * 100.0)

    def Center(self):
        if self.pattern.__class__ == LinearGradient:
            return (0.5, 0.5)
        return tuple(self.pattern.Center())

    def SetCenter(self, center):
        if self.pattern.__class__ == LinearGradient:
            return
        p = apply(Point, center)
        self.pattern = self.pattern.Duplicate()
        self.pattern.SetCenter(p)
        self.issue(CHANGED)

    def SetDirection(self, dir):
        if self.pattern.__class__ == RadialGradient:
            return
        dir = apply(Point, dir)
        self.pattern = self.pattern.Duplicate()
        self.pattern.SetDirection(dir)
        self.issue(CHANGED)

    def EditModes(self):
        if self.pattern.__class__ == LinearGradient:
            return (0, 1)
        elif self.pattern.__class__ == RadialGradient:
            return (1, 0)
        else:
            return (1, 1)

    def edit_gradient(self):
        gradient = gradientedit.EditGradient(self, self.gradient)
        if gradient is not None:
            pattern = self.pattern.Duplicate()
            pattern.SetGradient(gradient)
            self.SetPattern(pattern)
            self.issue(CHANGED)



class HatchingPatternFrame(PatternFrame):

    def __init__(self, master=None, **kw):
        apply(PatternFrame.__init__, (self, master), kw)

        frame = Frame(self)
        frame.pack(side = TOP, fill = X, expand = 1)
        self.colors = [None, None]
        self.colors[0] = ColorButton(frame, height = 1,
                                     command = self.set_color, args = 0)
        self.colors[0].pack(side = LEFT, fill = X, expand = 1)
        self.colors[1] = ColorButton(frame, height = 1,
                                     command = self.set_color, args = 1)
        self.colors[1].pack(side = LEFT, fill = X, expand = 1)

        var_spacing_number = DoubleVar(self)
        var_unit = StringVar(self)
        self.var_spacing = LengthVar(1.0, config.preferences.default_unit,
                                     var_spacing_number, var_unit,
                                     command = self.set_spacing)
        width_frame = Frame(self)
        width_frame.pack(side = TOP, fill = X, expand = 1)
        #label = Label(width_frame, text = 'Spacing')
        #label.pack(side = LEFT, expand = 1, anchor = E)
        entry = MyEntry(width_frame, textvariable = var_spacing_number,
                        justify = RIGHT, width = 6,
                        command = self.var_spacing.UpdateNumber)
        entry.pack(side = LEFT, expand = 1, fill = X)
        scroll = MiniScroller(width_frame, variable = var_spacing_number,
                              min = 0.0, max = None, step = 1.0,
                              command = self.var_spacing.UpdateNumber)
        scroll.pack(side = LEFT, fill = Y)
        optmenu = create_unit_menu(width_frame, self.var_spacing.UpdateUnit,
                                   variable = var_unit,
                                   indicatoron = 0, width = 3)
        optmenu.pack(side = LEFT, expand = 1, fill = X, anchor = W)

        self.SetPattern(HatchingPattern(StandardColors.red))

    def set_color(self, idx):
        self.pattern = self.pattern.Duplicate()
        self.pattern.SetForeground(self.__get_color(0))
        self.pattern.SetBackground(self.__get_color(1))
        self.issue(CHANGED)

    def __get_color(self, idx):
        return self.colors[idx].Color()

    def set_spacing(self, *rest):
        spacing = self.var_spacing.get()
        self.pattern = self.pattern.Duplicate()
        self.pattern.SetSpacing(spacing)
        self.issue(CHANGED)

    def SetPattern(self, pattern):
        PatternFrame.SetPattern(self, pattern)
        self.colors[0].SetColor(pattern.Foreground())
        self.colors[1].SetColor(pattern.Background())
        self.var_spacing.set(pattern.Spacing())

    def SetDirection(self, dir):
        dir = apply(Point, dir)
        self.pattern = self.pattern.Duplicate()
        self.pattern.SetDirection(dir)
        self.issue(CHANGED)

    def EditModes(self):
        return (0, 1)


class ImageTilePatternFrame(PatternFrame):

    def __init__(self, master, main_window, **kw):
        apply(PatternFrame.__init__, (self, master), kw)
        self.main_window = main_window
        button = UpdatedButton(self, text = _("Load Image..."),
                               command = self.load_image)
        button.pack(side = TOP, fill = X)
        button = UpdatedButton(self, text = _("Pick Image..."),
                               command = self.pick_image)
        button.pack(side = TOP, fill = X)

        file = os.path.join(config.std_res_dir, config.preferences.pattern)
        try:
            file = open(file)
            tile = load_image(file)
        except:
            warn_tb(INTERNAL, "Cannot load %s", file)
            return
        self.SetPattern(ImageTilePattern(tile))

    def load_image(self):
        dir = config.preferences.pattern_dir
        filename = self.main_window.GetOpenImageFilename(no_eps = 1,
                                                         initialdir = dir)
        if not filename:
            return
        try:
            tile = load_image(filename)
        except IOError, value:
            if type(value) == type(()):
                value = value[1]
            basename = os.path.split(filename)[1]
            self.main_window.application.MessageBox(title = _("Load Image"),
                                                    message=_("Cannot load %(filename)s:\n"
                                                              "%(message)s") \
                                                    % {'filename':`basename`,
                                                       'message':value},
                                                    icon = 'warning')
        else:
            self.SetPattern(ImageTilePattern(tile))
            self.issue(CHANGED)
            config.preferences.pattern_dir = os.path.split(filename)[0]

    def pick_image(self):
        self.main_window.canvas.PickObject(self.update_from_image)

    def update_from_image(self, obj):
        if obj is not None:
            if obj.is_Image:
                # XXX data is no public attribute
                self.SetPattern(ImageTilePattern(obj.data))
                self.issue(CHANGED)
            elif obj.has_properties:
                pattern = obj.Properties().fill_pattern
                if pattern.__class__ == ImageTilePattern:
                    # XXX data is no public attribute
                    self.SetPattern(ImageTilePattern(pattern.data))
                    self.issue(CHANGED)


class FillPanel(StylePropertyPanel):

    title = _("Fill Style")

    def __init__(self, master, main_window, doc):
        StylePropertyPanel.__init__(self, master, main_window, doc,
                                    name = 'filldlg')

    def build_dlg(self):
        top = self.top

        # a bit of a hack to accept drops...
        top.accept_drop = (DROP_COLOR,)
        top.DropAt = self.DropAt

        # the standard buttons (apply, cancel, update...)
        button_frame = self.create_std_buttons(top)
        button_frame.pack(side = BOTTOM, fill = X, expand = 0)

        #
        self.var_transform = IntVar(top)
        self.var_transform.set(1)
        button = UpdatedCheckbutton(top, text = _("Transform Pattern"),
                                    variable = self.var_transform,
                                    command = self.set_fill_transform)
        button.pack(side = BOTTOM, fill = X)

        # type frame
        type_frame = Frame(top)
        type_frame.pack(side = LEFT, fill = Y, expand = 0)

        # sample
        self.sample = InteractiveSample(top, width = 60, height = 60,
                                        background = 'white')
        self.sample.pack(side = TOP, fill = X, anchor = N)
        self.sample.SetPattern(EmptyPattern)
        self.sample.Subscribe(CENTER, self.center_changed)
        self.sample.Subscribe(DIRECTION, self.direction_changed)

        # pattern frames
        self.frames = [None, None, None, None, None]
        self.frames[0] = PatternFrame(top)
        self.frames[1] = SolidPatternFrame(top)
        self.frames[2] = GradientPatternFrame(top)
        self.frames[3] = HatchingPatternFrame(top)
        self.frames[4] = ImageTilePatternFrame(top,
                                               main_window = self.main_window)

        width = 0
        for frame in self.frames:
            frame.Subscribe(CHANGED, self.pattern_changed, 1)
            frame.update()
            w = frame.winfo_reqwidth()
            if w > width:
                width = w

        self.sample.config(width = width)

        self.var_pattern_type = IntVar(top)
        types = ((0, pixmaps.fill_none), (1, pixmaps.fill_solid),
                 (2, pixmaps.fill_gradient), (3, pixmaps.fill_hatch),
                 (4, pixmaps.fill_tile))
        for value, bitmap in types:
            button = make_button(type_frame, bitmap = bitmap, value = value,
                                 variable = self.var_pattern_type,
                                 command = self.choose_pattern)
            button.pack(side = TOP)

        # unknown
        self.frame_unknown = PatternFrame(top)

        self.active_frame = None

    def close_dlg(self):
        StylePropertyPanel.close_dlg(self)
        self.top.DropAt = None

    def activate_frame(self, frame):
        if self.active_frame != frame:
            if self.active_frame:
                self.active_frame.forget()
            if frame:
                frame.pack(side = TOP, fill = X)
            self.active_frame = frame
            self.update_sample()

    def choose_pattern(self, idx = None, pattern = None):
        if idx is None:
            idx = self.var_pattern_type.get()
        else:
            self.var_pattern_type.set(idx)
        self.activate_frame(self.frames[idx])
        if pattern is not None:
            self.active_frame.SetPattern(pattern)
        self.update_sample()

    def init_from_pattern(self, pattern, transform = 1):
        if pattern.__class__ == SolidPattern:
            self.choose_pattern(1, pattern)
        elif pattern.__class__ in gradient_types:
            self.choose_pattern(2, pattern)
        elif pattern.__class__ == HatchingPattern:
            self.choose_pattern(3, pattern)
        elif pattern.__class__ == ImageTilePattern:
            self.choose_pattern(4, pattern)
        else:
            self.activate_frame(self.frame_unknown)
            self.var_pattern_type.set(-1)
        self.var_transform.set(transform)

    def init_from_properties(self, properties):
        if properties.HasFill():
            self.init_from_pattern(properties.fill_pattern,
                                   properties.fill_transform)
        else:
            self.choose_pattern(0)

    def pattern_changed(self, *args):
        self.update_sample()

    def update_sample(self):
        if self.active_frame:
            self.sample.SetPattern(self.active_frame.Pattern())
            self.sample.SetCenter(self.active_frame.Center())
            apply(self.sample.SetEditMode, self.active_frame.EditModes())

    def center_changed(self, center):
        if self.active_frame:
            self.active_frame.SetCenter(center)

    def direction_changed(self, dir):
        if self.active_frame:
            self.active_frame.SetDirection(dir)

    def init_from_doc(self):
        self.Update()

    def Update(self):
        if self.document.HasSelection():
            self.init_from_properties(self.document.CurrentProperties())

    def do_apply(self):
        kw = {}
        if self.active_frame:
            kw['fill_pattern'] = self.active_frame.Pattern().Duplicate()
            kw['fill_transform'] = self.var_transform.get()
        else:
            kw['fill_pattern'] = EmptyFillStyle
        self.set_properties(_("Set Fill"), 'fill', kw)

    def set_fill_transform(self):
        self.document.SetProperties(fill_transform = self.var_transform.get())

    def update_from_object_cb(self, obj):
        if obj is not None:
            self.init_from_properties(obj.Properties())

    def DropAt(self, x, y, what, data):
        if what == DROP_COLOR:
            self.init_from_pattern(SolidPattern(data))
