"""
Script to add comprehensive logging to scripts_ui.py similar to workflows.py
This script will:
1. Update all run_* functions to return (output, success) tuples
2. Add log_command_output calls to all functions
3. Update all route handlers to handle tuple returns
"""

import re

def update_scripts_ui_logging():
    """Update scripts_ui.py with comprehensive logging"""
    
    with open('scripts_ui.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    # The functions to update and their operation names
    functions_to_log = {
        'run_copy_bulk': 'COPY BULK',
        'run_dataturn': 'DATATURN',
        'run_expfd_creation': 'EXPFD CREATION',
        'run_bulk_expfd': 'BULK EXPFD',
        'run_bulk_dataturn': 'BULK DATATURN',
        'run_bulk_conversion': 'BULK CONVERSION',
        'run_create_folder': 'CREATE FOLDER',
        'run_folder_open': 'OPEN FOLDERS',
        'run_copy_s3': 'COPY S3',
        'run_ff_mapping': 'FF MAPPING'
    }
    
    # Pattern to find each function and update its return statements
    for func_name, op_name in functions_to_log.items():
        print(f"Processing {func_name}...")
        
        # Find the function
        func_pattern = rf'(def {func_name}\([^)]+\):.*?)(^def |\Z)'
        match = re.search(func_pattern, content, re.MULTILINE | re.DOTALL)
        
        if match:
            func_body = match.group(1)
            func_start = match.start(1)
            func_end = match.end(1)
            
            # Check if already has log_command_output
            if 'log_command_output' in func_body:
                print(f"  - {func_name} already has logging")
                continue
            
            print(f"  - Found {func_name}, adding logging...")
            
            # Find all return statements
            # Look for: return 'string' or return f'string' or return '\n'.join(output)
            return_pattern = r"return (.*?)(?:\n|$)"
            
            # We'll need to update the logic to:
            # 1. Store output in result_output variable
            # 2. Call log_command_output
            # 3. Return (result_output, success_boolean)
            
    print("\nDone!")

if __name__ == '__main__':
    update_scripts_ui_logging()
