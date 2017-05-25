from gamelib import event
from gamelib.util import resources, sound

B_LEFT = 55     #to 4e1
B_CENTER = 54   #to 4e3, req yellow

FROM_3 = 75

msges = {}

def go_to(lev, keep_vel=True):
    event.go_to_level("Level_4"+lev, True, True, keep_vel)

def go_1():
    event.move_player(50, 0)
    go_to("e1")

def go_3():
    event.move_player(25, -25)
    sound.play(resources.elevator)
    go_to("e3", False)

def kill():
    event.clear_ai_messages()
    for i in range(200):
        try:
            o = event.get_object(i)
            if hasattr(o, 'active'):
                o.active = False
        except:
            pass

def init():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    event.set_flag('from_level', '4e2', True)
    event.register_collision_func(B_LEFT, go_1)
    event.register_collision_func(B_CENTER, go_3)
    
    event.show_ai_message(msges['e2h1_1'], 3, head='Terran_1')
    event.show_ai_message(msges['e2h2_2'], 4, head='Terran_2')
    event.show_ai_message(msges['e2h1_3'], head='Terran_1')
    event.show_ai_message(msges['e2h2_4'], head='Terran_2')
    if event.get_flag('kill_everything'): kill()

def on_load():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    if event.get_flag('from_level') == '4e3':
        event.move_player_to_object(FROM_3)
    event.set_flag('from_level', '4e2', True)
    if event.get_flag('kill_everything'): kill()