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

from uc2.presenter import UCDocPresenter 

class DocPresenter(UCDocPresenter):
    
    saved = True
    
    eventloop = None
    docarea = None
    canvas = None
    tab = None
    
    def __init__(self, app, doc_file=''):
        UCDocPresenter.__init__(self, config, appdata)
        pass
