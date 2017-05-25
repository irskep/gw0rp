"""
1. Put your game's name as the parameter in the settings_dir line
2. List your game's options and saved state necessities in the settings dict
3. "from settings import *" in other files and refer to settings['screen_width']
	or something.
4. Call save_settings() whenever you update the settings dictionary.
5. There is no step 5, because everything is loaded automatically at startup.

If you add settings that aren't in the save file and would be overwritten by the
loading step, then add the following lines to your game, run it once, and then
remove them:
settings = default_settings()
save_settings()
"""
import pyglet.resource, os, pickle

settings_dir = pyglet.resource.get_settings_path('gw0rp')
settings_path = os.path.join(settings_dir, 'Preferences.txt')

def set(k, v):
    global settings
    settings[k] = v
    globals().update(settings)

def save():
	"""Pickle settings dictionary to the appropriate location"""

	if not os.path.exists(settings_dir):
	    os.makedirs(settings_dir)
	settings_file = open(settings_path,'w')
	pickle.dump(settings,settings_file)
	settings_file.close()
	globals().update(settings)


settings = dict(
	fullscreen = False,
	music_volume = 1.0,
	sound_volume = 1.0,
	save_dir = os.path.join(settings_dir, 'Saved Games'),
	first_launch = True
)

if os.path.exists(settings_path):
	try:
	    settings.update(pickle.load(open(settings_path,'r')))
	except:
	    save()
else:
    try:
        os.makedirs(settings_dir)
    except:
        pass #Windows is being stupid.

if not os.path.exists(settings['save_dir']):
    os.makedirs(os.path.join(settings['save_dir'], 'Autosave'))

globals().update(settings)