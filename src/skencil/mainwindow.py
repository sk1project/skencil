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
import gtk

from skencil import _, config
from menubar import AppMenubar
from toolbar import AppToolbar
from tools import AppTools
from palette import Palette
from statusbar import AppStatusbar
from widgets.docarea import DocArea

class MainWindow(gtk.Window):

	canvas = None
	doc_index = 1

	def __init__(self, app):

		gtk.Window.__init__(self)
		self.app = app

		vbox = gtk.VBox(False, 0)

		self.mb = AppMenubar(self)
		vbox.pack_start(self.mb, False, False, 0)

		self.toolbar = AppToolbar(self)
		vbox.pack_start(self.toolbar, False, False, 0)

		#---CENTRAL PART
		hbox = gtk.HBox(False, 0)

		tools = AppTools(self)
		hbox.pack_start(tools, False, False, 0)

		self.nb_frame = gtk.EventBox()
		hbox.pack_start(self.nb_frame, True, True, 2)
		self.nodocs_color = self.get_style().fg[gtk.STATE_INSENSITIVE]
		self.nb_frame.modify_bg(gtk.STATE_NORMAL, self.nodocs_color)

		self.nb = gtk.Notebook()
		self.nb_frame.add(self.nb)
		self.nb.connect('switch-page', self.change_doc)

		vbox.pack_start(hbox , True, True, 2)
		#---CENTRAL PART

		self.statusbar = AppStatusbar(self)
		vbox.pack_end(self.statusbar, expand=False)

		self.palette = Palette(self)
		vbox.pack_end(self.palette, False, False, 0)

		self.add(vbox)
		self.set_win_title()
		self.set_default_size(900, 650)
		self.set_size_request(900, 650)
		self.set_position(gtk.WIN_POS_CENTER)
		self.connect("delete-event", self.app.proxy.exit)
		self.add_accel_group(self.app.accelgroup)
		icon = os.path.join(config.resource_dir, 'app_icon.png')
		self.set_icon_from_file(icon)


	def set_win_title(self, docname=''):
		if docname:
			title = '%s - %s' % (docname, self.app.appdata.app_name)
			self.set_title(title)
		else:
			self.set_title(self.app.appdata.app_name)

	def add_tab(self, da):
		if not self.nb.get_n_pages():
			color = self.get_style().bg[gtk.STATE_NORMAL]
			self.nb_frame.modify_bg(gtk.STATE_NORMAL, color)

		index = self.nb.append_page(da, da.tab_caption)
		da.show_all()
		self.nb.show_all()
		self.nb.set_current_page(index)
		self.set_win_title(da.presenter.doc_name)

	def remove_tab(self, tab):
		self.nb.remove_page(self.nb.page_num(tab))
		if not self.nb.get_n_pages():
			self.nb_frame.modify_bg(gtk.STATE_NORMAL, self.nodocs_color)
			self.set_win_title()
			self.app.current_doc = None

	def change_doc(self, *args):
		da = self.nb.get_nth_page(self.nb.get_current_page())
		self.app.current_doc = da.presenter

	def add_doc(self):
#		icon = os.path.join(config.resource_dir, 'app_icon.png')
#		cur = gtk.gdk.Cursor(gtk.gdk.display_get_default(), gtk.gdk.pixbuf_new_from_file(icon), 5, 5)
#		self.window.set_cursor(cur)
		pass

	def close_current_doc(self):
		self.nb.remove_page(self.nb.get_current_page())
		if not self.nb.get_n_pages():
			self.nb_frame.modify_bg(gtk.STATE_NORMAL, self.nodocs_color)
			self.set_win_title()

