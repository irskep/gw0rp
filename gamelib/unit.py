import math, pymunk, pyglet, random
from util import env, draw, particle, physics
from util import resources, settings, sound
import bullet, level, pyro, event

image_table = dict(
    Unit=None,
    Beacon=resources.beacon_1, 
    BlueTurret=resources.turret1_blue, 
    Bomb=resources.bomb_static,
    Brain=resources.core_anim,
    Brain2=resources.ph3ge_anim,
    CannonTurret=resources.turret3_static,
    Cargo=resources.cargo,
    Decoy=resources.logic_1,
    GworpBrain=resources.core_anim,
    RapidTurret=resources.turret2_static, 
    RapidTurret2=resources.turret2_R_static,
    Repair=resources.repair, 
    Shield=resources.shield, 
    Thruster=resources.thruster_off,
    Toxin=resources.Harvester_1
)

class Unit(pyglet.sprite.Sprite):
    def __init__(
            self, gluebody=None, offset=(0,0), rot=0.0, radius=0.0, mass=0.0, 
            obj_id=0, img=None, load_from=None):
        if radius == 0.0: radius = physics.default_radius
        if mass == 0.0: mass = physics.default_mass
        
        if img == None:
            img = image_table[self.__class__.__name__]
        
        super(Unit, self).__init__(
            img, batch=level.batch, group=level.unit_group
        )
        
        self.label = "Generic Unit"
        self.uses_keys = False
        self.ask_key = False
        self.persistent_attrs = []
        
        #self.init_attr('active', False, load_from)
        #Active state is saved but ignored on load.
        self.active = False
        self.persistent_attrs.append('active')
        
        if hasattr(self, 'health'):
            self.health_full = self.health
        else:
            self.health_full = physics.default_health*2
        
        self.init_attr('active_timer', 0, load_from)
        self.init_attr('health', self.health_full, load_from)
        self.init_attr('local_angle', rot, load_from)
        self.init_attr('local_angle_target', rot, load_from)
        self.init_attr('mass', mass, load_from)
        self.init_attr('obj_id', obj_id, load_from)
        self.init_attr('offset', offset, load_from)
        self.init_attr('radius', radius, load_from)
        
        self.local_angle_move = 90.0
        self.offset_dist_sq = self.offset[0]**2+self.offset[1]**2
            
        self.using_sound = False
        self.loop_sound = False
        
        self.gluebody = gluebody
        self.parent = None
        self.parent_unit = None
        self.circle = None
        self.circle2 = None
        self.segment = None
        self.line_length = 0
        self.circle2_dist = 0
        self.circle2_rad = 0
        
        self.ignore_death = False
        
        self.initialized = False
        if gluebody != None: self.initialize(gluebody)
    
    def init_attr(self, attr_string, default, load_dict):
        self.persistent_attrs.append(attr_string)
        if load_dict == None:
            setattr(self, attr_string, default)
        else:
            setattr(self, attr_string, load_dict[attr_string])
    
    def get_dict(self):
        return_dict = {
            'ClassName': self.__class__.__name__
        }
        key_list = []
        for k, unit_list in env.key_bindings.items():
            if self in unit_list:
                key_list.append(k)
        return_dict['key_bindings'] = key_list
        for item in self.persistent_attrs:
            return_dict[item] = getattr(self, item)
        return return_dict
    
    def initialize(self, gluebody=None, collision_type=1):
        """Create shape and attach it to a body"""
        if gluebody == None: gluebody = self.gluebody
        else: self.gluebody = gluebody
        self.parent = gluebody
        self.set_position(*self.offset)
        self.circle = pymunk.Circle(
            gluebody.body, self.radius, self.offset
        )
        self.circle.friction = physics.default_friction
        self.circle.elasticity = physics.default_elasticity
        self.circle.parent = self
        self.circle.collision_type = collision_type
        self.circle.layers = 1
        self.circle.obj_id = self.obj_id
        
        if self.line_length != 0 or self.circle2_rad > 0:
            xa = math.cos(-math.radians(self.local_angle))
            ya = math.sin(-math.radians(self.local_angle))
        
        if self.line_length != 0:    
            x2 = self.offset[0] + self.line_length*xa
            y2 = self.offset[1] + self.line_length*ya
            self.segment = pymunk.Segment(
                gluebody.body, self.offset, (x2, y2), 2
            )
        
            self.segment.friction = physics.default_friction
            self.segment.elasticity = physics.default_elasticity
            self.segment.collision_type = collision_type
            self.segment.layers = 1
            self.segment.parent = self
            self.segment.obj_id = self.obj_id
        
        if self.circle2_rad > 0:
            cx = self.offset[0] + self.circle2_dist*xa
            cy = self.offset[1] + self.circle2_dist*ya
            self.circle2 = pymunk.Circle(
                gluebody.body, self.circle2_rad, (cx, cy)
            )
            self.circle2.friction = physics.default_friction
            self.circle2.elasticity = physics.default_elasticity
            self.circle2.parent = self
            self.circle2.collision_type = collision_type
            self.circle2.layers = 1
            self.circle2.obj_id = self.obj_id
        
        self.initialized = True
    
    def add_shapes(self):
        physics.space.add(self.circle)
        if self.line_length != 0:
            physics.space.add(self.segment)
        if self.circle2_rad > 0:
            physics.space.add(self.circle2)
    
    def migrate(self):
        pass
    
    def remove_shapes(self):
        physics.space.remove(self.circle)
        if self.line_length != 0:
            physics.space.remove(self.segment)
        if self.circle2_rad > 0:
            physics.space.remove(self.circle2)
    
    def update_shapes(self):
        xa = math.cos(-math.radians(self.local_angle))
        ya = math.sin(-math.radians(self.local_angle))
        
        self.circle.center = self.offset
        if self.line_length != 0:
            x2 = self.offset[0] + self.line_length*xa
            y2 = self.offset[1] + self.line_length*ya
            self.segment.a = self.offset
            self.segment.b = (x2, y2)
        
        if self.circle2_rad > 0:
            cx = self.offset[0] + self.circle2_dist*xa
            cy = self.offset[1] + self.circle2_dist*ya
            self.circle2.center = (cx, cy)
    
    def update(self):
        if self.health <= 0:
            physics.update_bodies_now = True
        elif self.health < self.health_full * 0.5:
            self.health += physics.default_damage * 0.1 * env.dt
        
        self.set_position(*self.gluebody.body.local_to_world(self.offset))
            
        if self.local_angle != self.local_angle_target:
            move_max = self.local_angle_move*env.dt
            da = (self.local_angle_target - self.local_angle) % 360 - 180
            if abs(da) >= 180-move_max :
                self.local_angle = self.local_angle_target
            elif da < 0:
                self.local_angle += move_max
            elif da > 0:
                self.local_angle -= move_max
            self.update_shapes()
        if self.health <= self.health_full * 0.5:
            move_amt = -0.2 + (self.health_full*0.5 - self.health)*0.4
            move_amt *= random.random()
            self.rotation = -self.gluebody.angle_degrees + self.local_angle \
                            + move_amt
        else:
            self.rotation = -self.gluebody.angle_degrees + self.local_angle
        if self.active_timer:
            self.active_timer -= env.dt
            if self.active_timer < 0: self.active_timer = 0
    
    def die(self):
        if not self.ignore_death:
            if event.destroy_funcs.has_key(self.obj_id):
                for func in event.destroy_funcs[self.obj_id]:
                    result = func()
        self.parent = None
        physics.unit_update_list.remove(self)
        self.remove_shapes()
        self.delete()
    
    def set_offset(self, x, y):
        self.offset = (x,y)
        self.set_position(*self.offset)
        self.offset_dist_sq = self.offset[0]*self.offset[0] + \
                              self.offset[1]*self.offset[1]
    
    def init_sound(self, sound, loop=False):
        self.sound = sound
        self.sound_player = pyglet.media.Player()
        self.sound_player.pause()
        self.loop_sound = loop
        if self.loop_sound:
            self.sound_player.eos_action = self.sound_player.EOS_LOOP
            self.sound_player.volume = settings.sound_volume
            self.sound_player.queue(self.sound)
        self.using_sound = True
    
    def activate(self):
        self.active = True
        if self.using_sound:
            self.sound_player.volume = settings.sound_volume
            if self.loop_sound:
                self.sound_player.play()
            else:
                self.sound.play()
    
    def deactivate(self):
        self.active = False
        if self.using_sound and self.loop_sound:
            self.sound_player.pause()
    
    def attach(self):
        for unit in self.gluebody.units:
            if hasattr(unit, 'update_patients'):
                unit.update_patients()
    
    def release(self):
        try:
            for unit in self.gluebody.units:
                if hasattr(unit, 'update_patients'):
                    unit.patients = [unit]
        except:
            if hasattr(self, 'patients'):
                self.patients = [self]
        env.unbind_keys_for_unit(self)
    
    def draw_collisions(self):
        if self.line_length != 0:
            x1, y1 = self.gluebody.body.local_to_world(self.segment.a)
            x2, y2 = self.gluebody.body.local_to_world(self.segment.b)
            draw.line(x1, y1, x2, y2)
        if self.circle2_rad > 0:
            r = self.circle2.radius
            x, y = self.gluebody.body.local_to_world(self.circle2.center)
            draw.ellipse_outline(x-r, y-r, x+r, y+r)
        r = self.circle.radius
        x, y = self.gluebody.body.local_to_world(self.circle.center)
        draw.ellipse_outline(x-r, y-r, x+r, y+r)
    

