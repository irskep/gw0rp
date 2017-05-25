import pyglet
import resources, settings

queue = []

def play(sound, x=-1, y=-1):
    player = pyglet.media.ManagedSoundPlayer()
    player.queue(sound)
    player.volume = settings.sound_volume
    player.pause()
    queue.append(player)

def update():
    global queue
    for player in queue:
        player.play()
