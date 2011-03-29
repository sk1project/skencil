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
		
		vbox.pack_start(hbox , True, True, 2)	 
		#---CENTRAL PART
		
		self.statusbar = gtk.Statusbar()
		self.statusbar.push(0, _('To start create new or open existing document'))
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
			title = '%s - %s' % (docname, self.app.app_data.app_name)
			self.set_title(title)
		else:
			self.set_title(self.app.app_data.app_name)
		
	def add_doc(self):
#		icon = os.path.join(config.resource_dir, 'app_icon.png')
#		cur = gtk.gdk.Cursor(gtk.gdk.display_get_default(), gtk.gdk.pixbuf_new_from_file(icon), 5, 5)
#		self.window.set_cursor(cur)

		if not self.nb.get_n_pages():
			color = self.get_style().bg[gtk.STATE_NORMAL]
			self.nb_frame.modify_bg(gtk.STATE_NORMAL, color)
		frame = DocArea(self)
		tbox = gtk.Table()
		tbox.attach(frame, 0, 1, 0, 1,
					gtk.EXPAND | gtk.FILL, gtk.EXPAND | gtk.FILL,
					xpadding=2, ypadding=2)
		
		docname = '%s %d' % (_('Untitled'), self.doc_index)
		self.doc_index += 1
		
		tab_label = gtk.Label(' %s  ' % (docname))
		tab_icon = gtk.Image()
		tab_icon.set_from_stock(gtk.STOCK_FILE, gtk.ICON_SIZE_MENU)
		
		
		tab_button = gtk.Frame()
		but_icon = gtk.Image()
		but_icon.set_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)	   
		tab_button.add(but_icon)
		tab_button.set_property('shadow_type', gtk.SHADOW_NONE)
		
		tab_caption = gtk.HBox(False, 0)
		tab_caption.pack_start(tab_icon, False)
		tab_caption.pack_start(tab_label, False)
		tab_caption.pack_start(tab_button, False)
		tab_caption.show_all()
		
		index = self.nb.append_page(tbox, tab_caption)
		self.set_win_title(docname)
		self.nb.show_all()
		self.nb.set_current_page(index)
		
	def close_current_doc(self):
		self.nb.remove_page(self.nb.get_current_page())
		if not self.nb.get_n_pages():
			self.nb_frame.modify_bg(gtk.STATE_NORMAL, self.nodocs_color)
			self.set_win_title()
		
		
#> I use something like this:
#>
#> class NotebookTabLabel(gtk.HBox):
#>	 '''Notebook tab label with close button.
#>	 '''
#>	 def __init__(self, on_close, owner_):
#>		 gtk.HBox.__init__(self, False, 0)
#>		 
#>		 label = self.label = gtk.Label()
#>		 label.set_alignment(0.0, 0.5)
#>		 self.pack_start(label)
#>		 label.show()
#>		 
#>		 close_image = gtk.image_new_from_stock(gtk.STOCK_CLOSE, gtk.ICON_SIZE_MENU)
#>		 image_w, image_h = gtk.icon_size_lookup(gtk.ICON_SIZE_MENU)
#>		 
#>		 close_btn = gtk.Button()
#>		 close_btn.set_relief(gtk.RELIEF_NONE)
#>		 close_btn.connect('clicked', on_close, owner_)
#>		 close_btn.set_size_request(image_w+2, image_h+2)
#>		 close_btn.add(close_image)
#>		 self.pack_start(close_btn, False, False)
#>		 close_btn.show_all()
#>		 
#>		 self.show()
#>
#> tl = NotebookTabLabel(
#>	 lambda *args: self.owner.on_tab_close_doc(*args),
#>	 self )
