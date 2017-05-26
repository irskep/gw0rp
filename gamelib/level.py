import os, sys, operator, math
from collections import defaultdict
import pyglet, pymunk
from util import draw, env, gui, resources, music, sound
from util import physics, serialize, settings, widget
from util import save as savegame
import unit, body, bullet, enemy, obstacle, event
import yaml
from pyglet.window import key
from yamlobjects import *
from util.serialize import *

width = 50*40
height = 50*40
player_start_x = 100
player_start_y = 100
player_start_angle = 1.57
player_config = 'normal'
prim_color = (0,0,0,1)
batch = None
floor_group = None
decal_group = None
tank_group = None
bullet_group = None
unit_group = None
door_group = None
overlay_group = None
decals = []

background_image = None
background_cache = {}
background_tiled = False
background_scale = 1.0

big_backgrounds = [
    'level_2e',
    'level_2f',
    'level_3f',
    'level_5'
]

current_level = ""
level_dir = ""
entry_point = ""
entry_points = []

restart_countdown = -1

player = None
decoy_present = False
decoy_x = 0
decoy_y = 0
mass = 0
power = 0
logic = 0
power_per_unit = 0

music_player = None

root_1 = os.path.join('Data','Levels')
root_2 = os.path.join(settings.settings_dir,'Levels')

class Decal(pyglet.sprite.Sprite):
    def __init__(self, img, x, y, rot, obj_id=0, scale=1.0, overhead=False):
        if overhead:
            gp = overlay_group
        else:
            gp = decal_group
        super(Decal, self).__init__(
            img, x, y, batch=batch, group=gp
        )
        if abs(rot) < 5: rot = 0
        self.rotation = rot
        self.scale = scale
        self.obj_id = obj_id
        self.overhead = overhead
        decals.append(self)
    
    def get_yaml_object(self):
        return YamlDecal(
            obj_id = self.obj_id,
            name=self.image.instance_name,
            x=self.x,
            y=self.y, 
            rotation=self.rotation,
            scale=self.scale,
            visible=self.visible,
            overhead=self.overhead
        )
    
    def make_invisible(self):
        self.visible = False
    
    def make_visible(self):
        self.visible = True

def init_player(x, y, angle, config='normal'):
    global player
    if config == 'enhanced_1' or config == 'enhanced_3':
        ot = (10, 48)
        rt = 15
    elif config == 'enhanced_2':
        ot = (10, 48)
        rt = 45
    else:
        ot = (15, 45)
        rt = 0
    thruster_left_bottom = unit.Thruster(None, (-32,33), -rt, obj_id=-5)
    thruster_right_bottom = unit.Thruster(None, (-32,-33), rt, obj_id=-4)
    thruster_left_top = unit.Thruster(None, (ot[0], ot[1]), 180, obj_id=-3)
    thruster_right_top = unit.Thruster(None, (ot[0], -ot[1]), 180, obj_id=-2)
    
    if config == 'enhanced_3':
        brain = unit.Brain2(None, (0,0), 90, obj_id=-1)
    else:
        brain = unit.Brain(None, (0,0), 0, obj_id=-1)
    
    new_shapes = [brain, thruster_left_bottom, thruster_right_bottom,
                thruster_left_top, thruster_right_top]
    
    if config == 'enhanced_1' or config == 'enhanced_3':
        repair = unit.Repair(None, (40, 0), 0, obj_id=-6)
        gun_left = unit.BlueTurret(None, (55, 30), 10, obj_id=-7)
        gun_right = unit.BlueTurret(None, (55, -30), -10, obj_id=-8)
        new_shapes.extend([repair, gun_left, gun_right])
        env.bind_keys([key.SPACE], gun_left)
        env.bind_keys([key.SPACE], gun_right)
    if config == 'enhanced_2':
        repair = unit.Repair(None, (40, 0), 0, obj_id=-6)
        gun_left = unit.BlueTurret(None, (55, 30), 10, obj_id=-7)
        gun_right = unit.BlueTurret(None, (55, -30), -10, obj_id=-8)
        thruster_left_out = unit.Thruster(None, (-27,81), -20, obj_id=-9)
        thruster_right_out = unit.Thruster(None, (-27,-81), 20, obj_id=-10)
        new_shapes.extend([repair, thruster_right_out, thruster_left_out, gun_left, gun_right])
        env.bind_keys([key.SPACE], gun_left)
        env.bind_keys([key.SPACE], gun_right)
        env.bind_keys([key.RIGHT, key.UP], thruster_left_out)
        env.bind_keys([key.LEFT, key.UP], thruster_right_out)
    
    env.bind_keys([key.RIGHT, key.UP], thruster_left_bottom)
    env.bind_keys([key.LEFT, key.UP], thruster_right_bottom)
    env.bind_keys([key.LEFT, key.DOWN], thruster_left_top)
    env.bind_keys([key.RIGHT, key.DOWN], thruster_right_top)
    
    player = body.GlueBody((x, y), angle, new_shapes)

