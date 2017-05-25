import pyglet
from util import env, physics, resources
import level

class TNT(pyglet.sprite.Sprite):
    def __init__(self, x, y, rot):
        super(TNT, self).__init__(resources.tnt, x, y, 
                    batch=level.batch, group=level.floor_group)
        self.rotation = rot
        physics.body_update_list.append(self)
    
    def update(self):
        if (self.x-level.player.x)*(self.x-level.player.x) + \
                (self.y-level.player.y)*(self.y-level.player.y) \
                > env.norm_w*env.norm_w*2/4:
            for body in physics.body_update_list:
                if hasattr(body, 'x'):
                    if (body.x-self.x)*(body.x-self.x) + \
                        (body.y-self.y)*(body.y-self.y) < 400*400:
                        if hasattr(body, 'explode'):
                            body.explode()
            sound.play(resources.expl_huge)                
            resources.expl_large.play()
            physics.body_update_list.remove(self)
            self.delete()
    
    def update_physics(self):
        pass
    
