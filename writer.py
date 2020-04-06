from pathlib import Path, PurePath
from os import makedirs, remove, path

class writer:

    def __init__(self):
        self.save_dir = PurePath(Path(__file__).parent.absolute(), '..')
        pass

    def set_save_dir(self, new_save_dir):
        self.save_dir = new_save_dir

    def append_to_file(self, line, filename):
        makedirs(self.save_dir, exist_ok=True)
        file = PurePath(self.save_dir, filename + '.csv')
        with open(file, 'a', encoding='utf-8') as file:
            file.write(line)

    def write_buffer_to_file(self, linearray, filename):
        makedirs(self.save_dir, exist_ok=True)
        file = PurePath(self.save_dir, filename + '.csv')
        start = 1 if path.isfile(file) else 0
        with open(file, 'a', encoding='utf-8') as file:
            file.writelines(linearray[start:])
