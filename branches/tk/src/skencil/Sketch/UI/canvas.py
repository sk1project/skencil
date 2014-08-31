# Sketch - A Python-based interactive drawing program
# Copyright (C) 1996, 1997, 1998, 1999, 2000, 2001, 2004 by Bernhard Herzog
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

#
# SketchCanvas
#
# Displays the contents of a document and accepts user input in the form
# of mouse and keyboard events.
#

import string
from types import TupleType

from Sketch.Lib.util import Empty, format

from Sketch import _, InvertingDevice, HitTestDevice, StandardColors, Point
from Sketch.Graphics.selection import SelectionRectangle

from Sketch import const, SketchInternalError, SelectionMode, EditMode
from Sketch.config import preferences
from Sketch.warn import pdebug, warn, INTERNAL

from Sketch.const import STATE, MODE, SELECTION, VIEW, POSITION, EDITED, \
     LAYER_STATE, LAYER_ACTIVE, CURRENTINFO, CHANGED, \
     SelectSet, SelectAdd, SelectSubtract, \
     SelectSubobjects, SelectDrag, SelectGuide
import Sketch

import command
import skpixmaps
pixmaps = skpixmaps.PixmapTk
from tkext import MakeCommand, UpdatedMenu

from cursorstack import CursorStack
from view import SketchView
from modes import MajorMode, TemporaryMode, WidgetWithModes, noop

from converters import converters


constraint_keysyms =   {'Control_L' : const.ControlMask,
                        'Control_R' : const.ControlMask,
                        'Shift_L'   : const.ShiftMask,
                        'Shift_R'   : const.ShiftMask}

command_list = []
def AddCmd(name, menu_name, method_name = None, subscribe_to = STATE, **kw):
    # use name both as name and method name
    kw['menu_name'] = menu_name
    kw['subscribe_to'] = subscribe_to
    if not method_name:
        method_name = name
    cmd = apply(command.CommandClass, (name, method_name), kw)
    command_list.append(cmd)

def AddSelCmd(*args, **kw):
    if not kw.has_key('sensitive_cb'):
        kw['sensitive_cb'] = ('document', 'HasSelection')
    if not kw.has_key('subscribe_to'):
        kw['subscribe_to'] = SELECTION
    apply(AddCmd, args, kw)

def AddModeCmd(*args, **kw):
    if not kw.has_key('value_cb'):
        kw['value_cb'] = 'ModeName'
    if not kw.has_key('subscribe_to'):
        kw['subscribe_to'] = MODE
    if not kw.has_key('is_check'):
        kw['is_check'] = 1
    apply(AddCmd, args, kw)

class CanvasError(SketchInternalError):
    pass


# stop codes

stop_continue = 0
stop_regular = 1


def selection_type(state):
    state = state & const.AllowedModifierMask
    if state  == const.AddSelectionMask:
        type = SelectAdd
    elif state == const.SubtractSelectionMask:
        type = SelectSubtract
    elif state == const.SubobjectSelectionMask:
        type = SelectSubobjects
    else:
        type = SelectSet
    return type

