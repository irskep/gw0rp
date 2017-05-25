from leveleditorlibs import tool, resources
from leveleditorlibs import graphics, draw, level
from leveleditorlibs import gui

class Key(tool.Tool):
    
    key = 0
    
    def select(self):
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
    
    def start_drawing(self, x, y):
        obj_id = level.get_id()
        new_key = level.Key(obj_id, x, y, self.key)
        level.primitives.append(new_key)
        level.add_label(str(obj_id), x-5, y+5, new_key)

default = Key()
priority = 7
group = 'Objects'
image = resources.DoorKey
cursor = graphics.cursor['CURSOR_CROSSHAIR']