def add_wall(x1, y1, x2, y2, obj_id=0, visible=True, collides=True, color=None):
    if color == None: color = prim_color
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    new_seg = pymunk.Segment(physics.static_body, (x1, y1), (x2, y2), 1)
    new_seg.obj_id = obj_id
    new_seg.elasticity = physics.default_elasticity
    vertex_list = None
    if collides:
        new_seg.collision_type = physics.WALL
    else:    
        new_seg.collision_type = physics.INVISIBLE
    if visible:
        vertex_list = batch.add(2, pyglet.gl.GL_LINES, floor_group,
            ('v2i', (x1, y1, x2, y2)), ('c4f', color*2))
    else:
        new_seg.elasticity = physics.default_elasticity
    physics.space.add_static([new_seg])

def add_circle(x, y, radius, obj_id=0, visible=True, collides=True, color=None):
    if color == None: color = prim_color
    new_circ = pymunk.Circle(physics.static_body, radius, (x, y))
    new_circ.obj_id = obj_id
    new_circ.elasticity = physics.default_elasticity
    if collides:
        new_circ.collision_type = physics.WALL
    else:    
        new_circ.collision_type = physics.INVISIBLE
    if visible:
        segs = draw._concat(
                        draw._iter_ellipse(x-radius,y-radius,x+radius,y+radius))
        numpoints = len(segs)/2
        vertex_list = batch.add(
                numpoints, pyglet.gl.GL_LINE_LOOP, floor_group,
                ('v2f', segs), ('c4f', color*numpoints))
    physics.space.add_static([new_circ])

def add_rect(x1, y1, x2, y2, obj_id=0, color=None):
    if color == None: color = prim_color
    x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
    add_wall(x1, y1, x2, y1, obj_id, color=color)
    add_wall(x2, y1, x2, y2, obj_id, color=color)
    add_wall(x2, y2, x1, y2, obj_id, color=color)
    add_wall(x1, y2, x1, y1, obj_id, color=color)
    vertex_list = batch.add(
        4, pyglet.gl.GL_QUADS, floor_group,
        ('v2f', (x1, y1, x2, y1, x2, y2, x1, y2)), ('c4f', color*4))

def add_triangle(x1, y1, x2, y2, x3, y3, obj_id=0, color=None):
    if color == None: color = prim_color
    x1, y1 = int(x1), int(y1)
    x2, y2 = int(x2), int(y2)
    x3, y3 = int(x3), int(y3)
    add_wall(x1, y1, x2, y2, obj_id, color=color)
    add_wall(x2, y2, x3, y3, obj_id, color=color)
    add_wall(x3, y3, x1, y1, obj_id, color=color)
    vertex_list = batch.add(
        3, pyglet.gl.GL_TRIANGLES, floor_group,
        ('v2f', (x1, y1, x2, y2, x3, y3)), ('c4f', color*3))

def add_free_object(Class, x, y, rot, obj_id=0):
    free_unit = Class(obj_id=obj_id)
    free_body = body.SingleBody((x, y), rot, free_unit)
    return free_unit

def get_background(name):
    global background_tiled, background_scale
    background_tiled = False
    #HACKY HAX
    new_bg = getattr(resources, name)()
    if name in big_backgrounds:
        background_scale = 2.0
    else:
        background_scale = 1.0
    #END HACKY HAX
    if width <= new_bg.width and height <= new_bg.height or name in big_backgrounds:
        return new_bg
    background_tiled = True
    if name not in background_cache:
        background_cache[name] = pyglet.image.TileableTexture.create_for_image(
            new_bg
        )
    return background_cache[name]

