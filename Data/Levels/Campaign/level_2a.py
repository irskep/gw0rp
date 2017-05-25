from gamelib import event, level

TOP_TRIGGER = 14
RIGHT_TRIGGER = 15
DOOR = 16
BOTTOM_TRIGGER = 61

msges = {}

def go_up():
    level.player.body.position.y -= 50
    event.go_to_level("level_2c", True, True, True)

def go_right():
    level.player.body.position.x -= 50
    event.go_to_level("level_2b", True, True, True)

def reset_nag():
    event.set_flag('2a_nag', False)

def nag():
    if event.get_flag('2a_nag'): return
    event.set_flag('2a_nag', True)
    event.show_ai_message("You just came from there. No need to go back.")
    event.register_timed_func(reset_nag, 5.0)

def save_state():
    event.save_as("Mission 2")

def init():
    global msges
    msges = event.file_to_dict('Messages_2.txt')
    event.register_collision_func(TOP_TRIGGER, go_up)
    event.register_collision_func(RIGHT_TRIGGER, go_right)
    event.register_collision_func(BOTTOM_TRIGGER, nag)\
    
    event.set_flag('2a_nag', False)
    event.show_cutscene('t1_2')
    event.show_ai_message(msges['a_intro'])
    event.show_ai_message(msges['a_intro_2'], head="Terran_1")
    event.register_timed_func(save_state, 1.0)
    event.point_at_location(200, 10000)
    
def on_load():
    global msges
    msges = event.file_to_dict('Messages_2.txt')
    event.set_flag('from_level', '2a', True)
