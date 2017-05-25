"""
Main file. Compile this.

I suppose that in a perfect world, some sort of overall code summary would go here.
"""

import pyglet
from leveleditorlibs import graphics, PaintingEnvironment, settings, resources

class LevelEditorWindow(pyglet.window.Window):
    def __init__(self):
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screen = display.get_default_screen()
        width, height = screen.width-50, screen.height-100
        super(LevelEditorWindow, self).__init__(width=width, height=height)
        
        self.update_size_constants()
        graphics.main_window = self
        
        self.set_caption('gw0rp Level Editor')
        self.init_cursors()
        self.init_gl()
        
        self.painting_environment = PaintingEnvironment.PaintingEnvironment()
        self.push_handlers(self.painting_environment)
    
    def update_size_constants(self):
        graphics.width = self.width
        graphics.height = self.height
        graphics.canvas_x = settings.settings['toolbar_width']
        graphics.canvas_y = settings.settings['buttonbar_height']
    
    def init_gl(self):
        #enable alpha blending, line smoothing, init glScissor
        pyglet.gl.glEnable(pyglet.gl.GL_BLEND)
        pyglet.gl.glBlendFunc(
            pyglet.gl.GL_SRC_ALPHA, 
            pyglet.gl.GL_ONE_MINUS_SRC_ALPHA
        )
        pyglet.gl.glEnable(pyglet.gl.GL_LINE_SMOOTH)
        pyglet.gl.glEnable(pyglet.gl.GL_POINT_SMOOTH)
        #pyglet.gl.glHint(pyglet.gl.GL_LINE_SMOOTH_HINT,pyglet.gl.GL_NICEST)
        pyglet.gl.glScissor(
            graphics.canvas_x+1,graphics.canvas_y+1,
            self.width-graphics.canvas_x-1,self.height-graphics.canvas_y-1)
    
    def init_cursors(self):
        cursor_table = {
            'CURSOR_CROSSHAIR': self.CURSOR_CROSSHAIR,
            'CURSOR_HAND': self.CURSOR_HAND,
            'CURSOR_TEXT': self.CURSOR_TEXT,
            'CURSOR_WAIT': self.CURSOR_WAIT,
            'CURSOR_DEFAULT': self.CURSOR_DEFAULT
        }
        for k, v in cursor_table.items():
            graphics.cursor[k] = self.get_system_mouse_cursor(v)
    
    def on_close(self):
        settings.save_settings()
        pyglet.app.exit()
    

if __name__ == '__main__':
    graphics.main_window = LevelEditorWindow()
    pyglet.app.run()
