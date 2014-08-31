# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997 -- 2007 by Bernhard Herzog
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

import os, sys, string
from types import TupleType, ListType

from Sketch.Lib import util
from Sketch.warn import warn, warn_tb, INTERNAL, USER
from Sketch import _, config, load, plugins, SketchVersion
from Sketch import Publisher, Point, EmptyFillStyle, EmptyLineStyle, \
     EmptyPattern, Document, GuideLine, PostScriptDevice, SketchError
import Sketch
from Sketch.Graphics import image, eps
import Sketch.Scripting

from Sketch.const import DOCUMENT, CLIPBOARD, CLOSED, COLOR1, COLOR2
from Sketch.const import STATE, VIEW, MODE, SELECTION, POSITION, UNDO, EDITED,\
     CURRENTINFO

from Tkinter import TclVersion, TkVersion, Frame, Scrollbar
from Tkinter import X, BOTTOM, BOTH, TOP, HORIZONTAL, LEFT, Y
import Tkinter
from tkext import AppendMenu, UpdatedLabel, UpdatedButton, CommandButton, \
     CommandCheckbutton, MakeCommand, MultiButton
import tkext

from command import CommandClass, Keymap, Commands

from canvas import SketchCanvas
import ruler
from poslabel import PositionLabel
import palette, tooltips

import skpixmaps
pixmaps = skpixmaps.PixmapTk

import skapp



command_list = []

def AddCmd(name, menu_name, method_name = None, **kw):
    kw['menu_name'] = menu_name
    if not method_name:
        method_name = name
    cmd = apply(CommandClass, (name, method_name), kw)
    command_list.append(cmd)

def AddDocCmd(name, menu_name, method_name = None, **kw):
    kw['menu_name'] = menu_name
    if not method_name:
        method_name = name
    method_name = ('document', method_name)
    for key in CommandClass.callable_attributes:
        if kw.has_key(key):
            value = kw[key]
            if type(value) == type(""):
                kw[key] = ('document', value)
    if not kw.has_key('subscribe_to'):
        kw['subscribe_to'] = SELECTION
    if not kw.has_key('sensitive_cb'):
        kw['sensitive_cb'] = ('document', 'HasSelection')
    cmd = apply(CommandClass, (name, method_name), kw)
    command_list.append(cmd)


