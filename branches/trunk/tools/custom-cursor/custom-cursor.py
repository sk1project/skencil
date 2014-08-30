

import gtk
import cairo

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
		self.da.connect('expose_event', self.paint)
		frame.add(self.da)
		self.add(frame)
		self.show_all()

	def paint(self, *args):
		ctx = self.da.window.cairo_create()
		ctx.set_antialias(cairo.ANTIALIAS_NONE)
		ctx.set_source_rgb(0, 0, 0)
		ctx.set_line_width(1)
		ctx.move_to(10, 10)
		ctx.line_to(10, 13)
		ctx.stroke()
		ctx.move_to(10, 10)
		ctx.line_to(13, 10)
		ctx.stroke()


win = AppWin()
win.da.window.set_cursor(win.cur)
gtk.main()
