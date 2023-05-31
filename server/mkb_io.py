"""Mkb input-output library"""
import os.path
try:
    from utils import get_current_dir
except ModuleNotFoundError:
    from server.utils import get_current_dir

def read_file(file_path):
    """Read commands from file"""
    try:
        with open(get_current_dir() + os.path.normpath(file_path), 'r', encoding='utf-8') as file:
            commands = file.readlines()
    except OSError:
        with open(os.path.normpath(file_path), 'r', encoding='utf-8') as file:
            commands = file.readlines()
    return commands


class Command():
    def __init__(self, command) -> None:
        command = command.split(':')
        self.keys = command[0]
        self.name = command[1]
        self.background_color = [int(i)/255 for i in command[2].split(',')]     #TODO remove /255 and change mkb format from 255,255,255 to 1,1,1
        self.font_color = [int(i)/255 for i in command[3].split(',')]           #TODO add default colors

    def __repr__(self) -> str:
        return f'Name: {self.name}, Keys: {self.keys};'


def parse_mkb(file_path) -> dict:           # Maybe will be changed to json format
    """Read all layouts and return dict with all of them"""
    commands_dict = {}
    commands = read_file(file_path)
    current_layout = ''
    for each_command in commands:
        if each_command.startswith('<'):
            commands_dict[each_command] = []
            current_layout = each_command
        else:
            commands_dict[current_layout].append(Command(each_command))
    return commands_dict
