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

from skencil import _, config
from skencil import events
from app_conf import AppData
from proxy import AppProxy
from inspector import DocumentInspector
from mainwindow import MainWindow
from actions import create_actions
from presenter import DocPresenter 


class Application:
	
	app_data = None
	
	actions = {}
	docs = []
	current_doc = None
	
	proxy = None
	inspector = None
	
	
	def __init__(self, path):
		self.path = path
		
		self.app_data = AppData()
		
		self.proxy = AppProxy(self)
		self.inspector = DocumentInspector(self)
		
		
		self.accelgroup = gtk.AccelGroup()
		self.actiongroup = gtk.ActionGroup('BasicAction')
		
		self.actions = create_actions(self)
		self.mw = MainWindow(self)
		self.proxy.update_references()		
		
	def run(self):
		self.mw.show_all()
		events.emit(events.NO_DOCS)
		events.emit(events.APP_STATUS, 
				_('To start create new or open existing document'))
		gtk.main()		

	def get_new_docname(self):
		self.doc_counter += 1
		return _('Untitled') + ' ' + str(self.doc_counter)

	def set_current_doc(self, doc):
		self.current_doc = doc
		events.emit(events.DOC_CHANGED, doc)
		
	def exit(self):
		gtk.main_quit()
		
	def new(self):
		doc = DocPresenter(self)
		self.docs.append(doc)
		self.set_current_doc(doc)
#		self.mw.set_title()
		events.emit(events.APP_STATUS, _('New document created'))
	
	def open(self):
		pass
	
	def save(self):
		pass
	
	def save_as(self):
		pass
	
	def insert_doc(self):
		pass
	
	
