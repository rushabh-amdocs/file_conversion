
import os
import re
import shutil
import subprocess
import traceback
import time
import logging
import datetime
from flask import Flask, render_template_string, request, redirect, url_for

# Configure logging
def setup_logging():
    """Setup logging configuration with timestamps"""
    # Try to read LOG_PATH from path.txt first
    log_dir = None
    path_file = os.path.join(os.getcwd(), 'path.txt')
    if os.path.exists(path_file):
        try:
            with open(path_file, 'r') as f:
                for line in f:
                    if line.strip().startswith('LOG_PATH='):
                        log_dir = line.split('=', 1)[1].strip().replace('\r', '')
                        break
        except Exception as e:
            print(f"Warning: Could not read LOG_PATH from path.txt: {e}")
    
    # Fallback to logs folder in current directory if LOG_PATH not found
    if not log_dir:
        log_dir = os.path.join(os.getcwd(), 'logs')
    
    # Create logs directory if it doesn't exist
    try:
        os.makedirs(log_dir, exist_ok=True)
    except Exception as e:
        print(f"Warning: Could not create logs directory: {e}")
        # Fallback to current directory if logs directory cannot be created
        log_dir = os.getcwd()
    
    # Create log file with current date
    log_filename = f"workflows_{datetime.datetime.now().strftime('%Y%m%d')}.log"
    log_filepath = os.path.join(log_dir, log_filename)
    
    # Create a custom logger for our application only
    logger = logging.getLogger('workflows')
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        logger.removeHandler(handler)
    
    # Create file handler with custom format
    try:
        file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
        file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
        file_handler.setFormatter(file_formatter)
        
        # Add only file handler (no console output to avoid cluttering)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Warning: Could not create log file handler: {e}")
        # Create a console handler as fallback
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'))
        logger.addHandler(console_handler)
    
    # Disable Flask's werkzeug logger from writing to our log
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
    
    return logger

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
    """Read paths from path.txt file"""
    paths = {}
    with open(config_file, 'r') as f:
        for line in f:
            if '=' in line:
                var, val = line.strip().split('=', 1)
                paths[var.strip()] = val.strip().replace('\r', '')
    return paths

