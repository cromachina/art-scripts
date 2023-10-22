from pathlib import Path
import shutil

image_types = ['png', 'gif', 'jpg', 'mp4']
source_types = ['psd', 'clip']
archive = Path('H:/archives/current')
keys = archive / 'keys'
finished = Path('H:/art/finished')
temp = Path('H:/art/temp')

def copy(src, dst):
    shutil.copy2(src, dst)
    print(f'{src} -> {dst}')

def arch_dir(file, subname):
    year = file.name[:4]
    dir = archive / f'{year}-{subname}'
    return dir

for type in image_types:
    for file in temp.glob('*.' + type):
        images = arch_dir(file, 'images')
        copy(file, images)
        copy(file, finished)

for type in source_types:
    for file in temp.glob('*.' + type):
        psds = arch_dir(file, 'psds')
        copy(file, psds)

for file in temp.glob('*-key.txt'):
    copy(file, keys)
