import os
from pathlib import Path

def main():
    folder = Path('.')
    files = [x for x in sorted(os.listdir(folder)) if x.endswith('.png')]
    for file, i in zip(files, range(len(files))):
        if i % 3 != 0:
            os.unlink(folder / file)

if __name__ == '__main__':
    main()