class Brain(Unit):
    def __init__(
            self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None
            ):
        self.health = physics.default_health*3
        super(Brain, self).__init__(
            body, offset, rot, 0, 0, obj_id, None, load_from
        )
        self.label = "Brain"
        self.uses_keys = False
        self.power_output = 100
        self.logic_output = 100
    

class Brain2(Brain):
    def __init__(self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None):
        super(Brain2, self).__init__(body, offset, rot, obj_id, load_from)
    

class GworpBrain(Brain):
    def __init__(self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None):
        self.health = 1000000000000
        super(GworpBrain, self).__init__(body, offset, rot, obj_id, load_from)
        self.label = "gw0rp's brain"
    

class Decoy(Unit):
    def __init__(
                self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None
            ):
        self.health = physics.default_health*3
        super(Decoy, self).__init__(
            body, offset, rot, 0, 0, obj_id, None, load_from
        )
        self.label = "Decoy"
        self.uses_keys = True
        self.ask_key = True
        
        self.init_attr('toggled_on', False, load_from)
    
    def update(self):
        super(Decoy, self).update()
        if self.toggled_on:
            level.decoy_x, level.decoy_y = self.x, self.y
            level.decoy_present = True
    
    def activate(self):
        super(Decoy, self).activate()
        self.toggled_on = not self.toggled_on
        if self.toggled_on:
            self.image = resources.logic_anim
        else:
            self.image = resources.logic_1
    
    def attach(self):
        if not self.toggled_on:
            self.activate()
        super(Decoy, self).attach()
    

