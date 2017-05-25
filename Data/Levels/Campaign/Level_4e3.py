from gamelib import event
from gamelib.util import resources, sound

B_CENTER = 82   #to 4e2, req yellow
B_TOP = 83      #to 4e4

FROM_2  = 84

def go_to(lev, keep_vel=True):
    event.go_to_level("Level_4"+lev, True, True, keep_vel)

def go_4():
    event.move_player(0, -50)
    go_to("e4")

def go_2():
    event.move_player(-25, -25)
    sound.play(resources.elevator)
    go_to("e2", False)

def kill():
    event.clear_ai_messages()
    for i in range(300):
        try:
            o = event.get_object(i)
            if hasattr(o, 'active'):
                o.active = False
        except:
            pass

def init():
    event.set_flag('from_level', '4e3', True)
    event.register_collision_func(B_TOP, go_4)
    event.register_collision_func(B_CENTER, go_2)
    if event.get_flag('kill_everything'): kill()

def on_load():
    if event.get_flag('from_level') == '4e2':
        event.move_player_to_object(FROM_2)
    event.set_flag('from_level', '4e3', True)
    if event.get_flag('kill_everything'): kill()