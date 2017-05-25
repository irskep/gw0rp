import pyglet, yaml
import draw, resources, graphics
from yamlobjects import *

LINE = 0
CIRCLE = 1
primitives = []
labels = []
label_batch = pyglet.graphics.Batch()
simple_objects = []
simple_objects_batch = pyglet.graphics.Batch()
lower_group = pyglet.graphics.OrderedGroup(0)
upper_group = pyglet.graphics.OrderedGroup(5)
current_id = 0

width = 50*40
height = 50*40
player_x = 100
player_y = 100
player_angle = 1.57
player_config = 'normal'
background_image = pyglet.image.TileableTexture.create_for_image(resources.sand)
background_image_name = 'sand'
prim_color = (0,0,0,1)

camera_x = 0
camera_y = 0

THRUSTER = 0
DECOY = 1
BOMB = 2
SHIELD = 3
REPAIR = 4
BEACON = 5
PLASMA = 6
CARGO = 7
TOXIN = 8
BRAIN = 9
max_types_1 = 10

PTURRET1 = 100
PTURRET2 = 101
RTURRET1 = 102
CTURRET1 = 103
TANK1 = 104
TANK2 = 105
max_types_2 = 0

r = resources
obj_table = {
    #real img, class name, icon img
    THRUSTER:   [r.thruster_off,    FreeThruster,   r.FreeThruster],
    DECOY:      [r.logic_0,         FreeDecoy,      r.FreeDecoy],
    BOMB:       [r.power_0,         FreeBomb,       r.FreeBomb],
    SHIELD:     [r.ShieldGenerator, FreeShield,     r.FreeShield],
    REPAIR:     [r.repair,          FreeRepair,     r.FreeRepair],
    BEACON:     [r.beacon_1,        FreeBeacon,     r.FreeBeacon],
    PLASMA:     [r.turret1_blue,    FreeTurret,     r.FreeTurret],
    CARGO:      [r.cargo,           FreeCargo,      r.FreeCargo],
    TOXIN:      [r.Harvester_1,     FreeToxin,      r.FreeToxin],
    BRAIN:      [r.core_8,          FreeGworpBrain, r.t_core_8]
}

id_table = {
    u"!FreeThruster": THRUSTER,
    u"!FreeDecoy": DECOY,
    u"!FreeBomb": BOMB,
    u"!FreeShield": SHIELD,
    u"!FreeRepair": REPAIR,
    u"!FreeBeacon": BEACON,
    u"!FreeTurret": PLASMA,
    u"!FreeCargo": CARGO,
    u"!FreeToxin": TOXIN,
    u"!FreeGworpBrain": BRAIN
}

turrets = [
    ('turret1_blue', PlasmaTurret1),
    ('turret1_orange', PlasmaTurret2),
    ('turret2_static', RapidTurret1),
    ('turret3_static', CannonTurret1)
]

turret_bases = [
    ('turret_base', 'Scaffold'),
    ('Tower1_Static', 'MetalTower'),
    ('Tower2_Static', 'ConcreteTower'),
    ('tank_dead', 'Tank')
]

class SimpleObjectSprite(pyglet.sprite.Sprite):
    def __init__(self, obj_id, x, y, rotation, obj_type):
        self.obj_id = obj_id
        self.obj_type = obj_type
        
        img = obj_table[obj_type][0]
        super(SimpleObjectSprite, self).__init__(
            img, x, y, batch=simple_objects_batch
        )
        self.rotation = rotation
    
    def get_yaml_copy(self):
        return obj_table[self.obj_type][1](
            self.obj_id, self.x, self.y, self.rotation
        )
            

class ImageDoorSprite(pyglet.sprite.Sprite):
    def __init__(self, obj_id, key, x, y, rotation):
        self.obj_id = obj_id
        self.key = key
        
        door_images = {
            0: resources.Door2_R_Static,
            3: resources.Door3_G_Static,
            4: resources.Door1_B_1,
            5: resources.Door2_P_Static
        }
        
        super(ImageDoorSprite, self).__init__(
            door_images[key], x, y, batch=simple_objects_batch
        )
        self.rotation = rotation
    
    def get_yaml_copy(self):
        return ImageDoor(
            self.obj_id, self.key, self.x, self.y, self.rotation
        )
    

class TurretSprite(pyglet.sprite.Sprite):
    def __init__(self, obj_id, x, y, rotation, turret_type, base_type, base_rotation=0):
        self.obj_id = obj_id
        self.turret_type = turret_type
        self.base_type = base_type
        self.base_sprite = pyglet.sprite.Sprite(
            getattr(resources, turret_bases[base_type][0]), x, y,
            batch=simple_objects_batch, group=lower_group
        )
        super(TurretSprite, self).__init__(
            getattr(resources, turrets[turret_type][0]), x, y,
            batch=simple_objects_batch, group=upper_group
        )
        self.rotation = rotation
        self.base_sprite.rotation = base_rotation
    
    def set_position(self, x, y):
        self.base_sprite.set_position(x, y)
        super(TurretSprite, self).set_position(x, y)
    
    def delete(self):
        self.base_sprite.delete()
        super(TurretSprite, self).delete()
    
    def get_yaml_copy(self):
        return turrets[self.turret_type][1](
            self.obj_id, self.x, self.y, self.rotation, 
            turret_bases[self.base_type][1], self.base_sprite.rotation
        )
    

