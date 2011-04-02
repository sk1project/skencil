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
from skencil import events
from skencil.events import APP_STATUS, CLIPBOARD, CONFIG_MODIFIED, DOC_CHANGED, \
DOC_CLOSED, DOC_MODIFIED, DOC_SAVED, MODE_CHANGED, NO_DOCS, SELECTION_CHANGED


class AppAction(gtk.Action):

	def __init__(self, name, label, tooltip, icon, shortcut,
				 callable, channels, validator, flag=True):

		gtk.Action.__init__(self, name, label, tooltip, icon)
		self.shortcut = shortcut
		self.callable = callable
		self.events = events
		self.validator = validator

		self.connect('activate', self.callable)

		self.channels = channels
		self.validator = validator

		if channels:
			for channel in channels:
				events.connect(channel, self.receiver)

	def receiver(self, *args):
		self.set_sensitive(self.validator())

def create_actions(app):
	insp = app.inspector
	proxy = app.proxy
	accelgroup = app.accelgroup
	actiongroup = app.actiongroup
	actions = {}
	entries = [
#	name, label, tooltip, icon, shortcut, callable, [channels], validator 
#gtk.accelerator_name(ord('+'),gtk.gdk.CONTROL_MASK)


	['NEW', _('_New'), _('New'), gtk.STOCK_NEW, '<Control>N',
	 proxy.new, None, None],
	['OPEN', _('_Open'), _('Open'), gtk.STOCK_OPEN, '<Control>O',
	 proxy.open, None, None],
	['SAVE', _('_Save'), _('Save'), gtk.STOCK_SAVE, '<Control>S',
	 proxy.save, [NO_DOCS, DOC_CHANGED, DOC_MODIFIED, DOC_SAVED],
	 insp.is_doc_not_saved],
	['SAVE_AS', _('Save _As...'), _('Save As...'), gtk.STOCK_SAVE_AS, None,
	 proxy.save_as, [NO_DOCS, DOC_CHANGED], insp.is_doc],
	['CLOSE', _('_Close'), _('Close'), gtk.STOCK_CLOSE, '<Control>W',
	 proxy.close, [NO_DOCS, DOC_CHANGED], insp.is_doc],
	['CLOSE_ALL', _('_Close All'), _('Close All'), None, None,
	 proxy.close_all, [NO_DOCS, DOC_CHANGED], insp.is_doc],

	['PRINT', _('_Print...'), _('Print'), gtk.STOCK_PRINT, '<Control>P',
	 proxy.do_print, [NO_DOCS, DOC_CHANGED], insp.is_doc],
	['PRINT_SETUP', _('Print Setup...'), _('Print Setup'), gtk.STOCK_PRINT_PREVIEW, None,
	 proxy.do_print_setup, [NO_DOCS, DOC_CHANGED], insp.is_doc],


	['UNDO', _('_Undo'), _('Undo'), gtk.STOCK_UNDO, '<Control>Z',
	 proxy.undo, [events.NO_DOCS, events.DOC_CHANGED, events.DOC_MODIFIED,
	 events.DOC_CLOSED], insp.is_undo],
	['REDO', _('_Redo'), _('Redo'), gtk.STOCK_REDO, '<Control><Shift>Z',
	 proxy.redo, [events.NO_DOCS, events.DOC_CHANGED, events.DOC_MODIFIED,
	 events.DOC_CLOSED], insp.is_redo],
	['CLEAR_HISTORY', _('Clear undo history'), _('Clear undo history'),
	None, None, proxy.clear_history, [events.NO_DOCS, events.DOC_CHANGED,
	 events.DOC_MODIFIED, events.DOC_CLOSED], insp.is_history],


	['CUT', _('Cu_t'), _('Cut'), gtk.STOCK_CUT, '<Control>X',
	 proxy.cut, None, None],
	['COPY', _('_Copy'), _('Copy'), gtk.STOCK_COPY, '<Control>C',
	 proxy.copy, None, None],
	['PASTE', _('_Paste'), _('Paste'), gtk.STOCK_PASTE, '<Control>V',
	 proxy.paste, None, None],
	['DELETE', _('_Delete'), _('Delete'), gtk.STOCK_DELETE, 'Delete',
	 proxy.delete, None, None],


	['ZOOM_IN', _('Zoom in'), _('Zoom in'), gtk.STOCK_ZOOM_IN, '<Control>plus',
	 proxy.zoom_in, [NO_DOCS, DOC_CHANGED], insp.is_doc],
	['ZOOM_OUT', _('Zoom out'), _('Zoom out'), gtk.STOCK_ZOOM_OUT, '<Control>minus',
	 proxy.zoom_out, [NO_DOCS, DOC_CHANGED], insp.is_doc],
	['ZOOM_PAGE', _('Fit zoom to page'), _('Fit zoom to page'), gtk.STOCK_FILE, '<Shift>F4',
	 proxy.fit_zoom_to_page, [NO_DOCS, DOC_CHANGED], insp.is_doc],
	['ZOOM_100', _('Zoom 100%'), _('Zoom 100%'), gtk.STOCK_ZOOM_100, None,
	 proxy.zoom_100, [NO_DOCS, DOC_CHANGED], insp.is_doc],
	['ZOOM_SELECTED', _('Zoom selected'), _('Zoom selected'), gtk.STOCK_ZOOM_FIT, 'F4',
	 proxy.zoom_selected, [NO_DOCS, DOC_CHANGED], insp.is_doc],


	['PREFERENCES', _('Preferences'), _('Preferences'), gtk.STOCK_PREFERENCES, None,
	 proxy.preferences, None, None],
	['QUIT', _('_Exit'), _('Exit'), gtk.STOCK_QUIT, '<Control>Q',
	 proxy.exit, None, None],
	['ABOUT', _('_About Skencil'), _('About Skencil'), gtk.STOCK_ABOUT, None,
	 proxy.about, None, None],
	]

	for entry in entries:
		action = AppAction(entry[0], entry[1], entry[2], entry[3],
						   entry[4], entry[5], entry[6], entry[7])
		actions[entry[0]] = action
		if not action.shortcut is None:
			actiongroup.add_action_with_accel(action, action.shortcut)
			action.set_accel_group(accelgroup)
		else:
			actiongroup.add_action(action)

	return actions
