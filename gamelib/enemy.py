import pyglet, math, pymunk
from util import draw, env, particle, physics
from util import resources, sound, serialize
import level, unit, bullet, event

def get_target(x, y, target):
    d1 = (x-target.x)*(x-target.x) + (y-target.y)*(y-target.y)
    d2 = (x-level.decoy_x)*(x-level.decoy_x) + \
            (y-level.decoy_y)*(y-level.decoy_y)
    if d1 < d2 or not level.decoy_present:
        return target.x, target.y, d1
    else:
        return level.decoy_x, level.decoy_y, d2

class Turret(pyglet.sprite.Sprite):
    def __init__(
                self, img, unit_class, x, y, rotation, bullet_class, obj_id=0,
                base_img=None, base_rotation=0.0
            ):
        if base_img != None:
            self.base_sprite = pyglet.sprite.Sprite(
                base_img, x, y, 
                batch=level.batch, group=level.tank_group
            )
            self.base_sprite.rotation = base_rotation
        else:
            self.base_sprite = None
        super(Turret, self).__init__(
            img, x, y, batch=level.batch, group=level.bullet_group #stupid
        )
        
        self.turret_type = "Untyped"
        
        self.unit_class = unit_class
        self.bullet_class = bullet_class
        self.rotation = rotation
        self.obj_id = obj_id
        self.radius = img.height*0.45
        self.line_length = img.width-self.radius*1.2
        
        self.init_physics()
        
        physics.body_update_list.append(self)
        
        self.rotate_speed = 20.0
        self.should_dislodge = False
        self.dislodge_momentum = 4000
        self.recoil_time = 0.7
        self.recoil_status = 0.0
        self.range_sq = 263000
        #self.range_sq = 150000
        if not hasattr(self, 'health'):
            self.health = physics.default_health*0.6
        self.health_full = self.health
        self.targeting = False
        self.on_target = False
        self.alive = True
        self.active = True
        self.visible = True
        
        self.can_dislodge = True
        if base_img != None and base_img.instance_name == "Tower1_Static":
            self.can_dislodge = False
        
        self.target = None
        
        self.update_segment()
    
    def init_physics(self):
        self.body = pymunk.Body(pymunk.inf, pymunk.inf)
        self.body.position = (self.x, self.y)
        self.body.angle = -math.radians(self.rotation)
        
        self.circle = pymunk.Circle(self.body, self.radius, (0, 0))
        self.circle.friction = physics.default_friction
        self.circle.elasticity = physics.default_elasticity
        self.circle.collision_type = physics.ENEMY_STATIC
        self.circle.layers = 1
        self.circle.parent = self
        physics.space.add(self.circle)
        
        self.segment = pymunk.Segment(
            self.body, (0,0), (self.line_length, 0), 1
        )
        self.segment.collision_type = physics.ENEMY_STATIC
        self.segment.layers = 1
        self.segment.parent = self
        physics.space.add(self.segment)
    
    def get_yaml_object(self, from_tank=False):
        if not from_tank and self.base_sprite == None: return None
        if from_tank and self.base_sprite == None:
            bt = 'Tank'
            br = 0.0
        else:
            bt = self.base_sprite.image.instance_name
            br = self.base_sprite.rotation
        if hasattr(self.target, 'obj_id'):
            targ = self.target.obj_id
        else:
            targ = 0
        yaml_obj = serialize.YamlTurret(
            active = self.active,
            alive = self.alive,
            angle = -math.degrees(self.body.angle),
            base_type = bt,
            base_rotation = br,
            health = self.health,
            obj_id = self.obj_id,
            on_target = self.on_target,
            position = (self.body.position.x, self.body.position.y),
            recoil_status = self.recoil_status,
            target = targ,
            targeting = self.targeting,
            turret_type = self.turret_type,
            visible = self.visible
        )
        return yaml_obj
    
    def update_segment(self):
        a = -math.radians(self.rotation)
        self.body.angle = a
    
    def move_to(self, x, y):
        if self == None or self._texture == None:
            print 'something strange happened with turrets.'
            return
        self.x, self.y = x, y
        self.body.position = (x, y)
    
    def update(self):    
        if self == None or not self.alive: return
        if self.target == None:
            if level.player != None:
                self.target = level.player
            else:
                return
        if self.target == None or not self.active: return
        if self.recoil_status > 0: self.recoil_status -= env.dt
        tx, ty, d_sq = get_target(self.x, self.y, self.target)
        if self.target == level.player and d_sq > self.range_sq*3:
            self.targeting = False
            return
        self.targeting = True
        a2p = -math.degrees(math.atan2(ty-self.y, tx-self.x))
        da = (a2p - self.rotation) % 360
        move_max = self.rotate_speed * env.dt
        if da <= move_max or da >= 360-move_max:
            self.rotation = a2p
            self.update_segment()
        elif da < 180:
            self.rotation += move_max
            self.update_segment()
        else:
            self.rotation -= move_max
            self.update_segment()
        da = min(da, 360-da)
        if da < 20:
            self.on_target = True
        else:
            self.on_target = False
        if d_sq <= self.range_sq and da < 10:
            self.fire()
    
    def update_physics(self):
        if not self.alive: return
        if self.should_dislodge and self.health > 0: self.dislodge()
        if self.health <= 0:
            physics.update_bodies_now = True
            try:
                physics.body_update_list.remove(self)
            except:
                print 'Attempted update remove in turret, was already gone.'
                return
            physics.space.remove(self.circle)
            physics.space.remove(self.segment)
            sound.play(resources.expl_medium)
            particle.explode_medium(self.x, self.y)
            if event.destroy_funcs.has_key(self.obj_id):
                for func in event.destroy_funcs[self.obj_id]:
                    result = func()
            if self.base_sprite != None:
                level.decals.append(
                    level.Decal(self.base_sprite.image, self.x, self.y, self.base_sprite.rotation)
                )
                self.base_sprite.delete()
            self.visible = False
            self.alive = False
    
    def spawn_bullet(self, offset=(0,0)):
        if self.recoil_status > 0: return False
        self.recoil_status = self.recoil_time
        mx = math.cos(math.radians(-self.rotation))
        my = math.sin(math.radians(-self.rotation))
        amt = max(self.radius*1.3, self.line_length-1)
        px = self.x + offset[0] + mx*amt
        py = self.y + offset[1] + my*amt
        vx = mx*self.bullet_class.velocity
        vy = my*self.bullet_class.velocity
        self.bullet_class(px, py, vx, vy, level.batch, level.bullet_group)
        return True
    
    def handle_collision(self, other_unit):    
        if not self.can_dislodge: return True
        other_body = other_unit.gluebody
        angle_to_unit = other_body.body.angle
        angle_to_unit += math.atan2(
            other_unit.offset[1], other_unit.offset[0]
        )
        extra_angle = angle_to_unit + math.pi/2
        extra = other_body.body.angular_velocity * \
                math.sqrt(other_unit.offset_dist_sq)
        velocity = (
            other_body.body.velocity.x + extra * math.cos(extra_angle),
            other_body.body.velocity.y + extra * math.sin(extra_angle)
        )
        total_velocity = velocity[0]*velocity[0]+velocity[1]*velocity[1]
        mass = sum([u.mass for u in other_body.units])
        momentum = mass*total_velocity*total_velocity/10**10
        if momentum > self.dislodge_momentum:
            other_unit.health -= physics.default_health*0.9
            self.health -= self.health_full*0.8
            self.should_dislodge = True
            physics.update_bodies_now = True
            other_body.body.velocity.x *= 0.3
            other_body.body.velocity.y *= 0.3
            return False
        return True
    
    def dislodge(self):
        physics.space.remove(self.circle)
        physics.space.remove(self.segment)
        physics.body_update_list.remove(self)
        self.alive = False
        new_obj = level.add_free_object(
            self.unit_class, self.x, self.y, -self.rotation, self.obj_id
        )
        new_obj.health = new_obj.health_full*0.2
        sound.play(resources.turret_rip)
        if event.destroy_funcs.has_key(self.obj_id):
            for func in event.destroy_funcs[self.obj_id]:
                result = func()
        self.delete()
    
    def draw_collisions(self):
        x1, y1 = self.body.local_to_world(self.segment.a)
        x2, y2 = self.body.local_to_world(self.segment.b)
        draw.line(x1, y1, x2, y2)
        r = self.circle.radius
        x, y = self.body.local_to_world(self.circle.center)
        draw.ellipse_outline(x-r, y-r, x+r, y+r)
    
    def make_invisible(self):
        if not self.visible: return
        self.visible = False
        self.active = False
        physics.space.remove(self.circle)
        physics.space.remove(self.segment)
    
    def make_visible(self):
        if self.visible: return
        self.visible = True
        self.active = True
        physics.space.add(self.circle)
        physics.space.add(self.segment)
    

