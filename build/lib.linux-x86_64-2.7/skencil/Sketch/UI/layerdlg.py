# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 2000 by Bernhard Herzog
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


# A dialog to rearrange the layers of the document and change some of
# their properties.

from Tkinter import Button, Scrollbar, Frame, IntVar, Canvas, Label
from Tkinter import RIGHT, BOTTOM, X, Y, BOTH, LEFT, W, NW, NORMAL, DISABLED

from Sketch.const import LAYER, LAYER_ACTIVE, LAYER_ORDER, \
     SelectSubtract, SelectAdd
from Sketch import _

from tkext import UpdatedButton, MyEntry, UpdatedCheckbutton, \
     ColorButton, UpdatedRadiobutton, MenuCommand, UpdatedMenu, MakeCommand
from sketchdlg import SketchPanel, SKModal
import skpixmaps
pixmaps = skpixmaps.PixmapTk

class MutableNumber:

    def __init__(self, value = 0):
        self.value = value

    def SetValue(self, value):
        self.value = value

    def __int__(self):
        return int(self.value)

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return `self.value`

class LayerInfo:

    def __init__(self, frame, idx, info, active_var, rename, set_active_layer,
                 set_layer_state, set_color, context_menu):
        self.index = MutableNumber()
        self.active_var = active_var
        self.create_widgets(frame, idx, set_active_layer, rename,
                            set_layer_state, set_color, context_menu)
        if info:
            self.SetInfo(info)

    def create_widgets(self, frame, idx, set_active_layer, rename,
                       set_layer_state, set_color, context_menu):
        self.index.SetValue(idx)
        idx = (self.index,)
        self.button = UpdatedRadiobutton(frame, anchor = W, value = idx,
                                         width = 10,
                                         variable = self.active_var,
                                         command = set_active_layer)
        self.button.bind('<ButtonPress-3>', context_menu)
        self.button.bind('<ButtonPress-2>', rename)
        self.button.bind('<Double-Button-1>', rename)
        self.var_visible = IntVar(frame)
        self.visible = UpdatedCheckbutton(frame, variable = self.var_visible,
                                          indicatoron = 0, selectcolor = '',
                                          command = set_layer_state,
                                          args = idx)
        self.var_printable = IntVar(frame)
        self.printable = UpdatedCheckbutton(frame,
                                            variable = self.var_printable,
                                            indicatoron = 0, selectcolor = '',
                                            command = set_layer_state,
                                            args = idx)
        self.var_locked = IntVar(frame)
        self.locked = UpdatedCheckbutton(frame, variable = self.var_locked,
                                         indicatoron = 0, selectcolor = '',
                                         command = set_layer_state, args = idx)
        self.var_outlined = IntVar(frame)
        self.outlined = UpdatedCheckbutton(frame, variable = self.var_outlined,
                                           indicatoron = 0, selectcolor = '',
                                           command = set_layer_state,
                                           args = idx)
        self.color = ColorButton(frame, command = set_color, args = idx,
                                 width = 2,
                                 dialog_master =
                                 frame.master.master.master.master)

    def SetInfo(self, idx, info):
        self.index.SetValue(idx)
        p = pixmaps
        #name, visible, printable, locked, outlined, color = info
        self.button['text'] = info.Name()

        visible = info.Visible()
        self.var_visible.set(visible)
        self.visible['bitmap'] = visible and p.MiniEyeOpen or p.MiniEyeClosed

        printable = info.Printable()
        self.var_printable.set(printable)
        self.printable['bitmap']= printable and p.MiniPrintOn or p.MiniPrintOff

        locked = info.Locked()
        self.var_locked.set(locked)
        self.locked['bitmap'] = locked and p.MiniLockClosed or p.MiniLockOpen

        outlined = info.Outlined()
        self.var_outlined.set(outlined)
        bm = outlined and p.MiniOutlineOn or p.MiniOutlineOff
        self.outlined['bitmap'] = bm

        self.color.SetColor(info.OutlineColor())

        if info.is_GridLayer:
            self.locked['state'] = self.outlined['state'] \
                = self.printable['state'] = DISABLED
        else:
            self.locked['state'] = NORMAL
            if info.is_GuideLayer:
                self.printable['state'] = self.outlined['state'] = DISABLED
            else:
                self.printable['state'] = self.outlined['state'] = NORMAL

    def PlaceWidgets(self, idx):
        self.button.grid(row = idx, column = 0, sticky = 'NEWS')
        self.visible.grid(row = idx, column = 1, sticky = 'NEWS')
        self.printable.grid(row = idx, column = 2, sticky = 'NEWS')
        self.locked.grid(row = idx, column = 3, sticky = 'NEWS')
        self.outlined.grid(row = idx, column = 4, sticky = 'NEWS')
        self.color.grid(row = idx, column = 5, sticky = 'NEWS')

    def State(self):
        return (self.var_visible.get(),
                self.var_printable.get(),
                self.var_locked.get(),
                self.var_outlined.get())

    def Color(self):
        return self.color.Color()

    def Destroy(self):
        self.button.destroy()
        self.visible.destroy()
        self.printable.destroy()
        self.locked.destroy()
        self.outlined.destroy()
        self.color.destroy()

