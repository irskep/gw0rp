B_RIGHT = 26    #to 3c

from gamelib import event

def go_right():
    event.move_player(0, 50)
    event.go_to_level('level_3c', True, True, True)

def init():    
    global msges
    msges = event.file_to_dict('Messages_3.txt')
    event.register_collision_func(B_RIGHT, go_right)
    event.set_flag('from_level', '3d', True)
    event.show_ai_message(msges['gw0rp3d_1'], head='gw0rp')
    event.show_ai_message(msges['vn4n3d_2'])
    event.show_ai_message(msges['gw0rp3d_3'], head='gw0rp')

def on_load():
    global msges
    msges = event.file_to_dict('Messages_3.txt') 
    event.set_flag('from_level', '3d', True)
