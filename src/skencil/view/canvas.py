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


from skencil import _, config
from uc2.uc_conf import mm_to_pt, PAGE_FORMATS

PAGEFIT = 0.9
ZOOM_IN = 1.25
ZOOM_OUT = 0.8

WORKSPACE_HEIGHT = 2000 * mm_to_pt
WORKSPACE_WIDTH = 4000 * mm_to_pt

class AppCanvas(gtk.DrawingArea):

	mw = None
	matrix = None
	trafo = []
	zoom = 1.0
	width = 0
	height = 0

	def __init__(self, parent):

		gtk.DrawingArea.__init__(self)
		self.mw = parent
		self.modify_bg(gtk.STATE_NORMAL, gtk.gdk.Color("#ffffff"))


		self.connect('expose_event', self.repaint)
		self.trafo = [1, 0, 0, 1, 0 , 0]
		self.mw.h_adj.connect('value_changed', self.hscroll)
		self.mw.v_adj.connect('value_changed', self.vscroll)
		self.doc = DummyDoc()
		self.my_change = False

	def test(self, *args):
		print self.mw.v_adj.get_value()

	def vscroll(self, *args):
		if self.my_change:
			self.my_change = False
		else:
			m11, m12, m21, m22, dx, dy = self.trafo
			val = self.mw.v_adj.get_value()*m11
			dy = -val
			self.trafo = [m11, m12, m21, m22, dx, dy]
			self.matrix = cairo.Matrix(m11, m12, m21, m22, dx, dy)
			self.force_redraw()

	def hscroll(self, *args):
		m11, m12, m21, m22, dx, dy = self.trafo
		val = self.mw.h_adj.get_value()*m11
		dx = -val
		self.trafo = [m11, m12, m21, m22, dx, dy]
		self.matrix = cairo.Matrix(m11, m12, m21, m22, dx, dy)
		self.force_redraw()

	def update_scrolls(self):
		x, y = self.win_to_doc()

		self.mw.h_adj.set_lower(-WORKSPACE_WIDTH / 2)
		self.mw.h_adj.set_upper(WORKSPACE_WIDTH / 2)
		self.mw.h_adj.set_page_size(WORKSPACE_WIDTH / 10.0)
		self.my_change = True
		self.mw.h_adj.set_value(x)

		self.mw.v_adj.set_lower(-WORKSPACE_HEIGHT / 2)
		self.mw.v_adj.set_upper(WORKSPACE_HEIGHT / 2)
		self.mw.v_adj.set_page_size(WORKSPACE_HEIGHT / 10.0)
		self.my_change = True
		self.mw.v_adj.set_value(-y)

	def _keep_center(self):
		x, y, w, h = self.allocation
		if not w == self.width or not h == self.height:
			_dx = (w - self.width) / 2
			_dy = (h - self.height) / 2
			m11, m12, m21, m22, dx, dy = self.trafo
			dx += _dx
			dy += _dy
			self.trafo = [m11, m12, m21, m22, dx, dy]
			self.matrix = cairo.Matrix(m11, m12, m21, m22, dx, dy)
			self.width = w
			self.height = h
			self.update_scrolls()

	def doc_to_win(self, point=[0.0, 0.0]):
		x, y = point
		m11, m12, m21, m22, dx, dy = self.trafo
		x_new = m11 * x + dx
		y_new = m22 * y + dy
		return [x_new, y_new]

	def win_to_doc(self, point=[0, 0]):
		x, y = point
		m11, m12, m21, m22, dx, dy = self.trafo
		x_new = (x - dx) / m11
		y_new = (y - dy) / m22
		return [x_new, y_new]

	def _fit_to_page(self):
		#FIXME: here should be document page size request 
		width, height = PAGE_FORMATS["A4"]

		x, y, w, h = self.allocation
		self.width = w
		self.height = h
		zoom = min(w / width, h / height) * PAGEFIT
		dx = w / 2.0
		dy = h / 2.0
		self.trafo = [zoom, 0, 0, -zoom, dx, dy]
		self.matrix = cairo.Matrix(zoom, 0, 0, -zoom, dx, dy)
		self.zoom = zoom
		self.update_scrolls()

	def zoom_fit_to_page(self):
		self._fit_to_page()
		self.force_redraw()

	def _zoom(self, dzoom=1.0):
		m11, m12, m21, m22, dx, dy = self.trafo
		m11 *= dzoom
		_dx = (self.width * dzoom - self.width) / 2
		_dy = (self.height * dzoom - self.height) / 2
		dx = dx * dzoom - _dx
		dy = dy * dzoom - _dy
		self.trafo = [m11, m12, m21, -m11, dx, dy]
		self.matrix = cairo.Matrix(m11, m12, m21, -m11, dx, dy)
		self.zoom = m11
		self.update_scrolls()
		self.force_redraw()

	def zoom_in(self):
		self._zoom(ZOOM_IN)

	def zoom_out(self):
		self._zoom(ZOOM_OUT)

	def force_redraw(self):
		self.queue_draw()

	def repaint(self, *args):
		if self.matrix is None:
			self.zoom_fit_to_page()

		self._keep_center()

		painter = self.window.cairo_create()
		painter.set_matrix(self.matrix)

		#FIXME: here should be document redraw
		painter.set_antialias(cairo.ANTIALIAS_NONE)
		painter.set_line_width(1.0 / self.zoom)
		w, h = PAGE_FORMATS["A4"]
		painter.rectangle(-w / 2.0, -h / 2.0, w, h)
		painter.set_source_rgb(0, 0, 0)
		painter.stroke()
		painter.rectangle(0, 0, 5, 5)
		painter.stroke()
		painter.set_antialias(cairo.ANTIALIAS_DEFAULT)

		for child in self.doc.childs:
			x, y, w, h = child.shape
			r, g, b, a = child.color

			#FILL
			painter.rectangle(x, y, w, h)
			painter.set_source_rgba(r, g, b, a)
			painter.fill()
			#OUTLINE
			painter.set_line_width(1)
			painter.rectangle(x, y, w, h)
			painter.set_source_rgb(0, 0, 0)
			painter.stroke()


class DummyDoc:

	childs = []

	def __init__(self):
		self.childs = []
		for i in range(10):
			self.childs.append(DummyRect())

class DummyRect:
	def __init__(self):
		import random
		self.shape = [
		 random.randint(-100, 100), #self.x
		 random.randint(-100, 100), #self.y
		 random.randint(-100, 100), #self.w
		 random.randint(-100, 100)  #self.h
		]
		self.color = [
					random.randint(0, 255) / 255.0, #R
					random.randint(0, 255) / 255.0, #G
					random.randint(0, 255) / 255.0, #B
					random.randint(0, 255) / 255.0  #A
					  ]
