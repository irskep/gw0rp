from leveleditorlibs import tool, resources
from leveleditorlibs import graphics, draw, level, gui
import pyglet, math
from pyglet.window import key

class Move(tool.Tool):
    selected_object = None
    
    def select(self):
        self.selected_object = None
        self.snap = False

    def check_snap(self, x, y):
        if self.snap:
            xb = x - x % 50
            yb = y - y % 50
            if x-xb <= 25: x = xb
            else: x = xb + 50
            if y-yb <= 25: y = yb
            else: y = yb + 50
        return x, y
    
    def start_drawing(self, x, y):
        for obj in level.simple_objects:
            if isinstance(obj.image, pyglet.image.Animation):
                w = obj.image.frames[0].image.width
                w += obj.image.frames[0].image.height
                w /= 2
            else:
                w = (obj.image.width+obj.image.height)/2
            if math.sqrt((x-obj.x)*(x-obj.x)+(y-obj.y)*(y-obj.y)) <= w/2:
                self.selected_object = obj
    
    def keep_drawing(self, x, y, dx, dy):
        x, y = self.check_snap(x,y)
        if self.selected_object != None:
            self.selected_object.set_position(x, y)
            self.selected_object.label.x = x
            self.selected_object.label.y = y

    def key_press(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = True

    def key_release(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = False

default = Move()
priority = 1
group = 'Actions'
image = resources.Move
cursor = graphics.cursor['CURSOR_DEFAULT']