def load_yaml_objects(yaml_objects):
    global player_start_x, player_start_y, player_start_angle, player_config
    free_object_table = {
        u"!FreeThruster": unit.Thruster,
        u"!FreeDecoy": unit.Decoy,
        u"!FreeShield": unit.Shield,
        u"!FreeRepair": unit.Repair,
        u"!FreeBeacon": unit.Beacon,
        u"!FreeToxin": unit.Toxin,
        u"!FreeGworpBrain": unit.GworpBrain,
        u"!FreeBomb": unit.Bomb,
        u"!FreeTurret": unit.BlueTurret,
        u"!FreeCargo": unit.Cargo
    }
    
    turret_table = {
        u"!EnemyTurret": enemy.BluePlasmaTurret,
        u"!PlasmaTurret1": enemy.BluePlasmaTurret,
        u"!PlasmaTurret2": enemy.FixedRapidTurret2,
        u"!RapidTurret1": enemy.FixedRapidTurret,
        u"!CannonTurret1": enemy.CannonTurret
    }
    
    turret_base_table = {
        'Scaffold': resources.turret_base,
        'MetalTower': resources.Tower1_Static,
        'ConcreteTower': resources.Tower2_Static,
        '': resources.turret_base
    }
    
    tank_turret_table = {
        u"!Tank1": enemy.FixedRapidTurret,
        u"!Tank2": enemy.CannonTurret,
    }
    for obj in yaml_objects:
        if obj.yaml_tag == u"!Env":
            player_start_x, player_start_y = obj.player_x, obj.player_y
            if not hasattr(obj, 'player_angle'):
                obj.player_angle = 1.57
            player_start_angle = obj.player_angle
            if not hasattr(obj, 'player_config'):
                obj.player_config = 'normal'
            player_config = obj.player_config
        elif obj.yaml_tag == u"!Door":
            new_door = obstacle.Door(
                obj.x1, obj.y1, obj.x2, obj.y2, 
                obj.obj_id, obj.key, obj.visible
            )
        elif obj.yaml_tag == u"!ImageDoor":
            new_door = obstacle.ImageDoor(
                obj.x, obj.y, obj.rotation, obj.obj_id, obj.key
            )
        elif obj.yaml_tag == u"!Key":
            free_unit = unit.Key(
                number=obj.number, obj_id=obj.obj_id
            )
            free_body = body.SingleBody((obj.x, obj.y), 0, free_unit)
        elif obj.yaml_tag == u"!Rock":
            new_rock = obstacle.StationaryRock(
                obj.x, obj.y, obj.rotation, obj.rock_type, obj.obj_id
            )
        elif obj.yaml_tag == u"!Decal":
            if not hasattr(obj, 'overhead'): obj.overhead = False
            new_decal = Decal(
                getattr(resources, obj.img_name), obj.x, obj.y, 
                obj.rotation, obj.obj_id, obj.scale, obj.overhead
            )
        elif obj.yaml_tag in free_object_table.keys():
            add_free_object(
                free_object_table[obj.yaml_tag], 
                obj.x, obj.y, obj.rotation, obj.obj_id
            )
        elif obj.yaml_tag == u"!DestructibleWall":
            new_door = obstacle.DestructibleWall(
                obj.x, obj.y, obj.rotation, obj.img_name, obj.obj_id
            )
        elif obj.yaml_tag in turret_table.keys():
            if not hasattr(obj, 'base_type'):
                obj.base_type = 'Scaffold'
                obj.base_rotation = 0.0
            if obj.base_type == 'Tank':
                new_turret = turret_table[obj.yaml_tag](
                    obj.x, obj.y, obj.rotation, obj.obj_id, base_img=None
                )
                new_tank = enemy.Tank(
                    obj.x, obj.y, obj.rotation, obj.obj_id, new_turret
                )
            else:
                new_static_object = turret_table[obj.yaml_tag](
                    obj.x, obj.y, obj.rotation, obj.obj_id,
                    turret_base_table[obj.base_type], obj.base_rotation
                )
        elif obj.yaml_tag in tank_turret_table.keys():
            new_turret = tank_turret_table[obj.yaml_tag](
                obj.x, obj.y, obj.rotation, obj.obj_id, base_img=None
            )
            new_tank = enemy.Tank(
                obj.x, obj.y, obj.rotation, obj.obj_id, new_turret
            )

