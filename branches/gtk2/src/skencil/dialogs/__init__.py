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

from uc2.formats import data
from uc2.utils.fs import expanduser_unicode

from skencil import _, config

def _get_open_fiters():
	result = []
	descr = data.FORMAT_DESCRIPTION
	ext = data.FORMAT_EXTENSION
	items = [] + data.LOADER_FORMATS
	for item in items:
		filter = gtk.FileFilter()
		filter.set_name(descr[item])
		filter.add_pattern('*.' + ext[item])
		result.append(filter)

	filter = gtk.FileFilter()
	filter.set_name(_('All supported formats'))
	for item in items:
		filter.add_pattern('*.' + ext[item])
	result.append(filter)

	filter = gtk.FileFilter()
	filter.set_name(_('All files'))
	filter.add_pattern('*')
	result.append(filter)

	return result

def get_open_file_name(parent, app, start_dir):
	result = ''
	dialog = gtk.FileChooserDialog(_('Open file'),
				parent,
				gtk.FILE_CHOOSER_ACTION_OPEN,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
					gtk.STOCK_OPEN, gtk.RESPONSE_OK))

	dialog.set_default_response(gtk.RESPONSE_OK)
	start_dir = expanduser_unicode(start_dir)
	dialog.set_current_folder(start_dir)

	for filter in _get_open_fiters():
		dialog.add_filter(filter)

	ret = dialog.run()
	if not ret == gtk.RESPONSE_CANCEL:
		result = dialog.get_filename()
	dialog.destroy()
	return result

def _get_save_fiters():
	result = []
	descr = data.FORMAT_DESCRIPTION
	ext = data.FORMAT_EXTENSION
	items = [] + data.SAVER_FORMATS
	for item in items:
		filter = gtk.FileFilter()
		filter.set_name(descr[item])
		filter.add_pattern('*.' + ext[item])
		result.append(filter)

	return result

def get_save_file_name(parent, app, path):
	result = ''
	dialog = gtk.FileChooserDialog(_('Save file As...'),
				parent,
				gtk.FILE_CHOOSER_ACTION_SAVE,
				(gtk.STOCK_CANCEL, gtk.RESPONSE_CANCEL,
					gtk.STOCK_SAVE, gtk.RESPONSE_OK))
	dialog.set_do_overwrite_confirmation(True)

	dialog.set_default_response(gtk.RESPONSE_OK)
	path = expanduser_unicode(path)

	doc_folder = os.path.dirname(path)
	dialog.set_current_folder(doc_folder)

	doc_name = os.path.basename(path)
	dialog.set_current_name(doc_name)

	for filter in _get_save_fiters():
		dialog.add_filter(filter)

	ret = dialog.run()
	if not ret == gtk.RESPONSE_CANCEL:
		result = dialog.get_filename()
	dialog.destroy()
	return result

def msg_dialog(parent, title, text, seconary_text='',
			dlg_type=gtk.MESSAGE_ERROR):
	dialog = gtk.MessageDialog(parent,
					flags=gtk.DIALOG_MODAL,
					type=dlg_type,
					buttons=gtk.BUTTONS_OK,
					message_format=text)
	if seconary_text:
		dialog.format_secondary_text(seconary_text)
	dialog.set_title(title)
	dialog.run()
	dialog.destroy()

def warning_dialog(parent, title, text, seconary_text='',
				buttons=[(gtk.STOCK_OK, gtk.RESPONSE_OK)],
				dlg_type=gtk.MESSAGE_WARNING):
	dialog = gtk.MessageDialog(parent,
					flags=gtk.DIALOG_MODAL,
					type=dlg_type,
					message_format=text)
	if seconary_text:
		dialog.format_secondary_text(seconary_text)
	for button in buttons:
		dialog.add_button(button[0], button[1])
	dialog.set_title(title)
	dialog.set_default_response(buttons[-1][1])
	ret = dialog.run()
	dialog.destroy()
	return ret


def about_dialog(parent):
	from credits import CREDITS
	from license import LICENSE
	authors = [
		"\nIgor E. Novikov (Gtk+ version)\n\
		<igor.e.novikov@gmail.com>\n",
		"Bernhard Herzog (Tcl/Tk version)\n\
		<bernhard@users.sourceforge.net>\n",
		]

	about = gtk.AboutDialog()
	about.set_property('window-position', gtk.WIN_POS_CENTER)
	about.set_icon(parent.get_icon())

	about.set_program_name(parent.app.appdata.app_name)
	about.set_version(parent.app.appdata.version)
	about.set_copyright("Copyright (C) 2003-2011 by Igor E. Novikov\n" + \
						"Copyright (C) 1997-2005 by Bernhard Herzog")
	about.set_comments(_("Vector graphics editor based on sK1 0.9.x") + "\n" + \
						  _("and Skencil 0.6.x experience."))
	about.set_website('http://www.sk1project.org')
	logo = os.path.join(config.resource_dir, 'logo.png')
	about.set_logo(gtk.gdk.pixbuf_new_from_file(logo))
	about.set_authors(authors + [CREDITS])
	about.set_license(LICENSE)
	about.run()
	about.destroy()
