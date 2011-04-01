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

from skencil import _

class AppMenubar(gtk.MenuBar):

	def __init__(self, mw):
		gtk.MenuBar.__init__(self)
		self.mw = mw
		self.app = mw.app
		self.actions = self.app.actions

		#----FILE MENU
		self.file_item, self.file_menu = self.create_menu("_File")
		items = ['NEW',
				 None,
				 'OPEN',
				 'SAVE',
				 'SAVE_AS',
				 'CLOSE',
				 'CLOSE_ALL',
				 None,
				 'PRINT_SETUP',
				 'PRINT',
				 None,
				 'QUIT'
		]
		self.add_items(self.file_menu, items)

		#----EDIT MENU
		self.edit_item, self.edit_menu = self.create_menu("_Edit")
		items = ['UNDO',
				 'REDO',
				 None,
				 'CUT',
				 'COPY',
				 'PASTE',
				 'DELETE',
				 None,
				 'PREFERENCES',
		]
		self.add_items(self.edit_menu, items)

		#----VIEW MENU
		self.view_item, self.view_menu = self.create_menu("_View")

		#----LAYOUT MENU
		self.layout_item, self.effects_menu = self.create_menu("_Layout")

		#----ARRANGE MENU
		self.arrange_item, self.arrange_menu = self.create_menu("_Arrange")

		#----EFFETCS MENU
		self.effects_item, self.effects_menu = self.create_menu("E_ffects")

		#----BITMAPS MENU
		self.bitmaps_item, self.curve_menu = self.create_menu("_Bitmaps")

		#----STYLE MENU
		self.style_item, self.style_menu = self.create_menu("_Style")

		#----SCRIPT MENU
		self.script_item, self.script_menu = self.create_menu("_Script")

		#----WINDOWS MENU
		self.windows_item, self.windows_menu = self.create_menu("_Window")

		#----HELP MENU
		self.help_item, self.help_menu = self.create_menu("_Help")
		items = ['ABOUT',
		]
		self.add_items(self.help_menu, items)

		self.append(self.file_item)
		self.append(self.edit_item)
		self.append(self.view_item)
		self.append(self.layout_item)
		self.append(self.arrange_item)
		self.append(self.effects_item)
		self.append(self.bitmaps_item)
		self.append(self.style_item)
		self.append(self.script_item)
		self.append(self.windows_item)
		self.append(self.help_item)

	def create_menu(self, text):
		menu = gtk.Menu()
		item = gtk.MenuItem(text)
		item.set_submenu(menu)
		return item, menu

	def add_items(self, parent, items):
		for item in items:
			if item is None:
				parent.append(gtk.SeparatorMenuItem())
			else:
				action = self.actions[item]
				menuitem = action.create_menu_item()
				parent.append(menuitem)
