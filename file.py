import os
import shutil
import subprocess
import traceback
import time
import logging
import datetime
from flask import Flask, render_template_string, request, redirect, url_for

# Global variable to track current log date
_current_log_date = None

# Configure logging
def setup_logging():
    """Setup logging configuration with timestamps - supports daily log rotation"""
    global _current_log_date
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create log file with current date
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    log_filename = f"SmartFile_Converter_{current_date}.log"
    log_filepath = os.path.join(log_dir, log_filename)
    
    # Create a custom logger for our application only
    logger = logging.getLogger('SmartFile_Converter')
    logger.setLevel(logging.INFO)
    logger.propagate = False  # Don't propagate to root logger
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    
    # Create file handler with custom format
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    
    # Add only file handler (no console output to avoid cluttering)
    logger.addHandler(file_handler)
    
    # Disable Flask's werkzeug logger from writing to our log
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
    
    # Update current log date
    _current_log_date = current_date
    
    # Write initial log entry to confirm logging is working
    logger.info("="*60)
    logger.info(f"File.py Application Started - {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"Log file: {log_filepath}")
    logger.info("="*60)
    
    return logger

def check_log_rotation():
    """Check if we need to rotate to a new log file (new day)"""
    global _current_log_date, logger
    
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    if _current_log_date != current_date:
        # Date has changed, create new log file
        logger = setup_logging()

# Initialize logger
logger = setup_logging()

def strip_html_tags(text):
    """Remove HTML span tags and other HTML formatting from text"""
    import re
    # Remove HTML span tags with all attributes
    clean_text = re.sub(r'<span[^>]*>', '', text)
    clean_text = re.sub(r'</span>', '', clean_text)
    # Remove any other HTML tags
    clean_text = re.sub(r'<[^>]+>', '', clean_text)
    return clean_text

def log_command_output(operation_name, command, output, success=True):
    """Log command outputs that appear in UI output blocks"""
    # Check if we need to rotate to a new log file (daily rotation)
    check_log_rotation()
    
    # Strip HTML tags for clean log output
    clean_output = strip_html_tags(output)
    
    log_entry = f"\n{'='*60}\n"
    log_entry += f"OPERATION: {operation_name}\n"
    log_entry += f"TIMESTAMP: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    if command:
        log_entry += f"COMMAND: {command}\n"
    log_entry += f"STATUS: {'SUCCESS' if success else 'FAILED'}\n"
    log_entry += f"{'='*60}\n"
    log_entry += f"{clean_output}\n"
    log_entry += f"{'='*60}\n"
    
    logger.info(log_entry)
 
def read_paths(config_file):
    paths = {}
    with open(config_file, 'r') as f:
        for line in f:
            if '=' in line:
                var, val = line.strip().split('=', 1)
                paths[var.strip()] = val.strip().replace('\r', '')
    return paths
 
def rename_file(folder_path, old_filename, new_name):
    try:
        if not folder_path:
            error_output = 'Error: Folder path is empty. Please check your path.txt configuration.'
            log_command_output("RENAME FILE", f"Rename {old_filename} to {new_name}.ff", error_output, False)
            return error_output
        if not os.path.exists(folder_path):
            error_output = f'Error: Folder path does not exist: {folder_path}'
            log_command_output("RENAME FILE", f"Rename {old_filename} to {new_name}.ff", error_output, False)
            return error_output
        if not old_filename:
            error_output = 'Error: Please select a file to rename.'
            log_command_output("RENAME FILE", "Rename operation", error_output, False)
            return error_output
        if not new_name:
            error_output = 'Error: Please provide a new name for the file.'
            log_command_output("RENAME FILE", f"Rename {old_filename}", error_output, False)
            return error_output
        
        # Retry logic to handle file system delays
        max_retries = 3
        retry_delay = 0.5  # seconds
        
        for attempt in range(max_retries):
            try:
                src = os.path.join(folder_path, old_filename)
                
                if not os.path.exists(src):
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    error_output = f'Error: File not found: {old_filename}'
                    log_command_output("RENAME FILE", f"Rename {old_filename} to {new_name}.ff", error_output, False)
                    return error_output
                
                dst = os.path.join(folder_path, f'{new_name}.ff')
                
                # Delete destination file if it already exists (override mode)
                if os.path.exists(dst):
                    os.remove(dst)
                    msg = f"[Override] Removed existing file: '{new_name}.ff'\n"
                else:
                    msg = ""
                
                os.rename(src, dst)
                result = msg + f"✅ Successfully renamed '{old_filename}' to '{new_name}.ff'"
                
                # Log successful operation
                log_command_output(
                    "RENAME FILE",
                    f"Rename {old_filename} to {new_name}.ff",
                    result,
                    True
                )
                
                return result
            except (PermissionError, FileNotFoundError) as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise
                
    except Exception as e:
        error_output = f'Error in rename_file: {e}\nTraceback:\n{traceback.format_exc()}'
        log_command_output("RENAME FILE", f"Rename {old_filename} to {new_name}.ff", error_output, False)
        return error_output
 
def run_file_modify(new_name, filetype, condition_type):
    try:
        # Use os.getcwd() to get the actual working directory instead of __file__
        script_dir = os.getcwd()
        file_modify_path = os.path.join(script_dir, 'File_modify.py')
        
        if not os.path.exists(file_modify_path):
            error_output = f'Error: File_modify.py not found at {file_modify_path}'
            log_command_output("FILE MODIFY", f"Modify {new_name}", error_output, False)
            return error_output
        
        # Retry logic to handle file system delays
        max_retries = 3
        retry_delay = 0.5  # seconds
        
        for attempt in range(max_retries):
            try:
                # Create input for the subprocess (simulating user input)
                # File_modify.py asks for filetype first, then condition_type
                user_input = f"{filetype}\n{condition_type}\n"
                
                debug_msg = f"[File Override Mode: ON] Existing .ff files will be overwritten.\n\n"
                debug_msg += f"Sending inputs:\n  File Type: {filetype}\n  Condition Type: {condition_type}\n\n"
                
                result = subprocess.run(
                    ['python', file_modify_path, new_name], 
                    input=user_input,
                    capture_output=True, 
                    text=True, 
                    cwd=script_dir
                )
                output = debug_msg + result.stdout
                if result.stderr:
                    output += '\n[Error]\n' + result.stderr
                
                # Log the operation
                log_command_output(
                    "FILE MODIFY",
                    f"python File_modify.py {new_name}",
                    output,
                    result.returncode == 0
                )
                
                return output
            except (subprocess.TimeoutExpired, FileNotFoundError, PermissionError) as e:
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise
                
    except Exception as e:
        error_output = f'Error running File_modify.py: {e}\nTraceback:\n{traceback.format_exc()}'
        log_command_output("FILE MODIFY", f"Modify {new_name}", error_output, False)
        return error_output
        return f'Error running File_modify.py: {e}\n{traceback.format_exc()}'
 
def run_rexx(filename, rec_fm, rec_len, key_beg, key_pic, rdw_flag=''):
    try:
        # Use os.getcwd() to get the actual working directory instead of __file__
        script_dir = os.getcwd()
        rexx_path = os.path.join(script_dir, 'RoysEbcdicRecTypesV6.rexx')
        
        if not os.path.exists(rexx_path):
            error_output = f'Error: RoysEbcdicRecTypesV6.rexx not found at {rexx_path}'
            log_command_output("ROY'S TOOL", f"Process {filename}", error_output, False)
            return error_output
        
        # Read paths to get the input file path
        config_path = os.path.join(script_dir, 'path.txt')
        paths = read_paths(config_path)
        input_path = paths.get('INPUT_PATH', '')
        
        if not input_path or not os.path.exists(input_path):
            error_output = f'Error: INPUT_PATH is invalid or does not exist: {input_path}'
            log_command_output("ROY'S TOOL", f"Process {filename}", error_output, False)
            return error_output
        
        input_file = os.path.join(input_path, filename + '.txt')
        
        if not os.path.exists(input_file):
            error_output = f'Error: Input file not found: {input_file}'
            log_command_output("ROY'S TOOL", f"Process {filename}", error_output, False)
            return error_output
        
        # Create input for the subprocess (simulating user input)
        # Roy's tool prompts in this order:
        # 1. Input filename
        # 2. Record format (F or V)
        # 3. Record length
        # 4. Key beginning position
        # 5. Key PIC clause
        user_input = f"{input_file}\n{rec_fm}\n{rec_len}\n{key_beg}\n{key_pic}\n"
        
        debug_msg = f"[File Override Mode: ON] Output files will be overwritten if they exist.\n\n"
        debug_msg += f"Executing Roy's Tool with command-line parameters:\n"
        debug_msg += f"  Input File: {input_file}\n"
        debug_msg += f"  Record Format: {rec_fm}\n"
        debug_msg += f"  Record Length: {rec_len}\n"
        debug_msg += f"  Key Begin Position: {key_beg}\n"
        debug_msg += f"  Key PIC Clause: {key_pic}\n"
        if rdw_flag:
            debug_msg += f"  RDW Flag: --rdw\n"
        debug_msg += "\n"
        
        # Build command with optional RDW flag - use full path to rexx.exe
        rexx_exe = os.path.join(script_dir, 'rexx.exe')
        #rexx_exe='rexx.exe'
        if not os.path.exists(rexx_exe):
            error_output = f'Error: rexx.exe not found at {rexx_exe}'
            log_command_output("ROY'S TOOL", f"Process {filename}", error_output, False)
            return error_output
        
        # Build command with all parameters as command-line arguments
        cmd = [
            rexx_exe, 
            rexx_path,
            '--file', input_file,
            '--recfm', rec_fm,
            '--reclen', str(rec_len),
            '--keybeg', str(key_beg),
            '--keypic', key_pic
        ]
        
        if rdw_flag:
            cmd.append('--rdw')
        
        debug_msg += f"Command: {' '.join(cmd)}\n\n"
        
        result = subprocess.run(
            cmd,
            capture_output=True, 
            text=True
            #cwd=script_dir
        )
        output = debug_msg + result.stdout
        if result.stderr:
            output += '\n[Error]\n' + result.stderr
        if result.returncode != 0:
            output += f'\n[Exit Code: {result.returncode}]'
        
        # Log the operation
        log_command_output(
            "ROY'S TOOL",
            ' '.join(cmd),
            output,
            result.returncode == 0
        )
        
        return output
    except subprocess.TimeoutExpired:
        error_output = f'Error: REXX script timed out after 5 minutes'
        log_command_output("ROY'S TOOL", f"Process {filename}", error_output, False)
        return error_output
    except Exception as e:
        error_output = f'Error running RoysEbcdicRecTypesV6.rexx: {e}\n{traceback.format_exc()}'
        log_command_output("ROY'S TOOL", f"Process {filename}", error_output, False)
        return error_output
 
def run_dowitcher(paths, new_name, records=None, display=False, hex_display=False, input_display=False, particular_records=False):
    format_path = paths.get('FORMAT_PATH', '')
    input_path = paths.get('INPUT_PATH', '')
    output_path = paths.get('OUTPUT_PATH', '')
    log_path = paths.get('LOG_PATH', '')
    notepad_path = paths.get('NOTEPAD_PATH', '')
    source = paths.get('source', '')
    target = paths.get('target', '')
    
    # Validate critical paths
    if not format_path or not os.path.exists(format_path):
        return f'Error: FORMAT_PATH is invalid or does not exist: {format_path}'
    if not input_path or not os.path.exists(input_path):
        return f'Error: INPUT_PATH is invalid or does not exist: {input_path}'
    if not output_path or not os.path.exists(output_path):
        return f'Error: OUTPUT_PATH is invalid or does not exist: {output_path}'
    
    override_msg = "[File Override Mode: ON] Existing files in source/target folders will be cleared and overwritten.\n\n"
    
    # Use os.getcwd() to get the actual working directory
    script_dir = os.getcwd()
    dowitcher_exe = os.path.join(script_dir, 'dowitcher.exe')
    
    if not os.path.exists(dowitcher_exe):
        return f'Error: dowitcher.exe not found at {dowitcher_exe}'
    
    ff_file = os.path.join(format_path, new_name + '.ff')
    input_file = os.path.join(input_path, new_name + '.txt')
    output_file = os.path.join(output_path, new_name + '.txt')
    
    # Small delay to ensure file system has updated
    time.sleep(0.2)
    
    # Verify files exist before proceeding
    if not os.path.exists(ff_file):
        return f'Error: Format file not found: {ff_file}\nPlease make sure the file exists and try again.'
    if not display and not os.path.exists(input_file):
        return f'Error: Input file not found: {input_file}\nPlease make sure the file exists and try again.'
    
    cmd = [dowitcher_exe]
    if display:
        cmd.append('--display')
        if input_display:
            cmd.append('--source')
            cmd.extend(['--include-hex', '--include-field-number', '--include-field-offset'])
        if hex_display:
            cmd.append('--include-hex')
        cmd.extend(['--translation-table=IBM-037:ISO-8859-1', f'--format={ff_file}'])
        if input_display:
            cmd.append(input_file)
        else:
            cmd.append(output_file)
        if records:
            cmd.append(f'--records={records}')
    elif particular_records:
        cmd.extend(['--convert', '--translation-table=IBM-037:ISO-8859-1', f'--format={ff_file}', input_file, output_file, f'--log={log_path}', f'--records={records}'])
    else:
        cmd.extend(['--convert', '--translation-table=IBM-037:ISO-8859-1', f'--format={ff_file}', input_file, output_file, f'--log={log_path}'])
    try:
        # Use PIPE for both stdout and stderr, and merge them to get inline error messages
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        output = (override_msg if not display else "") + result.stdout
        
        # Log dowitcher command output
        operation_type = "DOWITCHER DISPLAY" if display else "DOWITCHER CONVERT"
        command_str = ' '.join(cmd)
        log_command_output(operation_type, command_str, output, result.returncode == 0)
        
    except Exception as e:
        output = (override_msg if not display else "") + f'Error executing dowitcher command: {e}\n'
        log_command_output("DOWITCHER ERROR", ' '.join(cmd), output, False)
    
    if not display:
        for folder in [source, target]:
            if folder and os.path.exists(folder):
                for f in os.listdir(folder):
                    file_path = os.path.join(folder, f)
                    if os.path.isfile(file_path):
                        os.remove(file_path)
        if target and os.path.exists(target):
            shutil.copy(output_file, target)
            shutil.copy(ff_file, target)
        if source and os.path.exists(source):
            shutil.copy(ff_file, source)
            shutil.copy(input_file, source)
        if output_path and os.path.exists(output_path):
            shutil.copy(ff_file, output_path)
    return output

def run_expfd_creation(copybook_names, expfd_path, copybook_path):
    """Run EXPFD creation from copybook files"""
    try:
        import re
        from datetime import datetime
        
        output = []
        output.append("="*60)
        output.append("EXPFD CREATION STARTED")
        output.append("="*60)
        output.append(f"Copybook Names: {', '.join(copybook_names)}")
        output.append(f"EXPFD Output Path: {expfd_path}")
        output.append(f"Copybook Path: {copybook_path}")
        output.append("")
        
        # Helper functions from EXPFD_creation.py
        def remove_88_and_values(copybook_content):
            keep_lines = []
            skip_mode = False
            lines = copybook_content.splitlines()
            
            for i, line in enumerate(lines):
                line = ' ' * 6 + line[6:]
                line = line[:72]
                stripped = line[7:72].lstrip()
                
                if re.match(r'^88\b', stripped):
                    skip_mode = True
                    continue
                
                if skip_mode:
                    if re.match(r'^\s*(01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42|43|44|45|46|47|48|49|77)\b', stripped):
                        skip_mode = False
                    else:
                        continue
                
                if not skip_mode:
                    keep_lines.append(line)
            
            return '\n'.join(keep_lines)
        
        def adjust_01_level(copybook_content):
            lines = copybook_content.splitlines()
            adjusted_lines = []
            
            for line in lines:
                if line.strip().startswith('*') or re.match(r'^\d{6}\*', line.strip()):
                    adjusted_lines.append(line)
                    continue
                
                stripped_line = line.lstrip()
                if stripped_line.startswith('01') and not line[7:9].strip() == '01':
                    adjusted_line = ' ' * 7 + stripped_line
                    adjusted_lines.append(adjusted_line)
                else:
                    adjusted_lines.append(line)
            
            return '\n'.join(adjusted_lines)
        
        def extract_columns(copybook_content):
            extracted_lines = []
            for line in copybook_content.splitlines():
                if not line.strip().startswith('*') and not re.match(r'^\d{6}\*', line.strip()):
                    if line[7:9].strip():
                        modified_line = '01' + line[9:72]
                    else:
                        modified_line = line[7:72]
                    extracted_lines.append(modified_line)
            return extracted_lines
        
        def check_and_replace_values(copybook_content):
            lines = copybook_content.splitlines()
            modified_lines = []
            lowest_column_position = None
            
            for line in lines:
                if not line.strip().startswith('*') and not re.match(r'^\d{6}\*', line.strip()):
                    if line[7:9].strip() == '01':
                        return lines
                    
                    stripped = line[7:72].lstrip()
                    match = re.match(r'^(02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42|43|44|45|46|47|48|49|77)\b', stripped)
                    if match:
                        column_position = line.find(match.group(0))
                        if column_position >= 7 and (lowest_column_position is None or column_position < lowest_column_position):
                            lowest_column_position = column_position
            
            for line in lines:
                if not line.strip().startswith('*') and not re.match(r'^\d{6}\*', line.strip()):
                    if lowest_column_position is not None:
                        stripped = line[7:72].lstrip()
                        match = re.match(r'^(02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42|43|44|45|46|47|48|49|77)\b', stripped)
                        if match and line.find(match.group(0)) == lowest_column_position:
                            modified_line = line[:7] + '01' + line[lowest_column_position + 2:]
                            modified_lines.append(modified_line)
                        else:
                            modified_lines.append(line)
                    else:
                        modified_lines.append(line)
                else:
                    modified_lines.append(line)
            
            return modified_lines
        
        # Process copybooks
        all_extracted_data = []
        header_lines = []
        
        for index, copybook_name in enumerate(copybook_names):
            copybook_file = os.path.join(copybook_path, copybook_name.strip())
            
            if not os.path.exists(copybook_file):
                output.append(f"❌ ERROR: Copybook file not found: {copybook_file}")
                continue
            
            try:
                with open(copybook_file, 'r') as f:
                    copybook_content = f.read()
                
                output.append(f"✅ Processing: {copybook_name}")
                
                filtered_content = remove_88_and_values(copybook_content)
                adjusted_content = adjust_01_level(filtered_content)
                modified_content = check_and_replace_values(adjusted_content)
                extracted_data = extract_columns('\n'.join(modified_content))
                all_extracted_data.extend(extracted_data)
                
                if index == 0:
                    current_timestamp = datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
                    header_lines = [
                        f"      * Generated by Python on {current_timestamp}",
                        f"      * Original source file: {os.path.basename(copybook_file)}",
                        f"      * Original SELECT source file: {os.path.basename(copybook_file)}",
                        f"        SELECT {os.path.splitext(os.path.basename(copybook_file))[0]} ASSIGN TO RA-G099."
                    ]
                
            except Exception as e:
                output.append(f"❌ ERROR processing {copybook_name}: {str(e)}")
                continue
        
        if not all_extracted_data:
            return '\n'.join(output) + "\n\n❌ ERROR: No data extracted from copybooks"
        
        # Write output file
        output_filename = os.path.join(expfd_path, f"{os.path.splitext(copybook_names[0].strip())[0]}.expfd")
        
        try:
            with open(output_filename, 'w') as f:
                for line in header_lines:
                    f.write(line + '\n')
                for line in all_extracted_data:
                    formatted_line = ' ' * 7 + line.ljust(65)
                    f.write(formatted_line + '\n')
            
            output.append("")
            output.append("="*60)
            output.append("EXPFD CREATION COMPLETED")
            output.append("="*60)
            output.append(f"✅ EXPFD file created: {output_filename}")
            output.append(f"📄 Total lines processed: {len(all_extracted_data)}")
            output.append("")
            
            # Log the operation
            log_command_output("EXPFD CREATION", f"Create EXPFD from {', '.join(copybook_names)}", '\n'.join(output), True)
            
        except Exception as e:
            error_msg = '\n'.join(output) + f"\n\n❌ ERROR writing EXPFD file: {str(e)}"
            log_command_output("EXPFD CREATION", f"Create EXPFD from {', '.join(copybook_names)}", error_msg, False)
            return error_msg
        
        return '\n'.join(output)
        
    except Exception as e:
        error_msg = f'Error running EXPFD creation: {e}\n{traceback.format_exc()}'
        log_command_output("EXPFD CREATION", "Create EXPFD", error_msg, False)
        return error_msg

def run_dataturn(expfd_name, config):
    """Run DataTurn script"""
    try:
        import subprocess
        
        output = []
        output.append("="*60)
        output.append("DATATURN OPERATION STARTED")
        output.append("="*60)
        output.append(f"EXPFD File Name: {expfd_name}")
        output.append("")
        
        # Get configuration - using paths from path.txt where available
        dataturn_exe = config.get('DATATURN_EXE_PATH', 'C:/Program Files/Anubex/DataTurn/bin/dataturn.exe')
        application = config.get('application', 'C:/File_conversion/occ')
        repo_name = f"{application}/repo/repoCBR2"  # Use application path from path.txt
        expfd_path = config.get('expfd', 'C:/File_conversion/occ/expfd')  # Use expfd from path.txt
        output_dir = f"{application}/FF_FILES/"  # Use FORMAT_PATH from path.txt
        config_file = config.get('DATATURN_CONFIG_FILE', 'rushabh.configuration')
        
        output.append(f"DataTurn Exe: {dataturn_exe}")
        output.append(f"Repository: {repo_name}")
        output.append(f"EXPFD Path: {expfd_path}")
        output.append(f"Output Directory: {output_dir}")
        output.append("")
        
        # Check if dataturn.exe exists
        if not os.path.exists(dataturn_exe):
            error_msg = '\n'.join(output) + f"\n❌ ERROR: DataTurn executable not found at: {dataturn_exe}"
            log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", error_msg, False)
            return error_msg
        
        # Check if expfd file exists
        expfd_file = os.path.join(expfd_path, f"{expfd_name}.expfd")
        if not os.path.exists(expfd_file):
            error_msg = '\n'.join(output) + f"\n❌ ERROR: EXPFD file not found: {expfd_file}"
            log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", error_msg, False)
            return error_msg
        
        # Prepare commands
        import_cmd = [
            dataturn_exe,
            '--repository-name', repo_name,
            '--import-data',
            '--input-dir', expfd_path,
            '--import-schema-type', 'FILE2FILE',
            '--import-schema-name', expfd_name,
            f'{expfd_name}.expfd',
            '--initialize',
            '--create-repository',
            '--configuration-file', config_file
        ]
        
        generate_cmd = [
            dataturn_exe,
            '--generate',
            '--repository-name', repo_name,
            '--generation-target', 'DowitcherFileFormat',
            '--generation-output-directory', output_dir,
            '--configuration-file', config_file
        ]
        
        output.append("Step 1: Importing data to repository...")
        output.append(f"Command: {' '.join(import_cmd)}")
        output.append("")
        
        # Run import command
        try:
            result = subprocess.run(import_cmd, capture_output=True, text=True)
            output.append("Import Output:")
            output.append(result.stdout if result.stdout else "(no output)")
            if result.stderr:
                output.append("Import Errors:")
                output.append(result.stderr)
            output.append(f"Import Exit Code: {result.returncode}")
            output.append("")
            
            if result.returncode == 0:
                output.append("✅ Import completed successfully")
            else:
                output.append(f"⚠️  Import completed with exit code {result.returncode}")
        except subprocess.TimeoutExpired:
            error_msg = '\n'.join(output) + "\n❌ ERROR: Import command timed out after 5 minutes"
            log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", error_msg, False)
            return error_msg
        except Exception as e:
            error_msg = '\n'.join(output) + f"\n❌ ERROR during import: {str(e)}"
            log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", error_msg, False)
            return error_msg
        
        output.append("")
        output.append("Step 2: Generating Dowitcher file format...")
        output.append(f"Command: {' '.join(generate_cmd)}")
        output.append("")
        
        # Run generate command
        try:
            result = subprocess.run(generate_cmd, capture_output=True, text=True)
            output.append("Generate Output:")
            output.append(result.stdout if result.stdout else "(no output)")
            if result.stderr:
                output.append("Generate Errors:")
                output.append(result.stderr)
            output.append(f"Generate Exit Code: {result.returncode}")
            output.append("")
            
            if result.returncode == 0:
                output.append("✅ Generation completed successfully")
            else:
                output.append(f"⚠️  Generation completed with exit code {result.returncode}")
        except subprocess.TimeoutExpired:
            error_msg = '\n'.join(output) + "\n❌ ERROR: Generate command timed out after 5 minutes"
            log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", error_msg, False)
            return error_msg
        except Exception as e:
            error_msg = '\n'.join(output) + f"\n❌ ERROR during generation: {str(e)}"
            log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", error_msg, False)
            return error_msg
        
        output.append("")
        output.append("="*60)
        output.append("DATATURN OPERATION COMPLETED")
        output.append("="*60)
        

        # Remove repository after processing
        if os.path.exists(repo_name):
                    try:
                        # Get the parent repository directory
                        repo_parent = os.path.dirname(repo_name)
                        if os.path.exists(repo_parent):
                            shutil.rmtree(repo_parent)
                            output.append("  🗑️  Repository Cleaned")
                    except Exception as e:
                        output.append(f"  ⚠️  Warning: Could not delete repository folder: {str(e)}")

        final_output = '\n'.join(output)
        
        # Log the operation
        log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", final_output, True)
        
        return final_output
        
    except Exception as e:
        error_msg = f'Error running DataTurn: {e}\n{traceback.format_exc()}'
        log_command_output("DATATURN", f"Run DataTurn for {expfd_name}", error_msg, False)
        return error_msg
 
app = Flask(__name__)
TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SmartFile Converter</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: rgba(37, 99, 235, 0.2);
            --shadow: rgba(0, 0, 0, 0.3);
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }
12
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }

        .container {
            max-width: 1000px;
            margin: 20px auto;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 20px 40px var(--shadow);
            padding: 40px;
            position: relative;
            overflow: hidden;
        }

        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--primary-gradient);
        }

        h1 {
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
        }

        .form-group {
            margin-bottom: 25px;
            min-width: 0;
        }

        label {
            display: block;
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        input[type="text"] {
            width: 100%;
            max-width: 100%;
            padding: 15px 20px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s ease;
            outline: none;
            box-sizing: border-box;
        }

        input[type="text"]:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            transform: translateY(-2px);
        }

        .input-row {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 30px;
            align-items: end;
        }

        .actions-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 15px;
            margin: 30px 0;
        }

        .btn-primary, .btn-secondary, .btn-success, .btn-info, 
        .btn-warning, .btn-danger, .btn-dark, .btn-light {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            padding: 15px 20px;
            border: none;
            border-radius: 12px;
            font-size: 0.95rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            position: relative;
            overflow: hidden;
            text-decoration: none;
            color: white;
            height: 60px;
            max-height: 60px;
            line-height: normal;
        }

        a.btn-primary, a.btn-secondary, a.btn-success, a.btn-info,
        a.btn-warning, a.btn-danger, a.btn-dark, a.btn-light {
            height: 60px !important;
            max-height: 60px !important;
            min-height: 60px !important;
            padding: 15px 20px !important;
            box-sizing: border-box !important;
        }

        .btn-primary { background: var(--primary-gradient); }
        .btn-secondary { background: var(--primary-gradient); }
        .btn-success { background: var(--primary-gradient); }
        .btn-info { background: var(--primary-gradient); }
        .btn-warning { background: var(--primary-gradient); }
        .btn-danger { background: var(--primary-gradient); }
        .btn-dark { background: var(--primary-gradient); }
        .btn-light { background: var(--primary-gradient); }

        .btn-primary:hover, .btn-secondary:hover, .btn-success:hover, .btn-info:hover,
        .btn-warning:hover, .btn-danger:hover, .btn-dark:hover, .btn-light:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .btn-icon {
            font-size: 1.2rem;
            display: inline-block;
            line-height: 1;
        }

        .btn-text {
            flex: 1;
            line-height: 1.2;
            text-align: center;
        }

        .output-section {
            margin-top: 40px;
        }

        .output-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .output-controls {
            display: flex;
            gap: 10px;
        }

        .btn-mini {
            padding: 8px 16px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-secondary);
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-mini:hover {
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }

        .output-container {
            position: relative;
        }

        .output-box {
            padding: 0;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            min-height: 450px;
            max-height: none;
            resize: both;
            overflow: auto;
            position: relative;
        }

        .output-content {
            padding: 20px;
            white-space: pre;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            color: var(--text-primary);
            margin: 0;
            min-width: max-content;
            overflow-wrap: normal;
            word-break: normal;
        }

        .output-box.success {
            border-color: var(--accent-color);
        }

        .output-box::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }

        .output-box::-webkit-scrollbar-track {
            background: var(--bg-primary);
            border-radius: 6px;
        }

        .output-box::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 6px;
        }

        .output-box::-webkit-scrollbar-thumb:hover {
            background: var(--accent-color);
        }

        .output-box::-webkit-scrollbar-corner {
            background: var(--bg-primary);
        }

        .resize-handle {
            position: absolute;
            bottom: 0;
            right: 0;
            width: 20px;
            height: 20px;
            background: var(--border);
            cursor: nw-resize;
            border-radius: 12px 0 12px 0;
        }

        .resize-handle:hover {
            background: var(--accent-color);
        }

        textarea#output {
            width: 100%;
            height: 450px;
            padding: 20px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            resize: vertical;
            outline: none;
            transition: border-color 0.3s ease;
            overflow: auto;
            white-space: pre;
            word-wrap: normal;
        }

        textarea#output:focus {
            border-color: var(--primary-color);
        }

        .output-status {
            position: absolute;
            bottom: 10px;
            right: 15px;
            background: var(--bg-primary);
            color: var(--text-secondary);
            padding: 5px 10px;
            border-radius: 6px;
            font-size: 0.8rem;
            opacity: 0.8;
        }

        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(5px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }

        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 4px solid rgba(37, 99, 235, 0.2);
            border-top: 4px solid #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--bg-card);
            color: var(--text-primary);
            padding: 15px 25px;
            border-radius: 10px;
            border-left: 4px solid var(--primary-color);
            box-shadow: 0 10px 25px var(--shadow);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1001;
        }

        .toast.show {
            transform: translateX(0);
        }

        [data-tooltip] {
            position: relative;
        }

        [data-tooltip]:hover::after {
            content: attr(data-tooltip);
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            background: var(--bg-primary);
            color: var(--text-primary);
            padding: 8px 12px;
            border-radius: 6px;
            font-size: 0.8rem;
            white-space: nowrap;
            z-index: 1000;
            margin-bottom: 5px;
            box-shadow: 0 5px 15px var(--shadow);
        }

        [data-tooltip]:hover::before {
            content: '';
            position: absolute;
            bottom: 100%;
            left: 50%;
            transform: translateX(-50%);
            width: 0;
            height: 0;
            border-left: 5px solid transparent;
            border-right: 5px solid transparent;
            border-top: 5px solid var(--bg-primary);
            margin-bottom: -5px;
            z-index: 1000;
        }

        @media (max-width: 768px) {
            .container {
                margin: 10px;
                padding: 20px;
            }
            
            .input-row {
                grid-template-columns: 1fr;
            }
            
            .actions-grid {
                grid-template-columns: 1fr;
            }
            
            h1 {
                font-size: 2rem;
            }
        }
    </style>
    <script>
        function showLoading() {
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay) {
                loadingOverlay.style.display = 'flex';
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('conversionForm');
            const loadingOverlay = document.getElementById('loadingOverlay');
            const clearBtn = document.getElementById('clearOutput');
            const copyBtn = document.getElementById('copyOutput');
            const output = document.getElementById('output');
            const toast = document.getElementById('toast');

            // Show toast notification
            function showToast(message) {
                if (toast) {
                    toast.textContent = message;
                    toast.classList.add('show');
                    setTimeout(() => {
                        toast.classList.remove('show');
                    }, 3000);
                }
            }

            // Show loading on form submit (backup handler)
            if (form && loadingOverlay) {
                form.addEventListener('submit', function(e) {
                    loadingOverlay.style.display = 'flex';
                });
            }

            // Add click handlers to all submit buttons for loading
            const submitButtons = form ? form.querySelectorAll('button[type="submit"]') : [];
            submitButtons.forEach(function(button) {
                button.addEventListener('click', function() {
                    if (loadingOverlay) {
                        loadingOverlay.style.display = 'flex';
                    }
                });
            });

            // Clear output - attach event listener
            if (clearBtn) {
                clearBtn.addEventListener('click', function() {
                    const outputEl = document.getElementById('output');
                    if (outputEl) {
                        outputEl.textContent = '';
                        showToast('Output cleared');
                    }
                });
            }

            // Copy output - attach event listener
            if (copyBtn) {
                copyBtn.addEventListener('click', function() {
                    const outputEl = document.getElementById('output');
                    if (outputEl) {
                        const textToCopy = outputEl.textContent;
                        navigator.clipboard.writeText(textToCopy).then(function() {
                            showToast('Output copied to clipboard');
                        }).catch(function(err) {
                            // Fallback for older browsers
                            const textArea = document.createElement('textarea');
                            textArea.value = textToCopy;
                            textArea.style.position = 'fixed';
                            textArea.style.left = '-999999px';
                            document.body.appendChild(textArea);
                            textArea.select();
                            try {
                                document.execCommand('copy');
                                showToast('Output copied to clipboard');
                            } catch (e) {
                                showToast('Failed to copy');
                            }
                            document.body.removeChild(textArea);
                        });
                    }
                });
            }

            // Hide loading overlay when page loads
            window.addEventListener('load', function() {
                if (loadingOverlay) {
                    loadingOverlay.style.display = 'none';
                }
            });
        });

        function scrollToTop() {
            const outputBox = document.querySelector('.output-box');
            if (outputBox) {
                outputBox.scrollTop = 0;
                outputBox.scrollLeft = 0;
            }
        }

        function scrollToBottom() {
            const outputBox = document.querySelector('.output-box');
            if (outputBox) {
                outputBox.scrollTop = outputBox.scrollHeight;
            }
        }

        function resetOutputSize() {
            const outputBox = document.querySelector('.output-box');
            if (outputBox) {
                outputBox.style.width = 'auto';
                outputBox.style.height = '450px';
            }
        }

        // Colorize output for errors, warnings, and success messages
        function colorizeOutput() {
            const outputEl = document.getElementById('output');
            if (outputEl) {
                let text = outputEl.innerHTML;
                // Colorize error lines (red)
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bError\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\berror\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bfailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                // Colorize warning lines (yellow)
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWarning\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                // Colorize success lines (green)
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                outputEl.innerHTML = text;
            }
        }

        // Run colorization when page loads
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
</head>
<body>
<div class="container">
    <h1>SmartFile Converter</h1>
    <form method="post" id="conversionForm" onsubmit="showLoading()">
        <div class="input-row">
            <div class="form-group">
                <label for="new_name">📁 File name (without .ff):</label>
                <input type="text" id="new_name" name="new_name" value="{{ new_name }}" 
                       placeholder="Enter your file name...">
            </div>
            <div class="form-group">
                <label for="records">📊 Records (optional):</label>
                <input type="text" id="records" name="records" value="{{ records }}" 
                       placeholder="e.g., 1-100">
            </div>
        </div>
        
        <div class="actions-grid">
            <button type="submit" name="action" value="expfd_creation" class="btn-primary" 
                    data-tooltip="Create EXPFD files from copybook definitions">
                <span class="btn-icon">📝</span>
                <span class="btn-text">Create EXPFD</span>
            </button>
            
            <button type="submit" name="action" value="dataturn" class="btn-primary" 
                    data-tooltip="Run DataTurn conversion process">
                <span class="btn-icon">🔄</span>
                <span class="btn-text">Run DataTurn</span>
            </button>
            
            <button type="submit" name="action" value="rename" class="btn-primary" 
                    data-tooltip="Rename the selected .FF file">
                <span class="btn-icon">🏷️</span>
                <span class="btn-text">Rename .FF File</span>
            </button>
            
            <button type="submit" name="action" value="modify" class="btn-secondary" 
                    data-tooltip="Modify the .FF file structure">
                <span class="btn-icon">✏️</span>
                <span class="btn-text">Modify .FF File</span>
            </button>
            
            <button type="submit" name="action" value="dowitcher" class="btn-success" 
                    data-tooltip="Execute Dowitcher conversion command">
                <span class="btn-icon">⚙️</span>
                <span class="btn-text">Run Dowitcher</span>
            </button>
            
            <button type="submit" name="action" value="display" class="btn-info" 
                    data-tooltip="Display formatted output">
                <span class="btn-icon">👁️</span>
                <span class="btn-text">Display Output</span>
            </button>
            
            <button type="submit" name="action" value="rexx" class="btn-warning" 
                    data-tooltip="Execute Roy's REXX tool">
                <span class="btn-icon">🔧</span>
                <span class="btn-text">Run Roys Tool</span>
            </button>
            
            <button type="submit" name="action" value="display_hex" class="btn-danger" 
                    data-tooltip="Display output with hexadecimal representation">
                <span class="btn-icon">🔢</span>
                <span class="btn-text">Display with Hex</span>
            </button>
            
            <button type="submit" name="action" value="particular_records" class="btn-dark" 
                    data-tooltip="Convert only specified records">
                <span class="btn-icon">📋</span>
                <span class="btn-text">Convert Records</span>
            </button>
            
            <button type="submit" name="action" value="input_display_hex" class="btn-light" 
                    data-tooltip="Display input with hex formatting">
                <span class="btn-icon">💾</span>
                <span class="btn-text">Input with Hex</span>
            </button>
            
            <button type="submit" name="action" value="update_paths" class="btn-primary" 
                    data-tooltip="Update application paths in path.txt configuration">
                <span class="btn-icon">⚙️</span>
                <span class="btn-text">Update Paths</span>
            </button>
            
            <a href="/view_logs" class="btn-secondary"
                    data-tooltip="View application logs">
                <span class="btn-icon">📋</span>
                <span class="btn-text">View Logs</span>
            </a>
            
            <a href="/user_guide" class="btn-primary"
                    data-tooltip="Open user guide and documentation">
                <span class="btn-icon">📖</span>
                <span class="btn-text">User Guide</span>
            </a>
        </div>
    </form>
    
    {% if output %}
    <div class="output-section">
        <div class="output-header">
            <label for="output">📤 Command Output:</label>
        </div>
        <div class="output-box">
            <div class="output-content" id="output">{{ output }}</div>
            <div class="resize-handle" title="Drag to resize"></div>
        </div>
        <div style="text-align: center; margin-top: 10px; color: var(--text-secondary); font-size: 0.85rem;">
            💡 <strong>Tip:</strong> Drag the bottom-right corner to resize • Use scroll bars for navigation • Long lines will scroll horizontally
        </div>
    </div>
    {% endif %}
    
    <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid var(--border); color: var(--text-secondary); font-size: 0.9rem;">
        <p style="margin: 5px 0;">SmartFile Converter</p>
        <p style="margin: 5px 0;">Powered by Astadia TEAM</p>
    </div>
