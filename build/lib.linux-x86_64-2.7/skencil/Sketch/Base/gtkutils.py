# -*- coding: utf-8 -*-

# Routines for UI fonts & colors management

# Copyright (c) 2010 by Igor E.Novikov
#
#This library is free software; you can redistribute it and/or
#modify it under the terms of the GNU Library General Public
#License as published by the Free Software Foundation; either
#version 2 of the License, or (at your option) any later version.
#
#This library is distributed in the hope that it will be useful,
#but WITHOUT ANY WARRANTY; without even the implied warranty of
#MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
#Library General Public License for more details.
#
#You should have received a copy of the GNU Library General Public
#License along with this library; if not, write to the Free Software
#Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

import os, string, copy
from tempfile import NamedTemporaryFile


##################################################
# Font routines
##################################################

def get_gtk_fonts():
    """
    Returns list of four fonts, used in UI:
    [small_font,normal_font,large_font,fixed_font]
    Each font is a list like:
    [font_family,font_style,font_size]
    where:
    font_family - string representation of font family
    font_style - list of font styles like 'bold' and 'italic'
    font_size - font size integer value
    """
    
    tmpfile = NamedTemporaryFile()
    command = "import gtk;w = gtk.Window();w.realize();style=w.get_style(); print style.font_desc.to_string();"
    os.system('python -c "%s" >%s 2>/dev/null' % (command, tmpfile.name))
    
    font = tmpfile.readline().strip()
    
    normal_font = process_gtk_font_string(font)
    small_font = copy.deepcopy(normal_font)
    small_font[2] -= 1
    
    large_font = copy.deepcopy(normal_font)
    large_font[2] += 2
    if not 'bold' in large_font[1]:
        large_font[1].append('bold')
        
    fixed_font = copy.deepcopy(normal_font)
    fixed_font[0] = 'monospace'
    
    return [small_font, normal_font, large_font, fixed_font]
    
    
def process_gtk_font_string(font):
    """
    Converts Gtk font string to font description list
    So Gtk string like: San Serif Bold Italic 10
    will be: ['San\ Serif', ['bold','italic'], 10]
    Such form is much better for constructing of 
    Tk font description.
    """
    
    font_style = []
    vals = font.split()
    font_size = int(vals[-1])
    vals.remove(vals[-1])
    if 'Bold' in vals:
        vals.remove('Bold')
        font_style.append('bold')
    if 'Italic' in vals:
        vals.remove('Italic')
        font_style.append('italic')
    font_family = string.join(vals, '\ ')
    return [font_family, font_style, font_size]

def tkfont_from_list(font_list):
    """
    Constructs tk font string from font list.
    """
    return '%s %d ' % (font_list[0], font_list[2]) + string.join(font_list[1])

def set_ui_fonts(widget, font_list):
    """
    Applies font list to tk defaults.
    """
    widget.tk.call('option', 'add', '*font', tkfont_from_list(font_list[1]))


##################################################
# Colors routines
##################################################

SYSTEM_SCHEME = 'System'
BUILTIN_SCHEME = 'Built-in'

            
def gtk_to_tk_color(color):
    """
    Converts gtk color representation to tk.
    For example: #0000ffff0000 will be converted to #00ff00
    """
    return color[0] + color[1] + color[2] + color[5] + color[6] + color[9] + color[10]

def tkcolor_to_rgb(tkcolor):
    """
    Converts tk color string as tuple of integer values.
    For example: #ff00ff => (255,0,255)
    """
    return (int(tkcolor[1:3], 0x10), int(tkcolor[3:5], 0x10), int(tkcolor[5:], 0x10))

def saturated_color(color):
    """
    Returns saturated color value. 
    """
    r, g, b = tkcolor_to_rgb(color)
    delta = 255 - max(r, g, b)
    return '#%02X%02X%02X' % (r + delta, g + delta, b + delta)
                
def middle_color(dark, light, factor=0.5):
    """
    Calcs middle color value.
    
    dark, light - tk color strings
    factor - resulted color shift 
    """
    dark = tkcolor_to_rgb(dark)
    light = tkcolor_to_rgb(light)
    r = dark[0] + (light[0] - dark[0]) * factor
    g = dark[1] + (light[1] - dark[1]) * factor
    b = dark[2] + (light[2] - dark[2]) * factor
    return '#%02X%02X%02X' % (r, g, b)

