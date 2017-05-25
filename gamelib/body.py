import math, pymunk
from util import env, draw, serialize, sound
from util import particle, physics, resources
import unit
import event, level
#import sidebar
import pyglet.gl as gl

class GlueBody(object):
    def __init__(self, pos=(0.0,0.0), rot=0.0, child_units=[]):
        mass = 0.0
        inertia = 0.0
        self.units = []
        offset_r = 0.0
        
        for this_unit in child_units:
            offset_r = math.sqrt(this_unit.offset[0]**2+this_unit.offset[1]**2)
            mass += this_unit.mass
            inertia += pymunk.moment_for_circle(
                this_unit.mass, 0, this_unit.radius, this_unit.offset
            )
        
        self.body = pymunk.Body(mass, inertia)
        
        self.units = child_units
        for this_unit in self.units:
            this_unit.initialize(self,collision_type=physics.PLAYER)
            this_unit.add_shapes()
        
        physics.body_update_list.append(self)
        physics.unit_update_list.extend(self.units)
        physics.space.add(self.body)
        
        self.update_center_of_mass()
        self.body.angle = rot
        self.body.position = pos
        self.x, self.y = self.body.position.x, self.body.position.y
        self.angle_degrees = math.degrees(self.body.angle)
        self.to_acquire = []
        self.parent_units = []
        self.to_release = []
        
        self.attachable = False
        
        event.update_player_units(self.units)
    
    def get_yaml_object(self):
        unit_yaml_list = []
        for unit in self.units:
            unit_yaml_list.append(unit.get_dict())
        yaml_obj = serialize.YamlGlueBody(
            self.body.angle, 
            self.body.angular_velocity,
            self.attachable,
            self == level.player,
            (self.body.position.x, self.body.position.y),
            unit_yaml_list, 
            (self.body.velocity.x, self.body.velocity.y)
        )
        return yaml_obj
    
    def update(self):
        self.angle_degrees = math.degrees(self.body.angle)
        self.x, self.y = self.body.position.x, self.body.position.y
        edt = min(env.dt, 0.2)
        if env.enable_damping and edt < 0.2:
            self.body.angular_velocity *= (1.0-edt*6)
            self.body.velocity[0] *= (1.0-edt*5)
            self.body.velocity[1] *= (1.0-edt*5)
        else:
            self.body.angular_velocity *= (1.0-edt*3)
            self.body.velocity[0] *= (1.0-edt*1)
            self.body.velocity[1] *= (1.0-edt*1)
    
    def update_physics(self):
        for singlebody, parent_unit in zip(self.to_acquire, self.parent_units):
            self._acquire_singlebody_now(singlebody, parent_unit)
        for unit in self.to_release:
            self._release_unit_now(unit)
        if len(self.to_acquire):
            self.to_acquire = []
            self.parent_units = []
        if len(self.to_release): self.to_release = []
        
        self.check_death()
    
    def check_death(self):
        remove_list = []
        for unit in self.units:
            if unit.health <= 0:
                for unit2 in self.units:
                    if unit2.parent_unit == unit:
                        self.release_unit(unit2)
                unit.deactivate()
                physics.update_bodies_now = True
                env.unbind_keys_for_unit(unit)
                unit.die()
                remove_list.append(unit)
                sound.play(resources.expl_medium)
                particle.explode_medium(unit.x, unit.y)
        
        if self.units[0] in remove_list:
            for unit in self.units:
                unit.health = 0
                if unit.x != 0 or unit.y != 0:
                    particle.explode_medium(unit.x, unit.y)
         
        if len(remove_list) > 0: 
            for unit in remove_list:
                self.units.remove(unit)
            self.update_center_of_mass()
            
        if len(self.units) == 0:
            physics.body_update_list.remove(self)
            physics.space.remove(self.body)
            if self == level.player:
                level.restart_countdown = 3.0
                level.player = None
                sound.play(resources.expl_large)
    
    def update_center_of_mass(self):
        if len(self.units) == 0: return
        avg_x = 0.0
        avg_y = 0.0
        mass_total = 0.0
        inertia_total = 0.0
        
        for u in self.units:
            mass_total += u.mass
            inertia_total += pymunk.moment_for_circle(
                            u.mass, 0, u.radius, u.offset)
            avg_x += u.mass * u.offset[0]
            avg_y += u.mass * u.offset[1]
            #u.remove_shapes()
        avg_x /= mass_total
        avg_y /= mass_total
        new_body_position = self.body.local_to_world((avg_x,avg_y))
        
        self.body.position = new_body_position
        self.body.mass = mass_total
        self.body.moment = inertia_total
        
        for u in self.units:
            x, y = u.offset[0]-avg_x, u.offset[1]-avg_y
            u.set_offset(x,y)
            u.update_shapes()
            #u.initialize(self,collision_type=physics.PLAYER)
            #u.add_shapes()
    
    def update_center_of_mass_old(self):
        if len(self.units) == 0: return
        avg_x = 0.0
        avg_y = 0.0
        mass_total = 0.0
        inertia_total = 0.0
        
        for u in self.units:
            mass_total += u.mass
            inertia_total += pymunk.moment_for_circle(
                            u.mass, 0, u.radius, u.offset)
            avg_x += u.mass * u.offset[0]
            avg_y += u.mass * u.offset[1]
            u.remove_shapes()
        avg_x /= mass_total
        avg_y /= mass_total
        new_body_position = self.body.local_to_world((avg_x,avg_y))
        
        old_body = self.body
        physics.space.remove(old_body)
        
        self.body = pymunk.Body(mass_total, inertia_total)
        self.body.position = new_body_position
        self.body.velocity = old_body.velocity
        self.body.angular_velocity = old_body.angular_velocity
        self.body.angle = old_body.angle
        old_body = None
        
        physics.space.add(self.body)
        
        for u in self.units:
            x, y = u.offset[0]-avg_x, u.offset[1]-avg_y
            u.set_offset(x,y)
            u.initialize(self,collision_type=physics.PLAYER)
            u.add_shapes()
    
    def draw_at(self, x, y):
        draw.set_color(1,1,1,1)
        for unit in self.units:
            ix, iy = x-unit.offset[1], y+unit.offset[0]
            gl.glPushMatrix()
            gl.glTranslatef(ix,iy,0)
            gl.glRotatef(unit.local_angle-90,0,0,-1)
            unit.image.blit(0,0)
            gl.glPopMatrix()
    
    def get_bounding_rect(self):
        min_x = 0
        min_y = 0
        max_x = 0
        max_y = 0
        for unit in self.units:
            ix, iy = unit.offset
            ix, iy = -iy, ix
            if ix < min_x: min_x = ix
            if iy < min_y: min_y = iy
            if ix > max_x: max_x = ix
            if iy > max_y: max_y = iy
        return min_x-physics.default_radius, min_y-physics.default_radius, \
                max_x+physics.default_radius, max_y+physics.default_radius
    
    def acquire_singlebody(self, singlebody, parent_unit=None):
        if not singlebody in self.to_acquire:
            self.to_acquire.append(singlebody)
            self.parent_units.append(parent_unit)
    
    def _acquire_singlebody_now(self, singlebody, parent_unit):
        #Calculate the new velocity vector for the big body
        vx1, vy1 = self.body.velocity.x, self.body.velocity.y
        vx2, vy2 = singlebody.body.velocity.x, singlebody.body.velocity.y
        m1, m2 = self.body.mass, singlebody.body.mass
        vx3 = (m1*vx1+m2*vx2)/(m1+m2)
        vy3 = (m1*vy1+m2*vy2)/(m1+m2)
        
        #Find the body-local offset of the new unit
        new_offset = self.body.world_to_local(singlebody.body.position)
        #Define a shortcut to eliminate ambiguity
        new_unit = singlebody.unit
        new_unit.parent_unit = parent_unit
        
        #Kill the old body and shape
        physics.space.remove(singlebody.body)
        singlebody.unit.remove_shapes()
        physics.body_update_list.remove(singlebody)
        
        #Add the new unit to the big body
        self.units.append(new_unit)
        #Initialize it with the proper parent (big body)
        new_unit.initialize(self, collision_type=physics.PLAYER)
        new_unit.set_offset(new_offset.x,new_offset.y)
        #Give it the proper local rotation
        new_unit.local_angle = (new_unit.rotation+self.angle_degrees)
        new_unit.local_angle_target = new_unit.local_angle
        #Tell the physics engine about it
        new_unit.add_shapes()
        
        #Fix the big body
        self.update_center_of_mass()
        self.body.velocity=(vx3,vy3)
        
        if hasattr(singlebody.unit, 'obj_id'):
            if singlebody.unit.obj_id in event.attach_funcs.keys():
                for func in event.attach_funcs[singlebody.unit.obj_id]:
                    try:
                        func(singlebody.unit.obj_id)
                    except:
                        func()
        
        event.update_player_units(self.units)
        new_unit.attach()
        #sidebar.main.update()
    
    def release_unit(self, unit):
        if unit in self.units:
            self.to_release.append(unit)
            self.units.remove(unit)
            #Queue attached units for release
            for unit2 in self.units[:]:
                if unit2.parent_unit == unit:
                    self.release_unit(unit2)
    
    def _release_unit_now(self, unit):
        #Find the new body's global coordinates and rotation
        physics.unit_update_list.remove(unit)
        new_body_position = self.body.local_to_world(unit.circle.center)
        new_body_rotation = math.degrees(self.body.angle) - unit.local_angle
        
        angle_to_unit = self.body.angle
        angle_to_unit += math.atan2(unit.offset[1], unit.offset[0])
        extra_angle = angle_to_unit + math.pi/2
        extra = self.body.angular_velocity * math.sqrt(unit.offset_dist_sq)
        new_body_velocity = (
            self.body.velocity.x + extra * math.cos(extra_angle),
            self.body.velocity.y + extra * math.sin(extra_angle)
        )
        
        unit.remove_shapes()
        
        #Create a new body, pass it the unit
        new_body = SingleBody(new_body_position, new_body_rotation, unit)
        new_body.body.velocity = new_body_velocity
        new_body.body.angular_velocity = self.body.angular_velocity
        unit.parent = None
        if unit.active:
            unit.active_timer = 1.0
            unit.deactivate()
        unit.release()
        #Fix self
        self.update_center_of_mass()
        
        if hasattr(unit, 'obj_id'):
            if unit.obj_id in event.release_funcs.keys():
                for func in event.release_funcs[unit.obj_id]:
                    try:
                        func(unit.obj_id)
                    except TypeError:
                        func()
        
        event.update_player_units(self.units)
    
    def make_invisible(self):
        pass
    
    def make_visible(self):
        pass
    

