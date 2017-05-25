from pyglet.window import key
from collections import defaultdict
from pyglet import gl

fullscreen = False
profiler = None
norm_w = 1120
norm_h = 700
norm_theta = 0.558599315344
sidebar_w = 0
scale_factor = 1.0
main_window = None
dt = 0.0

enable_damping = True

camera_x = 0
camera_y = 0
camera_target_x = 0
camera_target_y = 0
cvx = 1
cvy = 1

key_bindings = defaultdict(list)

def init():
    global key_bindings
    key_bindings = defaultdict(list)

def move_camera(x, y):
    global camera_x, camera_y
    if camera_x < camera_target_x-cvx: camera_x += cvx
    if camera_x > camera_target_x+cvx: camera_x -= cvx
    if abs(camera_x-camera_target_x) <= cvx: camera_x = camera_target_x
    if camera_y < camera_target_y-cvy: camera_y += cvy
    if camera_y > camera_target_y+cvy: camera_y -= cvy
    if abs(camera_y-camera_target_y) <= cvy: camera_y = camera_target_y

def scale():
    gl.glScalef(scale_factor,scale_factor,1)

def apply_camera():
    gl.glTranslatef( -camera_x+norm_w//2+sidebar_w//2, -camera_y+norm_h//2,0)

def clean_key_string(string):
    if string == "LSHIFT": return "Shift"
    if string == "RSHIFT": return "Right Shift"
    if string == "BACKSPACE": return "Backspace"
    if string == "TAB": return "Tab"
    if string == "CLEAR": return "Clear"
    if string == "RETURN": return "Return"
    if string == "ENTER": return "Enter"
    if string == "SCROLLLOCK": return "Scroll Lock"
    if string == "ESCAPE": return "Escape"
    if string == "HOME": return "Home"
    if string == "LEFT": return "Left"
    if string == "UP": return "Up"
    if string == "RIGHT": return "Right"
    if string == "DOWN": return "Down"
    if string == "PAGEUP": return "Page Up"
    if string == "PAGEDOWN": return "Page Down"
    if string == "END": return "End"
    if string == "DELETE": return "Delete"
    if string == "SELECT": return "Select"
    if string == "INSERT": return "Insert"
    if string == "SPACE": return "Space"
    if string == "CAPSLOCK": return "Caps Lock"
    return string

def symbol_to_string(symbol):
    return clean_key_string(key.symbol_string(symbol))
    
def bind_key(symbol, unit):
    global key_bindings
    key_bindings[symbol].append(unit)

def bind_keys(symbols, unit):
    global key_bindings
    for symbol in symbols:
        key_bindings[symbol].append(unit)

def clear_key_bindings():
    global key_bindings
    key_bindings = defaultdict(list)

def unbind_keys_for_unit(unit):
    global key_bindings
    for k, unit_list in key_bindings.items():
        if unit in unit_list:
            key_bindings[k].remove(unit)