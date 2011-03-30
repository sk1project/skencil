

import gtk

class AppWin(gtk.Window):
	def __init__(self):
		gtk.Window.__init__(self)

		self.connect("destroy", gtk.main_quit)
		self.set_size_request(250, 150)
		self.set_position(gtk.WIN_POS_CENTER)
		icon = 'shaper.png'
		self.cur = gtk.gdk.Cursor(gtk.gdk.display_get_default(),
							gtk.gdk.pixbuf_new_from_file(icon),
							 5, 5)
		frame = gtk.Frame()
		frame.set_property('shadow', gtk.SHADOW_IN)
		frame.set_border_width(20)
		self.da = gtk.DrawingArea()
		self.da.set_size_request(200, 100)
		frame.add(self.da)
		self.add(frame)
		self.show_all()

win = AppWin()
win.da.window.set_cursor(win.cur)
gtk.main()
