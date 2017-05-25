import math, pyglet
from pyglet.window import key

import level
from util import gui, keychooser, widget
from util import draw, env, physics

player_position = (0, 0)
screenshot = None
to_release = []

class UnitProxyButton(widget.TextButton):
    def __init__(self, unit, text, x, y, action=None):
        super(UnitProxyButton, self).__init__(text, x, y, action, 14)
        
        self.lineto_x = -unit.offset[1]
        self.lineto_y = unit.offset[0]
        self.unit = unit
    
    def draw(self):
        if self.selected:
            draw.set_color(0,1,0,1)
            x1, y1 = self.x-5, self.y+13
            x2 = self.lineto_x+player_position[0]
            y2 = self.lineto_y+player_position[1]
            draw.rect_outline(
                x2-physics.default_radius*1.3, 
                y2-physics.default_radius*1.3,
                x2+physics.default_radius*1.3, 
                y2+physics.default_radius*1.3
            )
        super(UnitProxyButton, self).draw()
    

class UnitProxy(pyglet.sprite.Sprite):
    def __init__(self, unit, offset_x, offset_y):
        self.unit = unit
        self.offset_x = offset_x
        self.offset_y = offset_y
        x = self.offset_x-self.unit.offset[1]
        y = self.offset_y+self.unit.offset[0]
        super(UnitProxy, self).__init__(unit.image, x, y)
        self.scale = unit.scale
        self.rotation = unit.local_angle_target-90
        self.dragging = False
    
    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        x, y = widget.convert_coords(x, y)
        if not self.dragging: return
        self.rotation = -math.degrees(math.atan2(y-self.y, x-self.x))
    
    def on_mouse_press(self, x, y, button, modifiers):
        x, y = widget.convert_coords(x, y)
        if math.sqrt((x-self.x)**2 + (y-self.y)**2) <= self.unit.radius:
            self.dragging = True
    
    def on_mouse_release(self, x, y, button, modifiers):
        x, y = widget.convert_coords(x, y)
        if self.dragging:
            self.unit.local_angle_target = self.rotation+90
            self.dragging = False
    

class UnitReleaser(UnitProxyButton):
    def __init__(self, unit, x, y):
        super(UnitReleaser, self).__init__(unit, "release", x, y, self.click)
        self.enabled = False
        
    def click(self):
        global to_release
        if self.enabled:
            self.enabled = False
            self.color_normal = (128, 128, 128, 255)
            self.color_mouse = (100, 100, 100, 255)
            self.color_pressed = (0, 0, 0, 255)
            to_release.remove(self.unit)
            self.text = "release"
        else:
            self.enabled = True
            self.color_normal = (200, 0, 0, 255)
            self.color_mouse = (255, 0, 0, 255)
            self.color_pressed = (128, 0, 0, 255)
            to_release.append(self.unit)
            self.text = "UNIT WILL BE RELEASED"
    

def unpause():
    global to_release
    for u in to_release:
        env.unbind_keys_for_unit(u)
        level.player.release_unit(u)
    to_release = []
    gui.state_goer(1)()

