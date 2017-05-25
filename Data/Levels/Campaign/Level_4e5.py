from gamelib import event

B_RIGHT = 72    #to 4e4

def go_to(lev):
    event.go_to_level("Level_4"+lev, True, True, True)

def go_4():
    event.move_player(-44, 24)
    go_to("e4")

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
    event.set_flag('from_level', '4e5', True)
    event.register_collision_func(B_RIGHT, go_4)
    if event.get_flag('kill_everything'): kill()

def on_load():
    event.set_flag('from_level', '4e5', True)
    if event.get_flag('kill_everything'): kill()