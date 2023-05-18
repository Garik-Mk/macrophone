"""Key press handler. TODO read configurations from mkb file.
It's also crossplatform with Windows, OSX, and Ubuntu LTS."""
import sys
from pyautogui import hotkey

def proceed_command(command_id: int):
    """Proceed command"""
    match command_id:
        case 1:
            hotkey('ctrl', 'shift', 'esc')

def handler(command):
    """Validate and handle command"""
    proceed_command(int(command))

if __name__ == '__main__':
    proceed_command(sys.argv[1])
