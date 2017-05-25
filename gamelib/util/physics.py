import pyglet, math

import pymunk
import pymunk.util as util
from pymunk import Vec2d

WALL = 1
INVISIBLE = 2
PLAYER = 100
FREE = 101
ENEMY_STATIC = 102
PLAYER_BULLET = 200
ENEMY_BULLET = 201

default_radius = 23
default_density = 0.1
default_friction = 0.4
default_elasticity = 0.5
default_mass = default_density*(default_radius*default_radius*2*math.pi)
default_thrust = 300000.0
default_thrust = 800000.0

default_damage = 5
default_health = 50

frame_time = 0.0033
dt_backlog = 0.0
run_physics = True
update_bodies_now = False
gravity = (0.0,0.0)

space = None
static_body = None
body_update_list = []
unit_update_list = []
doors = []
bullet_deletion_queue = []

def init(step=5, run=True, grav=(0.0,0.0)):
    global frame_time, dt_backlog, run_physics, gravity, space
    global static_body, bodies, body_update_list, doors
    global unit_update_list, bullet_deletion_queue
    global update_bodies_now
    
    frame_time = 1.0/60.0/step
    dt_backlog = 0.0
    run_physics = run
    update_bodies_now = False
    gravity = grav
    
    pymunk.init_pymunk()
    space = pymunk.Space()
    space._space.contents.elasticIterations = 5
    space.gravity = Vec2d(grav)
    #space.resize_static_hash()
    #space.resize_active_hash()
    
    static_body = pymunk.Body(pymunk.inf, pymunk.inf)
    body_update_list = []
    unit_update_list = []
    doors = []
    bullet_deletion_queue = []

def pause():
    global run_physics
    run_physics = False

def unpause():
    global run_physics
    run_physics = True

def toggle_pause():
    global run_physics
    run_physics = not run_physics

def step(dt=0):    
    global dt_backlog, bullet_deletion_queue, update_bodies_now
    if not run_physics: return
    dt += dt_backlog
    if dt > 0.2: dt = 0.0
    while dt >= frame_time:
        space.step(frame_time)
        if update_bodies_now:
            for bullet in bullet_deletion_queue:
                try:
                    space.remove(bullet.body)
                    space.remove(bullet.shape)
                    body_update_list.remove(bullet)
                    bullet.delete()
                except:
                    pass
            bullet_deletion_queue = []
            for body in body_update_list:
                body.update_physics()
            update_bodies_now = False
        dt -= frame_time
    dt_backlog = dt