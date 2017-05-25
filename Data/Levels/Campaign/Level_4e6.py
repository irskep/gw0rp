from gamelib import event
from gamelib.util import resources, sound

B_RIGHT = 68    #to 4e4
B_CENTER = 67   #to 4e7, req blue

FROM_7 = 69

KEY_B = 48
KEY_G = 47
KEY_R = 63

msges = {}

def go_to(lev, keep_vel=True):
    event.go_to_level("Level_4"+lev, True, True, keep_vel)

def go_4():
    event.move_player(-44, -24)
    go_to("e4")

def go_7():
    if not event.player_has_unit(KEY_B): return
    event.move_player(-25, 25)
    sound.play(resources.elevator)
    go_to("e7", False)

def kill():
    event.clear_ai_messages()
    if not event.get_flag('kmsg'):
        event.set_flag('kmsg', True)
        event.show_ai_message(msges['e6gs_1'], head='gw0rp_subverted')
    for i in range(300):
        try:
            o = event.get_object(i)
            if hasattr(o, 'active'):
                o.active = False
        except:
            pass

def init():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    event.set_flag('from_level', '4e6', True)
    event.register_collision_func(B_RIGHT, go_4)
    event.register_collision_func(B_CENTER, go_7)
    if event.get_flag('kill_everything'): kill()

def on_load():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    if event.get_flag('from_level') == '4e7':
        event.move_player_to_object(FROM_7)
    event.set_flag('from_level', '4e6', True)
    if event.get_flag('kill_everything'): kill()