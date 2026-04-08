from pathlib import Path
import glob
import hashlib
import argparse
from PIL import Image

def png_to_webp(file:Path):
    target = file
    if file.suffix == '.png':
        target = file.with_suffix('.webp')
        img = Image.open(file)
        img.save(target, 'webp')
        print(file, '->', target)
        file.unlink()
    return target

def hash_rename(file:Path):
    with open(file, 'rb') as f:
        md5 = hashlib.file_digest(f, 'md5').hexdigest()
    target = file.with_stem(md5)
    if file != target:
        print(file, '->', target)
        file.rename(target)
    return target

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('files', nargs='+')
    args = parser.parse_args()
    files = sorted([Path(globfile) for file in args.files for globfile in glob.glob(file, recursive=True)])
    for file in files:
        if file.is_file():
            hash_rename(png_to_webp(file))

if __name__ == '__main__':
    main()