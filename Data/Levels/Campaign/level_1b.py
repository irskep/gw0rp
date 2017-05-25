from gamelib import event, level
from gamelib.util import resources, sound

msges = {}

EDGE = 15
BEACON = 3
TARGET_IN = 165
TARGET_OUT = 154
ESCAPE_LINE = 12

ROCKS_1 = [2, 3, 4, 5, 7]
ROCKS_2 = [1, 10, 11, 8, 9]

BOMBS = [158, 159]
LANDER = 157

in_area = False

def enter_area():
    global in_area
    in_area = True

def exit_area():
    global in_area
    in_area = False

def attach_bomb():
    if not event.get_flag('got_bomb'):
        event.show_ai_message(msges['1b_bomb_1'])
        event.show_ai_message(msges['1b_bomb_2'])
        event.set_flag('got_bomb', True)

def goto_sublevel_a():
    level.player.body.position.y -= 50
    #event.move_player_back()
    event.go_to_level("level_1a", True, True, True)

def earthquake():    
    event.quake()
    event.register_timed_func(event.quake, 0.6)
    sound.play(resources.earthquake)

def release_beacon():
    if in_area:
        event.set_flag('set_beacon_2', True)
        unit = event.get_object(BEACON)
        unit.activate()
        unit.gluebody.attachable = False
        event.point_at(0)
        
        event.show_ai_message(msges['1b_release_0'], 1)
        event.register_timed_func(earthquake, 1)
        
        event.show_ai_message(msges['1b_release_1'])
        
        # event.show_radio_message("--~-**#*--$$#&^..")
        # event.show_radio_message(
        #     "... yeah, some kind of -~`#=%-- George's trail. Prolly #--#*-$"\
        #     "funky meteors. I'll go *-&=#*-. Red out."
        # )
        # event.show_radio_message("..^&#$$--*#**-~--")
        
        event.show_ai_message(msges['1b_release_2'])
        
        event.make_visible(LANDER)
        for obj_id in BOMBS + ROCKS_1:
            event.make_visible(obj_id)

def escape_line():
    if not event.get_flag('set_beacon_2') or event.get_flag('showed_escape_msg'):
        return
    event.clear_ai_messages()
    event.show_ai_message(msges['1b_bomb_3'])
    event.set_flag('showed_escape_msg', True)

def init():
    global msges
    msges = event.file_to_dict('Messages.txt')
    resources.wall_sound = resources.metal_against_stone2
    
    event.make_invisible(LANDER)
    for obj_id in ROCKS_1:
        event.make_invisible(obj_id)
    for obj_id in BOMBS:
        event.make_invisible(obj_id)
        event.register_attach_func(obj_id, attach_bomb)
    event.register_collision_func(EDGE, goto_sublevel_a)
    event.register_release_func(BEACON, release_beacon)
    event.register_collision_func(TARGET_IN, enter_area)
    event.register_collision_func(TARGET_OUT, exit_area)
    event.register_collision_func(ESCAPE_LINE, escape_line)
    
    event.set_flag('got_bomb', False)
    event.set_flag('showed_escape_msg', False)
    event.set_flag('from_level', '1b', True)
    
    if not event.get_flag('set_beacon_1'):
        event.show_ai_message(msges['1a_err_1'])
        event.set_flag('showed_intro', False)
    elif event.get_flag('got_beacon_1'):
        event.show_ai_message(msges['1b_intro_1'])
        event.show_ai_message(msges['1b_intro_2'])
        event.set_flag('showed_intro', True)
    
    if event.get_flag('got_beacon_2'):
        event.point_at_location(450,350)

def on_load():
    global msges
    msges = event.file_to_dict('Messages.txt')
    resources.wall_sound = resources.metal_against_stone2
    event.set_flag('from_level', '1b', True)
    if event.get_flag('set_beacon_1') and event.get_flag('got_beacon_2'):
        if not event.get_flag('showed_intro'):
            event.clear_ai_messages()
            event.show_ai_message(msges['1b_intro_1'])
            event.show_ai_message(msges['1b_intro_2'])
            event.set_flag('showed_intro', True)
    if event.get_flag('got_beacon_2') and not event.get_flag('set_beacon_2'):
        event.point_at_location(450,350)
