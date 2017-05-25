from gamelib import event, level

LEFT_TRIGGER = 1
RIGHT_TRIGGER = 2
REPAIR_UNIT = 21
REPAIR_TRIGGER = 83
BOMBS = [81, 82]
VICTORY_TRIGGERS = [84, 85]
CARGO = [84] + range(200, 211)

KEY = 72

def go_d():
    level.player.body.position.x += 50
    event.go_to_level("level_2d", True, True, True)

def go_b():
    level.player.body.position.x -= 50
    event.set_flag("d2b", True, True)
    event.go_to_level("level_2b", True, True, True)

def explain_repair():
    if not event.get_flag('repair_explained'):
        event.set_flag('repair_explained', True)
        event.show_ai_message(msges['e_repair_1'])
        event.show_ai_message(msges['e_repair_2'], 3, head='gw0rp')
        event.show_ai_message(msges['e_repair_3'], 3)

def init():
    global msges
    msges = event.file_to_dict('Messages_2.txt')
    
    event.register_collision_func(RIGHT_TRIGGER, go_b)
    event.register_collision_func(LEFT_TRIGGER, go_d)
    event.register_collision_func(REPAIR_TRIGGER, explain_repair)

def on_load():
    global msges
    msges = event.file_to_dict('Messages_2.txt')