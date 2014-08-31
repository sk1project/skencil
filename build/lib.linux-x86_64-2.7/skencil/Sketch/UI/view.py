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
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.	See the GNU
# Library General Public License for more details.
#
# You should have received a copy of the GNU Library General Public
# License along with this library; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307	USA

from Sketch.warn import pdebug

from Sketch import Rect, EmptyRect, IntersectRects, Document, GraphicsDevice,\
     SketchInternalError, QueueingPublisher, StandardColors

from Sketch.const import STATE, VIEW, DOCUMENT, LAYOUT, REDRAW
from Sketch.const import LAYER, LAYER_STATE, LAYER_ORDER, LAYER_COLOR

from tkext import PyWidget
from viewport import Viewport


class SketchView(PyWidget, Viewport, QueueingPublisher):

    document = None

    def __init__(self, master=None, toplevel = None, document = None,
                 show_visible = 0, show_printable = 1,
                 resolution = None, **kw):
        apply(PyWidget.__init__, (self, master), kw)
        Viewport.__init__(self, resolution)
        QueueingPublisher.__init__(self)
        self.toplevel = toplevel

        self.move_window_count = 0
        self.show_page_outline = 1
        self.show_visible = show_visible
        self.show_printable = show_printable
        self.gcs_initialized = 0
        self.gc = GraphicsDevice()

        self.init_transactions()
        if document is not None:
            self.SetDocument(document)
        else:
            self.SetDocument(Document(create_layer = 1))

    def destroy(self):
        self.unsubscribe_doc()
        PyWidget.destroy(self)
        QueueingPublisher.Destroy(self)


    def MapMethod(self):
        # when being mapped the first time, initialise the gcs. this cannot be
        # done earlier, because the hitgc creates a pixmap which currently
        # only works after the window (id) has been created. In Xt this can be
        # done in the Realize widget method (after calling the superclass'
        # method), but Tk doesn't seem to offer any similar thing.
        if not self.gcs_initialized:
            self.init_gcs()
            self.issue_state()

    def DestroyMethod(self):
        # make sure that gc is deleted. gc may have a shared memory ximage
        # which is not freed if the gc is not destroyed leaving unused shared
        # memory segments in the system even after the process has finished.
        self.gc = None
        PyWidget.DestroyMethod(self)

    def init_gcs(self):
        self.gc.init_gc(self.tkwin, graphics_exposures = 1)
        self.gc.draw_visible = self.show_visible
        self.gc.draw_printable = self.show_printable
        self.gc.allow_outline = 0
        self.gcs_initialized = 1
        self.default_view()
        self.set_gc_transforms()

    def default_view(self):
        self.FitPageToWindow()

    def set_gc_transforms(self):
        self.gc.SetViewportTransform(self.scale, self.doc_to_win,
                                     self.win_to_doc)

    #
    #	Channels
    #

    def issue_state(self):
        self.queue_message(STATE)

    def issue_view(self):
        self.queue_message(VIEW)

    def issue_document(self):
        self.doc_changed = 1

    def queue_message(self, Publisher):
        if self.transaction:
            QueueingPublisher.queue_message(self, Publisher)
        else:
            self.issue(Publisher)

    def init_transactions(self):
        self.sb_update_pending = 0
        self.doc_changed = 0
        self.transaction = 0

    def begin_transaction(self):
        self.transaction = self.transaction + 1

    def end_transaction(self):
        self.transaction = self.transaction - 1
        if self.transaction == 0:
            if self.doc_changed:
                self.issue(DOCUMENT, self.document)
            self.sb_update_pending = 0
            self.doc_changed = 0
            self.flush_message_queue()
        elif self.transaction < 0:
            raise SketchInternalError('transaction count < 0')

    #
    #	receivers
    #

    def redraw_doc(self, all, rects = None):
        if all:
            self.clear_window()
        else:
            map(self.clear_area_doc, rects)

    def layout_changed(self):
        self.SetPageSize(self.document.Layout().Size())
        self.set_gc_transforms()
        self.update_scrollbars()
        self.update_rulers()
        if self.show_page_outline:
            self.clear_window()

    def layer_changed(self, *args):
        if args:
            redraw = EmptyRect
            if args[0] == LAYER_STATE:
                layer, visible_changed, printable_changed, outlined_changed \
                     = args[1]
                rect = layer.bounding_rect
                if rect is not EmptyRect:
                    if self.show_printable and printable_changed:
                        redraw = rect
                    if self.show_visible:
                        if visible_changed:
                            redraw = rect
                        if outlined_changed and layer.Visible():
                            redraw = rect
            elif args[0] == LAYER_ORDER:
                layer = args[1]
                if (self.show_printable and layer.Printable()
                    or self.show_visible and layer.Visible()):
                    redraw = layer.bounding_rect
                if len(args) > 2:
                    other = args[2]
                    if (self.show_printable and other.Printable()
                        or self.show_visible and other.Visible()):
                        redraw = IntersectRects(redraw, other.bounding_rect)
                    else:
                        redraw = EmptyRect
            elif args[0] == LAYER_COLOR:
                layer = args[1]
                rect = layer.bounding_rect
                if self.show_visible and rect is not EmptyRect \
                   and layer.Visible():
                    redraw = rect
            self.clear_area_doc(redraw)

    #
    #	Widget Methods (Redraw, ... )
    #

    time_redraw = 0
    def RedrawMethod(self, region = None):
        # draw the document
        if __debug__:
            if self.time_redraw:
                import time
                start = time.clock()
        if self.move_window_count >= 2:
            self.clear_window(update = 0)
        self.move_window_count = 0

        region = self.do_clear(region)

        # draw document
        self.gc.InitClip()
        self.gc.ResetFontCache()
        if region:
            self.gc.PushClip()
            self.gc.ClipRegion(region)

        tkwin = self.tkwin
        if region:
            x, y, w, h = region.ClipBox()
            if x < 0:
                w = w - x; x = 0
            if y < 0:
                h = h - y; y = 0
            if w > tkwin.width:
                w = tkwin.width
            if h > tkwin.height:
                h = tkwin.height
        else:
            x = y = 0
            w = tkwin.width
            h = tkwin.height
        p1 = self.WinToDoc(x - 1, y - 1)
        p2 = self.WinToDoc(x + w + 1, y + h + 1)
        rect = Rect(p1, p2)

        self.gc.SetFillColor(StandardColors.white)
        self.gc.gc.FillRectangle(x, y, w, h) # XXX ugly to access gc.gc

        #	draw paper
        if self.show_page_outline:
            w, h = self.document.PageSize()
            self.gc.DrawPageOutline(w, h)


        self.document.Draw(self.gc, rect)
        if region:
            self.gc.PopClip()

        if __debug__:
            if self.time_redraw:
                pdebug('timing', 'redraw', time.clock() - start)

        return region

    def ResizedMethod(self, width, height):
        Viewport.ResizedMethod(self, width, height)
        self.gc.WindowResized(width, height)


    #
    #	Viewport- and related methods
    #
    #	extend some Viewport methods to issue VIEW whenever
    #	the displayed area changes
    #

    def ForceRedraw(self):
        # Force a redraw of the whole window
        self.clear_window()
        if __debug__:
            #self.time_redraw = 1
            pass

