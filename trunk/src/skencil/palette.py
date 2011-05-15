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

from skencil import config, _
from skencil.widgets.palette_widget import PaletteWidget

class Palette(gtk.HBox):

	def __init__(self, mw):
		gtk.HBox.__init__(self, False, 0)
		self.mw = mw
		self.app = mw.app

		self.dback = PalButton('double-arrow-left.png')
		self.pack_start(self.dback, False, False, 0)
		self.dback.connect('clicked', self.action_dback)
		self.back = PalButton('arrow-left.png')
		self.pack_start(self.back, False, False, 0)
		self.back.connect('clicked', self.action_back)

		self.no_color = NoColorButton(self)
		self.pack_start(self.no_color, False, False, 0)

		self.palwidget = PaletteWidget(self)
		self.pack_start(self.palwidget, True, True, 1)

		self.forward = PalButton('arrow-right.png')
		self.pack_start(self.forward, False, False, 0)
		self.forward.connect('clicked', self.action_forward)
		self.dforward = PalButton('double-arrow-right.png')
		self.pack_start(self.dforward, False, False, 0)
		self.dforward.connect('clicked', self.action_dforward)


	def action_dforward(self, *args):
		self.palwidget.position -= 20
		if self.palwidget.position < -self.palwidget.max_pos:
			self.palwidget.position = -self.palwidget.max_pos
		self.palwidget.queue_draw()

	def action_forward(self, *args):
		self.palwidget.position -= 1
		if self.palwidget.position < -self.palwidget.max_pos:
			self.palwidget.position = -self.palwidget.max_pos
		self.palwidget.queue_draw()

	def action_back(self, *args):
		self.palwidget.position += 1
		if self.palwidget.position > 0:
			self.palwidget.position = 0
		self.palwidget.queue_draw()

	def action_dback(self, *args):
		self.palwidget.position += 20
		if self.palwidget.position > 0:
			self.palwidget.position = 0
		self.palwidget.queue_draw()



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

class NoColorButton(gtk.EventBox):

	def __init__(self, master):
		gtk.EventBox.__init__(self)
		self.app = master.app
		self.set_size_request(-1, 22)
		image_dir = os.path.join(config.resource_dir, 'icons', 'palette')
		loader = gtk.gdk.pixbuf_new_from_file
		image = gtk.Image()
		pixbuf = loader(os.path.join(image_dir, 'no-color.png'))
		image.set_from_pixbuf(pixbuf)
		self.add(image)
		self.connect('button-press-event', self.button_press)
		self.set_tooltip_markup('<b>' + _('Empthy pattern') + '</b>')

	def button_press(self, *args):
		event = args[1]
		if event.button == 1:
			self.app.proxy.fill_selected([])
		if event.button == 3:
			self.app.proxy.stroke_selected([])

