"""It's also crossplatform with Windows, OSX, and Ubuntu LTS."""

from pyautogui import press, typewrite, hotkey

press('a')
typewrite('quick brown fox')
hotkey('ctrl', 'w')
