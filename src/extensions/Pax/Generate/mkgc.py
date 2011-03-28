#! /usr/bin/env python

def drawfn(pname, *argtypes):
	returntype = 'void'
	fname = 'X' + pname
	otype = 'PaxGC'
	#
	# -- function heading
	write('static PyObject *\n')
	write(Prefix, '_', pname,
	      '(', otype, 'Object * self, PyObject *args)\n')
	write('{\n')
	#
	# -- declare result
	if returntype <> 'void':
		write('\t', returntype, ' result;\n')
	#
	# -- declare arguments, collect argument info
	arglist = []
	fmtlist = ''
	nextarg = 1
	for argtype in argtypes:
		if argtype == '*':
			argname = 'self'
		elif argtype == '0':
			argname = '0'
		else:
			argname = 'arg%d' % nextarg
			nextarg = nextarg + 1
		declare(argtype, argname)
		fmtlist = fmtlist + typedefs[argtype][FMT]
		arglist.append((argtype, argname))
	#
	# -- extract arguments, return if failure
	write('\tif (!PyArg_ParseTuple(args, "', fmtlist, '"')
	for argtype, argname in arglist:
		if argname not in ('0', 'self'):
			write(',\n')
			write('\t\t\t&', argname)
	write('))\n')
	write('\t\treturn NULL;\n')
	#
	# -- check structure arguments, return if failure
	for argtype, argname in arglist:
		check(argtype, argname)
	#
	# -- call the function, with setjmp handling around
	#write('\tif (!setjmp(jump_where)) {\n')
	#write('\t\tjump_flag = 1;\n')
	#write('\t\t')
	if returntype != 'void':
		write('result = ')
	write(fname, '(self->display, self->drawable, self->gc')
	sep = ',\n\t\t\t'
	for argtype, argname in arglist:
		write(sep, extract(argtype, argname))
	write(');\n')
	#write('\t\tjump_flag = 0;\n')
	#write('\t}\n')
	#
	# -- clean up afterwards
	for argtype, argname in arglist:
		cleanup(argtype, argname)
	#
	# -- error return if long-jumped
	#write('\tif (jump_flag) { jump_flag = 0; return NULL; }\n')
	#
	# -- return result
	if returntype == 'void':
		write('\tPy_INCREF(Py_None);\n')
	write('\treturn ', create(returntype, 'result'), ';\n')
	#
	# -- end of function body
	write('}\n')
	write('\n')
	#
	# -- administration
	List.append(pname)

def gcfn(pname, *argtypes):
	returntype = 'void'
	fname = 'X' + pname
	otype = 'PaxGC'
	#
	# -- function heading
	write('static PyObject *\n')
	write(Prefix, '_', pname, '(', otype, 'Object *self, PyObject*args)\n')
	write('{\n')
	#
	# -- declare result
	if returntype <> 'void':
		write('\t', returntype, ' result;\n')
	#
	# -- declare arguments, collect argument info
	arglist = []
	fmtlist = ''
	nextarg = 1
	for argtype in argtypes:
		if argtype == '*':
			argname = 'self'
		elif argtype == '0':
			argname = '0'
		else:
			argname = 'arg%d' % nextarg
			nextarg = nextarg + 1
		declare(argtype, argname)
		fmtlist = fmtlist + typedefs[argtype][FMT]
		arglist.append((argtype, argname))
	#
	# -- check non-shared object
	write('\tif (self->shared) {\n')
	write('\t\tPyErr_SetString(PyExc_TypeError, "can\'t modify shared GC");\n')
	write('\t\treturn NULL;\n')
	write('\t}\n')
	#
	# -- extract arguments, return if failure
	write('\tif (!PyArg_ParseTuple(args, "', fmtlist, '"')
	for argtype, argname in arglist:
		if argname not in ('0', 'self'):
			write(',\n')
			write('\t\t\t&', argname)
	write('))\n')
	write('\t\treturn NULL;\n')
	#
	# -- check structure arguments, return if failure
	for argtype, argname in arglist:
		check(argtype, argname)
	#
	# -- call the function, with setjmp handling around
	#write('\tif (!setjmp(jump_where)) {\n')
	#write('\t\tjump_flag = 1;\n')
	#write('\t\t')
	if returntype != 'void':
		write('result = ')
	if fname == 'XPutImage':
		# special case for XPutImage
		write(fname, '(self->display, self->drawable, self->gc')
	else:
		write(fname, '(self->display, self->gc')
	sep = ',\n\t\t\t'
	for argtype, argname in arglist:
		write(sep, extract(argtype, argname))
	write(');\n')
	#write('\t\tjump_flag = 0;\n')
	#write('\t}\n')
	#
	# -- clean up afterwards
	for argtype, argname in arglist:
		cleanup(argtype, argname)
	#
	# -- error return if long-jumped
	#write('\tif (jump_flag) { jump_flag = 0; return NULL; }\n')
	#
	# -- return result
	if returntype == 'void':
		write('\tPy_INCREF(Py_None);\n')
	write('\treturn ', create(returntype, 'result'), ';\n')
	#
	# -- end of function body
	write('}\n')
	write('\n')
	#
	# -- administration
	List.append(pname)

