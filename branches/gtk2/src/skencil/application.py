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
import gc
import gtk

import uc2
from uc2.utils import system
from uc2 import cms
from uc2 import sk1doc

from skencil import _, config
from skencil import events
import dialogs
import modes
from app_conf import AppData
from proxy import AppProxy
from inspector import DocumentInspector
from mainwindow import MainWindow
from actions import create_actions
from presenter import DocPresenter
from clipboard import AppClipboard


class Application:

	appdata = None

	actions = {}
	docs = []
	current_doc = None
	doc_counter = 0

	proxy = None
	inspector = None
	default_cms = None
	cursors = None


	def __init__(self, path):
		self.path = path

		self.appdata = AppData()
		config.load(self.appdata.app_config)

		self.cursors = modes.get_cursors()
		self.default_cms = cms.ColorManager(self.stub)
		self.proxy = AppProxy(self)
		self.inspector = DocumentInspector(self)
		self.clipboard = AppClipboard(self)


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
			self.update_config()
			config.save(self.appdata.app_config)
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

		if not self.mw.nb.page_num(doc.docarea) == self.mw.nb.get_current_page():
			self.mw.set_active_tab(doc.docarea)

		if self.inspector.is_doc_not_saved(doc):
			first = _("Document '%s' has been modified.") % (doc.doc_name)
			second = _('Do you want to save your changes?')
			ret = dialogs.warning_dialog(self.mw, self.appdata.app_name,
					first, second,
					[(_("Don't save") , gtk.RESPONSE_NO,),
					(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL),
					(gtk.STOCK_SAVE, gtk.RESPONSE_OK)])

			if ret == gtk.RESPONSE_OK:
				if not self.save(): return False
			elif ret == gtk.RESPONSE_NO: pass
			else: return False

		if doc in self.docs:
			self.docs.remove(doc)
			doc.close()
			gc.collect()
			events.emit(events.DOC_CLOSED)
			if not len(self.docs):
				self.current_doc = None
				events.emit(events.NO_DOCS)
				msg = _('To start create new or open existing document')
				events.emit(events.APP_STATUS, msg)
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
		if os.path.lexists(doc_file):
			try:
				doc = DocPresenter(self, doc_file)
			except:
				msg = _('Cannot open file')
				msg = "%s '%s'" % (msg, doc_file)
				sec = _('The file may be corrupted or not supported format')
				dialogs.msg_dialog(self.mw, self.appdata.app_name, msg, sec)
				return
			self.docs.append(doc)
			self.set_current_doc(doc)
			config.open_dir = os.path.dirname(doc_file)
			events.emit(events.APP_STATUS, _('Document opened'))

	def save(self, doc=''):
		if not doc:
			doc = self.current_doc
		if not doc.doc_file:
			return self.save_as()
		ext = os.path.splitext(self.current_doc.doc_file)[1]
		if not ext == sk1doc.DOC_EXTENSION:
			return self.save_as()
		if not os.path.lexists(os.path.dirname(self.current_doc.doc_file)):
			return self.save_as()

		try:
			doc.save()
			events.emit(events.DOC_SAVED, doc)
		except:
			return False
		events.emit(events.APP_STATUS, _('Document saved'))
		return True

	def save_as(self):
		doc_file = '' + self.current_doc.doc_file
		if not doc_file:
			doc_file = '' + self.current_doc.doc_name
		if not os.path.splitext(doc_file)[1] == sk1doc.DOC_EXTENSION:
			doc_file = os.path.splitext(doc_file)[0] + sk1doc.DOC_EXTENSION
		if not os.path.lexists(os.path.dirname(doc_file)):
			doc_file = os.path.join(config.save_dir,
								os.path.basename(doc_file))
		doc_file = dialogs.get_save_file_name(self.mw, self, doc_file)
		if doc_file:
			old_file = self.current_doc.doc_file
			old_name = self.current_doc.doc_name
			self.current_doc.set_doc_file(doc_file)
			try:
				self.current_doc.save()
			except IOError:
				self.current_doc.set_doc_file(old_file, old_name)

				first = _('Cannot save document')
				sec = _('Please check file name and write permissions')
				msg = ("%s '%s'.") % (first, self.current_doc.doc_name)

				dialogs.msg_dialog(self.mw, self.appdata.app_name, msg, sec)

				return False
			config.save_dir = os.path.dirname(doc_file)
			events.emit(events.APP_STATUS, _('Document saved'))
			return True
		else:
			return False

	def save_all(self):
		for doc in [] + self.docs:
			self.save(doc)

	def insert_doc(self):
		pass

	def update_config(self):
		w, h = self.mw.get_size()
		state = self.mw.window.get_state()
		if state == gtk.gdk.WINDOW_STATE_MAXIMIZED:
			if config.os != system.MACOSX:
				config.mw_maximized = 1
		else:
			config.mw_maximized = 0

			config.mw_width = w
			config.mw_height = h

