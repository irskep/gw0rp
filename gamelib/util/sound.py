import pyglet, settings

def play(sound):
    player = sound.play()
    player.volume = settings.sound_volume
