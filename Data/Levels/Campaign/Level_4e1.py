from gamelib import event

B_BOTTOM = 62   #to 4c
B_RIGHT = 63    #to 4e2
msges = {}

def go_to(lev):
    event.go_to_level("Level_4"+lev, True, True, True)

def go_c():
    event.move_player(0, 50)
    go_to("c")

def go_2():
    event.move_player(-50, 0)
    go_to("e2")

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
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    event.set_flag('from_level', '4e1', True)
    event.register_collision_func(B_BOTTOM, go_c)
    event.register_collision_func(B_RIGHT, go_2)
    
    if event.get_flag('kill_everything'): kill()
    event.show_ai_message(msges['e1p_1'], head='ph3ge')
    event.show_ai_message(msges['e1gs_2'], 3, head='gw0rp_subverted')
    event.show_ai_message(msges['e1p_3'], 3, head='ph3ge')
    event.show_ai_message(msges['e1gs_4'], head='gw0rp_subverted')

def on_load():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    event.set_flag('from_level', '4e1', True)
    if event.get_flag('kill_everything'): kill()
