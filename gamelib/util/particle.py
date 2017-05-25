import math, random
import env, resources
from pyglet import gl

lepton_enabled = False
try:
    import lepton
    from lepton import controller, emitter, renderer
    lepton_enabled = True
except:
    lepton_enabled = False
    print "Lepton not available. Particle effects disabled."

t_color   = (1, 0.5, 0, 1)
t_col_dev = (0.02,0.02,0.02,0)
t_vel     = 50.0
t_vel_dev = (5,5,0)
t_size    = 15

smoke_trail_time = 0.15
smoke_trail_group = None

fire_big = None
fire_medium = None

class Renderer(object):
    """Renderer base class"""
    
    def draw(self):
        """Render the group's particles"""
        raise NotImplementedError
    

class BlitRenderer(Renderer):
    group = None
    def __init__(self, image):
        self.image = image
    
    def set_group(self, group):
        """Set the renderer's group"""
        if self.group is not None and self.group is not group:
            self.group.set_renderer(None)
        self.group = group
    
    def draw(self):
        for p in self.group:
            gl.glColor4f(*p.color)
            self.image.blit(p.position.x, p.position.y)
    

def fire_group(img):
    if lepton_enabled:
        return lepton.ParticleGroup(
            controllers=[
                controller.Lifetime(4),
                controller.Movement(damping=0.95),
                controller.Fader(
                    fade_in_start=0, start_alpha=0, fade_in_end=0.5,
                    max_alpha=0.4, fade_out_start=1.0, fade_out_end=4.0)
            ],
            renderer=BlitRenderer(img))
    else:
        return None

def init():
    global smoke_trail_group, fire_big, fire_medium
    
    if lepton_enabled:
        smoke_trail_group = lepton.ParticleGroup()
    
        point_renderer = renderer.PointRenderer(point_size=t_size)
        fader = controller.Fader(
            fade_in_end=0, max_alpha=1.0, fade_out_start=0, 
            fade_out_end=smoke_trail_time, end_alpha=0
        )
        lifetime = controller.Lifetime(smoke_trail_time)
    
        smoke_trail_group = lepton.ParticleGroup(
            controllers = [lifetime, fader, controller.Movement()],
            renderer = point_renderer)
    
        fire_big = fire_group(resources.puff)
        fire_medium = fire_group(resources.particle_faded_50)

def update():
    if lepton_enabled:
        lepton.default_system.update(env.dt)

def draw():
    if lepton_enabled:
        lepton.default_system.draw()
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE)
        fire_big.draw()
        fire_medium.draw()
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

def new_trail_emitter():
    if lepton_enabled:
        new_emitter = emitter.StaticEmitter(
            template=lepton.Particle(color=t_color),
            deviation=lepton.Particle(
                velocity=t_vel_dev, color=t_col_dev, age=1.5
            )
        )
        return new_emitter
    else:
        return None

def make_trail(particle_emitter, position, angle):
    if lepton_enabled:
        particle_emitter.template.position = (position)
        for i in xrange(3):
            v = t_vel * random.random()
            particle_emitter.template.velocity = (
                v*math.cos(angle), v*math.sin(angle),0
            )
            particle_emitter.emit(1, smoke_trail_group)

def explode_medium(x, y):
    if lepton_enabled:
        fire_emitter = emitter.StaticEmitter(
            template=lepton.Particle(
                position=(x,y,-10), 
                size=(20,20,0)),
            deviation=lepton.Particle(
                position=(5,5,2), 
                velocity=(80, 80, 20), 
                size=(5,5,0),
                up=(0,0,math.pi*2), 
                rotation=(0,0,math.pi*0.03),),
            color=[ (0.1,0.1,0.1), 
                    (0.5,0.5,0.0), 
                    (0.4,0.1,0.1), 
                    (0.5,0.2,0.0),
                    (0.5,0.5,0.5)],
        )
    
        fire_emitter.emit(40, fire_medium)

def explode_huge(x, y):
    if lepton_enabled:
        fire_emitter = emitter.StaticEmitter(
            template=lepton.Particle(
                position=(x,y,-10), 
                size=(20,20,0)),
            deviation=lepton.Particle(
                position=(30,30,2), 
                velocity=(130,130,20), 
                size=(5,5,0),
                up=(0,0,math.pi*2), 
                rotation=(0,0,math.pi*0.03),),
            color=[ (0.1,0.1,0.1), 
                    (0.5,0.5,0.0), 
                    (0.4,0.1,0.1), 
                    (0.5,0.2,0.0),
                    (0.5,0.5,0.5)],
        )
    
        fire_emitter.emit(30, fire_big)
