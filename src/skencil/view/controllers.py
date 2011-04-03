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

from skencil import modes

class AbstractController:

	draw = False
	canvas = None
	start = []
	end = []

	def __init__(self, canvas, presenter):
		self.canvas = canvas
		self.app = presenter.app
		self.presenter = presenter
		self.eventloop = presenter.eventloop
		self.start = []
		self.end = []

	def mouse_down(self, event):
		pass

	def mouse_up(self, event):
		pass

	def mouse_move(self, event):
		pass

	def wheel(self, event):
		va = self.canvas.mw.v_adj
		dy = va.get_step_increment()
		direction = 1
		if event.direction == gtk.gdk.SCROLL_DOWN:
			direction = -1
		va.set_value(va.get_value() - dy * direction)

class FleurController(AbstractController):

	viewport = None
	counter = 0

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def mouse_down(self, event):
		self.start = [event.x, event.y]
		self.counter = 0

	def mouse_up(self, event):
		if self.start:
			self.end = [event.x, event.y]
			self.counter = 0
			dx = self.end[0] - self.start[0]
			dy = self.end[1] - self.start[1]
			ha = self.canvas.mw.h_adj
			va = self.canvas.mw.v_adj
			zoom = self.canvas.zoom
			ha.set_value(ha.get_value() - dx / zoom)
			va.set_value(va.get_value() - dy / zoom)

			self.start = []
			self.end = []

	def mouse_move(self, event):
		if self.start:
			self.end = [event.x, event.y]
			self.counter += 1
			if self.counter > 5:
				self.counter = 0
				dx = self.end[0] - self.start[0]
				dy = self.end[1] - self.start[1]
				ha = self.canvas.mw.h_adj
				va = self.canvas.mw.v_adj
				zoom = self.canvas.zoom
				ha.set_value(ha.get_value() - dx / zoom)
				va.set_value(va.get_value() - dy / zoom)
				self.start = self.end
