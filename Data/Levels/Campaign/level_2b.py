import math
from gamelib import event, level

A_TRIGGER = 1
E_TRIGGER = 15
RIGHT_TRIGGER = 63
ENTER_TOP = 74
ENTER_BOTTOM = 75
CARGO  = [76, 77]
msges = {}


def go_a():
    level.player.body.position.x += 50
    level.player.body.position.y += 50
    event.go_to_level("level_2a", True, True, True)

def go_e():
    level.player.body.position.x -= 50
    event.go_to_level("level_2e", True, True, True)

def reset_nag():
    event.set_flag('2b_nag', False)

def nag():
    if event.get_flag('2b_nag'): return
    event.set_flag('2b_nag', True)
    n = event.get_flag('2b_nag_num')
    event.clear_ai_messages()
    event.show_ai_message(msges["nag_"+str(n)])
    event.set_flag('2b_nag_num', n % 12 + 1)
    event.register_timed_func(reset_nag, 5.0)

def init():
    global msges
    msges = event.file_to_dict('Messages_2.txt')
    
    event.register_collision_func(A_TRIGGER, go_a)
    event.register_collision_func(E_TRIGGER, go_e)
    event.register_collision_func(RIGHT_TRIGGER, nag)
    
    event.set_flag('2b_nag', False)
    event.set_flag('2b_nag_num', 1)
    event.rotate_player_velocity(0.5)
    
    event.show_ai_message(msges['b_intro'])

def on_load():
    global msges
    msges = event.file_to_dict('Messages_2.txt')
    if event.get_flag("d2b"):
        newpos_obj = event.get_object(ENTER_TOP)
        level.player.body.position.x = newpos_obj.x
        level.player.body.position.y = newpos_obj.y
    else:
        event.rotate_player_velocity(0.5)