def read_scripts_config(config_file):
    """Read configuration from scripts_config.txt and merge with path.txt"""
    config = {}
    
    # First, read path.txt to get common variables
    path_file = os.path.join(os.getcwd(), 'path.txt')
    if os.path.exists(path_file):
        try:
            with open(path_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        var, val = line.split('=', 1)
                        config[var.strip()] = val.strip().replace('\r', '')
        except Exception as e:
            print(f"Error reading path.txt: {e}")
    
    # Now read scripts_config.txt and add/override with script-specific paths
    if os.path.exists(config_file):
        try:
            with open(config_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        var, val = line.split('=', 1)
                        config[var.strip()] = val.strip().replace('\r', '')
        except Exception as e:
            print(f"Error reading scripts config: {e}")
    
    return config

def run_create_folder(folder_name, base_path):
    """Create folder structure"""
    try:
        output = []
        output.append("="*60)
        output.append("CREATE FOLDER STRUCTURE OPERATION")
        output.append("="*60)
        output.append(f"Base Path: {base_path}")
        output.append(f"Folder Name: {folder_name}")
        output.append("")
        
        # Define the folder structure
        folders = [
            os.path.join(base_path, folder_name),
            os.path.join(base_path, folder_name, 'input'),
            os.path.join(base_path, folder_name, 'output'),
            os.path.join(base_path, folder_name, 'FF_FILES'),
            os.path.join(base_path, folder_name, 'FF_FILES', 'datamig'),
            os.path.join(base_path, folder_name, 'FF_FILES', 'datamig', 'file-format'),
            os.path.join(base_path, folder_name, 'datamatch'),
            os.path.join(base_path, folder_name, 'datamatch', 'source'),
            os.path.join(base_path, folder_name, 'datamatch', 'target')
        ]
        
        success_count = 0
        for folder in folders:
            try:
                if not os.path.exists(folder):
                    os.makedirs(folder)
                    output.append(f"✅ Created: {folder}")
                    success_count += 1
                else:
                    output.append(f"ℹ️  Already exists: {folder}")
            except Exception as e:
                error_msg = f"Failed to create {folder}: {str(e)}"
                output.append(f"❌ {error_msg}")
        
        output.append("")
        output.append("="*60)
        output.append(f"OPERATION COMPLETED - {success_count} folders created")
        output.append("="*60)
        
        result_output = '\n'.join(output)
        
        # Log the complete command output
        log_command_output(
            "CREATE FOLDER STRUCTURE", 
            f"Create folders for: {folder_name}", 
            result_output,
            True
        )
        
        return result_output, True
    except Exception as e:
        error_output = f"❌ Error in run_create_folder: {str(e)}\n{traceback.format_exc()}"
        log_command_output("CREATE FOLDER STRUCTURE", f"Create folders for: {folder_name}", error_output, False)
        return error_output, False

def run_folder_open(folder_name, base_path):
    """Open project folders in Windows Explorer"""
    try:
        output = []
        output.append("="*60)
        output.append("OPEN PROJECT FOLDERS OPERATION")
        output.append("="*60)
        output.append(f"Base Path: {base_path}")
        output.append(f"Folder Name: {folder_name}")
        output.append("")
        
        # Define the folders to open
        folders = [
            os.path.join(base_path, folder_name, 'input'),
            os.path.join(base_path, folder_name, 'output'),
            os.path.join(base_path, folder_name, 'FF_FILES', 'datamig', 'file-format'),
            os.path.join(base_path, folder_name, 'datamatch', 'source'),
            os.path.join(base_path, folder_name, 'datamatch', 'target')
        ]
        
        opened_count = 0
        for folder in folders:
            if os.path.exists(folder):
                try:
                    subprocess.Popen(f'explorer "{folder}"')
                    output.append(f"✅ Opened: {folder}")
                    opened_count += 1
                except Exception as e:
                    output.append(f"❌ Failed to open {folder}: {str(e)}")
            else:
                output.append(f"⚠️  Folder not found: {folder}")
        
        output.append("")
        output.append("="*60)
        output.append(f"OPERATION COMPLETED - {opened_count} folders opened")
        output.append("="*60)
        
        result_output = '\n'.join(output)
        
        # Log the complete command output
        log_command_output(
            "OPEN FOLDERS", 
            f"Open explorer windows for: {folder_name}", 
            result_output,
            True
        )
        
        return result_output, True
    except Exception as e:
        error_output = f"❌ Error in run_folder_open: {str(e)}\n{traceback.format_exc()}"
        log_command_output("OPEN FOLDERS", f"Open explorer windows for: {folder_name}", error_output, False)
        return error_output, False

def run_bulk_conversion(folder_name, base_path):
    """Run bulk conversion script"""
    try:
        output = []
        output.append("="*60)
        output.append("BULK CONVERSION OPERATION STARTED")
        output.append("="*60)
        output.append(f"Base Path: {base_path}")
        output.append(f"Application: {folder_name}")
        output.append("")
        
        # Construct paths from path.txt structure
        format_path = os.path.join(base_path, folder_name, 'FF_FILES', 'datamig', 'file-format')
        input_path = os.path.join(base_path, folder_name, 'input')
        output_path = os.path.join(base_path, folder_name, 'output')
        dowitcher_path = os.path.join(base_path, 'dowitcher.exe')
        source_dir = os.path.join(base_path, folder_name, 'datamatch', 'source')
        target_dir = os.path.join(base_path, folder_name, 'datamatch', 'target')
        
        output.append(f"Format Path: {format_path}")
        output.append(f"Input Path: {input_path}")
        output.append(f"Output Path: {output_path}")
        output.append(f"Dowitcher Path: {dowitcher_path}")
        output.append("")
        
        # Verify paths
        if not os.path.exists(format_path):
            error_output = '\n'.join(output) + f"\n❌ ERROR: Format path not found: {format_path}"
            log_command_output("BULK CONVERSION", f"Process {folder_name} files", error_output, False)
            return error_output, False
        if not os.path.exists(input_path):
            error_output = '\n'.join(output) + f"\n❌ ERROR: Input path not found: {input_path}"
            log_command_output("BULK CONVERSION", f"Process {folder_name} files", error_output, False)
            return error_output, False
        if not os.path.exists(dowitcher_path):
            error_output = '\n'.join(output) + f"\n❌ ERROR: Dowitcher executable not found: {dowitcher_path}"
            log_command_output("BULK CONVERSION", f"Process {folder_name} files", error_output, False)
            return error_output, False
        
        # Create output directory if needed
        if not os.path.exists(output_path):
            os.makedirs(output_path)
            output.append(f"✅ Created output directory: {output_path}")
        
        # Create source and target directories if needed
        if source_dir and not os.path.exists(source_dir):
            os.makedirs(source_dir)
            output.append(f"✅ Created source directory: {source_dir}")
        if target_dir and not os.path.exists(target_dir):
            os.makedirs(target_dir)
            output.append(f"✅ Created target directory: {target_dir}")
        
        # Get list of input files (.txt files)
        input_files = [f for f in os.listdir(input_path) if f.endswith('.txt')]
        
        if not input_files:
            warning_output = '\n'.join(output) + f"\n⚠️  No input files (.txt) found in: {input_path}"
            log_command_output("BULK CONVERSION", f"Process {folder_name} files", warning_output, False)
            return warning_output, False
        
        output.append(f"\n📋 Found {len(input_files)} input files")
        output.append("")
        
        success_count = 0
        error_count = 0
        skipped_count = 0
        
        for input_file_name in input_files:
            basename = input_file_name[:-4]  # Remove .txt extension
            input_file = os.path.join(input_path, input_file_name)
            output_file = os.path.join(output_path, input_file_name)
            ff_file = f"{basename}.ff"
            ff_path = os.path.join(format_path, ff_file)
            
            # Check if corresponding .ff file exists
            if not os.path.exists(ff_path):
                output.append(f"<span style='color: #ef4444; font-weight: bold;'>⚠️  SKIPPED: {basename} (format file {ff_file} not found)</span>")
                skipped_count += 1
                continue
            
            # Run dowitcher conversion
            output.append(f"🔄 Processing: {basename}")
            command_str = f"dowitcher --convert --translation-table=IBM-037:ISO-8859-1 --format={ff_path} {input_file} {output_file}"
            output.append(f"   Command: {command_str}")
            output.append("")
            
            try:
                result = subprocess.run(
                    [dowitcher_path, '--convert', '--translation-table=IBM-037:ISO-8859-1', f'--format={ff_path}', input_file, output_file],
                    capture_output=True,
                    text=True
                )
                
                # Parse dowitcher output for record counts
                records_read = None
                records_written = None
                if result.stdout:
                    output.append("📋 Dowitcher Output:")
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            output.append(f"   {line}")
                            # Parse record counts from line like: "dowitcher.exe: 1114 record(s) read, 1114 record(s) written"
                            if 'record(s) read' in line and 'record(s) written' in line:
                                try:
                                    import re
                                    match = re.search(r'(\d+)\s+record\(s\)\s+read,\s+(\d+)\s+record\(s\)\s+written', line)
                                    if match:
                                        records_read = int(match.group(1))
                                        records_written = int(match.group(2))
                                except:
                                    pass
                    output.append("")
                
                if result.returncode == 0 and os.path.exists(output_file):
                    # Check if record counts match
                    if records_read is not None and records_written is not None:
                        if records_read == records_written:
                            output.append(f"<span style='color: #22c55e; font-weight: bold;'>✅ SUCCESS: {basename} - Record count matched ({records_read} records)</span>")
                        else:
                            output.append(f"<span style='color: #f59e0b; font-weight: bold;'>⚠️  WARNING: {basename} - Record count mismatch! Read: {records_read}, Written: {records_written}</span>")
                    else:
                        output.append(f"<span style='color: #22c55e; font-weight: bold;'>✅ SUCCESS: {basename}</span>")
                    success_count += 1
                    
                    # Copy .ff file to output directory
                    try:
                        shutil.copy2(ff_path, output_path)
                        output.append(f"   📂 Copied .ff file to output: {output_path}")
                    except Exception as e:
                        output.append(f"   ⚠️  Warning: Could not copy .ff to output: {str(e)}")
                    
                    # Copy to source directory (input .txt and .ff files)
                    if source_dir:
                        try:
                            shutil.copy2(ff_path, source_dir)
                            output.append(f"   📂 Copied .ff file to source: {source_dir}")
                        except Exception as e:
                            output.append(f"   ⚠️  Warning: Could not copy .ff to source: {str(e)}")
                        try:
                            shutil.copy2(input_file, source_dir)
                            output.append(f"   📂 Copied input .txt to source: {source_dir}")
                        except Exception as e:
                            output.append(f"   ⚠️  Warning: Could not copy input to source: {str(e)}")
                    
                    # Copy to target directory (output .txt and .ff files)
                    if target_dir:
                        try:
                            shutil.copy2(output_file, target_dir)
                            output.append(f"   📂 Copied output .txt to target: {target_dir}")
                        except Exception as e:
                            output.append(f"   ⚠️  Warning: Could not copy output to target: {str(e)}")
                        try:
                            shutil.copy2(ff_path, target_dir)
                            output.append(f"   📂 Copied .ff file to target: {target_dir}")
                        except Exception as e:
                            output.append(f"   ⚠️  Warning: Could not copy .ff to target: {str(e)}")
                else:
                    output.append(f"<span style='color: #ef4444; font-weight: bold;'>❌ FAILED: {basename}</span>")
                    error_count += 1
                    
                    # Display dowitcher stderr output for errors
                    if result.stderr:
                        output.append("<span style='color: #ef4444;'>🚨 Error Details:</span>")
                        for line in result.stderr.strip().split('\n'):
                            if line.strip():
                                output.append(f"<span style='color: #ef4444;'>   {line}</span>")
                    
                    if result.returncode != 0:
                        output.append(f"<span style='color: #ef4444;'>   Exit code: {result.returncode}</span>")
                
                output.append("")
                output.append("-" * 40)
                output.append("")
                
            except Exception as e:
                output.append(f"<span style='color: #ef4444; font-weight: bold;'>❌ ERROR: {basename} - {str(e)}</span>")
                error_count += 1
                output.append("")
                output.append("-" * 40)
                output.append("")
        
        output.append("")
        output.append("="*60)
        output.append(f"<span style='color: #3b82f6; font-weight: bold; font-size: 1.1em;'>🎉 BULK CONVERSION COMPLETED</span>")
        
        # Color-coded summary
        total_text = f"Total: {len(input_files)} files"
        success_text = f"<span style='color: #22c55e; font-weight: bold;'>Success: {success_count}</span>" if success_count > 0 else "Success: 0"
        error_text = f"<span style='color: #ef4444; font-weight: bold;'>Errors: {error_count}</span>" if error_count > 0 else "Errors: 0"
        skipped_text = f"<span style='color: #ef4444; font-weight: bold;'>Skipped: {skipped_count}</span>" if skipped_count > 0 else "Skipped: 0"
        
        output.append(f"{total_text} | {success_text} | {error_text} | {skipped_text}")
        
        # Overall status
        if error_count == 0 and success_count > 0 and skipped_count == 0:
            output.append(f"<span style='color: #22c55e; font-weight: bold;'>🎯 STATUS: ALL CONVERSIONS SUCCESSFUL!</span>")
        elif error_count == 0 and success_count > 0 and skipped_count > 0:
            output.append(f"<span style='color: #22c55e; font-weight: bold;'>🎯 STATUS: ALL CONVERSIONS SUCCESSFUL! (<span style='color: #ef4444;'>{skipped_count} files skipped due to missing format files</span>)</span>")
        elif success_count > 0 and error_count > 0:
            output.append(f"<span style='color: #f59e0b; font-weight: bold;'>⚠️  STATUS: PARTIAL SUCCESS ({success_count} completed, {error_count} failed, <span style='color: #ef4444;'>{skipped_count} skipped</span>)</span>")
        elif error_count > 0 and success_count == 0:
            output.append(f"<span style='color: #ef4444; font-weight: bold;'>❌ STATUS: ALL CONVERSIONS FAILED (<span style='color: #ef4444;'>{skipped_count} files also skipped</span>)</span>")
        elif skipped_count > 0 and success_count == 0 and error_count == 0:
            output.append(f"<span style='color: #ef4444; font-weight: bold;'>⚠️  STATUS: ALL FILES SKIPPED (no format files found)</span>")
        else:
            output.append(f"<span style='color: #6b7280;'>ℹ️  STATUS: NO FILES PROCESSED</span>")
            
        output.append("="*60)
        
        result_output = '\n'.join(output)
        
        # Log the complete bulk conversion output
        log_command_output(
            "BULK CONVERSION",
            f"Process all .ff files in {folder_name}",
            result_output,
            error_count == 0
        )
        
        return result_output, True
    except Exception as e:
        error_output = f"❌ Error in run_bulk_conversion: {str(e)}\n{traceback.format_exc()}"
        log_command_output("BULK CONVERSION", f"Process {folder_name} files", error_output, False)
        return error_output, False

def rename_file(folder_path, old_filename, new_name):
    """Rename a .ff file"""
    try:
        if not folder_path:
            return 'Error: Folder path is empty. Please check your path.txt configuration.'
        if not os.path.exists(folder_path):
            return f'Error: Folder path does not exist: {folder_path}'
        if not old_filename:
            return 'Error: Please select a file to rename.'
        if not new_name:
            return 'Error: Please provide a new name for the file.'
        
        max_retries = 3
        retry_delay = 0.5
        
        for attempt in range(max_retries):
            try:
                src = os.path.join(folder_path, old_filename)
                
                if not os.path.exists(src):
                    if attempt < max_retries - 1:
                        time.sleep(retry_delay)
                        continue
                    return f'Error: File not found: {old_filename}'
                
                dst = os.path.join(folder_path, f'{new_name}.ff')
                
                if os.path.exists(dst):
                    os.remove(dst)
                    msg = f"[Override] Removed existing file: '{new_name}.ff'\n"
                else:
                    msg = ""
                
                os.rename(src, dst)
                result = msg + f"✅ Successfully renamed '{old_filename}' to '{new_name}.ff'"
                
                # Log the rename operation
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

def run_dowitcher(paths, new_name, records=None, display=False, hex_display=False, input_display=False, particular_records=False):
    """Run dowitcher.exe for file conversion/display"""
    format_path = paths.get('FORMAT_PATH', '')
    input_path = paths.get('INPUT_PATH', '')
    output_path = paths.get('OUTPUT_PATH', '')
    log_path = paths.get('LOG_PATH', '')
    source = paths.get('source', '')
    target = paths.get('target', '')
    
    # Log operation start
    operation_name = "DOWITCHER DISPLAY" if display else "DOWITCHER CONVERT"
    logger.info(f"{'='*60}")
    logger.info(f"{operation_name} OPERATION STARTED")
    logger.info(f"File: {new_name}")
    if records:
        logger.info(f"Records: {records}")
    logger.info(f"{'='*60}")
    
    if not format_path or not os.path.exists(format_path):
        return f'Error: FORMAT_PATH is invalid or does not exist: {format_path}'
    if not input_path or not os.path.exists(input_path):
        return f'Error: INPUT_PATH is invalid or does not exist: {input_path}'
    if not output_path or not os.path.exists(output_path):
        return f'Error: OUTPUT_PATH is invalid or does not exist: {output_path}'
    
    override_msg = "[File Override Mode: ON] Existing files in source/target folders will be cleared and overwritten.\n\n"
    
    script_dir = os.getcwd()
    dowitcher_exe = os.path.join(script_dir, 'dowitcher.exe')
    
    if not os.path.exists(dowitcher_exe):
        return f'Error: dowitcher.exe not found at {dowitcher_exe}'
    
    ff_file = os.path.join(format_path, new_name + '.ff')
    input_file = os.path.join(input_path, new_name + '.txt')
    output_file = os.path.join(output_path, new_name + '.txt')
    
    time.sleep(0.2)
    
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
        # result = subprocess.run(cmd, capture_output=True, text=True)
        # output = (override_msg if not display else "") + result.stdout + ('\n[Error]\n' + result.stderr if result.stderr else '')
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



# Templates from file.py
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

        .output-box {
            margin-top: 30px;
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
                    const textContent = output.textContent;
                    navigator.clipboard.writeText(textContent).then(function() {
                        showToast('Output copied to clipboard');
                    }).catch(function() {
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = textContent;
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
                        showToast('Output copied to clipboard');
                    });
                });
            }
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
        
        // Hide loading overlay when page loads
        window.addEventListener('load', function() {
            if (loadingOverlay) {
                loadingOverlay.style.display = 'none';
            }
        });
    </script>
