# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2001, 2003 by Bernhard Herzog
# Copyright (c) 2010 by Igor E.Novikov
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

from math import floor, ceil, hypot
from string import atoi
from types import TupleType
import operator

import pax

from Sketch import StandardColors, GraphicsDevice, Identity, gtkutils
from Sketch import config, const, GuideLine, Point, ui_colors
from Sketch.warn import warn, USER
from Sketch.const import CHANGED
from Sketch.Graphics.color import XRGBColor

from tkext import PyWidget

from Sketch.Lib import units

HORIZONTAL = 0
VERTICAL = 1

tick_lengths = (8, 5, 3, 2)

# (base_unit_factor, (subdiv1, subdiv2,...))
tick_config = {'in': (1.0, (2, 2, 2, 2)),
               'cm': (1.0, (2, 5)),
               'mm': (10.0, (2, 5)),
               'pt': (100.0, (2, 5, 2, 5)),
               #'pt': (72.0, (2, 3, 12)),
               }

HFONT = {'.': (2, [(0, 0, 0, 0)]),
         ',': (2, [(0, 0, 0, 0)]),
         '-': (4, [(0, 2, 2, 2)]),
         '0': (5, [(0, 0, 3, 0), (3, 0, 3, 4), (3, 4, 0, 4), (0, 4, 0, 0)]),
         '1': (3, [(1, 0, 1, 4), (1, 4, 0, 4)]),
         '2': (5, [(3, 0, 0, 0), (0, 0, 0, 2), (0, 2, 3, 2), (3, 2, 3, 4), (3, 4, 0, 4)]),
         '3': (5, [(0, 0, 3, 0), (0, 2, 3, 2), (0, 4, 3, 4), (3, 4, 3, 0)]),
         '4': (5, [(0, 4, 0, 1), (0, 1, 3, 1), (3, 0, 3, 4)]),
         '5': (5, [(0, 0, 3, 0), (3, 0, 3, 2), (3, 2, 0, 2), (0, 2, 0, 4), (0, 4, 3, 4)]),
         '6': (5, [(2, 4, 0, 4), (0, 4, 0, 0), (0, 0, 3, 0), (3, 0, 3, 2), (3, 2, 0, 2)]),
         '7': (5, [(0, 4, 3, 4), (3, 3, 1, 1), (1, 1, 1, 0)]),
         '8': (5, [(0, 0, 0, 4), (3, 0, 3, 4), (0, 0, 3, 0), (0, 2, 3, 2), (0, 4, 3, 4)]),
         '9': (5, [(1, 0, 3, 0), (3, 0, 3, 4), (3, 4, 0, 4), (0, 4, 0, 2), (0, 2, 3, 2)]),
        }

VFONT = {'.': (2, [(0, 0, 0, 0),]),
         ',': (2, [(0, 0, 0, 0),]),
         '-': (4, [(2, 0, 2, 2),]),
         '0': (5, [(0, 0, 4, 0), (4, 0, 4, 3), (4, 3, 0, 3), (0, 3, 0, 0)]),
         '1': (3, [(0, 1, 4, 1), (4, 1, 4, 0)]),
         '2': (5, [(0, 3, 0, 0), (0, 0, 2, 0), (2, 0, 2, 3), (2, 3, 4, 3), (4, 3, 4, 0)]),
         '3': (5, [(0, 0, 0, 3), (0, 3, 4, 3), (4, 3, 4, 0), (2, 3, 2, 0)]),
         '4': (5, [(4, 0, 1, 0), (1, 0, 1, 3), (4, 3, 0, 3)]),
         '5': (5, [(4, 3, 4, 0), (4, 0, 2, 0), (2, 0, 2, 3), (2, 3, 0, 3), (0, 3, 0, 0)]),
         '6': (5, [(4, 2, 4, 0), (4, 0, 0, 0), (0, 0, 0, 3), (0, 3, 2, 3), (2, 3, 2, 0)]),
         '7': (5, [(4, 0, 4, 3), (3, 3, 1, 1), (1, 1, 0, 1)]),
         '8': (5, [(0, 0, 0, 3), (0, 3, 4, 3), (4, 3, 4, 0), (2, 3, 2, 0), (4, 0, 0, 0)]),
         '9': (5, [(0, 1, 0, 3), (0, 3, 4, 3), (4, 3, 4, 0), (4, 0, 2, 0), (2, 0, 2, 2)]),
        }


