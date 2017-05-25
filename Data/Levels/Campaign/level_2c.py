from gamelib import event, level
from gamelib.util import resources
import random

IN_TRIGGER = 10
BACK_TRIGGER = 30

START_TANKS = [35, 36]
WAVE_2 = [68, 69, 70]
ALL_TANKS = START_TANKS
DOOR_BOTTOM = 34
DOORS_TOP = [55, 56]
DIGGER = 37
DIGGER_IN = 38
DIGGER_OUT = [39, 40]
DIGGER_CIRC = 54
PLASMA = 59
ENTER_TRIGGER = 45
TURRETS = [32, 33, 35, 36, 50, 57, 58, 68]
THRUSTERS = [52, 53]

CARGO = [20, 76, 77, 84] + range(143, 149) + range(119, 122) + range(200, 211)

in_area = False

def win_2():
    event.clear_image_cache()
    event.go_to_level('level_3a')

def win():
    event.register_timed_func(win_2, 0.1)

def cargo_release(obj_id=0):
    if obj_id == 0: return
    if in_area:
        event.set_flag('cargo_list', event.get_flag('cargo_list') + [obj_id])    
        u = event.get_object(obj_id, search_decals=False, search_bodies=False)
        u.activate()
        event.point_at(0)
        event.clear_messages()
        if len(event.get_flag('cargo_list')) >= 15:
            event.register_timed_func(win, 3)
            event.show_message("Mission 2 complete")
            event.get_object(DIGGER).image = resources.Digger_anim
            event.set_flag('digger_fixed', True)
        else:
            msg = str(len(event.get_flag('cargo_list')))+" of 15 Resource Units Located"
            event.show_message(msg)

def cargo_attach(obj_id=0):
    if obj_id == 0: return
    clst = event.get_flag('cargo_list')
    event.get_object(obj_id).deactivate()
    if obj_id in clst:
        clst.remove(obj_id)
        event.set_flag('cargo_list', clst)

def go_a():
    level.player.body.position.y += 50
    event.go_to_level("level_2a", True, True, True)

def go_d():
    level.player.body.position.y -= 50
    event.go_to_level("level_2d", True, True, False)

def show_intro():
    if not event.get_flag('showed_intro'):
        event.set_flag('showed_intro', True)
        event.show_ai_message(msges['c_door'])

def explain_digger():
    event.clear_image_cache()
    event.start_music('lev2')
    if not event.get_flag('explained_digger'):
        event.clear_ai_messages()
        event.set_flag('explained_digger', True)
        event.show_ai_message(msges['c_digger_1'])
        event.show_ai_message(msges['c_digger_2'])
        event.show_message("Objective: Clear Hostiles")

def enter_area():
    global in_area
    in_area = True

def exit_area():
    global in_area
    in_area = False
    event.close_door(DOOR_BOTTOM)

def point_up():
    if not event.get_flag('from_level') == '2d':
        event.point_at_location(1041, 2048)

def decrement_tank_count():
    n = event.get_flag('tank_count')-1
    event.set_flag('tank_count', n)
    event.clear_messages()
    if n == 1:
        event.show_message("1 Hostile Remaining")
    elif n == 0:
        #event.show_message("Door Opened")
        #event.register_timed_func(point_up, 10)
        event.show_message("Misson 2 Complete")
        event.stop_music()
    else:
        event.show_message(str(n)+" Hostiles Remaining")
    if n == 0:
        event.register_timed_func(win_2, 4)
        return
        for obj_id in DOORS_TOP:
            event.open_door(obj_id)
        event.set_flag('digger_fixed', True)
        event.show_ai_message(msges['c_digger_4'], 1)
        event.show_ai_message(msges['c_digger_5'], head='gw0rp')
        event.show_ai_message(msges['c_digger_6'], 3)
        event.show_ai_message(msges['c_digger_7'], 2.5, head='Terran_1')
        event.show_ai_message(msges['c_digger_8'])
        event.show_ai_message(msges['c_digger_9'])
        event.show_ai_message(msges['c_digger_10'], head='gw0rp')

def plasma_attach():
    event.show_ai_message(msges['c_plasma_1'], 2)
    event.show_ai_message(msges['c_plasma_2'], 2, head='gw0rp')

def other_attach():
    if event.get_flag('gun_attach'): return
    event.set_flag('gun_attach', True)
    event.show_message("Press Escape to change your configuration.")
    event.show_ai_message(msges['c_gun_1'], head='gw0rp')
    event.show_ai_message(msges['c_gun_2'], 2)
    event.show_ai_message(msges['c_gun_3'], head='gw0rp')
    event.show_ai_message(msges['c_gun_4'], 2)

def init():
    global msges
    msges = event.file_to_dict('Messages_2.txt')
    
    event.register_collision_func(DOOR_BOTTOM, show_intro)
    event.register_collision_func(ENTER_TRIGGER, explain_digger)
    event.register_collision_func(BACK_TRIGGER, go_a)
    event.register_collision_func(IN_TRIGGER, go_d)
    event.register_attach_func(PLASMA, plasma_attach)
    
    event.register_collision_func(DIGGER_IN, enter_area)
    for obj_id in DIGGER_OUT:
        event.register_collision_func(obj_id, exit_area)
    
    for obj_id in CARGO:    
        event.register_attach_func(obj_id, cargo_attach)
        event.register_release_func(obj_id, cargo_release)
    
    for obj_id in TURRETS:
        event.register_destroy_func(obj_id, decrement_tank_count)
    for obj_id in WAVE_2:
        event.make_invisible(obj_id)
    
    for obj_id in TURRETS + THRUSTERS:
        event.register_attach_func(obj_id, other_attach)
    
    event.set_flag('countdown_set', False)
    event.set_flag('targets_set', False)
    event.set_flag('cargo_list', [], True)
    event.set_flag('digger_fixed', False)
    event.set_flag('tank_count', len(TURRETS)-len(WAVE_2))

def on_load():
    global msges
    msges = event.file_to_dict('Messages_2.txt')
    if event.get_flag('from_level') == '2a':
        event.move_player_to(1272, 127)
    event.set_flag('from_level', '2c', True)
    
    if event.get_flag('digger_fixed'):
        pos_obj = event.get_object(DIGGER)
        event.point_at_location(pos_obj.x, pos_obj.y)
