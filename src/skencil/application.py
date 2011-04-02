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

from uc2 import cms

from skencil import _, config
from skencil import events
import dialogs
from app_conf import AppData
from proxy import AppProxy
from inspector import DocumentInspector
from mainwindow import MainWindow
from actions import create_actions
from presenter import DocPresenter


class Application:

	appdata = None

	actions = {}
	docs = []
	current_doc = None
	doc_counter = 0

	proxy = None
	inspector = None
	default_cms = None


	def __init__(self, path):
		self.path = path

		self.appdata = AppData()

		self.default_cms = cms.ColorManager(self.stub)
		self.proxy = AppProxy(self)
		self.inspector = DocumentInspector(self)


		self.accelgroup = gtk.AccelGroup()
		self.actiongroup = gtk.ActionGroup('BasicAction')

		self.actions = create_actions(self)
		self.mw = MainWindow(self)
		self.proxy.update_references()

	def run(self):
		events.emit(events.NO_DOCS)
		events.emit(events.APP_STATUS,
				_('To start create new or open existing document'))
		gtk.main()

	def stub(self, *args):
		pass

	def get_new_docname(self):
		self.doc_counter += 1
		return _('Untitled') + ' ' + str(self.doc_counter)

	def set_current_doc(self, doc):
		self.current_doc = doc
		events.emit(events.DOC_CHANGED, doc)

	def exit(self):
		if self.close_all():
			gtk.main_quit()
			return True
		return False

	def new(self):
		doc = DocPresenter(self)
		self.docs.append(doc)
		self.set_current_doc(doc)
		events.emit(events.APP_STATUS, _('New document created'))

	def close(self, doc=None):
		if not self.docs:
			return
		if doc is None:
			doc = self.current_doc
		doc.close()
		self.docs.remove(doc)
		if not self.docs:
			events.emit(events.NO_DOCS)
		return True

	def close_all(self):
		result = True
		if self.docs:
			while self.docs:
				result = self.close(self.docs[0])
				if not result:
					break
		return result

	def open(self):
		doc_file = dialogs.get_open_file_name(self.mw, self,
											config.open_dir)
#		if os.path.lexists(doc_file):
#			try:
#				doc = DocumentPresenter(self, doc_file)
#			except:
#				msg = self.tr('Cannot open file')
#				msg = "<b>%s '%s'</b><br><br>" % (msg, doc_file)
#				s = self.tr('The file may be corrupted or not supported format')
#				QtGui.QMessageBox.warning(self.mw, self.appdata.app_name,
#												msg + s, QtGui.QMessageBox.Ok)
#				return
#			self.docs.append(doc)
#			self.set_current_doc(doc)
#			self.mw.menubar.rebuild_window_menu()
#			self.mw.set_title()
#			self.config.open_dir = os.path.dirname(doc_file)
#			events.emit(events.APP_STATUS, self.tr('Document opened'))

	def save(self):
		pass

	def save_as(self):
		pass

	def insert_doc(self):
		pass


