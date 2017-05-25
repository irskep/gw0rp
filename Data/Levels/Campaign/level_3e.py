import math
from gamelib import event
from gamelib.util import resources, sound

B_TOP = 41  #to 3c

YELLOW_FOREIGN_KEY = 25
BOMB = 47

def go_top():
    if not event.player_has_unit(YELLOW_FOREIGN_KEY): return False
    event.move_player(-50, -50)
    sound.play(resources.elevator)
    event.go_to_level('level_3c', True, True)

def init():
    global msges
    msges = event.file_to_dict('Messages_3.txt')
    event.register_collision_func(B_TOP, go_top)
    event.set_player_rotation(135)
    event.rotate_player_velocity(math.pi*1.25)
    event.set_flag('from_level', '3e', True)
    event.stop_player()
    event.get_object(BOMB).health = 100000

def on_load():
    global msges
    msges = event.file_to_dict('Messages_3.txt')
    event.set_player_rotation(135)
    event.rotate_player_velocity(math.pi*1.25)
    event.set_flag('from_level', '3e', True)
    event.stop_player()