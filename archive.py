import argparse
import os
import re
import secrets
import pathlib

def gen_key(key_file):
    key = secrets.token_hex(16)
    with open(key_file, 'w') as f:
        f.write(key)
    return key

def get_key(key_file):
    if os.path.exists(key_file):
        with open(key_file, 'r') as f:
            return f.read()
    else:
        return gen_key(key_file)

def zip(archive_name, file_glob, key, multipart=None):
    parts = '-v1g' if multipart else ''
    os.system(f'sh 7z a -m0=lzma2 -mmt=24 -mx=9 -mhe -p{key} {parts} {archive_name}.7z {file_glob}')

def archive_work(work_name):
    key = get_key(f'{work_name}-key.txt')
    zip(f'{work_name}', '*.png *.mp4', key)
    zip(f'{work_name}-psd', '*.psd *.clip', key)

def archive_everything(archive_name, key=None):
    if key == None:
        key = archive_name
    zip(archive_name, archive_name, get_key(f'{key}-key.txt'))

def archive_imgs_psds():
    reg = re.compile('(\d+)')
    for name in os.listdir():
        if pathlib.Path(name).is_dir():
            res = reg.match(name)
            if res is not None:
                year = res[0]
                key_file = f'{year}-archive'
                archive_everything(name, key_file)

def get_archive_name():
    for name in os.listdir():
        if name.endswith('png') or name.endswith('mp4'):
            return re.match('(\d+)', name)[0]
    return None

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--everything', action=argparse.BooleanOptionalAction)
    parser.add_argument('--gen-key', action=argparse.BooleanOptionalAction)
    parser.add_argument('--name', type=str, default='')
    args = parser.parse_args()
    if args.everything:
        archive_imgs_psds()
    elif args.gen_key:
        gen_key(args.name)
    elif args.name != '':
        archive_work(args.name)
    else:
        archive_work(get_archive_name())
