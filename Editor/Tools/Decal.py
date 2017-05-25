import math

from leveleditorlibs import tool, resources
from leveleditorlibs import graphics, draw, level
from leveleditorlibs import gui

class Decal(tool.Tool):
    
    decal_name = 1
    
    def select(self):
        self.button_group = gui.ButtonGroup()
        images = []
        names = []
        for decal in resources.decals:
            images.append(getattr(resources, 't_'+decal))
            names.append(decal)
        def select_obj_type(newtype):
            def select():
                self.decal_name = newtype
            return select
        
        functions = [select_obj_type(s) for s in names]
        tool.generate_button_row(images, functions, self.button_group)
    
    def start_drawing(self, x, y):
        self.obj_id = level.get_id()
        self.new_free_obj = level.DecalSprite(
            self.obj_id, x, y, 0.0, 1.0, self.decal_name
        )
        level.simple_objects.append(self.new_free_obj)
    
    def keep_drawing(self, x, y, dx, dy):    
        self.new_free_obj.rotation = math.degrees(
            -math.atan2(y-self.new_free_obj.y, x-self.new_free_obj.x)
        )
    
    def stop_drawing(self, x, y):    
        level.add_label(
            str(self.obj_id), 
            self.new_free_obj.x, self.new_free_obj.y, 
            self.new_free_obj
        )

default = Decal()
priority = 3
group = 'Objects'
image = resources.t_target_thumb
cursor = graphics.cursor['CURSOR_CROSSHAIR']