class RockSprite(pyglet.sprite.Sprite):
    img_table = [getattr(resources, "rock_"+str(i+1)) for i in range(7)]
    
    def __init__(self, obj_id, x, y, rotation, rock_type):
        self.obj_id = obj_id
        self.rock_type = rock_type
        img = self.img_table[rock_type]
        super(RockSprite, self).__init__(img, x, y, batch=simple_objects_batch)
        self.rotation = rotation
    
    def get_yaml_copy(self):
        return Rock(self.obj_id, self.x, self.y, self.rotation, self.rock_type)
    

class DecalSprite(pyglet.sprite.Sprite):
    def __init__(self, obj_id, x, y, rotation, scale, img_name, overhead=False):
        self.obj_id = obj_id
        self.img_name = img_name
        img = getattr(resources, img_name)
        super(DecalSprite, self).__init__(img, x, y, batch=simple_objects_batch)
        self.rotation = rotation
        self.scale = scale
        self.overhead = overhead
    
    def get_yaml_copy(self):
        return Decal(
            self.obj_id, self.x, self.y, self.rotation, self.scale, self.img_name, self.overhead
        )
    

class DestructibleWallSprite(DecalSprite):
    def get_yaml_copy(self):
        return DestructibleWall(self.obj_id, self.x, self.y, self.rotation, self.img_name)
        

def get_id():
    #global current_id
    #current_id += 1
    #return current_id
    id_inc = 0
    #COMMENSE STUPID, HASTILY-WRITTEN ALGORITHM
    id_list = []
    for obj in primitives:
        id_list.append(obj.obj_id)
    for obj in simple_objects:
        id_list.append(obj.obj_id)
    num_ids = len(primitives) + len(simple_objects)
    max_id = 1
    while max_id < num_ids+1:
        if max_id not in id_list: return max_id
        max_id += 1
    return max_id

def add_label(text, x, y, owner):
    global labels
    new_label = pyglet.text.Label(text, x=x, y=y, font_size=10,
                    anchor_x='center', anchor_y='center',
                    color=(0,0,0,255), batch=label_batch)
    owner.label = new_label
    labels.append(new_label)
    return new_label

def draw_level_objects():
    colors = {
        True: prim_color,
        False: (1,0,0,1)
    }
    for obj in primitives:
        if obj.yaml_tag == u"!Line":
            if obj.visible:
                draw.set_color(*prim_color)
            else:
                if obj.collides:
                    draw.set_color(0,1,0,1)
                else:
                    draw.set_color(1,0,0,1)
            draw.line(obj.x1, obj.y1, obj.x2, obj.y2)
        elif obj.yaml_tag == u"!Circle":
            if obj.visible:
                draw.set_color(*prim_color)
            else:
                if obj.collides:
                    draw.set_color(0,1,0,1)
                else:
                    draw.set_color(1,0,0,1)
            draw.circle(obj.x, obj.y, obj.radius)
        elif obj.yaml_tag == u"!FilledRect":
            draw.set_color(*colors[obj.visible])
            draw.rect(obj.x1, obj.y1, obj.x2, obj.y2)
        elif obj.yaml_tag == u"!FilledTriangle":
            draw.set_color(*colors[obj.visible])
            draw.polygon((obj.x1, obj.y1, obj.x2, obj.y2, obj.x3, obj.y3))
        elif obj.yaml_tag == u"!Door":
            draw.set_color(*resources.key_colors[obj.key])
            graphics.set_line_width(5.0)
            draw.line(obj.x1, obj.y1, obj.x2, obj.y2)
            draw.set_color(*colors[True])
            graphics.set_line_width(1.0)
            draw.line(obj.x1, obj.y1, obj.x2, obj.y2)
        elif obj.yaml_tag == u"!Key":
            draw.set_color(1,1,1,1)
            resources.key_images[obj.number].blit(obj.x, obj.y)
            
    simple_objects_batch.draw()
    draw.set_color(1,1,1,1)
    for label in labels:
        draw.rect(
            label.x-label.content_width/2-3, label.y-label.content_height/2,
            label.x+label.content_width/2+3, label.y+label.content_height/2
        )
    label_batch.draw()

def save(path):
    stream = file(path, 'w')
    yaml_objects = [
        Env(
            width, height, player_x, player_y, 
            background_image_name, tuple([int(c*255) for c in prim_color]),
            player_angle, player_config
        )
    ]
    for obj in primitives:
        yaml_objects.append(obj.get_yaml_copy())
    for obj in simple_objects:
        yaml_objects.append(obj.get_yaml_copy())
    yaml.dump(yaml_objects, stream)
    stream.close()