</div>

<div id="loadingOverlay" class="loading-overlay" style="display: none;">
    <div class="loading-spinner"></div>
    <p style="color: white; margin-top: 20px; font-size: 1.2rem; font-weight: 600;">Processing... Please wait</p>
</div>

<div id="toast" class="toast"></div>
</body>
</html>
'''

MODIFY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Modify .FF File - Configuration</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: rgba(37, 99, 235, 0.2);
            --shadow: rgba(0, 0, 0, 0.3);
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }

        .container {
            max-width: 1000px;
            margin: 20px auto;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 20px 40px var(--shadow);
            padding: 40px;
            position: relative;
            overflow: hidden;
        }

        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--secondary-gradient);
        }

        h1 {
            background: var(--secondary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
        }

        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 30px;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }

        .breadcrumb a {
            color: var(--accent);
            text-decoration: none;
            transition: color 0.2s;
        }

        .breadcrumb a:hover {
            color: var(--secondary-color);
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .help-text {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 5px;
            font-style: italic;
        }

        input[type="text"], select {
            width: 100%;
            padding: 15px 20px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s ease;
            outline: none;
        }

        input[type="text"]:focus, select:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            transform: translateY(-2px);
        }

        select {
            cursor: pointer;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23b8c5d1' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 15px center;
            padding-right: 40px;
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }

        .btn {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .btn-primary {
            background: var(--primary-gradient);
            color: white;
        }

        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 2px solid var(--border);
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .output-section {
            margin-top: 40px;
        }

        .output-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .output-controls {
            display: flex;
            gap: 10px;
        }

        .btn-mini {
            padding: 8px 16px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-secondary);
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-mini:hover {
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }

        .output-box {
            padding: 0;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            min-height: 450px;
            max-height: none;
            resize: both;
            overflow: auto;
            position: relative;
        }

        .output-content {
            padding: 20px;
            white-space: pre;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            color: var(--text-primary);
            margin: 0;
            min-width: max-content;
            overflow-wrap: normal;
            word-break: normal;
        }

        .output-box.success {
            border-color: var(--accent-color);
        }

        .output-box::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }

        .output-box::-webkit-scrollbar-track {
            background: var(--bg-primary);
            border-radius: 6px;
        }

        .output-box::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 6px;
        }

        .output-box::-webkit-scrollbar-thumb:hover {
            background: var(--accent-color);
        }

        .output-box::-webkit-scrollbar-corner {
            background: var(--bg-primary);
        }

        .resize-handle {
            position: absolute;
            bottom: 0;
            right: 0;
            width: 20px;
            height: 20px;
            background: var(--border);
            cursor: nw-resize;
            border-radius: 12px 0 12px 0;
        }

        .resize-handle:hover {
            background: var(--accent-color);
        }

        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(5px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }

        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 4px solid rgba(37, 99, 235, 0.2);
            border-top: 4px solid #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--bg-card);
            color: var(--text-primary);
            padding: 15px 25px;
            border-radius: 10px;
            border-left: 4px solid var(--primary-color);
            box-shadow: 0 10px 25px var(--shadow);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1001;
        }

        .toast.show {
            transform: translateX(0);
        }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('modifyForm');
            const loadingOverlay = document.getElementById('loadingOverlay');
            const clearBtn = document.getElementById('clearOutput');
            const copyBtn = document.getElementById('copyOutput');
            const output = document.getElementById('output');
            const toast = document.getElementById('toast');

            // Show loading on form submit
            if (form) {
                form.addEventListener('submit', function() {
                    loadingOverlay.style.display = 'flex';
                });
            }

            // Clear output
            if (clearBtn && output) {
                clearBtn.addEventListener('click', function() {
                    output.value = '';
                    showToast('Output cleared');
                });
            }

            // Copy output
            if (copyBtn && output) {
                copyBtn.addEventListener('click', function() {
                    output.select();
                    navigator.clipboard.writeText(output.value).then(function() {
                        showToast('Output copied to clipboard');
                    }).catch(function() {
                        // Fallback for older browsers
                        document.execCommand('copy');
                        showToast('Output copied to clipboard');
                    });
                });
            }

            // Show toast notification
            function showToast(message) {
                toast.textContent = message;
                toast.classList.add('show');
                setTimeout(() => {
                    toast.classList.remove('show');
                }, 3000);
            }

            // Hide loading overlay when page loads
            window.addEventListener('load', function() {
                loadingOverlay.style.display = 'none';
            });
        });

        // Colorize output for errors, warnings, and success messages
        function colorizeOutput() {
            const outputEl = document.getElementById('output');
            if (outputEl) {
                let text = outputEl.innerHTML;
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bError\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\berror\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bfailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWarning\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                outputEl.innerHTML = text;
            }
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
</head>
<body>
<div class="container">
    <div class="breadcrumb">
        <a href="/">🏠 Home</a> 
        <span>→</span> 
        <span>✏️ Modify .FF File</span>
    </div>

    <h1>SmartFile Converter - Modify .FF File</h1>
    
    <form method="post" id="modifyForm">
        <div class="form-group">
            <label for="new_name">📁 File name (without .ff):</label>
            <input type="text" id="new_name" name="new_name" value="{{ new_name }}" 
                   placeholder="Enter your file name...">
        </div>
        
        <div class="form-group">
            <label for="filetype">📂 File Type:</label>
            <select id="filetype" name="filetype" required>
                <option value="">-- Select File Type --</option>
                <option value="F" {% if filetype == 'F' %}selected{% endif %}>F - Fixed Block (FB)</option>
                <option value="V" {% if filetype == 'V' %}selected{% endif %}>V - Variable Block (VB)</option>
            </select>
            <div class="help-text">Select F for FB file type or V for VB file type</div>
        </div>

        <div class="form-group">
            <label for="condition_type">🔧 Condition Test Type:</label>
            <select id="condition_type" name="condition_type" required>
                <option value="">-- Select Condition Type --</option>
                <option value="S" {% if condition_type == 'S' %}selected{% endif %}>S - Single Condition</option>
                <option value="M" {% if condition_type == 'M' %}selected{% endif %}>M - Multiple Conditions</option>
            </select>
            <div class="help-text">Select S for single condition test or M for multiple condition tests</div>
        </div>

        <div class="button-group">
            <a href="/" class="btn btn-secondary">← Back to Main Menu</a>
            <button type="submit" class="btn btn-primary">✏️ Execute Modification</button>
        </div>
    </form>

    {% if output %}
    <div class="output-section">
        <div class="output-header">
            <label for="output">📤 Command Output:</label>
            <div class="output-controls">
                <button type="button" id="clearOutput" class="btn-mini">Clear</button>
                <button type="button" id="copyOutput" class="btn-mini">Copy</button>
                <button type="button" onclick="scrollToTop()" class="btn-mini">⬆️ Top</button>
                <button type="button" onclick="scrollToBottom()" class="btn-mini">⬇️ Bottom</button>
                <button type="button" onclick="resetOutputSize()" class="btn-mini">📐 Reset Size</button>
            </div>
        </div>
        <div class="output-box">
            <div class="output-content" id="output">{{ output }}</div>
            <div class="resize-handle" title="Drag to resize"></div>
        </div>
        <div style="text-align: center; margin-top: 10px; color: var(--text-secondary); font-size: 0.85rem;">
            💡 <strong>Tip:</strong> Drag the bottom-right corner to resize • Use scroll bars for navigation • Long lines will scroll horizontally
        </div>
    </div>
    {% endif %}
    
    <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid var(--border); color: var(--text-secondary); font-size: 0.9rem;">
        <p style="margin: 5px 0;">SmartFile Converter</p>
        <p style="margin: 5px 0;">Powered by Astadia TEAM</p>
    </div>
</div>

<div id="loadingOverlay" class="loading-overlay" style="display: none;">
    <div class="loading-spinner"></div>
    <p style="color: white; margin-top: 20px; font-size: 1.2rem; font-weight: 600;">Modifying file... Please wait</p>
</div>

<div id="toast" class="toast"></div>
</body>
</html>
'''

