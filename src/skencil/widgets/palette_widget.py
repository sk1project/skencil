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

import gtk
import cairo

from skencil import events, config
from skencil.resources import cmyk_palette

HEIGHT = 16
SHIFT = 15

class PaletteWidget(gtk.DrawingArea):

	def __init__(self, master):

		gtk.DrawingArea.__init__(self)
		self.master = master
		self.app = master.app
		self.pal = cmyk_palette.palette

		self.set_size_request(-1, HEIGHT)
		self.queue_draw()
		self.position = 0
		self.max_pos = 0
		self.max_position()
		self.add_events(gtk.gdk.BUTTON_PRESS_MASK |
					gtk.gdk.BUTTON_RELEASE_MASK |
              		gtk.gdk.SCROLL_MASK)
		self.connect('expose_event', self.repaint)
		self.connect('button-press-event', self.button_press)
		self.connect('button-release-event', self.button_release)
		self.connect('scroll-event', self.scroll_event)

	def max_position(self):
		x, y, w, h = self.allocation
		if w and h:
			size = float(config.palette_cell_horizontal)
			self.max_pos = len(self.pal) * size / w - 1.0
			self.max_pos *= w / size

	def scroll_event(self, *args):
		event = args[1]
		if event.direction == gtk.gdk.SCROLL_UP:
			self.position += SHIFT
			self.queue_draw()
		if event.direction == gtk.gdk.SCROLL_DOWN:
			self.position -= SHIFT
		if self.position > 0: self.position = 0
		if self.position < -self.max_pos: self.position = -self.max_pos
		self.queue_draw()


	def button_press(self, *args):
		event = args[1]
		offset = config.palette_cell_horizontal
		cell = int(float(event.x) / float(offset) - self.position)
		if event.button == 1:
			self.app.proxy.fill_selected(self.pal[cell])
		if event.button == 3:
			self.app.proxy.stroke_selected(self.pal[cell])

	def button_release(self, *args):
		pass

	def repaint(self, *args):
		self.max_position()
		if self.position < -self.max_pos: self.position = -self.max_pos

		ctx = self.window.cairo_create()
		ctx.set_antialias(cairo.ANTIALIAS_NONE)

		x0 = 0.0; y0 = 2.0
		offset = config.palette_cell_horizontal
		y1 = HEIGHT + 1

		i = self.position
		for color in self.pal:
			x0 = i * config.palette_cell_horizontal
			ctx.rectangle(x0, y0, offset, y1)
			r, g, b = self.app.default_cms.get_cairo_color(color)
			ctx.set_source_rgb(r, g, b)
			ctx.fill()
			ctx.rectangle(x0, y0, offset, y1)
			ctx.set_line_width(1.0)
			ctx.set_source_rgb(0, 0, 0)
			ctx.stroke()
			i += 1





