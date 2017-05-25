from leveleditorlibs import tool, resources
from leveleditorlibs import graphics, draw, level, gui
from pyglet.window import key
import pyglet, math

class Kill(tool.Tool):
    """Delete an object by entering its ID. Click it if it's an image."""
    id_string = ""
    
    def select(self):
        self.id_string = ""
        self.label = gui.Label("To delete: "+self.id_string, 5, 5)
        tool.controlspace.add(self.label)
        tool.controlspace.add(gui.Label(
                "Enter ID and press Return to kill. Press Esc to clear current ID. " \
                "Click it if it's an image.",
                x=5, y=50, size=14))
    
    def start_drawing(self, x, y):
        for obj in level.simple_objects:
            if math.sqrt((x-obj.x)*(x-obj.x)+(y-obj.y)*(y-obj.y)) <= obj.image.width/2:
                self.kill(obj)
    
    def kill(self, obj):
        if obj in level.primitives:
            level.primitives.remove(obj)
            level.labels.remove(obj.label)
            obj.label.delete()
        elif obj in level.simple_objects:
            obj.delete()
            level.simple_objects.remove(obj)
            level.labels.remove(obj.label)
            obj.label.delete()
    
    def key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            self.id_string = ""
            self.label.set_text("To delete: ")
        elif symbol == key.BACKSPACE:
            if len(self.id_string) > 0:
                self.id_string = self.id_string[0:-1]
                self.label.set_text("To delete: "+self.id_string)
        elif symbol == key.RETURN:
            try:
                to_kill = int(self.id_string)
                if to_kill > 0:
                    for obj in level.primitives:
                        if obj.obj_id == to_kill:
                            self.kill(obj)
                    for obj in level.simple_objects:
                        if obj.obj_id == to_kill:
                            self.kill(obj)
            except:
                pass
            self.id_string = ""
            self.label.set_text("To delete: ")
    
    def text(self, txt):
        try:
            new_num = int(txt)
            self.id_string = "".join([self.id_string, txt])
            self.label.set_text("To delete: "+self.id_string)
        except:
            pass

default = Kill()
priority = 3
group = 'Actions'
image = resources.Kill
cursor = graphics.cursor['CURSOR_DEFAULT']