RENAME_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Rename .FF File - Configuration</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: rgba(37, 99, 235, 0.2);
            --shadow: rgba(0, 0, 0, 0.3);
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 800px;
            margin: 0 auto;
            background: var(--bg-card);
            padding: 40px;
            border-radius: 20px;
            box-shadow: 0 20px 60px var(--shadow);
        }

        h1 {
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            margin-bottom: 30px;
            text-align: center;
        }

        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
            padding: 15px 20px;
            background: var(--bg-secondary);
            border-radius: 10px;
            font-size: 0.9rem;
        }

        .breadcrumb a {
            color: var(--accent);
            text-decoration: none;
            transition: color 0.3s;
        }

        .breadcrumb a:hover {
            color: var(--secondary-color);
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-weight: 500;
        }

        input[type="text"] {
            width: 100%;
            padding: 12px 15px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 10px;
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }

        .help-text {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 5px;
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }

        .btn {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .btn-primary {
            background: var(--primary-gradient);
            color: white;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 2px solid var(--border);
        }

        .btn-secondary:hover {
            border-color: var(--primary-color);
            transform: translateY(-2px);
        }

        .output-section {
            margin-top: 30px;
        }

        .output-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 10px;
        }

        .output-controls {
            display: flex;
            gap: 10px;
        }

        .btn-mini {
            padding: 5px 15px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 5px;
            color: var(--text-primary);
            cursor: pointer;
            font-size: 0.85rem;
            transition: all 0.3s;
        }

        .btn-mini:hover {
            background: var(--primary-color);
            border-color: var(--primary-color);
        }

        textarea {
            width: 100%;
            min-height: 300px;
            padding: 15px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            resize: vertical;
            outline: none;
            overflow: auto;
            white-space: pre;
            word-wrap: normal;
        }

        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.95);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }

        .loading-spinner {
            width: 50px;
            height: 50px;
            border: 5px solid var(--border);
            border-top-color: var(--accent);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            background: var(--bg-card);
            color: var(--text-primary);
            padding: 15px 25px;
            border-radius: 10px;
            border-left: 4px solid var(--primary-color);
            box-shadow: 0 10px 25px var(--shadow);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1001;
        }

        .toast.show {
            transform: translateX(0);
        }
    </style>
    <script>
        function showLoading() {
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay) {
                loadingOverlay.style.display = 'flex';
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('renameForm');
            const loadingOverlay = document.getElementById('loadingOverlay');
            const clearBtn = document.getElementById('clearOutput');
            const copyBtn = document.getElementById('copyOutput');
            const output = document.getElementById('output');
            const toast = document.getElementById('toast');

            // Show toast notification
            function showToast(message) {
                if (toast) {
                    toast.textContent = message;
                    toast.classList.add('show');
                    setTimeout(() => {
                        toast.classList.remove('show');
                    }, 3000);
                }
            }

            // Show loading on form submit
            if (form && loadingOverlay) {
                form.addEventListener('submit', function() {
                    loadingOverlay.style.display = 'flex';
                });
            }

            // Add click handlers to submit buttons
            const submitButtons = form ? form.querySelectorAll('button[type="submit"]') : [];
            submitButtons.forEach(function(button) {
                button.addEventListener('click', function() {
                    if (loadingOverlay) {
                        loadingOverlay.style.display = 'flex';
                    }
                });
            });

            // Clear output
            if (clearBtn && output) {
                clearBtn.addEventListener('click', function() {
                    output.value = '';
                    showToast('Output cleared');
                });
            }

            // Copy output
            if (copyBtn && output) {
                copyBtn.addEventListener('click', function() {
                    output.select();
                    navigator.clipboard.writeText(output.value).then(function() {
                        showToast('Output copied to clipboard');
                    }).catch(function() {
                        // Fallback for older browsers
                        document.execCommand('copy');
                        showToast('Output copied to clipboard');
                    });
                });
            }

            // Hide loading overlay when page loads
            window.addEventListener('load', function() {
                loadingOverlay.style.display = 'none';
            });
        });

        // Colorize output for errors, warnings, and success messages
        function colorizeOutput() {
            const outputEl = document.getElementById('output');
            if (outputEl) {
                let text = outputEl.innerHTML || outputEl.textContent;
                const isTextarea = outputEl.tagName === 'TEXTAREA';
                if (isTextarea) return; // Can't colorize textarea
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bError\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\berror\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bfailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWarning\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                outputEl.innerHTML = text;
            }
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
</head>
<body>
<div class="container">
    <div class="breadcrumb">
        <a href="/">🏠 Home</a>
        <span>→</span>
        <span>🏷️ Rename .FF File</span>
    </div>

    <h1>SmartFile Converter - Rename .FF File</h1>
    
    <form method="post" id="renameForm" onsubmit="showLoading()">
        <div class="form-group">
            <label for="old_filename">📂 Current file name (without .ff):</label>
            <input type="text" id="old_filename" name="old_filename" value="{{ old_filename }}" required 
                   placeholder="e.g., oldfile">
            <div class="help-text">Enter the current name of the file you want to rename</div>
        </div>
        
        <div class="form-group">
            <label for="new_name">📁 New file name (without .ff):</label>
            <input type="text" id="new_name" name="new_name" value="{{ new_name }}" required 
                   placeholder="e.g., newfile">
            <div class="help-text">Enter the new name for the file</div>
        </div>

        <div class="button-group">
            <a href="/" class="btn btn-secondary">← Back to Main Menu</a>
            <button type="submit" class="btn btn-primary">🏷️ Rename File</button>
        </div>
    </form>

    {% if output %}
    <div class="output-section">
        <div class="output-header">
            <label for="output">📤 Output:</label>
            <div class="output-controls">
                <button type="button" id="clearOutput" class="btn-mini">Clear</button>
                <button type="button" id="copyOutput" class="btn-mini">Copy</button>
            </div>
        </div>
        <textarea readonly id="output">{{ output }}</textarea>
    </div>
    {% endif %}
    
    <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid var(--border); color: var(--text-secondary); font-size: 0.9rem;">
        <p style="margin: 5px 0;">SmartFile Converter</p>
        <p style="margin: 5px 0;">Powered by Astadia TEAM</p>
    </div>
</div>

<div id="loadingOverlay" class="loading-overlay" style="display: none;">
    <div class="loading-spinner"></div>
    <p style="color: white; margin-top: 20px; font-size: 1.2rem; font-weight: 600;">Renaming file... Please wait</p>
</div>

<div id="toast" class="toast"></div>
</body>
</html>
'''

ROY_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Roy's EBCDIC Tool - Configuration</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: rgba(37, 99, 235, 0.2);
            --shadow: rgba(0, 0, 0, 0.3);
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }

        .container {
            max-width: 1000px;
            margin: 20px auto;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 20px 40px var(--shadow);
            padding: 40px;
            position: relative;
            overflow: hidden;
        }

        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--primary-gradient);
        }

        h1 {
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
        }

        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 30px;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }

        .breadcrumb a {
            color: var(--accent);
            text-decoration: none;
            transition: color 0.2s;
        }

        .breadcrumb a:hover {
            color: var(--secondary-color);
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .help-text {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 5px;
            font-style: italic;
        }

        input[type="text"], input[type="number"], select {
            width: 100%;
            padding: 15px 20px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s ease;
            outline: none;
        }

        input[type="text"]:focus, input[type="number"]:focus, select:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            transform: translateY(-2px);
        }

        select {
            cursor: pointer;
            appearance: none;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%23b8c5d1' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
            background-repeat: no-repeat;
            background-position: right 15px center;
            padding-right: 40px;
        }

        .checkbox-group {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-top: 10px;
        }

        input[type="checkbox"] {
            width: 20px;
            height: 20px;
            cursor: pointer;
            accent-color: var(--accent);
        }

        .checkbox-group label {
            margin: 0;
            text-transform: none;
            letter-spacing: normal;
            font-weight: 500;
            cursor: pointer;
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }

        .btn {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .btn-primary {
            background: var(--primary-gradient);
            color: white;
        }

        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 2px solid var(--border);
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .output-section {
            margin-top: 40px;
        }

        .output-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .output-controls {
            display: flex;
            gap: 10px;
        }

        .btn-mini {
            padding: 8px 16px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-secondary);
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-mini:hover {
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }

        textarea#output {
            width: 100%;
            height: 450px;
            padding: 20px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            resize: vertical;
            outline: none;
            overflow: auto;
            white-space: pre;
            word-wrap: normal;
        }

        textarea#output:focus {
            border-color: var(--primary-color);
        }

        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(5px);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }

        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 4px solid rgba(37, 99, 235, 0.2);
            border-top: 4px solid #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .toast {
            position: fixed;
            bottom: 30px;
            right: 30px;
            background: var(--bg-card);
            color: var(--text-primary);
            padding: 15px 25px;
            border-radius: 10px;
            border-left: 4px solid var(--primary-color);
            box-shadow: 0 10px 25px var(--shadow);
            transform: translateX(400px);
            transition: transform 0.3s ease;
            z-index: 1001;
        }

        .toast.show {
            transform: translateX(0);
        }

        .grid-2col {
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
        }

        @media (max-width: 768px) {
            .grid-2col {
                grid-template-columns: 1fr;
            }
        }
    </style>
    <script>
        function showLoading() {
            const loadingOverlay = document.getElementById('loadingOverlay');
            if (loadingOverlay) {
                loadingOverlay.style.display = 'flex';
            }
        }

        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('royForm');
            const loadingOverlay = document.getElementById('loadingOverlay');
            const clearBtn = document.getElementById('clearOutput');
            const copyBtn = document.getElementById('copyOutput');
            const output = document.getElementById('output');
            const toast = document.getElementById('toast');

            // Show loading on form submit
            if (form && loadingOverlay) {
                form.addEventListener('submit', function() {
                    loadingOverlay.style.display = 'flex';
                });
            }

            // Add click handlers to submit buttons
            const submitButtons = form ? form.querySelectorAll('button[type="submit"]') : [];
            submitButtons.forEach(function(button) {
                button.addEventListener('click', function() {
                    if (loadingOverlay) {
                        loadingOverlay.style.display = 'flex';
                    }
                });
            });

            // Clear output
            if (clearBtn && output) {
                clearBtn.addEventListener('click', function() {
                    output.value = '';
                    showToast('Output cleared');
                });
            }

            // Copy output
            if (copyBtn && output) {
                copyBtn.addEventListener('click', function() {
                    output.select();
                    navigator.clipboard.writeText(output.value).then(function() {
                        showToast('Output copied to clipboard');
                    }).catch(function() {
                        // Fallback for older browsers
                        document.execCommand('copy');
                        showToast('Output copied to clipboard');
                    });
                });
            }

            // Show toast notification
            function showToast(message) {
                toast.textContent = message;
                toast.classList.add('show');
                setTimeout(() => {
                    toast.classList.remove('show');
                }, 3000);
            }

            // Hide loading overlay when page loads
            window.addEventListener('load', function() {
                loadingOverlay.style.display = 'none';
            });
        });
    </script>
</head>
<body>
<div class="container">
    <div class="breadcrumb">
        <a href="/">🏠 Home</a> 
        <span>→</span> 
        <span>🔧 Roy's EBCDIC Tool</span>
    </div>

    <h1>SmartFile Converter - Roy's EBCDIC Tool</h1>
    
    <form method="post" id="royForm" onsubmit="showLoading()">
        <div class="form-group">
            <label for="filename">📁 File name (without .txt extension):</label>
            <input type="text" id="filename" name="filename" value="{{ filename }}" required 
                   placeholder="Enter your file name...">
            <div class="help-text">The tool will look for this file in the INPUT_PATH directory</div>
        </div>
        
        <div class="grid-2col">
            <div class="form-group">
                <label for="rec_fm">📂 Record Format:</label>
                <select id="rec_fm" name="rec_fm" required>
                    <option value="">-- Select Record Format --</option>
                    <option value="F" {% if rec_fm == 'F' %}selected{% endif %}>F - Fixed Length</option>
                    <option value="V" {% if rec_fm == 'V' %}selected{% endif %}>V - Variable Length</option>
                </select>
                <div class="help-text">F for fixed-length or V for variable-length records</div>
            </div>

            <div class="form-group">
                <label for="rec_len">📏 Record Length:</label>
                <input type="number" id="rec_len" name="rec_len" value="{{ rec_len }}" required 
                       placeholder="e.g., 80" min="1">
                <div class="help-text">Enter the record length in bytes (e.g., 80)</div>
            </div>
        </div>

        <div class="grid-2col">
            <div class="form-group">
                <label for="key_beg">🔑 Key Starting Position:</label>
                <input type="number" id="key_beg" name="key_beg" value="{{ key_beg }}" required 
                       placeholder="e.g., 1" min="1">
                <div class="help-text">Starting position of the key in the record (1-based)</div>
            </div>

            <div class="form-group">
                <label for="key_pic">📋 Key PIC Clause:</label>
                <input type="text" id="key_pic" name="key_pic" value="{{ key_pic }}" required 
                       placeholder="e.g., X(3) or S9(5) COMP">
                <div class="help-text">COBOL PIC clause for the key (e.g., X(3) or S9(5) COMP)</div>
            </div>
        </div>

        <div class="form-group">
            <div class="checkbox-group">
                <input type="checkbox" id="rdw_flag" name="rdw_flag" value="1" {% if rdw_flag %}checked{% endif %}>
                <label for="rdw_flag">Include RDW (Record Descriptor Word) in output</label>
            </div>
            <div class="help-text">Check this if you want to include the RDW in the hex file output</div>
        </div>

        <div class="button-group">
            <a href="/" class="btn btn-secondary">← Back to Main Menu</a>
            <button type="submit" class="btn btn-primary">🔧 Execute Roy's Tool</button>
        </div>
    </form>

    {% if output %}
    <div class="output-section">
        <div class="output-header">
            <label for="output">📤 Command Output:</label>
            <div class="output-controls">
                <button type="button" id="clearOutput" class="btn-mini">Clear</button>
                <button type="button" id="copyOutput" class="btn-mini">Copy</button>
            </div>
        </div>
        <div class="output-container">
            <textarea readonly id="output">{{ output }}</textarea>
        </div>
    </div>
    {% endif %}
    
    <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid var(--border); color: var(--text-secondary); font-size: 0.9rem;">
        <p style="margin: 5px 0;">SmartFile Converter</p>
        <p style="margin: 5px 0;">Powered by Astadia TEAM</p>
    </div>
</div>

<div id="loadingOverlay" class="loading-overlay" style="display: none;">
    <div class="loading-spinner"></div>
    <p style="color: white; margin-top: 20px; font-size: 1.2rem; font-weight: 600;">Running Roy's Tool... Please wait</p>
</div>

<div id="toast" class="toast"></div>
</body>
</html>
'''

EXPFD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create EXPFD - SmartFile Converter</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: rgba(37, 99, 235, 0.2);
            --shadow: rgba(0, 0, 0, 0.3);
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }
        .container {
            max-width: 1000px;
            margin: 20px auto;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 20px 40px var(--shadow);
            padding: 40px;
            position: relative;
        }
        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--primary-gradient);
        }
        h1 {
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
        }
        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 30px;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }
        .breadcrumb a {
            color: var(--accent-color);
            text-decoration: none;
            transition: color 0.2s;
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }
        .help-text {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 5px;
            font-style: italic;
        }
        input[type="text"], textarea {
            width: 100%;
            padding: 15px 20px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s ease;
            outline: none;
        }
        input[type="text"]:focus, textarea:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }
        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }
        .btn {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        .btn-primary {
            background: var(--primary-gradient);
            color: white;
        }
        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 2px solid var(--border);
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }
        .output-section {
            margin-top: 40px;
        }
        .output-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .output-box {
            padding: 0;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            min-height: 450px;
            resize: both;
            overflow: auto;
            position: relative;
        }
        .output-content {
            padding: 20px;
            white-space: pre;
            font-family: 'JetBrains Mono', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            color: var(--text-primary);
        }
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(5px);
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 4px solid rgba(37, 99, 235, 0.2);
            border-top: 4px solid #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    <script>
        function showLoading() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }
    </script>
