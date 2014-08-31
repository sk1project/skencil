# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2000, 2002, 2004 by Bernhard Herzog
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

import os

from sketchdlg import SketchPanel
from Tkinter import BOTH, LEFT, TOP, X
from Tkinter import Frame, Label, IntVar, StringVar, Radiobutton, Checkbutton
from tkext import UpdatedButton, MyEntry

from view import SketchView
import skapp

from Sketch import _, config
from Sketch.Lib import util
from Sketch.warn import warn_tb, INTERNAL
import Sketch



class PrintPanel(SketchPanel):

    title = _("Print")

    def __init__(self, master, main_window, doc):
        SketchPanel.__init__(self, master, main_window, doc, name = 'printdlg')

    def build_dlg(self):
        top = self.top

        # The preview widget
        self.view = SketchView(top, self.document, width = 200, height = 200,
                               background = 'white')
        self.view.pack(side = TOP, fill = BOTH, expand = 1)

        # PostScript Options
        frame = Frame(top, name = "options")
        frame.pack(side = TOP, fill = X)
        #	EPS
        #self.var_create_eps = IntVar(top)
        #self.var_create_eps.set(1)
        #button = Checkbutton(frame, text = _("Create EPS file"),
        #		      variable = self.var_create_eps)
        #button.pack(side = LEFT, expand = 1, fill = X)
        #	Rotate
        self.var_rotate = IntVar(top)
        self.var_rotate.set(0)
        button = Checkbutton(frame, text = _("Rotate ccw."),
                             variable = self.var_rotate)
        button.pack(side = LEFT, expand = 1, fill = X)
        #    Embed fonts
        self.var_embfnt = IntVar(top)
        self.var_embfnt.set(0)
        button = Checkbutton(frame, text = _("Embed fonts"),
                             variable = self.var_embfnt)
        button.pack(side = LEFT, expand = 1, fill = X)


        # Print Command and Filename
        frame = Frame(top, name = "command")
        frame.pack(side = TOP)
        self.print_dest = StringVar(top)
        button = Radiobutton(frame, text = _("Printer"), value = 'printer',
                             variable = self.print_dest, anchor = 'w')
        button.grid(column = 0,row = 0, sticky = 'ew')
        label = Label(frame, text = _("Command"), anchor = 'e')
        label.grid(column = 1, row = 0, sticky = 'ew')
        self.print_command = StringVar(top)
        self.print_command.set('lpr')
        entry = MyEntry(frame, textvariable = self.print_command)
        entry.grid(column = 2, row = 0, sticky = 'ew')

        button = Radiobutton(frame, text = _("EPS"), value = 'file',
                             variable = self.print_dest, anchor = 'w')
        button.grid(column = 0, row = 1, sticky = 'ew')
        label = Label(frame, text = _("Filename"), anchor = 'e')
        label.grid(column = 1, row = 1, sticky = 'ew')
        self.print_filename = StringVar(top)
        self.print_filename.set('')
        entry = MyEntry(frame, textvariable = self.print_filename)
        entry.grid(column = 2, row = 1, sticky = 'ew')
        button = UpdatedButton(frame, text = _("..."),
                               command = self.get_filename)
        button.grid(column = 3, row = 1, sticky = 'ew')

        frame = Frame(top)
        frame.pack(side = TOP)
        button = UpdatedButton(frame, text = _("Print"),
                               command = self.do_print)
        button.pack(side = LEFT)
        button = UpdatedButton(frame, text = _("Close"),
                               command = self.close_dlg)
        button.pack(side = LEFT)

        # init vars
        self.print_dest.set(config.preferences.print_destination)

    def init_from_doc(self):
        self.view.SetDocument(self.document)
        self.print_filename.set(self.default_filename())

    def get_filename(self):
        app = self.main_window.application
        dir, name = os.path.split(self.print_filename.get())
        if not dir:
            dir = self.document.meta.ps_directory
            if not dir:
                dir = config.preferences.print_dir
        filename = app.GetSaveFilename(title = _("Save As PostScript"),
                                       filetypes = skapp.psfiletypes,
                                       initialdir = dir,
                                       initialfile = name)
        if filename:
            self.print_filename.set(filename)

    def default_filename(self):
        dir = self.document.meta.ps_directory
        if not dir:
            dir = self.document.meta.directory
        if not dir:
            dir = os.getcwd()

        name = self.document.meta.filename
        name, ext = os.path.splitext(name)
        return os.path.join(dir, name + '.ps')


    def do_print(self):
        app = self.main_window.application
        bbox = self.document.BoundingRect(visible = 0, printable = 1)
        if bbox is None:
            app.MessageBox(title = _("Save As PostScript"),
                           message = _("The document doesn't have "
                                       "any printable layers."),
                           icon = "warning")
            return
        try:
            filename = ''
            file = None
            if self.print_dest.get() == 'file':
                # print to file
                filename = self.print_filename.get()
                # use filename as file just in case the user is trying
                # to save into an EPS that is referenced by the
                # document. The psdevice knows how to handle such cases.
                file = filename
                title = os.path.basename(filename)
            else:
                file = os.popen(self.print_command.get(), 'w')
                title = 'sketch'
            try:
                dev = Sketch.PostScriptDevice
                ps_dev = dev(file, as_eps = 1, bounding_box = tuple(bbox),
                             rotate = self.var_rotate.get(),
                             embed_fonts = self.var_embfnt.get(),
                             For = util.get_real_username(),
                             CreationDate = util.current_date(), Title = title,
                             document = self.document)
                self.document.Draw(ps_dev)
                ps_dev.Close()
                if filename:
                    self.document.meta.ps_filename = filename
                    self.document.meta.ps_directory =os.path.split(filename)[0]
            finally:
                # close the file. Check for the close attribute first
                # because file can be either a string or a file object.
                if hasattr(file, "close"):
                    file.close()

        except IOError, value:
            app.MessageBox(title = _("Save As PostScript"),
                           message = _("Cannot save %(filename)s:\n"
                                       "%(message)s") \
                           % {'filename':`os.path.split(filename)[1]`,
                              'message':value[1]},
                           icon = 'warning')
            return
        except:
            warn_tb(INTERNAL, 'printing to %s', file)
