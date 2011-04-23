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
import modes

class AppProxy:

	app = None
	mw = None
	stroke_view_flag = False
	draft_view_flag = False

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

	def save_all(self, *args):
		self.app.save_all()

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
		self.app.current_doc.api.do_undo()

	def redo(self, *args):
		self.app.current_doc.api.do_redo()

	def clear_history(self, *args):
		self.app.current_doc.api.clear_history()

	def cut(self, *args):
		self.app.current_doc.api.cut_selected()

	def copy(self, *args):
		self.app.current_doc.api.copy_selected()

	def paste(self, *args):
		self.app.current_doc.api.paste_selected()

	def delete(self, *args):
		self.app.current_doc.api.delete_selected()

	def select_all(self, *args):
		self.app.current_doc.selection.select_all()

	def deselect(self, *args):
		self.app.current_doc.selection.clear()

	def stroke_view(self, action=None):
		if self.stroke_view_flag:
			self.stroke_view_flag = False
			return
		if not action is None:
			canvas = self.app.current_doc.canvas
			if canvas.stroke_view:
				canvas.stroke_view = False
				canvas.force_redraw()
				if action.menuitem.get_active():
					self.stroke_view_flag = True
					action.menuitem.set_active(False)
			else:
				canvas.stroke_view = True
				canvas.force_redraw()
				if not action.menuitem.get_active():
					self.stroke_view_flag = True
					action.menuitem.set_active(True)

	def draft_view(self, action=None):
		if self.draft_view_flag:
			self.draft_view_flag = False
			return
		if not action is None:
			canvas = self.app.current_doc.canvas
			if canvas.draft_view:
				canvas.draft_view = False
				canvas.force_redraw()
				if action.menuitem.get_active():
					self.draft_view_flag = True
					action.menuitem.set_active(False)
			else:
				canvas.draft_view = True
				canvas.force_redraw()
				if not action.menuitem.get_active():
					self.draft_view_flag = True
					action.menuitem.set_active(True)

	def zoom_in(self, *args):
		self.app.current_doc.canvas.zoom_in()

	def zoom_out(self, *args):
		self.app.current_doc.canvas.zoom_out()

	def fit_zoom_to_page(self, *args):
		self.app.current_doc.canvas.zoom_fit_to_page()

	def zoom_100(self, *args):
		self.app.current_doc.canvas.zoom_100()

	def zoom_selected(self, *args):
		self.app.current_doc.canvas.zoom_selected()

	def force_redraw(self, *args):
		self.app.current_doc.canvas.force_redraw()

	def preferences(self, *args):
		pass

	def about(self, *args):
		dialogs.about_dialog(self.mw)

	#----Canvas modes

	def set_select_mode(self, *args):
		self.app.current_doc.canvas.set_mode(modes.SELECT_MODE)

	def set_shaper_mode(self, *args):
		self.app.current_doc.canvas.set_mode(modes.SHAPER_MODE)

	def set_zoom_mode(self, *args):
		self.app.current_doc.canvas.set_mode(modes.ZOOM_MODE)

	def set_fleur_mode(self, *args):
		self.app.current_doc.canvas.set_mode(modes.FLEUR_MODE)

	def set_line_mode(self, *args):
		self.app.current_doc.canvas.set_mode(modes.LINE_MODE)

	def set_curve_mode(self, *args):
		self.app.current_doc.canvas.set_mode(modes.CURVE_MODE)

	def set_rect_mode(self, *args):
		self.app.current_doc.canvas.set_mode(modes.RECT_MODE)

	def set_ellipse_mode(self, *args):
		self.app.current_doc.canvas.set_mode(modes.ELLIPSE_MODE)

	def set_text_mode(self, *args):
		self.app.current_doc.canvas.set_mode(modes.TEXT_MODE)

	def set_polygon_mode(self, *args):
		self.app.current_doc.canvas.set_mode(modes.POLYGON_MODE)

	def set_zoom_out_mode(self, *args):
		self.app.current_doc.canvas.set_mode(modes.ZOOM_OUT_MODE)

	def set_move_mode(self, *args):
		self.app.current_doc.canvas.set_mode(modes.MOVE_MODE)

	def set_copy_mode(self, *args):
		self.app.current_doc.canvas.set_mode(modes.COPY_MODE)

	#-------

	def fill_selected(self, color):
		if self.app.current_doc is None:
			#FIXME: here should be default style changing
			pass
		else:
			self.app.current_doc.api.fill_selected(color)

	def stroke_selected(self, color):
		if self.app.current_doc is None:
			#FIXME: here should be default style changing
			pass
		else:
			self.app.current_doc.api.stroke_selected(color)
