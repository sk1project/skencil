# Tools for generating files of C functions.

import sys

# Output functions

Outfp = sys.stdout

def setfile(filename):
	global Outfp
	Outfp = open(filename, 'w')

def write(*args):
	for s in args:
		Outfp.write(s)

def writef(fmt, *args):
	write(fmt % args)

# Stuff for doing various things to types defined in typedefs

from typedefs import *

def declare(type, name):
	if name == '0':
		return
	s = typedefs[type][DCL]
	if s:
		write('\t', s%{'arg':name}, ';\n')

def check(type, name, returntype = ''):
	dict = {'arg': name}
	if type == 'argdict':
		if returntype == 'Widget':
			dict['w'] = 'NULL'
		else:
			dict['w'] = 'w'
	s = typedefs[type][CHK]
	if not s:
		pass
	elif s[-1] == ';':
		write('\t', s%{'arg':name}, '\n')
	else:
		write('\tif (!', s % dict, ') {\n')
		write('\t\tif (!PyErr_Occurred())\n')
		if type == '*':
			write('\t\t\tPyErr_SetString(PyExc_RuntimeError, "',
			      'widget already destroyed");\n')
		else:
			write('\t\t\tPyErr_SetString(PyExc_TypeError, "', name,
			      ' should be ', type, '");\n')
		write('\t\treturn NULL;\n')
		write('\t}\n')

def extract(type, name):
	s = typedefs[type][EXT]
	if '%' in s:
		return s%{'arg':name}
	elif s:
		return s
	else:
		return name

def create(type, name):
	s = typedefs[type][CRE]
	if s:
		return s%{'arg':name}
	else:
		return 'Py_None'

def cleanup(type, name):
	item = typedefs[type]
	if len(item) > CLE:
		s = item[CLE]
		if s:
			write('\t', s%{'arg':name}, ';\n')

# Stuff to generate wrappers around C functions and add them to method chain

Prefix = None
SaveList = List = []
Lists = []
Skip = None

def setprefix(prefix, skip):
	global Prefix, List, SaveList, Skip
	Prefix = prefix
	Skip = skip
	List = SaveList
	del List[:]
	write('\n')
	write('/* automatically generated by ', sys.argv[0], ' */\n')
	write('/* ', 'Methods for ', Prefix, ' objects */\n')
	write('\n')

def setlist(list = None):
	global List
	if list is None:
		List = SaveList
	else:
		List = list

def dotaggedfunction(tag, returntype, fname, *argtypes):
	write('#if ', tag, '\n')
	apply(dofunction, (returntype, fname) + argtypes)
	write('#endif /* ', tag, ' */\n')
	List[-1] = (tag, List[-1])

