B_BOTTOM = 40   #to 3f
B_TOP = 41      #to 4a
T_TOP = 49

from gamelib import event
from gamelib.util import sound, resources

msges = {}

TURRETS = [42, 43, 44, 45, 46, 47, 48]

def go_bottom():
    event.go_to_level('level_3f', True, True, True)

def go_4():
    event.show_cutscene('t3_end')
    event.go_to_level('Level_4a')

def go_top():
    if event.get_flag('stolen'): return
    event.set_flag('stolen', True)
    event.register_timed_func(go_4, 6)
    sound.play(resources.the_sound)
    event.fade_out_countdown = 0

def init():
    global msges
    msges = event.file_to_dict('Messages_3.txt')
    event.register_collision_func(B_BOTTOM, go_bottom)
    event.register_collision_func(T_TOP, go_top)
    event.set_flag('stolen', False)
    for obj_id in TURRETS:
        event.get_object(obj_id).active = False
    event.show_ai_message(msges['human1_3g_1'], 4, head='Terran_1')    
    event.show_ai_message(msges['human2_3g_2'], 4, head='Terran_2')

def on_load():
    global msges
    msges = event.file_to_dict('Messages_3.txt')
