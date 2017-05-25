from gamelib import event

B_BOTTOM = 90   #to 4e8
B_LEFT = 63     #to 5

msges = {}

def go_to(lev):
    event.go_to_level("Level_4"+lev, True, True, True)

def go_8():
    event.move_player(0, 50)
    go_to("e8")

def win():
    event.go_to_level("Level_5", False, True, False)

def kill():
    event.clear_ai_messages()
    if not event.get_flag('kmsg'):
        event.set_flag('kmsg', True)
        event.show_ai_message(msges['e11gs_1'], head='gw0rp_subverted')
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
    event.set_flag('from_level', '4e11', True)
    event.register_collision_func(B_BOTTOM, go_8)
    event.register_collision_func(B_LEFT, win)
    if event.get_flag('kill_everything'): kill()

def on_load():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    event.set_flag('from_level', '4e11', True)
    if event.get_flag('kill_everything'): kill()