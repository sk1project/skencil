# -*- coding: utf-8 -*-
#
#    Copyright (C) 2011 by Igor E. Novikov
#    
#    This library is free software; you can redistribute it and/or
#    modify it under the terms of the GNU Lesser General Public
#    License as published by the Free Software Foundation; either
#    version 3 of the License, or (at your option) any later version.
#    
#    This library is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the GNU
#    Library General Public License for more details.
#    
#    You should have received a copy of the GNU Library General Public
#    License along with this library; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA

import os

from skencil import events

class ProgramDefaults:

    def __setattr__(self, attr, value):
        if not hasattr(self, attr) or getattr(self, attr) != value:
            self.__dict__[attr] = value
            events.emit(events.CONFIG_MODIFIED, attr, value)
    
    #
    #    Undo settings
    #

    #    how many undo steps sketch remembers. None means unlimited.
    undo_limit = None

    #
    #    Gridding
    #
    #    The initial grid geometry for a new document. It must be a tuple
    #    of the form (ORIG_X, ORIG_Y, WIDTH_X, WIDTH_Y). WIDTH_X and
    #    WIDTH_Y are the horizontal and the vertical distance between
    #    points of the grid, (ORIG_X, ORIG_X) is one point of the grid.
    #    These coordinates are given in Point
    grid_geometry = (0, 0, 20, 20)

    #    If the grid should be visible in a new document, set
    #    grid_visible to a true value
    grid_visible = 0

    #    The grid color of a new document as a tuple of RGB values in the
    #    range 0..1. E.g. (0, 0, 1) for blue
    grid_color = (0, 0, 1)


    #
    #    Guide Layer
    #
    #    The outline color of a new GuideLayer as a tuple of RGB values
    #    in the range 0..1.
    guide_color = (0, 0, 1)

    #
    #    Duplication offset
    #
    #    When objects are duplicated, the new copies are translated by
    #    duplicate_offset, given in document coordiates
    #
    duplicate_offset = (10, 10)

    #
    #    Units
    #
    #    The default unit used in various places.
    #
    #    Supported values: 'pt', 'in', 'cm', 'mm'
    #
    default_unit = 'pt'

    #   If true, setting the unit in the position indicator in the
    #   statusbar also sets the default unit
    poslabel_sets_default_unit = 1

    #
    #    Patterns
    #
    #    How many steps to draw in a gradient pattern
    #
    gradient_steps_editor = 30
    gradient_steps_print = 50

    #
    #    Text
    #
    #    If the text on the screen becomes smaller than greek_threshold,
    #    don't render a font, but draw little lines instead.
    # XXX see comments in graphics.py
    greek_threshold = 5

    #   If the metrics file for a font can't be found or if a requested
    #   font is not known at all, the (metrics of) fallback_font is used
    fallback_font = 'Times-Roman'

    #
    #    Maximum Snap Distance
    #
    #    When snapping is active, coordinates specified with the mouse
    #    are snapped to the nearest `special' point (e.g. a grid point)
    #    if that is nearer than max_snap_distance pixels. (Thus, this
    #    length is given in window (pixel-) coordinates).
    #
    max_snap_distance = 10

    #
    #    Snap Current Position
    #
    #    If true and snapping is active, the current position displayed
    #    in the status bar is the position the mouse position would be
    #    snapped to.
    snap_current_pos = 1

    #
    #   Cursor
    #
    #   If true, change the cursor when above a selected object or a
    #   guide line
    active_cursor = 1

    #
    #   Icons
    #
    color_icons = 1

    #
    #    List of most recently used files.
    #
    mru_files = ['', '', '', '']

    #
    #
    viewport_ring_length = 10

    #    The standard palette. If this is a relative pathname it is
    #    interpreted relative to std_res_dir.
    palette = 'standard.spl'

    arrows = 'standard.arrow'
    dashes = 'standard.dashes'
    pattern = 'pattern.ppm'

    #
    pattern_dir = ''
    image_dir = ''

    # whether the apply button in the property dialogs sets the default
    # properties for new objects.
    #   1       do it, but ask
    #   0       don't
    set_default_properties = 1

    #    Font dialog sample text. Can be changed by simply editing it in
    #    the font dialog.
    sample_text = 'ABCD abcd'

    #    Default paper format for new documents and documents read from a
    #    files that don't specify a paper format. This should be one of
    #    the formats defined in papersize.py.
    default_paper_format = 'A4'

    #    Default page orientation. Portrait = 0, Landscape = 1. Other
    #    values are silenty ignored.
    default_page_orientation = 0

    #    Screen resolution in pixel per point. Used by the canvas to
    #    convert document coordinates to screen coordinates for a zoom
    #    factor of 100%
    #
    #    None means to compute it from information obtained from the
    #    X-Server (ScreenWidth and ScreenMMWidth). 1.0 means 72 pixels
    #    per inch.
    screen_resolution = 1.0

    #    If true, switch to selection mode after drawing an object. Stay
    #    in creation mode otherwise.
    creation_is_temporary = 0

    #
    #
    #
    autoscroll_interval = 0   # ms, 0 disables auto scrolling
    autoscroll_amount = 3    # no. of scroll units

    #
    #    Images
    #
    #    Ask user for confirmation if the memory size of an image is
    #    larger than huge_image_size (measured in bytes) (unused at the
    #    moment)
    huge_image_size = 1 << 20

    #    Default resolution in pixels/inch for a new raster image that
    #    doesn't specify it itself. (not implemented yet)
    default_image_resolution = 72

    #
    #    EPS Files
    #
    #    The resoulution in pixel/inch of the preview image Sketch
    #    renders for preview. (using gs). Leave this at 72 for now.
    eps_preview_resolution = 72

    #
    #    Warning Messages
    #
    #    Whether to print internal warning messages. Useful for
    #    debugging.
    print_internal_warnings = 1

    #    print additional messages. these are usually only interesting
    #    for development purposes.
    print_debug_messages = 0

    #    Howto report warnings to the user:
    #        'dialog'    popup a dialog box
    #        'stderr'    write the message to stderr
    warn_method = 'dialog'

    #    whether to show the special menu. The special menu contains some
    #    commands that provide access to sketch internals and new,
    #    experimental features.
    show_special_menu = 0

    #    whether to show advanced snapping options.
    show_advanced_snap_commands = 0

    #    Use Tooltips. Seems to work now (Sketch 0.5.3)
    activate_tooltips = 1

    #    Delay for tooltips in milliseconds
    tooltip_delay = 500

    #
    #    Main Window
    #
    #    Window Title template. The SketchApplication class uses this
    #    template to form the window title via the %-operator and a
    #    dictionary containing the keys:
    #
    #        'docname'    The name of the document (usually the filename)
    #        'appname'    The name of the application. see above
    window_title_template = '%(docname)s - %(appname)s'

    #
    #    Panels
    #

    #    The panels save their screen position in the preferences file.
    #    These variables control whether this information is used and in
    #    what way.

    #    If true, use the saved coordinates when opening a panel
    panel_use_coordinates = 1

    #    If true, try to compensate for the coordinate changes the window
    #    manager introduces by reparenting.
    panel_correct_wm = 1

    #
    #    Blend Panel
    #
    blend_panel_default_steps = 10

    #
    #    Print Dialog
    #

    #    Default print destination. 'file' for file, 'printer' for printer
    print_destination = 'file'

    #    default directory for printing to file
    print_directory = ''

    #
    #    Menus
    #
    menu_tearoff_fix = 1

    #
    #   Rulers
    #

    ruler_min_tick_step = 3
    ruler_min_text_step = 30
    ruler_max_text_step = 100

    #ruler_font = '-*-helvetica-medium-r-*-*-10-*-*-*-*-*-iso8859-1'
    ruler_font = '-misc-fixed-medium-*-*-*-11-*-*-*-*-*-iso8859-1'
    #ruler_font = '-*-lucida-medium-r-*-*-11-*-*-*-*-*-iso8859-1'
    ruler_text_type = 'rotated' # can be 'rotated', 'horizontal' or 'vertical'
    #ruler_text_type = 'horizontal'
    #ruler_font_rotated = '-*-helvetica-medium-r-*-*-[0 10 ~10 0]-*-*-*-*-*-iso8859-1'
    ruler_font_rotated = '-misc-fixed-medium-*-*-*-[0 11 ~11 0]-*-*-*-*-*-iso8859-1'
    #ruler_font_rotated = '-*-lucida-medium-r-*-*-[0 11 ~11 0]-*-*-*-*-*-iso8859-1'

    #
    #    Color
    #
    #    For PseudoColor displays:
    color_cube = (6, 6, 6, 20)

    reduce_color_flashing = 1

    #    Screen Gamma. (leave this at 1.0 for now)
    #screen_gamma = 1.0

    #
    #    Bezier Objects
    #

    #    Whether the first click-drag-release in the PolyLine creator
    #    defines the start and end of the first line segment or just the
    #    start point.
    polyline_create_line_with_first_cklick = 1

    #    Mask Group
    topmost_is_mask = 1

    #
    #   Text
    #

    #   The name of the font used for new text-objects
    default_font = 'Times-Roman'

    #
    #    Import Filters
    #

    #    If true, try to unload some of the import filter modules after
    #    use. Only filters marked as unloadable in their config file are
    #    affected.
    unload_import_filters = 1


    #
    #   Misc
    #

    #   The line width for the outlines during a drag. On some servers
    #   dashed lines with a width of 0 are drawn solid. Set
    #   editor_line_width to 1 in those cases.
    editor_line_width = 0

    #   Load these standard scripts at runtime in interactive mode. This
    #   is really just a list of module names that are passed to
    #   __import__, but don't count on it.
    standard_scripts = ["Script.export_raster", "Script.simple_separation",
                        "Script.spread", "Script.reload_image",
                        "Script.create_star", "Script.create_star_outline",
                        "Script.create_spiral", "Script.read_gimp_path",
                        ]


