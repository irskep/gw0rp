from gamelib import event, level

TOP_TRIGGER = 3
RIGHT_TRIGGER = 2
BACK_TRIGGER = 1

CARGO = 20

BOMBS = [11, 21, 22]
SHELF = 13

def go_c():
    level.player.body.position.y += 50
    event.go_to_level("level_2c", True, True, True)

def go_e():
    level.player.body.position.x -= 50
    event.go_to_level("level_2e", True, True, True)

def go_f():
    level.player.body.position.y -= 50
    event.go_to_level("level_2f", True, True, True)

def get_cargo():
    event.point_at_location(950, -1000)

def point():
    if not event.get_flag('pointed'):
        event.set_flag('pointed', True)
        event.point_at(SHELF)

def door():
    if not event.get_flag('doored'):
        event.set_flag('doored', True)
        event.point_at(0)

def init():
    global msges
    msges = event.file_to_dict('Messages_2.txt')
    
    event.register_collision_func(TOP_TRIGGER, go_f)
    event.register_collision_func(RIGHT_TRIGGER, go_e)
    event.register_collision_func(BACK_TRIGGER, go_c)
    event.register_attach_func(CARGO, get_cargo)
    
    event.point_at(CARGO)
    event.show_ai_message(msges['d_intro_1'], 3, head='vn4n')
    event.show_ai_message(msges['d_intro_2'], 3, head='gw0rp')
    event.show_ai_message(msges['d_intro_3'], 3)
    event.show_ai_message(msges['d_cargo_1'])
    
    for obj_id in BOMBS:
        event.register_attach_func(obj_id, point)
    
    event.register_collision_func(23, door)
    event.set_flag('from_level', '2d', True)

def on_load():
    global msges
    msges = event.file_to_dict('Messages_2.txt')
    event.set_flag('from_level', '2d', True)