class Bomb(Unit):
    def __init__(
                self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None
            ):
        super(Bomb, self).__init__(
            body, offset, rot, 0, 0, obj_id, None, load_from
        )
        self.label = "Bomb"
        self.uses_keys = True
        self.blast_radius = 150
        
        self.init_attr('toggled_on', False, load_from)
        self.toggled_on = not self.toggled_on
        self.activate()
    
    def activate(self):
        super(Bomb, self).activate()
        self.toggled_on = not self.toggled_on
        if self.toggled_on:
            self.image = resources.bomb_anim
        else:
            self.image = resources.bomb_static
    
    def update(self):
        if not self.toggled_on or self.parent == level.player:
            super(Bomb, self).update()
            return
        if (self.gluebody.body.velocity.x != 0 or \
                self.gluebody.body.velocity.y != 0):
            self.gluebody.body.velocity = (0,0)
        if self.gluebody.body.angular_velocity != 0:
            self.gluebody.body.angular_velocity = 0
        super(Bomb, self).update()
        if level.player == None: return
        if (self.x-level.player.x)*(self.x-level.player.x) + \
                (self.y-level.player.y)*(self.y-level.player.y) \
                > (self.blast_radius+100)**2:
            self.detonate()
    
    def in_range(self, x, y):
        return (x-self.x)*(x-self.x) + (y-self.y)*(y-self.y) \
                <= self.blast_radius*self.blast_radius
    
    def detonate(self):        
        for body in physics.body_update_list:
            if hasattr(body, 'x'):
                if self.in_range(body.x, body.y):
                    if hasattr(body, 'explode'):
                        body.explode()
                    if hasattr(body, 'health'):
                        body.health -= physics.default_damage*5
        for unit in physics.unit_update_list:
            if hasattr(unit, 'health') and  self.in_range(unit.x, unit.y):
                    unit.health -= physics.default_damage*5
        sound.play(resources.expl_huge)                
        sound.play(resources.expl_large)
        particle.explode_huge(self.x, self.y)
        self.health = 0
        physics.update_bodies_now = True
        self.ignore_death = True
        event.quake()
    
    def attach(self):
        if not self.toggled_on:
            self.activate()
        super(Bomb, self).attach()
    

