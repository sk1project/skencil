import gtk, Tkinter


class FlatFrame(Tkinter.Frame):
	"""
	Represents flat frame which is often used in UI.
	The class just simplified UI composition.
	"""
	def __init__(self, parent=None, **kw):
		kw['borderwidth']=0
		kw['highlightthickness']=0
		kw['relief']=Tkinter.FLAT
		apply(Tkinter.Frame.__init__, (self, parent), kw)
		self['highlightcolor']=self['bg']
		self['highlightbackground']=self['bg']
		
class ColorSwatch(FlatFrame):
	
	def __init__(self,  parent=None, color='#dddddd', **kw):
		apply(FlatFrame.__init__, (self, parent), kw)
		cs_border=FlatFrame(self, bg='#000000')
		cs=FlatFrame(cs_border, bg=color, width=100, height=35)
		cs.pack(padx=1, pady=1)
		cs_border.pack()
		cs_label=Tkinter.Label(self, text=color)
		cs_label.pack()
		
class ColorCaption(FlatFrame):
	
	def __init__(self,  parent=None, color='#dddddd', **kw):
		apply(FlatFrame.__init__, (self, parent), kw)		
		cs=FlatFrame(self, width=100, height=2)
		cs.pack(padx=1, pady=1)
		cc_label=Tkinter.Label(self, text=color)
		cc_label.pack()
		
class ColorViewer(FlatFrame):
	
	def __init__(self, parent=None, text='???', color1='#dddddd', color2='#dddddd', color3='#dddddd', color4='#dddddd',  color5='#dddddd', **kw):
		apply(FlatFrame.__init__, (self, parent), kw)
		c1=ColorSwatch(self, color1)
		c2=ColorSwatch(self, color2)
		c3=ColorSwatch(self, color3)
		c4=ColorSwatch(self, color4)
		c5=ColorSwatch(self, color5)
		c5.pack(side=Tkinter.RIGHT, padx=5)
		c4.pack(side=Tkinter.RIGHT, padx=5)
		c3.pack(side=Tkinter.RIGHT, padx=5)
		c2.pack(side=Tkinter.RIGHT, padx=5)
		c1.pack(side=Tkinter.RIGHT, padx=5)
		label=Tkinter.Label(self, text=text)
		label.pack(side=Tkinter.LEFT, padx=15)
		
class ViewerCaption(FlatFrame):
	
	def __init__(self, parent=None, color1='#dddddd', color2='#dddddd', color3='#dddddd', color4='#dddddd', color5='#dddddd', **kw):
		apply(FlatFrame.__init__, (self, parent), kw)
		c1=ColorCaption(self, color1)
		c2=ColorCaption(self, color2)
		c3=ColorCaption(self, color3)
		c4=ColorCaption(self, color4)
		c5=ColorCaption(self, color5)
		c5.pack(side=Tkinter.RIGHT, padx=5)
		c4.pack(side=Tkinter.RIGHT, padx=5)
		c3.pack(side=Tkinter.RIGHT, padx=5)
		c2.pack(side=Tkinter.RIGHT, padx=5)
		c1.pack(side=Tkinter.RIGHT, padx=5)
		
def gtk_to_tk(color):
	return color[0]+color[1]+color[2]+color[5]+color[6]+color[9]+color[10]

root=Tkinter.Tk()


cv1=ViewerCaption(root, 'NORMAL', 'ACTIVE', 'PRELIGHT', 'SELECTED', 'INSENSITIVE')
cv1.pack(fill=Tkinter.X, pady=2)

w = gtk.Window()
w.realize()
style=w.get_style()

types=[gtk.STATE_NORMAL, gtk.STATE_ACTIVE, gtk.STATE_PRELIGHT, gtk.STATE_SELECTED, gtk.STATE_INSENSITIVE,]
items=[("- base ",style.base),("- text ",style.text),("- fg ",style.fg),("- bg ",style.bg),]

for item in items:
	colors=[]
	colors.append(item[0])
	for tp in types:
		fn=item[1]
		colors.append(gtk_to_tk(fn[tp].to_string()))
	print colors
	cv=ColorViewer(root, colors[0], colors[1], colors[2], colors[3], colors[4], colors[5])
	cv.pack(fill=Tkinter.X, pady=2, expand=1)

FlatFrame(root, bg='#000000', height=1).pack(fill=Tkinter.X, expand=1)

Tkinter.Label(root, text='FONT:'+style.font_desc.to_string()).pack()
root.mainloop()
	
