from gamelib import event

B_LEFT_BOTTOM = 86  #to 4e7
B_LEFT_TOP = 87     #to 4e9
B_TOP = 88          #to 4e11

msges = {}

def go_to(lev):
    event.go_to_level("Level_4"+lev, True, True, True)

def go_7():
    event.move_player(44, 24)
    go_to("e7")

def go_9():
    event.move_player(44, -24)
    go_to("e9")

def go_11():
    event.move_player(0, -50)
    go_to("e11")

def kill():
    event.clear_ai_messages()
    if not event.get_flag('kmsg'):
        event.set_flag('kmsg', True)
        event.show_ai_message(msges['e8gs_1'], head='gw0rp_subverted')
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
    event.set_flag('from_level', '4e8', True)
    event.register_collision_func(B_LEFT_BOTTOM, go_7)
    event.register_collision_func(B_LEFT_TOP, go_9)
    event.register_collision_func(B_TOP, go_11)
    if event.get_flag('kill_everything'): kill()

def on_load():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    event.set_flag('from_level', '4e8', True)
    if event.get_flag('kill_everything'): kill()