import math
from leveleditorlibs import tool, resources
from leveleditorlibs import graphics, draw, level
from leveleditorlibs import gui

class DestructibleWall(tool.Tool):
    
    shelf_type = 0
    shelf_types = ['Shelf_H', 'Shelf_V']
    
    def select(self):
        self.button_group = gui.ButtonGroup()
        num = len(self.shelf_types)
        images = [
            getattr(resources, "t_"+self.shelf_types[i]) for i in xrange(num)
        ]
        def select_obj_type(newtype):
            def select():
                self.shelf_type = newtype
            return select
        
        functions = [select_obj_type(i) for i in xrange(num)]
        tool.generate_button_row(images, functions, self.button_group)
    
    def start_drawing(self, x, y):
        self.new_obj_id = level.get_id()
        self.new_free_obj = level.DestructibleWallSprite(
            self.new_obj_id, x, y, 0, 1, self.shelf_types[self.shelf_type]
        )
        level.simple_objects.append(self.new_free_obj)

    def keep_drawing(self, x, y, dx, dy):
        self.new_free_obj.x = x
        self.new_free_obj.y = y
    
    def stop_drawing(self, x, y):
        level.add_label(
            str(self.new_obj_id), 
            self.new_free_obj.x, self.new_free_obj.y, 
            self.new_free_obj
        )

default = DestructibleWall()
priority = 12
group = 'Objects'
image = resources.t_Shelf_H
cursor = graphics.cursor['CURSOR_CROSSHAIR']
