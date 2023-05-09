from pathlib import Path
import shutil

image_types = ['png', 'gif', 'jpg', 'mp4']
source_types = ['psd', 'clip']
archive = Path('H:/Archives')
finished = Path('finished')
temp = Path('temp')

def arch_dir(file, subname):
    year = file.name[:4]
    dir = archive / f'{year}-{subname}'
    return dir

for type in image_types:
    for file in temp.glob('*.' + type):
        images = arch_dir(file, 'images')
        shutil.copy2(file, images)
        shutil.copy2(file, finished)

for type in source_types:
    for file in temp.glob('*.' + type):
        psds = arch_dir(file, 'psds')
        shutil.copy2(file, psds)
