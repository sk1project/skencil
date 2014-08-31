# Sketch - A Python-based interactive drawing program
# Copyright (C) 1998, 1999, 2000, 2002, 2003 by Bernhard Herzog
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

_pkgdir = __path__[0]
_parentdir = os.path.join(_pkgdir, '..')

SketchVersion = string.strip(open(os.path.join(_pkgdir, 'VERSION')).read())

for _dir in ('Modules', 'Base'):
    __path__.insert(0, os.path.join(_pkgdir, _dir))


dir = os.path.join(_pkgdir, 'Modules')
if os.path.isdir(dir):
    sys.path.insert(1, dir)


message_dir = os.path.join(_parentdir, 'Resources/Messages')
try:
    from intl import gettext, dgettext, bindtextdomain
    import intl, locale
    try:
        locale.setlocale(locale.LC_ALL, "")
    except:
        # if we can't set the locale we might not be able to get
        # properly translated messages
        print "Can't set locale." \
              " Please check your LANG and LC_* environment variables"
    intl.textdomain("skencil")
    bindtextdomain("skencil", message_dir)
except ImportError:
    def gettext(text):
        return text
    def dgettext(domain, text):
        return text
    def bindtextdomain(*args):
        pass
_ = gettext

import gtkutils
ui_fonts = gtkutils.get_gtk_fonts()
ui_colors = gtkutils.ColorScheme()

import _sketch
from _sketch import Point, Polar, PointType
NullPoint = Point(0, 0)

from _sketch import Rect, PointsToRect, UnionRects, IntersectRects, \
     EmptyRect, InfinityRect, RectType
UnitRect = Rect(0, 0, 1, 1)


from _sketch import Trafo, Scale, Translation, Rotation, SingularMatrix, \
     TrafoType
Identity = Trafo(1, 0, 0, 1, 0, 0)
IdentityMatrix = Identity.matrix()


from _sketch import CreatePath, RectanglePath, RoundedRectanglePath, \
     approx_arc, CreateFontMetric, SKCache, TransformRectangle

from _sketch import ContAngle, ContSmooth, ContSymmetrical, \
     SelNone, SelNodes, SelSegmentFirst, SelSegmentLast, Bezier, Line

import config
config.init_directories(_parentdir)

from skexceptions import *

from undo import Undo, UndoList, CreateListUndo, CreateMultiUndo, UndoAfter, \
     UndoRedo, NullUndo

from connector import Connect, Disconnect, Issue, RemovePublisher, Subscribe, \
     Publisher, QueueingPublisher

#

def _import_PIL():
    # Import PIL and work around some bugs...
    # First, try to import PIL as a package
    try:
        import PIL
        import PIL.Image
        # Work around a bug in PIL 1.0 when used as a package
        if PIL.__path__[0] not in sys.path:
            sys.path.append(PIL.__path__[0])
    except ImportError:
        # Must be an older PIL.
        try:
            import Image, ImageChops
        except:
            warn.warn(warn.USER, "Can't import the Python Imaging Library")
            sys.exit(1)
        import plugins
        plugins.create_packages('PIL')
        import PIL
        PIL.__path__.append(os.path.split(Image.__file__)[0])
        PIL.Image = Image
        PIL.ImageChops = ImageChops
        sys.modules['PIL.Image'] = Image
        sys.modules['PIL.ImageChops'] = ImageChops

_import_PIL()



#

command_classes = []

def RegisterCommands(aclass):
    for cmd in aclass.commands:
        cmd.SetClass(aclass)
    command_classes.append(aclass)


# from Graphics.base import GraphicsObject, Primitive

from Graphics.arrow import StandardArrows, Arrow
from Graphics.properties import Style, FillStyle, EmptyFillStyle, \
     LineStyle, EmptyLineStyle, PropertyStack, EmptyProperties

from Graphics.blend import MismatchError, Blend, BlendTrafo
from Graphics.blendgroup import BlendGroup, CreateBlendGroup, \
     BlendInterpolation

from Graphics.color import CreateRGBColor, XRGBColor, CreateCMYKColor, \
     StandardColors
from Graphics.compound import Compound, EditableCompound
from Graphics.dashes import StandardDashes

from Graphics.document import EditDocument, SelectionMode, EditMode
Document = EditDocument

from Graphics.font import GetFont
from Graphics.gradient import MultiGradient, CreateSimpleGradient
from Graphics.graphics import SimpleGC, GraphicsDevice, InvertingDevice, \
     HitTestDevice

from Graphics.group import Group
from Graphics.guide import GuideLine
from Graphics.image import Image, load_image, ImageData
from Graphics.layer import Layer, GuideLayer, GridLayer

from Graphics.maskgroup import MaskGroup

from Graphics.pattern import EmptyPattern, SolidPattern, HatchingPattern, \
     LinearGradient, RadialGradient, ConicalGradient, ImageTilePattern

from Graphics.plugobj import PluginCompound, TrafoPlugin

from Graphics.rectangle import Rectangle, RectangleCreator
from Graphics.ellipse import Ellipse, EllipseCreator
from Graphics.bezier import PolyBezier, PolyBezierCreator, PolyLineCreator, \
    CombineBeziers, CreatePath, ContAngle, ContSmooth, ContSymmetrical

from Graphics.psdevice import PostScriptDevice


from Graphics.text import SimpleText, SimpleTextCreator, PathText


def init_lib():
    import plugins
    config.load_user_preferences()
    Issue(None, const.INITIALIZE)

def init_ui():
    # workaround for a threaded _tkinter in Python 1.5.2
    if sys.version[:5] >= '1.5.2':
    	print 'CHANGED'
        import paxtkinter
        sys.modules['_tkinter'] = paxtkinter

    init_lib()

    # import the standard scripts
    for name in config.preferences.standard_scripts:
        __import__(name)

def init_modules_from_widget(root):
    import pax
    import UI.skpixmaps, Graphics.graphics
    import UI.tkext, Graphics.color
    UI.tkext.InitFromTkapp(root.tk)
    if hasattr(root.tk, 'interpaddr'):
        tkwin = pax.name_to_window('.', root.tk.interpaddr())
    else:
        tkwin = pax.name_to_window('.', root.tk)
    Graphics.color.InitFromWidget(tkwin, root)
    Graphics.graphics.InitFromWidget(tkwin)
    UI.skpixmaps.InitFromWidget(tkwin)