class SketchMainWindow(Publisher):

    tk_basename = 'sketch'
    tk_class_name = 'Sketch'

    def __init__(self, application, filename, run_script = None):
        self.application = application
        self.root = application.root # XXX
        self.filename = filename
        self.run_script = run_script
        self.canvas = None
        self.document = None
        self.commands = None
        self.NewDocument()
        self.create_commands()
        self.build_window()
        self.build_menu()
        self.build_toolbar()
        self.build_status_bar()
        self.__init_dlgs()

    def issue_document(self):
        self.issue(DOCUMENT, self.document)

    def create_commands(self):
        cmds = Commands()
        keymap = Keymap()
        for cmd_class in command_list:
            cmd = cmd_class.InstantiateFor(self)
            setattr(cmds, cmd.name, cmd)
            keymap.AddCommand(cmd)
        self.commands = cmds
        self.commands.Update()
        self.keymap = keymap

    def MapKeystroke(self, stroke):
        return self.keymap.MapKeystroke(stroke)

    def save_doc_if_edited(self, title = _("Save Document")):
        if self.document is not None and self.document.WasEdited():
            message = _("%s has been changed.\nDo you want to save it?") \
                    % self.document.meta.filename
            result = self.application.MessageBox(title = title,
                                                 message = message,
                                                 buttons = tkext.YesNoCancel)
            if result == tkext.Yes:
                self.SaveToFileInteractive()
            return result
        return tkext.No

    def Document(self):
        return self.document

    def SetDocument(self, document):
        channels = (SELECTION, UNDO, MODE)
        old_doc = self.document
        if old_doc is not None:
            for channel in channels:
                old_doc.Unsubscribe(channel, self.issue, channel)
        self.document = document
        for channel in channels:
            self.document.Subscribe(channel, self.issue, channel)
        if self.canvas is not None:
            self.canvas.SetDocument(document)
        self.issue_document()
        # issue_document has to be called before old_doc is destroyed,
        # because destroying it causes all connections to be deleted and
        # some dialogs (derived from SketchDlg) try to unsubscribe in
        # response to our DOCUMENT message. The connector currently
        # raises an exception in this case. Perhaps it should silently
        # ignore Unsubscribe() calls with methods that are actually not
        # subscribers (any more)
        if old_doc is not None:
            old_doc.Destroy()
        self.set_window_title()
        if self.commands:
            self.commands.Update()

    AddCmd('NewDocument', _("New"), bitmap = pixmaps.NewDocument)
    def NewDocument(self):
        if self.save_doc_if_edited(_("New Document")) == tkext.Cancel:
            return
        self.SetDocument(Document(create_layer = 1))

    AddCmd('LoadFromFile', _("Open..."), bitmap = pixmaps.Open,
           key_stroke = ('Ctrl+O','C-o'))
    AddCmd('LoadMRU0', '', 'LoadFromFile', args = 0, key_stroke = ('Alt+1','M-1'),
           name_cb = lambda: os.path.split(config.preferences.mru_files[0])[1])
    AddCmd('LoadMRU1', '', 'LoadFromFile', args = 1, key_stroke = ('Alt+2','M-2'),
           name_cb = lambda: os.path.split(config.preferences.mru_files[1])[1])
    AddCmd('LoadMRU2', '', 'LoadFromFile', args = 2, key_stroke = ('Alt+3','M-3'),
           name_cb = lambda: os.path.split(config.preferences.mru_files[2])[1])
    AddCmd('LoadMRU3', '', 'LoadFromFile', args = 3, key_stroke = ('Alt+4','M-4'),
           name_cb = lambda: os.path.split(config.preferences.mru_files[3])[1])
    def LoadFromFile(self, filename = None, directory = None):
        app = self.application
        if self.save_doc_if_edited(_("Open Document")) == tkext.Cancel:
            return
        if type(filename) == type(0):
            filename = config.preferences.mru_files[filename]
        if not filename:
            if not directory:
                directory = self.document.meta.directory
            if not directory:
                directory = os.getcwd()
            name = ''
            filename = app.GetOpenFilename(filetypes = skapp.openfiletypes(),
                                           initialdir = directory,
                                           initialfile = name)
            if not filename:
                return

        try:
            if not os.path.isabs(filename):
                filename = os.path.join(os.getcwd(), filename)
            doc = load.load_drawing(filename)
            self.SetDocument(doc)
            self.add_mru_file(filename)
        except SketchError, value:
            app.MessageBox(title = _("Open"),
                           message = _("An error occurred:\n") + str(value))
            #warn_tb(USER, "An error occurred:\n", str(value))
            self.remove_mru_file(filename)
        else:
            messages = doc.meta.load_messages
            if messages:
                app.MessageBox(title = _("Open"),
                               message=_("Warnings from the import filter:\n")
                               + messages)
            doc.meta.load_messages = ''


    AddCmd('SaveToFile', _("Save"), 'SaveToFileInteractive',
           bitmap = pixmaps.Save, key_stroke = ('Ctrl+S','C-s', 'F2'))
    AddCmd('SaveToFileAs', _("Save As..."), 'SaveToFileInteractive', args = 1,
           key_stroke = ('Ctrl+W','C-w', 'F3'))
    def SaveToFileInteractive(self, use_dialog = 0):
        filename =  self.document.meta.fullpathname
        native_format = self.document.meta.native_format
        compressed_file = self.document.meta.compressed_file
        compressed = self.document.meta.compressed
        app = self.application
        if use_dialog or not filename or not native_format:
            dir = self.document.meta.directory
            if not dir:
                dir = os.getcwd()
            name = self.document.meta.filename
            basename, ext = os.path.splitext(name)
            if not native_format:
                name = basename + '.sk'
            filename = app.GetSaveFilename(filetypes = skapp.savefiletypes(),
                                           initialdir = dir,
                                           initialfile = name)
            if not filename:
                return
            extension = os.path.splitext(filename)[1]
            fileformat = plugins.guess_export_plugin(extension)
            if not fileformat:
                fileformat = plugins.NativeFormat
            compressed_file = '' # guess compression from filename
            compressed = ''
        else:
            fileformat = plugins.NativeFormat
        self.SaveToFile(filename, fileformat, compressed, compressed_file)

    def SaveToFile(self, filename, fileformat = None, compressed = '',
                   compressed_file = ''):
        app = self.application
        try:
            if not self.document.meta.backup_created:
                try:
                    if compressed_file:
                        util.make_backup(compressed_file)
                    else:
                        util.make_backup(filename)
                except util.BackupError, value:
                    backupfile = value.filename
                    strerror = value.strerror
                    msg = (_("Cannot create backup file %(filename)s:\n"
                             "%(message)s\n"
                             "Choose `continue' to try saving anyway,\n"
                             "or `cancel' to cancel.")
                           % {'filename':`backupfile`, 'message':strerror})
                    cancel = _("Cancel")
                    result = app.MessageBox(title = _("Save To File"),
                                            message = msg, icon = 'warning',
                                            buttons = (_("Continue"), cancel))
                    if result == cancel:
                        return

                self.document.meta.backup_created = 1
            if fileformat is None:
                fileformat = plugins.NativeFormat
            try:
                saver = plugins.find_export_plugin(fileformat)
                if compressed:
                    # XXX there should be a plugin interface for this kind
                    # of post-processing
                    if compressed == "gzip":
                        cmd = 'gzip -c -9 > ' + util.sh_quote(compressed_file)
                    elif compressed == "bzip2":
                        cmd = 'bzip2 > ' + util.sh_quote(compressed_file)
                    file = os.popen(cmd, 'w')
                    saver(self.document, filename, file = file)
                else:
                    saver(self.document, filename)
            finally:
                saver.UnloadPlugin()
        except IOError, value:
            if type(value) == type(()):
                value = value[1]
            app.MessageBox(title = _("Save To File"),
                           message = _("Cannot save %(filename)s:\n"
                                       "%(message)s") \
                           % {'filename':`os.path.split(filename)[1]`,
                              'message':value},
                           icon = 'warning')
            self.remove_mru_file(filename)
            return

        if fileformat == plugins.NativeFormat:
            dir, name = os.path.split(filename)
            # XXX should meta.directory be set for non-native formats as well
            self.document.meta.directory = dir
            self.document.meta.filename = name
            self.document.meta.fullpathname = filename
            self.document.meta.file_type = plugins.NativeFormat
            self.document.meta.native_format = 1
        if not compressed_file:
            self.document.meta.compressed_file = ''
            self.document.meta.compressed = ''
        if compressed_file:
            self.add_mru_file(compressed_file)
        else:
            self.add_mru_file(filename)

        self.set_window_title()



    AddCmd('SavePS', _("Save as PostScript..."), key_stroke = ('Alt+P','M-p'))
    def SavePS(self, filename = None):
        app = self.application
        bbox = self.document.BoundingRect(visible = 0, printable = 1)
        if bbox is None:
            app.MessageBox(title = _("Save As PostScript"),
                           message = _("The document doesn't have "
                                       "any printable layers."),
                           icon = "warning")
            return
        if not filename:
            dir = self.document.meta.ps_directory
            if not dir:
                dir = self.document.meta.directory
            if not dir:
                dir = os.getcwd()
            name = self.document.meta.filename
            name, ext = os.path.splitext(name)
            name = name + '.ps'
            filename = app.GetSaveFilename(title = _("Save As PostScript"),
                                           filetypes = skapp.psfiletypes,
                                           initialdir = dir,
                                           initialfile = name)
            if not filename:
                return
        try:
            ps_dev = PostScriptDevice(filename, as_eps = 1,
                                      bounding_box = tuple(bbox),
                                      For = util.get_real_username(),
                                      CreationDate = util.current_date(),
                                      Title = os.path.basename(filename),
                                      document = self.document)
            self.document.Draw(ps_dev)
            ps_dev.Close()
            self.document.meta.ps_directory = os.path.split(filename)[0]
        except IOError, value:
            app.MessageBox(title = _("Save As PostScript"),
                           message = _("Cannot save %(filename)s:\n"
                                       "%(message)s") \
                           % {'filename':`os.path.split(filename)[1]`,
                              'message':value[1]},
                           icon = 'warning')

    def add_mru_file(self, filename):
        if filename:
            config.add_mru_file(filename)
            self.update_mru_files()

    def remove_mru_file(self, filename):
        if filename:
            config.remove_mru_file(filename)
            self.update_mru_files()

    def update_mru_files(self):
        self.commands.LoadMRU0.Update()
        self.commands.LoadMRU1.Update()
        self.commands.LoadMRU2.Update()
        self.commands.LoadMRU3.Update()
        self.file_menu.RebuildMenu()

    AddCmd('InsertFile', _("Insert Document..."))
    def InsertFile(self, filename = None):
        app = self.application
        if not filename:
            dir = self.document.meta.directory
            if not dir:
                dir = os.getcwd()
            name = ''
            filename = app.GetOpenFilename(filetypes = skapp.openfiletypes(),
                                           initialdir = dir,
                                           initialfile = name)
            if not filename:
                return

        try:
            if not os.path.isabs(filename):
                filename = os.path.join(os.getcwd(), filename)
            doc = load.load_drawing(filename)
            group = doc.as_group()
        except SketchError, value:
            app.MessageBox(title = _("Insert Document"),
                           message = _("An error occurred:\n") + str(value))
            #warn_tb(USER, "An error occurred:\n", str(value))
            self.remove_mru_file(filename)
        else:
            messages = doc.meta.load_messages
            if messages:
                app.MessageBox(title = _("Insert Document"),
                               message=_("Warnings from the import filter:\n")
                               + messages)
            doc.meta.load_messages = ''
        #
        if group is not None:
            self.canvas.PlaceObject(group)
        else:
            app.MessageBox(title = _("Insert Document"),
                           message=_("The document is empty"))


    AddCmd('LoadPalette', _("Load Palette..."))
    def LoadPalette(self, filename = None):
        if not filename:
            dir = config.std_res_dir
            if not dir:
                dir = os.getcwd()
            name = ''
            filename = self.application.GetOpenFilename(
                filetypes = palette.file_types,
                initialdir = dir,
                initialfile = name)
            if not filename:
                return

        pal = palette.LoadPalette(filename)
        if not pal:
            self.application.MessageBox(title = _("Load Palette"),
                                        message = _("Cannot load palette %(filename)s")
                                        % {'filename': filename})
        else:
            self.palette.SetPalette(pal)
            # XXX Should we just store the basename if the palette file
            # is located in the resource_dir?
            config.preferences.palette = filename

    def __init_dlgs(self):
        self.dialogs = {}

    def CreateDialog(self, module, dlgname):
        if self.dialogs.has_key(dlgname):
            dialog = self.dialogs[dlgname]
            dialog.deiconify_and_raise()
        else:
            exec "from %s import %s" % (module, dlgname)
            dlgclass = locals()[dlgname]
            dialog = dlgclass(self.root, self, self.document)
            dialog.Subscribe(CLOSED, self.__dlg_closed, dlgname)
            self.dialogs[dlgname] = dialog

    def HideDialogs(self):
        for dialog in self.dialogs.values():
            dialog.withdraw()
    AddCmd('HideDialogs', _("Hide Dialogs"))

    def ShowDialogs(self):
        for dialog in self.dialogs.values():
            dialog.deiconify_and_raise()
    AddCmd('ShowDialogs', _("Show Dialogs"))

    def __dlg_closed(self, dialog, name):
        try:
            del self.dialogs[name]
        except:
            # This might happen if the dialog is buggy...
            warn(INTERNAL, 'dialog %s alread removed from dialog list', name)

    AddCmd('CreateLayerDialog', _("Layers..."),
           'CreateDialog', args = ('layerdlg', 'LayerPanel'),
           key_stroke = 'F5')
    AddCmd('CreateAlignDialog', _("Align..."),
           'CreateDialog', args = ('aligndlg', 'AlignPanel'))
    AddCmd('CreateGridDialog', _("Grid..."),
           'CreateDialog', args = ('griddlg', 'GridPanel'))
    AddCmd('CreateLineStyleDialog', _("Line..."),
           'CreateDialog', args = ('linedlg', 'LinePanel'),
           key_stroke = 'F7')
    AddCmd('CreateFillStyleDialog', _("Fill..."),
           'CreateDialog', args = ('filldlg', 'FillPanel'),
           key_stroke = 'F6')
    AddCmd('CreateFontDialog', _("Font..."),
           'CreateDialog', args = ('fontdlg', 'FontPanel'))
    AddCmd('CreateStyleDialog', _("Styles..."),
           'CreateDialog', args = ('styledlg', 'StylePanel'))
    AddCmd('CreateBlendDialog', _("Blend..."),
           'CreateDialog', args = ('blenddlg', 'BlendPanel'),
           key_stroke = ('Ctrl+B','C-b'))
    AddCmd('CreateLayoutDialog', _("Page Layout..."),
           'CreateDialog', args = ('layoutdlg', 'LayoutPanel'))
    #AddCmd('CreateExportDialog', 'Export...',
