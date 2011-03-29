# -*- coding: utf-8 -*-
#
#    Copyright (C) 2011 by Igor E. Novikov
#    
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#    
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#    
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>. 

import os
import gtk

from skencil import _, config


def about_dialog(parent):
    from credits import CREDITS 
    from license import LICENSE 
    authors = [
        "Igor E. Novikov (Gtk+ version)\n\
        <igor.e.novikov@gmail.com>\n",
        "Bernhard Herzog (Tcl/Tk version)\n\
        <bernhard@users.sourceforge.net>\n",
        ]
        
    about = gtk.AboutDialog()
    about.set_property('window-position', gtk.WIN_POS_CENTER)
    about.set_icon(parent.get_icon())
    
    about.set_program_name(parent.app.app_data.app_name)
    about.set_version(parent.app.app_data.version)
    about.set_copyright("Copyright (C) 2003-2011 by Igor E. Novikov\n" + \
                        "Copyright (C) 1997-2005 by Bernhard Herzog")
    about.set_comments(_("Vector graphics editor based on sK1 0.9.x") + "\n" + \
                          _("and Skencil 0.6.x source code."))
    about.set_website('http://www.sk1project.org')
    logo = os.path.join(config.resource_dir, 'logo.png')
    about.set_logo(gtk.gdk.pixbuf_new_from_file(logo))
    about.set_authors(authors + [CREDITS])
    about.set_license(LICENSE)
    about.run()
    about.destroy()
