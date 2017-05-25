from leveleditorlibs import tool, resources, graphics, draw, level
from pyglet.window import key

class RightTriangle(tool.Tool):
    
    x1, y1, x2, y2 = 0.0, 0.0, 0.0, 0.0
    snap = True
    
    def select(self):
        self.snap = True
    
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
        x, y = self.check_snap(x,y)
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x, y
    
    def keep_drawing(self, x, y, dx, dy):
        x, y = self.check_snap(x,y)
        self.x2, self.y2 = x, y
        draw.set_color(0,0,0,1)
        draw.polygon((self.x1, self.y1, self.x2, self.y1, self.x1, self.y2))
    
    def keep_drawing_static(self):
        draw.set_color(0,0,0,1)
        draw.polygon((self.x1, self.y1, self.x2, self.y1, self.x1, self.y2))
    
    def stop_drawing(self, x, y):
        obj_id = level.get_id()
        new_triangle = level.FilledTriangle(obj_id, self.x1, self.y1, 
                                                self.x2, self.y1, 
                                                self.x1, self.y2, True)
        level.primitives.append(new_triangle)
        label_x = (self.x2-self.x1)/4 + self.x1
        label_y = (self.y2-self.y1)/4 + self.y1
        level.add_label(str(obj_id), label_x, label_y, new_triangle)
    
    def key_press(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = False
    
    def key_release(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = True

default = RightTriangle()
priority = 1
group = 'Shapes'
image = resources.FilledTriangle
cursor = graphics.cursor['CURSOR_CROSSHAIR']