</head>
<body>
<div class="container">
    <div class="breadcrumb">
        <a href="/">🏠 Home</a>
        <span>→</span>
        <span>📝 Create EXPFD</span>
    </div>
    <h1>SmartFile Converter - Create EXPFD</h1>
    <form method="post" onsubmit="showLoading()">
        <div class="form-group">
            <label for="copybook_names">📂 Copybook Names (comma-separated):</label>
            <textarea id="copybook_names" name="copybook_names" rows="3" required 
                   placeholder="e.g., copybook1.cpy, copybook2.cpy, copybook3.cpy">{{ copybook_names }}</textarea>
            <div class="help-text">Enter copybook file names separated by commas</div>
        </div>
        <div class="button-group">
            <a href="/" class="btn btn-secondary">← Back to Main Menu</a>
            <button type="submit" class="btn btn-primary">📝 Create EXPFD Files</button>
        </div>
    </form>
    {% if output %}
    <div class="output-section">
        <div class="output-header">
            <label>📤 Output:</label>
        </div>
        <div class="output-box">
            <div class="output-content">{{ output }}</div>
        </div>
    </div>
    {% endif %}
</div>
<div id="loadingOverlay" class="loading-overlay">
    <div class="loading-spinner"></div>
    <p style="color: white; margin-top: 20px; font-size: 1.2rem; font-weight: 600;">Creating EXPFD... Please wait</p>
