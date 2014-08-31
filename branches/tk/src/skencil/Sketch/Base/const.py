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
#	Constants...
#

#
#	Types of handles
#

# physical
# for rect handles: filled == handle_id & 1
Handle_OpenRect		= 0
Handle_FilledRect	= 1
Handle_SmallOpenRect	= 2
Handle_SmallFilledRect	= 3

Handle_OpenCircle	= 4
Handle_FilledCircle	= 5
Handle_SmallOpenCircle	= 6
Handle_SmallFilledCircle = 7

Handle_SmallOpenRectList = 8

Handle_Line		= 9
Handle_Pixmap		= 10
Handle_Caret		= 11
Handle_PathText         = 12

# logical	XXX should these be moved to config.py?
Handle			= Handle_FilledRect
HandleNode		= Handle_OpenRect
HandleSelectedNode	= Handle_FilledRect
HandleControlPoint	= Handle_SmallFilledRect
HandleLine		= Handle_Line
HandleCurvePoint        = Handle_FilledCircle

#
#
#

# The corners of the unit rectangle
corners = [(0, 0), (1, 0), (1, 1), (0, 1)]


#
#	Standard channel names
#

# common
CHANGED = 'CHANGED'
DOCUMENT = 'DOCUMENT'
MODE = 'MODE'
SELECTION = 'SELECTION'

# dialogs
CLOSED = 'CLOSED'

# TKExt
COMMAND = 'COMMAND'
# also uses SELECTION

# APPLICATION
CLIPBOARD = 'CLIPBOARD'
ADD_TO_SPECIAL_MENU = 'ADD_TO_SPECIAL_MENU'

# Global
INITIALIZE = 'INITIALIZE'
APP_INITIALIZED = 'APP_INITIALIZED'
INIT_READLINE = 'INIT_READLINE'


# CANVAS
STATE = 'STATE'
UNDO = 'UNDO'
VIEW = 'VIEW'
POSITION = 'POSITION'
CURRENTINFO = 'CURRENTINFO'

# DOCUMENT
EDITED = 'EDITED'
GRID = 'GRID'
LAYER = 'LAYER'
LAYER_STATE = 'LAYER_STATE';	LAYER_ORDER = 'LAYER_ORDER'
LAYER_COLOR = 'LAYER_COLOR';	LAYER_ACTIVE = 'LAYER_ACTIVE'
LAYOUT = 'LAYOUT'
REDRAW = 'REDRAW'
STYLE = 'STYLE'
UNDO = 'UNDO'
GUIDE_LINES = 'GUIDE_LINES'


# graphics object
#TRANSFORMED = 'TRANSFORMED'

# command
UPDATE = 'update'

# palette
COLOR1 = 'color1'
COLOR2 = 'color2'

# Drop types
DROP_COLOR = 'COLOR'


#
#       Scripting Access
#

SCRIPT_UNDO = 'SCRIPT_UNDO'
SCRIPT_GET = 'SCRIPT_GET'
SCRIPT_OBJECT = 'SCRIPT_OBJECT'
SCRIPT_OBJECTLIST = 'SCRIPT_OBJECTLIST'

#
#	constants for selections
#

# the same as in curveobject.c
SelectSet = 0
SelectAdd = 1
SelectSubtract = 2
SelectSubobjects = 3
SelectDrag = 4

SelectGuide = 5

# Arc modes. bezier_obj.approx_arc uses these
ArcArc = 0
ArcChord = 1
ArcPieSlice = 2

#
#	X specific stuff
#

import X

ShiftMask = X.ShiftMask
LockMask = X.LockMask
ControlMask = X.ControlMask
Mod1Mask = X.Mod1Mask
Mod2Mask = X.Mod2Mask
Mod3Mask = X.Mod3Mask
Mod4Mask = X.Mod4Mask
Mod5Mask = X.Mod5Mask
MetaMask = Mod1Mask

Button1Mask = X.Button1Mask
Button2Mask = X.Button2Mask
Button3Mask = X.Button3Mask
Button4Mask = X.Button4Mask
Button5Mask = X.Button5Mask
AllButtonsMask = Button1Mask | Button2Mask | Button3Mask

Button1 = X.Button1
Button2 = X.Button2
Button3 = X.Button3
Button4 = X.Button4
Button5 = X.Button5

ContextButton	= Button3
ContextButtonMask = Button3Mask

AllowedModifierMask = ShiftMask | ControlMask | MetaMask
ConstraintMask = ControlMask
AlternateMask = ShiftMask
AddSelectionMask = ShiftMask
SubtractSelectionMask = ControlMask
SubobjectSelectionMask = ShiftMask | ControlMask

#
#	Line Styles
#

JoinMiter	= X.JoinMiter
JoinRound	= X.JoinRound
JoinBevel	= X.JoinBevel
CapButt		= X.CapButt
CapRound	= X.CapRound
CapProjecting	= X.CapProjecting


# cursors

CurStd		= 'top_left_arrow'
CurHandle	= 'crosshair'
CurTurn		= 'exchange'
CurPick		= 'draft_small'
CurCreate	= 'pencil'
CurPlace	= 'crosshair'
CurDragColor	= 'spraycan'
CurHGuide       = 'sb_v_double_arrow'
CurVGuide       = 'sb_h_double_arrow'
CurZoom		= 'circle'	# is replaced by bitmap specification in
				# skpixmaps.py
# CurEdit, CurUp, CurDown and CurUpDown are also added by skpixmaps.py

# unused as yet
CurHelp		= 'question_arrow'
CurWait		= 'watch'
CurMove		= 'fleur'