#     def SetScrollbars(self, hbar, vbar):
# 	Viewport.SetScrollbars(self, hbar, vbar)
# 	hbar.configure(jump = 1)
# 	vbar.configure(jump = 1)

    def set_origin(self, xorg, yorg, move_contents = 1):
        self.begin_transaction()
        try:
            Viewport.set_origin(self, xorg, yorg,
                                move_contents = move_contents)
            self.set_gc_transforms()
            self.issue_view()
        finally:
            self.end_transaction()

    def move_window_contents(self, offx, offy):
        # implement the method needed by Viewport.set_origin
        w = self.tkwin
        width = w.width
        height = w.height
        if abs(offx) < width and abs(offy) < height:
            w.CopyArea(w, self.gc.gc, offx, offy, width, height, 0, 0)
            self.move_window_count = self.move_window_count + 1
        else:
            self.clear_window()

    def SetScale(self, scale, do_center = 1):
        # Set current scale
        self.begin_transaction()
        try:
            Viewport.SetScale(self, scale, do_center = do_center)
            self.set_gc_transforms()
        finally:
            self.end_transaction()

    def zoom_fit_rect(self, rect, save_viewport = 0):
        if save_viewport:
            self.save_viewport()
        Viewport.zoom_fit_rect(self, rect)


    #
    #	other view related methods
    #
    def FitToWindow(self, selected_only = 0, save_viewport = 1):
        self.begin_transaction()
        try:
            if selected_only:
                rect = self.document.SelectionBoundingRect()
            else:
                rect = self.document.BoundingRect()
            if rect:
                self.zoom_fit_rect(rect, save_viewport = save_viewport)
        finally:
            self.end_transaction()

    def FitPageToWindow(self, save_viewport = 1):
        self.begin_transaction()
        try:
            w, h = self.document.PageSize()
            self.zoom_fit_rect(Rect(0 - w * .03, 0 - h * .03, w * 1.03, h * 1.03).grown(10),
                               save_viewport = save_viewport)
        finally:
            self.end_transaction()


    #
    #	Outline Mode
    #
    #	Although not directly related to the viewport methods (the outline
    #	mode doesn't change the displayed area) the outline mode changes the
    #	way the drawing is displayed and thus issues VIEW.

    def SetOutlineMode(self, on = 1):
        self.begin_transaction()
        try:
            if on:
                if self.gc.IsOutlineActive():
                    return
                else:
                    self.gc.StartOutlineMode()
                    self.hitgc.StartOutlineMode()
            else:
                if self.gc.IsOutlineActive():
                    self.gc.EndOutlineMode()
                    self.hitgc.EndOutlineMode()
                else:
                    return
            self.issue_view()
            self.clear_window()
        finally:
            self.end_transaction()

    def ToggleOutlineMode(self):
        self.SetOutlineMode(not self.IsOutlineMode())

    def IsOutlineMode(self):
        return self.gc and self.gc.IsOutlineActive()

    #
    #	Show page outline on/off
    #

    def SetPageOutlineMode(self, on = 1):
        self.begin_transaction()
        try:
            self.show_page_outline = on
            self.issue_view()
            self.clear_window()
        finally:
            self.end_transaction()

    def TogglePageOutlineMode(self):
        self.SetPageOutlineMode(not self.IsPageOutlineMode())

    def IsPageOutlineMode(self):
        return self.show_page_outline

    #
    #
    #

    def unsubscribe_doc(self):
        if self.document is not None:
            self.document.Unsubscribe(REDRAW, self.redraw_doc)
            self.document.Unsubscribe(LAYOUT, self.layout_changed)
            self.document.Unsubscribe(LAYER, self.layer_changed)

    def subscribe_doc(self):
        self.document.Subscribe(REDRAW, self.redraw_doc)
        self.document.Subscribe(LAYOUT, self.layout_changed)
        self.document.Subscribe(LAYER, self.layer_changed)

    def SetDocument(self, doc):
        self.begin_transaction()
        try:
            self.unsubscribe_doc()
            self.document = doc
            self.subscribe_doc()
            self.clear_window()
            self.SetPageSize(self.document.Layout().Size())
            self.FitPageToWindow(save_viewport = 0)
            self.issue_document()
            self.issue_state()
            self.issue_view()
        finally:
            self.end_transaction()

