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

import cairo

class CairoRenderer:

	direct_matrix = None

	canvas = None
	ctx = None
	win_ctx = None
	surface = None
	doc = None

	def __init__(self, canvas):

		self.canvas = canvas
		self.direct_matrix = cairo.Matrix(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

	def draw_frame(self, start, end):
		win_ctx = self.canvas.window.cairo_create()
		surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
								int(self.canvas.width),
								int(self.canvas.height))
		ctx = cairo.Context(surface)
		ctx.set_source_surface(self.surface)
		ctx.paint()
		ctx.set_matrix(self.direct_matrix)
		ctx.set_antialias(cairo.ANTIALIAS_NONE)
		ctx.set_line_width(1.0)
		ctx.set_source_rgb(1, 1, 1)
		ctx.rectangle(start[0], start[1],
					end[0] - start[0], end[1] - start[1])
		ctx.stroke()
		ctx.set_dash([5, 5])
		ctx.set_source_rgb(0, 0, 0)
		ctx.rectangle(start[0], start[1],
					end[0] - start[0], end[1] - start[1])
		ctx.stroke()
		win_ctx.set_source_surface(surface)
		win_ctx.paint()

	def stop_draw_frame(self, start, end):
		ctx = self.canvas.window.cairo_create()
		ctx.set_source_surface(self.surface)
		ctx.paint()

	def paint_document(self):
		self.doc = self.canvas.doc
		self.win_ctx = self.canvas.window.cairo_create()
		self.start()
		self.paint_page_border()
		self.render_doc()
		self.finalize()

	def start(self):
		self.surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
								int(self.canvas.width),
								int(self.canvas.height))
		self.ctx = cairo.Context(self.surface)
		self.ctx.set_source_rgb(1, 1, 1)
		self.ctx.paint()

	def finalize(self):
		self.win_ctx.set_source_surface(self.surface)
		self.win_ctx.paint()

	def paint_page_border(self):
		self.ctx.set_matrix(self.canvas.matrix)
		self.ctx.set_line_width(1.0 / self.canvas.zoom)
		offset = 5.0 / self.canvas.zoom
		w, h = self.canvas.presenter.get_page_size()
		self.ctx.rectangle(-w / 2.0 + offset, -h / 2.0 - offset, w, h)
		self.ctx.set_source_rgb(0.5, 0.5, 0.5)
		self.ctx.fill()
		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		self.ctx.rectangle(-w / 2.0, -h / 2.0, w, h)
		self.ctx.set_source_rgb(1, 1, 1)
		self.ctx.fill()
		self.ctx.rectangle(-w / 2.0, -h / 2.0, w, h)
		self.ctx.set_source_rgb(0, 0, 0)
		self.ctx.stroke()
		self.ctx.rectangle(0, 0, 5, 5)
		self.ctx.stroke()


	def render_doc(self):
		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

	def render_dummy_doc(self):
		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)

		for child in self.canvas.dummy_doc.childs:
			x, y, w, h = child.shape
			r, g, b, a = child.color

			#FILL
			self.ctx.rectangle(x, y, w, h)
			self.ctx.set_source_rgba(r, g, b, a)
			self.ctx.fill()
			#OUTLINE
			self.ctx.set_line_width(1)
			self.ctx.rectangle(x, y, w, h)
			self.ctx.set_source_rgb(0, 0, 0)
			self.ctx.stroke()