#	   'CreateDialog', args = ('export', 'ExportPanel'))
    AddCmd('CreateCurveDialog', _("Curve Commands..."),
           'CreateDialog', args = ('curvedlg', 'CurvePanel'))
    AddCmd('CreateGuideDialog', _("Guide Lines..."),
           'CreateDialog', args = ('guidedlg', 'GuidePanel'))
    AddCmd('CreatePrintDialog', _("Print..."),
           'CreateDialog', args = ('printdlg', 'PrintPanel'),
           key_stroke = ('Ctrl+P', 'C-p'))

    AddCmd('CreateReloadPanel', _("Reload Module..."),
           'CreateDialog', args = ('reloaddlg', 'ReloadPanel'))

    def CreatePluginDialog(self, info):
        if info.HasCustomDialog():
            dialog = info.CreateCustomDialog(self.root, self, self.document)
        else:
            from plugindlg import PluginPanel
            dialog = PluginPanel(self.root, self, self.document, info)
        dialog.Subscribe(CLOSED, self.__dlg_closed, info.class_name)
        self.dialogs[info.class_name] = dialog

    AddCmd('SetOptions', _("Options..."))
    def SetOptions(self):
        import optiondlg
        optiondlg.OptionDialog(self.root, self.canvas)

    def set_window_title(self):
        self.root.client(util.gethostname())
        if self.document:
            appname = config.name
            meta = self.document.meta
            if meta.compressed:
                docname = os.path.split(meta.compressed_file)[1]
                docname = os.path.splitext(docname)[0]
            else:
                docname = self.document.meta.filename
            title = config.preferences.window_title_template % locals()
            command = (config.sketch_command, self.document.meta.fullpathname)
        else:
            title = config.name
            command = (config.sketch_command, )
        self.root.title(title)
        self.root.command(command)

    def UpdateCommands(self):
        self.canvas.UpdateCommands()

    def Run(self):
        #self.root.wait_visibility(self.canvas)
        if self.filename:
            if os.path.isdir(self.filename):
                filename = ''
                directory = self.filename
            else:
                filename = self.filename
                directory = ''
            self.LoadFromFile(filename, directory = directory)
            self.filename = ''
        if self.run_script:
            from Sketch.Scripting.script import Context
            dict = {'context': Context()}
            try:
                execfile(self.run_script, dict)
            except:
                warn_tb(USER, _("Error running script `%s'"), self.run_script)
        self.application.Mainloop()

    AddCmd('Exit', _("Exit"), key_stroke = ('Alt+F4','M-Q', 'M-F4'))
    def Exit(self):
        if self.save_doc_if_edited(_("Exit")) != tkext.Cancel:
            self.commands = None
            self.application.Exit()

    def build_window(self):
        root = self.application.root
        self.mbar = Frame(root, name = 'menubar')
        self.mbar.pack(fill=X)
        
        line = tkext.HSeparator(root)
        line.pack(fill = X)
        
        self.tbar = Frame(root, name = 'toolbar')
        self.tbar.pack(fill = X, pady = 3)
        
        line = tkext.HSeparator(root)
        line.pack(fill = X)
        
        space = Frame(root, height = 3)
        space.pack(fill = X)
        
        self.status_bar = Frame(root, name = 'statusbar')
        self.status_bar.pack(side = BOTTOM, fill=X)

        palette_frame = Frame(root, name = 'palette_frame')
        palette_frame.pack(side = BOTTOM, fill = X, pady = 5)

        frame = Frame(root, name = 'canvas_frame')
        frame.pack(side = TOP, fill = BOTH, expand = 1, padx = 4)
        vbar = Scrollbar(frame)
        vbar.grid(in_ = frame, column = 2, row = 1, sticky = 'ns')
        hbar = Scrollbar(frame, orient = HORIZONTAL)
        hbar.grid(in_ = frame, column = 1, row = 2, sticky = 'ew')
        hrule = ruler.Ruler(root, orient = ruler.HORIZONTAL)
        hrule.grid(in_ = frame, column = 1, row = 0, sticky = 'ew',
                   columnspan = 2)
        vrule = ruler.Ruler(root, orient = ruler.VERTICAL)
        vrule.grid(in_ = frame, column = 0, row = 1, sticky = 'ns',
                   rowspan = 2)
        tmp = Frame(frame, name = 'rulercorner')
        tmp.grid(column = 0, row = 0, sticky = 'news')

        resolution = config.preferences.screen_resolution
        self.canvas = SketchCanvas(root, toplevel = root,
                                   background = 'white', name = 'canvas',
                                   resolution = resolution, main_window = self,
                                   document = self.document)
        self.canvas.grid(in_ = frame, column = 1, row = 1, sticky = 'news')
        self.canvas.focus()
        self.canvas.SetScrollbars(hbar, vbar)
        self.canvas.SetRulers(hrule, vrule)
        hrule.SetCanvas(self.canvas)
        vrule.SetCanvas(self.canvas)
        frame.columnconfigure(0, weight = 0)
        frame.columnconfigure(1, weight = 1)
        frame.columnconfigure(2, weight = 0)
        frame.rowconfigure(0, weight = 0)
        frame.rowconfigure(1, weight = 1)
        frame.rowconfigure(2, weight = 0)
        hbar['command'] = self.canvas._w + ' xview'
        vbar['command'] = self.canvas._w + ' yview'

        # the palette
        button = MultiButton(palette_frame, bitmap = pixmaps.NoPattern,
                             command = self.no_pattern, args = 'fill')
        button.pack(side = LEFT)
        button.Subscribe('COMMAND2', self.no_pattern, 'line')

        pal = palette.GetStandardPalette()

        self.palette = palette.PaletteWidget(palette_frame, pal)
        ScrollXUnits = self.palette.ScrollXUnits
        ScrollXPages = self.palette.ScrollXPages
        CanScrollLeft = self.palette.CanScrollLeft
        CanScrollRight = self.palette.CanScrollRight
        for bitmap, command, args, sensitivecb in [
            (pixmaps.ArrArrLeft, ScrollXPages, -1, CanScrollLeft),
            (pixmaps.ArrLeft, ScrollXUnits, -1, CanScrollLeft),
            (pixmaps.ArrRight, ScrollXUnits, +1, CanScrollRight),
            (pixmaps.ArrArrRight, ScrollXPages, +1, CanScrollRight)]:
            button = UpdatedButton(palette_frame, bitmap = bitmap,
                                   command = command, args = args,
                                   sensitivecb = sensitivecb)
            button.pack(side = LEFT, anchor = 'w')
            self.palette.Subscribe(VIEW, button.Update)
            if bitmap == pixmaps.ArrLeft:
                self.palette.pack(side = LEFT, fill = X, expand = 1, padx = 1)

        self.palette.Subscribe(COLOR1, self.canvas.FillSolid)
        self.palette.Subscribe(COLOR2, self.canvas.LineColor)
        root.protocol('WM_DELETE_WINDOW', tkext.MakeMethodCommand(self.Exit))


    def make_file_menu(self):
        cmds = self.commands
        return map(MakeCommand,
                   [cmds.NewDocument,
                    cmds.LoadFromFile,
                    cmds.SaveToFile,
                    cmds.SaveToFileAs,
                    cmds.SavePS,
                    cmds.CreatePrintDialog,
                    None,
                    cmds.InsertFile,
                    #cmds.CreateExportDialog,
                    None,
                    cmds.SetOptions,
                    cmds.AboutBox,
                    None,
                    cmds.LoadMRU0,
                    cmds.LoadMRU1,
                    cmds.LoadMRU2,
                    cmds.LoadMRU3,
                    None,
                    cmds.Exit])

    def make_edit_menu(self):
        cmds = self.canvas.commands
        return map(MakeCommand,
                   [self.commands.Undo,
                    self.commands.Redo,
                    self.commands.ResetUndo,
                    None,
                    self.commands.CopySelected,
                    self.commands.CutSelected,
                    self.commands.PasteClipboard,
                    self.commands.RemoveSelected,
                    None,
                    self.commands.SelectAll,
                    None,
                    self.commands.DuplicateSelected,
                    None,
                    [(_("Create"), {'auto_rebuild':self.creation_entries}),
                     []],
                    None,
                    cmds.SelectionMode, cmds.EditMode,
                    ])

    def creation_entries(self):
        cmds = self.canvas.commands
        entries = [cmds.CreateRectangle,
                   cmds.CreateEllipse,
                   cmds.CreatePolyBezier,
                   cmds.CreatePolyLine,
                   cmds.CreateSimpleText,
                   self.commands.CreateImage,
                   None]
        items = plugins.object_plugins.items()
        items.sort()
        place = self.place_plugin_object
        dialog = self.CreatePluginDialog
        group = self.create_plugin_group
        for name, plugin in items:
            if plugin.UsesSelection():
                entries.append((plugin.menu_text, group, plugin))
            elif plugin.HasParameters() or plugin.HasCustomDialog():
                entries.append((plugin.menu_text + '...', dialog, plugin))
            else:
                entries.append((plugin.menu_text, place, plugin))
        return map(MakeCommand, entries)

    def place_plugin_object(self, info):
        self.canvas.PlaceObject(info())

    def create_plugin_group(self, info):
        self.document.group_selected(info.menu_text, info.CallFactory)

    def PlaceObject(self, object):
        self.canvas.PlaceObject(object)

    def make_effects_menu(self):
        return map(MakeCommand,
                   [self.commands.FlipHorizontal,
                    self.commands.FlipVertical,
                    None,
                    self.commands.RemoveTransformation,
                    None,
                    self.commands.CreateBlendDialog,
                    self.commands.CancelBlend,
                    None,
                    self.commands.CreateMaskGroup,
                    self.commands.CreatePathText,
                    ])

    def make_curve_menu(self):
        canvas = self.canvas
        cmds = self.canvas.commands.PolyBezierEditor
        return map(MakeCommand,
                   [cmds.ContAngle,
                    cmds.ContSmooth,
                    cmds.ContSymmetrical,
                    cmds.SegmentsToLines,
                    cmds.SegmentsToCurve,
                    cmds.SelectAllNodes,
                    None,
                    cmds.DeleteNodes,
                    cmds.InsertNodes,
                    None,
                    cmds.CloseNodes,
                    cmds.OpenNodes,
                    None,
                    self.commands.CombineBeziers,
                    self.commands.SplitBeziers,
                    None,
                    self.commands.ConvertToCurve])

    def make_view_menu(self):
        def MakeEntry(scale, call = self.canvas.SetScale):
            percent = int(100 * scale)
            return (('%3d%%' % percent), call, scale)
        cmds = self.canvas.commands
        scale = map(MakeEntry, [ 0.125, 0.25, 0.5, 1, 2, 4, 8])
        return map(MakeCommand,
                   [MakeEntry(1),
                    [_("Zoom")] + scale,
                    cmds.ZoomIn,
                    cmds.ZoomOut,
                    cmds.ZoomMode,
                    None,
                    cmds.FitToWindow,
                    cmds.FitSelectedToWindow,
                    cmds.FitPageToWindow,
                    cmds.RestoreViewport,
                    None,
                    cmds.ForceRedraw,
                    None,
                    cmds.ToggleOutlineMode,
                    cmds.TogglePageOutlineMode,
                    None,
                    cmds.ToggleCrosshairs,
                    None,
                    self.commands.LoadPalette
                    ])

    def make_arrange_menu(self):
        commands = [self.commands.CreateAlignDialog,
                    None,
                    self.commands.MoveSelectedToTop,
                    self.commands.MoveSelectedToBottom,
                    self.commands.MoveSelectionUp,
                    self.commands.MoveSelectionDown,
                    None,
                    self.commands.AbutHorizontal,
                    self.commands.AbutVertical,
                    None,
                    self.commands.GroupSelected,
                    self.commands.UngroupSelected,
                    None,
                    self.canvas.commands.ToggleSnapToObjects,
                    self.canvas.commands.ToggleSnapToGrid,
                    self.commands.CreateGridDialog,
                    None,
                    self.canvas.commands.ToggleSnapToGuides,
                    self.commands.AddHorizGuideLine,
                    self.commands.AddVertGuideLine,
                    self.commands.CreateGuideDialog]
        if config.preferences.show_advanced_snap_commands:
            commands.append(None)
            commands.append(self.canvas.commands.ToggleSnapMoveRelative)
            commands.append(self.canvas.commands.ToggleSnapBoundingRect)
        commands = commands + [None,
                               self.commands.CreateLayoutDialog
                               ]
        return map(MakeCommand, commands)

    def make_style_menu(self):
        return map(MakeCommand,
                   [self.commands.FillNone,
                    self.commands.CreateFillStyleDialog,
                    self.canvas.commands.FillSolid,
                    None,
                    self.commands.LineNone,
                    self.commands.CreateLineStyleDialog,
                    None,
                    self.commands.CreateStyleFromSelection,
                    self.commands.CreateStyleDialog,
                    self.commands.UpdateStyle,
                    None,
                    self.commands.CreateFontDialog
                    ])

    def make_window_menu(self):
        cmds = self.commands
        return map(MakeCommand,
                   [cmds.HideDialogs,
                    cmds.ShowDialogs,
                    None,
                    cmds.CreateLayerDialog,
                    cmds.CreateAlignDialog,
                    cmds.CreateGridDialog,
                    None,
                    cmds.CreateLineStyleDialog,
                    cmds.CreateFillStyleDialog,
                    cmds.CreateFontDialog,
                    cmds.CreateStyleDialog,
                    None,
                    cmds.CreateLayoutDialog,
                    None,
                    cmds.CreateBlendDialog,
                    cmds.CreateCurveDialog
                    ])

    def make_special_menu(self):
        cmdlist = [self.commands.python_prompt,
                   self.commands.CreateReloadPanel,
                   self.commands.DocumentInfo,
                   None,
                   self.commands.DumpXImage,
                   self.commands.CreateClone,
                   #self.commands.export_bitmap,
                   ]
        Sketch.Issue(None, Sketch.const.ADD_TO_SPECIAL_MENU, cmdlist)
        return map(MakeCommand, cmdlist)

    def make_script_menu(self):
        tree = Sketch.Scripting.Registry.MenuTree()
        cmdlist = self.convert_menu_tree(tree)
        return map(MakeCommand, cmdlist)


    def convert_menu_tree(self, tree):
        result = []
        for title, item in tree:
            if type(item) == ListType:
                result.append([title] + self.convert_menu_tree(item))
            else:
                result.append((title, item.Execute))
        return result

    def build_menu(self):
        mbar = self.mbar
        self.file_menu = AppendMenu(mbar, _("File"), self.make_file_menu())
        AppendMenu(mbar, _("Edit"), self.make_edit_menu())
        AppendMenu(mbar, _("View"), self.make_view_menu())
        AppendMenu(mbar, _("Arrange"), self.make_arrange_menu())
        AppendMenu(mbar, _("Effects"), self.make_effects_menu())
        AppendMenu(mbar, _("Curve"), self.make_curve_menu())
        AppendMenu(mbar, _("Style"), self.make_style_menu())
        AppendMenu(mbar, _("Script"), self.make_script_menu())
        AppendMenu(mbar, _("Windows"), self.make_window_menu())
        if config.preferences.show_special_menu:
            AppendMenu(mbar, _("Special"), self.make_special_menu())
        self.update_mru_files()
        self.file_menu.RebuildMenu()

    def build_toolbar(self):
        tbar = self.tbar
        canvas = self.canvas

        cmds = [self.commands.NewDocument,
                self.commands.LoadFromFile,
                self.commands.SaveToFile,
                None,
                canvas.commands.EditMode,
                canvas.commands.SelectionMode,
                None,
                self.commands.Undo,
                self.commands.Redo,
                self.commands.RemoveSelected,
                None,
                self.commands.DuplicateSelected,
                self.commands.FlipHorizontal,
                self.commands.FlipVertical,
                None,
                self.commands.MoveSelectedToTop,
                self.commands.MoveSelectionUp,
                self.commands.MoveSelectionDown,
                self.commands.MoveSelectedToBottom,
                None,
                self.commands.GroupSelected,
                self.commands.UngroupSelected,
                None,
                canvas.commands.ZoomMode,
                canvas.commands.ToggleSnapToGrid,
                None,
                canvas.commands.CreateRectangle,
                canvas.commands.CreateEllipse,
                canvas.commands.CreatePolyBezier,
                canvas.commands.CreatePolyLine,
                canvas.commands.CreateSimpleText,
                self.commands.CreateImage,
                ]

        buttons = []
        for cmd in cmds:
            if cmd is None:
