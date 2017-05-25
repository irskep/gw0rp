"""
Load resources with minimal effort.

    1. Drop this module into your game folder.
    
    2. Tweak resource_paths.
    
    3. Insert custom resource loading (streaming sounds, fonts).
    
    4. Import the module.
    
    5. Refer to images and sounds as resources.your_resource. Automatically updates
        when you add new resources to your folder.
"""

import pyglet, os, yaml
vb = True
def repr_for_obj(obj):
    sl = ['%s(']
    vl = [obj.__class__.__name__]
    
    for k, v in obj.__dict__.items():
        sl.append(k + "=%r, ")
        vl.append(v)
    sl[-1] = sl[-1][:-2]
    sl.append(')')
    return_str = ''.join(sl) % tuple(vl)
    return return_str

class alias(yaml.YAMLObject):
    yaml_tag = u"!alias"
    def __init__(self, name, original):
        self.name = name
        self.original = original
        self.__repr__ = repr_for_obj(self)
    

class anchor(yaml.YAMLObject):
    yaml_tag = u"!anchor"
    def __init__(self, point, images):
        self.point = point
        self.images = images
        self.__repr__ = repr_for_obj(self)
    

class animation(yaml.YAMLObject):
    yaml_tag = u"!animation"
    def __init__(self, name, period, mirror, loop, images):
        self.name = name
        self.period = period
        self.mirror = mirror
        self.loop = loop
        self.images = images
        self.__repr__ = repr_for_obj(self)
    

class background(yaml.YAMLObject):
    yaml_tag = u"!background"
    def __init__(self, name):
        self.name = name
        self.__repr__ = repr_for_obj(self)
    

class center_prefixes(yaml.YAMLObject):
    yaml_tag = u"!center_prefixes"
    def __init__(self, prefixes):
        self.prefixes = images
        self.__repr__ = repr_for_obj(self)
    

class key(yaml.YAMLObject):
    yaml_tag = u"!key"
    def __init__(self, tag, image, color):
        self.tag = tag
        self.image = image
        self.color = color
        self.__repr__ = repr_for_obj(self)
    

class text_sound(yaml.YAMLObject):
    yaml_tag = u"!text_sound"
    def __init__(self, name, sound):
        self.name = name
        self.original = sound
        self.__repr__ = repr_for_obj(self)
    

supported_image_formats = [
    'bmp','dds','exif','gif','jpg','jpeg','jp2','jpx','pcx','png',
    'pnm','ras','tga','tif','tiff','xbm', 'xpm'
]

#Change this to fit your folder structure
resource_paths = [
    ''.join(['Data/', f]) for f in \
    ['Backgrounds', 'Decals', 'Doors', 'Enemies', 'Graphics', 
    'Music', 'Sounds', 'Units']
]

resource_paths.extend([
    ''.join(['Editor/', f]) for f in \
    ['Button Images', 'Resources', 'Tool Resources']
])

exclude = []

loaded = False

function_pairs = {
    #'ext':(func, {args})
    'mp3':(pyglet.resource.media,{'streaming':True}),
    'ogg':(pyglet.resource.media,{'streaming':True}),
    'wav':(pyglet.resource.media,{'streaming':False})
}

pyglet.resource.path = resource_paths
pyglet.resource.reindex()
#Make default function for images be pyglet.resource.image().
for ext in supported_image_formats:
    if not ext in function_pairs.keys():
        function_pairs[ext] = (pyglet.resource.image,{})

#Then a miracle occurs!
decals = []
for path in pyglet.resource.path:
    for file_name in os.listdir(path):
        name, ext = os.path.splitext(file_name)
        if name not in exclude:
            if vb: print 'loading', name
            for key, (func, kwargs) in function_pairs.iteritems():
                if ext == '.'+key and os.path.exists(path):
                    new = func(file_name,**kwargs)
                    globals()[name] = new
                    new.instance_name = name
                    new.folder = os.path.split(path)[-1]
                    if new.folder == 'Decals':
                        new.anchor_x = new.width/2
                        new.anchor_y = new.height/2
                        decals.append(name)

background_images = {}
key_images = {}
key_colors = {}
text_sounds = {}

stream = file(os.path.join('Data','content_data.yaml'), 'r')
yaml_objects = [obj for obj in yaml.load(stream) if obj != None]
stream.close()

stream = file(os.path.join('Editor','content_data.yaml'), 'r')
yl = yaml.load(stream)
if yl != None:
    yaml_objects.extend([obj for obj in yl if obj != None])
stream.close()

for obj in yaml_objects:
    if obj.yaml_tag == u'!anchor':
        if vb: print 'anchor', obj
        for img in obj.images:
            if img in globals():
                globals()[img].anchor_x = obj.point[0]
                globals()[img].anchor_y = obj.point[1]
    elif obj.yaml_tag == u"!animation":
        if vb: print 'anim', obj, obj.name
        img_list = [globals()[img] for img in obj.images if img in globals()]
        if obj.mirror:
            k = len(img_list)
            for i in xrange(1,k-1):
                img_list.insert(k, img_list[i])
        new_anim = pyglet.image.Animation.from_image_sequence(
            img_list, obj.period, loop=obj.loop
        )
        globals()[obj.name] = new_anim
    elif obj.yaml_tag == u"!alias":
        if vb: print 'alias', obj, obj.name
        if obj.original in globals():
            globals()[obj.name] = globals()[obj.original]
    elif obj.yaml_tag == u"!background":
        if vb: print 'bg', obj, obj.name
        new_tile = pyglet.image.TileableTexture.create_for_image(
            globals()[obj.name]
        )
        background_images[obj.name] = new_tile
    elif obj.yaml_tag == u"!center_prefixes":
        for k, v in globals().items():
            if hasattr(v, 'instance_name'):
                for prefix in obj.prefixes:
                    if v.instance_name.startswith(prefix):
                        v.anchor_x, v.anchor_y = v.width//2, v.height//2
    elif obj.yaml_tag == u"!key":
        if vb: print 'key', obj, obj.tag
        key_images[obj.tag] = globals()[obj.image]
        key_colors[obj.tag] = tuple(obj.color)
    elif obj.yaml_tag == u"!text_sound":
        if vb: print 'sound', obj, obj.name
        text_sounds[obj.name] = globals()[obj.sound]