</div>
</body>
</html>
'''

DATATURN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Run DataTurn - SmartFile Converter</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: rgba(37, 99, 235, 0.2);
            --shadow: rgba(0, 0, 0, 0.3);
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }
        .container {
            max-width: 1000px;
            margin: 20px auto;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 20px 40px var(--shadow);
            padding: 40px;
            position: relative;
        }
        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--primary-gradient);
        }
        h1 {
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
        }
        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 30px;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }
        .breadcrumb a {
            color: var(--accent-color);
            text-decoration: none;
            transition: color 0.2s;
        }
        .form-group {
            margin-bottom: 25px;
        }
        label {
            display: block;
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 8px;
        }
        .help-text {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 5px;
            font-style: italic;
        }
        input[type="text"] {
            width: 100%;
            padding: 15px 20px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s ease;
            outline: none;
        }
        input[type="text"]:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
        }
        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }
        .btn {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }
        .btn-primary {
            background: var(--primary-gradient);
            color: white;
        }
        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 2px solid var(--border);
        }
        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }
        .output-section {
            margin-top: 40px;
        }
        .output-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }
        .output-box {
            padding: 0;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            min-height: 450px;
            resize: both;
            overflow: auto;
            position: relative;
        }
        .output-content {
            padding: 20px;
            white-space: pre;
            font-family: 'JetBrains Mono', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            color: var(--text-primary);
        }
        .loading-overlay {
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.95);
            backdrop-filter: blur(5px);
            display: none;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            z-index: 9999;
        }
        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 4px solid rgba(37, 99, 235, 0.2);
            border-top: 4px solid #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
    <script>
        function showLoading() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }
    </script>
</head>
<body>
<div class="container">
    <div class="breadcrumb">
        <a href="/">🏠 Home</a>
        <span>→</span>
        <span>🔄 Run DataTurn</span>
    </div>
    <h1>SmartFile Converter - Run DataTurn</h1>
    <form method="post" onsubmit="showLoading()">
        <div class="form-group">
            <label for="expfd_name">📁 EXPFD File Name:</label>
            <input type="text" id="expfd_name" name="expfd_name" value="{{ expfd_name }}" required 
                   placeholder="Enter EXPFD name without extension">
            <div class="help-text">Enter the EXPFD file name without the .expfd extension</div>
        </div>
        <div class="button-group">
            <a href="/" class="btn btn-secondary">← Back to Main Menu</a>
            <button type="submit" class="btn btn-primary">🔄 Run DataTurn</button>
        </div>
    </form>
    {% if output %}
    <div class="output-section">
        <div class="output-header">
            <label>📤 Output:</label>
        </div>
        <div class="output-box">
            <div class="output-content">{{ output }}</div>
        </div>
    </div>
    {% endif %}
</div>
<div id="loadingOverlay" class="loading-overlay">
    <div class="loading-spinner"></div>
    <p style="color: white; margin-top: 20px; font-size: 1.2rem; font-weight: 600;">Running DataTurn... Please wait</p>
</div>
</body>
</html>
'''

