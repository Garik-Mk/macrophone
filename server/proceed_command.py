"""Process hotkey command. Other types of commands will be added soon"""
from pyautogui import hotkey

def get_keys_out_of_str(data: str) -> list[str]:
    return data.decode('utf-8').split('+')

def apply_hotkey(commands: str):
    commands = get_keys_out_of_str(commands)
    hotkey(*commands)