class BluePlasmaTurret(Turret):
    def __init__(self, x, y, rotation, obj_id=0, base_img=None,
                base_rotation=0.0
            ):
        img = resources.turret1_blue
        super(BluePlasmaTurret, self).__init__(
            resources.turret1_blue, unit.BlueTurret, x, y, 
            rotation, bullet.EnemyPlasmaBlue, obj_id, base_img, base_rotation
        )
        
        self.turret_type = "Blue Plasma"
    
    def fire(self):
        fired = super(BluePlasmaTurret, self).spawn_bullet()
        if fired: sound.play(resources.laser_3)
    

class OrangePlasmaTurret(Turret):
    def __init__(self, x, y, rotation, obj_id=0, base_img=None,
                base_rotation=0.0
            ):
        img = resources.turret1_blue
        super(OrangePlasmaTurret, self).__init__(
            resources.turret1_orange, unit.BlueTurret, x, y, 
            rotation, bullet.EnemyPlasmaBlue, obj_id, base_img, base_rotation
        )
        
        self.turret_type = "Orange Plasma"
    
    def fire(self):
        fired = super(OrangePlasmaTurret, self).spawn_bullet()
        if fired: sound.play(resources.laser_3)
    

class CannonTurret(Turret):
    def __init__(self, x, y, rotation, obj_id=0, base_img=None,
                base_rotation=0.0
            ):
        img = resources.turret1_blue
        self.health = physics.default_health
        super(CannonTurret, self).__init__(
            resources.turret3_static, unit.CannonTurret, x, y, 
            rotation, bullet.EnemyShell, obj_id, base_img, base_rotation
        )
        
        self.turret_type = "Cannon"
        self.recoil_time = 0.8
        self.dislodge_momentum = 3000
    
    def fire(self):
        fired = super(CannonTurret, self).spawn_bullet()
        if fired:
            sound.play(resources.fire_tank)
            self.image = resources.turret3_static
            self.image = resources.turret3_anim
    