</head>
<body>
<div class="container">
    <div class="breadcrumb">
        <a href="/">🏠 Home</a>
        <span>→</span>
        <span>🏷️ Rename .FF File</span>
    </div>

    <h1>File Conversion - Rename .FF File</h1>
    
    <form method="post" id="renameForm">
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
                <button type="button" onclick="scrollToTop()" class="btn-mini">⬆️ Top</button>
                <button type="button" onclick="scrollToBottom()" class="btn-mini">⬇️ Bottom</button>
                <button type="button" onclick="resetOutputSize()" class="btn-mini">📐 Reset Size</button>
            </div>
        </div>
        <div class="output-box">
            <div class="output-content">{{ output }}</div>
            <div class="resize-handle" title="Drag to resize"></div>
        </div>
        <div style="text-align: center; margin-top: 10px; color: var(--text-secondary); font-size: 0.85rem;">
            💡 <strong>Tip:</strong> Drag the bottom-right corner to resize • Use scroll bars for navigation • Long lines will scroll horizontally
        </div>
    </div>
    {% endif %}
    
    <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid var(--border); color: var(--text-secondary); font-size: 0.9rem;">
        <p style="margin: 5px 0;">File Conversion</p>
        <p style="margin: 5px 0;">Powered by Astadia TEAM</p>
    </div>
</div>

<div id="loadingOverlay" class="loading-overlay" style="display: none;">
    <div class="loading-spinner"></div>
    <p>Processing your request...</p>
