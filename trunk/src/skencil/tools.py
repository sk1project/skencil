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

class AppTools(gtk.VBox):

	def __init__(self, mw):
		gtk.VBox.__init__(self, False, 0)
		self.mw = mw
		self.app = mw.app
		self.actions = self.app.actions

		icons = ['select.png',
			   'shaper.png',
			   'zoom.png',
			   'create_rect.png',
			   'create_ellipse.png',
			   'create_poly.png',
			   'create_curve.png',
			   'create_text.png'
			   ]

		for icon_file in icons:
			icon_file = os.path.join(config.resource_dir,
									 'icons', 'tools', icon_file)
			icon = gtk.Image()
			icon.set_from_file(icon_file)
			toolbutton = gtk.ToolButton(icon)
			self.pack_start(toolbutton, False, False, 0)


