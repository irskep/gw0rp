import time, pyglet, os, math
import level
import gworpplayer
from util import gui, env, music, physics, resources, save
from collections import defaultdict

shared_flags = {}

collision_funcs = defaultdict(list)
release_funcs = defaultdict(list)
attach_funcs = defaultdict(list)
destroy_funcs = defaultdict(list)
damage_funcs = defaultdict(list)

player_units = []
player_unit_ids = [] #list of obj_ids set by body.py
next_level = "" #checked by GworpPlayer
persist_status = False
prefer_saved = False
keep_ship_config = False
keep_ship_velocity = False

event_time = 0.0
level_start_time = 0.0
end_game = False
start_countdown = False
quake_level = 0.0
fade_out_countdown = -100
stay_black = True

message = ""
message_queue = []
message_size = 36
message_countdown = 0.0

ai_message = ""
ai_message_queue = []
ai_message_countdown = 0.0
ai_head = resources.gw0rp

timed_funcs = []
cutscene_queue = []
level_flags = {}

active_countdown = 0.0
counting_down = False

class Point(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
point_object = None
point_at_id = 0

#Housekeeping, initialization
def init():
    global player_unit_ids, next_level, player_units, fade_out_countdown, stay_black
    global level_flags, message, ai_message, message_countdown
    global ai_message_countdown, message_queue, ai_message_queue
    global collision_funcs, release_funcs, attach_funcs, destroy_funcs
    global cutscene_queue, timed_funcs, event_time, damage_funcs
    global end_game, start_countdown, quake_level, point_object
    global keep_ship_config, keep_ship_velocity, active_countdown, level_start_time
    
    fade_out_countdown = -100
    stay_black = False
    
    collision_funcs = defaultdict(list)
    release_funcs = defaultdict(list)
    attach_funcs = defaultdict(list)
    destroy_funcs = defaultdict(list)
    damage_funcs = defaultdict(list)
    
    level_flags = {}
    player_units = []
    player_unit_ids = []
    cutscene_queue = []
    
    next_level = ""
    keep_ship_config = False
    keep_ship_velocity = False
    message = ""
    message_queue = []
    message_countdown = 0
    ai_message = ""
    ai_message_queue = []
    ai_message_countdown = 0
    
    timed_funcs = []
    event_time = 0.0
    end_game = False
    start_countdown = False
    quake_level = 0.0
    point_object = None
    
    level_start_time = event_time

def func_dict_to_strings(func_dict, default=False):
    return_dict = {}
    for k, v in func_dict.items():
        return_dict[k] = [f.__name__ for f in v]
    return return_dict

def string_dict_to_funcs(string_dict, func_source, default=False):
    if default:
        return_dict = defaultdict(list)
    else:
        return_dict = {}
    for k, v in string_dict.items():
        return_dict[k] = [getattr(func_source, f) for f in v]
    return return_dict

def collision_funcs_as_strings():
    return func_dict_to_strings(collision_funcs)

def collision_funcs_from_strings(sd, fs):
    return string_dict_to_funcs(sd, fs, True)

def release_funcs_as_strings():
    return func_dict_to_strings(release_funcs)

def release_funcs_from_strings(sd, fs):
    return string_dict_to_funcs(sd, fs, True)

def attach_funcs_as_strings():
    return func_dict_to_strings(attach_funcs)

def attach_funcs_from_strings(sd, fs):
    return string_dict_to_funcs(sd, fs, True)

def destroy_funcs_as_strings():
    return func_dict_to_strings(destroy_funcs)

def destroy_funcs_from_strings(sd, fs):
    return string_dict_to_funcs(sd, fs, True)

def damage_funcs_as_strings():
    return func_dict_to_strings(damage_funcs)

def damage_funcs_from_strings(sd, fs):
    return string_dict_to_funcs(sd, fs, True)

def timed_funcs_as_strings():
    return [(d, f.__name__) for d, f in timed_funcs]

def timed_funcs_from_strings(str_lst, func_source):
    return [(d, getattr(func_source, f)) for d, f in str_lst]

def ai_message_queue_as_strings():
    return [(m, d, i.instance_name) for m, d, i in ai_message_queue]

def ai_message_queue_from_strings(q):
    return [(m, d, getattr(resources, i)) for m, d, i in q]

def load_from_yaml_obj(obj, func_source):
    global ai_head, ai_message, ai_message_countdown, ai_message_queue
    global attach_funcs, collision_funcs, destroy_funcs, release_funcs, damage_funcs
    global event_time, level_flags, timed_funcs, point_at_id, point_object
    global message, message_countdown, message_queue, message_size
    global active_countdown, shared_flags, persist_status
    
    ai_head = getattr(resources, obj.ai_head)
    ai_message = obj.ai_message
    ai_message_countdown = obj.ai_message_countdown
    ai_message_queue = ai_message_queue_from_strings(obj.ai_message_queue)
    
    attach_funcs = attach_funcs_from_strings(obj.attach_funcs, func_source)
    collision_funcs = collision_funcs_from_strings(obj.collision_funcs, func_source)
    destroy_funcs = destroy_funcs_from_strings(obj.destroy_funcs, func_source)
    release_funcs = release_funcs_from_strings(obj.release_funcs, func_source)
    damage_funcs = damage_funcs_from_strings(obj.damage_funcs, func_source)
    timed_funcs = timed_funcs_from_strings(obj.timed_funcs, func_source)
    
    event_time = obj.event_time
    level_flags = obj.level_flags
    if not persist_status:
        shared_flags = obj.shared_flags
        active_countdown = obj.active_countdown
    else:
        persist_status = False
    
    message = obj.message
    message_countdown = obj.message_countdown
    message_queue = obj.message_queue
    message_size = obj.message_size
    
    point_at_id = obj.point_at
    point_object = None
    
    if not hasattr(obj, 'music'):
        obj.music = None
    if obj.music != None and not music.playing():
        music.new_song(getattr(obj, 'music'))

def update(dt=0):
    global message, message_queue, message_countdown, message_size
    global ai_message, ai_message_queue, ai_message_countdown, ai_head
    global event_time, timed_funcs, quake_level, point_object, point_at_id
    global active_countdown, counting_down, fade_out_countdown, stay_black
    
    if counting_down and active_countdown > 0.0:
        active_countdown -= dt
        if active_countdown <= 0.0:
            counting_down = False
            active_countdown = 0.0
    
    if fade_out_countdown != -100:
        fade_out_countdown += dt
        if fade_out_countdown >= 1.0:
            fade_out_countdown = -100
            stay_black = True
    
    if point_at_id != 0:
        point_at(point_at_id)
        point_at_id = 0
    
    if message_countdown > 0:
        message_countdown -= dt
    if ai_message_countdown > 0:
        ai_message_countdown -= dt
    if quake_level > 0:
        quake_level -= dt
    event_time += dt
    
    if len(timed_funcs) > 0:
        call_queue = []
        i = 0
        while i < len(timed_funcs) and timed_funcs[i][0] <= event_time:
            call_queue.append(timed_funcs[i])
            i += 1
        for tup in call_queue:
            tup[1]()
            timed_funcs.remove(tup)
    
    if message_countdown <= 0 and len(message_queue) > 0:
        message = message_queue[0][0]
        message_countdown = message_queue[0][1]
        message_size = message_queue[0][2]
        message_queue = message_queue[1:]
    if ai_message_countdown <= 0 and len(ai_message_queue) > 0:
        ai_message = ai_message_queue[0][0]
        ai_message_countdown = ai_message_queue[0][1]
        ai_head = ai_message_queue[0][2]
        ai_message_queue = ai_message_queue[1:]

def reset_countdown():
    global message_countdown, ai_message_countdown
    message_countdown = 0
    ai_message_countdown = 0

def update_player_units(raw_units):
    global player_unit_ids, player_units
    player_units = raw_units
    player_unit_ids = [unit.obj_id for unit in raw_units]

def register_collision_func(obj_id, func):
    global collision_funcs
    collision_funcs[obj_id].append(func)

def register_attach_func(obj_id, func):
    global attach_funcs
    attach_funcs[obj_id].append(func)

def register_release_func(obj_id, func):
    global release_funcs
    release_funcs[obj_id].append(func)

def register_destroy_func(obj_id, func):
    global destroy_funcs
    destroy_funcs[obj_id].append(func)

def register_damage_func(obj_id, func):
    global damage_funcs
    damage_funcs[obj_id].append(func)

def register_timed_func(func, delay):
    global timed_funcs
    delay += event_time
    timed_funcs.append((delay, func))
    timed_funcs = sorted(timed_funcs)

#Accessors for level scripts
def player_has_unit(obj_id):
    return (obj_id in player_unit_ids)

def get_object(obj_id, search_units=True, search_bodies=True, search_decals=True):
    if search_units:
        for unit in physics.unit_update_list:
            if unit.obj_id == obj_id: return unit
    if search_bodies:
        for body in physics.body_update_list:
            if hasattr(body, 'obj_id'):
                if body.obj_id == obj_id: return body
    if search_decals:
        for decal in level.decals:
            if decal.obj_id == obj_id: return decal
    return None

def file_to_dict(name):
    f=open(os.path.join(level.level_dir, name))
    m_dict = {}
    for line in f:
        if line.find(':') != -1:
            p, m = [s.strip() for s in line.split(":")]
            m_dict[p] = m
    f.close()
    return m_dict

#Commands for level scripts
def go_to_level(name, use_saved=False, keep_config=False, keep_veloctiy=False):
    global next_level, keep_ship_config, keep_ship_velocity, prefer_saved, persist_status
    global level_start_time
    if event_time-level_start_time < 3:
        return
    next_level = name
    prefer_saved = use_saved
    keep_ship_config = keep_config
    keep_ship_velocity = keep_veloctiy
    persist_status = True
    level_start_time = event_time

def start_music(music_name):
    music.new_song(music_name)

def pause_music():
    music.pause()

def stop_music():
    music.stop()

def music_playing():
    return music.playing()

def clear_image_cache():
    for k, v in resources.lazies.items():
        del v
    resources.lazies = {}

def show_message(msg, duration = 4.0, size = 36):
    message_queue.append((msg, duration, size))

def show_ai_message(msg, duration = 5.0, head='vn4n'):
    ai_message_queue.append((msg, duration, getattr(resources, head)))

def make_invisible(obj_id):
    obj = None
    for decal in level.decals:
        if decal.obj_id == obj_id: obj = decal
    for body in physics.body_update_list:
        if hasattr(body, 'obj_id'):
            if body.obj_id == obj_id: obj = body
    if hasattr(obj, 'make_invisible'):
        obj.make_invisible()
    else:
        print 'failed to make invisible:', obj

def make_visible(obj_id):
    obj = None
    for decal in level.decals:
        if decal.obj_id == obj_id: obj = decal
    for body in physics.body_update_list:
        if hasattr(body, 'obj_id'):
            if body.obj_id == obj_id: obj = body
    if hasattr(obj, 'make_visible'):
        obj.make_visible()
    else:
        print 'failed to make visible:', obj, obj_id

def set_target(obj_id_src, obj_id_target):
    obj = get_object(obj_id_src)
    target = get_object(obj_id_target)
    for obj in physics.body_update_list:
        if hasattr(obj, 'obj_id'):
            if obj.obj_id == obj_id_src and hasattr(obj, 'target'):
                obj.target = target

def close_door(obj_id):
    for body in physics.body_update_list:
        if hasattr(body, 'obj_id'):
            if body.obj_id == obj_id and hasattr(body, 'close'):
                body.manual = True
                body.close()

def open_door(obj_id):
    for body in physics.body_update_list:
        if hasattr(body, 'obj_id'):
            if body.obj_id == obj_id and hasattr(body, 'open'):
                body.manual = True
                body.open()

def set_flag(k, v, shared=False):
    if k in shared_flags: shared = True
    if shared:
        shared_flags[k] = v
        return
    level_flags[k] = v

def get_flag(k):
    if k in level_flags: return level_flags[k]
    if k in shared_flags: return shared_flags[k]
    return None

def show_cutscene(name):
    cutscene_queue.append(name)

def clear_ai_messages():
    global ai_message_queue, ai_message, ai_message_countdown
    ai_message_queue = []
    ai_message = ""
    ai_message_countdown = 0.0

def clear_messages():
    global message_queue, message, message_countdown
    message_queue = []
    message = ""
    message_countdown = 0.0

def point_at(obj_id):
    global point_object
    if obj_id == 0: 
        point_object = None
        return
    point_object = get_object(obj_id)

def point_at_location(x, y):
    global point_object
    point_object = Point(x, y)

def rotate_player_velocity(new_angle):
    magnitude = math.sqrt(
        level.player.body.velocity.x**2 + level.player.body.velocity.y**2
    )
    ax = math.cos(new_angle)
    ay = math.sin(new_angle)
    level.player.body.velocity.x = ax*magnitude
    level.player.body.velocity.y = ay*magnitude
    level.player.body.angle = new_angle

def stop_player():
    level.player.body.velocity.x = 0
    level.player.body.velocity.y = 0

def move_player(dx, dy):
    level.player.body.position.x += dx
    level.player.body.position.y += dy

def move_player_to(x, y):
    level.player.body.position.x = x
    level.player.body.position.y = y

def move_player_back():
    level.player.body.position.x -= level.player.body.velocity.x*0.06
    level.player.body.position.y -= level.player.body.velocity.y*0.06

def move_player_to_object(obj_id):
    dest = get_object(obj_id)
    if hasattr(dest, 'body'):
        dest = dest.body.position
    level.player.body.position.x = dest.x
    level.player.body.position.y = dest.y

def set_player_rotation(r):
    level.player.body.angle = -math.radians(r)

def set_player_angle(a):
    level.player.body.angle = a

def autosave():
    level.save()

def save_as(dest):
    save.save_to(dest)

def trigger_fail():
    global end_game, start_countdown
    end_game = True
    start_countdown = True

def quake(ql = 1.0):
    global quake_level
    quake_level = ql

def set_countdown(n):
    global active_countdown, counting_down
    active_countdown = n
    counting_down = True

def pause_countdown():
    global counting_down
    counting_down = False

def resume_countdown():
    global counting_down
    counting_down = True

def win():
    global next_level, fade_out_countdown
    if next_level == 'win': return
    stop_music()
    show_cutscene('win')
    next_level = 'win'
    fade_out_countdown = 0
