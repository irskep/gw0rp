"""
Base class and utilities for tools.

Writing a Tool
==============

    1. B{Subclass I{Tool}}
    
    2. B{Override Appropriate Methods}
    
    Most simple tools will want to at least override start_drawing() and keep_drawing(). More sophisticated tools will need to override more methods to achieve the desired behavior.
    
    3. B{Set Module Properties}
    ::
        default = YourClass()   #: Instance of your class
        priority = 1000         #: Rank
        group = 'Example'       #: Grouping - Drawing, Shapes, etc
        image = None            #: Icon
        cursor = None           #: Default cursor

Adding Buttons
==============
    1. Make a button. See L{Button<gui.Button>} and L{ImageButton<gui.ImageButton>}.
    
    2. Add it to the control space with L{tool.controlspace.add()<tool.ControlSpace.add()>}.
    
    3. Repeat as necessary.
    
    4. If you want radio button behavior (only one button selected at a time), 
"""

import pyglet, math
import gui, resources, graphics, draw

# =======================
# = BEGIN TOOL TEMPLATE =
# =======================

class Tool(object):
    """Abstract base tool"""
    
    def select(self):
        """User selects tool in toolbar. Also called in special cases like file saving/loading."""
        pass
    
    def unselect(self):
        """User selects a different tool. Perform clean-up here if necessary."""
        pass
    
    def start_drawing(self, x, y):
        """Mouse has been pressed in the canvas area."""
        pass
    
    def keep_drawing(self, x, y, dx, dy):
        """Mouse is being dragged after being pressed in the canvas area."""
        pass
    
    def keep_drawing_static(self):
        """Mouse is pressed but nothing is happening."""
        pass
    
    def stop_drawing(self, x, y):
        """Mouse is released."""
        pass
    
    def text(self, text):
        """Unicode text is being entered from the keyboard."""
        pass
    
    def key_press(self, symbol, modifiers):
        """A key has been pressed. See pyglet documentation on keyboard input for more information."""
        pass
    
    def key_release(self, symbol, modifiers):
        """A key has been released. See pyglet documentation on keyboard input for more information."""
        pass
    
default = Tool()    #: Instance of your class
priority = 1000     #: Position in toolbar
group = 'Example'   #: Toolbar grouping - Drawing, Shapes, etc
image = None        #: Toolbar icon
cursor = None       #: Default cursor

class ControlSpace(object):
    """A singleton that allows tools to add GUI elements to the bottom bar"""

    controls = []
    max_x = 0
    max_y = 0

    def draw(self):
        """Draw all controls added by the tool. Called by the main loop."""
        for control in self.controls:
            control.draw()

    def add(self, new_object):
        """
        Add a new button to the control space.
        
        @param new_object: GUI object to add to the control space
        """
        if new_object.x >= 0 and new_object.y >= 0 \
                and new_object.x+new_object.width <= self.max_x \
                and new_object.y+new_object.height <= self.max_y:
            self.controls.append(new_object)
            return True
        else:
            print "Attempt to add button failed. Out of bounds."
            print new_object.x, new_object.y
            return False

    def clear(self):
        self.controls = []

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        for control in self.controls: 
            control.on_mouse_drag(x,y,dx,dy,buttons,modifiers)

    def on_mouse_press(self, x, y, button, modifiers):
        for control in self.controls:   
            control.on_mouse_press(x,y,button,modifiers)

    def on_mouse_release(self, x, y, button, modifiers):
        for control in self.controls: 
            control.on_mouse_release(x,y,button,modifiers)

painting_env = None

controlspace = ControlSpace()

def generate_button_row(
            images, functions, button_group=None, start_x=5, start_y=55,
            anchor='bottomleft'
        ):
    buttons = []
    w, h = resources.SquareButton.width, resources.SquareButton.height
    x = start_x
    y = start_y
    for i in xrange(len(functions)):
        temp_button = gui.ImageButton(
            resources.SquareButton, functions[i], x, y,
            image_2=images[i], parent_group=button_group, anchor=anchor
        )
        buttons.append(temp_button)
        controlspace.add(temp_button)
        x += w
        if x > controlspace.max_x - 50:
            x = start_x
            y -= h
    buttons[0].select()
    buttons[0].action()
    return buttons

def generate_complex_button_row(images, functions, button_group=None, 
                                start_x=5, start_y=55):   
    def centerblitter(x, y, img):
        def blitter():
            img.blit(x+25,y+25)
        return blitter
    
    chosen = False
    x = start_x
    y = start_y
    for i in xrange(len(functions)):
        newbutton = gui.Button(
            text="", image=resources.SquareButton,
            action=functions[i], x=x, y=y, 
            more_draw=centerblitter(x, y, images[i]),
            parent_group=button_group
        )
        controlspace.add(newbutton)
        if not chosen:
            newbutton.action()
            newbutton.select()
            chosen = True
        x += 50
        if x > controlspace.max_x - 50:
            x = start_x
            y -= 50