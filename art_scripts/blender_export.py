import bpy
import subprocess
from pathlib import Path

file_name = bpy.path.display_name_from_filepath(bpy.context.blend_data.filepath)
output_dir = '//output/'

def downscale_video(file:Path, scale, codec, tag=None):
    tag = f'-{tag}' if tag is not None else ''
    outfile = file.with_stem(f'{file.stem}-{codec}{tag}')
    subprocess.run(['ffmpeg',
        '-i', str(file),
        '-vf', f'scale=iw*{scale}:ih*{scale}',
        '-color_primaries', 'bt709',
        '-colorspace', 'bt709',
        '-color_trc', 'iec61966-2-1',
        '-vcodec', codec,
        '-c:a', 'copy',
        '-y',
        outfile
    ])
    return outfile

def twitter_video(file:Path):
    outfile = file.with_stem(f'{file.stem}-twitter')
    subprocess.run(['ffmpeg',
        '-i', str(file),
        '-vcodec', 'libx264',
        '-pix_fmt', 'yuv420p',
        '-strict', 'experimental',
        '-vf', f'scale=1920:1080',
        '-aspect', '1:1'
        '-color_primaries', 'bt709',
        '-colorspace', 'bt709',
        '-color_trc', 'iec61966-2-1',
        '-c:a', 'copy',
        '-y',
        outfile
    ])
    return outfile

def video_to_gif(file:Path, fps=8):
    outfile = file.with_suffix('.gif')
    subprocess.run(['ffmpeg',
        '-i', str(file),
        '-vf', f'fps={fps},split[a][b];[a]palettegen[p];[b][p]paletteuse',
        '-loop', '0',
        '-y',
        outfile
    ])
    return outfile

def set_render_settings(scene):
    scene.render.use_file_extension = False
    scene.render.resolution_percentage = 100
    scene.render.ffmpeg.format = 'MPEG4'
    scene.render.ffmpeg.codec = 'PNG'

def make_file_name(base_name, channels):
    active = [channel.lower() for channel,value in channels.items() if value]
    active.sort()
    active_str = '-'.join(active)
    return f'{base_name}-{active_str}.mp4'

def set_channels(scene, channels):
    for channel, value in channels.items():
        scene.sequence_editor.channels[channel].mute = not value

def render_scene(scene, channels):
    current_scene = bpy.context.scene
    bpy.context.window.scene = scene
    bpy.ops.scene.new(type='FULL_COPY')
    new_scene = bpy.context.scene
    set_render_settings(new_scene)
    set_channels(new_scene, channels)
    outfile = make_file_name(f'{output_dir}{file_name}-{scene.name.lower()}', channels)
    new_scene.render.filepath = outfile
    bpy.ops.render.render(animation=True)
    bpy.context.window.scene = current_scene
    bpy.data.scenes.remove(new_scene)
    return outfile

def render_all(render_sets):
    for render_set in render_sets:
        file = render_scene(bpy.data.scenes[render_set['scene']], render_set['channels'])
        post_op = render_set['post_op']
        if post_op is not None:
            post_op(Path(bpy.path.abspath(file)))

def censor_post_op(file):
    downscale_video(file, 1, 'h264')
    downscale_video(file, 0.5, 'h264', 'half')
    png_out = downscale_video(file, 0.5, 'png')
    video_to_gif(png_out)

def base_post_op(file):
    downscale_video(file, 1, 'h264')
    png_out = downscale_video(file, 0.5, 'png')
    video_to_gif(png_out)

render_sets = [
    {
        'scene': 'Sequence',
        'channels': { 'Base': True, 'Censor': False, 'Text': False },
        'post_op': base_post_op,
    },
    {
        'scene': 'Sequence',
        'channels': { 'Base': False, 'Censor': True, 'Text': False },
        'post_op': censor_post_op,
    },
    {
        'scene': 'Sequence',
        'channels': { 'Base': False, 'Censor': True, 'Text': True },
        'post_op': censor_post_op,
    },
    {
        'scene': 'Loop',
        'channels': { 'Base': True, 'Censor': False},
        'post_op': base_post_op,
    },
    {
        'scene': 'Loop',
        'channels': { 'Base': False, 'Censor': True},
        'post_op': censor_post_op,
    },
]

test_sets = [
    {
        'scene': 'Sequence',
        'channels': { 'Base': False, 'Censor': True, 'Text': False },
        'post_op': lambda f: downscale_video(f, 1, 'h264'),
    },
]

render_all(render_sets)