def load_geometry(yaml_objects):
    global width, height, decals
    global background_image, prim_color
    decals = []
    
    for obj in yaml_objects:
        if obj.yaml_tag == u"!Line":
            c = True
            if hasattr(obj, 'collides'):
                c = obj.collides
            add_wall(
                obj.x1, obj.y1, obj.x2, obj.y2, obj.obj_id, obj.visible, c
            )
        elif obj.yaml_tag == u"!Circle":
            c = True
            if hasattr(obj, 'collides'):
                c = obj.collides
            add_circle(
                obj.x, obj.y, obj.radius, obj.obj_id, obj.visible, c
            )
        elif obj.yaml_tag == u"!FilledRect":
            add_rect(
                obj.x1, obj.y1, obj.x2, obj.y2, obj.obj_id
            )
        elif obj.yaml_tag == u"!FilledTriangle":
            add_triangle(
                obj.x1, obj.y1, obj.x2, obj.y2, obj.x3, obj.y3, obj.obj_id
            )
        elif obj.yaml_tag == u"!Env":
            width, height = obj.width, obj.height
            prim_color = tuple([c/255.0 for c in obj.prim_color])
            background_image = get_background(obj.background_image)
    
    add_wall(0, 0, width, 0)
    add_wall(width, 0, width, height)
    add_wall(width, height, 0, height)
    add_wall(0, height, 0, 0)

def change_entry_point(new_level_dir, new_entry_point):
    global level_dir, entry_point
    if level_dir != "":
        sys.path.remove(level_dir)
    sys.path.append(new_level_dir)
    level_dir = new_level_dir
    entry_point = new_entry_point

def change_level_set(set_name):
    global level_dir
    set_name = os.path.split(set_name)[-1]
    for info in entry_points:
        if os.path.split(info['Path'])[-1] == set_name:
            if level_dir != "":
                sys.path.remove(level_dir)
            sys.path.append(info['Path'])
            level_dir = info['Path']

def reset():
    global batch, bullet_group, floor_group,  unit_group, decal_group
    global tank_group, restart_countdown, door_group, overlay_group
    
    restart_countdown = -1
    batch = pyglet.graphics.Batch()
    floor_group = pyglet.graphics.OrderedGroup(0)
    decal_group = pyglet.graphics.OrderedGroup(1)
    tank_group = pyglet.graphics.OrderedGroup(2)
    unit_group = pyglet.graphics.OrderedGroup(3)
    door_group = pyglet.graphics.OrderedGroup(4)
    bullet_group = pyglet.graphics.OrderedGroup(5)
    overlay_group = pyglet.graphics.OrderedGroup(6)

def load(level_name, keep_config=False, keep_velocity=False):
    global current_level, player
    reset()
    current_level = level_name
    
    path = os.path.join(level_dir, level_name+".yaml")
    stream = file(path, 'r')
    yaml_objects = yaml.load(stream)
    stream.close()
    
    load_geometry(yaml_objects)
    load_yaml_objects(yaml_objects)
    
    add_wall(0, 0, width, 0)
    add_wall(width, 0, width, height)
    add_wall(width, height, 0, height)
    add_wall(0, height, 0, 0)
    
    #physics.space.resize_static_hash()
    #physics.space.resize_active_hash()
    if not keep_config:
        init_player(player_start_x, player_start_y, math.pi/2, player_config)
        player.body.angle = player_start_angle
    else:
        player.body.position.x = player_start_x
        player.body.position.y = player_start_y
        if not keep_velocity:
            player.body.velocity.x = 0.0
            player.body.velocity.y = 0.0
        physics.body_update_list.append(player)
        physics.unit_update_list.extend(player.units)
        physics.space.add(player.body)
        for unit in player.units:
            if hasattr(unit, 'update_patients_now'):
                unit.update_patients_now = True
            unit.add_shapes()
            unit.batch = None
            unit.batch = batch
            unit.migrate()
    resources.wall_sound = resources.metal_against_metal2        
    event.update_player_units(player.units)
    level_module = __import__(level_name)
    if hasattr(level_module, 'init'): level_module.init()

