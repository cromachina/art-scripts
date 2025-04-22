from pathlib import Path
import shutil

image_types = ['png', 'gif', 'jpg', 'mp4']
source_types = ['psd', 'clip']
archive = Path('~/aux/archives/current').expanduser()
keys = archive / 'keys'
finished = Path('~/aux/art/finished').expanduser()
temp = Path('~/aux/art/temp').expanduser()

def copy(src_file: Path, dst_dir: Path):
    dst_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src_file, dst_dir)
    print(f'{src_file} -> {dst_dir}')

def arch_dir(file, subname):
    year = file.name[:4]
    dir = archive / f'{year}-{subname}'
    return dir

def main():
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

if __name__ == '__main__':
    main()