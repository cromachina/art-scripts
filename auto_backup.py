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
    backup_path = backup_directory / src_path.relative_to(scan_directory).parent / f'{src_path.stem}.{timestamp}{src_path.suffix}'
    temp_path = backup_path.with_name(f'{backup_path.name}.tmp')
    # Move first because it's atomic. Move back to src to prevent recursive `on_closed` calls.
    os.makedirs(backup_path.parent, exist_ok=True)
    shutil.move(src_path, backup_path)
    shutil.copy2(backup_path, temp_path)
    shutil.move(temp_path, src_path)
    print(f'backup {src_path} -> {backup_path}')

    # Cleanup old backups.
    matcher = re.compile(f'{src_path.stem}\\.\\d+\\.*')
    sub_backup_dir = backup_path.parent
    files = os.listdir(sub_backup_dir)
    files = [file for file in files if matcher.match(file)]
    if len(files) <= backup_limit:
        return
    files.sort()
    files = files[:-backup_limit]
    for file in files:
        (pathlib.Path(sub_backup_dir) / file).unlink(missing_ok=True)

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

observer = Observer()
observer.schedule(EventHandler(), str(scan_directory), recursive=recursive)
observer.start()
try:
    while observer.is_alive():
        observer.join(1)
finally:
    observer.stop()
    observer.join()