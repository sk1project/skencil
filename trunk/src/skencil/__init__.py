# -*- coding: utf-8 -*-
#
#    Copyright (C) 2011 by Igor E. Novikov
#    
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 3 of the License, or (at your option) any later version.
#    
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the GNU
#    Library General Public License for more details.
#    
#    You should have received a copy of the GNU Library General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os

from app_conf import AppConfig

global config

def dummy_translator(text):
    return text

_ = dummy_translator
config = None


def skencil_run():
    
    """Skencil application launch routine."""
    
    global config
    
    _pkgdir = __path__[0]
    config = AppConfig(_pkgdir)   
    __path__.insert(0, os.path.join(_pkgdir, 'modules'))
    
    from application import Application
    
    app = Application(_pkgdir)
    app.run()