</div>

<div id="toast" class="toast"></div>
</body>
</html>
'''

app = Flask(__name__)

# Main template with the new buttons
MAIN_TEMPLATE = '''
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
            margin-top: 30px;
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
                    output.textContent = '';
                    showToast('Output cleared');
                });
            }

            // Copy output
            if (copyBtn && output) {
                copyBtn.addEventListener('click', function() {
                    const textContent = output.textContent;
                    navigator.clipboard.writeText(textContent).then(function() {
                        showToast('Output copied to clipboard');
                    }).catch(function() {
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = textContent;
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
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
    </script>
</head>
<body>
<div class="container">
    <div class="breadcrumb">
        <a href="/">🏠 Home</a> 
        <span>→</span> 
        <span>✏️ Modify .FF File</span>
    </div>

    <h1>File Conversion - Modify .FF File</h1>
    
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
        <p style="margin: 5px 0;">File Conversion</p>
        <p style="margin: 5px 0;">Powered by Astadia TEAM</p>
    </div>
</div>

<div id="loadingOverlay" class="loading-overlay" style="display: none;">
    <div class="loading-spinner"></div>
    <p>Processing your request...</p>
</div>

<div id="toast" class="toast"></div>
</body>
</html>
'''

# Create Folder Template
CREATE_FOLDER_TEMPLATE = '''
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

        .output-box {
            margin-top: 30px;
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
        document.addEventListener('DOMContentLoaded', function() {
            const form = document.getElementById('royForm');
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
                    output.textContent = '';
                    showToast('Output cleared');
                });
            }

            // Copy output
            if (copyBtn && output) {
                copyBtn.addEventListener('click', function() {
                    const textContent = output.textContent;
                    navigator.clipboard.writeText(textContent).then(function() {
                        showToast('Output copied to clipboard');
                    }).catch(function() {
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = textContent;
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
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
    </script>
</head>
<body>
<div class="container">
    <div class="breadcrumb">
        <a href="/">🏠 Home</a> 
        <span>→</span> 
        <span>🔧 Roy's EBCDIC Tool</span>
    </div>

    <h1>File Conversion - Roy's EBCDIC Tool</h1>
    
    <form method="post" id="royForm">
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
        <p style="margin: 5px 0;">File Conversion</p>
        <p style="margin: 5px 0;">Powered by Astadia TEAM</p>
    </div>
</div>

<div id="loadingOverlay" class="loading-overlay" style="display: none;">
    <div class="loading-spinner"></div>
    <p>Processing your request...</p>
</div>

<div id="toast" class="toast"></div>
</body>
</html>
'''

app = Flask(__name__)

# Main template with the new buttons
MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Conversion Studio</title>
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
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            width: 100%;
            background: var(--bg-card);
            padding: 40px;
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
            margin-bottom: 30px;
            text-align: center;
        }

        .button-grid {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-top: 30px;
        }

        .btn {
            padding: 20px 15px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            text-decoration: none;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 8px;
            color: white;
            background: var(--primary-gradient);
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .icon {
            font-size: 1.3rem;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-weight: 600;
            font-size: 0.9rem;
        }

        input[type="text"] {
            width: 100%;
            padding: 15px 20px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
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
            font-style: italic;
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

        .control-btn {
            padding: 8px 16px;
            background: var(--primary-gradient);
            border: none;
            border-radius: 8px;
            color: white;
            font-size: 0.85rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
        }

        .control-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(37, 99, 235, 0.4);
        }

        .output-box {
            position: relative;
            width: 100%;
            min-height: 450px;
            max-height: 800px;
            padding: 15px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            color: var(--text-primary);
            font-family: 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            overflow: auto;
            white-space: pre;
            resize: both;
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
            background: var(--primary-color);
            border-radius: 6px;
        }

        .output-box::-webkit-scrollbar-thumb:hover {
            background: var(--accent-color);
        }

        .resize-handle {
            position: absolute;
            bottom: 5px;
            right: 5px;
            width: 15px;
            height: 15px;
            background: linear-gradient(135deg, transparent 0%, transparent 50%, var(--primary-color) 50%, var(--primary-color) 100%);
            pointer-events: none;
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            padding-top: 30px;
            border-top: 1px solid var(--border);
            color: var(--text-secondary);
            font-size: 0.9rem;
        }

        .footer p {
            margin: 5px 0;
        }

        /* Responsive design for smaller screens */
        @media (max-width: 1024px) {
            .button-grid {
                grid-template-columns: repeat(2, 1fr);
            }
        }

        @media (max-width: 640px) {
            .button-grid {
                grid-template-columns: 1fr;
            }
            
            .container {
                padding: 20px;
            }
            
            h1 {
                font-size: 2rem;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 File Conversion Studio</h1>
        
        <!-- Button Reference Guide -->
        <div style="background: var(--bg-secondary); border: 2px solid var(--border); border-radius: 12px; padding: 20px; margin-bottom: 30px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="color: var(--accent-color); margin: 0; font-size: 1.2rem;">📖 Quick Reference Guide</h3>
                <button type="button" onclick="toggleReferenceGuide()" style="padding: 8px 16px; background: var(--primary-gradient); border: none; border-radius: 8px; color: white; font-size: 0.85rem; font-weight: 600; cursor: pointer; transition: all 0.3s;" onmouseover="this.style.transform='translateY(-2px)'" onmouseout="this.style.transform='translateY(0)'">
                    <span id="toggleIcon">➖</span> <span id="toggleText">Minimize</span>
                </button>
            </div>
            <div id="referenceContent" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 10px; font-size: 0.9rem; line-height: 1.8;">
                <div><strong>📁 Create Folder Structure:</strong> Creates project directories (input, output, copybook, expfd, datamatch, etc.)</div>
                <div><strong>🗂️ Open Project Folders:</strong> Opens all project folders in Windows Explorer for easy access</div>
                <div><strong>🔧 Run Dowitcher:</strong> Converts EBCDIC file to ASCII format using Dowitcher tool</div>
                <div><strong>🔁 Bulk Conversion:</strong> Processes multiple files in batch mode for mass conversion</div>
                <div><strong>👁️ Display Output:</strong> Shows converted output file contents in readable format</div>
                <div><strong>🔢 Display Output with Hex:</strong> Displays output with hexadecimal values for debugging</div>
                <div><strong>📋 Particular Records:</strong> Extracts and displays specific record ranges from output file</div>
                <div><strong>📄 Input Display Hex:</strong> Shows input file with hexadecimal representation</div>
                <div><strong>⚙️ Update Paths:</strong> Configure base paths and project settings</div>
                <div><strong>📋 View Logs:</strong> Access application logs for troubleshooting and monitoring</div>
                <div><strong>📖 View User Guide:</strong> Complete documentation and usage instructions</div>
            </div>
        </div>
        
        <form method="POST" action="/">
            <div class="form-group">
                <label for="new_name">📂 File Name (without extension):</label>
                <input type="text" id="new_name" name="new_name" value="{{ new_name }}" 
                       placeholder="e.g., myfile">
                <div class="help-text">Enter the file name for conversion/display operations</div>
            </div>

            <div class="form-group">
                <label for="records">📋 Records (optional):</label>
                <input type="text" id="records" name="records" value="{{ records }}" 
                       placeholder="e.g., 1-10 or 5">
                <div class="help-text">Specify record range for display/particular records operations</div>
            </div>
            
            <div class="button-grid">
                <button type="submit" name="action" value="create_folder" class="btn">
                    <span class="icon">📁</span>
                    <span>Create Folder Structure</span>
                </button>
                
                <button type="submit" name="action" value="open_folders" class="btn">
                    <span class="icon">🗂️</span>
                    <span>Open Project Folders</span>
                </button>
                
                <button type="submit" name="action" value="dowitcher" class="btn">
                    <span class="icon">🔧</span>
                    <span>Run Dowitcher (Convert to ASCII)</span>
                </button>
                
                <button type="submit" name="action" value="bulk_conversion" class="btn">
                    <span class="icon">🔁</span>
                    <span>Bulk Conversion</span>
                </button>
                
                <button type="submit" name="action" value="display" class="btn">
                    <span class="icon">👁️</span>
                    <span>Display Output</span>
                </button>
                
                <button type="submit" name="action" value="display_hex" class="btn">
                    <span class="icon">🔢</span>
                    <span>Display Output with Hex</span>
                </button>
                
                <button type="submit" name="action" value="particular_records" class="btn">
                    <span class="icon">📋</span>
                    <span>Particular Records</span>
                </button>
                
                <button type="submit" name="action" value="input_display_hex" class="btn">
                    <span class="icon">📄</span>
                    <span>Input Display Hex</span>
                </button>
                
                <button type="submit" name="action" value="update_paths" class="btn">
                    <span class="icon">⚙️</span>
                    <span>Update Paths</span>
                </button>
                
                <button type="submit" name="action" value="view_logs" class="btn">
                    <span class="icon">📋</span>
                    <span>View Logs</span>
                </button>
                
                <a href="/user_guide" class="btn" style="text-decoration: none;">
                    <span class="icon">📖</span>
                    <span>View User Guide</span>
                </a>
            </div>
        </form>

        <script>
            function toggleReferenceGuide() {
                const content = document.getElementById('referenceContent');
                const icon = document.getElementById('toggleIcon');
                const text = document.getElementById('toggleText');
                
                if (content.style.display === 'none') {
                    content.style.display = 'grid';
                    icon.textContent = '➖';
                    text.textContent = 'Minimize';
                } else {
                    content.style.display = 'none';
                    icon.textContent = '➕';
                    text.textContent = 'Maximize';
                }
            }
        </script>

        {% if output %}
        <div class="output-section">
            <div class="output-header">
                <label for="output">📤 Output:</label>
                <div class="output-controls">
                    <button type="button" class="control-btn" onclick="scrollToTop()">⬆️ Top</button>
                    <button type="button" class="control-btn" onclick="scrollToBottom()">⬇️ Bottom</button>
                    <button type="button" class="control-btn" onclick="resetOutputSize()">🔄 Reset Size</button>
                    <button type="button" class="control-btn" onclick="clearOutput()">🗑️ Clear</button>
                    <button type="button" class="control-btn" onclick="copyOutput()">📋 Copy</button>
                </div>
            </div>
            <div class="output-box" id="output">{{ output|safe }}</div>
        </div>

        <script>
            function scrollToTop() {
                document.getElementById('output').scrollTop = 0;
            }

            function scrollToBottom() {
                const output = document.getElementById('output');
                output.scrollTop = output.scrollHeight;
            }

            function resetOutputSize() {
                const output = document.getElementById('output');
                output.style.width = '';
                output.style.height = '';
            }

            function clearOutput() {
                if (confirm('Are you sure you want to clear the output?')) {
                    document.getElementById('output').innerHTML = '';
                }
            }

            function copyOutput() {
                const output = document.getElementById('output');
                const text = output.innerText;
                navigator.clipboard.writeText(text).then(() => {
                    alert('Output copied to clipboard!');
                }).catch(err => {
                    console.error('Failed to copy:', err);
                });
            }
        </script>
        {% endif %}

        <div class="footer">
            <p>File Conversion Studio</p>
            <p>Powered by Astadia TEAM</p>
        </div>
    </div>
</body>
</html>
'''

# Create Folder Template
CREATE_FOLDER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Folder Structure</title>
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
            max-width: 800px;
            margin: 20px auto;
            background: var(--bg-card);
            padding: 40px;
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
            margin-bottom: 30px;
            text-align: center;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9rem;
        }

        input[type="text"] {
            width: 100%;
            padding: 15px 20px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
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
            font-style: italic;
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
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 2px solid var(--border);
        }

        .btn-secondary:hover {
            border-color: var(--primary-color);
            transform: translateY(-3px);
        }

        .output-box {
            margin-top: 30px;
            padding: 0;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            min-height: 500px;
            max-height: none;
            resize: both;
            overflow: auto;
            position: relative;
        }

        .output-box pre {
            padding: 20px;
            white-space: pre;
            font-family: 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            color: var(--text-primary);
            margin: 0;
            min-width: max-content;
            overflow-wrap: normal;
            word-break: normal;
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

        .output-box.success {
            border-color: var(--accent-color);
        }

        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.95);
            justify-content: center;
            align-items: center;
            z-index: 9999;
            flex-direction: column;
        }

        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 5px solid rgba(37, 99, 235, 0.3);
            border-top-color: var(--accent-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .loading-text {
            color: var(--accent-color);
            margin-top: 20px;
            font-size: 1.2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">Creating folders... Please wait</div>
    </div>

    <div class="container">
        <h1>📁 Create Folder Structure</h1>
        
        <form method="POST" id="folderForm" onsubmit="showLoading()">
            <div class="form-group">
                <label for="folder_name">📂 Project Folder Name:</label>
                <input type="text" id="folder_name" name="folder_name" value="{{ folder_name }}" required 
                       placeholder="e.g., MyProject">
                <div class="help-text">Enter the name for your project folder</div>
            </div>

            <div class="button-group">
                <a href="/" class="btn btn-secondary">← Back to Main Menu</a>
                <button type="submit" class="btn btn-primary">📁 Create Folders</button>
            </div>
        </form>

        {% if output %}
        <div style="margin-top: 30px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="color: var(--text-secondary); margin: 0;">📤 Operation Output</h3>
                <div style="display: flex; gap: 10px;">
                    <button onclick="scrollToTop()" style="padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); font-size: 0.85rem; cursor: pointer;">⬆️ Top</button>
                    <button onclick="scrollToBottom()" style="padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); font-size: 0.85rem; cursor: pointer;">⬇️ Bottom</button>
                    <button onclick="resetOutputSize()" style="padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); font-size: 0.85rem; cursor: pointer;">📐 Reset Size</button>
                </div>
            </div>
            <div class="output-box {% if success %}success{% endif %}">
                <pre>{{ output }}</pre>
                <div class="resize-handle" title="Drag to resize"></div>
            </div>
            <div style="text-align: center; margin-top: 10px; color: var(--text-secondary); font-size: 0.85rem;">
                💡 <strong>Tip:</strong> Drag the bottom-right corner to resize • Use scroll bars for navigation
            </div>
        </div>
        {% endif %}
        
        <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid var(--border); color: var(--text-secondary); font-size: 0.9rem;">
            <p>File Conversion Studio</p>
            <p>Powered by Astadia TEAM</p>
        </div>
    </div>

    <script>
        function showLoading() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }
        
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
                outputBox.style.height = '500px';
            }
        }
        
        window.addEventListener('load', function() {
            document.getElementById('loadingOverlay').style.display = 'none';
        });
    </script>
</body>
</html>
'''

# Open Folders Template
OPEN_FOLDERS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Open Project Folders</title>
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
            max-width: 800px;
            margin: 20px auto;
            background: var(--bg-card);
            padding: 40px;
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
            margin-bottom: 30px;
            text-align: center;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: var(--text-secondary);
            font-weight: 600;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            font-size: 0.9rem;
        }

        input[type="text"] {
            width: 100%;
            padding: 15px 20px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
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
            font-style: italic;
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
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 2px solid var(--border);
        }

        .btn-secondary:hover {
            border-color: var(--primary-color);
            transform: translateY(-3px);
        }

        .output-box {
            margin-top: 30px;
            padding: 0;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            min-height: 500px;
            max-height: none;
            resize: both;
            overflow: auto;
            position: relative;
        }

        .output-box pre {
            padding: 20px;
            white-space: pre;
            font-family: 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            color: var(--text-primary);
            margin: 0;
            min-width: max-content;
            overflow-wrap: normal;
            word-break: normal;
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

        .output-box.success {
            border-color: var(--accent-color);
        }

        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.95);
            justify-content: center;
            align-items: center;
            z-index: 9999;
            flex-direction: column;
        }

        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 5px solid rgba(37, 99, 235, 0.3);
            border-top-color: var(--accent-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .loading-text {
            color: var(--accent-color);
            margin-top: 20px;
            font-size: 1.2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">Opening folders... Please wait</div>
    </div>

    <div class="container">
        <h1>🗂️ Open Project Folders</h1>
        
        <form method="POST" id="openForm" onsubmit="showLoading()">
            <div class="form-group">
                <label for="folder_name">📂 Project Folder Name:</label>
                <input type="text" id="folder_name" name="folder_name" value="{{ folder_name }}" required 
                       placeholder="e.g., MyProject">
                <div class="help-text">Enter the project folder name to open all subfolders</div>
            </div>

            <div class="button-group">
                <a href="/" class="btn btn-secondary">← Back to Main Menu</a>
                <button type="submit" class="btn btn-primary">🗂️ Open All Folders</button>
            </div>
        </form>

        {% if output %}
        <div style="margin-top: 30px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="color: var(--text-secondary); margin: 0;">📤 Operation Output</h3>
                <div style="display: flex; gap: 10px;">
                    <button onclick="scrollToTop()" style="padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); font-size: 0.85rem; cursor: pointer;">⬆️ Top</button>
                    <button onclick="scrollToBottom()" style="padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); font-size: 0.85rem; cursor: pointer;">⬇️ Bottom</button>
                    <button onclick="resetOutputSize()" style="padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); font-size: 0.85rem; cursor: pointer;">📐 Reset Size</button>
                </div>
            </div>
            <div class="output-box {% if success %}success{% endif %}">
                <pre>{{ output }}</pre>
                <div class="resize-handle" title="Drag to resize"></div>
            </div>
            <div style="text-align: center; margin-top: 10px; color: var(--text-secondary); font-size: 0.85rem;">
                💡 <strong>Tip:</strong> Drag the bottom-right corner to resize • Use scroll bars for navigation
            </div>
        </div>
        {% endif %}
        
        <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid var(--border); color: var(--text-secondary); font-size: 0.9rem;">
            <p>File Conversion Studio</p>
            <p>Powered by Astadia TEAM</p>
        </div>
    </div>

    <script>
        function showLoading() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }
        
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
                outputBox.style.height = '500px';
            }
        }
        
        window.addEventListener('load', function() {
            document.getElementById('loadingOverlay').style.display = 'none';
        });
    </script>
</body>
</html>
'''

# Bulk Conversion Template
BULK_CONVERSION_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bulk Conversion</title>
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
            max-width: 900px;
            margin: 20px auto;
            background: var(--bg-card);
            padding: 40px;
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
            margin-bottom: 30px;
            text-align: center;
        }

        .info-box {
            background: var(--bg-secondary);
            padding: 20px;
            border-radius: 12px;
            margin-bottom: 30px;
            border-left: 4px solid var(--accent-color);
        }

        .info-box p {
            color: var(--text-secondary);
            margin: 5px 0;
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
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-primary);
            border: 2px solid var(--border);
        }

        .btn-secondary:hover {
            border-color: var(--primary-color);
            transform: translateY(-3px);
        }

        .output-box {
            margin-top: 30px;
            padding: 0;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            min-height: 600px;
            max-height: none;
            resize: both;
            overflow: auto;
            position: relative;
        }

        .output-content {
            padding: 20px;
            white-space: pre;
            font-family: 'Consolas', monospace;
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
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 23, 42, 0.95);
            justify-content: center;
            align-items: center;
            z-index: 9999;
            flex-direction: column;
        }

        .loading-spinner {
            width: 60px;
            height: 60px;
            border: 5px solid rgba(37, 99, 235, 0.3);
            border-top-color: var(--accent-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .loading-text {
            color: var(--accent-color);
            margin-top: 20px;
            font-size: 1.2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="loading-spinner"></div>
        <div class="loading-text">Processing bulk conversion... This may take several minutes</div>
    </div>

    <div class="container">
        <h1>🔁 Bulk Conversion</h1>
        
        <div class="info-box">
            <p><strong>ℹ️ How it works:</strong></p>
            <p>• Enter your application name (e.g., occ, myapp)</p>
            <p>• Uses BASE_PATH from path.txt as the base directory</p>
            <p>• Processes all .ff files from: BASE_PATH/appname/FF_FILES/datamig/file-format</p>
            <p>• Converts input files from: BASE_PATH/appname/input</p>
            <p>• Saves output to: BASE_PATH/appname/output</p>
        </div>

        <form method="POST" id="bulkForm" onsubmit="showLoading()">
            <div style="margin-bottom: 25px;">
                <label for="folder_name" style="display: block; margin-bottom: 8px; color: var(--text-secondary); font-weight: 600;">
                    📁 Application Name:
                </label>
                <input type="text" 
                       id="folder_name" 
                       name="folder_name" 
                       value="{{ folder_name }}"
                       placeholder="e.g., occ"
                       required
                       style="width: 100%; padding: 15px 20px; background: var(--bg-secondary); border: 2px solid var(--border); border-radius: 12px; color: var(--text-primary); font-size: 1rem;">
                <div style="font-size: 0.85rem; color: var(--text-secondary); margin-top: 5px; font-style: italic;">
                    Enter the application folder name (e.g., occ, myapp)
                </div>
            </div>
            
            <div class="button-group">
                <a href="/" class="btn btn-secondary">← Back to Main Menu</a>
                <button type="submit" class="btn btn-primary">🔁 Start Bulk Conversion</button>
            </div>
        </form>

        {% if output %}
        <div style="margin-top: 30px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                <h3 style="color: var(--text-secondary); margin: 0;">📤 Conversion Output</h3>
                <div style="display: flex; gap: 10px;">
                    <button onclick="scrollToTop()" style="padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); font-size: 0.85rem; cursor: pointer;">⬆️ Top</button>
                    <button onclick="scrollToBottom()" style="padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); font-size: 0.85rem; cursor: pointer;">⬇️ Bottom</button>
                    <button onclick="resetOutputSize()" style="padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); font-size: 0.85rem; cursor: pointer;">📐 Reset Size</button>
                    <button onclick="copyOutput()" style="padding: 8px 16px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-secondary); font-size: 0.85rem; cursor: pointer;">📋 Copy</button>
                </div>
            </div>
            <div class="output-box {% if success %}success{% endif %}">
                <div class="output-content">{{ output|safe }}</div>
                <div class="resize-handle" title="Drag to resize"></div>
            </div>
            <div style="text-align: center; margin-top: 10px; color: var(--text-secondary); font-size: 0.85rem;">
                💡 <strong>Tip:</strong> Drag the bottom-right corner to resize • Use scroll bars for navigation • Long lines will scroll horizontally
            </div>
        </div>
        {% endif %}
        
        <div style="text-align: center; margin-top: 40px; padding-top: 30px; border-top: 1px solid var(--border); color: var(--text-secondary); font-size: 0.9rem;">
            <p>File Conversion Studio</p>
            <p>Powered by Astadia TEAM</p>
        </div>
    </div>

    <script>
        function showLoading() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }
        
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
                outputBox.style.height = '600px';
            }
        }
        
        function copyOutput() {
            const outputContent = document.querySelector('.output-content');
            if (outputContent) {
                const textContent = outputContent.textContent;
                navigator.clipboard.writeText(textContent).then(function() {
                    alert('Output copied to clipboard!');
                }).catch(function() {
                    // Fallback for older browsers
                    const textArea = document.createElement('textarea');
                    textArea.value = textContent;
                    document.body.appendChild(textArea);
                    textArea.select();
                    document.execCommand('copy');
                    document.body.removeChild(textArea);
                    alert('Output copied to clipboard!');
                });
            }
        }
        
        window.addEventListener('load', function() {
            document.getElementById('loadingOverlay').style.display = 'none';
            
            // Auto-scroll to bottom when output is loaded
            const outputBox = document.querySelector('.output-box');
            if (outputBox) {
                setTimeout(() => {
                    outputBox.scrollTop = outputBox.scrollHeight;
                }, 100);
            }
        });
    </script>
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
        script_dir = os.getcwd()
        config_path = os.path.join(script_dir, 'path.txt')
        
        if not os.path.exists(config_path):
            output = f'Error: path.txt not found at {config_path}\nCurrent working directory: {script_dir}'
            return render_template_string(MAIN_TEMPLATE, output=output, new_name=new_name, records=records)
        
        paths = read_paths(config_path)
        
        if request.method == 'POST':
            if action == 'create_folder':
                return redirect(url_for('create_folder_page'))
            elif action == 'open_folders':
                return redirect(url_for('open_folders_page'))
            elif action == 'dowitcher' and new_name:
                output = run_dowitcher(paths, new_name)
            elif action == 'bulk_conversion':
                return redirect(url_for('bulk_conversion_page'))
            elif action == 'display' and new_name:
                output = run_dowitcher(paths, new_name, records=records, display=True)
            elif action == 'display_hex' and new_name:
                output = run_dowitcher(paths, new_name, records=records, display=True, hex_display=True)
            elif action == 'particular_records' and new_name:
                output = run_dowitcher(paths, new_name, records=records, particular_records=True)
            elif action == 'input_display_hex' and new_name:
                output = run_dowitcher(paths, new_name, records=records, display=True, hex_display=True, input_display=True)
            elif action == 'update_paths':
                return redirect(url_for('update_paths_page'))
            elif action == 'view_logs':
                return redirect(url_for('view_logs_page'))
    except Exception as e:
        output = f'Critical Error: {e}\n\nFull Traceback:\n{traceback.format_exc()}'
    
    return render_template_string(MAIN_TEMPLATE, output=output, new_name=new_name, records=records)

@app.route('/create_folder', methods=['GET', 'POST'])
def create_folder_page():
    output = None
    success = False
    folder_name = ''
    
    if request.method == 'POST':
        folder_name = request.form.get('folder_name', '').strip()
        
        # Read path.txt to get base_path
        config_file = os.path.join(os.getcwd(), 'path.txt')
        config = read_paths(config_file)
        base_path = config.get('base_path', os.getcwd())
        
        if folder_name:
            output, success = run_create_folder(folder_name, base_path)
    
    return render_template_string(CREATE_FOLDER_TEMPLATE, 
                                   output=output, 
                                   success=success,
                                   folder_name=folder_name)

@app.route('/open_folders', methods=['GET', 'POST'])
def open_folders_page():
    output = None
    success = False
    folder_name = ''
    
    if request.method == 'POST':
        folder_name = request.form.get('folder_name', '').strip()
        
        # Read path.txt to get base_path
        config_file = os.path.join(os.getcwd(), 'path.txt')
        config = read_paths(config_file)
        base_path = config.get('base_path', os.getcwd())
        
        if folder_name:
            output, success = run_folder_open(folder_name, base_path)
    
    return render_template_string(OPEN_FOLDERS_TEMPLATE, 
                                   output=output, 
                                   success=success,
                                   folder_name=folder_name)

@app.route('/bulk_conversion', methods=['GET', 'POST'])
def bulk_conversion_page():
    output = None
    success = False
    folder_name = ''
    
    if request.method == 'POST':
        folder_name = request.form.get('folder_name', '').strip()
        
        # Read path.txt to get base_path
        path_file = os.path.join(os.getcwd(), 'path.txt')
        
        if not os.path.exists(path_file):
            output = f'Error: path.txt not found at {path_file}'
            success = False
        elif folder_name:
            # Read base path from path.txt
            config = read_paths(path_file)
            base_path = config.get('base_path', os.getcwd())
            
            output, success = run_bulk_conversion(folder_name, base_path)
        else:
            output = 'Error: Application name cannot be empty.'
            success = False
    
    return render_template_string(BULK_CONVERSION_TEMPLATE, 
                                   output=output, 
                                   success=success,
                                   folder_name=folder_name)

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

        .output-box {
            margin-top: 30px;
            padding: 0;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            min-height: 350px;
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
                    output.textContent = '';
                    alert('Output cleared!');
                });
            }

            // Copy output
            if (copyBtn && output) {
                copyBtn.addEventListener('click', function() {
                    const textContent = output.textContent;
                    navigator.clipboard.writeText(textContent).then(function() {
                        alert('Output copied to clipboard!');
                    }).catch(function() {
                        // Fallback for older browsers
                        const textArea = document.createElement('textarea');
                        textArea.value = textContent;
                        document.body.appendChild(textArea);
                        textArea.select();
                        document.execCommand('copy');
                        document.body.removeChild(textArea);
                        alert('Output copied to clipboard!');
                    });
                });
            }
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
                outputBox.style.height = '350px';
            }
        }
    </script>
