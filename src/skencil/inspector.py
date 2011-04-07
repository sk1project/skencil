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

class DocumentInspector:

	def __init__(self, app):
		self.app = app

	def is_doc(self):
		if self.app.docs:
			return True
		else:
			return False

	def is_not_doc(self):
		if self.app.docs:
			return False
		else:
			return True

	def is_doc_saved(self, doc=None):
		if doc:
			return doc.saved
		elif self.app.current_doc:
			return self.app.current_doc.saved
		else:
			return True

	def is_doc_not_saved(self, doc=None):
		return self.is_doc_saved(doc) != True

	def is_any_doc_not_saved(self):
		result = False
		if self.app.docs:
			for doc in self.app.docs:
				if not doc.saved:
					result = True
					break
		return result

	def is_undo(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		if doc.api.undo:
			return True
		else:
			return False

	def is_redo(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		if doc.api.redo:
			return True
		else:
			return False

	def is_history(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if self.is_undo(doc) or self.is_redo(doc):
			return True
		else:
			return False

	def is_selection(self, doc=None):
		if doc is None:
			doc = self.app.current_doc
		if doc is None:
			return False
		elif doc.selection is None:
			return False
		elif doc.selection.objs:
			return True
		else:
			return False

	def is_clipboard(self):
		if self.app.clipboard.contents:
			return True
		else:
			return False


