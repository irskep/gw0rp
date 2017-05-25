import pyglet.clock, time

"""
Import this module to get game pausing features for free. It basically just
hijacks the time function of the default clock to take off time paused.
Any scheduled functions will also be paused, unless they are scheduled to
be run as often as possible, like GameWindow.on_draw() in this example game.

If you don't want your scheduled functions to be affected by pausing, you can
create your own custom clock. You could also tweak this file to use its
own custom clock.

Functions:
pause()
unpause()
dt(): Time since last tick in seconds
toggle_pause(): pauses/unpauses
paused(): current pause state
"""

class GameClock(pyglet.clock.Clock):
    def __init__(self):
        self.dt = 0.0
        self.paused = False
        self.pause_start = 0
        self.total_pause_time = 0
        super(GameClock, self).__init__(time_function=self.game_time)

    def tick(self,poll=False):
        self.dt = super(GameClock,self).tick(poll)
        if self.dt > 0.2: self.dt = 0   #sanity check
        if self.paused: self.dt = 0

    def game_time(self):
        if self.paused:
            return self.pause_start - self.total_pause_time
        else:
            return time.time() - self.total_pause_time

    def pause(self):
        if not self.paused: self.toggle_pause

    def unpause(self):
        if self.paused: self.toggle_pause()

    def toggle_pause(self):
        self.paused = not self.paused
        if self.paused: self.total_pause_time += time.time() - self.pause_start
        else: self.pause_start = time.time()

#convenience functions
def dt(): return pyglet.clock.get_default().dt
def toggle_pause(): pyglet.clock.get_default().toggle_pause()
def pause(): pyglet.clock.get_default().pause()
def unpause(): pyglet.clock.get_default().unpause()
def paused(): return pyglet.clock.get_default().paused

pyglet.clock.set_default(GameClock())