from mktools import setprefix, setfile
setfile('gcmethods.c')
setprefix('PaxGC', 'X')

from mktools import *

write('#define checkshortlist pax_checkshortlist\n')

drawfn('DrawArc', 'int', 'int', 'unsigned int', 'unsigned int',
       'int', 'int')
drawfn('DrawArcs', 'XArc[]')
drawfn('DrawImageString', 'int', 'int', 'char[]')
drawfn('DrawLine', 'int', 'int', 'int', 'int')
drawfn('DrawLines', 'XPoint[]', 'int')
drawfn('DrawPoint', 'int', 'int')
drawfn('DrawPoints', 'XPoint[]', 'int')
drawfn('DrawRectangle', 'int', 'int', 'unsigned int', 'unsigned int')
drawfn('DrawRectangles', 'XRectangle[]')
drawfn('DrawSegments', 'XSegment[]')
drawfn('DrawString', 'int', 'int', 'char[]')
#drawfn('DrawText', 'int', 'int', 'XTextItem[]')
drawfn('FillArc', 'int', 'int', 'unsigned int', 'unsigned int',
       'int', 'int')
drawfn('FillArcs', 'XArc[]')
drawfn('FillPolygon', 'XPoint[]', 'int', 'int')
drawfn('FillRectangle', 'int', 'int', 'unsigned int', 'unsigned int')
drawfn('FillRectangles', 'XRectangle[]')
drawfn('PutImage', 'XImage', 'int', 'int', 'int', 'int', 'int', 'int')
# XXX omitted Text16/String16 variants

gcfn('ChangeGC', 'XGCValues#')
gcfn('SetArcMode', 'int')
gcfn('SetBackground', 'unsigned long')
gcfn('SetClipOrigin', 'int', 'int')
gcfn('SetClipRectangles', 'int', 'int', 'XRectangle[]', 'int')
#gcfn('SetDashes', 'int', 'char[]')
gcfn('SetFillRule', 'int')
gcfn('SetFillStyle', 'int')
gcfn('SetFont', 'Font')
gcfn('SetForeground', 'unsigned long')
gcfn('SetFunction', 'int')
gcfn('SetGraphicsExposures', 'Bool')
gcfn('SetLineAttributes', 'unsigned int', 'int', 'int', 'int')
gcfn('SetPlaneMask', 'unsigned long')
gcfn('SetRegion', 'Region')
gcfn('SetState', 'unsigned long', 'unsigned long', 'int', 'unsigned long')
gcfn('SetStipple', 'Pixmap')
gcfn('SetSubwindowMode', 'int')
gcfn('SetTSOrigin', 'int', 'int')
gcfn('SetTile', 'Pixmap')

myfunction('', 'SetDrawable', 'PyObject*')
myfunction('', 'SetDashes')
myfunction('', 'SetForegroundAndFill')
myfunction('', 'SetClipMask')
myfunction('', 'ShmPutImage')

dolist()

