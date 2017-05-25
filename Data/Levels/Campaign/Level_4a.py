from gamelib import event

B_TOP = 2       #to 4b

TOXIN = 86

msges = {}

def go_to_4b():
    event.move_player(0, -50)
    #event.move_player_back()
    event.go_to_level("Level_4b", True, True, True)

def get_toxin():
    if not event.get_flag('msg'):
        event.set_flag('msg', True)
        event.show_ai_message("A little trip down the elevator and these animals will no longer be a problem.", head='ph3ge')

def save_state():
    event.start_music('dark')
    event.save_as("Mission 4")

def init():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    event.register_collision_func(B_TOP, go_to_4b)
    event.register_timed_func(save_state, 1.0)
    event.register_attach_func(TOXIN, get_toxin)
    event.show_cutscene('t3_4')
    event.make_invisible(TOXIN)
    event.set_flag('show_toxin', False, True)
    event.set_flag('kill_everything', False, True)
    event.show_ai_message(msges['ah2_1'], 3, head='Terran_2')
    event.show_ai_message(msges['ah1_2'], 3, head='Terran_1')
    event.show_ai_message(msges['ah2_3'], head='Terran_2')

def on_load():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    if event.get_flag('show_toxin'):
        try:
            event.make_visible(TOXIN)
        except:
            pass