def dofunction(returntype, fname, *argtypes):
	pname = fname
	if pname[:len(Skip)] == Skip: pname = pname[len(Skip):]
	if '*' in argtypes:
		otype = Prefix
	else:
		otype = ''
	#
	# -- function heading
	write('static PyObject *\n')
	write(Prefix, '_', pname, '(')
	if otype:
		write(otype, 'object *self, ')
	else:
		write('PyObject *self, ')
	write('PyObject *args)\n')
	write('{\n')
	#
	# -- declare result
	retlist = []
	if returntype <> 'void':
		if returntype == 'SUCCESS':
			r = 'Boolean'
		else:
			retlist.append((returntype, 'result'))
			r = returntype
		write('\t', r, ' result;\n')
	#
	# -- declare arguments, collect argument info
	arglist = []
	fmtlist = ''
	nextarg = 1
	winitialized = wCinitialized = 0
	newargtypes = []
	argdict = None
	for argtype in argtypes:
		if argtype == '*':
			argname = 'self'
		elif argtype[-1] == '0':
			argname = '0'
		else:
			argname = 'arg%d' % nextarg
			nextarg = nextarg + 1
		if argtype[:7] == 'argdict':
			import string
			argdict = string.splitfields(argtype[8:], ',')
			if argdict[0] == '':
				del argdict[0]
			write('\tWidget w;\n')
			if len(argdict) > 0:
				write('\tWidgetClass wClist[%d];\n' % len(argdict))
			else:
				write('\tWidgetClass wClist[1];\n')
			argtype = 'argdict'
		arglist.append((argtype, argname))
		if argtype[0] == '>':
			# output parameter
			argtype = argtype[1:]
			retlist.append((argtype, argname))
		else:
			# input parameter
			fmtlist = fmtlist + typedefs[argtype][FMT]
		declare(argtype, argname)
		newargtypes.append(argtype)
	argtypes = tuple(newargtypes)
	if len(retlist) > 1:
		write('\tPyObject *retval;\n')
	elif returntype not in ('void', 'SUCCESS') and \
	     len(typedefs[returntype]) > RCL:
		write('\tPyObject *retval;\n')
	if argdict is not None and len(argdict) > 0:
		for i in range(len(argdict)):
			write('\twClist[%d] = %s;\n' % (i, argdict[i]))
		wCinitialized = 1
	if returntype == 'Widget' and argdict is None:
		write('\tPyObject *dict = NULL;\n')
	#
	# -- extract arguments, return if failure
	write('\tif (!PyArg_ParseTuple(args, "', fmtlist, '"')
	for argtype, argname in arglist:
		if argname not in ('0', 'self') and argtype[0] != '>':
			write(',\n')
			write('\t\t\t&', argname)
	write('))\n')
	write('\t\treturn NULL;\n')
	#
	# -- check structure arguments, return if failure
	for argtype, argname in arglist:
		if argtype[0] == '>':
			continue
		check(argtype, argname, returntype)
		if 'argdict' not in argtypes:
			continue
		if argtype == '*':
			write('\tw = self->ob_widget;\n')
			winitialized = 1
			if not wCinitialized and \
			   'WidgetClass' not in argtypes:
				write('\twClist[0] = XtClass(w);\n')
				wCinitialized = 1
		elif argtype == 'Widget':
			write('\tw = getwidgetvalue(', argname, ');\n')
			winitialized = 1
			if not wCinitialized and \
			   'WidgetClass' not in argtypes and \
			   '*' not in argtypes:
				write('\twClist[0] = XtClass(w);\n')
				wCinitialized = 1
		elif argtype == 'WidgetClass':
			if not winitialized and '*' not in argtypes and \
			   'Widget' not in argtypes:
				write('\tw = NULL;\n')
				winitialized = 1
			write('\twClist[0] = getwclassvalue(',
				  argname, ');\n')
			wCinitialized = 1
	#
	# -- call the function, with setjmp handling around
	write('\tif (!setjmp(jump_where)) {\n')
	write('\t\tjump_flag = 1;\n')
	write('\t\t')
	if returntype != 'void':
		write('result = ')
	write(fname, '(')
	sep = ''
	for argtype, argname in arglist:
		if argtype == 'argdict':
			if not winitialized and not wCinitialized:
				raise RuntimeError, \
		  '\'argdict\' must be preceded by Widget or WidgetClass arg'
		if argtype == '*' and 'argdict' in argtypes:
			write(sep, 'w')
		else:
			write(sep)
			if argtype[0] == '>':
				write('&')
				argtype = argtype[1:]
			write(extract(argtype, argname))
		sep = ',\n\t\t\t'
	write(');\n')
	write('\t\tjump_flag = 0;\n')
	write('\t}\n')
	#
	# -- clean up afterwards
	for argtype, argname in arglist:
		if argtype[0] == '>':
			argtype = argtype[1:]
		cleanup(argtype, argname)
	#
	# -- error return if long-jumped
	write('\tif (jump_flag || PyErr_Occurred()) { jump_flag = 0; return NULL; }\n')
	#
	# -- do something about argdicts
	if fname[2:2+6] == 'Create' and 'argdict' in argtypes:
		for argtype, argname in arglist:
			if argtype == 'argdict':
