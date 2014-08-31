# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 2001, 2003 by Bernhard Herzog
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

import operator, os
from types import StringType, TupleType, IntType
from string import strip, split, atof, atoi

import X

from Sketch.const import CHANGED, COLOR1, COLOR2, CHANGED, VIEW, \
     DROP_COLOR, CurDragColor
from Sketch.warn import warn, INTERNAL, USER, pdebug, warn_tb
from Sketch import Publisher, config, SketchError, _
from Sketch import CreateRGBColor, StandardColors, GraphicsDevice, Identity

from tkext import PyWidget


class NameInUse(SketchError):
    pass

class RGBAlreadyStored(SketchError):
    pass

class RGBPalette(Publisher):

    ignore_issue = 1

    def __init__(self):
        self.entries = []
        self.name_to_entry = {}
        self.rgb_to_entry = {}

    def Subscribe(self, channel, func, *args):
        apply(Publisher.Subscribe, (self, channel, func) + args)
        self.ignore_issue = 0

    def update_dicts(self):
        self.name_to_entry = {}
        self.rgb_to_entry = {}
        for entry in self.entries:
            rgb, name = entry
            self.name_to_entry[name] = entry
            self.rgb_to_entry[rgb] = entry

    def AddEntry(self, rgb, name = None, rename = 0):
        if name:
            if self.name_to_entry.has_key(name):
                if self.name_to_entry[name] != (rgb, name):
                    raise NameInUse
        if self.rgb_to_entry.has_key(rgb):
            if self.rgb_to_entry[rgb] != (rgb, name) and not rename:
                raise RGBAlreadyStored
        if not name:
            i = 0
            base = 'Color '
            name = base + `i`
            known = self.name_to_entry.has_key
            while known(name):
                i = i + 1
                name = base + `i`
        entry = (rgb, name)
        self.entries.append(entry)
        self.name_to_entry[name] = entry
        self.rgb_to_entry[rgb] = entry
        self.issue(CHANGED)

    def __getitem__(self, idx):
        if type(idx) == StringType:
            return self.name_to_entry[idx]
        if type(idx) == TupleType:
            return self.rgb_to_entry[idx]
        if type(idx) == IntType:
            return self.entries[idx]


    def GetRGB(self, idx):
        return self[idx][0]

    def Colors(self):
        return map(operator.getitem, self.entries, [0] * len(self.entries))

    def WriteFile(self, file):
        for entry in self.entries:
            (r, g, b), name = entry
            file.write('%g %g %g\t%s\n' % (r, g, b, name))

    def __len__(self):
        return len(self.entries)



#
#	Get the standard palette. User settable.
#

def read_standard_palette(filename):
    filename = os.path.join(config.std_res_dir, filename)
    return read_palette_file(filename)

#minimalistic fallback:
_mini_pal = [(0, 0, 0, 'Black'),
             (1, 1, 1, 'White')]

def GetStandardPalette():
    palette = read_standard_palette(config.preferences.palette)
    if not palette:
        warn(USER, _("Could not load palette %s; trying mini.spl..."),
             config.preferences.palette)
        palette = read_standard_palette('mini.spl')
        if not palette:
            warn(USER,
                 _("Could not load palette mini.spl; reverting to black&white"))
            palette = RGBPalette()
            for r, g, b, name in _mini_pal:
                palette.AddEntry((r, g, b), name)
    return palette


def LoadPalette(filename):
    return read_palette_file(filename)

file_types = ((_("Skencil/Sketch Palette"), '.spl'),
              (_("All Files"),	 '*'))


magic_rgb_palette = '##Sketch RGBPalette 0'
magic_gimp_palette = 'GIMP Palette'

def read_palette_file(filename):
    """Read the palette file filename"""
    file = open(filename)
    line = file.readline()
    line = strip(line)
    palette = None
    try:
        if line == magic_rgb_palette:
            palette = ReadRGBPaletteFile(filename)
        elif line == magic_gimp_palette:
            palette = Read_X_RGB_TXT(filename)
    except:
        warn_tb(USER)
    return palette


