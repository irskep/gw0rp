import yaml

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

class yaml_obj(yaml.YAMLObject):
    def __repr__(self):
        return repr_for_obj(self)

class Env(yaml_obj):
    yaml_tag = u"!Env"
    def __init__(
            self, width, height, player_x, player_y, background_image, 
            prim_color=(0,0,0,1), player_angle=0.0, player_config='normal'
            ):
        self.width = width
        self.height = height
        self.player_x = player_x
        self.player_y = player_y
        self.background_image = background_image
        self.prim_color = prim_color
        self.player_angle = player_angle
        self.player_config = player_config
    
    def get_offset(self):
        return self

class Line(yaml_obj):
    yaml_tag = u"!Line"
    def __init__(self, obj_id, x1, y1, x2, y2, visible, collides):
        self.obj_id = obj_id
        self.collides = collides
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.visible = visible
    
    def get_yaml_copy(self):
        return Line(
            self.obj_id, self.x1, self.y1, self.x2, self.y2, self.visible,
            self.collides
        )
    

class Door(yaml_obj):
    yaml_tag = u"!Door"
    def __init__(self, obj_id, x1, y1, x2, y2, key, visible):
        self.obj_id = obj_id
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.key = key
        self.visible = visible
    
    def get_yaml_copy(self):
        return Door(
            self.obj_id, self.x1, self.y1, self.x2, self.y2, 
            self.key, self.visible
        )
    

class ImageDoor(yaml_obj):
    yaml_tag = u"!ImageDoor"
    def __init__(self, obj_id, key, x, y, rotation):
        self.obj_id = obj_id
        self.key = key
        self.x = x
        self.y = y
        self.rotation = rotation
    

class Key(yaml_obj):
    yaml_tag = u"!Key"
    def __init__(self, obj_id, x, y, number):
        self.obj_id = obj_id
        self.x = x
        self.y = y
        self.number = number
    
    def get_yaml_copy(self):
        return Key(self.obj_id, self.x, self.y, self.number)
    

class FilledRect(yaml_obj):
    yaml_tag = u"!FilledRect"
    def __init__(self, obj_id, x1, y1, x2, y2, visible):
        self.obj_id = obj_id
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.visible = visible
    
    def get_yaml_copy(self):
        return FilledRect(
            self.obj_id, self.x1, self.y1, self.x2, self.y2, self.visible
        )
    

class FilledTriangle(yaml_obj):
    yaml_tag = u"!FilledTriangle"
    def __init__(self, obj_id, x1, y1, x2, y2, x3, y3, visible):
        self.obj_id = obj_id
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.x3 = x3
        self.y3 = y3
        self.visible = visible
    
    def get_yaml_copy(self):
        return FilledTriangle(
            self.obj_id, self.x1, self.y1, 
            self.x2, self.y2, self.x3, self.y3, 
            self.visible
        )
    

class Circle(yaml_obj):
    yaml_tag = u"!Circle"
    def __init__(self, obj_id, x, y, radius, visible, collides):
        self.obj_id = obj_id
        self.x = x
        self.y = y
        self.radius = radius
        self.visible = visible
        self.collides = collides
    
    def get_yaml_copy(self):
        return Circle(
            self.obj_id, self.x, self.y, self.radius, self.visible,
            self.collides
        )
    

class Rock(yaml_obj):
    yaml_tag = u"!Rock"
    def __init__(self, obj_id, x, y, rotation, rock_type):
        self.obj_id = obj_id
        self.x = x
        self.y = y
        self.rotation = rotation
        self.rock_type = rock_type
    

class Decal(yaml_obj):
    yaml_tag = u"!Decal"
    def __init__(self, obj_id, x, y, rotation, scale, img_name, overhead=False):
        self.obj_id = obj_id
        self.x = x
        self.y = y
        self.rotation = rotation
        self.img_name = img_name
        self.scale = scale
        self.overhead = overhead
    

class DestructibleWall(yaml_obj):
    yaml_tag = u"!DestructibleWall"
    def __init__(self, obj_id, x, y, rotation, img_name):
        self.obj_id = obj_id
        self.x = x
        self.y = y
        self.rotation = rotation
        self.img_name = img_name
    

class SimpleObject(yaml_obj):
    yaml_tag = u"!SimpleObject"
    def __init__(self, obj_id, x, y, rotation):
        self.obj_id = obj_id
        self.x = x
        self.y = y
        self.rotation = rotation
    

class Turret(yaml_obj):
    yaml_tag = u"!Turret"
    def __init__(self, obj_id, x, y, rotation, base_type="", base_rotation=0):
        super(Turret, self).__init__()
        self.obj_id = obj_id
        self.x = x
        self.y = y
        self.rotation = rotation
        self.base_type = base_type
        self.base_rotation = base_rotation
        

class Tank1(SimpleObject):
    yaml_tag = u"!Tank1"

class Tank2(SimpleObject):
    yaml_tag = u"!Tank2"

class PlasmaTurret1(Turret):
    yaml_tag = u"!PlasmaTurret1"

class PlasmaTurret2(Turret):
    yaml_tag = u"!PlasmaTurret2"

class PlasmaTurret3(Turret):
    yaml_tag = u"!PlasmaTurret3"

class RapidTurret1(Turret):
    yaml_tag = u"!RapidTurret1"

class RapidTurret2(Turret):
    yaml_tag = u"!RapidTurret2"

class CannonTurret1(Turret):
    yaml_tag = u"!CannonTurret1"

class CannonTurret2(Turret):
    yaml_tag = u"!CannonTurret2"

class FreeThruster(SimpleObject):
    yaml_tag = u"!FreeThruster"

class FreeDecoy(SimpleObject):
    yaml_tag = u"!FreeDecoy"

class FreeShield(SimpleObject):
    yaml_tag = u"!FreeShield"

class FreeRepair(SimpleObject):
    yaml_tag = u"!FreeRepair"

class FreeBeacon(SimpleObject):
    yaml_tag = u"!FreeBeacon"

class FreeToxin(SimpleObject):
    yaml_tag = u"!FreeToxin"

class FreeGworpBrain(SimpleObject):
    yaml_tag = u"!FreeGworpBrain"

class FreeBomb(SimpleObject):
    yaml_tag = u"!FreeBomb"

class FreeTurret(SimpleObject):
    yaml_tag = u"!FreeTurret"

class FreeCargo(SimpleObject):
    yaml_tag = u"!FreeCargo"