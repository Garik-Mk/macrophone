import os

def get_current_dir():
    return os.path.dirname(os.path.abspath(__file__))

def split_list(lst, chunk_size):
    return [lst[i:i + chunk_size] for i in range(0, len(lst), chunk_size)]