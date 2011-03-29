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

from app_conf import get_app_config

global config

def dummy_translator(text):
	return text

_ = dummy_translator
config = None


def skencil_run():

	"""Skencil application launch routine."""

	global config

	_pkgdir = __path__[0]
	config = get_app_config(_pkgdir)
	__path__.insert(0, os.path.join(_pkgdir, 'modules'))

	from application import Application

	app = Application(_pkgdir)
	app.run()
