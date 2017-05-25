import os, yaml, settings

def repr_for_obj(obj):
    sl = ['%s(']
    vl = [obj.__class__.__name__]
    
    for k, v in obj.__dict__.items():
        sl.append(k + "=%r, ")
        vl.append(v)
    sl[-1] = sl[-1][:-2]
    sl.append(')')
    return_str = ''.join(sl) % tuple(vl)
    return return_str

class EasyYAML(yaml.YAMLObject):
    def __repr__(self):
        return repr_for_obj(self)
    

class YamlLevelData(EasyYAML):
    yaml_tag = u"!i_LevelData"
    def __init__(self, level_dir, level_name):
        self.level_dir = level_dir
        self.level_name = level_name
    

class YamlEventData(EasyYAML):
    yaml_tag = u"!i_EventData"
    def __init__(self, active_countdown, ai_message, ai_message_queue, ai_message_countdown,
                ai_head, attach_funcs, collision_funcs, counting_down, damage_funcs, destroy_funcs, 
                event_time, level_flags, message, message_countdown, 
                message_queue, message_size, music, release_funcs, point_at, 
                shared_flags, timed_funcs
            ):
        self.active_countdown = active_countdown
        self.ai_message = ai_message
        self.ai_message_queue = ai_message_queue
        self.ai_message_countdown = ai_message_countdown
        self.ai_head = ai_head
        self.attach_funcs = attach_funcs
        self.collision_funcs = collision_funcs
        self.counting_down = counting_down
        self.damage_funcs = damage_funcs
        self.destroy_funcs = destroy_funcs
        self.event_time = event_time
        self.level_flags = level_flags
        self.message = message
        self.message_countdown = message_countdown
        self.message_queue = message_queue
        self.message_size = message_size
        self.music = music
        self.point_at = point_at
        self.release_funcs = release_funcs
        self.shared_flags = shared_flags
        self.timed_funcs = timed_funcs
    

class YamlGlueBody(EasyYAML):
    yaml_tag = u"!i_GlueBody"
    def __init__(self, angle, angular_velocity, attachable, is_player, 
                position, units, velocity
            ):
        self.angle = angle
        self.angular_velocity = angular_velocity
        self.attachable = attachable
        self.is_player = is_player
        self.position = position
        self.units = units
        self.velocity = velocity
    

class YamlSingleBody(EasyYAML):
    yaml_tag = u"!i_SingleBody"
    def __init__(self, angle, angular_velocity, attachable, position, unit,
                velocity, visible
            ):
        self.angle = angle
        self.angular_velocity = angular_velocity
        self.attachable = attachable
        self.position = position
        self.unit = unit
        self.velocity = velocity
        self.visible = visible
    

class YamlTurret(EasyYAML):
    yaml_tag = u"!i_Turret"
    def __init__(self, active, alive, angle, base_type, base_rotation,
                health, obj_id, on_target, position, recoil_status, target, 
                targeting, turret_type, visible
            ):
        self.active = active
        self.alive = alive
        self.angle = angle
        self.base_type = base_type
        self.base_rotation = base_rotation
        self.health = health
        self.obj_id = obj_id
        self.on_target = on_target
        self.position = position
        self.recoil_status = recoil_status
        self.target = target
        self.targeting = targeting
        self.turret_type = turret_type
        self.visible = visible
    

class YamlTank(EasyYAML):
    yaml_tag = u"!i_Tank"
    def __init__(
                self, alive, obj_id, position, rotation, target, turn_state, 
                turret, visible
            ):
        self.alive = alive
        self.obj_id = obj_id
        self.position = position
        self.rotation = rotation
        self.target = target
        self.turn_state = turn_state
        self.turret = turret
        self.visible = visible
    

class YamlDoor(EasyYAML):
    yaml_tag = u"!i_Door"
    def __init__(self, a, b, key, obj_id, visible, closed):
        self.a = a
        self.b = b
        self.key = key
        self.obj_id = obj_id
        self.visible = visible
        self.closed = closed
    

class YamlImageDoor(EasyYAML):
    yaml_tag = u"!i_ImageDoor"
    def __init__(self, x, y, rotation, obj_id, key, closed, manual=False):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.obj_id = obj_id
        self.key = key
        self.closed = closed
        self.manual = manual
    

class YamlDecal(EasyYAML):
    yaml_tag = u"!i_Decal"
    def __init__(self, obj_id, name, x, y, rotation, scale, visible, overhead=False):
        self.obj_id = obj_id
        self.name = name
        self.x = x
        self.y = y
        self.rotation = rotation
        self.scale = scale
        self.visible = visible
        self.overhead = overhead
    

class YamlWall(EasyYAML):
    yaml_tag = u"!i_Wall"
    def __init__(self, x, y, rotation, name, obj_id):
        self.obj_id = obj_id
        self.x = x
        self.y = y
        self.rotation = rotation
        self.name = name
    

class YamlRock(EasyYAML):
    yaml_tag = u"!i_Rock"
    def __init__(self, kind, obj_id, position, rotation, visible):
        self.kind = kind
        self.obj_id = obj_id
        self.position = position
        self.rotation = rotation
        self.visible = visible
    

class YamlDecalInvisList(EasyYAML):
    yaml_tag = u"!i_DecalInvisList"
    def __init__(self, invisibles):
        super(YamlDecalInvisList, self).__init__()
        self.invisibles = invisibles
    

def save(level_dir, current_level, obj_list, save_path, yaml_list):
    for obj in obj_list:
        if hasattr(obj, 'get_yaml_object'):
            o = obj.get_yaml_object()
            yaml_list.append(obj.get_yaml_object())
        else:
            print "Ignoring", obj
    stream = file(save_path, 'w')
    yaml.dump(yaml_list, stream)
    stream.close()
