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

from copy import deepcopy

from skencil import _, config
from skencil import events
from uc2.sk1doc import model


class PresenterAPI:

	presenter = None
	view = None
	methods = None
	model = None
	app = None
	eventloop = None
	undo = []
	redo = []
	undo_marked = False
	selection = None

	def __init__(self, presenter):
		self.presenter = presenter
		self.selection = presenter.selection
		self.methods = self.presenter.methods
		self.model = presenter.model
		self.view = presenter.canvas

		self.eventloop = presenter.eventloop
		self.app = presenter.app
		self.undo = []
		self.redo = []

	def do_undo(self):
		transaction_list = self.undo[-1][0]
		for transaction in transaction_list:
			self._do_action(transaction)
		tr = self.undo[-1]
		self.undo.remove(tr)
		self.redo.append(tr)
		self.eventloop.emit(self.eventloop.DOC_MODIFIED)
		if self.undo and self.undo[-1][2]:
			self.presenter.reflect_saving()
		if not self.undo and not self.undo_marked:
			self.presenter.reflect_saving()

	def do_redo(self):
		transaction_list = self.redo[-1][1]
		for transaction in transaction_list:
			self._do_action(transaction)
		tr = self.redo[-1]
		self.redo.remove(tr)
		self.undo.append(tr)
		self.eventloop.emit(self.eventloop.DOC_MODIFIED)
		if not self.undo or self.undo[-1][2]:
			self.presenter.reflect_saving()

	def _do_action(self, action):
		if not action: return
		if len(action) == 1:
			action[0]()
		elif len(action) == 2:
			action[0](action[1])
		elif len(action) == 3:
			action[0](action[1], action[2])
		elif len(action) == 4:
			action[0](action[1], action[2], action[3])
		elif len(action) == 5:
			action[0](action[1], action[2], action[3], action[4])
		elif len(action) == 6:
			action[0](action[1], action[2], action[3], action[4], action[5])

	def add_undo(self, transaction):
		self.redo = []
		self.undo.append(transaction)
		self.eventloop.emit(self.eventloop.DOC_MODIFIED)

	def save_mark(self):
		for item in self.undo:
			item[2] = False
		for item in self.redo:
			item[2] = False

		if self.undo:
			self.undo[-1][2] = True
			self.undo_marked = True

	def clear_history(self):
		self.undo = []
		self.redo = []
		events.emit(events.DOC_MODIFIED, self.presenter)

	def set_doc_origin(self, origin):
		cur_origin = self.model.doc_origin
		transaction = [
			[[self.methods.set_doc_origin, cur_origin]],
			[[self.methods.set_doc_origin, origin]],
			False]
		self.methods.set_doc_origin(origin)
		self.add_undo(transaction)

	def _delete_object(self, obj):
		self.methods.delete_object(obj)

	def _insert_object(self, obj, parent, index):
		self.methods.insert_object(obj, parent, index)

	def insert_object(self, obj, parent, index):
		self._insert_object(obj, parent, index)
		transaction = [
			[[self._delete_object, obj]],
			[[self._insert_object, obj, parent, index]],
			False]
		self.add_undo(transaction)

	def _normalize_rect(self, rect):
		x0, y0, x1, y1 = rect
		x0, y0 = self.view.win_to_doc([x0, y0])
		x1, y1 = self.view.win_to_doc([x1, y1])
		new_rect = [0, 0, 0, 0]
		if x0 < x1:
			new_rect[0] = x0
			new_rect[2] = x1 - x0
		else:
			new_rect[0] = x1
			new_rect[2] = x0 - x1
		if y0 < y1:
			new_rect[1] = y0
			new_rect[3] = y1 - y0
		else:
			new_rect[1] = y1
			new_rect[3] = y0 - y1
		return new_rect

	def create_rectangle(self, rect):
		rect = self._normalize_rect(rect)
		parent = self.presenter.active_layer
		obj = model.Rectangle(config, parent, rect)
		style = deepcopy(self.model.styles['Default Style'])
		obj.style = style
		obj.update()
		index = len(parent.childs)
		self.insert_object(obj, parent, index)
		self.selection.set([obj])



