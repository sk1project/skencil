# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999, 2003, 2004 by Bernhard Herzog
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

#
#	Pixmap/Bitmap handling stuff
#

import os

from Sketch import config
from Sketch.warn import warn, USER

_builtin = ['NewDocument', 'Open', 'Save',
            'EditMode', 'SelectionMode',
            'Undo', 'Redo', 'Delete',
            'MoveToTop', 'MoveToBottom', 'MoveOneUp', 'MoveOneDown',
            'CreateRect', 'CreateEllipse', 'CreateCurve', 'CreatePoly',
            'Text', 'Image',
            'BezierAngle', 'BezierSmooth', 'BezierSymm',
            'BezierDeleteNode', 'BezierInsertNode',
            'BezierCurveLine', 'BezierLineCurve',
            'BezierOpenNodes', 'BezierCloseNodes',
            'Group', 'Ungroup',
            'GridOn', 'Zoom',
            'JoinMiter', 'JoinRound', 'JoinBevel',
            'CapButt', 'CapRound', 'CapProjecting',
            'FlipVertical', 'FlipHorizontal',
            'Duplicate',

            'fill_gradient', 'fill_hatch', 'fill_solid', 'fill_tile',
            'fill_none',
            'gradient_linear', 'gradient_conical', 'gradient_radial',

            'AlignTop', 'AlignBottom', 'AlignCenterY',
            'AlignLeft', 'AlignRight', 'AlignCenterX',

            'LayerNew', 'LayerUp', 'LayerDown',

            'ArrLeft', 'ArrRight', 'ArrArrLeft', 'ArrArrRight', 'NoPattern',

            'Portrait', 'Portrait_mask',
            'EyeInHand', 'EyeInHand_mask', 'EyeInHand_large',
            'hand_pencil', 'hand_pencil_mask', 'skencil_splash'
            ]

_small = ['MiniEyeOpen', 'MiniEyeClosed', 'MiniPrintOn', 'MiniPrintOff',
          'MiniLockOpen', 'MiniLockClosed', 'MiniOutlineOn', 'MiniOutlineOff']

_small_dir = 'New12'

_cursors = ['CurEdit', 'CurZoom', 'CurUpDown', 'CurDown', 'CurUp']

_load_these = ['TurnTL', 'TurnTR', 'TurnBL', 'TurnBR', 'Center',
               'ShearLR', 'ShearUD']

_alias = [('Icon', 'hand_pencil'), ('Icon_mask', 'hand_pencil_mask'),
          ('IconLarge', 'skencil_splash')]


class SketchPixmaps:

    def InitFromWidget(self, widget, files, basedir):
        for name in files:
            file_base = os.path.join(basedir, name)
            try:
                pixmap = widget.ReadBitmapFile(file_base + '.xbm')[2]
                setattr(self, name, pixmap)
            except IOError, info:
                warn(USER, "Warning: Can't load Pixmap from %s: %s",
                     file_base + '.xbm', info)


class PixmapTk:

    _cache = {}

    def load_image(self, name):
        import Tkinter
        if name[0] == '*':
            if config.preferences.color_icons:
                image = self._cache.get(name)
                if image is None:
                    image = Tkinter.PhotoImage(file = name[1:], format = 'GIF')
                    self._cache[name] = image
            else:
                image = '@' + name[1:-3] + 'xbm'
        else:
            image = name
        return image

    def clear_cache(self):
        self._cache.clear()

PixmapTk = PixmapTk()


def make_file_names(filenames, subdir = ''):
    default = 'error'	# a standard Tk bitmap
    for name in filenames:
        fullname = os.path.join(config.pixmap_dir, subdir, name)
        if os.path.exists(fullname + '.gif'):
            setattr(PixmapTk, name, '*' + fullname + '.gif')
        elif os.path.exists(fullname + '.xbm'):
            setattr(PixmapTk, name, '@' + fullname + '.xbm')
        else:
            warn(USER, "Warning: no file %s substituting '%s'",
                 fullname, default)
            setattr(PixmapTk, name, default)

make_file_names(_builtin)
make_file_names(_small, _small_dir)

def make_cursor_names(names):
    from Sketch import const
    default = 'X_cursor'	# a standard X cursor
    for name in names:
        fullname = os.path.join(config.pixmap_dir, name + '.xbm')
        fullname_mask = os.path.join(config.pixmap_dir, name + '_mask.xbm')
        if os.path.exists(fullname) and os.path.exists(fullname_mask):
            setattr(const, name, ('@' + fullname, fullname_mask,
                                  'black', 'white'))
        else:
            warn(USER, "Warning: no file %s (or *_mask) substituting '%s'",
                 fullname, default)
            setattr(const, name, default)

make_cursor_names(_cursors)

def make_alias(aliases):
    for alias, name in aliases:
        setattr(PixmapTk, alias, getattr(PixmapTk, name))

make_alias(_alias)

pixmaps = SketchPixmaps()


_init_done = 0
def InitFromWidget(widget):
    global _init_done
    if not _init_done:
        pixmaps.InitFromWidget(widget, _load_these, config.pixmap_dir)
