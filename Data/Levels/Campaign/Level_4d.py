from gamelib import event

B_BOTTOM = 61   #to 4c

TRIG = 62
TRIG_2 = 63

KEY_B = 48
KEY_G = 47
msges = {}

def go_c():
    event.move_player(0, 50)
    event.go_to_level("Level_4c", True, True, True)

def dig_msg():
    if event.get_flag('digger_msg'): return
    event.set_flag('digger_msg', True)
    event.show_ai_message(msges['dp_1'], head='ph3ge')

def dig_msg_2():
    if event.get_flag('digger_msg_2'): return
    event.set_flag('digger_msg_2', True)
    event.show_ai_message(msges['d2p_1'], head='ph3ge')
    event.show_ai_message(msges['d2v_2'])
    event.show_ai_message(msges['d2p_3'], head='ph3ge')
    event.show_ai_message(msges['d2v_4'])
    event.show_ai_message(msges['d2v_5'])
    event.show_ai_message(msges['d2p_6'], head='ph3ge')
    event.show_ai_message(msges['d2gs_7'], head='gw0rp_subverted')

def init():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    event.set_flag('from_level', '4d', True)
    event.register_collision_func(B_BOTTOM, go_c)
    event.register_collision_func(TRIG, dig_msg)
    event.register_collision_func(TRIG_2, dig_msg_2)

def on_load():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    event.set_flag('from_level', '4d', True)