class Shield(Unit):
    def __init__(
                self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None
            ):
        super(Shield, self).__init__(
            body, offset, rot, 0, 0, obj_id, None, load_from
        )
        self.label = "Shield"
        self.uses_keys = False
    

class Cargo(Unit):
    def __init__(
                self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None
            ):
        radius = (physics.default_radius)*0.6
        mass = physics.default_mass*0.2
        super(Cargo, self).__init__(
            body, offset, rot, radius, mass, obj_id, None, load_from
        )
        self.label = "Cargo"
        self.uses_keys = False
        self.scale = 0.6
    
    def update(self):
        if self.active and (self.gluebody.body.velocity.x != 0 or \
                            self.gluebody.body.velocity.y != 0):
            self.gluebody.body.velocity = (0,0)
        if self.active and self.gluebody.body.angular_velocity != 0:
            self.gluebody.body.angular_velocity = 0
        super(Cargo, self).update()
    

class Drone(pyglet.sprite.Sprite):
    """Used by Repair"""
    def __init__(self, patient):
        super(Drone, self).__init__(
            resources.drone, patient.x, patient.y,
            batch=level.batch, group=level.unit_group
        )
        self.patient = patient
    
    def update(self):
        if self.patient == None:
            self.delete()
            return
        if self.patient.health < self.patient.health_full * 0.9 and self.patient.health > 0:
            self.x = self.patient.x
            self.y = self.patient.y
            if not self.visible:
                self.visible = True
        elif self.visible:
            self.visible = False
    

class Repair(Unit):
    def __init__(
                self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None
            ):
        super(Repair, self).__init__(
            body, offset, rot, physics.default_radius*0.7, 0, obj_id, None, load_from
        )
        self.scale = 0.7
        self.label = "Repair"
        self.uses_keys = False
        self.patients = []
        self.drones = []
        self.update_patients_now = True
    
    def update(self):
        if self.update_patients_now:
            self.update_patients()
            self.update_patients_now = False
        amt = physics.default_damage * env.dt
        for unit in self.patients:
            if unit.health < unit.health_full:
                unit.health += amt
            if unit.gluebody != self.gluebody and unit in self.patients:
                self.patients.remove(unit)
                self.update_patients()
        for drone in self.drones:
            drone.update()
        super(Repair, self).update()
    
    def update_patients(self):
        for drone in self.drones:
            drone.delete()
        self.patients = []
        self.drones = []
        if not hasattr(self.gluebody, 'units'): return
        self.patients = self.gluebody.units
        for unit in self.patients:
            self.drones.append(Drone(unit))
        # for unit in self.gluebody.units:
        #             d = (self.offset[0]-unit.offset[0])*(self.offset[0]-unit.offset[0])
        #             d += (self.offset[1]-unit.offset[1])*(self.offset[1]-unit.offset[1])
        #             if d <= 65*65:
        #                 self.patients.append(unit)
        #                 self.drones.append(Drone(unit))
    
    def die(self):
        for drone in self.drones:
            drone.patient = None
            drone.visible = False
        self.drones = []
        super(Repair, self).die()
    
    def release(self):
        for drone in self.drones:
            drone.patient = None
            drone.visible = False
            drone.delete()
        self.drones = []
        super(Repair, self).release()
    

