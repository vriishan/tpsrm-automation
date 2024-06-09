import json

def read_json(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)

def write_json(data, file_path):
    with open(file_path, 'w') as file:
        json.dump(data, file)

def print_info(text):
    print('############################################################################')
    print(text)
    print('############################################################################')
