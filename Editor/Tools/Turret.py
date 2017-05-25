import math

from leveleditorlibs import tool, resources
from leveleditorlibs import graphics, draw, level
from leveleditorlibs import gui

class Turret(tool.Tool):
    
    turret_type = 0
    base_type = 0
    
    def select(self):
        self.base_button_group = gui.ButtonGroup()
        self.turret_button_group = gui.ButtonGroup()
        def attr_setter(attr_name, newtype):
            def select():
                setattr(self, attr_name, newtype)
            return select
        
        images_1 = [
            getattr(resources, 't_'+level.turrets[i][0]) \
            for i in range(len(level.turrets))
        ]
        functions_1 = [
            attr_setter('turret_type', i) \
            for i in range(len(level.turrets))
        ]
        tool.generate_button_row(
            images_1, functions_1, self.turret_button_group
        )    
        
        images_2 = [
            getattr(resources, 't_'+level.turret_bases[i][0]) \
            for i in range(len(level.turret_bases))
        ]
        functions_2 = [
            attr_setter('base_type', i) \
            for i in range(len(level.turret_bases))
        ]
        tool.generate_button_row(
            images_2, functions_2, self.base_button_group, start_y=5
        )
    
    def start_drawing(self, x, y):
        self.new_obj_id = level.get_id()
        self.new_free_obj = level.TurretSprite(
            self.new_obj_id, x, y, 0, self.turret_type, self.base_type
        )
        level.simple_objects.append(self.new_free_obj)
    
    def keep_drawing(self, x, y, dx, dy):
        self.new_free_obj.rotation = math.degrees(
            -math.atan2(y-self.new_free_obj.y, x-self.new_free_obj.x)
        )
        self.new_free_obj.base_sprite.rotation = self.new_free_obj.rotation
    
    def stop_drawing(self, x, y):
        level.add_label(
            str(self.new_obj_id), 
            self.new_free_obj.x, self.new_free_obj.y, 
            self.new_free_obj
        )

default = Turret()
priority = 2
group = 'Objects'
image = resources.t_turret2_static
cursor = graphics.cursor['CURSOR_CROSSHAIR']
