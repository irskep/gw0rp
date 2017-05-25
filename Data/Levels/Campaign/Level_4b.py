from gamelib import event
from gamelib.util import resources, sound

B_BOTTOM = 40   #to 4a
B_TOP = 41      #to 4c
KEY_R = 62

TOXIN = 86

KEY_Y = 87
msges = {}

def go_to_4c():
    if not event.player_has_unit(KEY_Y):
        if not event.get_flag("el_msg"):
            event.show_message("Key required for elevator.")
            event.set_flag("el_msg", True)
        return
    event.move_player(-25, 25)
    sound.play(resources.elevator)
    event.go_to_level("Level_4c", True, True)

def go_to_4a():
    event.move_player(0, 50)
    event.go_to_level("Level_4a", True, True, True)

def init():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    event.set_flag('from_level', '4b', True)
    event.register_collision_func(B_TOP, go_to_4c)
    event.register_collision_func(B_BOTTOM, go_to_4a)
    event.show_ai_message(msges['bv_1'])

def on_load():
    global msges
    msges = event.file_to_dict('Messages_4.txt')
    if event.get_flag("show_toxin") and not event.player_has_unit(TOXIN):
        event.point_at_location(504, -100)
    event.set_flag('from_level', '4b', True)