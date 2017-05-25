from leveleditorlibs import tool, resources, graphics, draw, level, gui
from pyglet.window import key

class LineRect(tool.Tool):
    """Simple line tool"""
    
    x1, y1, x2, y2 = 0.0, 0.0, 0.0, 0.0
    
    collides = True
    visible = True
    
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
        self.x1, self.y1 = x, y
        self.x2, self.y2 = x, y
    
    def keep_drawing(self, x, y, dx, dy):
        x, y = self.check_snap(x,y)
        self.x2, self.y2 = x, y
        draw.set_color(0,0,0,1)
        draw.rect_outline(self.x1, self.y1, self.x2, self.y2)
    
    def keep_drawing_static(self):    
        draw.set_color(0,0,0,1)
        draw.rect_outline(self.x1, self.y1, self.x2, self.y2)
    
    def stop_drawing(self, x, y):
        coord_list = (
            (self.x1, self.y1, self.x1, self.y2),
            (self.x1, self.y2, self.x2, self.y2),
            (self.x2, self.y2, self.x2, self.y1),
            (self.x2, self.y1, self.x1, self.y1)
        )
        for coords in coord_list:
            obj_id = level.get_id()
            new_line = level.Line(
                obj_id, coords[0], coords[1], coords[2], coords[3], 
                self.visible, self.collides
            )
            level.primitives.append(new_line)
            level.add_label(
                str(obj_id), (coords[0] + coords[2])/2, (coords[1] + coords[3])/2, new_line
            )
    
    def key_press(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = False
    
    def key_release(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = True

default = LineRect()
priority = 1
group = 'Primitives'
image = resources.LineRect
cursor = graphics.cursor['CURSOR_CROSSHAIR']
