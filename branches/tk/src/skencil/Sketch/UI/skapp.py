# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2000, 2002, 2003, 2004 by Bernhard Herzog
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307	USA

import sys

from Sketch.warn import pdebug
from Sketch import _, config, plugins, Publisher, gtkutils
import Sketch
from Sketch.Graphics import document

from Sketch.const import CLIPBOARD

from Tkinter import Tk, TclError
import tkext

import tooltips

import skpixmaps
pixmaps = skpixmaps.PixmapTk

#
# meta info defaults
#
meta_defaults = [
    ('fullpathname', None),# the full pathname if read from a file
    ('filename', 'unnamed.sk'),# filename without dir
    ('directory', None),# the directory
    ('backup_created', 0),# true if a backup has been created
    ('format_name', plugins.NativeFormat),# the filetype (do we need this ?)
    ('native_format', 1),# whether the file was in native format
    ('ps_directory', None),# dir where PostScript file was created
    ('ps_filename', ''),# name of last postscript file
    ('compressed', ''),# was compressed (by gzip or bzip2)
    ('compressed_file', ''),# filename of compressed file
    ('load_messages', ''),# (warning) messages
]

for key, val in meta_defaults:
    if not hasattr(document.MetaInfo, key):
        setattr(document.MetaInfo, key, val)

#
#	file type info
#

def openfiletypes():
    types = [(_("Skencil/Sketch Document"), '.sk')]
    for info in plugins.import_plugins:
        types.append(info.tk_file_type)
    types.append((_("All Files"), '*'))
    types = tuple(types)
    return types

def savefiletypes():
    types = [(_("Skencil/Sketch Document"), '.sk')]
    for info in plugins.export_plugins:
        types.append(info.tk_file_type)
    types = tuple(types)
    return types

psfiletypes = (('PostScript', '.ps'),)

imagefiletypes = ((_("All Files"), '*'),
                  (_("Encapsulated PostScript"), ('.eps', '.ps')),
                  (_("JPEG"), 	('.jpg', '.jpeg')),
                  (_("GIF"), 	'.gif'),
                  (_("Portable Bitmap"), 	'.pbm'),
                  (_("Portable Graymap"), 	'.pgm'),
                  (_("Portable Pixmap"), 	'.ppm'),
                  (_("TIFF"), 	('.tif', '.tiff')),
                  (_("Windows / OS/2 Bitmap"), '.bmp'),
                  (_("PCX"), 	'.pcx'))
bitmapfiletypes = imagefiletypes[:1] + imagefiletypes[2:]


#
#	Application classes
#

class TkApplication:

    # these are passed to Tk() and must be redefined by the subclasses:
    tk_basename = ''
    tk_class_name = ''

    def __init__(self, screen_name=None, geometry=None):
        self.init_tk(screen_name, geometry)

    def init_tk(self, screen_name=None, geometry=None):
        self.root = Tk()
#        self.root = Tk(screenName=screen_name,
#                       baseName=self.tk_basename,
#                       className=self.tk_class_name)

        gtkutils.set_ui_fonts(self.root, Sketch.ui_fonts)
        gtkutils.set_ui_colors(self.root, Sketch.ui_colors)

        # Reset locale again to make sure we get properly translated
        # messages if desired by the user. For some reason it may
        # have been reset by Tcl/Tk.
        # if this fails it will already have failed in
        # Sketch/__init__.py which also prints a warning.
        try:
            import locale
        except ImportError:
            pass
        else:
            try:
                locale.setlocale(locale.LC_MESSAGES, "")
            except:
                pass

        if not geometry:
            # try to read geometry from resource database
            geometry = self.root.option_get('geometry', 'Geometry')
        if geometry:
            try:
                self.root.geometry(geometry)
            except TclError:
                sys.stderr.write('%s: invalid geometry specification %s'
                                 % (self.tk_basename, geometry))

    def Mainloop(self):
        self.root.mainloop()

    def MessageBox(self, *args, **kw):
        return apply(tkext.MessageDialog, (self.root,) + args, kw)

    def GetOpenFilename(self, **kwargs):
        return apply(tkext.GetOpenFilename, (self.root,), kwargs)

    def GetSaveFilename(self, **kwargs):
        return apply(tkext.GetSaveFilename, (self.root,), kwargs)

    clipboard = None

    def EmptyClipboard(self):
        self.SetClipboard(None)

    def SetClipboard(self, data):
        self.clipboard = data

    def GetClipboard(self):
        return self.clipboard

    def ClipboardContainsData(self):
        return self.clipboard is not None


class ClipboardWrapper:

    def __init__(self, object):
        self.object = object

    def __del__(self):
        pdebug('__del__', '__del__', self)
        self.object.Destroy()

    def Object(self):
        return self.object


class SketchApplication(TkApplication, Publisher):

    tk_basename = 'sketch'
    tk_class_name = 'Sketch'

    def __init__(self, filename, screen_name=None, geometry=None,
                 run_script=None):
        self.filename = filename
        self.geometry = geometry
        self.run_script = run_script
        TkApplication.__init__(self, screen_name=screen_name,
                               geometry=geometry)
        self.build_window()

    def issue_clipboard(self):
        self.issue(CLIPBOARD)

    def SetClipboard(self, data):
        if data is not None:
            data = ClipboardWrapper(data)
        TkApplication.SetClipboard(self, data)
        self.issue_clipboard()

    def AskUser(self, title, message):
        return self.MessageBox(title=title, message=message,
                               buttons=tkext.YesNo) == tkext.Yes

    def Run(self):
        self.SetClipboard(None)
        tooltips.Init(self.root)
        self.main_window.UpdateCommands()
        # Enter Main Loop
        if self.geometry is None:
            width = self.root.winfo_reqwidth()
            height = self.root.winfo_reqheight()
            if width < 800 : width = 800
            if height < 600 : height = 600
            posx = (self.root.winfo_screenwidth() - width) / 2
            posy = (self.root.winfo_screenheight() - height) / 2
            self.root.geometry('%dx%d%+d%+d' % (width, height, posx, posy))
        self.main_window.Run()

    def Exit(self):
        pixmaps.clear_cache()
        self.root.destroy()

    def init_tk(self, screen_name=None, geometry=None):
        TkApplication.init_tk(self, screen_name=screen_name,
                              geometry=geometry)
        root = self.root
        Sketch.init_modules_from_widget(root)
        root.iconbitmap(pixmaps.Icon)
        root.iconmask(pixmaps.Icon_mask)
        root.iconname('Skencil')
        root.group(root)
        config.add_options(root)

    def build_window(self):
        from mainwindow import SketchMainWindow
        self.main_window = SketchMainWindow(self, self.filename,
                                            self.run_script)

    def SavePreferences(self, *args):
        config.save_user_preferences()

