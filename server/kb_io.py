"""Mkb input-output library"""
import os.path
import json
try:
    from utils import get_current_dir
except ModuleNotFoundError:
    from server.utils import get_current_dir

def parse_json_kb(file_path) -> dict:
    try:
        try:
            with open(get_current_dir() + os.path.normpath(file_path), 'r', encoding='utf-8') as read_file:
                data = json.load(read_file)
        except OSError:
            with open(os.path.normpath(file_path), 'r', encoding='utf-8') as read_file:
                data = json.load(read_file)
    except ValueError:  # includes simplejson.decoder.JSONDecodeError
        print('Decoding JSON has failed')
        return {}
    except FileNotFoundError:
        print("File don't exist")
        return {}
    return data


def save_kb(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as write_file:
        json.dump(data, write_file, indent=4)