#                b = Frame(tbar, class_ = 'TBSeparator')
                b = tkext.VSeparator(tbar)
                b.pack(side = LEFT, fill = Y, pady = 3, padx = 2)
            else:
                if cmd.is_check:
                    b = CommandCheckbutton(tbar, cmd,
                                           highlightthickness = 0,
                                           takefocus = 0)
                else:
                    b = CommandButton(tbar, cmd, highlightthickness = 0,
                                      takefocus = 0)
                tooltips.AddDescription(b, cmd.menu_name)
                b.pack(side = LEFT, fill = Y)

        def state_changed(buttons = buttons):
            for button in buttons:
                button.Update()

        canvas.Subscribe(STATE, state_changed)

    def build_status_bar(self):
        status_bar = self.status_bar
        canvas = self.canvas
        stat_mode = UpdatedLabel(status_bar, name = 'mode', text = '',
                                 updatecb = canvas.ModeInfoText)
        stat_mode.pack(side = 'left', padx = 2)
        stat_mode.Update()
        canvas.Subscribe(MODE, stat_mode.Update)

        stat_edited = UpdatedLabel(status_bar, name = 'edited', text = '',
                                   updatecb = self.EditedInfoText)
        stat_edited.pack(side = 'left', padx = 2)
        stat_edited.Update()
        self.Subscribe(UNDO, stat_edited.Update)

        stat_zoom = UpdatedLabel(status_bar, name = 'zoom', text = '',
                                 updatecb = canvas.ZoomInfoText)
        stat_zoom.pack(side = 'left', padx = 2)
        stat_zoom.Update()
        canvas.Subscribe(VIEW, stat_zoom.Update)

        stat_pos = PositionLabel(status_bar, name = 'position', text = '',
                                 updatecb = canvas.GetCurrentPos)
        stat_pos.pack(side = 'left', padx = 2)
        stat_pos.Update()
        canvas.Subscribe(POSITION, stat_pos.Update)

        stat_sel = UpdatedLabel(status_bar, name = 'selection', text = '',
                                updatecb = canvas.CurrentInfoText)
        stat_sel.pack(side = 'left', fill = X, expand = 1, padx = 2)
        stat_sel.Update()
        update = stat_sel.Update
        canvas.Subscribe(SELECTION, update)
        canvas.Subscribe(CURRENTINFO, update)
        canvas.Subscribe(EDITED, update)

    def EditedInfoText(self):
        if self.document.WasEdited():
            return _("modified")
        return _("unmodified")


    AddCmd('AboutBox', _("About..."))
    def AboutBox(self):
        abouttext = _("Skencil (%(version)s)\n"
                      "(c) 1996-2007 by Bernhard Herzog\n\n"
                      "Versions:\n"
                      "Python:\t%(py)s\tTcl:\t%(tcl)s\n"
                      "Tkinter:\t%(tkinter)s\tTk:\t%(tk)s") \
                  % {'version':SketchVersion,
                     'py':string.split(sys.version)[0],
                     'tcl':TclVersion,
                     'tkinter':string.split(Tkinter.__version__)[1],
                     'tk':TkVersion}

        self.application.MessageBox(title = _("About Skencil"),
                                    message = abouttext,
                                    icon = pixmaps.IconLarge)


    #
    #	Special methods. Mainly interesting for debugging
    #
    AddCmd('DocumentInfo', "Document Info...", key_stroke = 'F12')
    def DocumentInfo(self):
        text = self.document.DocumentInfo()

        from Sketch import _sketch
        meminfo = 'Memory:\n'\
                '# Bezier Paths:\t%d\n'\
                '# RGBColors:\t%d\n' \
                '# Rects:\t\t%d\n'\
                '# Trafos:\t\t%d\n'\
                '# Points:\t\t%d' % (_sketch.num_allocated(),
                                     _sketch.colors_allocated(),
                                     _sketch.rects_allocated(),
                                     _sketch.trafos_allocted(),
                                     _sketch.points_allocated())
        text = text + '\n\n' + meminfo

        self.application.MessageBox(title = 'Document Info', message = text,
                                    icon = 'info')

    AddCmd('DumpXImage', 'Dump XImage')
    def DumpXImage(self):
        gc = self.canvas.gc
        if gc.ximage:
            gc.ximage.dump_data("/tmp/ximage.dat")