def pause_screen_widgets():
    global player_position
    
    #unit proxy bounding box
    x1, y1, x2, y2 = level.player.get_bounding_rect()
    player_offset = (env.norm_w//2, env.norm_h//4*3)
    player_offset = (-x1 + physics.default_radius + 250, env.norm_h//2)
    proxy_rotate_desc = pyglet.text.Label(
        "Click and drag a unit to change its rotation.",
        font_name='Gill Sans', font_size=12,
        x=player_offset[0], y=player_offset[1],
        anchor_x='center', anchor_y='top',
        color=(0,0,0,255)
    )
    min_w = proxy_rotate_desc.content_width + 10
    x1 = min(-min_w/2, x1)
    x2 = max(min_w/2, x2)
    player_box = (
        x1 + player_offset[0] - physics.default_radius, 
        y1 + player_offset[1] - physics.default_radius, 
        x2 + player_offset[0] + physics.default_radius, 
        y2 + player_offset[1] + physics.default_radius + 30
    )
    proxy_rotate_desc.y = player_box[3]-10
    
    player_box_args = (
        player_box[0],
        player_box[1],
        player_box[2]-player_box[0], 
        player_box[3]-player_box[1]
    )
    player_box_rect = widget.Rect(*player_box_args)
    player_box_rect.color = (1,1,1,0.7)
    player_box_rect_outline = widget.RectOutline(*player_box_args)
    player_box_rect_outline.color = (0,0,0,1)
    
    #more positional constants
    player_position = ((player_box[0]+player_box[2])/2, player_offset[1])
    
    #key list
    #key_list_desc = pyglet.text.Label(
    #    "Key Bindings",
    #    font_name='Gill Sans', font_size=24,
    #    x=env.norm_w//2, y=keylist_y-5,
    #    anchor_x='center', anchor_y='top',
    #    color=(0,0,0,255)
    #)
    
    #unit proxies
    labels = [proxy_rotate_desc]
    unit_proxies = []
    offset_x, offset_y = (player_box[0]+player_box[2])/2, player_offset[1]
    y = 1
    spacing = 25
    keylist_x = player_box[2]+20
    keylist_y = env.norm_h/2+spacing*(len(level.player.units)-1)/2+25
    
    #Labels and key buttons
    def make_key_killer(unit, key, x, y):
        def kill_key():
            env.key_bindings[key].remove(unit)
            gui.change_to_card_fast(gui.Card(pause_screen_widgets()))
        new_button = UnitProxyButton(
            unit, env.symbol_to_string(key), x, y, kill_key
        )
        new_button.color_mouse = (255, 0, 0, 255)
        new_button.color_pressed = (200, 0, 0, 255)
        return new_button
    
    def make_key_adder(unit, x, y):
        def add():
            keychooser.unit_to_bind = unit
            gui.change_to_card_fast(gui.Card(keychooser.widgets()))
        newbutton = UnitProxyButton(
            unit, "add key", x, y, add
        )
        newbutton.color_normal = (0, 200, 0, 255)
        newbutton.color_mouse = (0, 255, 0, 255)
        newbutton.color_pressed = (0, 128, 0, 255)
        return newbutton
    
    kb_x_max = 0
    kb_x = 0
    for unit in reversed(level.player.units):
        unit_proxies.append(UnitProxy(unit, offset_x, offset_y))
        if unit.label != "Brain":
            new_label = UnitProxyButton(
                unit, unit.label + ":", keylist_x+12, keylist_y-y*spacing
            )    
            labels.append(new_label)
            kb_x = new_label.x+new_label.content_width+5
            kb_y = new_label.y
            if unit.uses_keys:
                key_buttons = []
                for k, unit_list in env.key_bindings.items():
                    if unit in unit_list:
                        new_button = make_key_killer(unit, k, kb_x, kb_y)
                        kb_x = new_button.x + new_button.content_width+10
                        key_buttons.append(new_button)
                for kb in key_buttons[0:-1]:
                    kb.text = kb.text + ","
                labels.extend(key_buttons)
            y += 1
            kb_x_max = max(kb_x, kb_x_max)
    
    kb_x = kb_x_max + 10
    add_buttons = []
    y = 1
    for unit in reversed(level.player.units):
        if unit.label != "Brain":
            kb_y = keylist_y-y*spacing
            new_adder = make_key_adder(unit, kb_x, kb_y)
            if unit.uses_keys:
                add_buttons.append(new_adder)
            new_releaser = UnitReleaser(
                unit, new_adder.x+new_adder.content_width+10, kb_y
            )
            add_buttons.append(new_releaser)
            y += 1
    labels.extend(add_buttons)
    
    unit_list_desc = pyglet.text.Label(
        "Units near the top are released first.",
        font_name='Gill Sans', font_size=12,
        x=env.norm_w//2, y=new_label.y-30,
        anchor_x='center', anchor_y='baseline'
    )
    unit_list_desc_2 = pyglet.text.Label(
        "Click a key name to delete it.",
        font_name='Gill Sans', font_size=12,
        x=env.norm_w//2, y=unit_list_desc.y-25,
        anchor_x='center', anchor_y='baseline'
    )
    keylist_rect = [
        keylist_x, keylist_y-8, 
        env.norm_w-new_releaser.x+220, -(keylist_y-new_releaser.y)
    ]
    key_box_rect = widget.Rect(*keylist_rect)
    key_box_rect.color = (1,1,1,0.7)
    key_box_rect_outline = widget.RectOutline(*keylist_rect)
    key_box_rect_outline.color = (0,0,0,1)
    
    #labels.extend([unit_list_desc, unit_list_desc_2])
    
    # ==============
    # = AESTHETICS =
    # ==============
    background = widget.UnscaledImage(screenshot, 0, 0)
    darken = widget.Rect(0,0,env.norm_w,env.norm_h,(1,1,1,0.7))
    
    # ==================
    # = NORMAL WIDGETS =
    # ==================
    unpause_trigger = widget.KeyTrigger(key.ESCAPE, unpause)
    resume_button = widget.TextButton(
        "Resume Game", env.norm_w-10, env.norm_h-7,
         unpause, anchor_y='top', anchor_x='right', size=24
    )
    end_button = widget.TextButton(
        "End Game", 10, env.norm_h-7, 
        gui.state_goer(3), anchor_y='top', size=24
    )
    restart_button = widget.TextButton(
        "Load Last Autosave", 10, end_button.y-50, 
        gui.state_goer(5),
        anchor_y='top', size=24
    )
    settings_button = widget.TextButton(
        "Settings", 10, restart_button.y-50, 
        gui.get_card_changer(gui.cards['settings']),
        anchor_y='top', size=24
    )
    save_button = widget.TextButton(
        "Save Game", 10, settings_button.y-100, 
        gui.get_card_changer(gui.cards['save']),
        anchor_y='top', size=24
    )
    
    widgets = [
        background, darken, 
        player_box_rect, player_box_rect_outline,
        key_box_rect, key_box_rect_outline,
        unpause_trigger, end_button,
        restart_button, settings_button, save_button, resume_button
    ]
    widgets.extend(unit_proxies)
    widgets.extend(labels)
    return widgets

def init_pause():
    global screenshot, to_release
    buffer_manager = pyglet.image.get_buffer_manager()
    screenshot = buffer_manager.get_color_buffer().get_texture()
    keychooser.screenshot = screenshot
    gui.cards['pause'] = gui.Card(pause_screen_widgets())
    gui.current_card = gui.cards['pause']
    gui.next_card = None
    gui.transition_time = 0
    gui.push_handlers()
    keychooser.prev_card_func = pause_screen_widgets
