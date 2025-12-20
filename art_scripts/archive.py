import argparse
import os
import re
import secrets
from pathlib import Path
from PIL import Image, ImageFont, ImageDraw

_7z_name = '7zz'
zip_name = 'zip'

def letters(start, end):
    return list(map(chr, range(ord(start), ord(end) + 1)))

chars = letters('a', 'z') + letters('0', '9')

def gen_pw(size):
    return "".join([secrets.choice(chars) for _ in range(size)])

def gen_key(key_file):
    key = gen_pw(6)
    with open(key_file, 'w') as f:
        f.write(key)
    return key

def get_key(key_file):
    if os.path.exists(key_file):
        with open(key_file, 'r') as f:
            return f.read()
    else:
        return gen_key(key_file)

def make_key_image(key, in_file:Path, out_file:Path, font_scale):
    image = Image.open(in_file)
    fontsize = int(max(image.size) * font_scale)
    offset = fontsize // 4
    ctx = ImageDraw.Draw(image)
    ctx.text(
        text=key,
        font=ImageFont.truetype('ARIALBD_1', fontsize),
        xy=(offset, image.height - offset),
        anchor='ld',
        stroke_width=fontsize // 10,
        fill=(255, 255, 255, 255),
        stroke_fill=(0, 0, 0, 255)
    )
    os.makedirs(out_file.parent, exist_ok=True)
    image.save(out_file)

def run_7zip(archive_name, file_glob, key=None, multipart=None):
    parts = '-v1g' if multipart else ''
    key = f'-p{key}' if key is not None else ''
    os.system(f'{_7z_name} -xr"!.*" a -m0=lzma2 -mmt=24 -mx=9 -mhe {key} {parts} {archive_name}.7z {file_glob}')

def run_zip(archive_name, file_glob):
    os.system(f'{zip_name} -9 -u -r {archive_name}.zip {file_glob}')

def get_first_image(dir_path):
    try:
        files = os.listdir(dir_path)
    except:
        return None
    if len(files) == 0:
        return None
    files.sort()
    return Path(dir_path) / files[0]

def get_first_censor_image():
    for dir_path in ['censor', 'bars']:
        image_path = get_first_image(dir_path)
        if image_path is not None:
            return image_path
    return None

def archive_work(work_name, font_scale):
    key = get_key(f'{work_name}-key.txt')
    try:
        make_key_image(key, get_first_censor_image(), Path('key/0.png'), font_scale)
    except:
        pass
    run_7zip(f'{work_name}', f'{work_name} *.png *.mp4 *.psd *.clip *.kra', key)

def archive_everything(archive_name, key=None):
    if key == None:
        key = archive_name
    run_7zip(archive_name, archive_name, get_key(f'{key}-key.txt'))

def archive_imgs_psds():
    reg = re.compile('(\\d+)')
    for name in os.listdir():
        if Path(name).is_dir():
            res = reg.match(name)
            if res is not None:
                archive_everything(name, 'archive')

def archive_doujin(name):
    key = gen_key(f'{name}-key.txt')
    run_7zip(f'{name}-en', 'en', key)
    run_7zip(f'{name}-jp', 'jp', key)
    run_7zip(f'{name}-psd', '*psd', key)
    run_zip(f'{name}-en', 'en-censor')
    run_zip(f'{name}-jp', 'jp-censor')

def get_archive_name():
    for name in sorted(os.listdir()):
        if name.endswith('png') or name.endswith('mp4'):
            return re.match('(\\d+)', name)[0]
    return None

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--everything', action=argparse.BooleanOptionalAction)
    parser.add_argument('--gen-key', action=argparse.BooleanOptionalAction)
    parser.add_argument('--name', type=str, default='')
    parser.add_argument('--doujin', action=argparse.BooleanOptionalAction)
    parser.add_argument('--font-scale', type=float, default=0.02)
    args = parser.parse_args()
    if args.everything:
        archive_imgs_psds()
    elif args.gen_key:
        gen_key(args.name)
    elif args.doujin:
        archive_doujin(args.name)
    else:
        if args.name != '':
            name = args.name
        else:
            name = get_archive_name()
            if name == None:
                print('No data found')
                return
        archive_work(name, args.font_scale)

if __name__ == '__main__':
    main()