#     AddCmd('export_bitmap', 'Export Bitmap')
#     def export_bitmap(self):
#	import export
#	export.export_bitmap(self.document)

    AddCmd('python_prompt', 'Python Prompt', key_stroke = 'F11')
    def python_prompt(self):
        if config.preferences.show_special_menu:
            import prompt
            prompt.PythonPrompt()


    #
    #	Insert Special Objects
    #

    #
    #	Create Image
    #

    def GetOpenImageFilename(self, title = None, initialdir = '',
                             initialfile = '', no_eps = 0):
        if title is None:
            title = _("Load Image")
        if no_eps:
            filetypes = skapp.bitmapfiletypes
        else:
            filetypes = skapp.imagefiletypes
        filename = self.application.GetOpenFilename(title = title,
                                                    filetypes = filetypes,
                                                    initialdir = initialdir,
                                                    initialfile = initialfile)
        return filename

    AddCmd('CreateImage', _("Load Raster/EPS Image..."),
           bitmap = pixmaps.Image, subscribe_to = None)
    def CreateImage(self, filename = None):
        if not filename:
            filename = self.GetOpenImageFilename(title = _("Load Image"),
                                                 initialdir = config.preferences.image_dir,
                                                 initialfile = '')
        if filename:
            try:
                file = open(filename, 'r')
                is_eps = eps.IsEpsFileStart(file.read(256))
                file.close()
                dir, name = os.path.split(filename)
                config.preferences.image_dir = dir
                if is_eps:
                    imageobj = eps.EpsImage(filename = filename)
                else:
                    imageobj = image.Image(imagefile = filename)
                self.canvas.PlaceObject(imageobj)
            except IOError, value:
                if type(value) == TupleType:
                    value = value[1]
                self.application.MessageBox(title = _("Load Image"),
                                            message = _("Cannot load %(filename)s:\n"
                                                        "%(message)s") \
                                            % {'filename':`os.path.split(filename)[1]`,
                                               'message':value},
                                            icon = 'warning')

    AddCmd('AddHorizGuideLine', _("Add Horizontal Guide Line"), 'AddGuideLine',
           args = 1)
    AddCmd('AddVertGuideLine', _("Add Vertical Guide Line"), 'AddGuideLine',
           args = 0)
    def AddGuideLine(self, horizontal = 1):
        self.canvas.PlaceObject(GuideLine(Point(0, 0), horizontal))

    #
    #
    #

    AddCmd('CreateStyleFromSelection', _("Name Style..."),
           sensitive_cb = ('document', 'CanCreateStyle'),
           subscribe_to = SELECTION)
    def CreateStyleFromSelection(self):
        import styledlg
        doc = self.document
        object = doc.CurrentObject()
        style_names = doc.GetStyleNames()
        if object:
            name = styledlg.GetStyleName(self.root, object, style_names)
            if name:
                name, which_properties = name
                doc.CreateStyleFromSelection(name, which_properties)

    def no_pattern(self, category):
        import styledlg
        if category == 'fill':
            title = _("No Fill")
            prop = 'fill_pattern'
        else:
            title = _("No Line")
            prop = 'line_pattern'
        styledlg.set_properties(self.root, self.document, title, category,
                                {prop: EmptyPattern})


    #
    #	Document commands
    #

    AddDocCmd('SelectAll', _("Select All"), sensitive_cb = 'IsSelectionMode',
              subscribe_to = MODE)
    AddDocCmd('SelectNextObject', _("Select Next"), key_stroke = ('Alt+Right','M-Right'))
    AddDocCmd('SelectPreviousObject', _("Select Previous"),
              key_stroke = 'M-Left')
    AddDocCmd('SelectFirstChild', _("Select First Child"),
              key_stroke = 'M-Down')
    AddDocCmd('SelectParent', _("Select Parent"), key_stroke = ('Alt+Up','M-Up'))

    # rearrange object

    AddDocCmd('RemoveSelected', _("Delete"), key_stroke = 'Delete',
              bitmap = pixmaps.Delete)

    AddDocCmd('MoveSelectedToTop', _("Move to Top"),
              bitmap = pixmaps.MoveToTop, key_stroke = 'Home')

    AddDocCmd('MoveSelectedToBottom', _("Move to Bottom"),
              bitmap = pixmaps.MoveToBottom, key_stroke = 'End')

    AddDocCmd('MoveSelectionUp', _("Move One Up"), bitmap = pixmaps.MoveOneUp,
              key_stroke = ('Shift+PageUp', 'S-Prior'))

    AddDocCmd('MoveSelectionDown', _("Move One Down"),
              bitmap = pixmaps.MoveOneDown, key_stroke = ('Shift+PageDown','S-Next'))

    AddDocCmd('DuplicateSelected', _("Duplicate"), bitmap = pixmaps.Duplicate,
              key_stroke = ('Ctrl+D','C-d'))
    #

    AddDocCmd('GroupSelected', _("Group"), sensitive_cb = 'CanGroup',
              key_stroke = ('Ctrl+G', 'C-g'), bitmap = pixmaps.Group)


    AddDocCmd('UngroupSelected', _("Ungroup"), sensitive_cb = 'CanUngroup',
              key_stroke = ('Ctrl+U', 'C-u'), bitmap = pixmaps.Ungroup)

    #

    AddDocCmd('ConvertToCurve', _("Convert To Curve"),
              sensitive_cb = 'CanConvertToCurve', key_stroke = ('Ctrl+Q','C-q'))

    AddDocCmd('CombineBeziers', _("Combine Beziers"),
              sensitive_cb = 'CanCombineBeziers')

    AddDocCmd('SplitBeziers', _("Split Beziers"),
              sensitive_cb = 'CanSplitBeziers')

    #
    #	Align
    #
    AddDocCmd('AbutHorizontal', _("Abut Horizontal"))
    AddDocCmd('AbutVertical', _("Abut Vertical"))

    AddDocCmd('FlipHorizontal', _("Flip Horizontal"), 'FlipSelected',
              args = (1, 0), bitmap = pixmaps.FlipHorizontal)

    AddDocCmd('FlipVertical', _("Flip Vertical"), 'FlipSelected',
              args = (0, 1), bitmap = pixmaps.FlipVertical)


    # effects
    AddDocCmd('CancelBlend', _("Cancel Blend"),
              sensitive_cb = 'CanCancelBlend')

    AddDocCmd('RemoveTransformation', _("Remove Transformation"))

    AddDocCmd('CreateMaskGroup', _("Create Mask Group"),
              sensitive_cb = 'CanCreateMaskGroup')
    AddDocCmd('CreatePathText', _("Create Path Text"),
              sensitive_cb = 'CanCreatePathText')
    AddDocCmd('CreateClone', _("Create Clone"),
              sensitive_cb = 'CanCreateClone')


    #
    #	Cut/Paste
    #

    def CutCopySelected(self, method):
        objects = getattr(self.document, method)()
        if objects is not None:
            self.application.SetClipboard(objects)

    AddCmd('CopySelected', _("Copy"), 'CutCopySelected',
           args= ('CopyForClipboard',), subscribe_to = SELECTION,
           sensitive_cb = ('document', 'HasSelection'))
    AddCmd('CutSelected', _("Cut"), 'CutCopySelected',
           args= ('CutForClipboard',), subscribe_to = SELECTION,
           sensitive_cb = ('document', 'HasSelection'))
    AddCmd('PasteClipboard', _("Paste"),
           subscribe_to = ('application', CLIPBOARD),
           sensitive_cb = ('application', 'ClipboardContainsData'))
    def PasteClipboard(self):
        if self.application.ClipboardContainsData():
            obj = self.application.GetClipboard().Object()
            obj = obj.Duplicate()
            self.canvas.PlaceObject(obj)
    #
    #	Undo/Redo
    #

    AddDocCmd('Undo', _("Undo"), subscribe_to = UNDO,
              sensitive_cb = 'CanUndo', name_cb = 'UndoMenuText',
              key_stroke = ('Ctrl+Z','C-z'), bitmap = pixmaps.Undo)

    AddDocCmd('Redo', _("Redo"), subscribe_to = UNDO,
              sensitive_cb = 'CanRedo', name_cb = 'RedoMenuText',
              key_stroke = ('Ctrl+R','C-r'), bitmap = pixmaps.Redo)

    AddDocCmd('ResetUndo', _("Discard Undo History"), subscribe_to = None,
              sensitive_cb = None)



    #
    #	Styles
    #
    AddDocCmd('FillNone', _("No Fill"), 'AddStyle', args = EmptyFillStyle)
    AddDocCmd('LineNone', _("No Line"), 'AddStyle', args = EmptyLineStyle)
    AddDocCmd('UpdateStyle', _("Update Style"), 'UpdateDynamicStyleSel')