def lighter_color(color, factor):
    """
    Calcs lighted color value according factor.
    
    color - tk color strings
    factor - resulted color shift   
    """
    return middle_color(color, saturated_color(color), factor)
    


class ColorScheme:
    """
    The class represents UI color scheme.
    Colors can be imported from system (SYSTEM_SCHEME)
    or built-in values (BUILTIN_SCHEME).
    """
    
    bg = '#d4d0c8'
    fg = '#000000'
    highlightbackground = '#f3f2ef'
    highlightcolor = '#b0ada5'
    disabledforeground = '#b0ada6'
    selectbackground = '#002468'
    selectforeground = '#ffffff'
    
    menubackground = '#dedad2'
    menuforeground = '#000000'
    menuselectbackground = '#002468'
    menuselectforeground = '#ffffff'
    menudisabledforeground = '#b0ada6'
    menubordercolor = '#7e7b77'
    
    editfieldbackground = '#ffffff'
    editfieldforeground = '#000000'
    treelinescolor = '#000000'
    
    d3_light = '#ffffff'
    d3_dark = '#b0ada6'
    
    light_border = '#b0ada6'
    normal_border = '#b0ada6'
    dark_border = '#b0ada6'
    
    evencolor = '#f0f0f0'
    
    name = BUILTIN_SCHEME
    
    def __init__(self, scheme=SYSTEM_SCHEME):
        self.name = scheme
        if scheme == BUILTIN_SCHEME:
            return  
        else:
            self.name = SYSTEM_SCHEME
            self.import_gtk_colors()
            
    def import_gtk_colors(self):
        """
        Imports system gtk color scheme using pygtk binding. 
        """
        colors = {}
        tmpfile = NamedTemporaryFile()
        command = "import gtk;w = gtk.Window();w.realize();style=w.get_style();"
        command += "print style.base[gtk.STATE_NORMAL].to_string()," + \
            " style.base[gtk.STATE_ACTIVE].to_string()," + \
            " style.base[gtk.STATE_PRELIGHT].to_string()," + \
            " style.base[gtk.STATE_SELECTED].to_string()," + \
            " style.base[gtk.STATE_INSENSITIVE].to_string();"
        command += "print style.text[gtk.STATE_NORMAL].to_string()," + \
            " style.text[gtk.STATE_ACTIVE].to_string()," + \
            " style.text[gtk.STATE_PRELIGHT].to_string()," + \
            " style.text[gtk.STATE_SELECTED].to_string()," + \
            " style.text[gtk.STATE_INSENSITIVE].to_string();"
        command += "print style.fg[gtk.STATE_NORMAL].to_string()," + \
            " style.fg[gtk.STATE_ACTIVE].to_string()," + \
            " style.fg[gtk.STATE_PRELIGHT].to_string()," + \
            " style.fg[gtk.STATE_SELECTED].to_string()," + \
            " style.fg[gtk.STATE_INSENSITIVE].to_string();"
        command += "print style.bg[gtk.STATE_NORMAL].to_string()," + \
            " style.bg[gtk.STATE_ACTIVE].to_string()," + \
            " style.bg[gtk.STATE_PRELIGHT].to_string()," + \
            " style.bg[gtk.STATE_SELECTED].to_string()," + \
            " style.bg[gtk.STATE_INSENSITIVE].to_string();"
    
        os.system('python -c "%s" >%s 2>/dev/null' % (command, tmpfile.name))    

        for type in ["base", "text", "fg", "bg"]:
            line = tmpfile.readline().strip().split()
            colors[type + ' normal'] = gtk_to_tk_color(line[0])
            colors[type + ' active'] = gtk_to_tk_color(line[1])
            colors[type + ' prelight'] = gtk_to_tk_color(line[2])
            colors[type + ' selected'] = gtk_to_tk_color(line[3])
            colors[type + ' insensitive'] = gtk_to_tk_color(line[4])
        tmpfile.close()
        
        self.map_gtk_colors(colors)
    
    def map_gtk_colors(self, gtk_colors):
        """
        Maps gtk colors to ColorScheme fields.
        """
        
        self.bg = gtk_colors['bg normal']
        self.fg = gtk_colors['text normal']
        
        self.highlightbackground = gtk_colors['bg active']
        self.highlightcolor = gtk_colors['fg active']
        self.disabledforeground = gtk_colors['fg insensitive']
        self.selectbackground = gtk_colors['bg selected']
        self.selectforeground = gtk_colors['text selected']
        
        self.menubackground = lighter_color(self.bg, .25)
        self.menuforeground = gtk_colors['fg normal']
        self.menuselectbackground = gtk_colors['bg selected']
        self.menuselectforeground = gtk_colors['fg selected']
        self.menudisabledforeground = gtk_colors['text insensitive']
        self.menubordercolor = gtk_colors['fg insensitive']
        
        self.editfieldbackground = gtk_colors['base normal']
        self.editfieldforeground = gtk_colors['text normal']
        self.treelinescolor = gtk_colors['text normal']
        
        self.d3_light = middle_color('#ffffff', gtk_colors['bg normal'])
        self.d3_dark = middle_color(gtk_colors['bg active'], gtk_colors['fg insensitive'])
        
        self.light_border = gtk_colors['bg active']
        self.normal_border = middle_color(gtk_colors['bg active'], gtk_colors['fg insensitive'])
        self.dark_border = gtk_colors['fg insensitive']
        
        self.evencolor = middle_color(self.bg, self.editfieldbackground, 0.7)
        
