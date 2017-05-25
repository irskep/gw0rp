import pyglet, math, pymunk
from util import physics, resources

class Bullet(pyglet.sprite.Sprite):
    velocity = 700.0
    def __init__(
                self, col_type, img, damage, 
                x, y, vx, vy, rotate=False, batch=None, group=None
            ):
        super(Bullet, self).__init__(img, x, y, batch=batch, group=group)
        self.damage = damage
        
        if rotate:
            self.rotation = math.degrees(-math.atan2(vy, vx))
        
        radius = 4
        mass = physics.default_density*(radius*radius*2*math.pi)
        inertia = pymunk.moment_for_circle(mass, 0, radius, (0,0))
        self.body = pymunk.Body(mass, inertia)
        self.body.position = (x,y)
        self.body.velocity = (vx, vy)
        
        self.shape = pymunk.Circle(self.body, radius, (0,0))
        self.shape.friction = 1.0
        self.shape.elasticity = 0.0
        self.shape.parent = self
        self.shape.collision_type = col_type
        self.shape.layers = 1
        
        physics.space.add(self.body)
        physics.space.add(self.shape)
        
        physics.body_update_list.append(self)
    
    def update(self):
        self.x = self.body.position.x
        self.y = self.body.position.y
    
    def update_physics(self):
        pass
    

class EnemyPlasmaBlue(Bullet):
    velocity  = 700
    def __init__(self, x, y, vx, vy, batch=None, group=None):
        super(EnemyPlasmaBlue, self).__init__(
            physics.ENEMY_BULLET, resources.bullet_blue, 10, 
            x, y, vx, vy, False, batch, group
        )
    

class PlayerPlasmaBlue(Bullet):
    velocity = 700
    def __init__(self, x, y, vx, vy, batch=None, group=None):
        super(PlayerPlasmaBlue, self).__init__(
            physics.PLAYER_BULLET, resources.bullet_blue, 10, 
            x, y, vx, vy, False, batch, group
        )
    

class EnemyRapid(Bullet):
    velocity  = 1200
    def __init__(self, x, y, vx, vy, batch=None, group=None):
        super(EnemyRapid, self).__init__(
            physics.ENEMY_BULLET, resources.bullet_long, 2, 
            x, y, vx, vy, True, batch, group
        )
    

class PlayerRapid(Bullet):
    velocity  = 1200
    def __init__(self, x, y, vx, vy, batch=None, group=None):
        super(PlayerRapid, self).__init__(
            physics.PLAYER_BULLET, resources.bullet_long, 2, 
            x, y, vx, vy, True, batch, group
        )


class EnemyRapid2(Bullet):
    velocity  = 1600
    def __init__(self, x, y, vx, vy, batch=None, group=None):
        super(EnemyRapid2, self).__init__(
            physics.ENEMY_BULLET, resources.bullet_long_red, 8, 
            x, y, vx, vy, True, batch, group
        )


class PlayerRapid2(Bullet):
    velocity  = 1600
    def __init__(self, x, y, vx, vy, batch=None, group=None):
        super(PlayerRapid2, self).__init__(
            physics.PLAYER_BULLET, resources.bullet_long_red, 8, 
            x, y, vx, vy, True, batch, group
        )


class EnemyShell(Bullet):
    velocity  = 500
    def __init__(self, x, y, vx, vy, batch=None, group=None):
        super(EnemyShell, self).__init__(
            physics.ENEMY_BULLET, resources.bullet_big, 40, 
            x, y, vx, vy, True, batch, group
        )


class PlayerShell(Bullet):
    velocity  = 500
    def __init__(self, x, y, vx, vy, batch=None, group=None):
        super(PlayerShell, self).__init__(
            physics.PLAYER_BULLET, resources.bullet_big, 40, 
            x, y, vx, vy, True, batch, group
        )