def unit_from_dict(unit_dict):
    unit_table = {
        "Brain": unit.Brain,
        "Brain2": unit.Brain2,
        "GworpBrain": unit.GworpBrain,
        "Toxin": unit.Toxin,
        "Thruster": unit.Thruster,
        "Decoy": unit.Decoy,
        "Shield": unit.Shield,
        "Repair": unit.Repair,
        "Beacon": unit.Beacon,
        "Bomb": unit.Bomb,
        "RapidTurret": unit.RapidTurret,
        "RapidTurret2": unit.RapidTurret2,
        "BlueTurret": unit.BlueTurret,
        "CannonTurret": unit.CannonTurret,
        "Cargo": unit.Cargo
    }
    if unit_dict['ClassName'] == 'Key':
        new_unit = unit.Key(
            number=unit_dict['number'], obj_id=unit_dict['obj_id'],
            load_from=unit_dict
        )
    elif unit_dict['ClassName'] in unit_table:
        new_unit = unit_table[unit_dict['ClassName']](load_from=unit_dict)
    else:
        print "Did not load", unit_dict['ClassName']
        return None
    env.bind_keys(unit_dict['key_bindings'], new_unit)
    return new_unit

def make_turret(obj, on_tank=False):
    if obj == None: return None
    turret_class = None
    turret_dict = {
        "Blue Plasma": enemy.BluePlasmaTurret,
        "Orange Plasma": enemy.OrangePlasmaTurret,
        "Fixed Rapid": enemy.FixedRapidTurret,
        "Fixed Rapid 2": enemy.FixedRapidTurret2,
        "Cannon": enemy.CannonTurret
    }
    if obj.turret_type in turret_dict.keys():
        turret_class = turret_dict[obj.turret_type]
        if on_tank:
            base_img = None
            base_rotation = 0.0
        else:
            base_img = getattr(resources, obj.base_type)
            base_rotation = obj.base_rotation
        new_turret = turret_class(
            obj.position[0], obj.position[1], 
            math.degrees(obj.angle), obj.obj_id, base_img, base_rotation
        )
        new_turret.alive = obj.alive
        new_turret.health = obj.health
        new_turret.on_target = obj.on_target
        new_turret.recoil_status = obj.recoil_status
        new_turret.targeting = obj.targeting
        return new_turret
    return None

