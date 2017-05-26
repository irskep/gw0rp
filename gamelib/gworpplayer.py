import os, math, random, pyglet, pymunk

from util import draw, env, gui, keychooser, music, particle, physics, save
from util import resources, sound, timer, settings, cutscene, serialize
import unit, body, obstacle
import event, level, pausescreen

from pyglet.window import key
from pyglet import gl
from collections import defaultdict

PLAYING     = 0
PAUSED      = 1
CHOOSE_KEY  = 2
CUTSCENE    = 3

debug_draw = False

class GworpPlayer():
    def __init__(self, parent):
        self.parent = parent
        self.fps_display = pyglet.clock.ClockDisplay()
        self.keys = key.KeyStateHandler()
        env.main_window.push_handlers(self)
        env.main_window.push_handlers(self.keys)

        self.message_label = pyglet.text.Label("",
            font_name="Gill Sans", font_size=36,
            x=env.norm_w/2, y=env.norm_h//4*3,
            anchor_x='center', anchor_y='center',
            color=(255,255,255,255)
        )

        self.ai_message_label = pyglet.text.Label("",
            font_name="Gill Sans", font_size=14,
            x=env.norm_w//8+80, y=90,
            anchor_x='left', anchor_y='top',
            multiline=True,
            width=env.norm_w//4*3-80,
            color=(255,255,255,255)
        )

        self.timer_label = pyglet.text.Label(
            "", font_name="Gill Sans", font_size=64,
            x=5, y=env.norm_h+5, anchor_x='left', anchor_y='top',
            color=(0, 255, 0, 200)
        )

        self.loading = False
        pyglet.clock.schedule(self.on_draw)

    def clean_up(self):
        if self.mode == PAUSED:
            gui.next_card = gui.cards['title']
            gui.transition_time = 0.5
        self.clean_up_game()
        for unit in physics.unit_update_list:
            del unit
        for body in physics.body_update_list:
            del body
        env.main_window.pop_handlers()
        env.main_window.pop_handlers()
        pyglet.clock.unschedule(self.on_draw)
        env.main_window.set_mouse_visible(True)
        if event.next_level == 'win':
            gui.current_card = gui.cards['credits']
            gui.last_card = gui.cards['title']
            gui.transition_time = 0.5

    def clean_up_game(self):
        for unit in physics.unit_update_list:
            unit.deactivate()

    def init_pre_load(self, keep_keys=False):
        self.loading = True
        for u in physics.unit_update_list:
            u.deactivate()
        env.main_window.set_mouse_visible(False)
        physics.init()
        if not keep_keys:
            env.init()
        event.init()

    def init_post_load(self):
        self.current_level = level.current_level
        self.init_collision_funcs()

        gui.current_card = None
        env.camera_x = level.player.body.position.x
        env.camera_y = level.player.body.position.y

        self.mode = PLAYING
        self.collided_last = []
        self.current_message = ""
        self.current_ai_message = ""

        self.collide_sound_delay = 0
        self.flip = 0

        self.arrow_sprite = pyglet.sprite.Sprite(resources.dest_arrow, 0, 0)
        self.arrow_sprite.visible = False
        self.fade_countdown = 0.5
        self.loading = False

    def init_game(self, level_name, keep_config=False, keep_velocity=False):
        self.init_pre_load(keep_config)
        level.load(level_name, keep_config, keep_velocity)
        self.init_post_load()
        level.save()

    def init_from_save(self, path, keep_config=False, keep_velocity=False):
        self.init_pre_load(keep_config)
        level.load_save_from_path(path, keep_config, keep_velocity)
        self.init_post_load()
        level.save()

    def init_collision_funcs(self):
        #shortcut
        acpf = physics.space.add_collisionpair_func

        #player
        acpf(physics.PLAYER, physics.FREE, self.collide_player_free)
        acpf(physics.PLAYER, physics.WALL, self.collide_player_wall)
        acpf(physics.PLAYER, physics.ENEMY_STATIC, self.collide_player_static)
        acpf(physics.PLAYER, physics.INVISIBLE, self.collide_player_invisible)

        #player bullets
        acpf(physics.PLAYER_BULLET, physics.WALL, self.collide_bullet_silent)
        acpf(physics.PLAYER_BULLET, physics.FREE, self.collide_bullet_with_sound)
        acpf(physics.PLAYER_BULLET, physics.ENEMY_STATIC, self.collide_bullet_with_sound)
        acpf(physics.PLAYER_BULLET, physics.PLAYER, self.collide_default)

        #enemy bullets
        acpf(physics.ENEMY_BULLET, physics.WALL, self.collide_bullet_silent)
        acpf(physics.ENEMY_BULLET, physics.FREE, self.collide_bullet_with_sound)
        acpf(physics.ENEMY_BULLET, physics.PLAYER, self.collide_bullet_with_sound)
        acpf(physics.ENEMY_BULLET, physics.ENEMY_STATIC, self.collide_default)

        acpf(physics.PLAYER_BULLET, physics.ENEMY_BULLET, self.collide_default)

        #ignore invisibles, except player
        acpf(physics.FREE, physics.INVISIBLE, self.collide_default)
        acpf(physics.ENEMY_STATIC, physics.INVISIBLE, self.collide_default)
        acpf(physics.WALL, physics.INVISIBLE, self.collide_default)
        acpf(physics.PLAYER_BULLET, physics.INVISIBLE, self.collide_default)
        acpf(physics.ENEMY_BULLET, physics.INVISIBLE, self.collide_default)

    def on_draw(self,dt=0):
        if env.profiler != None:
            env.profiler.enable()

        #Make dt global
        env.dt = dt
        #Update physics if not paused
        if self.mode == PLAYING and not self.loading:
            level.decoy_present = False
            physics.step(dt)
        #Update particle system
        particle.update()
        #Update message queue
        if self.mode == PLAYING: event.update(dt)
        #Update camera position
        self.move_camera(dt)

        if self.mode == PLAYING:
            for obj in physics.body_update_list:
                obj.update_physics()
                obj.update()
            env.enable_damping = True
            for this_unit in physics.unit_update_list:
                this_unit.update()
            particle.update()

        #Do some fancy-pants OpenGL stuff
        gl.glLoadIdentity()
        if env.scale_factor != 1.0:
            gl.glPushMatrix()
            env.scale()

        gl.glPushMatrix()
        env.apply_camera()
        if event.quake_level > 0.0:
            quake_x = random.random()*10.0*event.quake_level*2.0
            quake_x -= 10*event.quake_level
            quake_y = random.random()*10.0*event.quake_level*2.0
            quake_y -= 10*event.quake_level
            gl.glTranslatef(quake_x,quake_y,0)

        if self.mode == PLAYING:

            self.draw_level()

            gl.glPopMatrix()

            if event.point_object != None:
                self.draw_pointer()
            else:
                if self.arrow_sprite.visible:
                    self.arrow_sprite.visible = False

            if event.message_countdown > 0: self.draw_message()
            if event.ai_message_countdown > 0: self.draw_ai_message()
            if event.active_countdown > 0: self.draw_countdown()

            self.fps_display.draw()
            if self.fade_countdown > 0:
                draw.set_color(1,1,1,self.fade_countdown/0.5)
                draw.rect(0, 0, env.norm_w, env.norm_h)
                self.fade_countdown -= dt
                if self.fade_countdown < 0:
                    self.fade_countdown = 0
            if self.mode == PLAYING and (event.fade_out_countdown != -100 or event.stay_black):
                draw.set_color(0, 0, 0, min(1, event.fade_out_countdown*2))
                if event.stay_black:
                    draw.set_color(0,0,0,1)
                draw.rect(0, 0, env.norm_w, env.norm_h)

        else:
            gl.glPopMatrix()
            gui.draw_card()

        if env.scale_factor != 1.0:
            gl.glPopMatrix()

        if self.collide_sound_delay > 0: self.collide_sound_delay -= 1
        self.check_mode_change()
        if env.profiler != None:
            env.profiler.disable()

    def move_camera(self, dt=0):
        if level.player == None: return
        env.camera_target_x = level.player.body.position.x
        env.camera_target_y = level.player.body.position.y
        env.cvx = abs(level.player.body.velocity.x * dt)
        env.cvy = abs(level.player.body.velocity.y * dt)
        env.move_camera(level.player.x, level.player.y)
        env.camera_x = max(env.camera_x, env.norm_w/2)
        env.camera_y = max(env.camera_y, env.norm_h/2)
        env.camera_x = min(env.camera_x, level.width-env.norm_w/2)
        env.camera_y = min(env.camera_y, level.height-env.norm_h/2)
        if level.width < env.norm_w:
            env.camera_x += env.norm_w/2-level.width/2
        if level.height < env.norm_h:
            env.camera_y += env.norm_h/2-level.height/2

    def draw_level(self):
        draw.clear(0,0,0,1)
        draw.set_color(1,1,1,1)
        if level.background_image != None:
            #level.background_image.blit_tiled(
            #    -env.norm_w//2, -env.norm_h//2,
            #    0, level.width+env.norm_w, level.height+env.norm_h
            #)
            if level.background_tiled:
                level.background_image.blit_tiled(
                    0, 0, 0, level.width, level.height
                )
            else:
                if level.background_scale != 1.0:
                    gl.glPushMatrix()
                    gl.glScalef(level.background_scale, level.background_scale, 1.0)
                level.background_image.blit(0, 0)
                if level.background_scale != 1.0:
                    gl.glPopMatrix()

        gl.glLineWidth(3.0)
        level.batch.draw()
        particle.draw()

        if not debug_draw: return
        draw.set_color(1,0,0,1)
        gl.glLineWidth(1.0)
        for body in physics.body_update_list:
            if hasattr(body, 'draw_collisions'):
                body.draw_collisions()
        for unit in physics.unit_update_list:
            if hasattr(unit, 'draw_collisions'):
                unit.draw_collisions()

    def draw_pointer(self):
        if level.player == None or event.point_object == None:
            return
        p = event.point_object
        if hasattr(p, 'body'):
            p = p.body.position
        if not self.arrow_sprite.visible:
            self.arrow_sprite.visible = True
        if p == None:
            return
        offset_x = env.camera_x - level.player.x
        offset_y = env.camera_y - level.player.y
        offset_x, offset_y = 0, 0
        dist_sq = (p.x-env.camera_x)*(p.x-env.camera_x) + \
                    (p.y-env.camera_y)*(p.y-env.camera_y)
        if dist_sq < 200*200: return
        angle = math.atan2(p.y-env.camera_y, p.x-env.camera_x)
        t = env.norm_theta % (math.pi*2.0)
        a = angle % (math.pi*2.0)
        b = env.norm_w/2
        if (a > t and a < math.pi-t) or \
                (a > math.pi+t and a < math.pi*2-t):
            a = math.pi/2-a
            b = env.norm_h/2
        radius = min(abs(b/math.cos(a))-60, math.sqrt(dist_sq)-100)
        self.arrow_sprite.set_position(
            env.norm_w/2-offset_x+radius*math.cos(angle),
            env.norm_h/2-offset_y+radius*math.sin(angle)
        )
        self.arrow_sprite.rotation = -math.degrees(angle)
        self.arrow_sprite.draw()

    def draw_message(self):
        if event.message != self.current_message:
            self.current_message = event.message
            self.message_label.text = event.message
            self.message_label.font_size = event.message_size
        xa = self.message_label.content_width//2 + 20
        ya = self.message_label.content_height//2 + 5
        gl.glLineWidth(3.0)
        gl.glPointSize(1.0)
        draw.set_color(0,0,0,0.8)
        draw.rect(self.message_label.x-xa, self.message_label.y-ya,
                    self.message_label.x+xa, self.message_label.y+ya)
        draw.set_color(0,0,0,1)
        draw.rect_outline(self.message_label.x-xa, self.message_label.y-ya,
                    self.message_label.x+xa, self.message_label.y+ya)
        draw.points((self.message_label.x-xa, self.message_label.y-ya,
                    self.message_label.x+xa, self.message_label.y-ya,
                    self.message_label.x+xa, self.message_label.y+ya,
                    self.message_label.x-xa, self.message_label.y+ya))
        self.message_label.draw()

    def draw_ai_message(self):
        if event.ai_message != self.current_ai_message:
            self.current_ai_message = event.ai_message
            self.ai_message_label.text = event.ai_message
        w = self.ai_message_label.content_width
        mx = self.ai_message_label.x
        my = self.ai_message_label.y
        gl.glLineWidth(3.0)
        gl.glPointSize(1.0)
        draw.set_color(0,0,0,0.8)
        draw.rect(mx-80, 10, mx+w+10, 100)
        self.ai_message_label.draw()
        draw.set_color(1,1,1,1)
        if event.ai_head != None:
            event.ai_head.blit(mx-80, 17)

    def draw_countdown(self):
        mins, secs = divmod(event.active_countdown, 60)
        self.timer_label.text = "%02d:%02d" % (mins, secs)
        self.timer_label.draw()

    def check_mode_change(self):
        if gui.current_card == 1:
            #unpause
            self.toggle_pause()
        if gui.current_card == 2:
            self.mode = PLAYING
            gui.current_card = None
        if gui.next_card == 3:
            #end game
            self.parent.stop_game()
        if event.next_level == 'win' and gui.current_card == 4:
            self.mode = PLAYING
            self.parent.stop_game()
            return
        if gui.current_card == 5:
            #restart game
            level.player = None
            level.restart_countdown = 0

        if level.player == None or event.end_game:
            if event.start_countdown:
                event.start_countdown = False
                level.restart_countdown = 3.0
            if level.restart_countdown > 0:
                event.message = "Mission Failed"
                event.message_countdown = 3.0
                level.restart_countdown -= env.dt
            else:
                set, path = save.most_recent_save()
                self.init_from_save(path)
        self.check_cutscene()
        if self.mode != CUTSCENE and event.next_level not in ['', 'win']:
            self.loading = True
            level.save()
            self.clean_up_game()
            if event.prefer_saved:
                load_path = save.get_save(event.next_level)
                if load_path != "":
                    self.init_from_save(load_path, True, True)
                    return
            self.init_game(
                event.next_level,
                event.keep_ship_config, event.keep_ship_velocity
            )

    def play_metal_collision(self, a=None, b=None):
        a = a.parent.gluebody.body.velocity
        b = b.parent
        if hasattr(b, 'gluebody'):
            b = b.gluebody
        if hasattr(b, 'body'):
            b = b.body.velocity
        dx = a.x-b.x
        dy = a.y-b.y
        speed_sq = dx*dx+dy*dy
        if speed_sq > 100*100 and self.collide_sound_delay <= 0:
            sound.play(resources.big_metal_clank4)
            self.collide_sound_delay = 10

    def play_wall_collision(self, a=None, b=None):
        a = a.parent.gluebody.body.velocity
        speed_sq = a.x*a.x+a.y*a.y
        if speed_sq > 130*130 and self.collide_sound_delay <= 0:
            sound.play(resources.wall_sound)
            self.collide_sound_delay = 10

    def collide_default(self, a, b, contacts, normal_coef, data):
        return False

    def collide_bullet_silent(self, a, b, *args, **kwargs):
        physics.bullet_deletion_queue.append(a.parent)
        physics.update_bodies_now = True
        if hasattr(b, 'parent'):
            b = b.parent
        if hasattr(b, 'health'):
            b.health -= a.parent.damage
        if hasattr(b, 'obj_id'):
            if b.obj_id in event.damage_funcs.keys():
                for func in event.damage_funcs[b.obj_id]:
                    func(a.parent.damage)
        return False

    def collide_bullet_with_sound(self, a, b, *args, **kwargs):
        sound.play(resources.expl_tiny)
        return self.collide_bullet_silent(a, b, *args, **kwargs)

    def collide_player_free(self, a, b, contacts, normal_coef, data):
        return_val = True
        self.collided_last.append(b)
        if self.keys[key.LSHIFT] and b.parent.gluebody.attachable and \
                b == b.parent.circle:
            a.parent.gluebody.acquire_singlebody(b.parent.gluebody, a.parent)
            if b.parent.ask_key:
                if self.mode == CHOOSE_KEY: return True
                self.mode = CHOOSE_KEY
                gui.last_card = 2
                keychooser.unit_to_bind = b.parent
                keychooser.prev_card_func = keychooser.flag_func
                keychooser.screenshot = pyglet.image.get_buffer_manager().\
                                        get_color_buffer().get_texture()
                gui.current_card = gui.Card(keychooser.widgets())
                gui.next_card = None
                gui.last_card = None
                gui.transition_time = 0
                gui.push_handlers()
                for u in physics.unit_update_list:
                    if u.uses_keys: u.deactivate()
            sound.play(resources.big_metal_clank2)
        else:
            self.play_metal_collision(a, b)
            if hasattr(b, 'obj_id'):
                if b.obj_id in event.collision_funcs.keys():
                    for func in event.collision_funcs[b.obj_id]:
                        result = func()
                        if result == False: return_val = False
        return return_val

    def collide_player_static(self, a, b, contacts, normal_coef, data):
        self.play_metal_collision(a, b)
        return b.parent.handle_collision(a.parent)

    def check_collision_func(self, b, default_return=True):
        return_val = default_return
        if hasattr(b, 'obj_id'):
            if b.obj_id in event.collision_funcs.keys():
                for func in event.collision_funcs[b.obj_id]:
                    result = func()
                    if result == False: return_val = False
        return return_val

    def collide_player_wall(self, a, b, contacts, normal_coef, data):
        if hasattr(b, 'parent'):
            b = b.parent
        self.play_wall_collision(a, b)
        rv = self.check_collision_func(b, True)
        if rv:
            self.play_wall_collision(a, b)
        return rv

    def collide_player_invisible(self, a, b, contacts, normal_coef, data):
        physics.update_bodies_now = True
        if hasattr(b, 'parent'):
            b = b.parent
        rv = self.check_collision_func(b, False)
        if rv:
            self.play_wall_collision(a, b)
        return rv

    def toggle_pause(self):
        if self.mode == PLAYING:
            if level.player == None or event.end_game: return
            self.mode = PAUSED
            for u in physics.unit_update_list:
                if u.uses_keys:
                    u.deactivate()
            pausescreen.init_pause()
            #timer.pause()
            env.main_window.set_mouse_visible(True)

        elif self.mode == PAUSED:
            self.mode = PLAYING
            music.update_volume()
            gui.current_card = None
            gui.next_card = None
            gui.transition_time = 0.0
            for s, l in env.key_bindings.items():
                if self.keys[s]:
                    for u in l:
                        u.activate()
            #timer.unpause()
            env.main_window.set_mouse_visible(False)
            self.fade_countdown = 0.5

    def check_cutscene(self):
        if gui.current_card == 4:
            self.mode = PLAYING
            gui.current_card = None
            for s, l in env.key_bindings.items():
                if self.keys[s]:
                    for u in l:
                        u.activate()
            level.save()
            #timer.unpause()
            self.fade_countdown = 0.5
        if len(event.cutscene_queue) > 0:
            for u in physics.unit_update_list:
                if u.uses_keys:
                    u.deactivate()
            self.mode = CUTSCENE
            #timer.pause()
            cutscene_card = cutscene.Cutscene(
                'Data/Cutscenes/'+event.cutscene_queue[0]+'.txt',
                gui.state_goer(4)
            )
            event.cutscene_queue = event.cutscene_queue[1:]
            gui.current_card = cutscene_card
            gui.next_card = None
            gui.transition_time = 0.5

    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE: return True
        if self.mode != PLAYING: return

        if symbol == key.Z:
            if len(level.player.units) > 5:
                dead_unit = level.player.units[-1]
                env. unbind_keys_for_unit(dead_unit)
                level.player.release_unit(dead_unit)
        else:
            for u in env.key_bindings[symbol]:
                u.activate()

    def on_key_release(self, symbol, modifiers):
        if self.mode != PLAYING:
            if gui.current_card == 2:
                self.mode = PLAYING
            return
        elif symbol == key.ESCAPE:
            self.toggle_pause()
            return True
        elif symbol == key.TAB:
            event.reset_countdown()
        elif symbol == key.COMMA:
            global debug_draw
            debug_draw = not debug_draw
        for u in env.key_bindings[symbol]:
            u.deactivate()
        for s, l in env.key_bindings.items():
            if s != symbol:
                if not self.keys[s]:
                    for u in l:
                        u.deactivate()
        for s, l in env.key_bindings.items():
            if self.keys[s]:
                for u in l:
                    u.activate()