def ReadRGBPaletteFile(filename):
    file = open(filename)

    line = file.readline()
    if line != magic_rgb_palette + '\n':
        file.close()
        raise ValueError, 'Invalid file type'

    palette = RGBPalette()

    linenr = 1
    for line in file.readlines():
        line = strip(line)
        linenr = linenr + 1
        if not line or line[0] == '#':
            continue

        line = split(line, None, 3)

        if len(line) != 4:
            warn(INTERNAL, '%s:%d: wrong number of fields', filename, linenr)
            continue
        try:
            rgb = tuple(map(atof, line[:3]))
        except:
            warn(INTERNAL, '%s:%d: cannot parse rgb values', filename, linenr)
            continue

        for value in rgb:
            if value < 0 or value > 1.0:
                warn(INTERNAL, '%s:%d: value out of range', filename, linenr)
                continue

        name = strip(line[-1])

        try:
            palette.AddEntry(rgb, name)
        except NameInUse:
            warn(INTERNAL, '%s:%d: color name already used', filename, linenr)
            continue
        except RGBAlreadyStored:
            warn(INTERNAL, '%s:%d: color already stored', filename, linenr)
            continue

    file.close()

    return palette



def Read_X_RGB_TXT(filename):
    file = open(filename)

    palette = RGBPalette()

    linenr = 0
    color_num = 0
    for line in file.readlines():
        line = strip(line)
        linenr = linenr + 1
        if not line or line[0] in ('#', '!'):
            # an empty line or an X-style comment (!) or a GIMP comment (#)
            # GIMP's palette files have practically the same format as rgb.txt
            continue

        line = split(line, None, 3)
        if len(line) == 3:
            # the name is missing
            while 1:
                name = 'color ' + str(color_num)
                try:
                    palette[name]
                    used = 1
                except KeyError:
                    used = 0
                if not used:
                    line.append(name)
                    break
                color_num = color_num + 1
        if len(line) != 4:
            warn(INTERNAL, '%s:%d: wrong number of fields', filename, linenr)
            continue
        try:
            values = map(atoi, line[:3])
        except:
            warn(INTERNAL, '%s:%d: cannot parse rgb values', filename, linenr)
            continue

        rgb = []
        for value in values:
            value = round(value / 255.0, 3)
            if value < 0:
                value = 0.0
            elif value > 1.0:
                value = 1.0
            rgb.append(value)
        rgb = tuple(rgb)

        name = strip(line[-1])

        try:
            palette.AddEntry(rgb, name)
        except NameInUse:
            warn(INTERNAL, '%s:%d: color name already used', filename, linenr)
            continue
        except RGBAlreadyStored:
            warn(INTERNAL, '%s:%d: color already stored', filename, linenr)
            continue

    file.close()

    return palette



