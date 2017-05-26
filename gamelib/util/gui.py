import os, pyglet
import env, draw, music, resources, save, settings, widget
from pyglet.window import key
from pyglet import gl

cards = {}
current_card = None
last_card = None
next_card = None
transition_time = 0.0
window = None

pushed = False

START = 1
QUIT  = 2
LOAD = 3

load_path = ""

class Card(object):
    def __init__(self, widgets):
        super(Card, self).__init__()
        self.widgets = widgets
    
    def push_handlers(self):    
        for widget in self.widgets:
            window.push_handlers(widget)
    
    def pop_handlers(self):
        for widget in self.widgets:
            window.pop_handlers()
        
    def draw(self):
        for widget in self.widgets:
            widget.draw()
    

def push_handlers():
    global pushed
    #print "pushing", current_card
    if pushed:
        print "event push mismatch"
        return
    pushed = True
    current_card.push_handlers()

def pop_handlers():
    global pushed
    #print "popping", current_card
    if not pushed:
        print "event pop mismatch"
        return
    pushed = False
    current_card.pop_handlers()

def refresh(card):
    global current_card
    pop_handlers()
    current_card = card
    push_handlers()

def draw_card():
    global last_card, current_card, next_card, transition_time
    draw.set_color(1,1,1,1)
    draw.rect(0, 0, env.norm_w, env.norm_h)
    current_card.draw()
    if transition_time > 0:
        if next_card != None:
            a = (1.0-transition_time/0.5)
        else:
            a = transition_time/0.5
        draw.set_color(1,1,1,a)
        draw.rect(0, 0, env.norm_w, env.norm_h)
        transition_time -= env.dt
        if transition_time <= 0:
            if next_card != None:
                last_card = current_card
                current_card = next_card
                next_card = None
                transition_time = 0.5
            else:
                transition_time = 0.0
                push_handlers()

def change_to_card(card, time=0.5):
    global next_card, transition_time
    time = max(0.00001, time)
    pop_handlers()
    next_card = card
    transition_time = time

def change_to_card_fast(card):
    global last_card, current_card, next_card
    pop_handlers()
    last_card = current_card
    current_card = card
    next_card = None
    push_handlers()

def get_card_changer(card, time=0.5):
    time = max(0.00001, time)
    def change():
        change_to_card(card, time)
    return change

def get_active_card_changer(widget_func, time=0.5):
    def change():
        card = Card(widget_func())
        if time > 0:
            change_to_card(card, time)
        else:
            change_to_card_fast(card)
    return change

def get_fast_card_changer(card):
    def change():
        change_to_card_fast(card)
    return change

def go_back(time=0.5):
    time = max(0.00001, time)
    global next_card, transition_time
    pop_handlers()
    next_card = last_card
    transition_time = time

def go_back_fast():
    global last_card, current_card, next_card
    pop_handlers()
    last_card, current_card = current_card, last_card
    next_card = None
    push_handlers()

def settings_tweaker_label(k, v, l):
    def change_setting():
        settings.set(k, v)
        settings.save()
        l.show = True
    return change_setting

def get_slider(k):
    def change_setting(v):
        settings.set(k, v)
        settings.save()
    return change_setting

def state_goer(state):
    def go_to_state():
        global next_card, transition_time
        pop_handlers()
        next_card = state
        transition_time = 0.5
    return go_to_state