def load(path):
    global primitives, simple_objects, current_id
    global label_batch, simple_objects_batch, lower_group, upper_group
    global width, height, player_x, player_y, player_angle, player_config
    global prim_color, labels, background_image_name
    global camera_x, camera_y, background_image
    camera_x, camera_y = 0, 0
    
    primitives = []
    simple_objects = []
    for label in labels:
        label.delete()
    labels = []
    label_batch = pyglet.graphics.Batch()
    simple_objects_batch = pyglet.graphics.Batch()
    lower_group = pyglet.graphics.OrderedGroup(0)
    upper_group = pyglet.graphics.OrderedGroup(5)
    
    turret_table = {
        u"!PlasmaTurret1": 0,
        u"!PlasmaTurret2": 1,
        u"!RapidTurret1": 2,
        u"!CannonTurret1": 3,
    }
    
    base_table = {
        'Scaffold': 0,
        'MetalTower': 1,
        'ConcreteTower': 2,
        'Tank': 3, 
        '': 0
    }
    
    stream = file(path, 'r')
    current_id = 0
    yaml_objects = yaml.load(stream)
    for obj in yaml_objects:
        if hasattr(obj, 'obj_id'):
            if current_id < obj.obj_id:
                current_id = obj.obj_id
        
        if obj.yaml_tag == u"!Circle":
            if not hasattr(obj, 'collides'):
                obj.collides = True
            primitives.append(obj)
            add_label(str(obj.obj_id), obj.x, obj.y, obj)
        
        if obj.yaml_tag == u"!Key":
            primitives.append(obj)
            add_label(str(obj.obj_id), obj.x-5, obj.y+5, obj)
        
        if obj.yaml_tag == u"!Line" or obj.yaml_tag == u"!Door":
            if not hasattr(obj, 'collides'):
                obj.collides = True
            primitives.append(obj)
            add_label(
                str(obj.obj_id), (obj.x1+obj.x2)/2, (obj.y1+obj.y2)/2, obj
            )
        
        if obj.yaml_tag == u"!FilledRect":
            primitives.append(obj)
            add_label(
                str(obj.obj_id), (obj.x1+obj.x2)/2, (obj.y1+obj.y2)/2, obj
            )
        
        if obj.yaml_tag == u"!FilledTriangle":
            primitives.append(obj)
            add_label(
                str(obj.obj_id), 
                (obj.x1+obj.x2+obj.x3)/3, (obj.y1+obj.y2+obj.y3)/3, obj
            )
        
        if obj.yaml_tag == u"!Rock":
            new_sprite = RockSprite(
                obj.obj_id, obj.x, obj.y, obj.rotation, obj.rock_type)
            simple_objects.append(new_sprite)
            add_label(str(obj.obj_id), obj.x, obj.y, new_sprite)
        
        if obj.yaml_tag == u"!Decal":
            if not hasattr(obj, 'overhead'): obj.overhead = False
            new_decal = DecalSprite(
                obj.obj_id, obj.x, obj.y, obj.rotation, obj.scale, obj.img_name, obj.overhead
            )
            simple_objects.append(new_decal)
            add_label(str(obj.obj_id), obj.x, obj.y, new_decal)
        
        if obj.yaml_tag == u"!DestructibleWall":
            new_decal = DestructibleWallSprite(
                obj.obj_id, obj.x, obj.y, obj.rotation, 1, obj.img_name)
            simple_objects.append(new_decal)
            add_label(str(obj.obj_id), obj.x, obj.y, new_decal)
        
        if obj.yaml_tag == u"!ImageDoor":
            new_door = ImageDoorSprite(
                obj.obj_id, obj.key, obj.x, obj.y, obj.rotation
            )    
            simple_objects.append(new_door)
            add_label(str(obj.obj_id), obj.x, obj.y, new_door)
        
        if obj.yaml_tag in turret_table:
            if not hasattr(obj, 'base_type'):
                obj.base_type=""
                obj.base_rotation = 0
            new_turret = TurretSprite(
                obj.obj_id, obj.x, obj.y, obj.rotation,
                turret_table[obj.yaml_tag], base_table[obj.base_type],
                obj.base_rotation
            )    
            simple_objects.append(new_turret)
            add_label(str(obj.obj_id), obj.x, obj.y, new_turret)
        
        if obj.yaml_tag in id_table:
            new_sprite = SimpleObjectSprite(
                obj.obj_id, obj.x, obj.y, obj.rotation, 
                id_table[obj.yaml_tag])
            simple_objects.append(new_sprite)
            add_label(str(obj.obj_id), obj.x, obj.y, new_sprite)
        
        if obj.yaml_tag == u"!Env":
            width, height = obj.width, obj.height
            player_x, player_y = obj.player_x, obj.player_y
            img = getattr(resources, obj.background_image)
            if img.width != width or img.height != height:
                background_image = pyglet.image.TileableTexture.create_for_image(img)
            else:
                background_image = img
            background_image_name = obj.background_image
            prim_color = tuple([c/255.0 for c in obj.prim_color])
            if not hasattr(obj, 'player_angle'):
                obj.player_angle = 1.57
            if not hasattr(obj, 'player_config'):
                obj.player_config = 'normal'
            player_angle = obj.player_angle
            player_config = obj.player_config
    stream.close()
