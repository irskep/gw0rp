from gamelib import event
from gamelib.util import resources, sound

B_BOTTOM = 42   #to 4c
T_RIGHT = 41
TRIG_OUT = 50
TOXIN = 86

KEY_B = 48
KEY_G = 47
KEY_R = 62

in_area = False
msges = {}

def kill():
    for i in range(200):
        try:
            o = event.get_object(i)
            if hasattr(o, 'active'):
                o.active = False
        except:
            pass

def go_to(lev, keep_vel=True):
    event.go_to_level("Level_4"+lev, True, True, keep_vel)

def go_c():
    if not event.player_has_unit(KEY_R): return
    event.move_player(0, 50)
    sound.play(resources.elevator)
    go_to("c", False)

def enter_area():
    global in_area
    if not in_area and not event.get_flag('msg_1'):
        event.set_flag('msg_1', True)
        event.show_ai_message("This is far enough. Time to let go...", head='ph3ge')
    in_area = True

def exit_area():
    global in_area
    in_area = False

def toxinate():
    if in_area and not event.get_flag('kill_everything'):
        event.set_flag('kill_everything', True, True)
        sound.play(resources.gas)
        event.quake()
        event.show_cutscene("4_2")
        event.point_at(0)

def be_badass():
    event.start_music('battle')

def init():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    event.set_flag('from_level', '4f', True)
    event.register_collision_func(B_BOTTOM, go_c)
    event.register_collision_func(T_RIGHT, enter_area)
    event.register_collision_func(TRIG_OUT, exit_area)
    event.register_release_func(TOXIN, toxinate)
    
    event.point_at_location(1350, 590)
    event.show_message("Place bomb at arrow")
    
    if not event.get_flag('cut') and event.player_has_unit(TOXIN):
        event.set_flag('cut', True)
        event.stop_music()
        event.show_cutscene('4_1')
        event.register_timed_func(be_badass, 3)
    kill()

def on_load():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    event.set_flag('from_level', '4f', True)
    kill()