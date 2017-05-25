import pyglet
import resources, settings

players = {}

now_playing = ""

def new_song(song):
    global now_playing, player
    if song == now_playing and players[song].playing: return
    if now_playing != "" and players[now_playing].playing:
        players[now_playing].pause()
    now_playing = song
    if song in players.keys():
        players[song].seek(0)
        players[song].play()
    else:
        players[song] = pyglet.media.Player()
        players[song].eos_action = players[song].EOS_LOOP
        players[song].volume = settings.music_volume
        players[song].queue(getattr(resources, song))
        players[song].play()

def resume():
    players[now_playing].play()

def pause():
    players[now_playing].pause()

def stop():
    try:
        players[now_playing].pause()
    except:
        pass

def playing():
    return players[now_playing].playing

def current_track():
    if players[now_playing].playing:
        return now_playing
    else:
        return None

def update_volume():
    for k, v in players.items():
        v.volume = settings.music_volume
