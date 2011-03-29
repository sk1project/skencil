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

import dialogs

class AppProxy:

	app = None
	mw = None

	def __init__(self, app):
		self.app = app

	def update_references(self):
		self.mw = self.app.mw

	def exit(self, *args):
		self.app.exit()

	def new(self, *args):
		self.app.new()

	def open(self, *args):
		self.app.open()

	def save(self, *args):
		self.app.save()

	def save_as(self, *args):
		self.app.save_as()

	def close(self, *args):
		self.app.close()

	def close_all(self, *args):
		self.app.close_all()

	def insert_doc(self, *args):
		self.app.insert_doc()

	def do_print(self, *args):
		pass

	def do_print_setup(self, *args):
		pass

	def undo(self, *args):
		pass

	def redo(self, *args):
		pass

	def cut(self, *args):
		pass

	def copy(self, *args):
		pass

	def paste(self, *args):
		pass

	def delete(self, *args):
		pass

	def zoom_in(self, *args):
		self.app.current_doc.canvas.zoom_in()

	def zoom_out(self, *args):
		self.app.current_doc.canvas.zoom_out()

	def fit_zoom_to_page(self, *args):
		self.app.current_doc.canvas.zoom_fit_to_page()

	def zoom_100(self, *args):
		pass
	def zoom_selected(self, *args):
		pass

	def preferences(self, *args):
		pass

	def about(self, *args):
		dialogs.about_dialog(self.mw)

