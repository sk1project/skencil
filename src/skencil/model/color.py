# Sketch - A Python-based interactive drawing program
# Copyright (C) 1997, 1998, 1999 by Bernhard Herzog
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
#	Color Handling
#

from string import atoi

from Sketch.warn import warn, INTERNAL, USER
from Sketch._sketch import RGBColor, XVisual
from Sketch import config, _

skvisual = None

def CreateRGBColor(r, g, b):
    #print 'CreateRGBColor', round(r, 3), round(g, 3), round(b, 3)
    return RGBColor(round(r, 3), round(g, 3), round(b, 3))

def XRGBColor(s):
    # only understands the old x specification with two hex digits per
    # component. e.g. `#00FF00'
    if s[0] != '#':
        raise ValueError("Color %s dosn't start with a '#'" % s)
    r = atoi(s[1:3], 16) / 255.0
    g = atoi(s[3:5], 16) / 255.0
    b = atoi(s[5:7], 16) / 255.0
    return CreateRGBColor(r, g, b)

def CreateCMYKColor(c, m, y, k):
    r = 1.0 - min(1.0, c + k)
    g = 1.0 - min(1.0, m + k)
    b = 1.0 - min(1.0, y + k)
    return CreateRGBColor(r, g, b)


#
#	some standard colors.
#

class StandardColors:
    black	= CreateRGBColor(0.0, 0.0, 0.0)
    darkgray	= CreateRGBColor(0.25, 0.25, 0.25)
    gray	= CreateRGBColor(0.5, 0.5, 0.5)
    lightgray	= CreateRGBColor(0.75, 0.75, 0.75)
    white	= CreateRGBColor(1.0, 1.0, 1.0)
    red		= CreateRGBColor(1.0, 0.0, 0.0)
    green	= CreateRGBColor(0.0, 1.0, 0.0)
    blue	= CreateRGBColor(0.0, 0.0, 1.0)
    cyan	= CreateRGBColor(0.0, 1.0, 1.0)
    magenta	= CreateRGBColor(1.0, 0.0, 1.0)
    yellow	= CreateRGBColor(1.0, 1.0, 0.0)


#
#	For 8-bit displays:
#

def float_to_x(float):
    return int(int(float * 63) / 63.0 * 65535)

def fill_colormap(cmap):
    max = 65535
    colors = []
    color_idx = []
    failed = 0

    shades_r, shades_g, shades_b, shades_gray = config.preferences.color_cube
    max_r = shades_r - 1
    max_g = shades_g - 1
    max_b = shades_b - 1

    for red in range(shades_r):
        red = float_to_x(red / float(max_r))
        for green in range(shades_g):
            green = float_to_x(green / float(max_g))
            for blue in range(shades_b):
                blue = float_to_x(blue / float(max_b))
                colors.append((red, green, blue))
    for i in range(shades_gray):
        value = int((i / float(shades_gray - 1)) * max)
        colors.append((value, value, value))

    for red, green, blue in colors:
        try:
            ret = cmap.AllocColor(red, green, blue)
            color_idx.append(ret[0])
        except:
            color_idx.append(None)
            failed = 1

    if failed:
        warn(USER,
             _("I can't alloc all needed colors. I'll use a private colormap"))
        warn(INTERNAL, "allocated colors without private colormap: %d",
             len(filter(lambda i: i is None, color_idx)))
        if config.preferences.reduce_color_flashing:
            #print 'reduce color flashing'
            cmap = cmap.CopyColormapAndFree()
            for idx in range(len(color_idx)):
                if color_idx[idx] is None:
                    color_idx[idx] = apply(cmap.AllocColor, colors[idx])[0]
        else:
            #print "don't reduce color flashing"
            cmap = cmap.CopyColormapAndFree()
            cmap.FreeColors(filter(lambda i: i is not None, color_idx), 0)
            color_idx = []
            for red, green, blue in colors:
                color_idx.append(cmap.AllocColor(red, green, blue)[0])

    return cmap, color_idx

_init_from_widget_done = 0
global_colormap = None
def InitFromWidget(tkwin, root = None):
    global _init_from_widget_done, skvisual
    if _init_from_widget_done:
        return
    if root:
        visual = root.winfo_visual()
        if visual == 'truecolor':
            skvisual = XVisual(tkwin.c_display(), tkwin.c_visual())
            #skvisual.set_gamma(config.preferences.screen_gamma)
            alloc_function = skvisual.get_pixel
        if visual == 'pseudocolor' and root.winfo_depth() == 8:
            global global_colormap
            cmap = tkwin.colormap()
            newcmap, idxs = fill_colormap(cmap)
            if newcmap != cmap:
                cmap = newcmap
                tkwin.SetColormap(cmap)
            shades_r, shades_g, shades_b, shades_gray \
                    = config.preferences.color_cube
            skvisual = XVisual(tkwin.c_display(), tkwin.c_visual(),
                               (shades_r, shades_g, shades_b, shades_gray, idxs))
            global_colormap = cmap
    _init_from_widget_done = 1