def load_save_from_path(path, keep_config=False, keep_velocity=False):
    global player, current_level
    reset()
    event.init()
    stream = file(path, 'r')
    yaml_objects = [obj for obj in yaml.load(stream) if obj != None]
    stream.close()
    
    level_module = None
    
    target_queue = []
    
    if player != None:
        for unit in player.units:
            unit.batch = None
    
    for obj in yaml_objects:
        if obj.yaml_tag == u"!i_LevelData":
            change_level_set(obj.level_dir)
            current_level = obj.level_name
            savegame.set_current_level(obj.level_dir, current_level)
            level_module = __import__(current_level)
            path = os.path.join(level_dir, obj.level_name+".yaml")
            stream = file(path, 'r')
            yaml_geometry = yaml.load(stream)
            stream.close()
            load_geometry(yaml_geometry)
        elif obj.yaml_tag == u"!i_EventData":
            event.load_from_yaml_obj(obj, level_module)
        elif obj.yaml_tag == u"!i_DecalInvisList":
            for d in decals:
                if d.obj_id in obj.invisibles:
                    d.make_invisible()
        elif obj.yaml_tag == u"!i_Decal":
            if not hasattr(obj, 'overhead'): obj.overhead = False
            new_decal = Decal(
                getattr(resources, obj.name), obj.x, obj.y, 
                obj.rotation, obj.obj_id, obj.scale, obj.overhead
            )
            if not obj.visible: new_decal.make_invisible()
        elif obj.yaml_tag == u"!i_Door":
            new_door = obstacle.Door(
                obj.a[0], obj.a[1], obj.b[0], obj.b[1], 
                obj.obj_id, obj.key, obj.visible
            )
            if not obj.closed:
                new_door.open(True)
        elif obj.yaml_tag == u"!i_ImageDoor":
            new_door = obstacle.ImageDoor(
                obj.x, obj.y, obj.rotation, obj.obj_id, obj.key, obj.closed, obj.manual
            )
        elif obj.yaml_tag == u"!i_Wall":
            new_wall = obstacle.DestructibleWall(
                obj.x, obj.y, obj.rotation, obj.name, obj.obj_id
            )
        elif obj.yaml_tag == u"!i_Rock":
            new_rock = obstacle.StationaryRock(
                obj.position[0], obj.position[1], obj.rotation,
                obj.kind, obj.obj_id
            )
            if not obj.visible: new_rock.make_invisible()
        elif obj.yaml_tag == u"!i_SingleBody":
            free_unit = unit_from_dict(obj.unit)
            if free_unit != None:
                free_body = body.SingleBody(
                    obj.position, math.degrees(obj.angle), free_unit
                )
                free_body.attachable = obj.attachable
                free_body.body.velocity = obj.velocity
                free_body.body.angular_velocity = obj.angular_velocity
                if not obj.visible:
                    free_body.make_invisible()
        elif obj.yaml_tag == u"!i_GlueBody":
            if not obj.is_player or not keep_config:
                unit_list = [unit_from_dict(u) for u in obj.units]
                new_gluebody = body.GlueBody(
                    obj.position, obj.angle, unit_list
                )
                new_gluebody.attachable = obj.attachable
                new_gluebody.body.velocity = obj.velocity
                new_gluebody.body.angular_velocity = obj.angular_velocity
                if obj.is_player:
                    player = new_gluebody
                for unit in unit_list:
                    if hasattr(unit, 'update_patients_now'):
                        unit.update_patients_now = True
                    
            if obj.is_player and keep_config:
                player.body.position = obj.position
                if not keep_velocity:
                    player.body.velocity.x = 0.0
                    player.body.velocity.y = 0.0
                physics.body_update_list.append(player)
                physics.unit_update_list.extend(player.units)
                physics.space.add(player.body)
                for unit in player.units:
                    unit.add_shapes()
                    unit.batch = batch
                    unit.migrate()
                    if unit.using_sound: unit.init_sound(unit.sound, unit.loop_sound)
            
        elif obj.yaml_tag == u"!i_Turret":
            new_turret = make_turret(obj, on_tank=False)
            new_turret.active = obj.active
            target_queue.append((new_turret, obj.target))
            if not obj.visible: new_turret.make_invisible()
        elif obj.yaml_tag == u"!i_Tank":
            if obj.turret != None:
                new_turret = make_turret(obj.turret, on_tank=True)
                new_turret.active = obj.turret.active
                target_queue.append((new_turret, obj.turret.target))
            new_tank = enemy.Tank(
                obj.position[0], obj.position[1], obj.rotation, 
                obj.obj_id, new_turret
            )
            target_queue.append((new_tank, obj.target))
            if not obj.visible: new_tank.make_invisible()
        else:
            print "Did not load", obj
    
    for obj, target in target_queue:
        if target > 0:
            obj.target = event.get_object(target)
    event.update_player_units(player.units)
    resources.wall_sound = resources.metal_against_metal2
    if hasattr(level_module, 'on_load'):
        level_module.on_load()

def load_save(name, keep_config=False, keep_velocity=False):
    new_set, path = savegame.load_from(name)
    change_level_set(new_set)
    load_save_from_path(path, keep_config, keep_velocity)

def save(dest = ""):
    if event.end_game: return
    level_set = os.path.split(level_dir)[-1]
    save_path = os.path.join(savegame.save_path, current_level+".yaml")
    savegame.set_current_level(level_set, current_level)
    try:
        po = event.point_object.obj_id
    except:
        po = 0
    decal_obj = YamlDecalInvisList(
        [d.obj_id for d in decals if not d.visible]
    )
    event_obj = YamlEventData(
        active_countdown=event.active_countdown,
        ai_message=event.ai_message,
        ai_message_queue=event.ai_message_queue_as_strings(),
        ai_message_countdown=event.ai_message_countdown,
        ai_head=event.ai_head.instance_name,
        attach_funcs=event.attach_funcs_as_strings(),
        collision_funcs=event.collision_funcs_as_strings(),
        counting_down = event.counting_down,
        damage_funcs=event.damage_funcs_as_strings(),
        destroy_funcs=event.destroy_funcs_as_strings(),
        event_time=event.event_time,
        level_flags=event.level_flags,
        message=event.message,
        message_countdown=event.message_countdown,
        message_queue=event.message_queue,
        message_size=event.message_size,
        music=music.current_track(),
        release_funcs=event.release_funcs_as_strings(),
        point_at=po,
        shared_flags=event.shared_flags,
        timed_funcs=event.timed_funcs_as_strings()
    )
    save_list = physics.body_update_list + decals
    level_obj = YamlLevelData(level_dir, current_level)
    yaml_list = [level_obj, event_obj]
    serialize.save(
        level_dir, current_level, save_list, save_path, yaml_list
    )
    if dest != "":
        savegame.save_to(dest)