##				write('\tinit_res_dict(result, wClist, sizeof(wClist)/sizeof(wClist[0]));\n')
				break

	if returntype == 'SUCCESS':
		write('\tif (!result) {\n')
		write('\t\tPy_INCREF(Py_None);\n')
		write('\t\treturn Py_None;\n')
		write('\t}\n')
	#
	# return result
	if len(retlist) > 1:
		write('\tretval = PyTuple_New(',`len(retlist)`,');\n')
		for i in range(len(retlist)):
			argtype, argname = retlist[i]
			write('\tPyTuple_SetItem(retval, ', `i`, ', ',
			      create(argtype, argname),');\n')
		write('\tif (PyErr_Occurred()) {\n')
		write('\t\tPy_XDECREF(retval);\n')
		write('\t\treturn NULL;\n')
		write('\t}\n')
		write('\treturn retval;\n')
	elif len(retlist) == 1:
		if returntype not in ('void', 'SUCCESS') and \
		   len(typedefs[returntype]) > RCL:
			write('\tretval = ',
			      create(retlist[0][0], retlist[0][1]), ';\n')
			s = typedefs[returntype][RCL]
			if s:
				write('\t', s%{'arg':retlist[0][1]}, ';\n')
			write('\treturn retval;\n')
		else:
			write('\treturn ',
			      create(retlist[0][0], retlist[0][1]), ';\n')
	else:
		write('\tPy_INCREF(Py_None);\n\treturn Py_None;\n')
	#
	# -- end of function body
	write('}\n')
	write('\n')
	#
	# -- administration
	List.append(pname)

def mytaggedfunction(tag, returntype_unused, fname, *args_unused):
	apply(myfunction, (returntype_unused, fname) +args_unused)
	List[-1] = (tag, List[-1])

def myfunction(returntype_unused, fname, *args_unused):
	pname = fname
	if pname[:len(Skip)] == Skip: pname = pname[len(Skip):]
	List.append(pname)

def listsort(a, b):
	if type(a) == type(()):
		a = a[1]
	if type(b) == type(()):
		b = b[1]
	if a < b:
		return -1
	elif a == b:
		return 0
	else:
		return 1

def dolist(listname = None, widgetClass = None, superchain = 'widget'):
	if listname is None:
		listname = Prefix
	write('static PyMethodDef ', listname, '_methods[] = {\n')
	List.sort(listsort)
	for pname in List:
		tag = ''
		if type(pname) == type(()):
			tag, pname = pname
		if tag: write('#if ', tag, '\n')
		writef('\t{"%s", (PyCFunction)%s_%s, 1},\n',
		       pname, Prefix, pname)
		if tag: write('#endif /* ', tag, ' */\n')
	write('\t{0, 0} /* Sentinel */\n')
	write('};\n')
	if widgetClass:
		if type(widgetClass) == type(''):
			widgetClass = [widgetClass]
		write('PyMethodChain ',
		      listname, '_methodchain = {\n')
		write('\t', listname, '_methods,\n')
		write('\t&', superchain, '_methodchain,\n')
		write('};\n')
		Lists.append((listname, widgetClass))
	write('\n')
	del List[:]
	if listname is not Prefix or widgetClass is not None:
		setlist()

def dotaggedlist(tag, listname = None, widgetClass = None, superchain = 'widget'):
	write('#if ', tag, '\n')
	dolist(listname, widgetClass, superchain)
	write('#endif /* ', tag, ' */\n')
	if widgetClass:
		Lists[-1] = (tag, Lists[-1])

# Stuff to generate complete widget set modules (e.g. Xm, Xaw)

Widgets = []
Mname, Wname, Cname, Includef, Classnamef, Mskip = \
	  None, None, None, None, None, None

def initwidgetset(mname, wname, cname, includef, classnamef, mskip):
	global Mname, Wname, Cname, Includef, Classnamef, Widgets, Mskip
	Mname, Wname, Cname, Includef, Classnamef, Mskip = \
		  mname, wname, cname, includef, classnamef, mskip
	del Widgets[:]

