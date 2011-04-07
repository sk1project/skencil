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

from uc2.libcairo import sum_bbox, is_bbox_in_rect

from skencil import _, config
from skencil import events

MARKER_SIZE = 9.0
FRAME_OFFSET = 10.0

class Selection:

	objs = []
	bbox = []
	frame = []
	markers = []

	def __init__(self, presenter):
		self.presenter = presenter
		self.app = presenter.app
		self.objs = []
		self.bbox = []
		self.frame = []
		self.markers = []

	def update(self):
		self.update_bbox()
		eventloop = self.presenter.eventloop
		eventloop.emit(eventloop.SELECTION_CHANGED)
		msg = _('object(s) in selection')
		msg = '%i %s' % (len(self.objs), msg)
		events.emit(events.APP_STATUS, msg)

	def update_bbox(self):
		self.bbox = []
		if self.objs:
			self.bbox += self.objs[0].cache_bbox
			for obj in self.objs:
				self.bbox = sum_bbox(self.bbox, obj.cache_bbox)
		self.update_markers()

	def update_markers(self):
		self.frame = []
		if self.bbox:
			x0, y0, x1, y1 = self.bbox
			size = FRAME_OFFSET / self.presenter.canvas.zoom
			self.frame = [x0 - size, y0 - size, x1 + size, y1 + size]

	def select_by_rect(self, rect):
		result = []
		model = self.presenter.model
		page = self.presenter.active_page
		layers = page.childs + model.childs[1].childs
		for layer in layers:
			for obj in layer.childs:
				if is_bbox_in_rect(rect, obj.cache_bbox):
					result.append(obj)
		self.set(result)

	def select_at_point(self, point):
		result = []
		model = self.presenter.model
		page = self.presenter.active_page
		layers = page.childs + model.childs[1].childs
		layers.reverse()
		rect = point + point
		for layer in layers:
			if result: break
			objs = [] + layer.childs
			objs.reverse()
			for obj in objs:
				if is_bbox_in_rect(obj.cache_bbox, rect):
					result.append(obj)
					break
		if result and result[0] in self.objs:
			self.update()
			return
		self.set(result)


	def remove(self, objs):
		for obj in objs:
			if obj in self.objs:
				self.objs.remove(obj)
		self.update()

	def add(self, objs):
		for obj in objs:
			if obj in self.objs:
				self.objs.remove(obj)
			else:
				self.objs.append(obj)
		self.update()

	def set(self, objs):
		self.objs = objs
		self.update()

	def clear(self):
		self.objs = []
		self.update()
