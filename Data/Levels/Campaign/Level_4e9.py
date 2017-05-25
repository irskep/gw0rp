from gamelib import event

B_RIGHT = 70    #to 4e8
#B_CENTER = 69   #to 4e10, req red

def go_to(lev):
    event.go_to_level("Level_4"+lev, True, True, True)

def go_8():
    event.move_player(-44, 24)
    go_to("e8")

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
    event.set_flag('from_level', '4e9', True)
    event.register_collision_func(B_RIGHT, go_8)
    if event.get_flag('kill_everything'): kill()

def on_load():
    event.set_flag('from_level', '4e9', True)
    if event.get_flag('kill_everything'): kill()