class PaletteWidget(PyWidget, Publisher):

    def __init__(self, master=None, palette = None, cell_size = 37, **kw):
        if not kw.has_key('height'):
            kw['height'] = 18
        apply(PyWidget.__init__, (self, master), kw)

        self.cell_size = cell_size
        self.num_cells = 0
        self.gc_initialized = 0
        self.gc = GraphicsDevice()
        self.gc.SetViewportTransform(1.0, Identity, Identity)
        self.start_idx = 0
        self.palette = None
        if palette is None:
            palette = RGBPalette()
        self.SetPalette(palette)
        self.dragging = 0
        self.bind('<ButtonPress-1>', self.press_1)
        self.bind('<Motion>', self.move_1)
        self.bind('<ButtonRelease-1>', self.release_1)
        self.bind('<ButtonRelease-3>', self.apply_color_2)

    def DestroyMethod(self):
        self.palette.Unsubscribe(CHANGED, self.palette_changed)
        Publisher.Destroy(self)

    def compute_num_cells(self):
        self.num_cells = self.tkwin.width / self.cell_size + 1

    def MapMethod(self):
        self.compute_num_cells()
        self.issue(VIEW)
        if not self.gc_initialized:
            self.init_gc()
            self.gc_initialized = 1

    def init_gc(self):
        self.gc.init_gc(self.tkwin)

    def get_color(self, x, y):
        if 0 <= x < self.tkwin.width and 0 <= y < self.tkwin.height:
            i = self.start_idx + x / self.cell_size
            if i < len(self.palette):
                return apply(CreateRGBColor, self.palette.GetRGB(i))

    def release_1(self, event):
        try:
            if self.dragging:
                self.drop_color(event)
            else:
                self.apply_color_1(event)
        finally:
            self.dragging = 0

    def drop_color(self, event):
        self['cursor'] = self.drag_old_cursor
        w = self.winfo_containing(event.x_root, event.y_root)
        while w and w != self:
            if __debug__:
                pdebug('DND', 'trying to drop on', w)
            try:
                accepts = w.accept_drop
            except AttributeError:
                accepts = ()
            if DROP_COLOR in accepts:
                x = event.x_root - w.winfo_rootx()
                y = event.y_root - w.winfo_rooty()
                w.DropAt(x, y, DROP_COLOR, self.drag_start)
                break
            if w != w.winfo_toplevel():
                parent = self.tk.call('winfo', 'parent', w._w)
                w = self.nametowidget(parent)
            else:
                break


    def apply_color_1(self, event):
        c = self.get_color(event.x, event.y)
        if c:
            self.issue(COLOR1, c)

    def apply_color_2(self, event):
        c = self.get_color(event.x, event.y)
        if c:
            self.issue(COLOR2, c)

    drag_start = (0, 0, 0)
    def press_1(self, event):
        self.drag_start = self.get_color(event.x, event.y)

    def move_1(self, event):
        if event.state & X.Button1Mask:
            if not self.dragging:
                self.dragging = 1
                self.drag_old_cursor = self['cursor']
                self['cursor'] = CurDragColor
            w = self.winfo_containing(event.x_root, event.y_root)

    def Palette(self):
        return self.palette

    def SetPalette(self, palette):
        if self.palette is not None:
            self.palette.Unsubscribe(CHANGED, self.palette_changed)
        self.palette = palette
        self.palette.Subscribe(CHANGED, self.palette_changed)
        self.palette_changed()

    def palette_changed(self):
        self.compute_num_cells()
        self.normalize_start()
        self.issue(VIEW)
        self.UpdateWhenIdle()

    def RedrawMethod(self, region = None):
        win = self.tkwin
        width = win.width
        height = win.height
        self.gc.StartDblBuffer()
        self.gc.SetFillColor(StandardColors.black)
        self.gc.FillRectangle(0, 0, width, height)

        x = 0
        FillRectangle = self.gc.FillRectangle
        SetFillColor = self.gc.SetFillColor
        create_color = CreateRGBColor
        rgbs = self.palette.Colors()
        rgbs = rgbs[self.start_idx:self.start_idx + self.num_cells]
        for rgb in rgbs:
            SetFillColor(apply(create_color, rgb))
            FillRectangle(x + 1, 1, x + self.cell_size, height - 1)
            x = x + self.cell_size
        self.gc.EndDblBuffer()

    def ResizedMethod(self, width, height):
        self.compute_num_cells()
        self.gc.WindowResized(width, height)
        self.normalize_start()
        self.UpdateWhenIdle()

    def normalize_start(self):
        length = len(self.palette)
        if self.start_idx < 0:
            self.start_idx = 0
        if length < self.num_cells:
            self.start_idx = 0
        elif length - self.start_idx < self.num_cells:
            self.start_idx = length - self.num_cells

    def CanScrollLeft(self):
        return self.start_idx > 0

    def CanScrollRight(self):
        return len(self.palette) - self.start_idx > self.num_cells

    def ScrollXPages(self, count):
        length = self.tkwin.width / self.cell_size
        start = self.start_idx
        self.start_idx = self.start_idx + count * length
        self.normalize_start()
        if start != self.start_idx:
            self.UpdateWhenIdle()
            self.issue(VIEW)

    def ScrollXUnits(self, count):
        start = self.start_idx
        self.start_idx = self.start_idx + count
        self.normalize_start()
        if start != self.start_idx:
            self.UpdateWhenIdle()
            self.issue(VIEW)