def set_ui_colors(widget, color_scheme):
    """
    Applies ColorScheme object values to tk defaults.
    """ 
    widget.tk.call('tk_setPalette', color_scheme.bg)
                
    widget.tk.call('option', 'add', '*background', color_scheme.bg, 'interactive')
    widget.tk.call('option', 'add', '*foreground', color_scheme.fg, 'interactive')
    widget.tk.call('option', 'add', '*selectForeground', color_scheme.selectforeground, 'interactive')
    widget.tk.call('option', 'add', '*selectBackground', color_scheme.selectbackground, 'interactive')
    widget.tk.call('option', 'add', '*highlightBackground', color_scheme.highlightbackground, 'interactive')
    widget.tk.call('option', 'add', '*highlightColor', color_scheme.highlightcolor, 'interactive')
    widget.tk.call('option', 'add', '*activeBackground', color_scheme.bg, 'interactive')
    widget.tk.call('option', 'add', '*activeForeground', color_scheme.fg, 'interactive')
    widget.tk.call('option', 'add', '*Menu.activeBackground', color_scheme.selectbackground, 'interactive')
    widget.tk.call('option', 'add', '*Menu.activeForeground', color_scheme.selectforeground, 'interactive')
    
    widget.tk.call('option', 'add', '*Listbox.background', color_scheme.editfieldbackground, 'interactive')
    widget.tk.call('option', 'add', '*Listbox.foreground', color_scheme.editfieldforeground, 'interactive')
    widget.tk.call('option', 'add', '*Entry.background', color_scheme.editfieldbackground, 'interactive')
    widget.tk.call('option', 'add', '*Entry.foreground', color_scheme.editfieldforeground, 'interactive')
  
    widget.tk.call('option', 'add', '*tooltips*background', '#F6F6B9', 'interactive')  
    widget.tk.call('option', 'add', '*tooltips.background', '#C2C24E', 'interactive')
    
    widget.tk.call('option', 'add', '*Menu.background', color_scheme.menubackground, 'interactive')
    widget.tk.call('option', 'add', '*Menu*background', color_scheme.menubackground, 'interactive')
    widget.tk.call('option', 'add', '*Menu.highlightColor', color_scheme.menubordercolor, 'interactive')
    
    widget.tk.call('option', 'add', '*canvas_frame.highlightColor', color_scheme.normal_border, 'interactive')
    widget.tk.call('option', 'add', '*canvas_frame.highlightBackground', color_scheme.normal_border, 'interactive')
     
    widget.tk.call('option', 'add', '*Darkline.background', color_scheme.d3_dark, 'interactive')
    widget.tk.call('option', 'add', '*Lightline.background', color_scheme.d3_light, 'interactive')
   
#module self testing
if __name__ == '__main__':
    
    fonts = get_gtk_fonts()
    for item in fonts:
        print tkfont_from_list(item)
    print tkfont_from_list(['San\ Serif', ['bold', 'italic'], 10])
    scheme = ColorScheme()
    print scheme.bg
    print scheme.fg
    print scheme.selectbackground
    print scheme.selectforeground
    print scheme.normal_border
