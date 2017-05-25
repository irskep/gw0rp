"""
A big ball of superglue - stay clear.
"""

import pyglet
import gui
import random, time
import resources, graphics, draw, tool, level
import sys, os, time
from pyglet.window import key
import settings
import collections

class PaintingEnvironment(object):
    busy = False
    def __init__(self):
        self.activated = True
        tool.painting_env = self
        
        #init buttons
        self.save_button = gui.Button(
            resources.Button, self.save, 
            graphics.width-resources.Button.width-3, 5, text='Save'
        )
        self.open_button = gui.Button(
            resources.Button, self.open, 
            self.save_button.x, resources.Button.height+10, text='Open'
        )
        
        self.buttons = [self.save_button, self.open_button]
        for button in self.buttons: graphics.main_window.push_handlers(button)
        
        #init tool control space
        self.toolbar_group = gui.ButtonGroup()
        tool.controlspace.max_x = graphics.width-200
        tool.controlspace.max_y = graphics.canvas_y
        graphics.main_window.push_handlers(tool.controlspace)
        
        #load tools, make toolbar
        self.toolbar = []
        self.labels = []
        self.current_tool = None
        self.toolsize = resources.SquareButton.width
        self.load_tools()
        
        self.keys = key.KeyStateHandler()
        graphics.main_window.push_handlers(self.keys)
        
        pyglet.clock.schedule(self.on_draw)
    
    #------------EVENT HANDLING------------#    
    def on_draw(self, dt=0):
        if self.keys[key.LEFT]: level.camera_x -= 10
        if self.keys[key.RIGHT]: level.camera_x += 10
        if self.keys[key.UP]: level.camera_y += 10
        if self.keys[key.DOWN]: level.camera_y -= 10
            
        draw.clear()
        pyglet.gl.glPushMatrix()
        self.apply_camera()
        self.draw_level()
        pyglet.gl.glPopMatrix()
        self.draw_tools()
    
    def apply_camera(self):
        if self.keys[key.SPACE]:
            pyglet.gl.glScalef(0.3, 0.3, 1)
            pyglet.gl.glTranslatef(graphics.width*1.1, graphics.height*1.1, 0)
        
        pyglet.gl.glTranslatef(-level.camera_x+graphics.canvas_x, 
                                -level.camera_y+graphics.canvas_y, 0)
    
    def draw_level(self):
        draw.set_color(1,1,1,1)
        if level.background_image != None:
            try:
                level.background_image.blit_tiled(
                    0, 0, 0, level.width, level.height
                )
            except:
                level.background_image.blit(0,0)
        
        draw.set_color(1, 0, 1, 0.5)
        draw.grid(level.camera_x, level.camera_y,
                    graphics.width, graphics.height)
        draw.set_color(0,0,0,1)
        draw.line(0,0,0,level.height)
        draw.line(0,level.height,level.width,level.height)
        draw.line(level.width,level.height,level.width,0)
        draw.line(level.width,0,0,0)
        level.draw_level_objects()
        draw.set_color(0,1,0,1)
        draw.circle(level.player_x, level.player_y, 80)
        if graphics.drawing: self.current_tool.keep_drawing_static()
    
    def draw_tools(self):
        #toolbar background
        draw.set_color(0.8, 0.8, 0.8, 1)
        draw.rect(0,graphics.canvas_y,graphics.canvas_x,graphics.height)
        draw.rect(0,0,graphics.width,graphics.canvas_y)
        
        #buttons
        draw.set_color(1,1,1,1)
        for button in self.toolbar: button.draw()   #toolbar buttons
        for button in self.buttons: button.draw()   #bottom buttons
        for label in self.labels: draw.label(label) #text labelsr
        
        tool.controlspace.draw()
        
        #divider lines
        draw.set_color(0,0,0,1)
        graphics.set_line_width(1.0)
        draw.line(0, graphics.canvas_y, graphics.width, graphics.canvas_y)
        draw.line(
            graphics.canvas_x, graphics.canvas_y, 
            graphics.canvas_x, graphics.height
        )
    
    def on_key_press(self, symbol, modifiers):
        if symbol == key.O and modifiers == key.MOD_COMMAND:
            self.open()
            return True
        if symbol == key.S and modifiers == key.MOD_COMMAND:
            self.save()
            return True
        if not graphics.drawing and \
                self.current_tool.key_press != tool.Tool.key_press:
            graphics.drawing = True
            self.current_tool.key_press(symbol, modifiers)
            graphics.drawing = False
        if symbol == key.ESCAPE: return True    #stop Pyglet from quitting
    
    def on_key_release(self, symbol, modifiers):
        if not graphics.drawing and \
                self.current_tool.key_release != tool.Tool.key_release:
            graphics.drawing = True
            self.current_tool.key_release(symbol, modifiers)
            graphics.drawing = False
    
    def on_text(self, text):
        if not graphics.drawing and self.current_tool.text != tool.Tool.text:
            graphics.drawing = True
            self.current_tool.text(text)
            graphics.drawing = False
    
    def on_mouse_motion(self, x, y, dx, dy):
        if not self.activated or self.keys[key.SPACE]: return
        lastx, lasty = x-dx, y-dy
        if x > graphics.canvas_x and y > graphics.canvas_y:
            if not (lastx > graphics.canvas_x and lasty > graphics.canvas_y) \
                    and self.current_tool.cursor != None:
                graphics.main_window.set_mouse_cursor(self.current_tool.cursor)
        else:
            if (lastx > graphics.canvas_x and lasty > graphics.canvas_y) \
                    or (lastx > graphics.width) or (lasty > graphics.height):
                graphics.set_cursor(graphics.cursor['CURSOR_DEFAULT'])
    
    def on_mouse_press(self, x, y, button, modifiers):
        if not self.activated or self.keys[key.SPACE]: return
        if x > graphics.canvas_x and y > graphics.canvas_y:
            graphics.drawing = True
            self.current_tool.start_drawing(x+level.camera_x-graphics.canvas_x,
                                            y+level.camera_y-graphics.canvas_y)
    
    def on_mouse_drag(self, x, y, dx, dy, button, modifiers):
        if not self.activated: return
        if self.keys[key.SPACE]:
            level.camera_x -= dx/0.3
            level.camera_y -= dy/0.3
            return
        self.on_mouse_motion(x,y,dx,dy)
        if graphics.drawing:
            self.current_tool.keep_drawing(
                x+level.camera_x-graphics.canvas_x,
                y+level.camera_y-graphics.canvas_y,dx,dy
            )
    
    def on_mouse_release(self, x, y, button, modifiers):
        if not self.activated or self.keys[key.SPACE]: return
        if graphics.drawing:
            self.current_tool.stop_drawing(
                x+level.camera_x-graphics.canvas_x,
                y+level.camera_y-graphics.canvas_y
            )
            graphics.drawing = False
    
    def on_close(self):
        settings.save_settings()
        pyglet.app.exit()
    
    def on_activate(self):
        self.activated = True
    
    def on_deactivate(self):
        self.activated = False
    
    #------------TOOL THINGS------------#
    def import_libs(self, dir):
        """ Imports the libs, returns a dictionary of the libraries."""
        library_dict = {}
        sys.path.append(dir)
        for f in os.listdir(os.path.abspath(dir)):
            module_name, ext = os.path.splitext(f)
            if ext == '.py' and module_name != '__init__':
                module = __import__(module_name)
                library_dict[module_name] = module
        
        return library_dict
    
    def load_tools(self):
        #Import everything in the Tools directory, shove them in a dictionary
        tools = self.import_libs('Editor/Tools')
        #Sort them by their priority property
        sorted_tools = sorted(tools.values(), key=lambda tool:tool.priority)
        
        #Categorize them by group - remain sorted
        self.grouped_tools = collections.defaultdict(list)
        for tool in sorted_tools:
            self.grouped_tools[tool.group].append(tool)
        
        #Create appropriate buttons in appropriate locations
        y = graphics.height
        for group in sorted(self.grouped_tools.keys()):
            #group label
            self.labels.append(pyglet.text.Label(group, x=self.toolsize, y=y-self.toolsize/3-3,
                                font_size=self.toolsize/4, anchor_x='center',anchor_y='bottom',
                                color=(0,0,0,255)))
            y -= self.toolsize/3+3
            
            i = 0
            for tool in self.grouped_tools[group]:
                tool.default.cursor = tool.cursor
                i += 1
                x = self.toolsize
                #two to a row
                if i % 2 != 0:
                    x = 0
                    y -= self.toolsize
                new_button = gui.ImageButton(
                    resources.SquareButton, 
                    self.get_toolbar_button_action(tool.default), x,y, 
                    parent_group = self.toolbar_group,image_2=tool.image
                )
                self.toolbar.append(new_button)
        
        self.current_tool = sorted_tools[0].default
        self.toolbar[0].selected = True
        self.toolbar_group.buttons = self.toolbar
        for tool in self.toolbar: graphics.main_window.push_handlers(tool)
    
    def get_toolbar_button_action(self, specific_tool):
        #decorator for toolbar buttons
        def action():
            if not graphics.drawing:
                self.current_tool.unselect()
                self.current_tool = specific_tool
                tool.controlspace.clear()
                self.current_tool.select()
        return action
    
    #------------BUTTON THINGS------------#
    def open(self):
        path = gui.open_file(type_list = ['yaml'])
        if path == None: return
        level.load(path)
    
    def save(self):
        path = gui.save_file(default_name="Level_.yaml")
        if path == None: return
        level.save(path)
    
    def open_old(self):
        if self.busy: return
        graphics.main_window.set_fullscreen(False)
        pyglet.clock.schedule_once(self.open_2,0.5)
        self.busy = True
    
    def open_2(self, dt=0):    
        self.busy = False
        path = gui.open_file(type_list = ['yaml'])
        graphics.main_window.set_fullscreen(True)
        if path == None: return
        pyglet.clock.schedule_once(self.open_3, 0.5, path)
        self.busy = True
    
    def open_3(self, dt=0, path=None):
        self.busy = False
        if path != None:
            level.load(path)
    
    def save_old(self):
        if self.busy: return
        graphics.main_window.set_fullscreen(False)
        pyglet.clock.schedule_once(self.save_2,0.5)
        self.busy = True
    
    def save_2(self, dt=0):
        self.busy = False
        path = gui.save_file(default_name="Level_.yaml")
        graphics.main_window.set_fullscreen(True)
        if path == None: return
        level.save(path)
        pyglet.clock.schedule_once(self.save_3, 0.5)
        self.busy = True
    
    def save_3(self, dt=0):
        self.busy = False
    