def settings_widgets():
    left = env.norm_w/2-resources.settings_box.width/2+23
    top = env.norm_h/2+resources.settings_box.height/2
    item_spacing = 78
    
    def back_button_func():
        music.update_volume()
        go_back()
    
    restart_label = widget.HideableLabel(
        False,
        "Changes will take effect the next time gw0rp is run.",
        x=env.norm_w/2, y=20,
        font_name='Gill Sans', font_size=24, 
        color=(128,128,128,255),
        anchor_x='center'
    )
    fullscreen_toggle = widget.TextToggle(
        left, top-item_spacing+15,
        "Fullscreen: Yes", 
            settings_tweaker_label('fullscreen', True, restart_label),
        "Fullscreen: No", 
            settings_tweaker_label('fullscreen', False, restart_label),
        settings.fullscreen
    )
    sound_label = pyglet.text.Label(
        "Sound Volume", 
        font_name='Gill Sans', font_size=36,
        x=left, y=fullscreen_toggle.y-item_spacing,
        color=(128,128,128,255)
    )
    music_label = pyglet.text.Label(
        "Music Volume", 
        font_name='Gill Sans', font_size=36,
        x=left, y=sound_label.y-item_spacing,
        color=(128,128,128,255)
    )
    settings_back_button = widget.TextButton(
        "Back",
        env.norm_w/2, music_label.y-item_spacing+5,
        back_button_func, 
        size=36, anchor_x='center'
    )
    
    slider_x = music_label.x+music_label.content_width + 50
    y_space = 22
    sound_slider = widget.Slider(
        slider_x, sound_label.y+y_space/2,
        get_slider('sound_volume'), settings.sound_volume
    )
    music_slider = widget.Slider(
        slider_x, music_label.y+y_space/2,
        get_slider('music_volume'), settings.music_volume
    )
    
    settings_back_trigger = widget.KeyTrigger(key.ESCAPE, go_back)
    x1 = fullscreen_toggle.x-10
    x2 = music_slider.x+music_slider.width+20
    line_1 = widget.Line(x1, fullscreen_toggle.y-y_space, 
                         x2, fullscreen_toggle.y-y_space)
    line_2 = widget.Line(x1, sound_label.y-y_space, 
                         x2, sound_label.y-y_space)
    settings_box = pyglet.sprite.Sprite(resources.settings_box, 
                                        env.norm_w/2, env.norm_h/2)
    return [
        settings_box,
        line_1, line_2,
        sound_label, music_label,
        fullscreen_toggle, 
        settings_back_button,
        sound_slider, music_slider,
        restart_label
    ]

def instruction_widgets():
    instructions_image = pyglet.sprite.Sprite(
        resources.instructions, 0, 0
    )
    back_label = pyglet.text.Label(
        "Click or press Escape to go back.",
        font_size=24, font_name="Gill Sans",
        x=10, y=10, color=(0,0,0,255)
    )
    click_back = widget.ClickTrigger(go_back)
    space_back = widget.KeyTrigger(key.SPACE, go_back)
    esc_back = widget.KeyTrigger(key.ESCAPE, go_back)
    return [instructions_image, back_label, click_back, space_back, esc_back]

def credit_widgets():
    background_rect = widget.Rect(0, 0, env.norm_w, env.norm_h, (0,0,0,1))
    credits_image = pyglet.sprite.Sprite(
        resources.credits, env.norm_w/2, env.norm_h/2
    )
    click_back = widget.ClickTrigger(go_back)
    space_back = widget.KeyTrigger(key.SPACE, go_back)
    esc_back = widget.KeyTrigger(key.ESCAPE, go_back)
    return [background_rect, credits_image, click_back, space_back, esc_back]

def instruction_widgets_first():
    instructions_image = pyglet.sprite.Sprite(
        resources.instructions, 0, 0
    )
    back_label = pyglet.text.Label(
        "Click or press Space to continue.",
        font_size=24, font_name="Gill Sans",
        x=10, y=10, color=(0,0,0,255)
    )
    click_back = widget.ClickTrigger(state_goer(START))
    space_back = widget.KeyTrigger(key.SPACE, state_goer(START))
    esc_back = widget.KeyTrigger(key.ESCAPE, state_goer(START))
    return [instructions_image, back_label, click_back, space_back, esc_back]

