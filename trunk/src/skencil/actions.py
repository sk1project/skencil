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
		print 'SIGNAL'
		result = self.validator()
		print result
		self.set_sensitive(result)

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
	 proxy.save, None, None],
	['SAVE_AS', _('Save _As...'), _('Save As...'), gtk.STOCK_SAVE_AS, None,
	 proxy.save_as, None, None], # [NO_DOCS, DOC_CHANGED], insp.is_doc],
	['CLOSE', _('_Close'), _('Close'), gtk.STOCK_CLOSE, '<Control>W',
	 proxy.close, [NO_DOCS], insp.is_doc],
	['CLOSE_ALL', _('_Close All'), _('Close All'), None, None,
	 proxy.close_all, None, None], # [NO_DOCS, DOC_CHANGED], insp.is_doc],

	['PRINT', _('_Print...'), _('Print'), gtk.STOCK_PRINT, '<Control>P',
	 proxy.do_print, None, None],
	['PRINT_SETUP', _('Print Setup...'), _('Print Setup'), gtk.STOCK_PRINT_PREVIEW, None,
	 proxy.do_print_setup, None, None],


	['UNDO', _('_Undo'), _('Undo'), gtk.STOCK_UNDO, '<Control>Z',
	 proxy.undo, None, None],
	['REDO', _('_Redo'), _('Redo'), gtk.STOCK_REDO, '<Control><Shift>Z',
	 proxy.redo, None, None],

	['CUT', _('Cu_t'), _('Cut'), gtk.STOCK_CUT, '<Control>X',
	 proxy.cut, None, None],
	['COPY', _('_Copy'), _('Copy'), gtk.STOCK_COPY, '<Control>C',
	 proxy.copy, None, None],
	['PASTE', _('_Paste'), _('Paste'), gtk.STOCK_PASTE, '<Control>V',
	 proxy.paste, None, None],
	['DELETE', _('_Delete'), _('Delete'), gtk.STOCK_DELETE, 'Delete',
	 proxy.delete, None, None],


	['ZOOM_IN', _('Zoom in'), _('Zoom in'), gtk.STOCK_ZOOM_IN, '<Control>plus',
	 proxy.zoom_in, None, None],
	['ZOOM_OUT', _('Zoom out'), _('Zoom out'), gtk.STOCK_ZOOM_OUT, '<Control>minus',
	 proxy.zoom_out, None, None],
	['ZOOM_PAGE', _('Fit zoom to page'), _('Fit zoom to page'), gtk.STOCK_FILE, '<Shift>F4',
	 proxy.fit_zoom_to_page, None, None],
	['ZOOM_100', _('Zoom 100%'), _('Zoom 100%'), gtk.STOCK_ZOOM_100, None,
	 proxy.zoom_100, None, None],
	['ZOOM_SELECTED', _('Zoom selected'), _('Zoom selected'), gtk.STOCK_ZOOM_FIT, 'F4',
	 proxy.zoom_selected, None, None],


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
