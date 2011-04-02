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

from uc2.uc_conf import UCConfig
from uc2.utils import system
from uc2.utils.fs import expanduser_unicode

from skencil import events

class AppData():

	app_name = 'Skencil'
	app_proc = 'skencil'
	app_org = 'sK1 Project'
	app_domain = 'sk1project.org'
	app_icon = None
	doc_icon = None
	version = "2.0"

	app_config_dir = expanduser_unicode(os.path.join('~', '.config', 'skencil2'))
	if not os.path.lexists(app_config_dir):
		os.makedirs(app_config_dir)
	app_config = os.path.join(app_config_dir, 'preferences.cfg')


class AppConfig(UCConfig):

	def __setattr__(self, attr, value):
		if not hasattr(self, attr) or getattr(self, attr) != value:
			self.__dict__[attr] = value
			events.emit(events.CONFIG_MODIFIED, attr, value)

	#============== GENERIC SECTION ===================

	#============== UI SECTION ===================
	palette_cell_vertical = 18
	palette_cell_horizontal = 40
	palette_orientation = 1

	# 0 - tabbed 
	# 1 - windowed 
	interface_type = 0

	mw_maximized = 1

	mw_width = 1000
	mw_height = 700

	mw_min_width = 1000
	mw_min_height = 700

	set_doc_icon = 1

	ruler_style = 1
	ruler_min_tick_step = 3
	ruler_min_text_step = 50
	ruler_max_text_step = 100

	# 0 - page center
	# 1 - lower-left page corner
	# 2 - upper-left page corner 
	ruler_coordinates = 1

	# 'pt', 'in', 'cm', 'mm'
	default_unit = 'mm'

	#============== I/O SECTION ===================
	open_dir = '~'
	save_dir = '~'
	import_dir = '~'
	export_dir = '~'
	make_backup = 1

	def __init__(self, path):
		self.resource_dir = os.path.join(path, 'share')




class LinuxConfig(AppConfig):
	os = system.LINUX

class MacosxConfig(AppConfig):
	os = system.MACOSX
	mw_maximized = 0
	set_doc_icon = 0
	ruler_style = 0

class WinConfig(AppConfig):
	os = system.WINDOWS
	ruler_style = 0



def get_app_config(path):
	os_family = system.get_os_family()
	if os_family == system.MACOSX:
		return MacosxConfig(path)
	elif os_family == system.WINDOWS:
		return WinConfig(path)
	else:
		return LinuxConfig(path)
