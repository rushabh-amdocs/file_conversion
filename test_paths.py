import os

def read_paths(config_file):
    paths = {}
    with open(config_file, 'r') as f:
        for line in f:
            if '=' in line:
                var, val = line.strip().split('=', 1)
                paths[var.strip()] = val.strip().replace('\r', '')
    return paths

paths = read_paths('path.txt')
print('FORMAT_PATH:', repr(paths.get('FORMAT_PATH', '')))
print('Path exists:', os.path.exists(paths.get('FORMAT_PATH', '')))

format_path = paths.get('FORMAT_PATH', '')
if format_path:
    print('Path normalized:', os.path.normpath(format_path))
    try:
        files = os.listdir(format_path)
        print('Files in dir:', files[:5] if len(files) > 5 else files)
    except Exception as e:
        print('Error listing files:', e)
else:
    print('FORMAT_PATH is empty!')

print('\nAll paths:')
for key, value in paths.items():
    print(f'  {key}: {repr(value)}')
