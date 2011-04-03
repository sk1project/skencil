# -*- coding: utf-8 -*-
#
#	Copyright (C) 2011 by Igor E. Novikov
#	
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#	
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#	
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import gtk

from skencil import config

#Canvas mode enumeration
SELECT_MODE = 0
SHAPER_MODE = 1
ZOOM_MODE = 2
FLEUR_MODE = 3
LINE_MODE = 10
CURVE_MODE = 11
RECT_MODE = 12
ELLIPSE_MODE = 13
TEXT_MODE = 14
POLYGON_MODE = 15
ZOOM_OUT_MODE = 16
MOVE_MODE = 17
COPY_MODE = 18


MODE_LIST = [SELECT_MODE, SHAPER_MODE, ZOOM_MODE, LINE_MODE,
			CURVE_MODE, RECT_MODE, ELLIPSE_MODE, TEXT_MODE,
			POLYGON_MODE, ZOOM_OUT_MODE, MOVE_MODE]

def get_cursors():
	cursors = {
			SELECT_MODE:('cur_std.png', (0, 0)),
			SHAPER_MODE:('cur_edit.png', (0, 0)),
			ZOOM_MODE:('cur_zoom.png', (6, 6)),
			FLEUR_MODE:('cur_fleur.png', (11, 4)),
			LINE_MODE:('cur_create_polyline.png', (6, 6)),
			CURVE_MODE:('cur_create_bezier.png', (6, 6)),
			RECT_MODE:('cur_create_rect.png', (6, 6)),
			POLYGON_MODE:('cur_create_polygon.png', (6, 6)),
			ELLIPSE_MODE:('cur_create_ellipse.png', (6, 6)),
			TEXT_MODE:('cur_text.png', (4, 8)),
			ZOOM_OUT_MODE:('cur_zoom_out.png', (6, 6)),
			MOVE_MODE:('cur_move.png', (0, 0)),
			COPY_MODE:('cur_copy.png', (0, 0)),
			}
	keys = cursors.keys()
	for key in keys:
		path = os.path.join(config.resource_dir, 'cursors', cursors[key][0])
		w, h = cursors[key][1]
		cursors[key] = gtk.gdk.Cursor(gtk.gdk.display_get_default(),
							gtk.gdk.pixbuf_new_from_file(path), w, h)
	return cursors
