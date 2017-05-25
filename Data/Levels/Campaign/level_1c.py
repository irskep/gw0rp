from gamelib import event, level
from gamelib.util import resources

LEFTWALL = 10
KEY = 7
TURRETS = [8, 9]
TRUCK = 13
TURRET_IN = 106
BEACON = 109
DETECTION = 156
KEY_SPOT = 158
BOMB = 157

msges = {}

def back_to_a():
    #if not event.get_flag('got_beacon_3') and event.get_flag('bomb_exploded'): return
    level.player.body.position.x += 50
    #event.move_player_back()
    event.go_to_level('level_1a', True, True, True)

def key_msg():
    if event.get_flag('showed_key_msg'): return
    event.set_flag('showed_key_msg', True)
    event.show_ai_message(msges['1c_key_msg'])

def detect():
    if event.get_flag('activated'): return
    event.set_flag('activated', True)
    for obj_id in TURRETS:
        obj = event.get_object(obj_id)
        obj.active = True
    #event.show_ai_message(msges['1c_attacking_1'])
    #event.show_ai_message(msges['1c_attacking_2'])
    #event.show_ai_message(msges['1c_attacking_3'])
    event.point_at(BEACON)

def beacon_attach():
    event.show_ai_message(msges['1c_run_1'])
    event.point_at_location(-1000, 200)
    event.set_flag('got_beacon_3', True, True)

def bomb_release():
    event.set_flag('bomb_exploded', True)

def bomb_attach():
    event.set_flag('bomb_exploded', False)

def init():
    global msges
    msges = event.file_to_dict('Messages.txt')
    resources.wall_sound = resources.metal_against_stone2
    event.register_collision_func(LEFTWALL, back_to_a)
    #event.register_attach_func(BOMB, bomb_attach)
    #event.register_release_func(BOMB, bomb_release)
    event.register_destroy_func(TURRET_IN, detect)
    event.register_attach_func(BEACON, beacon_attach)
    event.register_attach_func(KEY, key_msg)
    for obj_id in TURRETS:
        obj = event.get_object(obj_id)
        obj.active = False
        obj.rotation += 90
    
    event.set_flag('showed_key_msg', False)
    event.set_flag('activated', False)
    event.set_flag('from_level', '1c', True)
    event.set_flag('bomb_exploded', False)
    
    if not event.get_flag('set_beacon_1'):
        event.show_ai_message(msges['1c_err_1'])
        event.set_flag('showed_intro', False)
    elif not event.get_flag('showed_intro'):
        event.show_ai_message(msges['1c_intro_1'])
        #event.show_ai_message(msges['1c_intro_2'])
        event.set_flag('showed_intro', True)

def on_load():
    global msges
    msges = event.file_to_dict('Messages.txt')
    event.set_flag('from_level', '1c', True)
    resources.wall_sound = resources.metal_against_stone2