class Key(Unit):
    def __init__(
                self, number=0, body=None, offset=(0,0), rot=0.0, 
                obj_id=0, load_from=None
            ):
        img = resources.key_images[number]
        radius = img.height/2
        mass = physics.default_mass * 0.1
        self.health = 1000000000000 #keys should be indestructible.
        super(Key, self).__init__(
            body, offset, rot, radius, mass, obj_id, img, load_from
        )
        self.label = "Key"
        self.uses_keys = False
        
        self.init_attr('number', number, load_from)
    

class Turret(Unit):
    def __init__(
                self, body, offset, rot, bullet_class, obj_id=0, 
                mass=0.0, load_from=None
            ):
        img = image_table[self.__class__.__name__]
        radius = img.height*0.45
        if mass == 0.0:
            mass = physics.default_mass*0.8
        super(Turret, self).__init__(
            body, offset, rot, radius, mass, obj_id, None, load_from
        )
        self.label = "Turret"
        self.uses_keys = True
        self.ask_key = True
        self.logic_req = 15
        self.line_length = img.width-radius*1.2
        self.bullet_class = bullet_class
        
        self.recoil_status = 0.0
        
        self.init_attr('recoil_status', 0.3, load_from)
    
    def activate(self):
        super(Turret, self).activate()
    
    def fire(self):
        self.recoil_status = self.recoil_time
        local_angle_rad = math.radians(self.local_angle)
        vx = math.cos(self.gluebody.body.angle - local_angle_rad)
        vy = math.sin(self.gluebody.body.angle - local_angle_rad)
        vx *= self.bullet_class.velocity
        vy *= self.bullet_class.velocity
        vx += self.gluebody.body.velocity.x
        vy += self.gluebody.body.velocity.y
        tx = math.cos(-local_angle_rad)
        ty = math.sin(-local_angle_rad)
        amt = max(self.radius*1.3, self.line_length+5)
        blx = self.offset[0] + tx*amt
        bly = self.offset[1] + ty*amt
        bx, by = self.gluebody.body.local_to_world((blx, bly))
        self.bullet_class(bx, by, vx, vy, level.batch, level.bullet_group)
    
    def update(self):
        super(Turret, self).update()
        if self.recoil_status > 0: self.recoil_status -= env.dt
        if self.active and self.recoil_status <= 0: self.fire()
    

class RapidTurret(Turret):
    def __init__(
                self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None
            ):
        super(RapidTurret, self).__init__(
            body, offset, rot, bullet.PlayerRapid, obj_id, 0.0, load_from
        )
        self.label = "Machine Gun"
        self.recoil_time = 0.2
        self.which_barrel = 0
        self.circle2_dist = self.line_length-3
        self.circle2_rad = 3
    
    def fire(self):
        super(RapidTurret, self).fire()
        sound.play(resources.fire_automatic_old)
        if self.which_barrel == 0:
            self.image = resources.turret2_anim_left
            self.which_barrel = 1
        else:
            self.image = resources.turret2_anim_right
            self.which_barrel = 0
    

class RapidTurret2(Turret):
    def __init__(
                self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None
            ):
        super(RapidTurret2, self).__init__(
            body, offset, rot, bullet.PlayerRapid2, obj_id, 0.0, load_from
        )
        self.label = "Laser Gun"
        self.recoil_time = 0.2
        self.which_barrel = 0
        self.circle2_dist = self.line_length-3
        self.circle2_rad = 3
    
    def fire(self):
        super(RapidTurret2, self).fire()
        sound.play(resources.laser_1)
        if self.which_barrel == 0:
            self.image = resources.turret2_R_anim_left
            self.which_barrel = 1
        else:
            self.image = resources.turret2_R_anim_right
            self.which_barrel = 0
    

class BlueTurret(Turret):
    def __init__(
                self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None
            ):
        super(BlueTurret, self).__init__(
            body, offset, rot, bullet.PlayerPlasmaBlue, obj_id, 0.0, load_from
        )
        self.label = "Blue Plasma Turret"
        self.recoil_time = 0.5
        self.circle2_rad = 3
        self.circle2_dist = 25
    
    def fire(self):
        super(BlueTurret, self).fire()
        sound.play(resources.laser_3)
    