UPDATE_PATHS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Update Application Paths</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: rgba(37, 99, 235, 0.2);
            --shadow: rgba(0, 0, 0, 0.3);
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            color: var(--text-primary);
            line-height: 1.6;
        }

        .container {
            max-width: 1000px;
            margin: 20px auto;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 20px 40px var(--shadow);
            padding: 40px;
            position: relative;
            overflow: hidden;
        }

        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--primary-gradient);
        }

        h1 {
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
        }

        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 30px;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }

        .breadcrumb a {
            color: var(--accent);
            text-decoration: none;
            transition: color 0.2s;
        }

        .breadcrumb a:hover {
            color: var(--secondary-color);
        }

        .info-box {
            background: var(--bg-secondary);
            border-left: 4px solid var(--primary-color);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }

        .info-box h3 {
            color: var(--accent);
            margin-bottom: 10px;
        }

        .info-box p {
            color: var(--text-secondary);
            margin-bottom: 10px;
        }

        .current-app {
            display: inline-block;
            background: var(--primary-gradient);
            color: white;
            padding: 5px 15px;
            border-radius: 6px;
            font-weight: 600;
            margin-top: 10px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            font-size: 0.95rem;
            font-weight: 600;
            color: var(--text-secondary);
            margin-bottom: 8px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .help-text {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 5px;
            font-style: italic;
        }

        input[type="text"] {
            width: 100%;
            padding: 15px 20px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-size: 1rem;
            transition: all 0.3s ease;
            outline: none;
        }

        input[type="text"]:focus {
            border-color: var(--primary-color);
            box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.1);
            transform: translateY(-2px);
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }

        .btn {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-block;
            text-align: center;
        }

        .btn-primary {
            background: var(--primary-gradient);
            color: white;
        }

        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 2px solid var(--border);
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .output-section {
            margin-top: 40px;
        }

        .output-header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 15px;
        }

        .output-controls {
            display: flex;
            gap: 10px;
        }

        .btn-mini {
            padding: 8px 16px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-secondary);
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }

        .btn-mini:hover {
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }

        textarea#output {
            width: 100%;
            height: 350px;
            padding: 20px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            resize: vertical;
            outline: none;
            overflow: auto;
            white-space: pre;
            word-wrap: normal;
        }

        .success-message {
            background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
            color: #0f0f23;
            padding: 15px 20px;
            border-radius: 10px;
            margin-bottom: 20px;
            font-weight: 600;
        }
    </style>
    <script>
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('pathForm');
            const clearBtn = document.getElementById('clearOutput');
            const copyBtn = document.getElementById('copyOutput');
            const output = document.getElementById('output');

            // Clear output
            if (clearBtn && output) {
                clearBtn.addEventListener('click', function() {
                    output.value = '';
                    alert('Output cleared!');
                });
            }

            // Copy output
            if (copyBtn && output) {
                copyBtn.addEventListener('click', function() {
                    output.select();
                    navigator.clipboard.writeText(output.value).then(function() {
                        alert('Output copied to clipboard!');
                    }).catch(function() {
                        // Fallback for older browsers
                        document.execCommand('copy');
                        alert('Output copied to clipboard!');
                    });
                });
            }
        });
    </script>
</head>
<body>
<div class="container">
    <div class="breadcrumb">
        <a href="/">🏠 Home</a> 
        <span>→</span> 
        <span>⚙️ Update Paths</span>
    </div>

    <h1>SmartFile Converter - Update Paths</h1>
    
    <div class="info-box">
        <h3>ℹ️ What does this do?</h3>
        <p>This tool updates the application name in all paths in path.txt. For example, changing from "occ" to "newapp" will update all paths like C:/File_conversion/occ/ to C:/File_conversion/newapp/</p>
        <p>Current application name: <span class="current-app">{{ current_app }}</span></p>
    </div>
    
    <form method="post" id="pathForm">
        <div class="form-group">
            <label for="app_name">🔤 New Application Name:</label>
            <input type="text" id="app_name" name="app_name" value="{{ app_name }}" required 
                   placeholder="Enter new application name (e.g., myapp, project123)...">
            <div class="help-text">All instances of "occ" in paths will be replaced with this name</div>
        </div>

        <div class="form-group">
            <label for="dataturn_exe">DATATURN EXECUTABLE PATH:</label>
            <input type="text" id="dataturn_exe" name="dataturn_exe" value="{{ dataturn_exe }}" 
                   placeholder="C:/Program Files/Anubex/DataTurn/bin/dataturn.exe">
            <div class="help-text">Full path to dataturn.exe</div>
        </div>

        <div class="form-group">
            <label for="dataturn_config">CONFIGURATION FILE:</label>
            <input type="text" id="dataturn_config" name="dataturn_config" value="{{ dataturn_config }}" 
                   placeholder="rushabh.configuration">
            <div class="help-text">DataTurn configuration file name (Repository, EXPFD path, and output directory use paths from path.txt)</div>
        </div>

        <div class="button-group">
            <a href="/" class="btn btn-secondary">← Back to Main Menu</a>
            <button type="submit" class="btn btn-primary">⚙️ Update All Paths</button>
        </div>
    </form>

    {% if output %}
    <div class="output-section">
        {% if success %}
        <div class="success-message">
            ✅ Paths updated successfully! The application will use the new paths immediately.
        </div>
        {% endif %}
        
        <div class="output-header">
            <label for="output">📤 Updated path.txt content:</label>
            <div class="output-controls">
                <button type="button" id="clearOutput" class="btn-mini">Clear</button>
                <button type="button" id="copyOutput" class="btn-mini">Copy</button>
            </div>
        </div>
        <div class="output-container">
            <textarea readonly id="output">{{ output }}</textarea>
        </div>
    </div>
    {% endif %}
    
    <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid var(--border); color: var(--text-secondary); font-size: 0.9rem;">
        <p style="margin: 5px 0;">SmartFile Converter</p>
        <p style="margin: 5px 0;">Powered by Astadia TEAM</p>
    </div>
