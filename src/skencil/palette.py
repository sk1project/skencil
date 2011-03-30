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

from skencil import config

class Palette(gtk.HBox):

	def __init__(self, mw):
		gtk.HBox.__init__(self)
		self.mw = mw
		self.app = mw.app

		self.dback = PalButton('double-arrow-left.png')
		self.pack_start(self.dback, False, False, 0)
		self.back = PalButton('arrow-left.png')
		self.pack_start(self.back, False, False, 0)

		self.no_color = gtk.EventBox()
		image_dir = os.path.join(config.resource_dir, 'icons', 'palette')
		loader = gtk.gdk.pixbuf_new_from_file
		image = gtk.Image()
		pixbuf = loader(os.path.join(image_dir, 'no-color.png'))
		image.set_from_pixbuf(pixbuf)
		self.no_color.add(image)
		self.pack_start(self.no_color, False, False, 2)

		self.pal_widget = gtk.Frame(label=None)
		self.pal_widget.set_property('shadow_type', gtk.SHADOW_IN)
		self.pal_widget.set_size_request(-1, 18)
		self.pack_start(self.pal_widget, True, True, 0)

		self.forward = PalButton('arrow-right.png')
		self.pack_start(self.forward, False, False, 0)
		self.dforward = PalButton('double-arrow-right.png')
		self.pack_start(self.dforward, False, False, 0)



class PalButton(gtk.Button):
	def __init__(self, file_name):
		gtk.Button.__init__(self)
		self.set_property('relief', gtk.RELIEF_NONE)
		image_dir = os.path.join(config.resource_dir, 'icons', 'palette')
		loader = gtk.gdk.pixbuf_new_from_file
		image = gtk.Image()
		pixbuf = loader(os.path.join(image_dir, file_name))
		image.set_from_pixbuf(pixbuf)
		self.add(image)