class SingleBody(object):
    def __init__(self, pos, rot, child_unit):
        self.unit = child_unit
        self.obj_id = child_unit.obj_id
        inertia = pymunk.moment_for_circle(
            self.unit.mass, 0, self.unit.radius,(0,0)
        )
        
        self.body = pymunk.Body(self.unit.mass, inertia)
        self.unit.set_offset(0,0)
        self.unit.local_angle = 0
        self.unit.local_angle_target = 0
        self.unit.rotation = 0
        self.unit.initialize(self,collision_type=physics.FREE)
        
        self.body.angle = math.radians(rot)
        self.body.position = pos
        self.angle_degrees = rot
        
        self.attachable = True
        self.visible = True
        
        physics.body_update_list.append(self)
        physics.unit_update_list.append(self.unit)
        physics.space.add(self.body)
        self.unit.add_shapes()
    
    def get_yaml_object(self):
        yaml_obj = serialize.YamlSingleBody(
            self.body.angle,
            self.body.angular_velocity,
            self.attachable,
            (self.body.position.x, self.body.position.y),
            self.unit.get_dict(),
            (self.body.velocity.x, self.body.velocity.y), 
            self.visible
        )
        return yaml_obj
    
    def update(self):
        self.angle_degrees = math.degrees(self.body.angle)
        self.body.angular_velocity *= 0.93
        self.body.velocity[0] *= 0.97
        self.body.velocity[1] *= 0.97
    
    def update_physics(self):
        if self.unit.health <= 0:
            physics.body_update_list.remove(self)
            self.unit.die()
            physics.space.remove(self.body)
            sound.play(resources.expl_medium)
            particle.explode_medium(self.unit.x, self.unit.y)
            self.unit = None
            self.obj_id = 0
    
    def make_invisible(self):
        if not self.visible: return
        self.visible = False
        #physics.body_update_list.remove(self)
        physics.unit_update_list.remove(self.unit)
        self.unit.remove_shapes()
        self.unit.visible = False
        physics.space.remove(self.body)
    
    def make_visible(self):
        if self.visible: return
        self.visible = True
        #physics.body_update_list.append(self)
        physics.unit_update_list.append(self.unit)
        self.unit.add_shapes()
        self.unit.visible = True
        physics.space.add(self.body)
    

