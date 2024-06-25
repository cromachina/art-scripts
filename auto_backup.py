import pathlib
import shutil
import re
import os
from datetime import datetime
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

backup_limit = 6
file_match = re.compile(r'.*\.sai2')
recursive = True
scan_directory = pathlib.Path('/home/cro/aux/art')
backup_directory = pathlib.Path('/home/cro/aux/backups')

def backup_file(src_path):
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S%f')
    src_path = pathlib.Path(src_path)
    backup_path = backup_directory / f'{src_path.stem}.{timestamp}{src_path.suffix}'
    temp_path = backup_path.with_name(f'{backup_path.name}.tmp')
    # Move first because it's atomic. Move back to src to prevent recursive `on_closed` calls.
    shutil.move(src_path, backup_path)
    shutil.copy2(backup_path, temp_path)
    shutil.move(temp_path, src_path)
    print(f'backup {src_path} -> {backup_path}')

def clean_backups(src_path):
    src_stem = pathlib.Path(src_path).stem
    matcher = re.compile(f'{src_stem}\\.\\d+\\.*')
    files = os.listdir(backup_directory)
    files = [file for file in files if matcher.match(file)]
    if len(files) <= backup_limit:
        return
    files.sort()
    files = files[:-backup_limit]
    for file in files:
        (pathlib.Path(backup_directory) / file).unlink(missing_ok=True)

class EventHandler(FileSystemEventHandler):
    def __init__(self) -> None:
        super().__init__()

    def on_closed(self, event):
        if file_match.match(event.src_path) is None:
            return
        src_path = pathlib.Path(event.src_path)
        if src_path.is_relative_to(backup_directory):
            return
        backup_file(src_path)
        clean_backups(src_path)

observer = Observer()
observer.schedule(EventHandler(), str(scan_directory), recursive=recursive)
observer.start()
try:
    while observer.is_alive():
        observer.join(1)
finally:
    observer.stop()
    observer.join()