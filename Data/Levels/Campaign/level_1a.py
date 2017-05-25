from gamelib import event, level
from gamelib.util import resources

msges = {}

in_area = False
BEACON_1 = 2
BEACON_2 = 3
BEACON_3 = 109
BOTTOM_EDGE = 89
RIGHT_EDGE = 91
TARGET_IN = [88, 95]
TARGET_OUT = [90, 92, 93, 94] + [96, 97, 98, 99]

BEACON_PLANTED = 94

def enter_area():
    global in_area
    in_area = True
    if event.get_flag('z_1') and not event.get_flag('z_2'):
        event.set_flag('z_2', True)
        #event.show_message("Press Z to drop the beacon.")
    if not event.get_flag('showed_release_tut'):
        event.clear_ai_messages()
        event.show_ai_message(msges['1a_tut_1'])
        event.set_flag('showed_release_tut', True)

def exit_area():
    global in_area
    in_area = False
    if not event.get_flag('z_1'):
        event.set_flag('z_1', True)

def goto_sublevel_b():
    level.player.body.position.y += 50
    #event.move_player_back()
    event.go_to_level("level_1b", True, True, True)

def goto_sublevel_c():
    if not event.get_flag('set_beacon_2'): return
    level.player.body.position.x -= 50
    #event.move_player_back()
    event.go_to_level("level_1c", True, True, True)

def goto_level_2():
    event.stop_music()
    event.clear_image_cache()
    event.go_to_level("level_2a")

def collide_beacon_1():
    if event.get_flag('showed_collide_msg') or event.get_flag('set_beacon_1'): return
    event.set_flag('showed_collide_msg', True)
    event.show_message("Hold Shift and hit the beacon.")

def attach_beacon_1():
    if event.get_flag('got_beacon_1'): return
    event.set_flag('got_beacon_1', True)
    event.clear_ai_messages()
    event.show_ai_message(msges['1a_attach_1'])
    event.point_at_location(1100, 1300)
    event.show_ai_message(msges['1a_attach_2'])
    #event.show_ai_message(msges['1a_attach_3'])

def release_beacon_1():
    if not in_area: return
    event.clear_ai_messages()
    event.point_at(BEACON_2)
    unit = event.get_object(BEACON_1)
    unit.activate()
    unit.gluebody.attachable = False
    event.make_visible(BEACON_2)
    event.set_flag('set_beacon_1', True)
    event.show_ai_message(msges['1a_release'])

def attach_beacon_2():
    if event.get_flag('got_beacon_2'): return
    event.set_flag('got_beacon_2', True)
    event.point_at_location(1000, -1000)

def release_beacon_3():
    if not in_area: return
    if event.get_flag('set_beacon_3'): return
    event.set_flag('set_beacon_3', True)
    unit = event.get_object(BEACON_3)
    unit.activate()
    unit.gluebody.attachable = False
    event.point_at(0)
    event.show_message("Mission 1 Complete", 1000000000)
    event.register_timed_func(goto_level_2, 3.0)

def point_right():    
    if not event.get_flag('from_level') == '1c':
        event.point_at_location(4000, 100)

def start_music():    
    event.start_music('exploring')

def init():
    global msges
    msges = event.file_to_dict('Messages.txt')
    resources.wall_sound = resources.metal_against_stone2
    event.register_collision_func(BOTTOM_EDGE, goto_sublevel_b)
    event.register_collision_func(RIGHT_EDGE, goto_sublevel_c)
    event.register_collision_func(BEACON_1, collide_beacon_1)
    for obj_id in TARGET_IN:
        event.register_collision_func(obj_id, enter_area)
    for obj_id in TARGET_OUT:
        event.register_collision_func(obj_id, exit_area)
    event.register_attach_func(BEACON_1, attach_beacon_1)
    event.register_release_func(BEACON_1, release_beacon_1)
    event.register_attach_func(BEACON_2, attach_beacon_2)
    event.register_timed_func(start_music, 1.0)
    
    event.register_release_func(BEACON_3, release_beacon_3)
    
    event.show_message("Level 1")
    event.set_flag('got_beacon_1', False, True)
    event.set_flag('set_beacon_1', False, True)
    event.set_flag('got_beacon_2', False, True)
    event.set_flag('set_beacon_2', False, True)
    event.set_flag('got_beacon_3', False, True)
    event.set_flag('set_beacon_3', False, True)
    
    event.set_flag('showed_release_tut', False)
    event.set_flag('showed_b3_msg', False)
    event.set_flag('from_level', '1a', True)
    
    event.set_flag('z_1', False)
    event.set_flag('z_2', False)
    
    event.make_invisible(BEACON_2)
    
    event.show_cutscene('Intro')
    
    event.show_ai_message(msges['1a_intro_1'])
    event.show_ai_message(msges['1a_intro_2'])

def on_load():
    global msges
    msges = event.file_to_dict('Messages.txt')
    resources.wall_sound = resources.metal_against_stone2
    event.clear_messages()
    if event.get_flag('got_beacon_1') and not event.get_flag('set_beacon_1'):
        event.point_at_location(1100, 1300)
    if event.get_flag('set_beacon_2'):
        event.point_at(0)
        if not event.get_flag('showed_b3_msg'):
            event.show_ai_message(msges['1a_intro_3'])
            event.show_ai_message(msges['1a_intro_4'])
            event.register_timed_func(point_right, 5)
            event.set_flag('showed_b3_msg', True)
        else:
            event.clear_ai_messages()
    if event.get_flag('got_beacon_3') and not event.get_flag('set_beacon_3'):
        event.point_at_location(523,363)
    if event.get_flag('from_level') == '1c':
        event.rotate_player_velocity(3.14)
    event.set_flag('from_level', '1a', True)
