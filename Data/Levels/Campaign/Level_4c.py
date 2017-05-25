from gamelib import event
from gamelib.util import resources, sound

B_RIGHT = 41    #to 4d
B_TOP = 42      #to 4e1
B_R = 23        #to 4f
B_Y = 24        #to 4b        
FROM_4f = 44
FROM_4b = 43

KEY_Y = 87
KEY_B = 48
KEY_G = 47
KEY_R = 62

TOXIN = 86

DOOR_G = 45
msges = {}

def go_to(lev, keep_vel=True):
    event.go_to_level("Level_4"+lev, True, True, keep_vel)

def go_to_4d():
    event.move_player(-24, -43)
    go_to("d")

def go_to_4e1():
    event.move_player(0, -50)
    go_to("e1")

def go_to_4f():
    if not event.player_has_unit(KEY_R):
        if not event.get_flag("el_msg_1"):
            event.show_message("Key required for elevator.")
            event.set_flag("el_msg_1", True)
    event.move_player(25,-25)
    sound.play(resources.elevator)
    go_to("f", False)

def go_to_4b():
    if not event.player_has_unit(KEY_Y):
        if not event.get_flag("el_msg_2"):
            event.show_message("Key required for elevator.")
            event.set_flag("el_msg_2", True)
    event.move_player(-25, 25)
    sound.play(resources.elevator)
    go_to("b", False)

def init():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    event.set_flag('from_level', '4c', True)
    event.register_collision_func(B_RIGHT, go_to_4d)
    event.register_collision_func(B_TOP, go_to_4e1)
    event.register_collision_func(B_R, go_to_4f)
    event.register_collision_func(B_Y, go_to_4b)
    event.show_ai_message(msges['cp_1'], 3, head='ph3ge')
    event.show_ai_message(msges['cp_2'], 2, head='ph3ge')
    event.show_ai_message(msges['cgs_3'], 4, head='gw0rp_subverted')
    event.show_ai_message(msges['cp_4'], 4, head='ph3ge')

def on_load():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    if event.get_flag('from_level') == '4f':
        event.move_player_to_object(FROM_4f)
    if event.get_flag('from_level') == '4b':
        event.move_player_to_object(FROM_4b)
    if event.get_flag('from_level') == '4e1':
        if event.player_has_unit(KEY_R):
            if not event.get_flag('msg'):
                event.set_flag('msg', True)
                event.show_cutscene('4_0')
                event.set_flag('show_toxin', True, True)
                event.point_at_location(200, 277)
    if event.player_has_unit(TOXIN):
        event.point_at_location(300, 262)
    event.set_flag('from_level', '4c', True)
