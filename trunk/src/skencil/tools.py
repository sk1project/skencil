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

class AppTools(gtk.Frame):

	def __init__(self, mw):
		gtk.Frame.__init__(self)
		self.mw = mw
		self.app = mw.app
		self.actions = self.app.actions

#		self.set_snap_edge(gtk.POS_TOP | gtk.POS_LEFT)
#		self.set_handle_position(gtk.POS_TOP)
		self.set_property('shadow_type', gtk.SHADOW_NONE)
		self.set_border_width(0)

		self.toolbar = gtk.VBox(False, 0)

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
			self.toolbar.pack_start(toolbutton, False, False, 0)

		x, y, h, w = toolbutton.allocation
		self.add(self.toolbar)


#		self.build()

	def create_entries(self):
		return [
				'ZOOM_IN',
				'ZOOM_OUT',
			   ]

	def build(self):
		entries = self.create_entries()
		index = 0
		for entry in entries:
			if entry is None:
				button = gtk.SeparatorToolItem()
			else:
				action = self.actions[entry]
				button = action.create_tool_item()
			self.insert(button, index)
			index += 1
