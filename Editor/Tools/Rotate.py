from leveleditorlibs import tool, resources
from leveleditorlibs import graphics, draw, level, gui
import pyglet, math

class Rotate(tool.Tool):
    selected_object = None
    
    def select(self):
        self.selected_object = None
    
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
        if self.selected_object != None:
            self.selected_object.rotation = math.degrees(
                -math.atan2(y-self.selected_object.y, x-self.selected_object.x))

default = Rotate()
priority = 2
group = 'Actions'
image = resources.Rotate
cursor = graphics.cursor['CURSOR_DEFAULT']