</div>
</body>
</html>
'''

# Log Viewer Template
LOG_VIEWER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log Viewer - SmartFile Converter</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: rgba(37, 99, 235, 0.2);
            --shadow: rgba(0, 0, 0, 0.3);
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: var(--bg-card);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px var(--shadow);
            border: 1px solid var(--border);
        }

        h1 {
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            margin-bottom: 20px;
            text-align: center;
        }

        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }

        .breadcrumb a {
            color: var(--accent-color);
            text-decoration: none;
            transition: color 0.3s;
        }

        .breadcrumb a:hover {
            color: var(--secondary-color);
        }

        .log-info {
            background: var(--bg-secondary);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid var(--accent-color);
        }

        .log-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }

        .btn-mini {
            padding: 8px 16px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-secondary);
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
        }

        .btn-mini:hover {
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }

        .log-container {
            height: 600px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            overflow-y: auto;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 0.85rem;
            line-height: 1.4;
            white-space: pre-wrap;
        }

        .log-container::-webkit-scrollbar {
            width: 8px;
        }

        .log-container::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }

        .log-container::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 4px;
        }

        .log-container::-webkit-scrollbar-thumb:hover {
            background: var(--accent-color);
        }

        .back-btn {
            display: inline-block;
            background: var(--primary-gradient);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            margin-bottom: 20px;
            transition: all 0.3s;
        }

        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4);
        }

        .auto-scroll {
            text-align: center;
            margin-top: 15px;
        }

        .auto-scroll input[type="checkbox"] {
            margin-right: 8px;
        }
    </style>
    <script>
        function refreshPage() {
            location.reload();
        }

        function clearLogs() {
            if (confirm('Are you sure you want to clear the log display? This will not delete the actual log file.')) {
                document.getElementById('logContent').textContent = 'Logs cleared from display...';
            }
        }

        function copyLogs() {
            const logContent = document.getElementById('logContent').textContent;
            navigator.clipboard.writeText(logContent).then(function() {
                alert('Logs copied to clipboard!');
            }).catch(function() {
                // Fallback for older browsers
                const textArea = document.createElement('textarea');
                textArea.value = logContent;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('Logs copied to clipboard!');
            });
        }

        function toggleAutoScroll() {
            const logContainer = document.getElementById('logContent');
            const autoScroll = document.getElementById('autoScroll').checked;
            
            if (autoScroll) {
                logContainer.scrollTop = logContainer.scrollHeight;
            }
        }

        // Auto refresh every 30 seconds if enabled
        let autoRefreshInterval;
        function toggleAutoRefresh() {
            const autoRefresh = document.getElementById('autoRefresh').checked;
            
            if (autoRefresh) {
                autoRefreshInterval = setInterval(refreshPage, 30000);
            } else {
                clearInterval(autoRefreshInterval);
            }
        }

        // Scroll to bottom on load
        window.onload = function() {
            const logContainer = document.getElementById('logContent');
            logContainer.scrollTop = logContainer.scrollHeight;
            colorizeLogContent();
        }

        // Colorize log content for errors, warnings, and success messages
        function colorizeLogContent() {
            const logContainer = document.getElementById('logContent');
            if (logContainer) {
                let text = logContainer.innerHTML;
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bError\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\berror\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bfailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWarning\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                logContainer.innerHTML = text;
            }
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">🏠 Home</a>
            <span>→</span>
            <span>📋 Log Viewer</span>
        </div>

        <h1>📋 Log Viewer</h1>
        
        <a href="/" class="back-btn">← Back to Main Menu</a>
        
        <div class="log-info">
            <p><strong>📁 Log File:</strong> {{ log_filepath }}</p>
            <p><strong>📅 Showing:</strong> Last 10000 entries from today's log</p>
            <p><strong>🔄 Auto-refresh:</strong> Every 30 seconds (when enabled)</p>
        </div>

        <div class="log-controls">
            <button onclick="refreshPage()" class="btn-mini">🔄 Refresh</button>
            <button onclick="clearLogs()" class="btn-mini">🗑️ Clear Display</button>
            <button onclick="copyLogs()" class="btn-mini">📋 Copy All</button>
            <label class="btn-mini" style="cursor: pointer;">
                <input type="checkbox" id="autoRefresh" onchange="toggleAutoRefresh()" style="margin-right: 5px;">
                🔄 Auto-refresh
            </label>
            <label class="btn-mini" style="cursor: pointer;">
                <input type="checkbox" id="autoScroll" onchange="toggleAutoScroll()" checked style="margin-right: 5px;">
                📜 Auto-scroll
            </label>
        </div>

        <div class="log-container" id="logContent">{{ log_content }}</div>

        <div style="text-align: center; margin-top: 20px; color: var(--text-secondary); font-size: 0.9rem;">
            <p>📝 Log entries show timestamp, level, function, and message</p>
            <p>🔍 Use browser search (Ctrl+F) to find specific entries</p>
        </div>
    </div>
</body>
</html>
'''

USER_GUIDE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Guide - SmartFile Converter</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: rgba(30, 41, 59, 0.8);
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: rgba(37, 99, 235, 0.2);
            --shadow: rgba(0, 0, 0, 0.3);
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f0f23 0%, #1a1a2e 100%);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: var(--bg-card);
            padding: 30px;
            border-radius: 20px;
            box-shadow: 0 20px 60px var(--shadow);
            border: 1px solid var(--border);
        }

        h1 {
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            margin-bottom: 20px;
            text-align: center;
        }

        .breadcrumb {
            display: flex;
            align-items: center;
            gap: 10px;
            margin-bottom: 20px;
            font-size: 0.9rem;
            color: var(--text-secondary);
        }

        .breadcrumb a {
            color: var(--accent-color);
            text-decoration: none;
            transition: color 0.3s;
        }

        .breadcrumb a:hover {
            color: var(--secondary-color);
        }

        .guide-info {
            background: var(--bg-secondary);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid var(--accent-color);
        }

        .guide-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
        }

        .btn-mini {
            padding: 8px 16px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-secondary);
            font-size: 0.85rem;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
        }

        .btn-mini:hover {
            background: var(--primary-color);
            color: white;
            border-color: var(--primary-color);
        }

        .guide-container {
            max-height: 700px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 30px;
            overflow-y: auto;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            font-size: 0.95rem;
            line-height: 1.8;
            white-space: pre-wrap;
        }

        .guide-container::-webkit-scrollbar {
            width: 8px;
        }

        .guide-container::-webkit-scrollbar-track {
            background: var(--bg-primary);
        }

        .guide-container::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 4px;
        }

        .guide-container::-webkit-scrollbar-thumb:hover {
            background: var(--accent-color);
        }

        .guide-container h1,
        .guide-container h2,
        .guide-container h3,
        .guide-container h4 {
            color: var(--accent-color);
            margin-top: 25px;
            margin-bottom: 15px;
        }

        .guide-container h1 {
            font-size: 2rem;
            border-bottom: 2px solid var(--border);
            padding-bottom: 10px;
        }

        .guide-container h2 {
            font-size: 1.6rem;
        }

        .guide-container h3 {
            font-size: 1.3rem;
        }

        .guide-container p {
            margin-bottom: 15px;
        }

        .guide-container ul,
        .guide-container ol {
            margin-left: 25px;
            margin-bottom: 15px;
        }

        .guide-container li {
            margin-bottom: 8px;
        }

        .guide-container code {
            background: var(--bg-primary);
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            color: #22c55e;
        }

        .guide-container pre {
            background: var(--bg-primary);
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            margin-bottom: 15px;
        }

        .guide-container pre code {
            background: none;
            padding: 0;
        }

        .guide-container blockquote {
            border-left: 4px solid var(--accent-color);
            padding-left: 15px;
            margin: 15px 0;
            color: var(--text-secondary);
        }

        .guide-container table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 15px;
        }

        .guide-container th,
        .guide-container td {
            border: 1px solid var(--border);
            padding: 10px;
            text-align: left;
        }

        .guide-container th {
            background: var(--bg-primary);
            color: var(--accent-color);
        }

        .back-btn {
            display: inline-block;
            background: var(--primary-gradient);
            color: white;
            padding: 12px 24px;
            border-radius: 8px;
            text-decoration: none;
            font-weight: 600;
            margin-bottom: 20px;
            transition: all 0.3s;
        }

        .back-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4);
        }
    </style>
    <script>
        function copyGuide() {
            const guideContent = document.getElementById('guideContent').textContent;
            navigator.clipboard.writeText(guideContent).then(function() {
                alert('User Guide copied to clipboard!');
            }).catch(function() {
                const textArea = document.createElement('textarea');
                textArea.value = guideContent;
                document.body.appendChild(textArea);
                textArea.select();
                document.execCommand('copy');
                document.body.removeChild(textArea);
                alert('User Guide copied to clipboard!');
            });
        }

        function scrollToTop() {
            document.getElementById('guideContent').scrollTop = 0;
        }

        function scrollToBottom() {
            const container = document.getElementById('guideContent');
            container.scrollTop = container.scrollHeight;
        }
    </script>
</head>
<body>
    <div class="container">
        <div class="breadcrumb">
            <a href="/">🏠 Home</a>
            <span>→</span>
            <span>📖 User Guide</span>
        </div>

        <h1>📖 User Guide</h1>
        
        <a href="/" class="back-btn">← Back to Main Menu</a>
        
        <div class="guide-info">
            <p><strong>📁 Document:</strong> SmartFile_Converter_USER_GUIDE.md</p>
            <p><strong>📚 Complete step-by-step guide to using SmartFile Converter</strong></p>
        </div>

        <div class="guide-controls">
            <button onclick="scrollToTop()" class="btn-mini">⬆️ Top</button>
            <button onclick="scrollToBottom()" class="btn-mini">⬇️ Bottom</button>
            <button onclick="copyGuide()" class="btn-mini">📋 Copy All</button>
        </div>

        <div class="guide-container" id="guideContent">{{ guide_content }}</div>

        <div style="text-align: center; margin-top: 20px; color: var(--text-secondary); font-size: 0.9rem;">
            <p>📖 Complete documentation for all features</p>
            <p>🔍 Use browser search (Ctrl+F) to find specific topics</p>
        </div>
    </div>
