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

from uc2.sk1doc import model

from skencil import config

class CairoRenderer:

	direct_matrix = None

	canvas = None
	ctx = None
	win_ctx = None
	surface = None
	presenter = None
	doc = None

	def __init__(self, canvas):

		self.canvas = canvas
		self.direct_matrix = cairo.Matrix(1.0, 0.0, 0.0, 1.0, 0.0, 0.0)

	#------MARKER RENDERING

	def start_soft_repaint(self):
		self.win_ctx = self.canvas.window.cairo_create()
		self.temp_surface = cairo.ImageSurface(cairo.FORMAT_RGB24,
								int(self.canvas.width),
								int(self.canvas.height))
		self.ctx = cairo.Context(self.temp_surface)
		self.ctx.set_source_surface(self.surface)
		self.ctx.paint()

	def end_soft_repaint(self):
		self.win_ctx.set_source_surface(self.temp_surface)
		self.win_ctx.paint()

	def draw_frame(self, start, end, flag=True):
		self.start_soft_repaint()
		if flag:
			self._paint_selection()

		self.ctx.set_matrix(self.direct_matrix)
		self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
		self.ctx.set_line_width(1.0)
		self.ctx.set_dash([])
		self.ctx.set_source_rgb(1, 1, 1)
		self.ctx.rectangle(start[0], start[1],
					end[0] - start[0], end[1] - start[1])
		self.ctx.stroke()
		self.ctx.set_dash(config.sel_frame_dash)
		r, g, b = config.sel_frame_color
		self.ctx.set_source_rgb(r, g, b)
		self.ctx.rectangle(start[0], start[1],
					end[0] - start[0], end[1] - start[1])
		self.ctx.stroke()

		self.end_soft_repaint()

	def _paint_selection(self):
		selection = self.presenter.selection
		if selection.objs:
			selection.update_markers()
			zoom = self.canvas.zoom
			self.ctx.set_matrix(self.canvas.matrix)
			self.ctx.set_antialias(cairo.ANTIALIAS_NONE)
			x0, y0, x1, y1 = selection.frame
			self.ctx.set_line_width(1.0 / zoom)
			self.ctx.set_dash([])
			self.ctx.set_source_rgb(1, 1, 1)
			self.ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
			self.ctx.stroke()
			r, g, b = config.sel_marker_frame_color
			self.ctx.set_source_rgb(r, g, b)
			a, b = config.sel_marker_frame_dash
			self.ctx.set_dash([a / zoom, b / zoom])
			self.ctx.rectangle(x0, y0, x1 - x0, y1 - y0)
			self.ctx.stroke()

	def	paint_selection(self):
		self.start_soft_repaint()
		self._paint_selection()
		self.end_soft_repaint()

	def stop_draw_frame(self, start, end):
		self.start_soft_repaint()
		self.end_soft_repaint()

	def show_move_frame(self):
		bbox = self.presenter.selection.bbox
		start = self.canvas.doc_to_win(bbox[:2])
		end = self.canvas.doc_to_win(bbox[2:])
		self.draw_frame(start, end, False)

	def draw_move_frame(self, start_point, end_point):
		dx = end_point[0] - start_point[0]
		dy = end_point[1] - start_point[1]
		bbox = self.presenter.selection.bbox
		start = self.canvas.doc_to_win(bbox[:2])
		end = self.canvas.doc_to_win(bbox[2:])
		start = [start[0] + dx, start[1] + dy]
		end = [end[0] + dx, end[1] + dy]
		self.draw_frame(start, end, False)

	def hide_move_frame(self):
		self.start_soft_repaint()
		self._paint_selection()
		self.end_soft_repaint()

	#-------DOCUMENT RENDERING

	def paint_document(self):
		self.doc = self.canvas.doc
		self.presenter = self.canvas.presenter
		self.win_ctx = self.canvas.window.cairo_create()
		self.start()
		self.paint_page_border()
		self.render_doc()
#		self.finalize()
		self.paint_selection()

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


	def render_doc(self):
		self.ctx.set_antialias(cairo.ANTIALIAS_DEFAULT)
		page = self.presenter.active_page
		for layer in page.childs:
			for object in layer.childs:
				self.render_object(object)

	def render_object(self, object):
		if object.cid > model.PRIMITIVE_CLASS:
			self.render_primitives(object)
		else:
			pass
		#FIXME: Here should be groups rendering

	def render_primitives(self, object):
		if object.cache_cpath is None:
			object.update()
		if object.style[0]:
			self.ctx.new_path()
			self.process_fill(object.style)
			self.ctx.append_path(object.cache_cpath)
			self.ctx.fill()
		if object.style[1]:
			self.ctx.new_path()
			self.process_stroke(object.style)
			self.ctx.append_path(object.cache_cpath)
			self.ctx.stroke()

	def process_fill(self, style):
		fill = style[0]
		color = fill[2]
		r, g, b = self.presenter.cms.get_cairo_color(color)
		self.ctx.set_source_rgba(r, g, b, color[2])

	def process_stroke(self, style):
		stroke = style[1]
		#FIXME: add stroke style

		self.ctx.set_line_width(stroke[1])

		color = stroke[2]
		r, g, b = self.presenter.cms.get_cairo_color(color)
		self.ctx.set_source_rgba(r, g, b, color[2])

		self.ctx.set_dash(stroke[3])
		self.ctx.set_line_cap(stroke[4])
		self.ctx.set_line_join(stroke[5])
		self.ctx.set_miter_limit(stroke[6])







