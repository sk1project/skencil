# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011 by Igor E. Novikov 
#	
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>. 

import operator
from math import floor, ceil

import gtk
import cairo

from uc2.uc_conf import unit_dict
from uc2 import sk1doc

from skencil import _, config

SIZE = 18

tick_lengths = (5, 4, 2, 2)
text_tick = 9

tick_config = {'in': (1.0, (2, 2, 2, 2)),
               'cm': (1.0, (2, 5)),
               'mm': (10.0, (2, 5)),
               'pt': (100.0, (2, 5, 2, 5)),
               }

HFONT = {
	'.': (2, [(0, 0, 0, 0)]),
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

VFONT = {
	'.': (2, [(0, 0, 0, 0), ]),
	',': (2, [(0, 0, 0, 0), ]),
	'-': (4, [(2, 0, 2, 2), ]),
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

SIGN = {
	0: ([1, 1, 10, 16, 10], [1, 15, 9, 15, 11], [1, 8, 2, 8, 16], [1, 7, 3, 9, 3], [0, 2, 16, 14, 4]),
	1: ([1, 3, 2, 3, 16], [1, 2, 3, 4, 3], [1, 1, 14, 16, 14], [1, 15, 13, 15, 15], [0, 5, 12, 15, 2]),
	2: ([1, 3, 2, 3, 16], [1, 2, 15, 4, 15], [1, 1, 4, 16, 4], [1, 15, 3, 15, 5], [0, 3, 4, 13, 14])
}

class RulerCorner(gtk.DrawingArea):

	def __init__(self, docarea):
		gtk.DrawingArea.__init__(self)
		self.docarea = docarea

		self.set_size_request(SIZE, SIZE)
		self.connect('expose_event', self.repaint)

	def repaint(self, *args):
		color = self.get_style().bg[gtk.STATE_ACTIVE]
		r = color.red / 65535.0
		g = color.green / 65535.0
		b = color.blue / 65535.0
		painter = self.window.cairo_create()
		painter.set_antialias(cairo.ANTIALIAS_NONE)
		painter.set_source_rgb(r, g, b)
		painter.set_line_width(1)
		painter.rectangle(-1, -1, SIZE, SIZE)
		painter.stroke()


HORIZONTAL = 0
VERTICAL = 1

class Ruler(gtk.DrawingArea):

	def __init__(self, docarea, orient):
		gtk.DrawingArea.__init__(self)
		self.docarea = docarea
		self.mw = docarea.app.mw
		self.orient = orient
		self.presenter = docarea.presenter
		self.doc = self.presenter.model
		self.viewport = docarea.canvas

		self.origin = self.presenter.model.doc_origin
		self.positions = None
		self.set_range(0.0, 1.0)

		color = self.mw.get_style().bg[gtk.STATE_ACTIVE]
		self.border_color = [color.red / 65535.0,
						color.green / 65535.0,
						color.blue / 65535.0]
		r, g, b = self.border_color

		if self.orient:
			self.set_size_request(SIZE, -1)
			self.grad = cairo.LinearGradient(0, 0, SIZE, 0)
			self.grad.add_color_stop_rgba(0, r, g, b, 0)
			self.grad.add_color_stop_rgba(1, r, g, b, .8)
		else:
			self.set_size_request(-1, SIZE)
			self.grad = cairo.LinearGradient(0, 0, 0, SIZE)
			self.grad.add_color_stop_rgba(0, r, g, b, 0)
			self.grad.add_color_stop_rgba(1, r, g, b, .8)

		self.connect('expose_event', self.repaint)

	def check_config(self, *args):
		if not self.origin == self.presenter.model.doc_origin:
			self.origin = self.presenter.model.doc_origin
			self.queue_draw()
			return
		if args[0][0] == 'ruler_coordinates' or args[0][0] == 'default_unit':
			self.queue_draw()

	def update_ruler(self, *args):
		self.queue_draw()

	def set_range(self, start, pixel_per_pt):
		self.start = start
		self.pixel_per_pt = pixel_per_pt
		self.positions = None

	def get_positions(self):
		self.viewport = self.presenter.canvas
		scale = 1.0
		x = y = 0
		if not self.viewport is None:
			x, y = self.viewport.win_to_doc([0, 0])
			scale = self.viewport.zoom

		w, h = self.presenter.get_page_size()
		if self.origin == sk1doc.DOC_ORIGIN_LL:
			x += w / 2.0
			y += h / 2.0
		elif self.origin == sk1doc.DOC_ORIGIN_LU:
			x += w / 2.0
			y -= h / 2.0

		if self.orient:
			self.set_range(y, scale)
		else:
			self.set_range(x, scale)

		min_text_step = config.ruler_min_text_step
		max_text_step = config.ruler_max_text_step
		min_tick_step = config.ruler_min_tick_step
		x, y, w, h = self.allocation
		if self.orient == HORIZONTAL:
			length = w
			origin = self.start
		else:
			length = h
			origin = self.start - length / self.pixel_per_pt
		unit_name = config.default_unit
		pt_per_unit = unit_dict[unit_name]
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
			pos = round(pos, 5)
			if self.origin == sk1doc.DOC_ORIGIN_LU and self.orient == VERTICAL:
				pos *= -1
			if pos == 0.0:
				pos = 0.0
			texts.append(("%g" % pos, marks[i][-1]))

		self.positions = marks
		self.texts = texts
		return self.positions, self.texts

	def repaint(self, *args):
		ticks, texts = self.get_positions()
		x, y, w, h = self.allocation
		r, g, b = self.border_color
		painter = self.window.cairo_create()
		painter.set_antialias(cairo.ANTIALIAS_NONE)
		painter.set_line_width(1)
		if self.orient:
			painter.set_source(self.grad)
			painter.rectangle(-1, -1, SIZE, h)
			painter.fill ()

			painter.set_source_rgb(r, g, b)
			painter.rectangle(-1, -1, SIZE, h)
			painter.stroke()

			painter.set_source_rgb(0, 0, 0)
			self.draw_vertical(painter)
		else:
			painter.set_source(self.grad)
			painter.rectangle(-1, -1, w , SIZE)
			painter.fill ()

			painter.set_source_rgb(r, g, b)
			painter.rectangle(-1, -1, w , SIZE)
			painter.stroke()

			painter.set_source_rgb(0, 0, 0)
			self.draw_horizontal(painter)


	def draw_vertical(self, painter):
		x, y, width, height = self.allocation

		ticks, texts = self.get_positions()
		for h, pos in ticks:
			pos = height - pos
			painter.move_to(width - h - 1, pos)
			painter.line_to(width, pos)
			painter.stroke()
			pos += 1

		x = 7
		for text, pos in texts:
			pos = height - pos
			pos -= 1
			painter.move_to(width - text_tick - 1, pos + 1)
			painter.line_to(width, pos + 1)
			painter.stroke()

			for character in str(text):
				data = VFONT[character]
				lines = data[1]
				for line in lines:
					painter.move_to(x - line[0], pos - line[1])
					painter.line_to(x - line[2], pos - line[3])
					painter.stroke()
				pos -= data[0]

	def draw_horizontal(self, painter):
		x, y, width, height = self.allocation

		ticks, texts = self.get_positions()
		for h, pos in ticks:
			painter.move_to(pos, height)
			painter.line_to(pos, height - h - 1)
			painter.stroke()
			pos += 1

		y = 7
		for text, pos in texts:
			pos += 1
			painter.move_to(pos - 1 , height)
			painter.line_to(pos - 1, height - text_tick - 1)
			painter.stroke()

			for character in str(text):
				data = HFONT[character]
				lines = data[1]
				for line in lines:
					painter.move_to(line[0] + pos, y - line[1])
					painter.line_to(line[2] + pos, y - line[3])
					painter.stroke()
				pos += data[0]