class SketchCanvas(SketchView, CursorStack, WidgetWithModes):

    document = None
    commands = None

    context_menu_items = ['CreateFillStyleDialog',
                          'FillSolid',
                          'FillNone',
                          None,
                          'CreateLineStyleDialog',
                          'LineNone',
                          None,
                          'CreateFontDialog',
                          None,
                          'CreateStyleFromSelection',
                          None,
                          'FitSelectedToWindow',
                          'FitPageToWindow']

    def __init__(self, master=None, toplevel = None, main_window = None,
                 document = None, **kw):
        self.init_handles()
        self.init_modes()
        self.init_cross_hairs()
        WidgetWithModes.__init__(self)
        kw['show_visible'] = 1
        kw['show_printable'] = 0
        self.snap_to_object = 0
        self.snap_to_guide = 0
        self.snap_correction_rect = 1
        self.snap_move_relative = 0 #1
        apply(SketchView.__init__, (self, master, toplevel, document), kw)
        CursorStack.__init__(self, const.CurStd, self.set_handle_cursor)

        self.main_window = main_window

        self.current_pos = Point(0, 0)
        self.current_info_text = None
        self.expect_release_event = 0
        self.ignore_key_press_events = 0
        self.start_drag = 0
        self.start_pos = None
        self.dragging = 0	# true if dragging with left button down
        self.current = None	# currently dragged/edited object
        self.correction = Point(0, 0)
        self.create_creator = None	# Class of object to create
                                # None while in select/edit mode
        self.create_type = ''
        self.snap_to_grid = 0
        self.snap_points = ()
        self.init_bindings()

        self.SelectionMode()
        self.create_commands()
        self.context_commands = None

        preferences.Subscribe(CHANGED, self.preference_changed)

    def init_modes(self):
        self.modes = m = Empty()
        m.selection_mode = MajorMode(self.selection_enter,
                                     self.selection_down, self.drag_mouse,
                                     self.selection_up, noop,
                                     self.selection_cancel,
                                     start_drag = self.selection_start_drag,
                                     name = 'Select',
                                     text = _("Select"))
        m.edit_mode = MajorMode(self.edit_enter,
                                self.edit_down, self.drag_mouse, self.edit_up,
                                noop, self.edit_cancel,
                                start_drag = self.edit_start_drag,
                                name = 'Edit',
                                text = _("Edit"))
        m.creation_mode = MajorMode(self.creation_enter,
                                    self.creation_begin, self.drag_to,
                                    self.creation_end, self.creation_exit,
                                    self.creation_cancel,
                                    name = 'Create',
                                    text = _("Create"))
        m.zoom_mode = TemporaryMode(self.zoom_enter, self.zoom_begin,
                                    self.drag_to, self.zoom_end,
                                    noop, self.zoom_cancel,
                                    name = 'Zoom',
                                    text = _("Zoom Area"))
        m.pick_mode = TemporaryMode(self.pick_enter, self.pick_begin, noop,
                                    self.pick_end, noop, self.pick_cancel,
                                    name = 'Pick',
                                    text = _("Pick Object"))
        m.place_mode = TemporaryMode(self.place_enter, self.place_begin,
                                     self.place_drag, self.place_end,
                                     noop, self.place_cancel,
                                     name = 'Place',
                                     text = _("Place Object"))

    def init_bindings(self):
        self.bind('<ButtonPress>', self.ButtonPressEvent)
        self.bind('<Motion>', self.PointerMotionEvent)
        self.bind('<ButtonRelease>', self.ButtonReleaseEvent)
        self.bind('<KeyPress>', self.KeyPressEvent)
        self.bind('<KeyRelease>', self.KeyReleaseEvent)
        self.bind('<Leave>', self.LeaveEvent)
        self.bind('<Enter>', self.EnterEvent)
        self.last_event = None

    scroll_timer = None
    def start_auto_scroll(self):
        intervall = preferences.autoscroll_interval
        if intervall:
            self.scroll_timer = self.after(intervall, self.auto_scroll)

    def cancel_auto_scroll(self):
        if self.scroll_timer is not None:
            self.after_cancel(self.scroll_timer)

    def auto_scroll(self):
        x, y, state = self.tkwin.QueryPointer()[4:7]
        if state & const.Button1Mask:
            amount = preferences.autoscroll_amount
            self.begin_transaction()
            if x < 0:
                self.ScrollXUnits(-amount)
            elif x > self.tkwin.width:
                self.ScrollXUnits(amount)
            if y < 0:
                self.ScrollYUnits(-amount)
            elif y > self.tkwin.height:
                self.ScrollYUnits(amount)
            self.start_auto_scroll()
            self.handle_update_pending = 0
            self.end_transaction()

    def LeaveEvent(self, event):
        if event.state & const.Button1Mask:
            self.start_auto_scroll()
        self.hide_crosshairs()
        self.crosshairs_visible = 0

    def EnterEvent(self, event):
        self.cancel_auto_scroll()
        self.crosshairs_visible = 1
        self.show_crosshairs()

    def create_obj_cmds(self, commands):
        cmds = command.Commands()
        keymap = command.Keymap()
        for cmd_class in commands:
            cmd = cmd_class.InstantiateFor(self)
            setattr(cmds, cmd.name, cmd)
            keymap.AddCommand(cmd)
        return cmds, keymap

    def create_commands(self):
        cmds = command.Commands()
        keymap = command.Keymap()
        for cmd_class in command_list:
            cmd = cmd_class.InstantiateFor(self)
            setattr(cmds, cmd.name, cmd)
            keymap.AddCommand(cmd)
        self.keymap = keymap

        class_maps = {}
        classes = Sketch.command_classes
        for aclass in classes:
            name = aclass.__name__
            if aclass.is_Editor:
                #name = aclass.EditedClass.__name__
                commands = aclass.commands + aclass.EditedClass.commands
            else:
                commands = aclass.commands
            ocmds, keymap = self.create_obj_cmds(commands)
            setattr(cmds, name, ocmds)
            class_maps[name] = keymap

            if self.context_menu_items[-1] != None:
                # insert a separator if necessary
                self.context_menu_items.append(None)
            self.context_menu_items = self.context_menu_items \
                + list(aclass.context_commands)

        self.commands = cmds
        self.object_keymap = None
        self.class_maps = class_maps

    def find_map(self, classes):
        maps = self.class_maps
        result = None
        for c in classes:
            map = maps.get(c.__name__)
            if map is not None:
                result =  map
                break
            map = self.find_map(c.__bases__)
            if map is not None:
                result =  map
                break
        return result

    def update_object_keymap(self):
        self.object_keymap = None
        obj = self.document.CurrentObject()
        if obj is not None:
            if self.document.selection.is_EditSelection:
                # XXX very ugly hack
                cls = self.document.selection.editor.editor.__class__
            else:
                cls = obj.__class__
            self.object_keymap = self.find_map((cls,))

    def UpdateCommands(self):
        # currently needed to ensure that all buttons have correct
        # sensitivity at startup
        self.commands.Update()

    def init_gcs(self):
        # XXX: integrate with SketchView
        self.gc.init_gc(self.tkwin, graphics_exposures = 1)
        self.invgc = InvertingDevice()
        self.invgc.init_gc(self.tkwin)
        self.hitgc = HitTestDevice()
        self.hitgc.init_gc(self.tkwin)
        #self.tk.call(self._w, 'motionhints')
        self.draw_handle_funcs = [self.invgc.DrawRectHandle,
                                  self.invgc.DrawRectHandle,
                                  self.invgc.DrawSmallRectHandle,
                                  self.invgc.DrawSmallRectHandle,
                                  self.invgc.DrawCircleHandle,
                                  self.invgc.DrawCircleHandle,
                                  self.invgc.DrawSmallCircleHandle,
                                  self.invgc.DrawSmallCircleHandle,
                                  self.invgc.DrawSmallRectHandleList,
                                  self.invgc.DrawHandleLine,
                                  self.invgc.DrawPixmapHandle,
                                  self.invgc.DrawCaretHandle]
        self.gcs_initialized = 1
        self.FitPageToWindow(save_viewport = 0)
        self.set_gc_transforms()

    def set_gc_transforms(self):
        SketchView.set_gc_transforms(self)
        if self.gcs_initialized:
            self.invgc.SetViewportTransform(self.scale, self.doc_to_win,
                                            self.win_to_doc)
            self.hitgc.SetViewportTransform(self.scale, self.doc_to_win,
                                            self.win_to_doc)


    #
    #	Channels
    #

    def issue_selection(self):
        self.queue_message(SELECTION)

    def issue_mode(self):
        self.queue_message(MODE)

    def queue_update_handles(self):
        self.handle_update_pending = 1

    def init_transactions(self):
        SketchView.init_transactions(self)
        self.handle_update_pending = 0

    def end_transaction(self):
        SketchView.end_transaction(self)
        if self.transaction == 0:
            if self.handle_update_pending:
                self.update_handles()
            self.handle_update_pending = 0

    def check_transaction(self):
        # for debugging, check whether a transaction is active
        if not self.transaction:
            pdebug(None, 'Warning: no transaction')

    def call_document_method(self, method, *args, **kwargs):
        method = getattr(self.document, method)
        apply(method, args, kwargs)

    #
    #	receivers for channels
    #

    def preference_changed(self, attr, value):
        if attr == 'default_unit':
            self.selection_info_text = None
            self.issue(CURRENTINFO)

    def selection_changed(self):
        self.selection_info_text = None
        self.issue_selection()
        self.update_handles()
        self.update_object_keymap()
        if self.gcs_initialized:
            x, y = self.tkwin.QueryPointer()[4:6]
            self.set_handle_cursor(x, y)

    def doc_was_edited(self, *rest):
        self.selection_info_text = None
        self.update_snap_points()
        self.update_handles()
        self.queue_message(EDITED)

    # extend the method of SketchView. SketchView subscribes this.
    def layer_changed(self, *args):
        if args:
            recompute = 0
            if args[0] == LAYER_STATE:
                layer, visible_changed, printable_changed, outlined_changed \
                     = args[1]
                if layer.NumObjects():
                    if ((self.show_printable and printable_changed)
                        or (self.show_visible and visible_changed)):
                        recompute = 1
            elif args[0] == LAYER_ACTIVE:
                if (self.mode is self.modes.creation_mode
                    and self.document.ActiveLayer() is None):
                    self.mode.cancel()
                else:
                    self.issue_mode()
            if recompute:
                self.update_snap_points()
        apply(SketchView.layer_changed, (self,) + args)

    #
    #	Widget Methods (Redraw, ... )
    #

    def RedrawMethod(self, region = None):
        #self.hide_handles()
        #print 'RedrawMethod', region
        if hasattr(preferences, 'profile_redraw'):
            import profile
            warn(INTERNAL, 'profiling...')
            prof = profile.Profile()
            prof.runctx('region = SketchView.RedrawMethod(self, region)',
                        globals(), locals())
            prof.dump_stats('/tmp/redraw.prof')
            warn(INTERNAL, 'profiling... (done)')
            del preferences.profile_redraw
        else:
            region = SketchView.RedrawMethod(self, region)

        # draw the handles
        self.invgc.InitClip()
        if region:
            self.invgc.PushClip()
            self.invgc.ClipRegion(region)
        if self.current is not None:
            self.current.DrawDragged(self.invgc, 0)
        else:
            self.show_handles(1)
        self.show_crosshairs(1)
        if region:
            self.invgc.PopClip()
        #self.show_handles()

        # The sync helps to avoid the scroll bug. Clicking once into the
        # scroll bar to scroll by a page could scroll twice for a
        # complex drawing.
        self.tkwin.Sync()

    #
    #	Event handler
    #

    def ButtonPressEvent(self, event):
        # handle button press event
        self.begin_transaction()
        self.expect_release_event = 1
        self.last_event = event
        try:
            self.ignore_key_press_events = 1
            button = event.num
            if button == const.Button1:
                p = self.WinToDoc(event.x, event.y)
                self.mode.button_down(p, button, event.state)
            elif button == const.ContextButton:
                self.popup_context_menu(event.x_root, event.y_root,
                                        button, event.state)
                self.ignore_key_press_events = 0
            elif button == const.Button4:
                self.ScrollYUnits(-3)
            elif button == const.Button5:
                self.ScrollYUnits(3)
        finally:
            self.end_transaction()

    def PointerMotionEvent(self, event):
        # handle Motion events
        #event.button = event.num
        #event.x, event.y = self.tkwin.QueryPointer()[4:6]
        self.last_event = event
        p = self.WinToDoc(event.x, event.y)
        self.set_current_pos(p, snap = 1)
        if self.start_drag or self.dragging:
            self.mode.mouse_move(p, event.state)
            self.update_current_info_text()
        else:
            if self.cursor_function:
                self.cursor_function(event.x, event.y)
        self.hide_crosshairs()
        self.show_crosshairs()

    def ButtonReleaseEvent(self, event):
        self.grab_release()
        self.cancel_auto_scroll()
        if not self.expect_release_event:
            return
        self.last_event = event
        self.begin_transaction()
        try:
            p = self.WinToDoc(event.x, event.y)
            event.button = event.num
            if event.button == const.Button1:
                self.mode.button_up(p, event.button, event.state)
                self.dragging = 0
            elif event.button == const.Button2:
                self.mode.button_up(p, event.button, event.state,
                                    force_stop = stop_regular)
                self.dragging = 0
        finally:
            if self.mode.isTemporaryMode:
                self.exit_temporary_mode()
            self.ignore_key_press_events = 0
            self.expect_release_event = 0
            self.end_transaction()

    def MapKeystroke(self, stroke):
        if self.object_keymap:
            cmd = self.object_keymap.MapKeystroke(stroke)
            if cmd:
                return cmd
        cmd = self.keymap.MapKeystroke(stroke)
        if cmd:
            return cmd

        return self.main_window.MapKeystroke(stroke)

    def KeyPressEvent(self, event):
        self.begin_transaction()
        try:
            state = event.state
            sym = event.keysym
            char = event.char
            try:
                char = self.tk.utf8_to_latin1(char)
            except AttributeError:
                # we're using Python's own _tkinter. FIXME: we should
                # handle this case properly, bit it only happens with
                # python <= 1.5.1, so it shouldn't be much of a problem
                pass
            # key events should probably be also handled by the modes
            if sym == 'Escape':
                self.cancel_current_mode()
                return
            mask = constraint_keysyms.get(sym, 0)
            if mask:
                # generate a `fake' motion event if a modifier changed. This is
                # done to reflect changes in the constraints during a drag
                # immediately.
                # modify the state, because it reflects the state before the
                # key press
                event.state = event.state ^ mask
                self.PointerMotionEvent(event)
            if self.ignore_key_press_events:
                return
            if char and ord(char) < 32:
                char = ''

            # build the modifier part of the key for the keymap
            modm = state & const.MetaMask and 'M-' or ''
            modc = state & const.ControlMask and 'C-' or ''
            mods = state & const.ShiftMask and 'S-' or ''
            if char:
                mod = modm + modc
            else:
                mod = modm + modc + mods

            cmd = None
            if char:
                # the key produced a normal character. Try the binding
                # for this first.
                stroke = mod + char
                cmd = self.MapKeystroke(stroke)

            if not cmd and char != sym:
                # there was no character or no entry in the keymap. Try
                # the keysym next.
                #
                # XXX: The current implementation allows bindings for
                # the Shift- and Control-keys, etc.
                stroke = mod + sym
                cmd = self.MapKeystroke(stroke)

            if cmd:
                if cmd.invoke_with_keystroke:
                    cmd.Invoke(stroke)
                else:
                    cmd.Invoke()
        finally:
            self.end_transaction()

    def KeyReleaseEvent(self, event):
        # generate a `fake' motion event if a modifier changed. This is
        # done to reflect changes in the constraints during a drag
        # immediately.
        mask = constraint_keysyms.get(event.keysym, 0)
        if mask:
            # modify the state, because it reflects the state before the
            # key release
            event.state = event.state ^ mask
            self.PointerMotionEvent(event)


    #
    #

    def build_context_commands(self):
        items = []
        for entry in self.context_menu_items:
            if entry:
                cmd = self.commands.Get(entry)
                if not cmd:
                    cmd = self.main_window.commands.Get(entry)
                if cmd:
                    items.append(cmd)
                else:
                    # XXX: if the context menu is configurable by the
                    # user, this should be visible to the user.
                    warn(INTERNAL, 'unknown command', entry)
            else:
                items.append(entry)
        self.context_commands = items


    def popup_context_menu(self, x, y, button, state):
        if state & const.AllButtonsMask == 0:
            if __debug__:
                pdebug('context_menu', 'popup_context_menu',
                       x, y, button, state)
            if self.context_commands is None:
                self.build_context_commands()

            items = []
            last = None
            for cmd in self.context_commands:
                if cmd and not cmd.InContext():
                    cmd = None
                if cmd != last:
                    items.append(cmd)
                last = cmd
            if items and items[0] is None:
                del items[0]
            if items and items[-1] is None:
                del items[-1]
            if items:
                context_menu = UpdatedMenu(self, map(MakeCommand, items))
                context_menu.Popup(x, y)
                context_menu.clean_up()

    #
    #	Report the current pointer position in doc coords.
    #	(might be also interesting for the view)
    #

    def set_current_pos(self, p, snap = 0):
        if snap and preferences.snap_current_pos:
            p = self.snap_point(p)
        self.current_pos = p
        self.issue(POSITION)

    def GetCurrentPos(self):
        return self.current_pos

    #
    #	Report the current state of the dragged object.
    #

    def update_current_info_text(self):
        if self.current is not None:
            self.current_info_text = self.current.CurrentInfoText()
            self.issue(CURRENTINFO)

    def CurrentInfoText(self):
        if self.current is not None and self.current_info_text:
            if type(self.current_info_text) == TupleType:
                template, dict = self.current_info_text
                self.current_info_text = format(template, converters, dict)
            return self.current_info_text
        else:
            if self.selection_info_text is None:
                text = self.document.SelectionInfoText()
                if type(text) == TupleType:
                    template, dict = text
                    text = format(template, converters, dict)
                self.selection_info_text = text
            return self.selection_info_text


    #
    #	The mode specific functions
    #
    #	Extend some inherited methods to issue the appropriate messages

    def push_mode(self, mode):
        WidgetWithModes.push_mode(self, mode)
        self.issue_mode()

    def pop_mode(self):
        WidgetWithModes.pop_mode(self)
        self.issue_mode()

    def enter_mode(self, mode, *args):
        apply(WidgetWithModes.enter_mode, (self, mode) + args)
        self.issue_mode()


    #
    def cancel_current_mode(self):
        if self.mode.isTemporaryMode:
            self.cancel_temporary_mode()
        else:
            self.mode.cancel()
    #
    #	Creation mode
    #

    def can_create(self):
        return self.document.ActiveLayer() is not None

    # enter creation mode for a gfx_name objects
    AddModeCmd('CreateRectangle', _("Draw Rectangle"), 'Create',
               args = 'RectangleCreator', bitmap = pixmaps.CreateRect,
               value_on = 'Create:RectangleCreator',
               sensitive_cb = 'can_create')
    AddModeCmd('CreateEllipse', _("Draw Ellipse"), 'Create',
               args = 'EllipseCreator', bitmap = pixmaps.CreateEllipse,
               value_on = 'Create:EllipseCreator',
               sensitive_cb = 'can_create')
    AddModeCmd('CreatePolyBezier', _("Draw Curve"), 'Create',
               args = 'PolyBezierCreator', bitmap = pixmaps.CreateCurve,
               value_on = 'Create:PolyBezierCreator',
               sensitive_cb = 'can_create')
    AddModeCmd('CreatePolyLine', _("Draw Poly-Line"), 'Create',
               args = 'PolyLineCreator', bitmap = pixmaps.CreatePoly,
               value_on = 'Create:PolyLineCreator',
               sensitive_cb = 'can_create')
    AddModeCmd('CreateSimpleText', _("Draw Text"), 'Create',
               args = 'SimpleTextCreator', bitmap = pixmaps.Text,
               value_on = 'Create:SimpleTextCreator',
               sensitive_cb = 'can_create')
    def Create(self, gfx_name = None):
        self.begin_transaction()
        if gfx_name is None:
            gfx_name = self.create_type
        self.enter_mode(self.modes.creation_mode, gfx_name)
        self.end_transaction()

    def creation_enter(self, gfx_name):
        self.create_creator = getattr(Sketch, gfx_name)
        self.create_type = gfx_name
        self.push_static_cursor(const.CurCreate)
        self.mode.text = self.create_creator.creation_text

    def creation_begin(self, p, button, state):
        # Begin creating an instance of self.create_creator.
        if __debug__:
            self.check_transaction()
        if self.create_creator is None:
            raise CanvasError('no create_creator in creation mode')
        self.begin_creator(self.create_creator, p, button, state)

    def begin_creator(self, creator, p, button, state):
        # Begin creating an instance of creator
        # also used by zoom_mode
        self.hide_handles()
        if self.current is not None:
            self.current.Hide(self.invgc)
        snapped = self.snap_point(p)
        self.current = creator(snapped)
        self.set_correction(self.current.ButtonDown(snapped, button, state))
        self.current.Show(self.invgc)
        self.start_drag = 1
        self.dragging = 0


    def creation_end(self, p, button, state, force_stop = stop_continue):
        if __debug__:
            self.check_transaction()
        if self.current is None:
            # current might be none if the user ends creation before
            # she's begun creating something (i.e. clicking button-2
            # immediately after selecting CreateCurve)
            self.creation_cancel()
            return
        self.current.ButtonUp(self.correct_and_snap(p), button, state)
        self.do_end_creation(force_stop, set_mode = 1)

    def do_end_creation(self, force_stop = stop_regular, set_mode = 0):
        if __debug__:
            self.check_transaction()
        self.pop_cursor_state()
        obj = self.current
        obj.Hide(self.invgc)
        self.current = None
        was_ok = 1

        if force_stop:
            self.create_creator = None
            was_ok = obj.EndCreation()
        else:
            self.create_creator = obj.ContinueCreation()
        if self.create_creator is None:
            self.start_drag = 0
            self.dragging = 0
            if preferences.creation_is_temporary:
                new_mode = self.SelectionMode
            else:
                new_mode = self.Create
            if was_ok:
                self.document.Insert(obj.CreatedObject())
                # switch to edit mode if the new object is a text object.
                # There should be a better way to achieve this
                if obj.is_Text:
                    new_mode = self.EditMode
            else:
                self.document.SelectNone()
            if set_mode:
                new_mode()
        else:
            self.push_static_cursor(const.CurCreate)
            self.current = obj
            obj.Show(self.invgc)

    def creation_exit(self, set_mode = 0):
        if self.current is not None:
            self.do_end_creation(set_mode = set_mode)

    def creation_cancel(self):
        self.dragging = 0
        self.start_drag = 0
        if self.current is not None:
            self.current.Hide(self.invgc)
            self.current = None
        self.create_creator = None
        self.SelectionMode()


    #
    #	Selection and Edit mode
    #

    # two methods shared by the selection and edit modes
    def begin_edit_object(self, p, button, state, handle = None):
        # begin to edit OBJ
        self.current = self.document
        if handle is not None:
            self.current.SelectHandle(handle, SelectDrag)
        else:
            self.current.SelectPointPart(p, self.hitgc, SelectDrag)
        self.hide_handles()
        self.set_correction(self.current.ButtonDown(p, button, state))
        self.current.Show(self.invgc, 1)

    def stop_edit_object(self, p, button, state, force_stop = 0):
        if __debug__:
            self.check_transaction()
        if self.current is None:
            return None
        obj = self.current
        p = self.correct_and_snap(p)
        self.current = None
        self.start_drag = 0
        self.dragging = 0
        obj.Hide(self.invgc, 1)
        obj.ButtonUp(p, button, state)
        return obj

    def drag_mouse(self, p, state):
        if self.start_drag:
            # XXX it sometimes happens that self.start_pos has not been
            # set yet. Why?
            if abs(self.start_pos[0] - p) * self.scale > 3:
                apply(self.mode.start_drag, self.start_pos)
                self.start_drag = 0
            else:
                return
        self.dragging = 1
        if self.current is not None and (state & self.current.drag_mask):
            # if something is being edited, hide it and show it at new
            # position
            self.current.Hide(self.invgc, 1)
            self.current.MouseMove(self.correct_and_snap(p), state)
            self.current.Show(self.invgc, 1)

    def selection_rect(self, p, button, state):
        self.current = SelectionRectangle(p)
        self.set_correction(self.current.ButtonDown(p, button, state))
        self.current.Show(self.invgc)

    #
    #	Selection
    #

    # enter selection mode
    AddModeCmd('SelectionMode', _("Selection Mode"), value_on = 'Select',
               bitmap = pixmaps.SelectionMode)
    def SelectionMode(self):
        self.begin_transaction()
        self.document.SetMode(SelectionMode)
        self.end_transaction()

    def selection_mode(self):
        self.enter_mode(self.modes.selection_mode)

    def selection_enter(self):
        self.create_creator = None
        self.set_active_cursor(self.set_handle_cursor, const.CurStd)

    def selection_down(self, p, button, state):
        self.start_pos = (p, button, state)
        self.start_drag = 1
        self.dragging = 0
        self.hide_handles()

    def selection_start_drag(self, p, button, state):
        if selection_type(state) == SelectSet:
            handle = self.handle_hit(p)
            if handle is not None or self.document.SelectionHit(p, self.hitgc):
                # something is already selected and the user pressed the
                # button somewhere on the selection. Edit the current
                # object(s)
                self.begin_edit_object(p, button, state, handle)
                return
        # there's no selection or the user pressed the button somewhere
        # outside the current selection.

        # test for a guide line
        guide = self.document.SelectPoint(p, self.hitgc, SelectGuide)
        if guide is not None:
            self.current = guide
            self.set_correction(self.current.ButtonDown(p, button, state))
            self.current.Show(self.invgc)
        else:
            # Make a new selection
            self.selection_rect(p, button, state)

    def selection_click(self, p, button, state):
        type = selection_type(state)
        if type == SelectSet and self.document.SelectionHit(p, self.hitgc):
            self.document.ToggleSelectionBehaviour()
        else:
            self.document.SelectPoint(p, self.hitgc, type)

    def selection_up(self, p, button, state, force_stop = 0):
        if not self.dragging:
            self.selection_click(p, button, state)
        else:
            obj = self.stop_edit_object(p, button, state, force_stop)
            if obj is not None:
                if isinstance(obj, SelectionRectangle):
                    self.document.SelectRect(obj.bounding_rect,
                                             selection_type(state))
                elif obj.is_GuideLine:
                    # a guideline
                    x = self.last_event.x
                    y = self.last_event.y
                    if (0 <= x < self.winfo_width()
                        and 0 <= y <= self.winfo_height()):
                        self.document.MoveGuideLine(obj, obj.drag_cur)
                    else:
                        self.document.RemoveGuideLine(obj)

        self.show_handles()
        self.current = None
        self.start_drag = self.dragging = 0

    def selection_cancel(self):
        if self.dragging:
            if self.current is not None:
                self.current.Hide(self.invgc)
                self.current = None
            self.dragging = 0
        else:
            self.document.SelectNone()
        self.start_drag = 0

    #
    #	Edit mode
    #
    AddModeCmd('EditMode', _("Edit Mode"), bitmap = pixmaps.EditMode,
               value_on = 'Edit')
    def EditMode(self):
        self.begin_transaction()
        self.document.SetMode(EditMode)
        self.end_transaction()

    def edit_mode(self):
        self.enter_mode(self.modes.edit_mode)

    def edit_enter(self):
        self.create_creator = None
        self.set_active_cursor(self.set_handle_cursor, const.CurEdit)

    def edit_down(self, p, button, state):
        self.start_pos = (p, button, state)
        self.start_drag = 1
        self.dragging = 0

    def edit_start_drag(self, p, button, state):
        handle = self.handle_hit(p)
        if handle is None:
            self.hitgc.StartOutlineMode()
            is_hit = self.document.SelectionHit(p, self.hitgc, test_all = 0)
            self.hitgc.EndOutlineMode()
        else:
            is_hit = 1
        if is_hit:
            # something is already selected and the user pressed the
            # button somewhere on the selection. Edit the current object
            self.begin_edit_object(p, button, state, handle)
        else:
            # there's no selection or the user pressed the button
            # somewhere outside the current selection.

            # test for a guide line
            guide = self.document.SelectPoint(p, self.hitgc, SelectGuide)
            if guide is not None:
                # edit the guide line
                self.current = guide
                self.set_correction(self.current.ButtonDown(p, button, state))
                self.current.Show(self.invgc)
            else:
                # Make a new selection
                self.selection_rect(p, button, state)

    def edit_click(self, p, button, state):
        handle = self.handle_hit(p)
        if handle is not None:
            self.document.SelectHandle(handle, selection_type(state))
        else:
            self.hitgc.StartOutlineMode()
            is_hit = self.document.SelectionHit(p, self.hitgc, test_all = 0)
            self.hitgc.EndOutlineMode()
            if is_hit:
                self.document.SelectPointPart(p, self.hitgc)
            else:
                self.document.SelectPoint(p, self.hitgc)

    def edit_up(self, p, button, state, force_stop = stop_continue):
        if not self.dragging:
            self.edit_click(p, button, state)
        else:
            obj = self.stop_edit_object(p, button, state, force_stop)
            if obj.__class__ == SelectionRectangle:
                self.document.SelectRectPart(obj.bounding_rect,
                                             selection_type(state))
            elif obj.is_GuideLine:
                # a guideline
                x = self.last_event.x
                y = self.last_event.y
                if 0 <= x < self.winfo_width() and 0<= y <=self.winfo_height():
                    self.document.MoveGuideLine(obj, obj.drag_cur)
                else:
                    self.document.RemoveGuideLine(obj)
        self.current = None
        self.show_handles()
        self.start_drag = 0
        self.dragging = 0

    def edit_cancel(self):
        if self.dragging:
            self.current.Hide(self.invgc)
            self.current = None
            self.dragging = 0
        self.show_handles()
        self.start_drag = 0

    #
    #	the standard mouse_move method for the modes
    #

    def drag_to(self, p, state):
        self.dragging = 1
        if self.current is not None and (state & self.current.drag_mask):
            # if something is being created/edited, hide it and show it
            # at new position
            self.current.Hide(self.invgc, 1)
            self.current.MouseMove(self.correct_and_snap(p), state)
            self.current.Show(self.invgc, 1)



    #
    #	Temporary modes
    #

    #
    #		Place object mode
    #

    def PlaceObject(self, object, text = None):
        self.begin_transaction()
        if self.IsCreationMode():
            self.creation_exit(set_mode = 1)
        self.enter_mode(self.modes.place_mode, object, text)
        self.end_transaction()

    def place_enter(self, object, text):
        #self.create_creator = None
        self.push_static_cursor(const.CurPlace)
        self.place_object = object
        self.place_text = text
        self.start_drag = 1

    def place_begin(self, p, button, state):
        if self.start_drag:
            self.place_start_drag(p, state)

    def place_start_drag(self, p, state):
        if self.place_object.is_GuideLine:
            self.place_object.SetPoint(p)
            self.current = self.place_object
        else:
            self.place_object.SetLowerLeftCorner(p)
            self.current = SelectionRectangle(self.place_object.coord_rect,
                                              anchor = self.place_object.LayoutPoint())
            self.current.Select()
        # selection rect doesn't use button and state:
        self.set_correction(self.current.ButtonDown(p, 0, state))
        self.current.Show(self.invgc)
        self.dragging = 1
        self.start_drag = 0

    def place_drag(self, p, state):
        if self.start_drag:
            self.place_start_drag(p, state)
        self.dragging = 1
        if self.current is not None:
            # if something is being placed, hide it and show it at new
            # position
            self.current.Hide(self.invgc, 1)
            state = state | const.Button1Mask
            self.current.MouseMove(self.correct_and_snap(p), state)
            self.current.Show(self.invgc, 1)

    def place_cancel(self):
        self.pop_cursor_state()
        if self.current is not None:
            self.current.Hide(self.invgc)
        self.current = None
        self.place_object = None
        self.place_text = None
        self.dragging = 0
        self.start_drag = 0

    def place_end(self, p, button, state, force_stop = stop_continue):
        self.pop_cursor_state()
        if self.current is None:
            return
        rect = self.current
        rect.Hide(self.invgc)
        p = self.correct_and_snap(p)
        rect.ButtonUp(p, button, state)
        self.current = None

        obj = self.place_object
        self.place_object = None
        if obj.is_GuideLine:
            x = self.last_event.x
            y = self.last_event.y
            if (0 <= x < self.winfo_width() and 0 <= y <= self.winfo_height()):
                obj.SetPoint(p)
            else:
                # guide line is outside of the canvas window.
                obj = None
        else:
            obj.SetLowerLeftCorner(rect.start)
        if obj:
            if self.place_text:
                self.document.Insert(obj, self.place_text)
            else:
                self.document.Insert(obj)
        self.place_text = None

    #
    #		Pick object mode
    #

    def PickObject(self, callback, args = ()):
        self.begin_transaction()
        self.enter_mode(self.modes.pick_mode, callback, args)
        self.end_transaction()

    def pick_enter(self, callback, args):
        self.create_creator = None
        self.push_static_cursor(const.CurPick)
        self.pick_object_cb = callback, args

    def pick_begin(self, p, button, state):
        pass

    def pick_cancel(self):
        self.pop_cursor_state()
        self.pick_object_cb = None

    def pick_end(self, p, button, state, force_stop = stop_continue):
        self.pop_cursor_state()
        object = self.document.PickObject(self.hitgc, p)
        cb, args = self.pick_object_cb
        self.pick_object_cb = None
        args = (object,) + args
        apply(cb, args)

    #
    #		Zoom mode
    #

    AddModeCmd('ZoomMode', _("Zoom Area"), bitmap = pixmaps.Zoom,
               value_on = 'Zoom')
    def ZoomMode(self):
        self.begin_transaction()
        self.enter_mode(self.modes.zoom_mode)
        self.end_transaction()

    def zoom_enter(self):
        self.push_static_cursor(const.CurZoom)

    def zoom_begin(self, p, button, state):
        self.begin_creator(SelectionRectangle, p, button, state)

    def zoom_cancel(self):
        self.pop_cursor_state()
        if self.current is not None:
            self.current.Hide(self.invgc)
        self.current = None
        self.dragging = 0
        self.start_drag = 0

    def zoom_end(self, p, button, state, force_stop = stop_continue):
        self.pop_cursor_state()
        obj = None
        if self.current is not None:
            obj = self.current
            obj.Hide(self.invgc)
            obj.ButtonUp(self.correct_and_snap(p), button, state)
            self.current = None

        zoom_out = state & const.ControlMask

        self.save_viewport()
        if self.dragging and obj is not None:
            epsilon = 1e-10
            rect = obj.bounding_rect
            rw = rect.right - rect.left
            rh = rect.top - rect.bottom
            width = self.tkwin.width
            height = self.tkwin.height
            if abs(rw) < epsilon or abs(rh) < epsilon:
                return
            scalex = width / rw
            scaley = height / rh
            if zoom_out:
                scale = (self.scale ** 2) / max(scalex, scaley)
                x, y = self.DocToWin(rect.center())
                center = rect.center() + Point(width / 2 - x,
                                               -height / 2 + y) / scale
            else:
                scale = min(scalex, scaley, self.max_scale)
                center = rect.center()
        else:
            if zoom_out:
                scale = 0.5 * self.scale
            else:
                scale = 2 * self.scale
            center = p
        self.SetScale(scale / self.pixel_per_point, do_center = 0)
        self.SetCenter(center, move_contents = 0)

        self.start_drag = 0
        self.dragging = 0

    #
    #	Other mode related methods
    #

    AddCmd('ToggleMode', _("Toggle Mode"), key_stroke = (' ', 'C-space'),
           subscribe_to = None)
    def ToggleMode(self):
        self.begin_transaction()
        try:
            if self.IsCreationMode():
                self.SelectionMode()
            elif self.IsSelectionMode():
                self.EditMode()
            else:
                # go to selection mode as default
                self.SelectionMode()
        finally:
            self.end_transaction()

    def set_mode_from_doc(self, *args, **kwargs):
        mode = self.document.Mode()
        if mode == SelectionMode:
            self.selection_mode()
        else:
            self.edit_mode()
        self.update_object_keymap()

    def IsSelectionMode(self):
        return self.mode == self.modes.selection_mode

    def IsEditMode(self):
        return self.mode == self.modes.edit_mode

    def IsCreationMode(self):
        return self.mode == self.modes.creation_mode

    def ModeInfoText(self):
        return self.mode.text

    def ModeName(self):
        name = self.mode.name
        if name == 'Create':
            name = name + ':' + self.create_type
        return name



    #
    #	Selection related methods
    #

    def SelectionInfoText(self):
        # Return a string describing the currently selected objects
        return self.document.SelectionInfoText()


    #
    #	correction, snapping
    #

    def set_correction(self, correct):
        if type(correct) == TupleType:
            correct, rect = correct
        else:
            rect = None
            if correct is None:
                correct = Point(0, 0)
        self.correction = correct
        self.correction_rect = rect

    snap_update_installed = 0
    def update_snap_points(self):
        if self.snap_to_object and not self.snap_update_installed:
            self.after_idle(self.idle_update_snap_points)
            self.snap_update_installed = 1

    def extract_snap_points(self, obj):
        self.snap_points[0:0] = obj.GetSnapPoints()

    def idle_update_snap_points(self):
        self.snap_update_installed = 0
        self.snap_points = []
        self.document.WalkHierarchy(self.extract_snap_points, visible = 1,
                                    printable = 0)
        self.snap_points.sort()

    def correct_and_snap(self, point):
        point = point - self.correction
        points = [point]
        if self.correction_rect and self.snap_correction_rect:
            l, b, r, t = self.correction_rect.translated(point)
            points = points + [Point(l,b), Point(l,t), Point(r,b), Point(r,t)]

        if self.dragging and self.start_pos \
           and self.snap_move_relative:
            start_pos = point - self.start_pos[0] + self.correction
            x, y = self.document.GridGeometry()[:2]
            points.append(Point(start_pos.x - x, start_pos.y - y))

        mindist = 1e100
        result = point
        #print points
        for p in points:
            dist, snapped = self.snap_point_dist(p)
            if dist < mindist:
                mindist = dist
                result = point - p + snapped

        self.set_current_pos(result)
        return result

    def snap_point(self, p):
        dist, p = self.snap_point_dist(p)
        return p

    def snap_point_dist(self, p):
        maxdist = preferences.max_snap_distance / self.scale
        pgrid = pobj = pguide = pmax = (maxdist, p)
        if self.snap_to_grid:
            pgrid = self.document.SnapToGrid(p)
        if self.snap_to_guide:
            pgh, pgv, pguide = self.document.SnapToGuide(p, maxdist)
            if (self.current is None
                or isinstance(self.current, SelectionRectangle)
                or not self.current.is_GuideLine):
                # We're not dragging a guideline, so snap to guide-lines
                # or to guide-objects. Otherwise, only snap to guide
                # objects
                pguide = min(pgh, pgv, pguide)
            if pguide == pgh or pguide == pgv:
                dist, (x, y) = pguide
                if x is None:
                    if pgv[0] < maxdist:
                        x = pgv[-1][0]
                        dist = dist + pgv[0] - maxdist
                    else:
                        x = p.x
                else:
                    if pgh[0] < maxdist:
                        y = pgh[-1][1]
                        dist = dist + pgh[0] - maxdist
                    else:
                        y = p.y
                pguide = dist, Point(x, y)
        if self.snap_to_object and self.snap_points:
            x, y = p
            mindist = 1e100;
            xlow = x - maxdist; ylow = y - maxdist
            xhigh = x + maxdist; yhigh = y + maxdist
            points = self.snap_points
            ilow = 0; ihigh = len(points)
            while ilow < ihigh:
                imid = (ilow + ihigh) / 2
                if points[imid].x > xlow:
                    ihigh = imid
                else:
                    ilow = imid + 1
            for idx in range(ilow, len(points)):
                pmin = points[idx]
                if pmin.x > xhigh:
                    break
                if ylow < pmin.y < yhigh:
                    dist = max(abs(pmin.x - x), abs(pmin.y - y))
                    if dist < mindist:
                        pobj = pmin
                        mindist = dist
            if type(pobj) != TupleType:
                pobj = (abs(pobj - p), pobj)

        result = min(pgrid, pguide, pobj, pmax)
        return result

    AddCmd('ToggleSnapToGrid', _("Snap to Grid"), bitmap = pixmaps.GridOn,
           value = 0, value_cb = 'IsSnappingToGrid', is_check = 1)
    def ToggleSnapToGrid(self):
        self.begin_transaction()
        try:
            self.snap_to_grid = not self.snap_to_grid
            self.issue_state()
        finally:
            self.end_transaction()

    def IsSnappingToGrid(self):
        return self.snap_to_grid


    AddCmd('ToggleSnapToObjects', _("Snap to Objects"),
           value = 0, value_cb = 'IsSnappingToObjects', is_check = 1)
    def ToggleSnapToObjects(self):
        self.begin_transaction()
        try:
            self.snap_to_object = not self.snap_to_object
            self.snap_points = ()
            self.update_snap_points()
            self.issue_state()
        finally:
            self.end_transaction()

    def IsSnappingToObjects(self):
        return self.snap_to_object

    AddCmd('ToggleSnapToGuides', _("Snap to Guides"),
           value = 0, value_cb = 'IsSnappingToGuides', is_check = 1)
    def ToggleSnapToGuides(self):
        self.begin_transaction()
        try:
            self.snap_to_guide = not self.snap_to_guide
            self.issue_state()
        finally:
            self.end_transaction()

    def IsSnappingToGuides(self):
        return self.snap_to_guide

    AddCmd('ToggleSnapBoundingRect', _("Snap Bounding Rect"),
           value = 0, value_cb = 'IsSnappingBoundingRect', is_check = 1)
    def ToggleSnapBoundingRect(self):
        self.begin_transaction()
        try:
            self.snap_correction_rect = not self.snap_correction_rect
            self.issue_state()
        finally:
            self.end_transaction()

    def IsSnappingBoundingRect(self):
        return self.snap_correction_rect

    AddCmd('ToggleSnapMoveRelative', _("Snap Move Relative"),
           value = 0, value_cb = 'IsSnappingRelative', is_check = 1)
    def ToggleSnapMoveRelative(self):
        self.begin_transaction()
        try:
            self.snap_move_relative = not self.snap_move_relative
            self.issue_state()
        finally:
            self.end_transaction()

    def IsSnappingRelative(self):
        return self.snap_move_relative

    def SnapInfoText(self):
        # NLS might make problems here
        snap = []
        if self.snap_to_grid:
            snap.append(_("Grid"))
        if self.snap_to_object:
            snap.append(_("Objects"))
        if self.snap_to_guide:
            snap.append(_("Guide"))
        if snap:
            return _("Snap: ") + string.join(snap, '/')
        return _("No Snap")

    #
    #   Crosshairs
    #

    def init_cross_hairs(self):
        self.crosshairs = 0
        self.crosshairs_visible = 0
        self.crosshairs_pos = ()
        self.crosshairs_drawn = 0

    def draw_crosshairs(self, pos):
        x, y = self.DocToWin(pos)
        width = self.tkwin.width
        height = self.tkwin.height
        self.invgc.gc.DrawLine(0, y, width, y)
        self.invgc.gc.DrawLine(x, 0, x, height)
        self.crosshairs_pos = pos

    def show_crosshairs(self, force = 0):
        if self.crosshairs and self.crosshairs_visible:
            if not self.crosshairs_drawn or force:
                self.draw_crosshairs(self.current_pos)
            self.crosshairs_drawn = 1

    def hide_crosshairs(self):
        if self.crosshairs_drawn:
            self.draw_crosshairs(self.crosshairs_pos)
        self.crosshairs_drawn = 0

    AddCmd('ToggleCrosshairs', _("Crosshairs"), key_stroke = 'F2',
           value = 0, value_cb = 'IsShowingCrosshairs', is_check = 1)
    def ToggleCrosshairs(self):
        self.begin_transaction()
        try:
            self.hide_crosshairs()
            self.crosshairs = not self.crosshairs
            self.show_crosshairs()
            self.issue_state()
        finally:
            self.end_transaction()

    def IsShowingCrosshairs(self):
        return self.crosshairs



    #
    #	Handles
    #

    def init_handles(self):
        self.handle_points = []
        self.handle_funcs = []
        self.handles_drawn = 0

    handle_update_installed = 0
    def update_handles(self):
        self.hide_handles()
        if not self.handle_update_installed:
            self.after_idle(self.idle_update_handles)
        self.handle_update_installed = 1

    def idle_update_handles(self):
        self.handle_update_installed = 0
        self.set_handles(self.document.GetSelectionHandles())

    def set_handles(self, handles):
        from Sketch.const import HandleLine, Handle_Pixmap, Handle_Caret, \
             Handle_SmallOpenRectList
        points = []
        funcs = []
        used = {}
        if self.gcs_initialized:
            factor = self.gc.LengthToDoc(8)
        else:
            factor = 1

        for handle in handles:
            handle_type = handle.type
            p = handle.p
            cursor = handle.cursor

            if handle.offset is not None:
                offset = handle.offset
                p = p + Point(offset[0] * factor, offset[1] * factor)

            if handle_type == HandleLine:
                funcs.append((self.invgc.DrawHandleLine, (p, handle.p2)))
            elif handle_type == Handle_Pixmap:
                if cursor:
                    points.append(self.DocToWin(p) + (cursor, handle))
                funcs.append((self.draw_handle_funcs[handle_type],
                              (p, handle.pixmap)))
            elif handle_type == Handle_Caret:
                funcs.append((self.invgc.DrawCaretHandle, (p, handle.p2)))
            elif handle_type == Handle_SmallOpenRectList:
                p = handle.list
                if p:
                    pts = map(self.DocToWin, p)
                    last = pts[-1]
                    for idx in range(len(p) - 2, -1, -1):
                        if pts[idx] == last:
                            del p[idx]
                        else:
                            last = pts[idx]
                    funcs.append((self.draw_handle_funcs[handle_type], (p, 0)))
            else:
                win = self.DocToWin(p)
                if cursor:
                    points.append(win + (cursor, handle))
                if not used.has_key(win):
                    funcs.append((self.draw_handle_funcs[handle_type],
                                  (p, handle_type & 1)))
                    used[win] = 0

        self.hide_handles()
        self.handle_points = points
        self.handle_funcs  = funcs
        self.show_handles()

    def show_handles(self, force = 0):
        if __debug__:
            pdebug('handles',
                   'show_handles: drawn = %d, force = %d, update = %d',
                   self.handles_drawn, force, self.handle_update_installed)
        if not self.handle_update_installed\
           and (not self.handles_drawn or force):
            self.draw_handles()
            self.handles_drawn = 1

    def hide_handles(self):
        if __debug__:
            pdebug('handles', 'hide_handles: drawn = %d', self.handles_drawn)
        if self.handles_drawn:
            self.draw_handles()
            self.handles_drawn = 0

    def draw_handles(self):
        for f, args in self.handle_funcs:
            apply(f, args)


    handle_hit_radius = 4
    def set_handle_cursor(self, x, y):
        dist = self.handle_hit_radius
        for xp, yp, cursor, handle in self.handle_points:
            if abs(xp - x) < dist and abs(yp - y) < dist:
                self.set_window_cursor(cursor)
                break
        else:
            cursor = self.cursor_shape
            if preferences.active_cursor:
                object = self.document.PickActiveObject(self.hitgc,
                                                        self.win_to_doc(x, y))
                if object is not None:
                    if object.is_GuideLine:
                        if object.horizontal:
                            cursor = const.CurHGuide
                        else:
                            cursor = const.CurVGuide
                    elif self.IsSelectionMode():
                        cursor = const.CurMove
            self.set_window_cursor(cursor)

    def handle_hit(self, p):
        x, y = self.DocToWin(p)
        dist = self.handle_hit_radius
        handle_points = self.handle_points
        for idx in range(len(handle_points)):
            xp, yp, cursor, handle = handle_points[idx]
            if abs(xp - x) < dist and abs(yp - y) < dist:
                handle.index = idx
                return handle
        return None

    #
    #	Viewport- and related methods
    #
    #	extend some Viewport methods to handle handles and to issue VIEW
    #	whenever the displayed area changes
    #

    AddCmd('ForceRedraw', _("Redraw"), key_stroke = ('Alt+R', 'M-r'), subscribe_to = None)


    def set_origin(self, xorg, yorg, move_contents = 1):
        self.begin_transaction()
        try:
            #self.hide_handles()
            SketchView.set_origin(self, xorg, yorg,
                                  move_contents = move_contents)
            self.queue_update_handles()
        finally:
            self.end_transaction()

    def SetScale(self, scale, do_center = 1):
        # Set current scale
        self.begin_transaction()
        try:
            self.hide_handles() # XXX: really necessary ?
            SketchView.SetScale(self, scale, do_center = do_center)
            self.queue_update_handles()
        finally:
            self.end_transaction()

    def ZoomFactor(self, factor):
        self.SetScale(self.scale * factor)
    AddCmd('ZoomIn', _("Zoom In"), 'ZoomFactor', args = 2.0,
           key_stroke = '>')
    AddCmd('ZoomOut', _("Zoom Out"), 'ZoomFactor', args = 0.5,
           key_stroke = '<')



    # add commands for inherited methods
    AddCmd('ScrollYPages', 'Page Up', args = -1, key_stroke = 'Prior',
           subscribe_to = None)
    AddCmd('ScrollYPages', 'Page Down', args = +1, key_stroke = 'Next',
           subscribe_to = None)

    # scrolling with the cursor keys
    AddCmd('ScrollYPages', '', args = -1, key_stroke = 'C-Up',
           subscribe_to = None)
    AddCmd('ScrollYPages', '', args = +1, key_stroke = 'C-Down',
           subscribe_to = None)
    AddCmd('ScrollXPages', '', args = -1, key_stroke = 'C-Left',
           subscribe_to = None)
    AddCmd('ScrollXPages', '', args = +1, key_stroke = 'C-Right',
           subscribe_to = None)

    #	other view related methods

    AddCmd('FitToWindow', _("Fit to Window"), key_stroke = ('Shift+F4', 'S-F4'),
           subscribe_to = None)
    AddSelCmd('FitSelectedToWindow', _("Fit Selected to Window"),
              'FitToWindow', args = 1, key_stroke = ('Ctrl+F4', 'C-F4'))
    def FitToWindow(self, selected_only = 0, save_viewport = 1):
        self.begin_transaction()
        try:
            self.hide_handles() # XXX: really necessary ?
            SketchView.FitToWindow(self, selected_only = selected_only,
                                   save_viewport = save_viewport)
        finally:
            self.end_transaction()

    AddCmd('FitPageToWindow', _("Fit Page to Window"), key_stroke = 'F4',
           subscribe_to = None)
    def FitPageToWindow(self, save_viewport = 1):
        self.begin_transaction()
        try:
            self.hide_handles()	 # XXX: really necessary ?
            SketchView.FitPageToWindow(self, save_viewport = save_viewport)
        finally:
            self.end_transaction()

    def CanRestoreViewport(self):
        return len(self.viewport_ring)

    AddCmd('RestoreViewport', _("Restore Previous View"), key_stroke = 'F3',
           subscribe_to = VIEW, sensitive_cb = 'CanRestoreViewport')
    def RestoreViewport(self):
        if self.viewport_ring:
            self.begin_transaction()
            try:
                self.restore_viewport()
            finally:
                self.end_transaction()

    AddCmd('ToggleOutlineMode', _("Outline"), key_stroke = ('Shift+F9', 'S-F9'),
           value = 0, value_cb = 'IsOutlineMode', subscribe_to = VIEW,
           is_check = 1)

    AddCmd('TogglePageOutlineMode', _("Draw Page Outline"),
           value = 0, value_cb = 'IsPageOutlineMode', subscribe_to = VIEW,
           is_check = 1)

    #
    #
    #

    def unsubscribe_doc(self):
        if self.document is not None:
            self.document.Unsubscribe(SELECTION,self.selection_changed)
            self.document.Unsubscribe(EDITED,self.doc_was_edited)
            self.document.Unsubscribe(MODE, self.set_mode_from_doc)
        SketchView.unsubscribe_doc(self)

    def subscribe_doc(self):
        self.document.Subscribe(SELECTION, self.selection_changed)
        self.document.Subscribe(EDITED,self.doc_was_edited)
        self.document.Subscribe(MODE, self.set_mode_from_doc)
        SketchView.subscribe_doc(self)

    def SetDocument(self, doc):
        self.begin_transaction()
        try:
            SketchView.SetDocument(self, doc)
            self.SelectionMode()
            self.hide_handles()
            self.issue_selection()
            self.issue_mode()
            self.update_handles()
            self.update_snap_points()
        finally:
            self.end_transaction()
            self.init_viewport_ring()


    #
    #	Fill
    #

    AddSelCmd('FillSolid', _("Set Fill Color..."))
    def FillSolid(self, col = None):
        # Set the fill style of the currently selected objects to a
        # solid fill of color COL. If COL is None let the user
        # interactively select a color.
        if col is None:
            import colordlg
            current_color = self.document.CurrentFillColor()
            if current_color is None:
                current_color = StandardColors.white
            col = colordlg.GetColor(self, current_color)
            if not col:
                return
        from Sketch import SolidPattern
        import styledlg
        styledlg.set_properties(self.master, self.document,
                                _("Set Fill Color"), 'fill',
                                {'fill_pattern' : SolidPattern(col)})


    #
    #	LineStyle
    #
    def LineColor(self, color):
        # Set the line color of the currently selected objects to COLOR
        # XXX: should be removed; only needed by skapp to connect
        # palette with canvas. (Dec 97)
        if self.document.CountSelected() > 1:
            self.call_document_method('SetLineColor', color)
        else:
            from Sketch import SolidPattern
            import styledlg
            styledlg.set_properties(self.master, self.document,
                                    _("Set Line Color"), 'line',
                                    {'line_pattern' : SolidPattern(color)})

