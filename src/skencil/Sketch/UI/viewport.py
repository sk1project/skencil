# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2001 by Bernhard Herzog
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Library General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

from Sketch import Trafo, RectType, EmptyRect, InfinityRect
from Sketch.config import preferences
from Sketch.Graphics.papersize import Papersize


class Viewport:

    max_scale = 16
    min_scale = 0.05

    def __init__(self, resolution = None):
        self.hbar = None
        self.vbar = None
        self.hruler = None
        self.vruler = None

        self.base_width = 3000
        self.base_height = 3000
        self.nominal_scale = 1
        self.scale = 1.0
        self.virtual_width = self.base_width
        self.virtual_height =  self.base_height
        self.virtual_x = 0
        self.virtual_y = 0
        self.init_resolution(resolution)
        self.set_page_size(Papersize['A4']) # XXX config
        self.compute_win_to_doc()
        self.clear_rects = []
        self.clear_entire_window = 0

        self.init_viewport_ring()


    def init_resolution(self, resolution):
        if resolution is not None:
            self.pixel_per_point = resolution
        else:
            width = self.winfo_screenwidth()
            width_mm = self.winfo_screenmmwidth()
            pixel_per_point = (width / float(width_mm)) * 25.4 / 72
            self.pixel_per_point = float(pixel_per_point)
        self.max_scale = self.__class__.max_scale * self.pixel_per_point

    #
    #	Coordinate conversions
    #

    def set_page_size(self, (width, height)):
        self.page_width = width
        self.page_height = height

    def compute_win_to_doc(self):
        scale = self.scale
        # virtual coords of ll corner of page
        llx = (self.virtual_width - self.page_width * scale) / 2
        lly = (self.virtual_height + self.page_height * scale) / 2
        self.doc_to_win = Trafo(scale, 0.0, 0.0, -scale,
                                llx - self.virtual_x, lly - self.virtual_y)
        scale = 1.0 / scale
        self.win_to_doc = Trafo(scale, 0.0, 0.0, -scale,
                                (self.virtual_x - llx) * scale,
                                (lly - self.virtual_y) * scale)

    #	document to window coordinates

    def DocToWin(self, *args):
        # returns a tuple of ints
        return apply(self.doc_to_win.DocToWin, args)

    #	window to document coordinates

    def WinToDoc(self, *args):
        return apply(self.win_to_doc, args)

    def LengthToDoc(self, len):
        return len / self.scale

    #
    #	Redraw Parts of the window.
    #

    def clear_area_doc(self, rect):
        # Mark the rectangular area of self, given by RECT in document
        # coordinates, as invalid. The rect is put into a list of rects
        # that have to be cleared via do_clear() once RedrawMethod() is
        # invoked.
        if not self.clear_entire_window:
            if rect is EmptyRect:
                return
            elif rect is InfinityRect:
                self.clear_window()
            elif type(rect) == RectType:
                x1, y1 = self.DocToWin(rect.left, rect.top)
                x2, y2 = self.DocToWin(rect.right, rect.bottom)
                if x1 > x2:
                    t = x1; x1 = x2; x2 = t
                if y1 > y2:
                    t = y1; y1 = y2; y2 = t

                # clip the rect to the window
                if x1 < 0:
                    x1 = 0
                elif x1 > self.tkwin.width:
                    return
                if x2 > self.tkwin.width:
                    x2 = self.tkwin.width
                elif x2 < 0:
                    return
                if y1 < 0:
                    y1 = 0
                elif y1 > self.tkwin.height:
                    return
                if y2 > self.tkwin.height:
                    y2 = self.tkwin.height
                elif y2 < 0:
                    return

                self.clear_rects.append((x1 - 1, y1 - 1,
                                         x2 - x1 + 2, y2 - y1 + 2))
            else:
                # special case: clear a guide line
                p, horizontal = rect
                x, y = self.DocToWin(p)
                if horizontal:
                    self.clear_rects.append((0, y, self.tkwin.width, 1))
                else:
                    self.clear_rects.append((x, 0, 1, self.tkwin.height))
        self.UpdateWhenIdle()

    def clear_window(self, update = 1):
        # Mark the entire window as invalid.
        self.clear_entire_window = 1
        self.clear_rects = []
        if update:
            self.UpdateWhenIdle()

    def do_clear(self, region):
        # Clear all areas marked as invalid by clear_area_doc() or
        # clear_window(). These areas are added to REGION via its
        # UnionRectWithRegion method. This function should be called by
        # RedrawMethod() before any drawing is done.
        if region and not self.clear_entire_window:
            clear_area = self.tkwin.ClearArea
            union = region.UnionRectWithRegion
            for rect in self.clear_rects:
                apply(clear_area, rect + (0,))
                apply(union, rect)
        else:
            self.tkwin.ClearArea(0, 0, 0, 0, 0)
            region = None
        self.clear_entire_window = 0
        self.clear_rects = []
        return region

    #
    #
    #

    def set_origin(self, xorg, yorg, move_contents = 1):
        old_org_x = xo = self.virtual_x
        old_org_y = yo = self.virtual_y
        if xorg != None:
            xo = xorg
        if yorg != None:
            yo = yorg
        offx = round(xo - old_org_x)
        offy = round(yo - old_org_y)
        xo = old_org_x + offx
        yo = old_org_y + offy
        self.virtual_x = xo
        self.virtual_y = yo
        offx = int(offx)
        offy = int(offy)
        if move_contents and (offx or offy):
            self.move_window_contents(offx, offy)
        self.compute_win_to_doc()
        self.update_scrollbars()
        self.update_rulers()


    def move_window_contents(self, offx, offy):
        # Noop here, because moving the window contents requires a gc.
        # The implementation could be as follows:
        #
        #	w = self.tkwin
        #	width = w.width
        #	height = w.height
        #	w.CopyArea(w, self.gc.gc, offx, offy, width, height, 0, 0)
        pass


    #
    #	Managing the displayed area
    #

    def SetCenter(self, center, move_contents = 1):
        # set origin so that center (in doc-coords) is in the center of the
        # widget
        cx, cy = self.DocToWin(center)
        self.set_origin(self.virtual_x + cx - self.tkwin.width / 2,
                        self.virtual_y + cy - self.tkwin.height / 2,
                        move_contents = move_contents)

    def SetScale(self, scale, do_center = 1):
        # Set current scale
        scale = scale * self.pixel_per_point
        if scale > self.max_scale:
            scale = self.max_scale
        elif scale < self.min_scale:
            scale = self.min_scale
        self.scale = scale
        self.nominal_scale = scale / self.pixel_per_point
        width = int(scale * self.base_width)
        height = int(scale * self.base_height)
        self.virtual_width = width
        self.virtual_height = height
        if do_center:
            cx = self.tkwin.width / 2
            cy = self.tkwin.height / 2
            center = self.WinToDoc(cx, cy)

        self.compute_win_to_doc()

        if do_center:
            self.SetCenter(center, move_contents = 0)
        else:
            self.set_origin(0, 0, move_contents = 0)

        self.gc.SetViewportTransform(scale, self.doc_to_win, self.win_to_doc)

        self.clear_window()

    def SetPageSize(self, size):
        self.set_page_size(size)
        self.compute_win_to_doc()

    def Scale(self):
        return self.scale

    #
    #	Some convenient methods
    #

    def zoom_fit_rect(self, rect):
        # set the scale and origin of the canvas so that the document
        # rectangle rect is centered and fills the window (keeping the aspect
        # ratio)
        epsilon = 1e-10

        rw = rect.right - rect.left
        if abs(rw) < epsilon:
            return
        width = self.tkwin.width
        scalex = float(width) / rw

        rh = rect.top - rect.bottom
        if abs(rh) < epsilon:
            return
        height = self.tkwin.height
        scaley = float(height) / rh

        scale = min((scalex, scaley, self.max_scale))

        self.SetScale(scale / self.pixel_per_point, do_center = 0)
        self.SetCenter(rect.center(), move_contents = 0)


    def ZoomInfoText(self):
        # Return a string that describes the current zoom factor in percent.
        # Usually this is displayed in a status bar.
        # NLS
        return "%g%%" % round(100 * self.nominal_scale, 1)


    #
    #	Scrollbar handling
    #

    def ResizedMethod(self, width, height):
        self.update_scrollbars()
        self.update_rulers()

    def SetScrollbars(self, hbar, vbar):
        self.hbar = hbar
        self.vbar = vbar

    def SetRulers(self, hruler, vruler):
        self.hruler = hruler
        self.vruler = vruler

    def update_scrollbars(self):
        w = self.tkwin.width
        h = self.tkwin.height
        if self.hbar:
            vw = float(self.virtual_width)
            min = self.virtual_x / vw
            self.hbar.set(min, min + w / vw)
        if self.vbar:
            vh = float(self.virtual_height)
            min = self.virtual_y / vh
            self.vbar.set(min, min + h / vh)

    def update_rulers(self, force = 0):
        start = self.WinToDoc(0, 0)
        if self.hruler:
            self.hruler.SetRange(start.x, self.scale, force = force)
        if self.vruler:
            self.vruler.SetRange(start.y, self.scale, force = force)

    def xview(self, *args):
        apply(self.tk.call, (self._w, 'xview') + args)

    def yview(self, *args):
        apply(self.tk.call, (self._w, 'yview') + args)

    def ScrollXMove(self, fraction):
        vw = self.virtual_width
        w = self.tkwin.width
        amount = float(w) / vw
        max = 1.0 - amount
        if fraction > max:
            fraction = max
        if fraction < 0:
            fraction = 0
        self.set_origin(fraction * vw, None)

    def ScrollXPages(self, count):
        vw = float(self.virtual_width)
        w = self.tkwin.width
        amount = w / vw
        self.ScrollXMove(self.virtual_x / vw + count * amount)

    def ScrollXUnits(self, count):
        self.set_origin(self.virtual_x + count * 10, None)

    def ScrollYMove(self, fraction):
        vh = self.virtual_height
        h = self.tkwin.height
        amount = float(h) / vh
        max = 1.0 - amount
        if fraction > max:
            fraction = max
        if fraction < 0:
            fraction = 0
        self.set_origin(None, fraction * vh)

    def ScrollYPages(self, count):
        vh = float(self.virtual_height)
        h = self.tkwin.height
        amount = h / vh
        self.ScrollYMove(self.virtual_y / vh + count * amount)

    def ScrollYUnits(self, count):
        self.set_origin(None, self.virtual_y + count * 10)


    #
    #	 the viewport ring.
    #

    def init_viewport_ring(self):
        self.viewport_ring = []

    def save_viewport(self):
        self.viewport_ring.insert(0,
                                  (self.scale, self.virtual_x, self.virtual_y))
        length = preferences.viewport_ring_length
        self.viewport_ring = self.viewport_ring[:length]

    def restore_viewport(self):
        if self.viewport_ring:
            scale, vx, vy = self.viewport_ring[0]
            del self.viewport_ring[0]
            self.SetScale(scale / self.pixel_per_point, do_center = 0)
            self.set_origin(vx, vy, move_contents = 0)
