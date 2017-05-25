import string
import pyglet, draw, env, gui, resources, settings, sound
from pyglet.window import key

class Cutscene(object):
    def __init__(self, path, action):
        self.action = action
        self.message_groups = []
        f=open(path)
        message_group = []
        for line in f:
            if line[0] == '-':
                self.message_groups.append(message_group)
                message_group = []
            elif line.find(':') != -1:
                tup = [s for s in line.split(":")]
                m = tup[0].strip()
                p = ':'.join(tup[1:]).lstrip()
                message_group.append((m, p))
        self.message_groups.append(message_group)
        f.close()
        
        self.char_delay_default = 0.05
        self.char_delay = self.char_delay_default
        self.countdown = self.char_delay
        self.msg_delay = 0.5
        self.typing = True
        
        self.batch = pyglet.graphics.Batch()
        self.msg_strings = []
        self.labels = []
        self.sender_sprites = []
        self.sender_names = []
        self.sender_labels = []
        self.current_group = -1
        self.next_group()
    
    def push_handlers(self):
        env.main_window.push_handlers(self)
    
    def pop_handlers(self):
        env.main_window.pop_handlers()
    
    def sender_color_hash(self, name):
        if not name: return 0
        def c_mul(a, b):
            return eval(hex((long(a) * b) & 0xFFFFFFFFL)[:-1])
        
        value = ord(name[0]) << 7
        for char in name:
            value = c_mul(1000003, value) ^ ord(char)
        value = value ^ len(name)
        
        while value < 100000:
            value *= 10
        
        num_string = str(value)
        r = int(num_string[0:2])
        g = int(num_string[2:4])
        b = int(num_string[4:6])
        r = int(128 * (1 + r/99.0))
        g = int(128 * (1 + g/99.0))
        b = int(128 * (1 + b/99.0))
        
        return (r, g, b, 255)
    
    def next_group(self):
        self.char_delay = self.char_delay_default
        for label in self.labels:
            label.delete()
        for sprite in self.sender_sprites:
            sprite.delete()
        for label in self.sender_labels:
            label.delete()
        
        self.current_group += 1
        
        if self.current_group >= len(self.message_groups):
            sound.play(resources.whoosh_1)
            self.action()
            return
        
        self.text_position = 0
        self.msg_num = 0
        
        self.msg_strings = []
        self.labels = []
        self.sender_sprites = []
        self.sender_names = []
        self.sender_labels = []
        last_y = env.norm_h-10
        for sender, message in self.message_groups[self.current_group]:
            col = self.sender_color_hash(sender)
            if sender == 'time':
                new_label = pyglet.text.Label(
                    message, x=env.norm_w/2, y=env.norm_h/2,
                    font_size=36, font_name='Gill Sans',
                    anchor_x='left', anchor_y='center',
                    color=(255,255,255,255), batch=self.batch
                )
                new_label.x -= new_label.content_width/2
                self.char_delay = self.char_delay_default * 1.5
            elif sender == 'blank':
                new_label = pyglet.text.Label(
                    message, x=50, y=last_y-30,
                    font_size=28, font_name='Gill Sans',
                    anchor_x='left', anchor_y='top',
                    multiline=True, width=env.norm_w-100,
                    color=(255,255,255,255), batch=self.batch
                )
            else:
                new_label = pyglet.text.Label(
                    message, x=200, y=last_y-30,
                    font_size=28, font_name='Gill Sans',
                    anchor_x='left', anchor_y='top',
                    multiline=True, width=env.norm_w-250,
                    color=col, batch=self.batch
                )
            self.labels.append(new_label)    
            self.msg_strings.append(message)
            self.sender_names.append(sender)
            new_y = new_label.y - new_label.content_height + 50
            
            if sender not in ['time', 'blank']:
                new_sprite = pyglet.sprite.Sprite(
                    getattr(resources,sender), 70, last_y-110,
                    batch=self.batch
                )
                new_sender_label = pyglet.text.Label(
                    "", font_size=12, font_name='Gill Sans', 
                    x=70+new_sprite.width/2, y=new_sprite.y,
                    anchor_x='center', anchor_y='top',
                    color=col, batch=self.batch
                )
                new_sprite.visible = False
                self.sender_labels.append(new_sender_label)
                self.sender_sprites.append(new_sprite)
            
            if last_y-new_y < 110: new_y = last_y-110
            last_y = new_y
        
        for label in self.labels:
            label.text = ""
        
        if len(self.sender_sprites) > 0:
            self.sender_sprites[0].visible = True
            self.sender_labels[0].text = self.sender_names[0]
        self.typing = True
    
    def update_text(self):        
        if self.msg_num >= len(self.labels):
            self.typing = False
            return
        self.text_position += 1
        this_label = self.labels[self.msg_num]
        if self.text_position > len(self.msg_strings[self.msg_num]):
            self.next_message()
        else:
            this_text = self.msg_strings[self.msg_num]
            this_label.text = this_text[0:self.text_position]
            if this_label.text[-1] == '.':
                self.countdown += self.char_delay*3
    
    def next_message(self):
        self.labels[self.msg_num].text = self.msg_strings[self.msg_num]
        self.text_position = -1
        self.msg_num += 1
        self.countdown = self.msg_delay
        self.sender_sprites[self.msg_num].visible = True
        self.sender_labels[self.msg_num].text = self.sender_names[self.msg_num]
        self.update_text()
    
    def draw(self):
        draw.clear(0,0,0,1)
        self.batch.draw()
        if self.typing:
            self.countdown -= env.dt
            if self.countdown <= 0:
                self.update_text()
                sound = resources.text_sounds[self.sender_names[self.msg_num]]
                if self.labels[self.msg_num].text[-1] != ' ':
                    player = pyglet.media.ManagedSoundPlayer()
                    player.pause()
                    player.queue(sound)
                    player.volume = settings.sound_volume*0.1
                    player.play()
                self.countdown += self.char_delay
    
    def on_mouse_release(self, x, y, button, modifiers):
        self.on_key_release(key.SPACE, 0)
    
    def on_key_release(self, symbol, modifiers):
        self.countdown = 0
        if symbol == key.ESCAPE:
            sound.play(resources.whoosh_1)
            self.action()
            return
        trigger_keys = [key.SPACE, key.RETURN, key.ENTER, key.TAB]
        if symbol not in trigger_keys: return
        if self.typing:
            if self.msg_num >= len(self.msg_strings):
                self.typing = False
            else:
                self.text_position = len(self.msg_strings[self.msg_num])-1
        if not self.typing:
            self.next_group()
    
