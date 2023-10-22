from PIL import Image
import sys
from pathlib import Path

outfile = Path(sys.argv[2])

im = Image.open(sys.argv[1])
if outfile.suffix in ['.bmp', '.jpg']:
    im = Image.alpha_composite(Image.new('RGBA', im.size, 'WHITE'), im.convert('RGBA'))
im.save(outfile)