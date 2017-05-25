B_BOTTOM = 18   #to 3a

from gamelib import event

def go_bottom():
    event.move_player(0, 50)
    event.go_to_level('level_3a', True, True, True)

def init():
    global msges
    msges = event.file_to_dict('Messages_3.txt')
    event.register_collision_func(B_BOTTOM, go_bottom)

def on_load():
    global msges
    msges = event.file_to_dict('Messages_3.txt')