class Ruler(PyWidget):

    def __init__(self, master=None, orient = HORIZONTAL, canvas = None, **kw):
        apply(PyWidget.__init__, (self, master), kw)
        self.orient = orient
        self.canvas = canvas
        
        self.gc_initialized = 0
        self.gc = GraphicsDevice()
        self.gc.SetViewportTransform(1.0, Identity, Identity)

        self.positions = None
        self.SetRange(0.0, 1.0, force = 1)

        self['height'] = 19
        self['width'] = 19
        
        self.border_color = XRGBColor(ui_colors.light_border)
        self.bg_color = XRGBColor(ui_colors.menubackground)
        self.fg_color = XRGBColor(ui_colors.fg)
        
        self.gradient = []
        start = ui_colors.menubackground
        stop = ui_colors.light_border
        for pos in range(20):
            color = gtkutils.middle_color(start, stop, pos * 3.5 /100)
            self.gradient.append(XRGBColor(color))
            

        self.bind('<ButtonPress>', self.ButtonPressEvent)
        self.bind('<ButtonRelease>', self.ButtonReleaseEvent)
        self.bind('<Motion>', self.PointerMotionEvent)
        self.button_down = 0
        self.forward_motion = 0

        config.preferences.Subscribe(CHANGED, self.preference_changed)

    def destroy(self):
        PyWidget.destroy(self)
        self.canvas = None

    def MapMethod(self):
        if not self.gc_initialized:
            self.gc.init_gc(self.tkwin)
            self.gc_initialized = 1

    def ResizedMethod(self, width, height):
        self.SetRange(self.start, self.pixel_per_pt, force = 1)

    def SetRange(self, start, pixel_per_pt, force = 0):
        if not force and start==self.start and pixel_per_pt==self.pixel_per_pt:
            return
        self.start = start
        self.pixel_per_pt = pixel_per_pt
        self.positions = None
        self.UpdateWhenIdle()

    def preference_changed(self, pref, value):
        if pref == 'default_unit':
            self.positions = None # force recomputation
            self.UpdateWhenIdle()

    def get_positions(self):
        if self.positions is not None:
            return self.positions, self.texts

        min_text_step = config.preferences.ruler_min_text_step
        max_text_step = config.preferences.ruler_max_text_step
        min_tick_step = config.preferences.ruler_min_tick_step
        if self.orient == HORIZONTAL:
            length = self.tkwin.width
            origin = self.start
        else:
            length = self.tkwin.height
            origin = self.start - length / self.pixel_per_pt
        unit_name = config.preferences.default_unit
        pt_per_unit = units.unit_dict[unit_name]
        units_per_pixel = 1.0 / (pt_per_unit * self.pixel_per_pt)
        factor, subdivisions = tick_config[unit_name]
        subdivisions = (1,) + subdivisions

        factor = factor * pt_per_unit
        start_pos = floor(origin / factor) * factor
        main_tick_step = factor * self.pixel_per_pt
        num_ticks = floor(length / main_tick_step) + 2

        if main_tick_step < min_tick_step:
            tick_step = ceil(min_tick_step / main_tick_step) * main_tick_step
            subdivisions = (1,)
            ticks = 1
        else:
            tick_step = main_tick_step
            ticks = 1
            for depth in range(len(subdivisions)):
                tick_step = tick_step / subdivisions[depth]
                if tick_step < min_tick_step:
                    tick_step = tick_step * subdivisions[depth]
                    depth = depth - 1
                    break
                ticks = ticks * subdivisions[depth]
            subdivisions = subdivisions[:depth + 1]

        positions = range(int(num_ticks * ticks))
        positions = map(operator.mul, [tick_step] * len(positions), positions)
        positions = map(operator.add, positions,
                        [(start_pos - origin) * self.pixel_per_pt]
                        * len(positions))

        stride = ticks
        marks = [None] * len(positions)
        for depth in range(len(subdivisions)):
            stride = stride / subdivisions[depth]
            if depth >= len(tick_lengths):
                height = tick_lengths[-1]
            else:
                height = tick_lengths[depth]
            for i in range(0, len(positions), stride):
                if marks[i] is None:
                    marks[i] = (height, int(round(positions[i])))

        texts = []
        if main_tick_step < min_text_step:
            stride = int(ceil(min_text_step / main_tick_step))
            start_index = stride - (floor(origin / factor) % stride)
            start_index = int(start_index * ticks)
            stride = stride * ticks
        else:
            start_index = 0
            stride = ticks
            step = main_tick_step
            for div in subdivisions:
                step = step / div
                if step < min_text_step:
                    break
                stride = stride / div
                if step < max_text_step:
                    break

        for i in range(start_index, len(positions), stride):
            pos = positions[i] * units_per_pixel + origin / pt_per_unit
            pos = round(pos, 3)
            if pos == 0.0:
                # avoid '-0' strings
                pos = 0.0
            texts.append(("%g" % pos, marks[i][-1]))
        self.positions = marks
        self.texts = texts

        return self.positions, self.texts


    def RedrawMethod(self, region = None):
        if self.orient == HORIZONTAL:
            self.draw_ruler_horizontal()
        else:
            self.draw_ruler_vertical()

    def draw_ruler_horizontal(self):
        DrawLine = self.gc.gc.DrawLine
        height = self.tkwin.height
        width = self.tkwin.width
        
        for pos in range(0,20):
            self.gc.SetFillColor(self.gradient[pos])
            DrawLine(0, pos, width, pos)
        
        self.gc.SetFillColor(self.fg_color)
        ticks, texts = self.get_positions()
        for h, pos in ticks:
            DrawLine(pos, height, pos, height - h - 1)
            pos = pos + 1

        y = 8
        for text, pos in texts:
            pos += 1
            for character in str(text):
                data = HFONT[character]
                lines = data[1]
                for line in lines:
                    DrawLine(line[0] + pos, y - line[1], line[2] + pos, y - line[3])
                pos += data[0]

        self.gc.SetFillColor(self.border_color)
        self.gc.gc.DrawLine(0, 0, 0, height)
        self.gc.gc.DrawLine(0, height - 1, width, height - 1)

    def draw_ruler_vertical(self):
        DrawLine = self.gc.gc.DrawLine
        height = self.tkwin.height
        width = self.tkwin.width

        for pos in range(0,20):
            self.gc.SetFillColor(self.gradient[pos])
            DrawLine(pos, 0, pos, height)

        self.gc.SetFillColor(self.fg_color)
        ticks, texts = self.get_positions()
        for h, pos in ticks:
            pos = height - pos
            DrawLine(width - h - 1, pos, width, pos)
            pos = pos + 1

        x = 8
        for text, pos in texts:
            pos = height - pos
            pos -= 1
            for character in str(text):
                data = VFONT[character]
                lines = data[1]
                for line in lines:
                    DrawLine(x - line[0], pos - line[1], x - line[2], pos - line[3])
                pos -= data[0]
                
        self.gc.SetFillColor(self.border_color)
        DrawLine(0, 0, width, 0)
        DrawLine(width - 1, 0, width - 1, height)

    def ButtonPressEvent(self, event):
        if event.num == const.Button1:
            self.button_down = 1
            self.pressevent = event

    def ButtonReleaseEvent(self, event):
        if event.num == const.Button1:
            self.button_down = 0

    def PointerMotionEvent(self, event):
        if self.button_down:
            if self.canvas is not None:
                press = self.pressevent
                if hypot(press.x - event.x, press.y - event.y) > 3:
                    guide = GuideLine(Point(0, 0), self.orient == HORIZONTAL)
                    self.canvas.PlaceObject(guide)
                    press.x = press.x_root - self.canvas.winfo_rootx()
                    press.y = press.y_root - self.canvas.winfo_rooty()
                    self.canvas.ButtonPressEvent(press)
                    self.canvas.grab_set()
                    self.button_down = 0

    def SetCanvas(self, canvas):
        self.canvas = canvas
