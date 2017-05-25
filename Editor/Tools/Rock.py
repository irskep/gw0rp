import math
from leveleditorlibs import tool, resources
from leveleditorlibs import graphics, draw, level
from leveleditorlibs import gui

class Rock(tool.Tool):
    
    rock_type = 1
    
    def select(self):
        self.button_group = gui.ButtonGroup()
        num = 7
        images = [getattr(resources, "t_rock_"+str(i+1)) for i in xrange(num)]
        def select_obj_type(newtype):
            def select():
                self.rock_type = newtype
            return select
        
        functions = [select_obj_type(i) for i in xrange(num)]
        tool.generate_button_row(images, functions, self.button_group)
    
    def start_drawing(self, x, y):
        self.new_obj_id = level.get_id()
        self.new_free_obj = level.RockSprite(
            self.new_obj_id, x, y, 0, self.rock_type
        )
        level.simple_objects.append(self.new_free_obj)

    def keep_drawing(self, x, y, dx, dy):    
        self.new_free_obj.rotation = math.degrees(
            -math.atan2(y-self.new_free_obj.y, x-self.new_free_obj.x)
        )
    
    def stop_drawing(self, x, y):
        level.add_label(
            str(self.new_obj_id), 
            self.new_free_obj.x, self.new_free_obj.y, 
            self.new_free_obj
        )

default = Rock()
priority = 3
group = 'Objects'
image = resources.t_rock_1
cursor = graphics.cursor['CURSOR_CROSSHAIR']
