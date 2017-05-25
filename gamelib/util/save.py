import os, shutil
import settings

save_path = os.path.join(settings.save_dir, 'Autosave')

def clear_save(name):
    path = os.path.join(settings.save_dir, name)
    if not os.path.exists(path): return
    for f in os.listdir(path):
        os.remove(os.path.join(path, f))
    os.rmdir(path)

def init():
    new_file = os.path.join(save_path, 'Info.txt')
    if os.path.exists(save_path):
        clear_save('Autosave')
    os.makedirs(save_path)
    f = open(new_file, 'w')
    f.write('Invalid')
    f.close()

def set_current_level(level_set, level_name):    
    f = open(os.path.join(save_path, 'Info.txt'), 'w')
    f.write(''.join([level_set, '\n', level_name, '\n']))
    f.close()

def save_to(dest, src='Autosave'):
    newpath = os.path.join(settings.save_dir, dest)
    oldpath = os.path.join(settings.save_dir, src)
    if oldpath == newpath: return
    if os.path.exists(newpath):
        clear_save(dest)
    shutil.copytree(oldpath, newpath)

def autosave_exists():
    return os.path.exists(os.path.join(save_path, 'Info.txt'))

def most_recent_save():
    f = open(os.path.join(save_path, 'Info.txt'), 'r')
    level_set, name = [l.strip() for l in f]
    level_path = os.path.join(save_path, name+".yaml")
    return level_set, level_path

def load_from(src):
    save_to('Autosave', src)
    return most_recent_save()[1]

def get_save(level_name):
    path = os.path.join(save_path, level_name+".yaml")
    if os.path.exists(path):
        return path
    return ""

def list_saves():
    return [
        f for f in os.listdir(settings.save_dir) \
        if os.path.isdir(os.path.join(settings.save_dir, f))
    ]
    