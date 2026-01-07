import os
import sys

# Test the rename function
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def read_paths(config_file):
    paths = {}
    with open(config_file, 'r') as f:
        for line in f:
            if '=' in line:
                var, val = line.strip().split('=', 1)
                paths[var.strip()] = val.strip().replace('\r', '')
    return paths

script_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(script_dir, 'path.txt')

print(f"Script directory: {script_dir}")
print(f"Config path: {config_path}")
print(f"Config exists: {os.path.exists(config_path)}")

paths = read_paths(config_path)
format_path = paths.get('FORMAT_PATH', '')

print(f"\nFORMAT_PATH: {format_path}")
print(f"FORMAT_PATH exists: {os.path.exists(format_path)}")

if format_path and os.path.exists(format_path):
    print(f"\nFiles in FORMAT_PATH:")
    for f in os.listdir(format_path):
        full_path = os.path.join(format_path, f)
        print(f"  - {f} (is_file: {os.path.isfile(full_path)})")
