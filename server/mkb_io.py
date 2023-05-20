"""Mkb input-output library"""
import os.path
try:
    from utils import get_current_dir
except ModuleNotFoundError:
    from server.utils import get_current_dir

def read_file(file_path):
    """Read commands from file"""
    with open(get_current_dir() + os.path.normpath(file_path), 'r', encoding='utf-8') as file:
        commands = file.readlines()
    return commands

def parse_commands(commands):
    """From 2:ctrl+b:Brush make {2: ('ctrl+b', 'Brush')}"""
    result_commands = {}
    for each_command in commands:
        command_id, keys, name = each_command.split(':')
        keys = keys.split('+')
        result_commands[command_id] = (keys, name)
    return result_commands
