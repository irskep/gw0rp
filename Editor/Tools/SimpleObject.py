import math

from leveleditorlibs import tool, resources
from leveleditorlibs import graphics, draw, level
from leveleditorlibs import gui

class SimpleObject(tool.Tool):
    
    obj_type = level.THRUSTER
    
    def select(self):
        self.button_group = gui.ButtonGroup()
        def select_obj_type(newtype):
            def select():
                self.obj_type = newtype
            return select
        
        top_length = level.max_types_1
        images_1 = [level.obj_table[i][2] for i in xrange(top_length)]
        functions_1 = [select_obj_type(i) for i in xrange(top_length)]
        tool.generate_button_row(images_1, functions_1, self.button_group)
    
    def start_drawing(self, x, y):
        self.new_obj_id = level.get_id()
        self.new_free_obj = level.SimpleObjectSprite(
            self.new_obj_id, x, y, 0, self.obj_type
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

default = SimpleObject()
priority = 1
group = 'Objects'
image = resources.FreeThruster
cursor = graphics.cursor['CURSOR_CROSSHAIR']
