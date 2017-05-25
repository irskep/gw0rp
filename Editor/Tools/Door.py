import math
from leveleditorlibs import tool, resources, graphics, draw, level, gui
from pyglet.window import key

class Door(tool.Tool):
    """Simple line tool"""
    
    x1, y1, x2, y2 = 0.0, 0.0, 0.0, 0.0
    which_door = 0
    visible = True
    
    def select(self):
        self.snap = False
        self.button_group = gui.ButtonGroup()
        
        self.doors = [
            (0, 'Door2_R_Static'),
            (3, 'Door3_G_Static'),
            (4, 'Door1_B_1'),
            (5, 'Door2_P_Static')
        ]

        door_buttons = [
            getattr(resources, "t_"+self.doors[i][1]) \
            for i in range(len(self.doors))
        ]
        
        def select_door(num):
            def select():
                self.which_door = num
            return select
        
        functions = []
        for i in range(len(self.doors)):
            functions.append(select_door(i))
        tool.generate_button_row(
            door_buttons, functions, self.button_group
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
        self.new_obj_id = level.get_id()
        self.new_free_obj = level.ImageDoorSprite(
            self.new_obj_id, self.doors[self.which_door][0],
            x, y, 0
        )
        level.simple_objects.append(self.new_free_obj)
    
    def keep_drawing(self, x, y, dx, dy):
        x, y = self.check_snap(x,y)
        self.new_free_obj.rotation = math.degrees(
            -math.atan2(y-self.new_free_obj.y, x-self.new_free_obj.x)
        )
    
    def stop_drawing(self, x, y):
        level.add_label(
            str(self.new_obj_id), 
            self.new_free_obj.x, self.new_free_obj.y, 
            self.new_free_obj
        )
    
    def key_press(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = True
    
    def key_release(self, symbol, modifiers):
        if symbol == key.LSHIFT:
            self.snap = False

default = Door()
priority = 6
group = 'Primitives'
image = resources.t_Door2_R_Static
cursor = graphics.cursor['CURSOR_CROSSHAIR']
