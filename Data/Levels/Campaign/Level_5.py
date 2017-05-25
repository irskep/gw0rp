from gamelib import event

BRAIN = 77
TRIGS = range(78, 84)
msges = {}

def msg_1():
    if not event.get_flag('msg_1'):
        event.set_flag('msg_1', True)
        event.show_ai_message(msges['k1'], head='gw0rp_subverted')

def msg_2():
    if not event.get_flag('msg_2'):
        event.set_flag('msg_2', True)
        event.show_ai_message(msges['k2'], head='gw0rp_subverted')

def msg_3():
    if not event.get_flag('msg_3'):
        event.set_flag('msg_3', True)
        event.show_ai_message(msges['k3'], head='gw0rp_subverted')

def msg_4():
    if not event.get_flag('msg_4'):
        event.set_flag('msg_4', True)
        event.show_ai_message(msges['k4'], head='gw0rp_subverted')

def msg_5():
    if not event.get_flag('msg_5'):
        event.set_flag('msg_5', True)
        event.show_ai_message(msges['k5'], head='gw0rp_subverted')

def msg_6():
    if not event.get_flag('msg_6'):
        event.set_flag('msg_6', True)
        event.show_ai_message(msges['k6'], head='gw0rp_subverted')

def win():
    event.win()

def lose():
    event.trigger_fail()

def init():
    global msges
    msges = event.file_to_dict('Messages_5.txt')
    funcs = [msg_1, msg_2, msg_3, msg_4, msg_5, msg_6]
    i = 77
    for f in funcs:
        i += 1
        event.register_collision_func(i, f)
    event.show_message("Objective: Assimilate gw0rp")
    event.register_attach_func(BRAIN, win)
    event.register_destroy_func(BRAIN, lose)

def on_load():
    global msges
    msges = event.file_to_dict('Messages_5.txt')