class CannonTurret(Turret):
    def __init__(
                self, body=None, offset=(0,0), rot=0.0, obj_id=0, 
                mass=physics.default_mass*2, load_from=None
            ):
        self.health = physics.default_health*1.5
        super(CannonTurret, self).__init__(
            body, offset, rot, bullet.PlayerShell, obj_id, mass, load_from
        )
        self.label = "Cannon Turret"
        self.recoil_time = 0.8
        self.circle2_dist = self.line_length-3
        self.circle2_rad = 3
    
    def fire(self):
        super(CannonTurret, self).fire()
        sound.play(resources.fire_tank)
        self.image = resources.turret3_static
        self.image = resources.turret3_anim
    

class Beacon(Unit):
    def __init__(
                self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None
            ):
        super(Beacon, self).__init__(
            body, offset, rot, 0, 0, obj_id, None, load_from
        )
        self.label = "Beacon"
        self.uses_keys = False
        self.image_on = resources.beacon_anim
        self.image_off = resources.beacon_1
    
    def update(self):
        if self.active and (self.gluebody.body.velocity.x != 0 or \
                            self.gluebody.body.velocity.y != 0):
            self.gluebody.body.velocity = (0,0)
        if self.active and self.gluebody.body.angular_velocity != 0:
            self.gluebody.body.angular_velocity = 0
        super(Beacon, self).update()
    
    def activate(self):
        super(Beacon, self).activate()
        self.image = self.image_on
    
    def deactivate(self):
        super(Beacon, self).deactivate()
        self.image = self.image_off
    

class Toxin(Beacon):
    def __init__(
                self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None
            ):
        super(Toxin, self).__init__(body, offset, rot, obj_id, load_from)
        self.image_on = resources.toxin_anim
        self.image_off = resources.Harvester_1
    

class Thruster(Unit):
    def __init__(
                self, body=None, offset=(0,0), rot=0.0, obj_id=0, load_from=None
            ):
        self.health = physics.default_health*2
        super(Thruster, self).__init__(
            body, offset, rot, 0, 0, obj_id, None, load_from
        )
        self.label = "Thruster"
        self.uses_keys = True
        self.ask_key = True
        self.logic_req = 25
        self.line_length = -35
        self.circle2_rad = 5
        self.circle2_dist = -27
        
        self.subtract_amt = 1.0
        
        self.init_sound(resources.thrust_2, loop=True)
        
        self.flame_sprite = pyglet.sprite.Sprite(
            resources.engine_flame_1, self.x, self.y,
            batch=level.batch, group=level.decal_group
        )
        self.flame_sprite.visible = False
    
    def migrate(self):
        self.flame_sprite.batch = None
        self.flame_sprite.batch = level.batch
    
    def thrust(self, angle, force):
        impulse = ( force*env.dt*math.cos(angle+math.pi),
                    force*env.dt*math.sin(angle+math.pi))
        impulse_offset = (  self.position[0]-self.gluebody.body.position.x,
                            self.position[1]-self.gluebody.body.position.y)
        self.gluebody.body.apply_impulse(impulse, impulse_offset)
        env.enable_damping = False
    
    def update(self):
        super(Thruster,self).update()
        
        if self.active or self.active_timer:
            if self.subtract_amt > 0:
                self.subtract_amt -= env.dt*2
            angle = self.gluebody.body.angle - math.radians(self.local_angle)
            angle += math.pi
            self.thrust(angle, physics.default_thrust*(1.0-self.subtract_amt))
            
            self.flame_sprite.rotation = self.rotation+random.randint(-2,2)
            self.flame_sprite.x, self.flame_sprite.y = self.x, self.y
        
        if self.flame_sprite.visible:
            if not self.active and self.active_timer <= 0:
                self.flame_sprite.visible = False
                self.image = resources.thruster_off
    
    def activate(self):
        super(Thruster, self).activate()
        self.image = resources.thruster_active_anim
        self.flame_sprite.visible = True
        if env.enable_damping:
            self.subtract_amt = 1.0
        else:
            self.subtract_amt = 0.0
    
    def deactivate(self):
        super(Thruster, self).deactivate()
        if self.active_timer <= 0:
            self.image = resources.thruster_off
            self.flame_sprite.visible = False
    
