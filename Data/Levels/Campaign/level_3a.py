from gamelib import event

B_TOP = 20      #to 3b
B_RIGHT = 7    #to 3c
B_BOTTOM = 21   #to 3f

RED_FOREIGN_KEY = 200

def go_top():
    event.move_player(-50, -50)
    event.go_to_level('level_3b', True, True, True)

def go_right():
    if not event.player_has_unit(RED_FOREIGN_KEY): return True
    event.move_player(-50, 0)
    event.go_to_level('level_3c', True, True, True)

def go_bottom():
    event.move_player(-50, 0)
    event.go_to_level('level_3f', True, True, True)

def save_state():    
    event.start_music('spooky')
    event.save_as("Mission 3")

def point():
    event.point_at_location(1000, 200)

def init():
    global msges
    msges = event.file_to_dict('Messages_3.txt')
    event.register_collision_func(B_TOP, go_top)
    event.register_collision_func(B_RIGHT, go_right)
    event.register_collision_func(B_BOTTOM, go_bottom)
    event.show_cutscene('t2_3')
    event.set_flag('from_level', '3a', True)
    event.register_timed_func(save_state, 1.0)
    
    event.show_ai_message(msges['human1_1'], 2, head='Terran_1')
    event.show_ai_message(msges['human2_2'], 2, head='Terran_2')
    event.show_ai_message(msges['human1_3'], 2, head='Terran_1')
    event.show_ai_message(msges['vn4n_7'], 3)
    event.show_ai_message(msges['gw0rp_8'], 2, head='gw0rp')
    event.show_ai_message(msges['vn4n_9'])
    event.register_timed_func(point, 11)
    #event.show_ai_message(msges['human2_4'], 3, head='Terran_2')
    #event.show_ai_message(msges['human1_5'], 3, head='Terran_1')
    #event.show_ai_message(msges['human2_6'], 4, head='Terran_2')

def on_load():
    global msges
    msges = event.file_to_dict('Messages_3.txt')
    if event.get_flag('from_level') == '3c':
        event.set_player_angle(-1.57)
    event.set_flag('from_level', '3a', True)