</head>
<body>
<div class="container">
    <div class="breadcrumb">
        <a href="/">🏠 Home</a> 
        <span>→</span> 
        <span>⚙️ Update Paths</span>
    </div>

    <h1>File Conversion - Update Paths</h1>
    
    <div class="info-box">
        <h3>ℹ️ What does this do?</h3>
        <p>This tool updates the base path and application name in all paths in path.txt. It will:</p>
        <ul style="color: var(--text-secondary); margin-left: 20px;">
            <li>Update the base path (e.g., C:/File_conversion/delivery) for all directories</li>
            <li>Update the application name across all configured paths</li>
            <li>Automatically modify paths for input, output, FF_FILES, copybook, expfd, and datamatch directories</li>
            <li>Update CSV file name to match new application name</li>
        </ul>
        <p style="margin-top: 10px;"><strong>Example:</strong> Changing from "{{ base_path }}/RBS" to "D:/Projects/OCC" will update all paths accordingly</p>
        <p>Current base path: <span class="current-app">{{ base_path }}</span></p>
        <p>Current application name: <span class="current-app">{{ current_app }}</span></p>
    </div>
    
    <form method="post" id="pathForm">
        <div class="form-group">
            <label for="base_path">📁 Base Path:</label>
            <input type="text" id="base_path" name="base_path" value="{{ base_path }}" required 
                   placeholder="Enter base path (e.g., C:/File_conversion/delivery, D:/Projects)">
            <div class="help-text">The root directory where all application folders are located</div>
        </div>

        <div class="form-group">
            <label for="app_name">🔤 New Application Name:</label>
            <input type="text" id="app_name" name="app_name" value="{{ app_name }}" required 
                   placeholder="Enter new application name (e.g., RBS, OCC, CBR, MC)">
            <div class="help-text">All instances of "{{ current_app }}" in paths will be replaced with this name</div>
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
        <p style="margin: 5px 0;">File Conversion</p>
        <p style="margin: 5px 0;">Powered by Astadia TEAM</p>
    </div>
