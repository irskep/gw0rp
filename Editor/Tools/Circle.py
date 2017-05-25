from leveleditorlibs import tool, resources, graphics, draw, level, gui
import random, math
from pyglet.window import key

class Circle(tool.Tool):
    
    x, y, rad = 0, 0, 0
    
    visible = True
    collides = True
    
    def select(self):
        self.snap = True
        
        self.button_group = gui.ButtonGroup()
        
        def f1():
            self.collides = True
            self.visible = True
        
        def f2():
            self.collides = True
            self.visible = False
        
        def f3():
            self.collides = False
            self.visible = False
        
        
        btn_imgs = [
            resources.line_vis, resources.line_coll, resources.line_invis
        ]
        
        functions = [f1, f2, f3]
        tool.generate_button_row(
            btn_imgs, functions, self.button_group
        )
    
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
        self.x, self.y = x, y
        self.rad = 0
    
    def keep_drawing(self, x, y, dx, dy):
        x, y = self.check_snap(x,y)
        self.rad = math.sqrt((x-self.x)*(x-self.x)+(y-self.y)*(y-self.y))
        draw.set_color(0,0,0,1)
        draw.circle_outline(self.x, self.y, self.rad)
    
    def keep_drawing_static(self):
        draw.set_color(0,0,0,1)
        draw.circle_outline(self.x, self.y, self.rad)
    
    def stop_drawing(self, x, y):
        x, y = self.check_snap(x,y)
        if self.rad < 10: return
        obj_id = level.get_id()
        new_circ = level.Circle(
            obj_id, self.x, self.y, self.rad, self.visible, self.collides
        )
        level.primitives.append(new_circ)
        level.add_label(str(obj_id), self.x, self.y, new_circ)
    
    def key_press(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = False
    
    def key_release(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = True

default = Circle()
priority = 2
group = 'Primitives'
image = resources.Ellipse
cursor = graphics.cursor['CURSOR_CROSSHAIR']
