from leveleditorlibs import tool, resources, graphics, draw, level, gui
from pyglet.window import key

class Door(tool.Tool):
    """Simple line tool"""
    
    x1, y1, x2, y2 = 0.0, 0.0, 0.0, 0.0
    key = 0
    visible = True
    
    def select(self):
        self.snap = True
        self.button_group = gui.ButtonGroup()
        
        def select_key(key):
            def select():
                self.key = key
            return select
        
        functions = []
        images = []
        for k, v in sorted(resources.key_images.items()):
            functions.append(select_key(k))
            images.append(resources.key_images[k])
        tool.generate_complex_button_row(
            resources.key_images, functions, self.button_group
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
        self.keep_drawing_static()
    
    def keep_drawing_static(self):
        draw.set_color(*resources.key_colors[self.key])
        graphics.set_line_width(5)
        draw.line(self.x1, self.y1, self.x2, self.y2)
        draw.set_color(0,0,0,1)
        graphics.set_line_width(1)
        draw.line(self.x1, self.y1, self.x2, self.y2)
    
    def stop_drawing(self, x, y):
        obj_id = level.get_id()
        new_door = level.Door(
            obj_id, self.x1, self.y1, self.x2, self.y2, self.key, self.visible
        )
        level.primitives.append(new_door)
        level.add_label(
            str(obj_id), (self.x1+self.x2)/2, (self.y1+self.y2)/2, new_door
        )
    
    def key_press(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = False
    
    def key_release(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = True

default = Door()
priority = 123
group = 'Primitives'
image = resources.Door
cursor = graphics.cursor['CURSOR_CROSSHAIR']
