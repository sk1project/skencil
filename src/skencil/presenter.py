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

import os
import sys

from uc2.presenter import UCDocPresenter

from skencil import config, events
from widgets.docarea import DocArea

from eventloop import EventLoop
from api import PresenterAPI
from view.selection import Selection

class DocPresenter(UCDocPresenter):

	saved = True

	eventloop = None
	docarea = None
	canvas = None
	selection = None
	traced_objects = None

	def __init__(self, app, doc_file=''):
		UCDocPresenter.__init__(self, config, app.appdata)
		self.app = app
		self.eventloop = EventLoop(self)
		self.selection = Selection(self)


		if doc_file:
			self.load(doc_file)
			self.doc_name = os.path.basename(self.doc_file)
		else:
			self.new()
			self.doc_name = self.app.get_new_docname()

		self.cms = self.app.default_cms

		self.api = PresenterAPI(self)
		self.docarea = DocArea(self.app, self)
		self.canvas = self.docarea.canvas
		self.api.view = self.canvas
		self.app.mw.add_tab(self.docarea)
		self.eventloop.connect(self.eventloop.DOC_MODIFIED, self.modified)
		self.traced_objects = [
							self.eventloop,
							self.api,
							self.docarea.hruler,
							self.docarea.vruler,
							self.docarea.corner,
							self.docarea,
							self.canvas.renderer,
							self.canvas,
							self.selection,
							self
							]

	def close(self):
		if not self.docarea is None:
			self.app.mw.remove_tab(self.docarea)
		UCDocPresenter.close(self)
		for obj in self.traced_objects:
			fields = obj.__dict__
			items = fields.keys()
			for item in items:
				fields[item] = None

	def modified(self, *args):
		self.saved = False
		self.set_title()
		events.emit(events.DOC_MODIFIED, self)

	def reflect_saving(self):
		self.saved = True
		self.set_title()
		self.api.save_mark()
		events.emit(events.DOC_SAVED, self)

	def set_title(self):
		if self.saved:
			title = self.doc_name
		else:
			title = self.doc_name + '*'
		self.app.mw.set_tab_title(self.docarea, title)

	def set_doc_file(self, doc_file, doc_name=''):
		self.doc_file = doc_file
		if doc_name:
			self.doc_name = doc_name
		else:
			self.doc_name = os.path.basename(self.doc_file)
		self.set_title()

	def save(self):
		try:
			if config.make_backup:
				if os.path.lexists(self.doc_file):
					if os.path.lexists(self.doc_file + '~'):
						os.remove(self.doc_file + '~')
					os.rename(self.doc_file, self.doc_file + '~')
			UCDocPresenter.save(self, self.doc_file)
		except IOError:
			errtype, value, traceback = sys.exc_info()
			raise IOError(errtype, value, traceback)
		self.reflect_saving()

