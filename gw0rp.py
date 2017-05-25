import cProfile
import pyglet, math, os
pyglet.options['debug_gl'] = False

from gamelib.util import env, gui, music, particle, save, settings
from gamelib import gworpplayer, event, level

from pyglet import gl
from pyglet.window import key

psyco_imported = False
profiler = None

GUI = 0
PLAYING = 1

class GworpWindow(pyglet.window.Window):
    def __init__(self):
        self.init_window()
        level.init_entry_points()
        self.init_gui()
        particle.init()
        settings.set('first_launch', False)
        pyglet.clock.schedule(self.on_draw)
    
    def init_window(self):
        vsync = True
        #vsync = False
        
        platform = pyglet.window.get_platform()
        display = platform.get_default_display()
        screen = display.get_default_screen()
        
        template = gl.Config(double_buffer=True, sample_buffers=1, samples=4)
        try:
            config = screen.get_best_config(template)
        except pyglet.window.NoSuchConfigException:
            template = gl.Config()
            config = screen.get_best_config(template)
        
        if settings.fullscreen:
            super(GworpWindow,self).__init__(
                fullscreen=True, config=config
            )
        else:
            super(GworpWindow,self).__init__(
                width=env.norm_w, height=env.norm_h,
                config=config
            )
            self.set_caption("gw0rp")
        
        env.main_window = self
        
        scale_factor_1 = self.height / float(env.norm_h)
        norm_w_1 = int(self.width/scale_factor_1)
        scale_factor_2 = self.width / float(env.norm_w)
        norm_h_2 = int(self.height/scale_factor_1)
        if scale_factor_2 > scale_factor_1:
            env.norm_h = norm_h_2
            env.scale_factor = scale_factor_2
        else:    
            env.norm_w = norm_w_1
            env.scale_factor = scale_factor_1
        env.norm_theta = math.atan2(env.norm_h, env.norm_w)
        
        self.init_gl()
        self.music_countdown = 1.0
        music.update_volume()
    
    def init_gui(self):
        self.mode = GUI
        gui.window = self
        gui.cards['start'] = gui.Card(level.start_widgets())
        gui.cards['save'] = gui.Card(level.save_widgets())
        gui.cards['instructions'] = gui.Card(gui.instruction_widgets())
        gui.cards['settings'] = gui.Card(gui.settings_widgets())
        gui.cards['title'] = gui.Card(gui.title_widgets())
        gui.cards['credits'] = gui.Card(gui.credit_widgets())
        gui.current_card = gui.cards['title']
        gui.push_handlers()
    
    def init_gl(self):
        gl.glEnable(gl.GL_BLEND)
        gl.glEnable(gl.GL_POINT_SMOOTH)
        gl.glEnable(gl.GL_LINE_SMOOTH)
        gl.glShadeModel(gl.GL_SMOOTH)
        gl.glBlendFunc(gl.GL_SRC_ALPHA,gl.GL_ONE_MINUS_SRC_ALPHA)
        gl.glHint(gl.GL_PERSPECTIVE_CORRECTION_HINT,gl.GL_NICEST);
        #gl.glHint(gl.GL_POINT_SMOOTH_HINT,gl.GL_NICEST);
        #gl.glHint(gl.GL_LINE_SMOOTH_HINT,gl.GL_NICEST);
        gl.glDisable(gl.GL_DEPTH_TEST)
    
    def on_draw(self, dt=0):
        env.dt = dt
        if self.music_countdown > 0:
            self.music_countdown -= dt
            if self.music_countdown <= 0:
                music.new_song('spooky')
        if self.mode == GUI:
            gl.glLoadIdentity()
            if env.scale_factor != 1.0:
                gl.glPushMatrix()
                env.scale()
            
            gl.glClearColor(1,1,1,1)
            self.clear()
            gui.draw_card()
            if gui.current_card == gui.START: self.start_game()
            if gui.current_card == gui.QUIT: pyglet.app.exit()
            if gui.current_card == gui.LOAD: self.load_game()
            
            if env.scale_factor != 1.0:
                gl.glPopMatrix()
    
    def start_game(self):
        music.stop()
        pyglet.clock.unschedule(self.on_draw)
        self.mode = PLAYING
        save.init()
        self.gworpplayer = gworpplayer.GworpPlayer(self)
        self.gworpplayer.init_game(level.entry_point)
    
    def load_game(self):
        music.stop()
        pyglet.clock.unschedule(self.on_draw)
        self.mode = PLAYING
        self.gworpplayer = gworpplayer.GworpPlayer(self)
        self.gworpplayer.init_from_save(save.load_from(gui.load_path))
    
    def stop_game(self):
        self.gworpplayer.clean_up()
        #self.gworpplayer = None
        del self.gworpplayer
        self.mode = GUI
        gui.cards['title'] = gui.Card(gui.title_widgets())
        #if gui.current_card == None:
        gui.current_card = gui.cards['title']
        if event.next_level == 'win':
            gui.current_card = gui.cards['credits']
        gui.transition_time = 0.5
        gui.next_card = None
        pyglet.clock.schedule(self.on_draw)
        music.new_song('spooky')
    
    def on_key_press(self, symbol, modifiers):
        if symbol == key.ESCAPE:
            return True
    

def run_game():
    try:
        import psyco
        psyco_imported = True
        psyco.full()
    except:
        pass
    main_window = GworpWindow()
    pyglet.app.run()

def profile():
    env.profiler = profile
    profiler.disable()
    run_game()

if __name__ == '__main__':
    run_game()
    settings.save()