def title_widgets():
    title_label = pyglet.text.Label(
        "gw0rp", x=env.norm_w/2, y=env.norm_h/16*11,
        anchor_x='center', anchor_y='baseline', 
        font_size=36*3, font_name='Gill Sans', 
        color=(128,128,128,255)
    )
    title_underline = widget.Line(
        title_label.x-title_label.content_width/2,
        title_label.y-3*env.scale_factor, 
        title_label.x+title_label.content_width/2,
        title_label.y-3*env.scale_factor
    )
    # instructions_button = widget.TextButton(
    #        "Instructions", env.norm_w/2, env.norm_h/16*8,
    #        get_card_changer(cards['instructions']),
    #        anchor_x='center'
    #    )
    
    def load():
        global load_path, next_card, transition_time
        pop_handlers()
        next_card = LOAD
        transition_time = 0.5
        load_path = os.path.join(os.path.split(save.most_recent_save()[1])[:-1])[0]
    
    continue_button = widget.TextButton(
        "Continue", env.norm_w/2, env.norm_h/16*8,
        load, anchor_x='center'
    )
    
    center_x = env.norm_w/2 + 30
    
    start_button = widget.TextButton(
        "New Game", center_x-30, continue_button.y-env.norm_h/8,
        get_card_changer(cards['start']), anchor_x='right'
    )
    settings_button = widget.TextButton(
        "Settings", center_x+30, start_button.y,
        get_card_changer(cards['settings']), 
        anchor_x='left'
    )
    load_button = widget.TextButton(
        "Load Game", center_x-30, start_button.y-env.norm_h/8,
        get_active_card_changer(load_widgets),
        anchor_x='right'
    )
    quit_button = widget.TextButton(
        "Quit", center_x+30, load_button.y,
        state_goer(QUIT), 
        anchor_x='left'
    )
    start_key_trigger = widget.KeyTrigger(key.SPACE, start_button.action)
    button_sep = widget.Line(
        center_x, start_button.y+start_button.content_height*0.7,
        center_x, quit_button.y-5
    )
    
    udg_label_1 = pyglet.text.Label(
        "gw0rp is an entry in uDevGames 2008/2009. Visit www.udevgames.com for more information.",
        x=10, y=30, font_size=14, font_name='Gill Sans', color=(128,128,128,255)
    )
    udg_label_2 = pyglet.text.Label(
        "Please send any questions or suggestions to diordna@gmail.com.",
        x=10, y=10, font_size=14, font_name='Gill Sans', color=(128,128,128,255)
    )
    widgets = [
        udg_label_1,
        udg_label_2,
        button_sep,
        title_underline,
        start_button, 
        start_key_trigger, 
        load_button,
        settings_button, 
        quit_button,
        title_label
    ]
    if save.autosave_exists():
        widgets.append(continue_button)
    return widgets

def load_widgets():
    #def back_2():
        #cards['title'] = Card(title_widgets())
        #go_back()
    back_2 = get_active_card_changer(title_widgets)
    
    back_button = widget.TextButton(
        "Back", 5, 7, back_2, 
        size=36, anchor_x='left', anchor_y='baseline'
    )
    back_trigger = widget.KeyTrigger(key.ESCAPE, back_2)
    widgets = [back_trigger, back_button]
    
    def level_loader(path):
        def load():
            global load_path, next_card, transition_time
            pop_handlers()
            next_card = LOAD
            transition_time = 0.5
            load_path = path
        return load
    
    def save_deleter(name):
        def delete():
            global last_card
            temp_last_card = last_card
            save.clear_save(name)
            get_active_card_changer(load_widgets, 0)()
            last_card = temp_last_card
        return delete
    
    item_spacing = 50
    x = 100
    max_w = 0
    y = env.norm_h-50
    new_line = widget.Line(
        x, y-item_spacing/3.3333+item_spacing, 
        x+300, y-item_spacing/3.3333+item_spacing
    )
    widgets.append(new_line)
    for p in save.list_saves():
        new_button = widget.TextButton(
            os.path.splitext(os.path.split(p)[-1])[0], 
            x, y, level_loader(p),size=24, anchor_x='left'
        )
        new_del_button = widget.TextButton(
            "x", new_button.x+new_button.content_width+10, new_button.y,
            save_deleter(os.path.splitext(os.path.split(p)[-1])[0]), size=20, anchor_x='left'
        )
        new_del_button.color_mouse = (255, 0, 0, 255)
        new_del_button.color_pressed = (200, 0, 0, 255)
        new_line = widget.Line(
            x, y-item_spacing/3.3333, x+300, y-item_spacing/3.3333
        )
        widgets.append(new_line)
        widgets.append(new_button)
        widgets.append(new_del_button)
        y -= item_spacing
    #back_button.y = y
    return widgets