class FixedRapidTurret(Turret):
    def __init__(self, x, y, rotation, obj_id=0, base_img=None,
                base_rotation=0.0
            ):
        img = resources.turret2_static
        super(FixedRapidTurret, self).__init__(
            resources.turret2_static, unit.RapidTurret, x, y, 
            rotation, bullet.EnemyRapid, obj_id, base_img, base_rotation
        )
        
        self.turret_type = "Fixed Rapid"
        
        self.rotate_speed = 40.0
        self.recoil_time = 0.2
        self.which_barrel = 0
    
    def fire(self):
        if self.which_barrel == 0:
            offset = (
                math.cos(-self.body.angle)*3,
                math.sin(-self.body.angle)*3
            )
        else:
            offset = (
                math.cos(-self.body.angle)*-6,
                math.sin(-self.body.angle)*-6
            )
        fired = super(FixedRapidTurret, self).spawn_bullet(offset)
        if fired:
            sound.play(resources.fire_automatic_old)
            if self.which_barrel == 0:
                self.image = resources.turret2_anim_left
                self.which_barrel = 1
            else:
                self.image = resources.turret2_anim_right
                self.which_barrel = 0


class FixedRapidTurret2(Turret):
    def __init__(self, x, y, rotation, obj_id=0, base_img=None,
                base_rotation=0.0
            ):
        img = resources.turret2_R_static
        super(FixedRapidTurret2, self).__init__(
            resources.turret2_R_static, unit.RapidTurret2, x, y, 
            rotation, bullet.EnemyRapid2, obj_id, base_img, base_rotation
        )
        
        self.turret_type = "Fixed Rapid 2"
        
        self.rotate_speed = 40.0
        self.recoil_time = 0.2
        self.which_barrel = 0
    
    def fire(self):
        if self.which_barrel == 0:
            offset = (
                math.cos(-self.body.angle)*3,
                math.sin(-self.body.angle)*3
            )
        else:
            offset = (
                math.cos(-self.body.angle)*-6,
                math.sin(-self.body.angle)*-6
            )
        fired = super(FixedRapidTurret2, self).spawn_bullet(offset)
        if fired:
            sound.play(resources.laser_1)
            if self.which_barrel == 0:
                self.image = resources.turret2_R_anim_left
                self.which_barrel = 1
            else:
                self.image = resources.turret2_R_anim_right
                self.which_barrel = 0
    

