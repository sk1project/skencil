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

from uc2.presenter import UCDocPresenter 

from skencil import config
from eventloop import EventLoop
from widgets.docarea import DocArea 

class DocPresenter(UCDocPresenter):
	
	saved = True
	
	eventloop = None
	docarea = None
	canvas = None
	
	def __init__(self, app, doc_file=''):
		UCDocPresenter.__init__(self, config, app.appdata)
		self.app = app
		self.eventloop = EventLoop(self)


		if doc_file:
			self.load(doc_file)
			self.doc_name = os.path.basename(self.doc_file)
		else:
			self.new()
			self.doc_name = self.app.get_new_docname()

		self.cms = self.app.default_cms
		
		self.docarea = DocArea(self.app, self)
		self.canvas = self.docarea.canvas
		self.app.mw.add_tab(self.docarea)
		
	def close(self):
		if not self.docarea is None:
			self.app.mw.remove_tab(self.docarea)
		UCDocPresenter.close(self)
		
		