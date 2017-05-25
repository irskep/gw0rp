from gamelib import event

B_BOTTOM = 81       #to 4e3
B_LEFT_TOP = 83     #to 4e5
B_LEFT_BOTTOM = 82  #to 4e6

def go_to(lev):
    event.go_to_level("Level_4"+lev, True, True, True)

def go_3():
    event.move_player(0, 50)
    go_to("e3")

def go_5():
    event.move_player(44, -24)
    go_to("e5")

def go_6():
    event.move_player(44, 24)
    go_to("e6")

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
    event.set_flag('from_level', '4e4', True)
    event.register_collision_func(B_BOTTOM, go_3)
    event.register_collision_func(B_LEFT_TOP, go_5)
    event.register_collision_func(B_LEFT_BOTTOM, go_6)
    if event.get_flag('kill_everything'): kill()

def on_load():
    event.set_flag('from_level', '4e4', True)
    if event.get_flag('kill_everything'): kill()