class LayerPanel(SketchPanel):

    title = _("Layers")
    receivers = SketchPanel.receivers[:]

    def __init__(self, master, main_window, doc):
        self.info_list = []
        SketchPanel.__init__(self, master, main_window, doc, name = 'layerdlg')

    def build_dlg(self):
        top = self.top

        frame = Frame(top)
        frame.pack(side = BOTTOM, fill = X)
        button = UpdatedButton(frame, bitmap = pixmaps.LayerNew, name = 'new',
                               command = self.new_layer)
        button.pack(side = LEFT, fill = BOTH, expand = 1)
        button = UpdatedButton(frame, bitmap = pixmaps.LayerUp, name = 'up',
                               command = self.layer_up)
        button.pack(side = LEFT, fill = BOTH, expand = 1)
        button = UpdatedButton(frame, bitmap = pixmaps.LayerDown,
                               name = 'down', command = self.layer_down)
        button.pack(side = LEFT, fill = BOTH, expand = 1)
        button = UpdatedButton(frame, text = _("Close"), name = 'close',
                               command = self.close_dlg)
        button.pack(side = LEFT, fill = BOTH, expand = 1)

        list_frame = Frame(top)
        list_frame.pack(side = LEFT, expand = 1, fill = BOTH)

        sb_vert = Scrollbar(list_frame, takefocus = 0)
        sb_vert.pack(side = RIGHT, fill = Y)

        self.canvas = canvas = Canvas(list_frame)
        canvas.pack(expand = 1, fill = BOTH)

        self.frame = frame = Frame(canvas, name = 'list')
        canvas.create_window(0, 0, window = frame, anchor = NW)
        sb_vert['command'] = (canvas, 'yview')
        canvas['yscrollcommand'] = (sb_vert, 'set')

        self.active_var = IntVar(top)

    def init_from_doc(self):
        self.Update(LAYER_ORDER)

    receivers.append((LAYER, 'Update'))
    def Update(self, detail = '', *args):
        if detail != LAYER_ACTIVE:
            if detail == LAYER_ORDER:
                self.create_widget_list()
            else:
                self.update_widgets()
        self.update_active()

    def create_widget_list(self):
        frame = self.frame
        set_active_layer = self.set_active_layer
        set_layer_state = self.set_layer_state
        set_color = self.set_color
        context_menu = self.popup_context_menu
        rows = self.info_list
        layers = self.document.NumLayers()
        if layers > len(rows):
            for idx in range(len(rows), layers):
                row = LayerInfo(frame, idx, (), self.active_var,
                                self.rename_layer, set_active_layer,
                                set_layer_state, set_color, context_menu)
                row.PlaceWidgets(idx)
                rows.append(row)
        elif layers < len(rows):
            for row in rows[layers:]:
                row.Destroy()
            del rows[layers:]
        self.update_widgets()
        frame.update()
        self.canvas['scrollregion'] = (0, 0, frame.winfo_reqwidth(),
                                       frame.winfo_reqheight())
        self.canvas['width'] = frame.winfo_reqwidth()

    def update_widgets(self):
        layers = self.document.layers[:]
        layers.reverse()
        for idx in range(len(layers)):
            self.info_list[idx].SetInfo(idx, layers[idx])

    def update_active(self):
        idx = self.document.ActiveLayerIdx()
        if idx is None:
            idx = -1
        self.active_var.set(self.document.NumLayers() - 1 - idx)

    def set_active_layer(self):
        idx = self.document.NumLayers() - self.active_var.get() - 1
        self.document.SetActiveLayer(idx)

    def set_layer_state(self, idx):
        idx = int(idx)
        row = self.info_list[idx]
        idx = self.document.NumLayers() - idx - 1
        state = row.State()
        apply(self.document.SetLayerState, (idx,) + state)

    def set_color(self, idx):
        idx = int(idx)
        row = self.info_list[idx]
        idx = self.document.NumLayers() - idx - 1
        self.document.SetLayerColor(idx, row.Color())

    def set_event_context(self, event):
        for idx in range(len(self.info_list)):
            if self.info_list[idx].button == event.widget:
                break
        else:
            return
        self.context_idx = self.document.NumLayers() - 1 - idx
        self.context_layer = self.document.Layers()[self.context_idx]

    context_menu = None
    def popup_context_menu(self, event):
        self.set_event_context(event)
        if self.context_menu is None:
            self.context_menu = UpdatedMenu(self.frame, [], tearoff = 0,
                                            auto_rebuild = self.build_context_menu)
        self.context_menu.Popup(event.x_root, event.y_root)

    def build_context_menu(self):
        entries = [
            (_("Rename"), self.rename_layer),
            None,
            (_("Lower Layer"), self.layer_down, 0),
            (_("Raise Layer"), self.layer_up, 0),
            (_("Delete"), self.delete_layer, (), self.can_delete_layer),
            None,
            (_("Move Selection Here"), self.move_selection_here, (),
             self.can_move_selection),
            (_("Select All Children"), self.select_layer, SelectAdd,
             self.is_not_locked),
            (_("Deselect All Children"), self.select_layer, SelectSubtract,
             self.is_not_locked)
        ]
        if self.context_layer.is_GuideLayer:
            entries.append(None)
            entries.append(self.main_window.commands.CreateGuideDialog)
        if self.context_layer.is_GridLayer:
            entries.append(None)
            entries.append(self.main_window.commands.CreateGridDialog)
        return map(MakeCommand, entries)

    def close_dlg(self):
        SketchPanel.close_dlg(self)
        if self.context_menu is not None:
            self.context_menu.destroy()

    def rename_layer(self, event = None):
        if event is not None:
            self.set_event_context(event)
        name = GetName(self.top, self.context_layer.Name())
        if name != None:
            self.document.SetLayerName(self.context_idx, name)

    def delete_layer(self):
        self.document.DeleteLayer(self.context_idx)

    def can_delete_layer(self):
        return self.document.CanDeleteLayer(self.context_idx)

    def new_layer(self):
        self.document.NewLayer()

    def layer_up(self, active_layer = 1):
        if active_layer:
            active_idx = self.active_var.get()
            if active_idx < 0:
                return
            idx = self.document.NumLayers() - 1 - active_idx
        else:
            idx = self.context_idx
        self.document.MoveLayerUp(idx)

    def layer_down(self, active_layer = 1):
        if active_layer:
            active_idx = self.active_var.get()
            if active_idx < 0:
                return
            idx = self.document.NumLayers() - 1 - active_idx
        else:
            idx = self.context_idx
        self.document.MoveLayerDown(idx)

    def move_selection_here(self):
        self.document.MoveSelectionToLayer(self.context_idx)

    def can_move_selection(self):
        return not self.context_layer.Locked() and self.document.HasSelection()

    def is_not_locked(self):
        return not self.context_layer.Locked()

    def select_layer(self, mode):
        self.document.SelectLayer(self.context_idx, mode)



class GetNameDlg(SKModal):

    title = _("Name")

    def __init__(self, master, name, **kw):
        self.name = name
        apply(SKModal.__init__, (self, master), kw)

    def build_dlg(self):
        top = self.top

        frame = Frame(top)
        frame.pack(side = BOTTOM, fill = BOTH, expand = 1)
        button = Button(frame, text = _("OK"), command = self.ok)
        button.pack(side = LEFT, expand = 1)
        button = Button(frame, text = _("Cancel"), command = self.cancel)
        button.pack(side = RIGHT, expand = 1)

        self.label = Label(top, text = _("Name"))
        self.label.pack(side = LEFT)

        self.entry = MyEntry(top, command = self.ok)
        self.entry.pack(side = RIGHT, expand = 1, fill = X)
        self.entry.SetText(self.name)

    def ok(self, *args):
        self.close_dlg(self.entry.get())

def GetName(master, name):
    dlg = GetNameDlg(master, name)
    return dlg.RunDialog()
