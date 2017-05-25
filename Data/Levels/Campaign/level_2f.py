from gamelib import event, level
from gamelib.util import physics, resources

ENTER_TRIGGER = 149
EXIT_TRIGGER = 150
BACK_TRIGGER = 1
GENERATOR = 112
GENERATOR_OUTLINE = range(122, 143)
TURRETS = range(113, 118)

BOMB = 118
CARGO = range(119, 122) + [143, 144, 145, 146, 147, 148]
GUARDED_CARGO = [119, 143, 144, 145, 146, 147, 148]
CARGO_TRIGGER = 143

TURRET_EXPLAIN_TRIGGER = 151

in_area = False

def go_d():
    level.player.body.position.y += 50
    event.go_to_level("level_2d", True, True, True)
    
def enter_area():
    global in_area
    in_area = True

def exit_area():
    global in_area
    in_area = False
    if event.get_flag('placed_bomb') and not event.get_flag('generator_destroyed'):
        event.set_flag('generator_destroyed', True)
        event.get_object(GENERATOR).image = resources.Generator_wrecked
        try:
            event.get_object(BOMB).detonate()
        except:
            pass
        for obj_id in TURRETS:
            event.get_object(obj_id).active = False
        event.show_ai_message(msges['f_explode_1'], head='Terran_1')    
        event.show_ai_message(msges['f_explode_2'], head='Terran_2')

def drop_bomb():
    if in_area:
        event.set_flag('placed_bomb', True)

def explain_turrets():
    if not event.get_flag('turrets_explained'):
        event.set_flag('turrets_explained', True)
        event.show_ai_message(msges['f_turrets_1'])
        event.show_ai_message(msges['f_turrets_2'])
        event.point_at(BOMB)

def attach_bomb():
    event.point_at(GENERATOR)

def init():
    global msges
    msges = event.file_to_dict('Messages_2.txt')
    event.register_collision_func(TURRET_EXPLAIN_TRIGGER, explain_turrets)
    event.register_collision_func(BACK_TRIGGER, go_d)
    event.register_collision_func(ENTER_TRIGGER, enter_area)
    event.register_collision_func(EXIT_TRIGGER, exit_area)
    event.register_release_func(BOMB, drop_bomb)
    event.register_attach_func(BOMB, attach_bomb)
    event.set_flag('generator_destroyed', False)
    event.set_flag('placed_bomb', False)
    for obj_id in TURRETS:
        event.get_object(obj_id).health = 5000

def on_load():
    global msges
    msges = event.file_to_dict('Messages_2.txt')
