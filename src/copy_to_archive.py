from pathlib import Path
import shutil

image_types = ['png', 'gif', 'jpg']
video_types = ['mp4']
source_types = ['psd', 'clip', 'kra', 'blend']
archive = Path('~/aux/archives/current').expanduser()
keys = archive / 'keys'
finished = Path('~/aux/art/finished').expanduser()
timelapse = Path('~/aux/art/timelapse').expanduser()
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
    has_images = False

    for type in image_types:
        for file in temp.glob('*.' + type):
            has_images = True
            images = arch_dir(file, 'images')
            copy(file, images)
            copy(file, finished)

    for type in video_types:
        for file in temp.glob('*.' + type):
            if has_images:
                timelapse_arch = arch_dir(file, 'recordings')
                copy(file, timelapse_arch)
                copy(file, timelapse)
            else:
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