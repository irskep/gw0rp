from leveleditorlibs import tool, resources, graphics, draw, level
from pyglet.window import key

class Rect(tool.Tool):
    
    x1, y1, x2, y2 = 0.0, 0.0, 0.0, 0.0
    
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
        draw.rect(self.x1, self.y1, self.x2, self.y2)
    
    def keep_drawing_static(self):
        draw.set_color(0,0,0,1)
        draw.rect(self.x1, self.y1, self.x2, self.y2)
    
    def stop_drawing(self, x, y):
        obj_id = level.get_id()
        new_rect = level.FilledRect(obj_id, self.x1, self.y1, self.x2, self.y2, True)
        level.primitives.append(new_rect)
        level.add_label(str(obj_id), (self.x1+self.x2)/2, (self.y1+self.y2)/2, new_rect)
    
    def key_press(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = False
    
    def key_release(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = True

default = Rect()
priority = 1
group = 'Shapes'
image = resources.FilledRect
cursor = graphics.cursor['CURSOR_CROSSHAIR']
