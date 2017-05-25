import pyglet
from pyglet.window import key
import env, gui, widget

class KeyGetter(object):
    def __init__(self, action):
        self.key = -1
        self.action = action
    
    def on_key_press(self, symbol, modifiers):
        if self.key != -1:
            if symbol == key.RETURN:
                self.action(self.key)
                return True
        self.key = symbol
    

class KeyLabel(pyglet.text.Label):
    def __init__(self, x, y, key_getter):
        super(KeyLabel, self).__init__(
            "", x=x, y=y, font_size=24, 
            anchor_x='center', anchor_y='center',
            color=(255,255,255,255)
        )
        self.key_getter = key_getter
    
    def on_key_press(self, symbol, modifiers):
        self.text = env.symbol_to_string(symbol)

def flag_func():
    return 2

screenshot = None
unit_to_bind = None
prev_card_func = flag_func

def bind_key_and_return(key):
    env.bind_key(key, unit_to_bind)
    if prev_card_func == flag_func:
        gui.pop_handlers()
        gui.current_card = flag_func()
        gui.last_card = None
        gui.next_card = None
    else:
        gui.change_to_card_fast(gui.Card(prev_card_func()))

def widgets():
    background = widget.UnscaledImage(screenshot, 0, 0)
    darken = widget.Rect(0,0,env.norm_w,env.norm_h,(0,0,0,0.7))
    background_rect = (env.norm_w//2-200, env.norm_h//2-120, 400, 240)
    rect_fill = widget.Rect(*background_rect)
    rect_fill.color = (0,0,0,0.7)
    rect_outline = widget.Rect(*background_rect)
    rect_outline.color = (0,0,0,1)
    
    getter = KeyGetter(bind_key_and_return)
    
    choose_key_desc_1 = pyglet.text.Label(
        "You have acquired a new unit.", font_name='Gill Sans', font_size=20,
        x=env.norm_w//2, y=env.norm_h//2+90, anchor_x='center', anchor_y='center'
    )
    choose_key_desc_2 = pyglet.text.Label(
        "Choose a key to assign.", font_name='Gill Sans', font_size=20,
        x=env.norm_w//2, y=env.norm_h//2+60, anchor_x='center', anchor_y='center'
    )
    choose_key_desc_confirm = pyglet.text.Label(
        "Press Return to confirm.", font_name='Gill Sans', font_size=20,
        x=env.norm_w//2, y=env.norm_h//2-80, anchor_x='center', anchor_y='center'\
    )
    key_label = KeyLabel(env.norm_w//2, env.norm_h//2, getter)
    
    return [
        background, darken,
        rect_fill, rect_outline,
        choose_key_desc_1,
        choose_key_desc_2,
        choose_key_desc_confirm,
        key_label,
        getter
    ]