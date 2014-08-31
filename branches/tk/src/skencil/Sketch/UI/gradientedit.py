# Sketch - A Python-based interactive drawing program
# Copyright (C) 1998, 1999, 2000, 2002 by Bernhard Herzog
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

import PIL.Image
import X, pax

from Sketch import _, Publisher, SketchError, _sketch
from Sketch import Blend, CreateRGBColor, MultiGradient
from Sketch.const import DROP_COLOR
from Sketch.warn import pdebug
from Sketch.Graphics import color

from Tkinter import Frame, Button
from Tkinter import BOTTOM, LEFT, RIGHT, BOTH
from tkext import PyWidget, MenuCommand, UpdatedMenu
import tkext

from colordlg import GetColor
from sketchdlg import SKModal

import skpixmaps
pixmaps = skpixmaps.PixmapTk



handle_height = 8

class GradientView(PyWidget, Publisher):

    accept_drop = (DROP_COLOR,)

    def __init__(self, master, width, height, gradient, **kw):
        image = PIL.Image.new('RGB', (width, height))
        self.orig_x = handle_height / 2
        if not kw.has_key('width'):
            kw["width"] = width + handle_height
        if not kw.has_key('height'):
            kw["height"] = height + handle_height
        apply(PyWidget.__init__, (self, master), kw)
        self.set_gradient(gradient)
        self.update_pending = 0
        self.dragging = 0
        self.drag_idx = 0
        self.drag_start = 0
        self.drag_min = self.drag_max = 0.0
        self.gc_initialized = 0
        self.image = image
        self.ximage = None
        self.context_menu = None
        self.bind('<ButtonPress-3>', self.PopupContextMenu)
        self.bind('<ButtonPress>', self.ButtonPressEvent)
        self.bind('<Motion>', self.PointerMotionEvent)
        self.bind('<ButtonRelease>', self.ButtonReleaseEvent)

    def __del__(self):
        pdebug('__del__', '__del__', self)

    def MapMethod(self):
        if not self.gc_initialized:
            self.init_gc()
            self.tk.call(self._w, 'motionhints')
            self.gc_initialized = 1

    def DestroyMethod(self):
        if self.context_menu is not None:
            self.context_menu.clean_up()
        self.context_menu = None
        PyWidget.DestroyMethod(self)

    def init_gc(self):
        self.gc = self.tkwin.GetGC()
        self.visual = color.skvisual
        w = self.tkwin
        width, height = self.image.size
        depth = self.visual.depth
        if depth > 16:
            bpl = 4 * width
        elif depth > 8:
            bpl = ((2 * width + 3) / 4) * 4
        elif depth == 8:
            bpl = ((width + 3) / 4) * 4
        else:
            raise SketchError('unsupported depth for images')
        self.ximage = w.CreateImage(depth, X.ZPixmap, 0, None, width, height,
                                    32, bpl)
        self.set_image(self.image)

    def set_image(self, image):
        self.image = image
        if self.ximage:
            ximage = self.ximage
            _sketch.copy_image_to_ximage(self.visual, image.im, ximage,
                                         0, 0, ximage.width, ximage.height)
            self.UpdateWhenIdle()

    def ResizedMethod(self, width, height):
        pass

    def set_gradient(self, gradient):
        gradient = gradient.Colors()
        self.gradient = []
        for pos, color in gradient:
            self.gradient.append((pos, tuple(color)))

    def reverse(self):
        for i in range(len(self.gradient)):
            self.gradient[i]=(1 - self.gradient[i][0], self.gradient[i][1])
        self.gradient.reverse()
        self.UpdateWhenIdle()

    def x_to_idx(self, x):
        width = self.ximage.width
        w2 = handle_height / 2
        orig_x = self.orig_x
        for i in range(len(self.gradient)):
            if abs(x - orig_x - self.gradient[i][0] * width) < w2:
                return i
        return -1

    def ButtonPressEvent(self, event):
        if not self.dragging:
            self.drag_idx = self.x_to_idx(event.x)
            if self.drag_idx < 0:
                return
            if self.drag_idx == 0:
                self.gradient.insert(0, self.gradient[0])
                self.drag_idx = self.drag_idx + 1
            if self.drag_idx == len(self.gradient) - 1:
                self.gradient.append(self.gradient[-1])
            self.drag_start = event.x, self.gradient[self.drag_idx][0]
            if self.drag_idx > 0:
                self.drag_min = self.gradient[self.drag_idx - 1][0]
            else:
                self.drag_min = 0.0
            if self.drag_idx < len(self.gradient) - 1:
                self.drag_max = self.gradient[self.drag_idx + 1][0]
            else:
                self.drag_max = 1.0

        self.dragging = self.dragging + 1

    def ButtonReleaseEvent(self, event):
        if self.dragging:
            self.dragging = self.dragging - 1
            self.move_to(event.x)
            if self.drag_idx == 1 and \
               self.gradient[0][0] == self.gradient[1][0]:
                del self.gradient[0]
            elif self.drag_idx == len(self.gradient) - 2 and \
                 self.gradient[-1][0] == self.gradient[-2][0]:
                del self.gradient[-1]

    def PointerMotionEvent(self, event):
        if self.dragging:
            x = self.tkwin.QueryPointer()[4]
            self.move_to(x)

    def move_to(self, x):
        start_x, start_pos = self.drag_start
        pos = x - start_x + start_pos * self.ximage.width
        pos = float(pos) / self.ximage.width
        if pos < self.drag_min:
            pos = self.drag_min
        if pos > self.drag_max:
            pos = self.drag_max
        color = self.gradient[self.drag_idx][-1]
        self.gradient[self.drag_idx] = (pos, color)
        self.UpdateWhenIdle()

    def PopupContextMenu(self, event):
        self.context_idx = self.x_to_idx(event.x)
        self.context_pos = (event.x - self.orig_x) / float(self.ximage.width)
        if self.context_menu is None:
            items = [MenuCommand(_("Set Handle Color"), self.set_handle_color,
                                 sensitivecb = self.can_set_handle_color),
                     MenuCommand(_("Delete Handle"), self.delete_handle,
                                 sensitivecb = self.can_delete_handle),
                     MenuCommand(_("Insert Handle"), self.insert_handle,
                                 sensitivecb = self.can_insert_handle)]
            self.context_menu = UpdatedMenu(self, items)
        self.context_menu.Popup(event.x_root, event.y_root)

    def delete_handle(self):
        if 0 < self.context_idx < len(self.gradient) - 1:
            del self.gradient[self.context_idx]
            self.UpdateWhenIdle()

    def can_delete_handle(self):
        return 0 < self.context_idx < len(self.gradient) - 1

    def insert_handle(self):
        gradient = self.gradient
        pos = self.context_pos
        if 0.0 <= pos <= 1.0:
            for i in range(len(gradient) - 1):
                if gradient[i][0] < pos < gradient[i + 1][0]:
                    p1, c1 = gradient[i]
                    p2, c2 = gradient[i + 1]
                    color = Blend(apply(CreateRGBColor, c2),
                                  apply(CreateRGBColor, c1),
                                  (pos - p1) / (p2 - p1))
                    gradient.insert(i + 1, (pos, tuple(color)))
                    self.UpdateWhenIdle()
                    break

    def can_insert_handle(self):
        return self.context_idx < 0 and 0.0 <= self.context_pos <= 1.0

    def set_handle_color(self):
        if self.context_idx >= 0:
            pos, color = self.gradient[self.context_idx]
            color = GetColor(self, apply(CreateRGBColor, color))
            if color is not None:
                self.gradient[self.context_idx] = (pos, tuple(color))
                self.UpdateWhenIdle()

    def can_set_handle_color(self):
        return self.context_idx >= 0

    def update_gradient(self):
        _sketch.fill_axial_gradient(self.image.im, self.gradient,
                                    0, 0, self.image.size[0] - 1, 0)
        self.set_image(self.image)

    def UpdateWhenIdle(self):
        if not self.update_pending:
            self.update_pending = 1
            PyWidget.UpdateWhenIdle(self)

    def RedrawMethod(self, region = None):
        if self.update_pending:
            self.update_gradient()
            self.update_pending = 0
        pixmap = self.tkwin.CreatePixmap()
        width = self.ximage.width
        height = self.ximage.height
        startx = handle_height / 2
        self.gc.SetDrawable(pixmap)
        self.tkborder.Fill3DRectangle(pixmap, 0, 0,
                                      self.tkwin.width, self.tkwin.height,
                                      0, pax.TK_RELIEF_FLAT)
        self.gc.PutImage(self.ximage, 0, 0, startx, 0, width, height)

        border = self.tkborder
        win = self.tkwin
        w2 = handle_height / 2
        bot = handle_height + height
        for pos in self.gradient:
            pos = pos[0]
            x = int(pos * width) + startx
            poly = [(x - w2, bot), (x, height), (x + w2, bot)]
            border.Draw3DPolygon(pixmap, poly, -2, pax.TK_RELIEF_SUNKEN)

        self.gc.SetDrawable(self.tkwin)
        pixmap.CopyArea(self.tkwin, self.gc, 0, 0,
                        self.tkwin.width, self.tkwin.height, 0, 0)

    def DropAt(self, x, y, what, data):
        if what == DROP_COLOR:
            idx = self.x_to_idx(x)
            if idx >= 0:
                pos, color = self.gradient[idx]
                self.gradient[idx] = (pos, tuple(data))
                self.UpdateWhenIdle()

    def GetGradient(self):
        result = []
        for pos, color in self.gradient:
            result.append((pos, apply(CreateRGBColor, color)))
        return MultiGradient(result)




gradient_size = (200, 10)

class EditGradientDlg(SKModal):

    title = _("Edit Gradient")

    def __init__(self, master, gradient, **kw):
        self.gradient = gradient
        apply(SKModal.__init__, (self, master), kw)

    def build_dlg(self):
        top = self.top

        frame = Frame(top)
        frame.pack(side = BOTTOM, fill = BOTH, expand = 1)
        button = Button(frame, text = _("Reverse"), command = self.reverse)
        button.pack(side = LEFT, expand = 1)
        button = Button(frame, text = _("OK"), command = self.ok)
        button.pack(side = LEFT, expand = 1)
        button = Button(frame, text = _("Cancel"), command = self.cancel)
        button.pack(side = RIGHT, expand = 1)

        view = GradientView(top, gradient_size[0], gradient_size[1],
                            self.gradient)
        view.pack(side = LEFT)
        self.gradient_view = view

    def reverse(self, *args):
        self.gradient_view.reverse()

    def ok(self, *args):
        self.close_dlg(self.gradient_view.GetGradient())


def EditGradient(master, gradient):
    dlg = EditGradientDlg(master, gradient)
    return dlg.RunDialog(grab = 0)