</body>
</html>
'''
 
@app.route('/', methods=['GET', 'POST'])
def index():
    output = ''
    new_name = request.form.get('new_name', '')
    records = request.form.get('records', '')
    action = request.form.get('action', '')
    
    try:
        # Use os.getcwd() to get the actual working directory
        script_dir = os.getcwd()
        config_path = os.path.join(script_dir, 'path.txt')
        
        if not os.path.exists(config_path):
            output = f'Error: path.txt not found at {config_path}\nCurrent working directory: {script_dir}'
            return render_template_string(TEMPLATE, output=output, new_name=new_name, records=records)
        
        paths = read_paths(config_path)
        
        if request.method == 'POST':
            if action == 'expfd_creation':
                # Redirect to EXPFD creation page
                return redirect(url_for('expfd_creation_page'))
            elif action == 'dataturn':
                # Redirect to DataTurn page
                return redirect(url_for('dataturn_page'))
            elif action == 'rename':
                # Redirect to rename page
                return redirect(url_for('rename_page'))
            elif action == 'modify':
                # Redirect to modify page with filename (if provided)
                if new_name:
                    return redirect(url_for('modify_page', filename=new_name))
                else:
                    return redirect(url_for('modify_page'))
            elif action == 'dowitcher' and new_name:
                output = run_dowitcher(paths, new_name)
            elif action == 'display' and new_name:
                output = run_dowitcher(paths, new_name, records=records, display=True)
            elif action == 'rexx':
                # Redirect to Roy's tool page with filename (if provided)
                if new_name:
                    return redirect(url_for('roy_page', filename=new_name))
                else:
                    return redirect(url_for('roy_page'))
            elif action == 'display_hex' and new_name:
                output = run_dowitcher(paths, new_name, records=records, display=True, hex_display=True)
            elif action == 'particular_records' and new_name:
                output = run_dowitcher(paths, new_name, records=records, particular_records=True)
            elif action == 'input_display_hex' and new_name:
                output = run_dowitcher(paths, new_name, records=records, display=True, hex_display=True, input_display=True)
            elif action == 'update_paths':
                # Redirect to update paths page
                return redirect(url_for('update_paths_page'))
    except Exception as e:
        output = f'Critical Error: {e}\n\nFull Traceback:\n{traceback.format_exc()}'
    
    return render_template_string(TEMPLATE, output=output, new_name=new_name, records=records)

@app.route('/rename', methods=['GET', 'POST'])
def rename_page():
    output = ''
    old_filename = request.form.get('old_filename', '')
    new_name = request.form.get('new_name', '')
    
    try:
        if request.method == 'POST' and old_filename and new_name:
            # Use os.getcwd() to get the actual working directory
            script_dir = os.getcwd()
            config_path = os.path.join(script_dir, 'path.txt')
            
            if not os.path.exists(config_path):
                output = f'Error: path.txt not found at {config_path}\nCurrent working directory: {script_dir}'
                return render_template_string(RENAME_TEMPLATE, output=output, old_filename=old_filename, new_name=new_name)
            
            paths = read_paths(config_path)
            
            # Add .ff extension if not already present
            old_filename_with_ext = old_filename.strip()
            if not old_filename_with_ext.lower().endswith('.ff'):
                old_filename_with_ext = old_filename_with_ext + '.ff'
            
            # Rename the file
            output = rename_file(paths.get('FORMAT_PATH', ''), old_filename_with_ext, new_name)
    except Exception as e:
        output = f'Critical Error: {e}\n\nFull Traceback:\n{traceback.format_exc()}'
    
    return render_template_string(RENAME_TEMPLATE, output=output, old_filename=old_filename, new_name=new_name)

@app.route('/modify', methods=['GET', 'POST'])
def modify_page():
    output = ''
    new_name = request.args.get('filename', '') or request.form.get('new_name', '')
    filetype = request.form.get('filetype', '')
    condition_type = request.form.get('condition_type', '')
    
    try:
        if request.method == 'POST' and new_name and filetype and condition_type:
            # Use os.getcwd() to get the actual working directory
            script_dir = os.getcwd()
            config_path = os.path.join(script_dir, 'path.txt')
            
            if not os.path.exists(config_path):
                output = f'Error: path.txt not found at {config_path}\nCurrent working directory: {script_dir}'
                return render_template_string(MODIFY_TEMPLATE, output=output, new_name=new_name, filetype=filetype, condition_type=condition_type)
            
            paths = read_paths(config_path)
            
            # Run the modify script directly (no renaming)
            output = run_file_modify(new_name, filetype, condition_type)
    except Exception as e:
        output = f'Critical Error: {e}\n\nFull Traceback:\n{traceback.format_exc()}'
    
    return render_template_string(MODIFY_TEMPLATE, output=output, new_name=new_name, filetype=filetype, condition_type=condition_type)

@app.route('/roy', methods=['GET', 'POST'])
def roy_page():
    output = ''
    # Prioritize form data over URL parameters - if user overrides filename in form, use that
    filename = request.form.get('filename', '') or request.args.get('filename', '')
    rec_fm = request.form.get('rec_fm', '')
    rec_len = request.form.get('rec_len', '')
    key_beg = request.form.get('key_beg', '')
    key_pic = request.form.get('key_pic', '')
    rdw_flag = request.form.get('rdw_flag', '')
    
    try:
        if request.method == 'POST' and filename and rec_fm and rec_len and key_beg and key_pic:
            # Run Roy's tool with the provided parameters
            output = run_rexx(filename, rec_fm, rec_len, key_beg, key_pic, rdw_flag)
    except Exception as e:
        output = f'Critical Error: {e}\n\nFull Traceback:\n{traceback.format_exc()}'
    
    return render_template_string(ROY_TEMPLATE, output=output, filename=filename, rec_fm=rec_fm, 
                                 rec_len=rec_len, key_beg=key_beg, key_pic=key_pic, rdw_flag=rdw_flag)

@app.route('/expfd_creation', methods=['GET', 'POST'])
def expfd_creation_page():
    output = ''
    copybook_names_input = request.form.get('copybook_names', '')
    
    try:
        if request.method == 'POST' and copybook_names_input:
            script_dir = os.getcwd()
            config_path = os.path.join(script_dir, 'path.txt')
            
            if os.path.exists(config_path):
                paths = read_paths(config_path)
                # Use lowercase keys as they appear in path.txt
                expfd_path = paths.get('expfd', os.path.join(script_dir, 'mc', 'expfd'))
                copybook_path = paths.get('copybook', os.path.join(script_dir, 'mc', 'copybook'))
            else:
                expfd_path = os.path.join(script_dir, 'mc', 'expfd')
                copybook_path = os.path.join(script_dir, 'mc', 'copybook')
            
            # Parse copybook names (comma-separated)
            copybook_names = [name.strip() for name in copybook_names_input.split(',') if name.strip()]
            
            output = run_expfd_creation(copybook_names, expfd_path, copybook_path)
    except Exception as e:
        output = f'Critical Error: {e}\n\nFull Traceback:\n{traceback.format_exc()}'
    
    return render_template_string(EXPFD_TEMPLATE, output=output, copybook_names=copybook_names_input)

@app.route('/dataturn', methods=['GET', 'POST'])
def dataturn_page():
    output = ''
    expfd_name = request.form.get('expfd_name', '')
    
    try:
        if request.method == 'POST' and expfd_name:
            script_dir = os.getcwd()
            config_path = os.path.join(script_dir, 'path.txt')
            
            if os.path.exists(config_path):
                config = read_paths(config_path)
            else:
                config = {}
            
            output = run_dataturn(expfd_name, config)
    except Exception as e:
        output = f'Critical Error: {e}\n\nFull Traceback:\n{traceback.format_exc()}'
    
    return render_template_string(DATATURN_TEMPLATE, output=output, expfd_name=expfd_name)

@app.route('/update_paths', methods=['GET', 'POST'])
def update_paths_page():
    """Update application name in path.txt"""
    output = ''
    success = False
    app_name = ''
    dataturn_exe = ''
    dataturn_config = ''
    current_app = 'occ'  # Default value
    
    # Read current application name and DataTurn config from path.txt
    try:
        config_file = os.path.join(os.getcwd(), 'path.txt')
        if os.path.exists(config_file):
            config = read_paths(config_file)
            # Try to find current app name from paths
            import re
            content = open(config_file, 'r').read()
            match = re.search(r'/([^/]+)/(?:input|output|FF_FILES)', content)
            if match:
                current_app = match.group(1)
            
            # Get current DataTurn settings
            dataturn_exe = config.get('DATATURN_EXE_PATH', 'C:/Program Files/Anubex/DataTurn/bin/dataturn.exe')
            dataturn_config = config.get('DATATURN_CONFIG_FILE', 'rushabh.configuration')
    except:
        pass
    
    if request.method == 'POST':
        app_name = request.form.get('app_name', '').strip()
        new_dataturn_exe = request.form.get('dataturn_exe', '').strip()
        new_dataturn_config = request.form.get('dataturn_config', '').strip()
        
        if app_name:
            try:
                # Validate application name
                if not re.match(r'^[a-zA-Z0-9_-]+$', app_name):
                    output = 'Error: Application name can only contain letters, numbers, underscores, and hyphens.'
                else:
                    # Read path.txt
                    config_file = os.path.join(os.getcwd(), 'path.txt')
                    if not os.path.exists(config_file):
                        output = f'Error: path.txt not found at {config_file}'
                    else:
                        with open(config_file, 'r') as f:
                            lines = f.readlines()
                        
                        # Replace all occurrences of current_app with app_name
                        updated_lines = []
                        changes_count = 0
                        dataturn_exe_found = False
                        dataturn_config_found = False
                        
                        for line in lines:
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                original_value = value
                                
                                # Update DataTurn exe path if provided
                                if key == 'DATATURN_EXE_PATH':
                                    dataturn_exe_found = True
                                    if new_dataturn_exe:
                                        value = new_dataturn_exe + '\n'
                                        changes_count += 1
                                
                                # Update DataTurn config file if provided
                                elif key == 'DATATURN_CONFIG_FILE':
                                    dataturn_config_found = True
                                    if new_dataturn_config:
                                        value = new_dataturn_config + '\n'
                                        changes_count += 1
                                
                                # Update application paths
                                elif current_app in value:
                                    # Replace in directory paths: /occ/
                                    value = value.replace(f'/{current_app}/', f'/{app_name}/')
                                    
                                    # Replace in filenames: occ.csv
                                    value = value.replace(f'{current_app}.', f'{app_name}.')
                                    
                                    # Replace standalone application path: /occ\n
                                    value = value.replace(f'/{current_app}\n', f'/{app_name}\n')
                                    value = value.replace(f'/{current_app}\r\n', f'/{app_name}\r\n')
                                    
                                    if value != original_value:
                                        changes_count += 1
                                
                                updated_lines.append(f'{key}={value}')
                            else:
                                updated_lines.append(line)
                        
                        # Add DataTurn settings if they don't exist and were provided
                        if new_dataturn_exe and not dataturn_exe_found:
                            updated_lines.append(f'DATATURN_EXE_PATH={new_dataturn_exe}\n')
                            changes_count += 1
                        
                        if new_dataturn_config and not dataturn_config_found:
                            updated_lines.append(f'DATATURN_CONFIG_FILE={new_dataturn_config}\n')
                            changes_count += 1
                        
                        # Write back to path.txt
                        with open(config_file, 'w') as f:
                            f.writelines(updated_lines)
                        
                        success = True
                        output = ''.join(updated_lines)
                        output = f'✅ Successfully updated {changes_count} configuration(s)\n\n' + output
                        current_app = app_name  # Update current_app display
                        if new_dataturn_exe:
                            dataturn_exe = new_dataturn_exe
                        if new_dataturn_config:
                            dataturn_config = new_dataturn_config
                        
            except Exception as e:
                output = f'Error updating paths: {e}\n\nFull Traceback:\n{traceback.format_exc()}'
        else:
            output = 'Error: Application name cannot be empty.'
    
    return render_template_string(UPDATE_PATHS_TEMPLATE, output=output, success=success, 
                                 app_name=app_name, current_app=current_app,
                                 dataturn_exe=dataturn_exe, dataturn_config=dataturn_config)

@app.route('/view_logs')
def view_logs_page():
    """Display recent log entries"""
    try:
        log_dir = os.path.join(os.getcwd(), 'logs')
        log_filename = f"SmartFile_Converter_{datetime.datetime.now().strftime('%Y%m%d')}.log"
        log_filepath = os.path.join(log_dir, log_filename)
        
        log_content = ""
        if os.path.exists(log_filepath):
            try:
                with open(log_filepath, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    # Get last 10000 lines for display
                    recent_lines = lines[-10000:] if len(lines) > 10000 else lines
                    log_content = ''.join(recent_lines)
            except Exception as e:
                log_content = f"Error reading log file: {str(e)}"
        else:
            log_content = f"Log file not found: {log_filepath}"
        
        return render_template_string(LOG_VIEWER_TEMPLATE, log_content=log_content, log_filepath=log_filepath)
    except Exception as e:
        logger.error(f"Error in view_logs_page: {str(e)}")
        return f"Error loading logs: {str(e)}"

@app.route('/user_guide')
def user_guide_page():
    """Display user guide"""
    try:
        # Use os.getcwd() to get the actual working directory
        guide_path = os.path.join(os.getcwd(), 'SmartFile_Converter_USER_GUIDE.md')
        
        guide_content = ""
        if os.path.exists(guide_path):
            try:
                with open(guide_path, 'r', encoding='utf-8') as f:
                    guide_content = f.read()
            except Exception as e:
                guide_content = f"Error reading user guide: {str(e)}"
        else:
            guide_content = "User guide file not found. Please ensure 'SmartFile_Converter_USER_GUIDE.md' exists in the application directory."
        
        return render_template_string(USER_GUIDE_TEMPLATE, guide_content=guide_content)
    except Exception as e:
        logger.error(f"Error in user_guide_page: {str(e)}")
        return f"Error loading user guide: {str(e)}"
 
if __name__ == '__main__':
    import sys
    
    # Only ask for port on first run (not on Flask reloader restart)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        # Ask user for port number
        print("\n" + "="*60)
        print("  FILE CONVERSION TOOL - Server Configuration")
        print("="*60)
        
        default_port = 5000
        port_input = input(f"\nEnter port number to run the server (default: {default_port}): ").strip()
        
        # Validate and use the port
        if port_input:
            try:
                port = int(port_input)
                if port < 1 or port > 65535:
                    print(f"⚠️  Invalid port number. Using default port {default_port}")
                    port = default_port
                else:
                    print(f"✅ Server will start on port {port}")
            except ValueError:
                print(f"⚠️  Invalid input. Using default port {default_port}")
                port = default_port
        else:
            port = default_port
            print(f"✅ Using default port {port}")
        
        # Store port in environment variable for reloader
        os.environ['FLASK_PORT'] = str(port)
        
        print("\n" + "="*60)
        print(f"  Starting Flask server at http://127.0.0.1:{port}")
        print("  Press CTRL+C to stop the server")
        print("="*60 + "\n")
        
        # Log server startup
        logger.info(f"Starting Flask server on port {port}")
        
    else:
        # Reloader process - get port from environment
        port = int(os.environ.get('FLASK_PORT', 5000))
    
    app.run(debug=True, port=port)