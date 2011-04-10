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
import gobject

from skencil import modes

ZOOM_IN = 1.25
ZOOM_OUT = 0.8

class AbstractController:

	draw = False
	canvas = None
	start = []
	end = []

	counter = 0
	timer = None
	DELAY = 50

	def __init__(self, canvas, presenter):
		self.canvas = canvas
		self.app = presenter.app
		self.presenter = presenter
		self.eventloop = presenter.eventloop
		self.start = []
		self.end = []

	def mouse_down(self, event):
		if event.button == 1:
			self.draw = True
			self.start = [event.x, event.y]
			self.end = [event.x, event.y]
			self.counter = 0
			self.timer = gobject.timeout_add(self.DELAY, self._draw_frame)

	def mouse_up(self, event):
		if event.button == 1:
			if self.draw:
				gobject.source_remove(self.timer)
				self.draw = False
				self.counter = 0
				self.end = [event.x, event.y]
				self.canvas.renderer.stop_draw_frame(self.start, self.end)
				self.do_action(event)

	def mouse_move(self, event):
		if self.draw:
			self.end = [event.x, event.y]

	def do_action(self, event):
		pass

	def _draw_frame(self, *args):
		if self.end:
			self.canvas.renderer.draw_frame(self.start, self.end)
			self.end = []
		return True


	def wheel(self, event):
		va = self.canvas.mw.v_adj
		dy = va.get_step_increment()
		direction = 1
		if event.direction == gtk.gdk.SCROLL_DOWN:
			direction = -1
		va.set_value(va.get_value() - dy * direction)

class FleurController(AbstractController):

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

class ZoomController(AbstractController):

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def mouse_down(self, event):
		if event.button == 1:
			AbstractController.mouse_down(self, event)
		elif event.button == 3:
			self.start = [event.x, event.y]
			cursor = self.canvas.app.cursors[modes.ZOOM_OUT_MODE]
			self.canvas.set_temp_cursor(cursor)

	def mouse_up(self, event):
		if event.button == 1:
			AbstractController.mouse_up(self, event)
		if event.button == 3:
			if not self.draw:
				self.canvas.zoom_at_point(self.start, ZOOM_OUT)
				self.canvas.restore_cursor()

	def do_action(self, event):
		if self.start and self.end:
			change_x = abs(self.end[0] - self.start[0])
			change_y = abs(self.end[1] - self.start[1])
			if change_x < 5 and change_y < 5:
				self.canvas.zoom_at_point(self.start, ZOOM_IN)
			else:
				self.canvas.zoom_to_rectangle(self.start, self.end)
			self.start = []
			self.end = []

class SelectController(AbstractController):

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)

	def mouse_move(self, event):
		if self.draw:
			AbstractController.mouse_move(self, event)
		else:
			point = [event.x, event.y]
			dpoint = self.canvas.win_to_doc(point)
			if self.presenter.selection.is_point_over(dpoint):
				self.canvas.set_temp_mode(modes.MOVE_MODE)

	def do_action(self, event):
		if self.start and self.end:
			add_flag = False
			if event.state & gtk.gdk.SHIFT_MASK:
				add_flag = True
			change_x = abs(self.end[0] - self.start[0])
			change_y = abs(self.end[1] - self.start[1])
			if change_x < 5 and change_y < 5:
				self.canvas.select_at_point(self.start, add_flag)
			else:
				self.canvas.select_by_rect(self.start, self.end, add_flag)

			dpoint = self.canvas.win_to_doc(self.start)
			if self.presenter.selection.is_point_over(dpoint):
				self.canvas.set_temp_mode(modes.MOVE_MODE)

class MoveController(AbstractController):
	start = None
	end = None

	def __init__(self, canvas, presenter):
		AbstractController.__init__(self, canvas, presenter)
		self.move = False
		self.moved = False
		self.copy = False

	def mouse_down(self, event):
		if event.button == 1:
			self.start = [event.x, event.y]
			self.move = True
			self.canvas.renderer.show_move_frame()
			self.timer = gobject.timeout_add(self.DELAY, self._draw_frame)

	def _draw_frame(self, *args):
		if self.end:
			self.canvas.renderer.draw_move_frame(self.start, self.end)
			self.end = []
		return True

	def mouse_move(self, event):
		if self.move:
			self.moved = True
			new = [event.x, event.y]
			if event.state & gtk.gdk.CONTROL_MASK:
				change = [new[0] - self.start[0], new[1] - self.start[1]]
				if abs(change[0]) > abs(change[1]):
					new[1] = self.start[1]
				else:
					new[0] = self.start[0]
			self.end = new
		else:
			point = [event.x, event.y]
			dpoint = self.canvas.win_to_doc(point)
			if self.presenter.selection.is_point_over(dpoint):
				pass
			else:
				self.canvas.restore_mode()

	def mouse_up(self, event):
		if self.move and event.button == 1:
			gobject.source_remove(self.timer)
			new = [event.x, event.y]
			if event.state & gtk.gdk.CONTROL_MASK:
				change = [new[0] - self.start[0], new[1] - self.start[1]]
				if abs(change[0]) > abs(change[1]):
					new[1] = self.start[1]
				else:
					new[0] = self.start[0]
			self.end = new
			self.canvas.renderer.hide_move_frame()
			self.move = False
			if self.moved:
				start_point = self.canvas.win_to_doc(self.start)
				end_point = self.canvas.win_to_doc(self.end)
				dx = end_point[0] - start_point[0]
				dy = end_point[1] - start_point[1]
				trafo = [1.0, 0.0, 0.0, 1.0, dx, dy]
				self.presenter.api.transform_selected(trafo, self.copy)
			elif event.state & gtk.gdk.SHIFT_MASK:
				self.canvas.select_at_point(self.start, True)
				if not self.presenter.selection.is_point_over(self.start):
					self.canvas.restore_mode()
			if self.copy:
				self.canvas.restore_cursor()
			self.moved = False
			self.copy = False
			self.start = []
			self.end = []

		elif self.moved and event.button == 3:
			self.copy = True
			cursor = self.app.cursors[modes.COPY_MODE]
			self.canvas.set_temp_cursor(cursor)
