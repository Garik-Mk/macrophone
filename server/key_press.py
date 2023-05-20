"""Key press handler.
It's also crossplatform with Windows, OSX, and Ubuntu LTS."""

from pyautogui import hotkey
try:
    from mkb_io import read_file, parse_commands
except ModuleNotFoundError:
    from server.mkb_io import read_file, parse_commands


def handler(command, commands_file: str):
    """Validate and handle command"""
    try:
        command = int(command)
    except Exception:
        print('Error while processing command')
        return

    commands = read_file(commands_file)
    commands_list = parse_commands(commands)

    if command > len(commands_list.keys()) or command < 0:
        print('Command not found')
        return
    
    print(commands_list[str(command)][1])
    hotkey(*commands_list[str(command)][0])