class Tank(object):
    def __init__(
                self, x, y, rotation, obj_id, turret=None
            ):
        self.x = x
        self.y = y
        self.rotation = rotation
        self.obj_id = obj_id
        self.sprite_center = pyglet.sprite.Sprite(
            resources.tankbody, x=x, y=y, 
            batch=level.batch, group=level.tank_group
        )
        self.sprite_center.scale = 0.9
        self.sprite_left = pyglet.sprite.Sprite(
            resources.tank_left_1, x=x, y=y, 
            batch=level.batch, group=level.tank_group
        )
        self.sprite_right = pyglet.sprite.Sprite(
            resources.tank_right_1, x=x, y=y, 
            batch=level.batch, group=level.tank_group
        )
        self.sprite_left.rotation = self.rotation
        self.sprite_right.rotation = self.rotation
        self.sprite_center.rotation = self.rotation
        
        radius = resources.tankbody.height*0.6
        mass = physics.default_mass
        inertia = pymunk.moment_for_circle(mass, 0, radius, (17,-5))
        self.body = pymunk.Body(mass, inertia)
        self.body.position = (x, y)
        self.circle = pymunk.Circle(self.body, radius, (17,0))
        self.circle.parent = self
        self.circle.collision_type = physics.WALL
        self.circle.obj_id = self.obj_id
        self.circle.layers = 4
        physics.space.add(self.body)
        physics.space.add(self.circle)
        
        physics.body_update_list.append(self)
        
        self.turret = turret
        
        self.move_speed = 50.0
        if self.turret != None:
            self.rotate_speed = self.turret.rotate_speed*0.8
            self.move_speed = 3.1 * self.rotate_speed
            self.alive = True
        else:
            self.rotate_speed = 0
            self.lose_turret()
        self.turn_state = 0
        
        self.visible = True
    
    def get_yaml_object(self):
        if self.turret != None:
            t = self.turret.get_yaml_object(from_tank=True)
        else:
            t = None
        if self.turret != None and hasattr(self.turret.target, 'obj_id'):
            targ = self.turret.target.obj_id
        else:
            targ = 0
        yaml_obj = serialize.YamlTank(
            alive = self.alive,
            obj_id = self.obj_id,
            position = (self.x, self.y),
            rotation = self.rotation,
            target = targ,
            turn_state = self.turn_state,
            turret = t,
            visible = self.visible
        )
        return yaml_obj
    
    def update(self):
        if not self.visible: return
        self.body.angular_velocity = 0
        if self.turret == None or not self.alive \
                or not self.turret.active or not self.turret.alive \
                or not self.visible or not self.turret.visible:
            if self.turret == None or not self.turret.alive:
                self.lose_turret()
            return
        self.x, self.y = self.body.position
        if self.body.velocity.x != 0 or self.body.velocity.y != 0:
            self.sprite_left.x, self.sprite_left.y = self.x, self.y
            self.sprite_right.x, self.sprite_right.y = self.x, self.y
            self.sprite_center.x, self.sprite_center.y = self.x, self.y
            self.turret.move_to(self.x, self.y)
        
        if self.turret.target == None:
            self.body.velocity = (0,0)
            if self.sprite_left.image != resources.tank_left_1:
                self.sprite_left.image = resources.tank_left_1
            if self.sprite_right.image != resources.tank_right_1:
                self.sprite_right.image = resources.tank_right_1
            return
        
        if self.turret.health <= 0 or not self.turret.alive:
            self.lose_turret()
            return
        
        self.body.angle = -math.radians(self.rotation)    
        
        tx, ty, tdist = get_target(self.x, self.y, self.turret.target)
        if self.turret.target == level.player and tdist > self.turret.range_sq*5 \
                or (tdist < 200*200 and tdist > 150*150):
            self.body.velocity = (0,0)
            if self.turn_state != 0:
                self.turn_state = 0
                self.sprite_left.image = resources.tank_left_1
                self.sprite_right.image = resources.tank_right_1
            return
            
        da = (self.rotation - self.turret.rotation) % 360
        move_max = self.rotate_speed * env.dt
        if min(da, 360-da) <= move_max:
            self.rotation = self.turret.rotation
        elif da < 180:
            self.rotation -= move_max
        else:
            self.rotation += move_max
        
        self.set_sprite_images(da, move_max)
        self.sprite_left.rotation = self.rotation
        self.sprite_right.rotation = self.rotation
        self.sprite_center.rotation = self.rotation
        if (self.turret.target != level.player or abs(da) <= move_max*3) and self.turret.on_target:
            vx = math.cos(self.body.angle)*self.move_speed
            vy = math.sin(self.body.angle)*self.move_speed
            if tdist > 200*200:
                self.body.velocity = (vx, vy)
            else:
                self.body.velocity = (-vx, -vy)
        else:
            self.body.velocity = (0,0)
            self.sprite_left.image = resources.tank_left_1
            self.sprite_right.image = resources.tank_right_1
    
    def set_sprite_images(self, da, move_max):
        if abs(da) <= move_max*3 and self.turret.on_target:
            if self.turn_state != 1:
                self.turn_state = 1
                self.sprite_left.image = resources.tank_left_forward
                self.sprite_right.image = resources.tank_right_forward
                return
        elif da > 0:
            if self.turn_state != 2:
                self.turn_state = 2
                self.sprite_left.image = resources.tank_left_forward
                self.sprite_right.image = resources.tank_right_backward
                return
        elif da < 0:
            if self.turn_state != 3:
                self.turn_state = 3
                self.sprite_left.image = resources.tank_left_backward
                self.sprite_right.image = resources.tank_right_forward
                return
    
    def lose_turret(self):
        self.x, self.y = self.body.position
        self.body.velocity = (0,0)
        self.turret = None
        #self.sprite_left.image = resources.tank_left_1
        #self.sprite_right.image = resources.tank_right_1
        self.alive = False
        #physics.space.remove(self.circle)
        #physics.space.remove(self.body)
        physics.body_update_list.remove(self)
        level.decals.append(
            level.Decal(resources.tank_dead, self.x, self.y, self.rotation)
        )
        self.sprite_left.delete()
        self.sprite_right.delete()
        self.sprite_center.delete()
    
    def update_physics(self):
        pass
    
    def draw_collisions(self):
        x, y = self.body.local_to_world(self.circle.center)
        r = self.circle.radius
        draw.ellipse_outline(x-r, y-r, x+r, y+r)
    
    def make_invisible(self):
        if not self.visible: return
        self.visible = False
        self.sprite_left.visible = False
        self.sprite_right.visible = False
        self.sprite_center.visible = False
        self.active = False
        self.turret.make_invisible()
    
    def make_visible(self):
        if self.visible: return
        self.visible = True
        self.sprite_left.visible = True
        self.sprite_right.visible = True
        self.sprite_center.visible = True
        self.active = True
        self.turret.make_visible()
    
