from gamelib import event
from gamelib.util import resources, sound

msges = {}

B_RIGHT = 15    #to 3d
B_LEFT = 29     #to 3a
B_TOP = 6       #to 3e

RED_FOREIGN_KEY = 200
YELLOW_FOREIGN_KEY = 25

GENERATOR = 26
GENERATOR_IN = 7
GENERATOR_OUT = [8, 9]

BOMB = 47

FROM_E_LOC = 43

TANK_L = 250
TANK_M = 23
TANK_R = 24

TURRETS = [18, 19, 21, 22]

in_area = False
    
def enter_area():
    global in_area
    in_area = True

def exit_area():
    global in_area
    if not event.get_flag('bomb_msg'):
        event.set_flag('bomb_msg', True)
        event.show_message("Objective: Find Bomb, Blow Generator")
    if not in_area and event.get_flag('3c_placed_bomb') and not event.get_flag('3_gen_destroyed'):
        event.set_flag('3_gen_destroyed', True, True)
        event.get_object(GENERATOR).image = resources.Generator_wrecked
        event.point_at(0)
        event.show_message('Door Opened')
        try:
            event.get_object(BOMB).detonate()
        except:
            pass
        for obj_id in TURRETS:
            try:
                event.get_object(obj_id).active = False
            except:
                pass    #don't care
    in_area = False

def drop_bomb():
    if in_area:
        event.set_flag('3c_placed_bomb', True)
    else:
        event.show_message('Bomb Not Close Enough')

def go_top():
    if not event.player_has_unit(YELLOW_FOREIGN_KEY):
        if not event.get_flag('key_msg'):
            event.set_flag('key_msg', True)
            event.show_message("Key required for elevator")
        return False
    sound.play(resources.elevator)
    event.move_player(-50, 0)
    event.go_to_level('level_3e', True, True)

def go_right():
    event.move_player(0, -50)
    event.go_to_level('level_3d', True, True, True)

def go_left():
    if not event.player_has_unit(RED_FOREIGN_KEY): return True
    event.move_player(50, 0)
    event.go_to_level('level_3a', True, True, True)

def init():
    global msges
    msges = event.file_to_dict('Messages_3.txt')
    event.register_collision_func(B_TOP, go_top)
    event.register_collision_func(B_RIGHT, go_right)
    event.register_collision_func(B_LEFT, go_left)
    event.register_collision_func(GENERATOR_IN, enter_area)
    event.register_collision_func(GENERATOR_OUT[0], exit_area)
    event.register_collision_func(GENERATOR_OUT[1], exit_area)
    event.register_release_func(BOMB, drop_bomb)
    if event.get_flag('from_level') == '3a':
        event.set_player_rotation(0)
    event.set_flag('from_level', '3c', True)    
    event.set_flag('3_gen_destroyed', False, True)
    event.get_object(TANK_L).active = False
    event.get_object(TANK_M).active = False
    event.get_object(TANK_R).active = False
    for obj_id in TURRETS:
        event.get_object(obj_id).active = False
    event.show_ai_message(msges['gw0rp_enter3c'], head='gw0rp')

def on_load():
    global msges
    msges = event.file_to_dict('Messages_3.txt')
    if event.get_flag('from_level') == '3a':
        event.set_player_rotation(0)
    elif event.get_flag('from_level') == '3e':
        #event.move_player_to_object(FROM_E_LOC)
        #event.set_player_angle(1.57)
        for obj_id in [TANK_L, TANK_M, TANK_R]:
            try:
                event.get_object(obj_id).active = True
            except:
                pass    #don't care
        for obj_id in TURRETS:
            try:
                event.get_object(obj_id).active = True
            except:
                pass #don't care
        event.stop_player()
    if event.player_has_unit(BOMB) and not event.get_flag('bomb_msg_1'):
        event.show_message("Plant the bomb near the generator.")
        event.point_at(GENERATOR)
        event.set_flag('bomb_msg_1', True)
    event.set_flag('from_level', '3c', True)
