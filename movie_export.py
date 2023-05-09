import math
import os
import pathlib

import ffmpeg

def make_mosaic(input_path, mask_path, output_path):
    input = ffmpeg.input(input_path).split()
    mask = ffmpeg.input(mask_path)
    mosaic = ffmpeg.filter(input[0], 'scale', 'trunc(iw / max(4, trunc(min(ih / 100, iw / 100))))', 'trunc(ih / max(4, trunc(min(ih / 100, iw / 100))))')
    mosaic = ffmpeg.filter_multi_output([mosaic, input[1]], 'scale2ref', flags='neighbor')
    out = ffmpeg.filter([mosaic[0], mosaic[1], mask], 'maskedmerge')
    out = ffmpeg.output(out, str(output_path))
    ffmpeg.overwrite_output(out).run()

def half_scale(input):
    return ffmpeg.filter(input, 'scale', 'iw / 2', 'ih / 2')

def palettize(input):
    input = input.split()
    palette = ffmpeg.filter(input[0], 'palettegen')
    return ffmpeg.filter([input[1], palette], 'paletteuse')

def output_stream(input, output_path, framerate, type):
    out = ffmpeg.output(input, str(output_path), **{'framerate': framerate, 'f':type})
    ffmpeg.overwrite_output(out).run()

def seq_to_mp4(input_path, framerate, output_path):
    input = ffmpeg.input(input_path)
    out = ffmpeg.output(input, str(output_path), **{'framerate': framerate, 'c:v': 'libx264', 'pix_fmt': 'yuv420p'})
    ffmpeg.overwrite_output(out).run()

def seq_to_apng(input_path, framerate, output_path):
    input = ffmpeg.input(input_path)
    input = half_scale(input)
    output_stream(input, output_path, framerate, 'apng')

def seq_to_gif(input_path, framerate, output_path):
    input = ffmpeg.input(input_path)
    input = half_scale(input)
    input = palettize(input)
    output_stream(input, output_path, framerate, 'gif')

def seq_to_webp(input_path, framerate, output_path):
    input = ffmpeg.input(input_path)
    input = half_scale(input)
    output_stream(input, output_path, framerate, 'webp')

def downscale(input_path, output_path):
    input = ffmpeg.input(input_path)
    input = half_scale(input)
    out = ffmpeg.output(input, str(output_path))
    ffmpeg.overwrite_output(out).run()

def get_movie_name():
    for name in os.listdir():
        if name.endswith('clip'):
            return pathlib.Path(name)
    return None

def get_min_loop_count(input_path):
    time = float(ffmpeg.probe(input_path)['format']['duration'])
    return math.ceil(2 / time)

def min_loop_video(input_path):
    count = get_min_loop_count(input_path)
    if count == 1:
        return
    input = ffmpeg.input(input_path, stream_loop=count)
    temp_path = input_path.with_stem(input_path.stem + '-temp')
    out = ffmpeg.output(input, str(temp_path), c='copy')
    ffmpeg.overwrite_output(out).run()
    temp_path.replace(input_path)

def main():
    framerate = 24
    movie_name = get_movie_name()
    base_path = 'output/base_%04d.png'
    mask_path = 'output/mask_%04d.png'
    censor_path = pathlib.Path('output/censor_%04d.png')
    censor_mp4 = censor_path.with_stem(movie_name.stem).with_suffix('.mp4')
    censor_pawoo = censor_mp4.with_stem(censor_mp4.stem + '-pawoo')
    censor_gif = censor_path.with_stem(movie_name.stem).with_suffix('.gif')
    uncensor_mp4 = movie_name.with_suffix('.mp4')
    make_mosaic(base_path, mask_path, censor_path)
    seq_to_mp4(censor_path, framerate, censor_mp4)
    downscale(censor_mp4, censor_pawoo)
    min_loop_video(censor_mp4)
    seq_to_gif(censor_path, framerate, censor_gif)
    seq_to_mp4(base_path, framerate, uncensor_mp4)

if __name__ == '__main__':
    main()