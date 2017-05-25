import math, sys, random
import pyglet.graphics, pyglet.image, pyglet.gl
import settings

#: set by Splatboard.py - pyglet stores cursors in an instance of Window.
cursor = {}
canvas_x, canvas_y = settings.settings['toolbar_width'], settings.settings['buttonbar_height']    
width, height = 0, 0
main_window = None
drawing = False

grid_spacing = 50

# =================
# = STATE CHANGES =
# =================
def set_cursor(new_cursor):
    main_window.set_mouse_cursor(new_cursor)

def set_line_width(width):
    pyglet.gl.glPointSize(width)
    pyglet.gl.glLineWidth(width)

