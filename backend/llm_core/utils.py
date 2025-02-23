# Traverse all code files & preserve structure in a root directory

import os
import pprint
import json

def traverse_directory(root_dir):
    def read_file(file_path):
        with open(file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def traverse(current_path):
        if os.path.isdir(current_path):
            folder_dict = {}
            for item in os.listdir(current_path):
                item_path = os.path.join(current_path, item)
                folder_dict[item] = traverse(item_path)
            # Remove any empty subfolders (those that lead to None)
            folder_dict = {k: v for k, v in folder_dict.items() if v is not None}
            return folder_dict if folder_dict else None
        else:
            # Assuming code files have extensions like .py, .js, .java, etc.
            file_ext = current_path.split('.')[-1]
            if file_ext in ['py', 'js', 'java', 'cpp', 'c']:
                return read_file(current_path)
            return None  # Ignore non-code files
    
    return json.dumps(traverse(root_dir), indent=4)

# Example Usage:
# root_directory = r"/Users/zhuxiaoai/Desktop/CodeScribe/backend"
# directory_structure = traverse_directory(root_directory)
# pprint.pprint(directory_structure, indent=4)