class AppConfig:
    
    def __init__(self, path):
        self.path = path
        #
        #    some fundamental defaults for Sketch
        #
        
        # The title of the application. The window title will be this plus the
        # name of the document.
        self.name = 'Skencil'
        
        # The version of Sketch.
        self.version = '2.0.0'
        
        # The command used to invoke sketch. set on startup
        self.sketch_command = 'skencil'
        
        
        #    Some directories. They are updated to full pathnames by the
        #    startup script
        
        # The directory where sketch and its modules are found. Set
        # automagically from __init__.py of the Sketch package
        self.sketch_dir = ''
        
        # Subdirectory where resources (palettes, arrows, dashes,...) are stored.
        self.resource_dir = os.path.join(self.path, 'share')
#        self.resource_dir = '/usr/share/skencil'
        self.std_res_dir = self.resource_dir + '/Misc'
        
        # Subdirectory for the pixmaps. Used by skpixmaps.py when loading the
        # pixmaps. 
        self.pixmap_dir = self.resource_dir + '/Pixmaps'
        self.icon_dir = self.resource_dir + '/icons'
        
        # Subdirectory for the font metrics.
        fontmetric_dir = self.resource_dir + '/Fontmetrics'
        
        # Directories where sketch looks for font related files such as font
        # metrics, Type1 files (pfb or pfa) and font database files. The
        # expanded fontmetric_dir is appended to this.
        #
        # On platforms other than Linux this probably needs a few additional
        # directories. (non-existing dirs are automatically removed)
        self.font_path = ['/usr/X11R6/lib/X11/fonts/Type1',
                 '/usr/share/ghostscript/fonts',
                 '/usr/lib/ghostscript/fonts']
        
        
        # List of directories, where Sketch searches for resource files like
        # palettes, arrow definitions and dash patterns. The expanded
        # resource_dir is appended to this.
        # XXX implement this. (together with a way for the user to specify their
        # own versions)
        #resource_path = []
        
        
        # Subdirectory for plugins
        self.plugin_dir = 'Plugins/'
        
        # Directories where Sketch searches for plugins. The expanded plugin_dir
        # is appended to this
        self.plugin_path = []
        
        # PostScript Prolog. PostScript file containing the sketch specific
        # procset. relative to sketch_dir
        self.postscript_prolog = os.path.join(self.resource_dir, 'sketch-proc.ps')
        
        #
        #    user config settings
        #
        
        # directory in the user's home directory that contains userspecific
        # files
        self.user_config_dir = os.path.expanduser(os.path.join('~', '.config', 'skencil'))
        # the user's home directory. Set on startup
        self.user_home_dir = os.path.expanduser('~')
        
        
        self.preferences = ProgramDefaults()
        
        # where these settings are saved in ~/.sketch/:
        self.user_settings_file = 'preferences.py'
    
        self.small_font = '-*-helvetica-medium-r-*-*-*-100-*-*-*-*-iso8859-1'
        self.normal_font = '-*-helvetica-bold-r-*-*-*-120-*-*-*-*-iso8859-1'