</div>
</body>
</html>
'''

@app.route('/update_paths', methods=['GET', 'POST'])
def update_paths_page():
    """Update application name and base path in path.txt"""
    output = ''
    success = False
    app_name = ''
    base_path = ''  # Will be read from path.txt
    current_app = ''  # Will be read from path.txt
    current_base = ''  # Will be read from path.txt
    
    # Read current application name and base path from path.txt
    try:
        config_file = os.path.join(os.getcwd(), 'path.txt')
        if os.path.exists(config_file):
            paths = read_paths(config_file)
            # Get base_path from path.txt
            if 'base_path' in paths:
                current_base = paths['base_path'].replace('\\', '/')
                base_path = current_base
            # Get current application from the application variable or parse from application path
            if 'application' in paths:
                app_path = paths['application'].replace('\\', '/')
                # Extract application name from path like C:/File_conversion/delivery/RBS
                current_app = app_path.split('/')[-1]
    except Exception as e:
        logger.error(f"Error reading paths from path.txt: {e}")
        pass
    
    if request.method == 'POST':
        app_name = request.form.get('app_name', '').strip()
        base_path = request.form.get('base_path', '').strip()
        
        if app_name and base_path:
            try:
                # Validate application name
                if not re.match(r'^[a-zA-Z0-9_-]+$', app_name):
                    output = 'Error: Application name can only contain letters, numbers, underscores, and hyphens.'
                else:
                    # Normalize base_path (remove trailing slash)
                    base_path = base_path.rstrip('/\\')
                    current_base_normalized = current_base.replace('\\', '/')
                    base_path_normalized = base_path.replace('\\', '/')
                    
                    # Read path.txt
                    config_file = os.path.join(os.getcwd(), 'path.txt')
                    if not os.path.exists(config_file):
                        output = f'Error: path.txt not found at {config_file}'
                    else:
                        with open(config_file, 'r') as f:
                            lines = f.readlines()
                        
                        # Replace base path and application name in paths
                        updated_lines = []
                        changes_count = 0
                        for line in lines:
                            if '=' in line:
                                # Get the key and value parts
                                key, value = line.split('=', 1)
                                original_value = value
                                
                                # First, replace base path if it changed (handle both forward and backslashes)
                                if current_base_normalized != base_path_normalized:
                                    # Replace both backslash and forward slash versions
                                    value = value.replace(current_base, base_path)
                                    value = value.replace(current_base.replace('\\', '/'), base_path.replace('\\', '/'))
                                    value = value.replace(current_base.replace('/', '\\'), base_path.replace('/', '\\'))
                                
                                # Then replace application name (only if it appears in the line)
                                if current_app in value:
                                    # Replace in directory paths: /RBS/ -> /newapp/
                                    value = value.replace(f'/{current_app}/', f'/{app_name}/')
                                    value = value.replace(f'\\{current_app}\\', f'\\{app_name}\\')
                                    
                                    # Replace in filenames: RBS.csv -> newapp.csv
                                    value = value.replace(f'{current_app}.', f'{app_name}.')
                                    
                                    # Replace standalone application path at end of line: /RBS\n -> /newapp\n
                                    value = value.replace(f'/{current_app}\n', f'/{app_name}\n')
                                    value = value.replace(f'/{current_app}\r\n', f'/{app_name}\r\n')
                                    value = value.replace(f'\\{current_app}\n', f'\\{app_name}\n')
                                    value = value.replace(f'\\{current_app}\r\n', f'\\{app_name}\r\n')
                                
                                updated_line = f'{key}={value}'
                                updated_lines.append(updated_line)
                                if value != original_value:
                                    changes_count += 1
                            else:
                                updated_lines.append(line)
                        
                        # Write back to path.txt
                        with open(config_file, 'w') as f:
                            f.writelines(updated_lines)
                        
                        success = True
                        output = ''.join(updated_lines)
                        if current_base_normalized != base_path_normalized and current_app != app_name:
                            output = f'✅ Successfully updated {changes_count} paths from "{current_base}/{current_app}" to "{base_path}/{app_name}"\n\n' + output
                        elif current_base_normalized != base_path_normalized:
                            output = f'✅ Successfully updated {changes_count} paths - base path changed to "{base_path}"\n\n' + output
                        else:
                            output = f'✅ Successfully updated {changes_count} paths from "{current_app}" to "{app_name}"\n\n' + output
                        current_app = app_name  # Update current_app display
                        current_base = base_path  # Update current_base display
                        
            except Exception as e:
                output = f'Error updating paths: {e}\n\nFull Traceback:\n{traceback.format_exc()}'
        else:
            output = 'Error: Both base path and application name are required.'
    
    return render_template_string(UPDATE_PATHS_TEMPLATE, output=output, success=success, 
                                 app_name=app_name, current_app=current_app, base_path=base_path)

@app.route('/view_logs')
def view_logs_page():
    """Display recent log entries"""
    try:
        log_dir = os.path.join(os.getcwd(), 'logs')
        log_filename = f"workflows_{datetime.datetime.now().strftime('%Y%m%d')}.log"
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
    """Display the User Guide"""
    try:
        guide_filepath = os.path.join(os.getcwd(), 'USER_GUIDE.txt')
        
        guide_content = ""
        if os.path.exists(guide_filepath):
            try:
                with open(guide_filepath, 'r', encoding='utf-8') as f:
                    guide_content = f.read()
            except Exception as e:
                guide_content = f"Error reading user guide: {str(e)}"
        else:
            guide_content = "User Guide not found. Please ensure USER_GUIDE.txt exists in the application directory."
        
        return render_template_string(USER_GUIDE_TEMPLATE, guide_content=guide_content, guide_filepath=guide_filepath)
    except Exception as e:
        logger.error(f"Error in user_guide_page: {str(e)}")
        return f"Error loading user guide: {str(e)}"

# Log Viewer Template
LOG_VIEWER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log Viewer - File Conversion Studio</title>
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

# User Guide Template
USER_GUIDE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>User Guide - File Conversion Studio</title>
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
            <p><strong>📁 Document:</strong> {{ guide_filepath }}</p>
            <p><strong>📚 Complete step-by-step guide to using File Conversion Studio</strong></p>
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



if __name__ == '__main__':
    import sys
    
    # Only ask for port on first run (not on Flask reloader restart)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        # Ask user for port number
        print("\n" + "="*60)
        print("  FILE CONVERSION STUDIO - Server Configuration")
        print("="*60)
        
        default_port = 3355
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
    else:
        # Reloader process - get port from environment
        port = int(os.environ.get('FLASK_PORT', 3355))
    
    app.run(debug=True, host='127.0.0.1', port=port)