def widgetset(mname, wname, cname, includef, classnamef, mskip):
	initwidgetset(mname, wname, cname, includef, classnamef, mskip)
	setfile(Mname + 'module.c')
	write('/* Widget Set ', Mname, ' */\n')
	write('\n')
	write('#include "Python.h"\n')
	write('#include "modsupport.h"\n')
	write('#include "import.h"\n')
	write('#include "widgetobject.h"\n')
	write('\n')
	write('#define is_optwidgetobject(x)\t((x) == Py_None || is_widgetobject(x))\n')
	write('#define getoptwidgetvalue(x)\t((x) == Py_None ? NULL : getwidgetvalue(x))\n')
	write('\n')


def setmoduleprefix():
	setprefix(Mname, Mskip)

def setwidgetprefix():
	setprefix(Wname, Mskip)

def setwclassprefix():
	setprefix(Cname, Mskip)

def dotaggedwidget(tag, name, fname = '', cname = ''):
	write('#if ', tag, '\n')
	dowidget(name, fname, cname)
	write('#endif /* ', tag, ' */\n')
	Widgets[-1] = (tag, Widgets[-1])

def dowidget(name, fname = '', cname = ''):
	if fname == '': fname = name
	if cname == '':
		if type(Classnamef) == type(''):
			cname = Classnamef % name
		else:
			cname = Classnamef(name)
		cname = cname + 'WidgetClass'
	if fname <> None:
		include = Includef % fname
		write('#include ', include, '\n')
		write('\n')
	Widgets.append((name, cname))

initextras = []

def endwidgetset(listname = None):
	if listname is None:
		listname = Wname
	write('\n')
	write('PyMethodChain ', listname, '_methodchain = {\n')
	write('\t', listname, '_methods,\n')
	write('\tNULL,\n')
	write('};\n')
	write('PyMethodChain ', Cname, '_methodchain = {\n')
	write('\t', Cname, '_methods,\n')
	write('\t&wclass_methodchain,\n')
	write('};\n')
	write('\n')
	write('void\ninit', Mname, '()\n{\n')
	write('\tPyObject *m, *d;\n')
	write('\tm = PyImport_ImportModule("Xt");\n')
	write('\tif (m == NULL)\n')
	write('\t\tPy_FatalError("can\'t import module Xt for %s");\n' % Mname)
	write('\tPy_DECREF(m);\n')
	write('\tm = Py_InitModule("', Mname, '", ', Mname, '_methods);\n')
	write('\td = PyModule_GetDict(m);\n')
	write('\tadd_widget_methodchain(&', listname, '_methodchain);\n')
	makewidgets()
	write('}\n')

def widgetsort(a, b):
	if type(a[1]) == type(()):
		a = a[1]
	if type(b[1]) == type(()):
		b = b[1]
	a = a[0]
	b = b[0]
	if a < b:
		return -1
	elif a == b:
		return 0
	else:
		return 1

def makewidgets():
	Widgets.sort(widgetsort)
	for entry in Widgets:
		tag = ''
		if type(entry[1]) == type(()):
			tag, (name, cname) = entry
		else:
			name, cname = entry
		if tag: write('#if ', tag, '\n')
		write('\tPyDict_SetItemString(d, "', name, '",\n')
		write('\t\t(PyObject*)newwclassobject(', cname, ',\n')
		write('\t\t\t&', Cname, '_methodchain));\n')
		if tag: write('#endif /* ', tag, ' */\n')
	for line in initextras:
		write('\t' + line + '\n');
	for entry in Lists:
		tag = None
		if type(entry[1]) == type(()):
			tag, entry = entry
		name, wClist = entry
		if tag: write('#if ', tag, '\n')
		for wC in wClist:
			write('\twidgetchainlist(', wC, ', &', name,
			      '_methodchain);\n')
		if tag: write('#endif /* ', tag, ' */\n')