def init_entry_points():
    global entry_points
    if not os.path.exists(settings.settings_dir):
        os.makedirs(settings.settings_dir)
    level_sets = [
        f for f in os.listdir(root_1) 
        if os.path.isdir(os.path.join(root_1, f))
    ]
    if not os.path.exists(root_2):
        os.mkdir(root_2)
    level_sets_2 = [
        f for f in os.listdir(root_2) 
        if os.path.isdir(os.path.join(root_2, f))
    ]
    level_sets.extend(level_sets_2)
    for level_set in level_sets:
        info_dict = {'Name': level_set}
        level_path = os.path.join(root_1, level_set)
        if not os.path.exists(os.path.join(level_path, 'Info.txt')):
            level_path = os.path.join(root_2, level_set)
        if os.path.exists(os.path.join(level_path, 'Info.txt')):
            info_dict['Path'] = level_path
            f = open(os.path.join(level_path, 'Info.txt'), 'r')
            for line in f:
                k, v = [s.strip() for s in line.split(":")]
                info_dict[k] = v
                if k == 'Rank': info_dict[k] = int(v)
            entry_points.append(info_dict)

def start_widgets():
    back_trigger = widget.KeyTrigger(key.ESCAPE, gui.go_back)
    widgets = [back_trigger]
    def level_starter(d, n):
        def start():
            sound.play(resources.whoosh_1)
            change_entry_point(d, n)
            if settings.first_launch:
                gui.change_to_card(Card(instruction_widgets_first()))
            else:
                gui.state_goer(gui.START)()
        return start
    
    y = env.norm_h/16*10
    sorted_entry_points = sorted(entry_points, key=operator.itemgetter('Rank'))
    
    for info in sorted_entry_points:
        new_button = widget.TextButton(
            info['Name'], env.norm_w/2, y,
            level_starter(info['Path'], info['First level']), 
            anchor_x='center'
        )    
        widgets.append(new_button)
        if 'Author' in info.keys():
            y -= 30
            new_label = pyglet.text.Label(
                "By "+info['Author'], x=env.norm_w/2, y=y,
                color=new_button.color, font_name='Gill Sans',
                font_size=14
            )
            widgets.append(new_label)
        if 'Difficulty' in info.keys():
            y -= 20
            new_label = pyglet.text.Label(
                "Difficulty: "+info['Difficulty'], x=env.norm_w/2, y=y,
                color=new_button.color, font_name='Gill Sans',
                font_size=14
            )
            widgets.append(new_label)
        y -= env.norm_h/8-30
    
    start_trigger = widget.KeyTrigger(key.SPACE, widgets[1].action)
    widgets.append(start_trigger)
    return widgets

def save_widgets():    
    back_trigger = widget.KeyTrigger(key.RETURN, gui.go_back)
    back_trigger_2 = widget.KeyTrigger(key.ESCAPE, gui.go_back)
    
    text_box = widget.TextEntry(
        "Save ", env.norm_w/2, env.norm_h/2, env.norm_w-10, 
        save, anchor_x='center'
    )
    back_button = widget.TextButton(
        "Back",
        env.norm_w/2, text_box.layout.y-50,
        gui.go_back, 
        size=36, anchor_x='center'
    )
    underline = widget.Line(
        env.norm_w/4, text_box.layout.y-3, env.norm_w/4*3, text_box.layout.y-3
    )
    return [text_box, back_button, back_trigger, back_trigger_2, underline]
