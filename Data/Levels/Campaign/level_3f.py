from gamelib import event

B_LEFT = 1      #to 3a
B_TOP = 2       #to 3g

TRIG = 89

DOOR = 71
TURRETS = [72, 73]

def go_top():
    event.move_player(0, -50)
    event.go_to_level('level_3g', True, True, True)
    event.stop_music()

def go_left():
    event.move_player(50, 0)
    event.go_to_level('level_3a', True, True, True)

def gen_msg():
    event.show_message("Objective: Destroy Generator")

def talk():
    if event.get_flag('3_gen_destroyed') and not event.get_flag('showed_msg_2'):
        event.set_flag('showed_msg_2', True)
        event.show_ai_message(msges['human2_3fbridge_1'], head='Terran_2')
        event.show_ai_message(msges['human1_3fbridge_2'], 2, head='Terran_1')
        event.show_ai_message(msges['vn4n_3fbridge_3'])
    else:
        if event.get_flag('showed_msg'): return
        event.set_flag('showed_msg', True)
        event.show_ai_message(msges['vn4n_10'])
        event.register_timed_func(gen_msg, 2)

def init():
    global msges
    msges = event.file_to_dict('Messages_3.txt')
    event.register_collision_func(B_TOP, go_top)
    event.register_collision_func(B_LEFT, go_left)
    event.register_collision_func(TRIG, talk)
    if not event.get_flag("3_gen_destroyed"):
        event.close_door(DOOR)
    else:
        event.open_door(DOOR)
        for obj_id in TURRETS:
            try:
                event.get_object(obj_id).active = False
            except:
                pass    #don't care

def on_load():
    global msges
    msges = event.file_to_dict('Messages_3.txt')
    if not event.get_flag("3_gen_destroyed"):
        event.close_door(DOOR)
    else:
        event.open_door(DOOR)
        for obj_id in TURRETS:
            try:
                event.get_object(obj_id).active = False
            except:
                pass    #don't care
