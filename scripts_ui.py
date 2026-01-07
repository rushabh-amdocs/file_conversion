import os
import re
import csv
import shutil
import subprocess
import traceback
import time
import logging
import datetime
from flask import Flask, render_template_string, request, redirect, url_for

# Global variable to track current log date
_current_log_date = None

# Setup logging
def setup_logging():
    """Setup logging configuration with timestamps - supports daily log rotation"""
    global _current_log_date
    
    # Create logs directory if it doesn't exist
    log_dir = os.path.join(os.getcwd(), 'logs')
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Create log file with current date
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    log_filename = f"ConvertFlow_{current_date}.log"
    log_filepath = os.path.join(log_dir, log_filename)
    
    # Create a custom logger for our application only
    logger = logging.getLogger('ConvertFlow')
    logger.setLevel(logging.INFO)
    
    # Remove any existing handlers
    for handler in logger.handlers[:]:
        handler.close()
        logger.removeHandler(handler)
    
    # Create file handler with custom format and immediate flushing
    file_handler = logging.FileHandler(log_filepath, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
    file_handler.setFormatter(file_formatter)
    
    # Add only file handler (no console output to avoid cluttering)
    logger.addHandler(file_handler)
    
    # Disable propagation to avoid duplicate logs
    logger.propagate = False
    
    # Disable Flask's werkzeug logger from writing to our log
    werkzeug_logger = logging.getLogger('werkzeug')
    werkzeug_logger.setLevel(logging.WARNING)
    
    # Update current log date
    _current_log_date = current_date
    
    return logger

def check_log_rotation():
    """Check if we need to rotate to a new log file (new day)"""
    global _current_log_date, logger
    
    current_date = datetime.datetime.now().strftime('%Y%m%d')
    if _current_log_date != current_date:
        # Date has changed, create new log file
        logger = setup_logging()

logger = setup_logging()

# Log application startup
logger.info("="*60)
logger.info("ConvertFlow Studio - Application Started")
logger.info(f"Timestamp: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
logger.info("="*60)

# Force flush at startup
for handler in logger.handlers:
    handler.flush()

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
    
    # Force immediate flush to ensure logs are written immediately
    for handler in logger.handlers:
        handler.flush()

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

def run_copy_bulk(source_path, dest_path, input_file):
    """Run the copy_bulk script functionality in Python"""
    try:
        output = []
        output.append("="*60)
        output.append("COPY BULK OPERATION STARTED")
        output.append("="*60)
        output.append(f"Source Path: {source_path}")
        output.append(f"Destination Path: {dest_path}")
        output.append(f"Input File: {input_file}")
        output.append("")
        
        # Check if input file exists
        if not os.path.exists(input_file):
            error_output = '\n'.join(output) + f"\n❌ ERROR: Input file '{input_file}' not found!"
            log_command_output("COPY BULK", f"Copy files from {source_path} to {dest_path}", error_output, False)
            return error_output, False
        
        # Check if source directory exists
        if not os.path.exists(source_path):
            error_output = '\n'.join(output) + f"\n❌ ERROR: Source directory not found: {source_path}"
            log_command_output("COPY BULK", f"Copy files from {source_path} to {dest_path}", error_output, False)
            return error_output, False
        
        # Create destination directory if it doesn't exist
        if not os.path.exists(dest_path):
            os.makedirs(dest_path)
            output.append(f"✅ Created destination directory: {dest_path}")
        
        # Read the input file and process each line
        total_files = 0
        success_count = 0
        error_count = 0
        
        with open(input_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or ',' not in line:
                    continue
                
                parts = line.split(',')
                if len(parts) < 2:
                    continue
                
                old_filename = parts[0].strip()
                new_filename = parts[1].strip()
                
                if not old_filename or not new_filename:
                    continue
                
                total_files += 1
                
                old_filepath = os.path.join(source_path, old_filename)
                new_filepath = os.path.join(dest_path, new_filename)
                
                # Check if source file exists
                if os.path.exists(old_filepath):
                    try:
                        # Copy the file
                        shutil.copy2(old_filepath, new_filepath)
                        output.append(f"✅ SUCCESS: Copied '{old_filename}' to '{new_filename}'")
                        success_count += 1
                    except Exception as e:
                        output.append(f"❌ ERROR: Failed to copy '{old_filename}' - {str(e)}")
                        error_count += 1
                else:
                    output.append(f"❌ ERROR: Source file not found: '{old_filename}'")
                    error_count += 1
        
        # Summary
        output.append("")
        output.append("="*60)
        output.append("OPERATION SUMMARY")
        output.append("="*60)
        output.append(f"Total files processed: {total_files}")
        output.append(f"✅ Successful copies: {success_count}")
        output.append(f"❌ Failed operations: {error_count}")
        output.append("="*60)
        
        if error_count == 0:
            output.append("\n🎉 All files have been copied successfully!")
        else:
            output.append(f"\n⚠️  {error_count} file(s) failed to copy. Check the log above for details.")
        
        result_output = '\n'.join(output)
        success = error_count == 0
        
        # Log the complete command output
        log_command_output(
            "COPY BULK",
            f"Copy files from {source_path} to {dest_path} using {input_file}",
            result_output,
            success
        )
        
        return result_output, True
        
    except Exception as e:
        error_output = f"❌ Error in run_copy_bulk: {str(e)}\n{traceback.format_exc()}"
        log_command_output("COPY BULK", f"Copy files from {source_path} to {dest_path}", error_output, False)
        return error_output, False

def run_bulk_expfd(config):
    """Run EXPFD creation for all copybooks in bulk"""
    try:
        from datetime import datetime
        import glob
        
        output = []
        output.append("="*60)
        output.append("BULK EXPFD CREATION STARTED")
        output.append("="*60)
        output.append(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        
        expfd_path = config.get('expfd', 'C:/File_conversion/occ/expfd')
        copybook_path = config.get('copybook', 'C:/File_conversion/occ/copybook')
        
        output.append(f"EXPFD Output Path: {expfd_path}")
        output.append(f"Copybook Path: {copybook_path}")
        output.append("")
        
        # Get all files in copybook directory
        copybook_files = glob.glob(os.path.join(copybook_path, '*'))
        
        if not copybook_files:
            error_output = '\n'.join(output) + f"\n❌ ERROR: No copybook files found in {copybook_path}"
            log_command_output("BULK EXPFD", "Create EXPFD files from copybooks", error_output, False)
            return error_output, False
        
        output.append(f"Found {len(copybook_files)} copybook file(s)")
        output.append("")
        
        # Helper functions
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
        
        # Process each copybook
        success_count = 0
        error_count = 0
        
        for copybook_file in copybook_files:
            copybook_name = os.path.basename(copybook_file)
            
            try:
                with open(copybook_file, 'r') as f:
                    copybook_content = f.read()
                
                # Process copybook
                filtered_content = remove_88_and_values(copybook_content)
                adjusted_content = adjust_01_level(filtered_content)
                modified_content = check_and_replace_values(adjusted_content)
                extracted_data = extract_columns('\n'.join(modified_content))
                
                # Generate header
                current_timestamp = datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
                header_lines = [
                    f"      * Generated by python on {current_timestamp}",
                    f"      * Original source file: {copybook_name}",
                    f"      * Original SELECT source file: {copybook_name}",
                    f"        SELECT {os.path.splitext(copybook_name)[0]} ASSIGN TO RA-GO99."
                ]
                
                # Write output file
                output_filename = os.path.join(expfd_path, f"{os.path.splitext(copybook_name)[0]}.expfd")
                with open(output_filename, 'w') as f:
                    for line in header_lines:
                        f.write(line + '\n')
                    for line in extracted_data:
                        formatted_line = ' ' * 7 + line.ljust(65)
                        f.write(formatted_line + '\n')
                
                output.append(f"✅ Created: {os.path.basename(output_filename)}")
                success_count += 1
                
            except Exception as e:
                output.append(f"❌ ERROR processing {copybook_name}: {str(e)}")
                error_count += 1
        
        output.append("")
        output.append("="*60)
        output.append("BULK EXPFD CREATION COMPLETED")
        output.append("="*60)
        output.append(f"Total files: {len(copybook_files)}")
        output.append(f"✅ Successful: {success_count}")
        output.append(f"❌ Failed: {error_count}")
        output.append(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        
        result_output = '\n'.join(output)
        success = error_count == 0 and success_count > 0
        log_command_output("BULK EXPFD", f"Create {len(copybook_files)} EXPFD file(s)", result_output, success)
        return result_output, True
        
    except Exception as e:
        error_output = f'❌ Error running Bulk EXPFD: {e}\n{traceback.format_exc()}'
        log_command_output("BULK EXPFD", "Create EXPFD files in bulk", error_output, False)
        return error_output, False

def run_bulk_dataturn(config):
    """Run DataTurn for all EXPFD files in bulk"""
    try:
        from datetime import datetime
        import glob
        
        output = []
        output.append("="*60)
        output.append("BULK DATATURN OPERATION STARTED")
        output.append("="*60)
        output.append(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        
        # Get configuration
        dataturn_exe = config.get('DATATURN_EXE_PATH', 'C:/Program Files/Anubex/DataTurn/bin/dataturn.exe')
        application = config.get('application', 'C:/File_conversion/occ')
        expfd_path = config.get('expfd', 'C:/File_conversion/occ/expfd')
        output_dir =f"{application}/FF_FILES"
        config_file = config.get('DATATURN_CONFIG_FILE', 'rushabh.configuration')
        repo_name = f"{application}/repo/repoCBR2"
        
        # Ensure repository directory exists
        repo_parent = os.path.dirname(repo_name)
        if not os.path.exists(repo_parent):
            os.makedirs(repo_parent, exist_ok=True)
        
        output.append(f"DataTurn Exe: {dataturn_exe}")
        output.append(f"EXPFD Path: {expfd_path}")
        output.append(f"Output Directory: {output_dir}")
        output.append(f"Repository: {repo_name}")
        output.append("")
        
        # Check if dataturn.exe exists
        if not os.path.exists(dataturn_exe):
            error_output = '\n'.join(output) + f"\n❌ ERROR: DataTurn executable not found at: {dataturn_exe}"
            log_command_output("BULK DATATURN", "Run DataTurn for EXPFD files", error_output, False)
            return error_output, False
        
        # Get all .expfd files
        expfd_files = glob.glob(os.path.join(expfd_path, '*.expfd'))
        
        if not expfd_files:
            error_output = '\n'.join(output) + f"\n❌ ERROR: No .expfd files found in {expfd_path}"
            log_command_output("BULK DATATURN", "Run DataTurn for EXPFD files", error_output, False)
            return error_output, False
        
        output.append(f"Found {len(expfd_files)} .expfd file(s)")
        output.append("")
        
        success_count = 0
        error_count = 0
        
        # Process each .expfd file
        for expfd_file in expfd_files:
            expfd_name = os.path.splitext(os.path.basename(expfd_file))[0]
            
            output.append(f"\n{'='*60}")
            output.append(f"Processing: {expfd_name}")
            output.append(f"{'='*60}")
            
            try:
                # Prepare import command
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
                
                output.append("Step 1: Importing data...")
                output.append(f"  📝 Import Command: {' '.join(import_cmd)}")
                
                # Run import
                result = subprocess.run(import_cmd, capture_output=True, text=True)
                
                # Display import output
                if result.stdout:
                    output.append(f"  📤 Import Output:")
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            output.append(f"     {line}")
                
                if result.stderr:
                    output.append(f"  ⚠️  Import Errors/Warnings:")
                    for line in result.stderr.strip().split('\n'):
                        if line.strip():
                            output.append(f"     {line}")
                
                if result.returncode == 0:
                    output.append("  ✅ Import successful")
                else:
                    output.append(f"  ⚠️  Import failed with exit code: {result.returncode}")
                
                output.append("")
                
                # Prepare generate command
                generate_cmd = [
                    dataturn_exe,
                    '--generate',
                    '--repository-name', repo_name,
                    '--generation-target', 'DowitcherFileFormat',
                    '--generation-output-directory', output_dir,
                    '--configuration-file', config_file
                ]
                
                output.append("Step 2: Generating format...")
                output.append(f"  📝 Generate Command: {' '.join(generate_cmd)}")
                
                # Run generate
                result = subprocess.run(generate_cmd, capture_output=True, text=True)
                
                # Display generate output
                if result.stdout:
                    output.append(f"  📤 Generate Output:")
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            output.append(f"     {line}")
                
                if result.stderr:
                    output.append(f"  ⚠️  Generate Errors/Warnings:")
                    for line in result.stderr.strip().split('\n'):
                        if line.strip():
                            output.append(f"     {line}")
                
                if result.returncode == 0:
                    output.append("  ✅ Generation successful")
                    success_count += 1
                else:
                    output.append(f"  ❌ Generation failed with exit code: {result.returncode}")
                    error_count += 1
                
                output.append("")
                
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
                
            except subprocess.TimeoutExpired:
                output.append(f"  ❌ TIMEOUT processing {expfd_name}")
                error_count += 1
            except Exception as e:
                output.append(f"  ❌ ERROR processing {expfd_name}: {str(e)}")
                error_count += 1
        
        output.append("")
        output.append("="*60)
        output.append("BULK DATATURN OPERATION COMPLETED")
        output.append("="*60)
        output.append(f"Total files: {len(expfd_files)}")
        output.append(f"✅ Successful: {success_count}")
        output.append(f"❌ Failed: {error_count}")
        output.append(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        
        result_output = '\n'.join(output)
        success = error_count == 0 and success_count > 0
        log_command_output("BULK DATATURN", f"Process {len(expfd_files)} EXPFD file(s)", result_output, success)
        return result_output, True
        
    except Exception as e:
        error_output = f'❌ Error running Bulk DataTurn: {e}\n{traceback.format_exc()}'
        log_command_output("BULK DATATURN", "Run DataTurn in bulk", error_output, False)
        return error_output, False

def run_bulk_conversion(app_name, base_path, config):
    """Run the Bulk Conversion script functionality"""
    logger.info(f"Bulk Conversion started - App: {app_name}, Base: {base_path}")
    try:
        from datetime import datetime
        
        output = []
        output.append("="*60)
        output.append("BULK CONVERSION OPERATION STARTED")
        output.append("="*60)
        output.append(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        output.append(f"Application Name: {app_name}")
        output.append(f"Base Path: {base_path}")
        output.append("")
        
        # Generate paths dynamically based on app_name and base_path
        format_dir = os.path.join(base_path, app_name, 'FF_FILES',)
        input_dir = os.path.join(base_path, app_name, 'input')
        output_dir = os.path.join(base_path, app_name, 'output')
        source_dir = os.path.join(base_path, app_name, 'datamatch', 'source')
        target_dir = os.path.join(base_path, app_name, 'datamatch', 'target')
        
        # Get dowitcher path from config
        dowitcher_exe = config.get('BULK_DOWITCHER_PATH', 'C:/File_conversion/dowitcher.exe')
        
        output.append(f"Format Directory: {format_dir}")
        output.append(f"Input Directory: {input_dir}")
        output.append(f"Output Directory: {output_dir}")
        output.append(f"Dowitcher Exe: {dowitcher_exe}")
        output.append(f"Source Directory: {source_dir}")
        output.append(f"Target Directory: {target_dir}")
        output.append("")
        
        # Validate paths
        if not os.path.exists(format_dir):
            return '\n'.join(output) + f"\n❌ ERROR: Format directory not found: {format_dir}", False
        
        if not os.path.exists(input_dir):
            return '\n'.join(output) + f"\n❌ ERROR: Input directory not found: {input_dir}", False
        
        if not os.path.exists(dowitcher_exe):
            return '\n'.join(output) + f"\n❌ ERROR: Dowitcher executable not found: {dowitcher_exe}", False
        
        # Create output directories if they don't exist
        os.makedirs(output_dir, exist_ok=True)
        os.makedirs(source_dir, exist_ok=True)
        os.makedirs(target_dir, exist_ok=True)
        
        # Clear source and target directories
        output.append("Cleaning source and target directories...")
        for directory in [source_dir, target_dir]:
            if os.path.exists(directory):
                for file in os.listdir(directory):
                    file_path = os.path.join(directory, file)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                    except Exception as e:
                        output.append(f"⚠️  Warning: Could not delete {file_path}: {e}")
        output.append("✅ Directories cleaned")
        output.append("")
        
        # Find all .ff files in format directory
        ff_files = [f for f in os.listdir(format_dir) if f.endswith('.ff')]
        
        if not ff_files:
            return '\n'.join(output) + f"\n❌ ERROR: No .ff files found in {format_dir}", False
        
        output.append(f"Found {len(ff_files)} .ff file(s) to process")
        output.append("")
        
        success_count = 0
        error_count = 0
        warning_count = 0
        
        # Process each .ff file
        for ff_file in ff_files:
            base_name = os.path.splitext(ff_file)[0]
            format_file = os.path.join(format_dir, ff_file)
            input_file = os.path.join(input_dir, f"{base_name}.txt")
            output_file = os.path.join(output_dir, f"{base_name}.txt")
            
            output.append(f"Processing: {base_name}")
            
            # Check if input file exists
            if not os.path.exists(input_file):
                output.append(f"  ❌ ERROR: Input file not found: {input_file}")
                error_count += 1
                output.append("")
                continue
            
            # Run dowitcher conversion
            try:
                cmd = [
                    dowitcher_exe,
                    '--convert',
                    '--translation-table=IBM-037:ISO-8859-1',
                    f'--format={format_file}',
                    input_file,
                    output_file
                ]
                
                output.append(f"  📝 Command: {' '.join(cmd)}")
                logger.info(f"Running dowitcher for {base_name}: {' '.join(cmd)}")
                
                result = subprocess.run(cmd, capture_output=True, text=True)
                
                # Display dowitcher output
                has_warnings = False
                if result.stdout:
                    output.append(f"  📤 Dowitcher Output:")
                    for line in result.stdout.strip().split('\n'):
                        if line.strip():
                            output.append(f"     {line}")
                            # Check if line contains actual warning counts (not "no warnings")
                            line_lower = line.lower()
                            if 'warning' in line_lower and 'no warning' not in line_lower:
                                # Check if there's a number before "warning" indicating warning count
                                import re
                                if re.search(r'\d+\s+warning', line_lower):
                                    has_warnings = True
                
                if result.stderr:
                    output.append(f"  ⚠️  Dowitcher Errors/Warnings:")
                    has_warnings = True
                    for line in result.stderr.strip().split('\n'):
                        if line.strip():
                            output.append(f"     {line}")
                
                if result.returncode == 0:
                    if has_warnings:
                        output.append(f"  ✅ SUCCESS (with warnings): Conversion completed for {base_name}.txt")
                        warning_count += 1
                    else:
                        output.append(f"  ✅ SUCCESS: Conversion completed for {base_name}.txt")
                    success_count += 1
                    
                    # Copy files to source and target directories
                    try:
                        shutil.copy(format_file, source_dir)
                        shutil.copy(format_file, output_dir)
                        shutil.copy(input_file, source_dir)
                        shutil.copy(output_file, target_dir)
                        shutil.copy(format_file, target_dir)
                        output.append(f"  📋 Files copied to datamatch directories")
                    except Exception as e:
                        output.append(f"  ⚠️  Warning: Error copying files: {e}")
                else:
                    output.append(f"  ❌ ERROR: Conversion failed for {base_name}.txt (Exit code: {result.returncode})")
                    error_count += 1
                    
            except subprocess.TimeoutExpired:
                output.append(f"  ❌ ERROR: Conversion timed out for {base_name}.txt")
                error_count += 1
            except Exception as e:
                output.append(f"  ❌ ERROR: {str(e)}")
                error_count += 1
            
            output.append("")
        
        # Summary
        output.append("="*60)
        output.append("BULK CONVERSION OPERATION COMPLETED")
        output.append("="*60)
        output.append(f"Total files processed: {len(ff_files)}")
        output.append(f"✅ Successful conversions: {success_count}")
        if warning_count > 0:
            output.append(f"⚠️  Files with warnings: {warning_count}")
        output.append(f"❌ Failed conversions: {error_count}")
        output.append(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        
        result_output = '\n'.join(output)
        success = error_count == 0
        
        # Log the complete bulk conversion output
        log_command_output(
            "BULK CONVERSION",
            f"Process all .ff files in {app_name}",
            result_output,
            success
        )
        
        return result_output, True
        
    except Exception as e:
        error_output = f"❌ Error in run_bulk_conversion: {str(e)}\n{traceback.format_exc()}"
        log_command_output("BULK CONVERSION", f"Process {app_name} files", error_output, False)
        return error_output, False


def run_create_folder(folder_name, base_path):
    """Create folder structure for a new project"""
    try:
        output = []
        output.append("="*60)
        output.append("CREATE FOLDER STRUCTURE OPERATION STARTED")
        output.append("="*60)
        output.append(f"Folder Name: {folder_name}")
        output.append(f"Base Path: {base_path}")
        output.append("")
        
        # Create the full path
        main_folder = os.path.join(base_path, folder_name)
        
        # Define all subdirectories
        subdirs = [
            os.path.join(main_folder, 'datamatch', 'source'),
            os.path.join(main_folder, 'datamatch', 'target'),
            os.path.join(main_folder, 'input'),
            os.path.join(main_folder, 'expfd'),
            os.path.join(main_folder, 'output'),
            os.path.join(main_folder, 'FF_FILES', 'datamig', 'file-format'),
            os.path.join(main_folder, 'copybook')
        ]
        
        # Create all directories
        created_count = 0
        for subdir in subdirs:
            try:
                os.makedirs(subdir, exist_ok=True)
                output.append(f"✅ Created: {subdir}")
                created_count += 1
            except Exception as e:
                output.append(f"❌ Failed to create {subdir}: {e}")
        
        output.append("")
        output.append("="*60)
        output.append("CREATE FOLDER STRUCTURE OPERATION COMPLETED")
        output.append("="*60)
        output.append(f"Total folders created: {created_count}/{len(subdirs)}")
        output.append(f"Main folder location: {main_folder}")
        output.append("")
        
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
    """Open multiple folders in Windows Explorer"""
    try:
        output = []
        output.append("="*60)
        output.append("OPEN FOLDERS OPERATION STARTED")
        output.append("="*60)
        output.append(f"Folder Name: {folder_name}")
        output.append(f"Base Path: {base_path}")
        output.append("")
        
        # Define all folder paths to open
        folders_to_open = [
            os.path.join(base_path, folder_name, 'datamatch', 'source'),
            os.path.join(base_path, folder_name, 'datamatch', 'target'),
            os.path.join(base_path, folder_name, 'input'),
            os.path.join(base_path, folder_name, 'expfd'),
            os.path.join(base_path, folder_name, 'output'),
            os.path.join(base_path, folder_name, 'FF_FILES', 'datamig', 'file-format'),
            os.path.join(base_path, folder_name, 'copybook')
        ]
        
        opened_count = 0
        for folder_path in folders_to_open:
            try:
                if os.path.exists(folder_path):
                    # Open folder in Windows Explorer
                    subprocess.Popen(['explorer', os.path.abspath(folder_path)])
                    output.append(f"✅ Opened: {folder_path}")
                    opened_count += 1
                else:
                    output.append(f"⚠️  Folder does not exist: {folder_path}")
            except Exception as e:
                output.append(f"❌ Failed to open {folder_path}: {e}")
        
        output.append("")
        output.append("="*60)
        output.append("OPEN FOLDERS OPERATION COMPLETED")
        output.append("="*60)
        output.append(f"Total folders opened: {opened_count}/{len(folders_to_open)}")
        output.append("")
        
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


def run_copy_s3(config):
    """Upload application data to AWS S3 using AWS CLI directly"""
    try:
        output = []
        output.append("="*60)
        output.append("AWS S3 UPLOAD OPERATION STARTED")
        output.append("="*60)
        output.append("")
        
        application_name = config.get('application_name', '').strip()
        
        if not application_name:
            error_output = '❌ Error: Application name is required.'
            log_command_output("COPY S3", "Copy files to AWS S3", error_output, False)
            return error_output, False
        
        output.append(f"Application Name: {application_name}")
        output.append("")
        
        # Get configuration
        s3_bucket = config.get('S3_BUCKET', 'sandboxdee01s3att01')
        s3_path_prefix = config.get('S3_PATH_PREFIX', 'file_Conversion')
        local_base_path = config.get('LOCAL_DATA_PATH', 'D:/File_conversion/File_conversion/Application_details')
        
        # Construct paths
        local_path = os.path.join(local_base_path, application_name, 'Converted_data')
        local_path = os.path.normpath(local_path)
        s3_path = f"s3://{s3_bucket}/{s3_path_prefix}/{application_name}/"
        
        output.append(f"S3 Bucket: {s3_bucket}")
        output.append(f"S3 Path Prefix: {s3_path_prefix}")
        output.append(f"Local Base Path: {local_base_path}")
        output.append("")
        output.append(f"Uploading files from:")
        output.append(f"  Local: {local_path}")
        output.append(f"  To S3: {s3_path}")
        output.append("")
        
        # Check if local path exists
        if not os.path.exists(local_path):
            error_output = '\n'.join(output) + f"\n❌ Error: Local path does not exist: {local_path}"
            log_command_output("COPY S3", f"Copy files from {local_path} to {s3_path}", error_output, False)
            return error_output, False
        
        # Count files to be copied
        file_count = 0
        for root, dirs, files in os.walk(local_path):
            file_count += len(files)
        
        output.append(f"Total files to copy: {file_count}")
        output.append("")
        
        if file_count == 0:
            warning_output = '\n'.join(output) + "\n⚠️  No files found to upload."
            log_command_output("COPY S3", f"Copy files from {local_path} to {s3_path}", warning_output, False)
            return warning_output, False
        
        output.append("Executing AWS CLI command...")
        output.append("")
        
        # Execute AWS S3 cp command directly
        # Command: aws s3 cp <local_path> <s3_path> --recursive
        cmd = [
            'aws',
            's3',
            'cp',
            local_path,
            s3_path,
            '--recursive'
        ]
        
        command_str = ' '.join(cmd)
        output.append("Command: " + command_str)
        output.append("")
        
        success = False
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True
            )
            
            output.append("AWS CLI Output:")
            output.append("-" * 60)
            if result.stdout:
                output.append(result.stdout)
            if result.stderr:
                output.append("Errors/Warnings:")
                output.append(result.stderr)
            output.append("-" * 60)
            
            if result.returncode == 0:
                output.append("")
                output.append(f"✅ FILES UPLOADED SUCCESSFULLY!")
                output.append(f"   Total files copied: {file_count}")
                success = True
            else:
                output.append("")
                output.append(f"❌ Upload failed with return code: {result.returncode}")
                output.append("   Please check the paths and AWS credentials.")
                success = False
            
        except subprocess.TimeoutExpired:
            output.append("❌ Error: AWS CLI command timed out (5 minutes)")
            success = False
        except FileNotFoundError:
            output.append("❌ Error: AWS CLI not found")
            output.append("   Please install AWS CLI: https://aws.amazon.com/cli/")
            success = False
        except Exception as e:
            output.append(f"❌ Error executing AWS CLI: {str(e)}")
            success = False
        
        output.append("")
        output.append("="*60)
        output.append("AWS S3 UPLOAD OPERATION COMPLETED")
        output.append("="*60)
        output.append("")
        
        result_output = '\n'.join(output)
        
        # Log the complete command output
        log_command_output(
            "COPY S3",
            command_str if 'command_str' in locals() else f"Copy files from {local_path} to {s3_path}",
            result_output,
            success
        )
        
        return result_output, True
        
    except Exception as e:
        error_output = f"❌ Error in run_copy_s3: {str(e)}\n{traceback.format_exc()}"
        log_command_output("COPY S3", "Copy files to AWS S3", error_output, False)
        return error_output, False


def run_ff_mapping(config):
    """Map and organize files based on CSV configuration - Pure Python implementation"""
    import csv
    
    try:
        output = []
        output.append("="*60)
        output.append("FF FILE MAPPING OPERATION STARTED")
        output.append("="*60)
        output.append("")
        
        # Get configuration
        source_dir = config.get('FF_MAPPING_SOURCE', '').strip()
        dest_dir = config.get('FF_MAPPING_DEST', '').strip()
        csv_file = config.get('FF_MAPPING_CSV', '').strip()
        
        if not all([source_dir, dest_dir, csv_file]):
            error_output = 'Error: Source directory, destination directory, and CSV file are all required.'
            log_command_output("FF MAPPING", "Generate FF mapping files", error_output, False)
            return error_output, False
        
        output.append(f"Source Directory: {source_dir}")
        output.append(f"Destination Directory: {dest_dir}")
        output.append(f"CSV Mapping File: {csv_file}")
        output.append("")
        
        # Validate paths
        if not os.path.exists(csv_file):
            output.append(f"❌ Error: CSV file not found: {csv_file}")
            output.append("")
            output.append("="*60)
            error_output = '\n'.join(output)
            log_command_output("FF MAPPING", "Generate FF mapping files", error_output, False)
            return error_output, False
        
        if not os.path.exists(source_dir):
            output.append(f"❌ Error: Source directory not found: {source_dir}")
            output.append("")
            output.append("="*60)
            error_output = '\n'.join(output)
            log_command_output("FF MAPPING", "Generate FF mapping files", error_output, False)
            return error_output, False
        
        # Create destination directory if it doesn't exist
        if not os.path.exists(dest_dir):
            os.makedirs(dest_dir)
            output.append(f"✅ Created destination directory: {dest_dir}")
            output.append("")
        
        output.append("Processing CSV file...")
        output.append("")
        
        # Initialize counters
        total_files = 0
        success_count = 0
        error_count = 0
        
        # Read and process CSV file
        try:
            with open(csv_file, 'r', encoding='utf-8') as f:
                csv_reader = csv.reader(f)
                next(csv_reader)  # Skip header row
                
                for row in csv_reader:
                    if len(row) < 3:
                        continue
                    
                    folder_name = row[0].strip()
                    file_name = row[1].strip()
                    dest_file_name = row[2].strip()
                    
                    # Skip empty lines
                    if not folder_name or not file_name or not dest_file_name:
                        continue
                    
                    total_files += 1
                    
                    # Create destination folders if they don't exist
                    ff_folder = os.path.join(dest_dir, folder_name, '.ff')
                    converted_folder = os.path.join(dest_dir, folder_name, 'Converted Files')
                    os.makedirs(ff_folder, exist_ok=True)
                    os.makedirs(converted_folder, exist_ok=True)
                    
                    # Determine source and destination based on file extension
                    source_file = os.path.join(source_dir, file_name)
                    
                    if file_name.endswith('.ff'):
                        # Copy .ff files to .ff folder
                        dest_file = os.path.join(ff_folder, dest_file_name)
                        
                        if os.path.exists(source_file):
                            try:
                                shutil.copy2(source_file, dest_file)
                                output.append(f"✅ Copied .ff file: {file_name} → {folder_name}/.ff/{dest_file_name}")
                                success_count += 1
                            except Exception as e:
                                output.append(f"❌ Failed to copy .ff file: {file_name} - {str(e)}")
                                error_count += 1
                        else:
                            output.append(f"❌ Source .ff file not found: {file_name}")
                            error_count += 1
                    
                    elif file_name.endswith('.txt'):
                        # Copy .txt files to Converted Files folder
                        dest_file = os.path.join(converted_folder, dest_file_name)
                        
                        if os.path.exists(source_file):
                            try:
                                shutil.copy2(source_file, dest_file)
                                output.append(f"✅ Copied .txt file: {file_name} → {folder_name}/Converted Files/{dest_file_name}")
                                success_count += 1
                            except Exception as e:
                                output.append(f"❌ Failed to copy .txt file: {file_name} - {str(e)}")
                                error_count += 1
                        else:
                            output.append(f"❌ Source .txt file not found: {file_name}")
                            error_count += 1
                    
                    else:
                        # Skip unsupported file types
                        output.append(f"⚠️  Skipped unsupported file type: {file_name}")
        
        except Exception as e:
            output.append(f"❌ Error reading CSV file: {str(e)}")
            output.append("")
            output.append("="*60)
            return '\n'.join(output)
        
        # Summary
        output.append("")
        output.append("="*60)
        output.append("OPERATION SUMMARY")
        output.append("="*60)
        output.append(f"Total files processed: {total_files}")
        output.append(f"✅ Successful operations: {success_count}")
        
        if error_count > 0:
            output.append(f"❌ Failed operations: {error_count}")
        else:
            output.append(f"Failed operations: 0")
        
        output.append("")
        
        if error_count == 0 and total_files > 0:
            output.append("✅ All files have been mapped successfully!")
        elif total_files == 0:
            output.append("⚠️  No files were processed from the CSV.")
        else:
            output.append(f"⚠️  {error_count} file(s) failed to process.")
        
        output.append("")
        output.append("="*60)
        output.append("FF FILE MAPPING OPERATION COMPLETED")
        output.append("="*60)
        output.append("")
        
        result_output = '\n'.join(output)
        success = error_count == 0 and total_files > 0
        
        # Log the complete command output
        log_command_output(
            "FF MAPPING",
            "Generate FF mapping files",
            result_output,
            success
        )
        
        return result_output, True
        
    except Exception as e:
        error_output = f"❌ Error in run_ff_mapping: {str(e)}\n{traceback.format_exc()}"
        log_command_output("FF MAPPING", "Generate FF mapping files", error_output, False)
        return error_output, False



def run_file_retrieval(file_list_path, source_folder, destination_folder):
    """Run file retrieval operation - search and copy files from source to destination"""
    logger.info(f"File Retrieval started - Source: {source_folder}, Dest: {destination_folder}")
    try:
        from datetime import datetime
        from pathlib import Path
        
        output = []
        output.append("="*60)
        output.append("FILE RETRIEVAL OPERATION STARTED")
        output.append("="*60)
        output.append(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        output.append(f"File List: {file_list_path}")
        output.append(f"Source Folder: {source_folder}")
        output.append(f"Destination Folder: {destination_folder}")
        output.append("")
        
        # Validate paths
        if not os.path.exists(file_list_path):
            return '\n'.join(output) + f"\n❌ ERROR: File list not found: {file_list_path}", False
        
        if not os.path.exists(source_folder):
            return '\n'.join(output) + f"\n❌ ERROR: Source folder not found: {source_folder}", False
        
        # Create destination folder
        os.makedirs(destination_folder, exist_ok=True)
        
        # Read file list
        with open(file_list_path, 'r', encoding='utf-8') as f:
            file_list = [line.strip() for line in f.readlines() if line.strip()]
        
        if not file_list:
            return '\n'.join(output) + f"\n❌ ERROR: File list is empty", False
        
        output.append(f"Found {len(file_list)} file(s) to retrieve")
        output.append("")
        
        # Counters
        found_count = 0
        copied_count = 0
        missing_count = 0
        empty_count = 0
        error_count = 0
        
        empty_files = []
        missing_files = []
        
        # Process each file
        for filename in file_list:
            output.append(f"Processing: {filename}")
            
            # Search recursively in source folder
            found_files = []
            for root, dirs, files in os.walk(source_folder):
                if filename in files:
                    found_files.append(os.path.join(root, filename))
            
            if not found_files:
                output.append(f"  ❌ MISSING: File not found")
                missing_count += 1
                missing_files.append(filename)
                output.append("")
                continue
            
            found_count += 1
            source_path = found_files[0]
            
            if len(found_files) > 1:
                output.append(f"  ⚠️  Multiple copies found, using first: {source_path}")
            
            # Check if file is empty
            try:
                file_size = os.path.getsize(source_path)
                if file_size == 0:
                    output.append(f"  ⚠️  EMPTY: File is empty (0 bytes)")
                    empty_count += 1
                    empty_files.append(filename)
                    output.append("")
                    continue
            except Exception as e:
                output.append(f"  ❌ ERROR: Cannot read file size: {e}")
                error_count += 1
                output.append("")
                continue
            
            # Copy file
            try:
                dest_path = os.path.join(destination_folder, filename)
                shutil.copy2(source_path, dest_path)
                output.append(f"  ✅ SUCCESS: Copied ({file_size:,} bytes)")
                output.append(f"     From: {source_path}")
                output.append(f"     To: {dest_path}")
                copied_count += 1
            except Exception as e:
                output.append(f"  ❌ ERROR: Copy failed: {e}")
                error_count += 1
            
            output.append("")
        
        # Save empty and missing files to log file
        if empty_files or missing_files:
            log_file_path = os.path.join(destination_folder, "empty_and_missing_files.txt")
            try:
                with open(log_file_path, 'w', encoding='utf-8') as f:
                    f.write("EMPTY FILES\n")
                    f.write("="*50 + "\n\n")
                    if empty_files:
                        for fname in empty_files:
                            f.write(f"{fname}\n")
                    else:
                        f.write("No empty files found.\n")
                    
                    f.write("\n\n")
                    f.write("MISSING FILES\n")
                    f.write("="*50 + "\n\n")
                    if missing_files:
                        for fname in missing_files:
                            f.write(f"{fname}\n")
                    else:
                        f.write("No missing files found.\n")
                
                output.append(f"📄 Empty and missing files list saved to: {log_file_path}")
                output.append("")
            except Exception as e:
                output.append(f"⚠️  Warning: Could not save empty/missing files list: {e}")
                output.append("")
        
        # Summary
        output.append("="*60)
        output.append("FILE RETRIEVAL OPERATION COMPLETED")
        output.append("="*60)
        output.append(f"Total files requested: {len(file_list)}")
        output.append(f"✅ Files copied successfully: {copied_count}")
        output.append(f"❌ Missing files: {missing_count}")
        output.append(f"⚠️  Empty files: {empty_count}")
        output.append(f"❌ Error files: {error_count}")
        output.append(f"Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        output.append("")
        
        result_output = '\n'.join(output)
        success = error_count == 0 and copied_count > 0
        
        # Log the complete output
        log_command_output(
            "FILE RETRIEVAL",
            f"Retrieve files from {source_folder}",
            result_output,
            success
        )
        
        return result_output, True
        
    except Exception as e:
        error_output = f"❌ Error in run_file_retrieval: {str(e)}\n{traceback.format_exc()}"
        log_command_output("FILE RETRIEVAL", "File retrieval operation", error_output, False)
        return error_output, False


app = Flask(__name__)

# Template for main screen with all scripts
MAIN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ConvertFlow Studio</title>
    <style>
        :root {
            /* Professional Corporate Color Palette */
            --primary-color: #2563eb;      /* Professional Blue */
            --secondary-color: #1e40af;    /* Dark Blue */
            --accent-color: #3b82f6;       /* Medium Blue */
            
            --bg-primary: #0f172a;         /* Dark Slate */
            --bg-secondary: #1e293b;       /* Slate 800 */
            --bg-card: #1e293b;            /* Slate 800 */
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;     /* Slate 300 */
            --border: #334155;             /* Slate 700 */
            --shadow: rgba(0, 0, 0, 0.3);
            
            /* Standardized Gradients */
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        /* Enable hardware acceleration */
        body, .container, .action-btn {
            -webkit-transform: translateZ(0);
            transform: translateZ(0);
            will-change: auto;
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: var(--bg-primary);
            min-height: 100vh;
            color: var(--text-primary);
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
        }

        .container {
            max-width: 700px;
            width: 100%;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 8px 16px var(--shadow);
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
            background-clip: text;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
        }

        .button-grid {
            display: grid;
            grid-template-columns: repeat(2, 1fr);
            gap: 20px;
            margin-top: 30px;
        }

        @media (max-width: 768px) {
            .button-grid {
                grid-template-columns: 1fr;
            }
        }

        .action-btn {
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
            padding: 20px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
            color: white;
            min-height: 70px;
        }

        .btn-copy {
            background: var(--primary-gradient);
        }

        .btn-dataturn {
            background: var(--primary-gradient);
        }

        .btn-expfd {
            background: var(--primary-gradient);
        }

        .btn-bulk {
            background: var(--primary-gradient);
        }

        .btn-create-folder {
            background: var(--primary-gradient);
        }

        .btn-open-folders {
            background: var(--primary-gradient);
        }

        .btn-copy-s3 {
            background: var(--primary-gradient);
        }

        .btn-ff-mapping {
            background: var(--primary-gradient);
        }

        .btn-config {
            background: var(--primary-gradient);
        }

        .action-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
        }

        .action-btn:active {
            transform: translateY(0);
        }

        .icon {
            font-size: 1.5rem;
        }

        .footer {
            text-align: center;
            margin-top: 40px;
            color: var(--text-secondary);
            font-size: 0.9rem;
            padding-top: 30px;
            border-top: 1px solid var(--border);
        }

        .footer p {
            margin: 5px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🚀 ConvertFlow Studio</h1>
        
        <form method="POST" action="/">
            <div class="button-grid">
                <button type="submit" name="action" value="create_folder" class="action-btn btn-create-folder">
                    <span class="icon">📁</span>
                    <span>Create Folder Structure</span>
                </button>
                
                <button type="submit" name="action" value="open_folders" class="action-btn btn-open-folders">
                    <span class="icon">🗂️</span>
                    <span>Open Project Folders</span>
                </button>
                
                <button type="submit" name="action" value="copy_bulk" class="action-btn btn-copy">
                    <span class="icon">📂</span>
                    <span>Copy Bulk Files</span>
                </button>
                
                <button type="submit" name="action" value="bulk_expfd" class="action-btn btn-expfd">
                    <span class="icon">📚</span>
                    <span>Bulk EXPFD</span>
                </button>
                
                <button type="submit" name="action" value="bulk_dataturn" class="action-btn btn-dataturn">
                    <span class="icon">🔁</span>
                    <span>Bulk DataTurn</span>
                </button>
                
                <button type="submit" name="action" value="bulk_conversion" class="action-btn btn-bulk">
                    <span class="icon">🔄</span>
                    <span>Bulk Conversion</span>
                </button>
                
                <button type="submit" name="action" value="ff_mapping" class="action-btn btn-ff-mapping">
                    <span class="icon">🗂️</span>
                    <span>FF File Mapping</span>
                </button>
                
                <button type="submit" name="action" value="file_retrieval" class="action-btn btn-copy">
                    <span class="icon">🔍</span>
                    <span>File Retrieval</span>
                </button>
                
                <button type="submit" name="action" value="copy_s3" class="action-btn btn-copy-s3">
                    <span class="icon">☁️</span>
                    <span>Copy to AWS S3</span>
                </button>
                
                <button type="submit" name="action" value="scripts_config" class="action-btn btn-config">
                    <span class="icon">⚙️</span>
                    <span>Scripts Configuration</span>
                </button>
                
                <button type="submit" name="action" value="view_logs" class="action-btn btn-config">
                    <span class="icon">📋</span>
                    <span>View Logs</span>
                </button>
                
                <button type="submit" name="action" value="user_guide" class="action-btn btn-config">
                    <span class="icon">📖</span>
                    <span>User Guide</span>
                </button>
            </div>
        </form>

        <div class="footer">
            <p>ConvertFlow Studio</p>
            <p>Powered By Astadia Team</p>
        </div>
    </div>
</body>
</html>
'''

# Template for Copy Bulk page
COPY_BULK_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Copy Bulk Files</title>
    <style>
        :root {
            /* Professional Corporate Color Palette */
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: #334155;
            --shadow: rgba(0, 0, 0, 0.3);
            
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%);
            min-height: 100vh;
            color: var(--text-primary);
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 20px auto;
            background: var(--bg-card);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 20px 40px var(--shadow);
            padding: 40px;
            position: relative;
            overflow: hidden;
            animation: slideIn 0.5s ease-out;
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

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
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
            border-color: #2563eb;
            box-shadow: 0 0 0 3px rgba(245, 87, 108, 0.1);
            transform: translateY(-2px);
        }

        .info-text {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 5px;
            font-style: italic;
            opacity: 0.8;
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }

        button {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-submit {
            background: var(--secondary-gradient);
            color: white;
        }

        .btn-submit:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .btn-home {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }

        .btn-home:hover {
            background: var(--accent-color);
            color: white;
            border-color: var(--accent-color);
            transform: translateY(-3px);
        }

        .output-box {
            margin-top: 30px;
            padding: 0;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            border-left: 4px solid #2563eb;
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

        .output-box pre {
            padding: 20px;
            white-space: pre;
            word-wrap: normal;
            overflow-wrap: normal;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            margin: 0;
            color: var(--text-primary);
            min-width: max-content;
        }

        /* Custom scrollbar styling */
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
            background: rgba(37, 99, 235, 0.8);
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
            clip-path: polygon(100% 0, 100% 100%, 0 100%);
        }

        .resize-handle:hover {
            background: rgba(37, 99, 235, 0.6);
        }

        .success {
            border-left-color: #3b82f6;
        }

        /* Loading spinner styles */
        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 9999;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }

        .loading-overlay.active {
            display: flex;
        }

        .spinner {
            width: 60px;
            height: 60px;
            border: 5px solid rgba(255, 255, 255, 0.1);
            border-top: 5px solid #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .loading-text {
            color: white;
            margin-top: 20px;
            font-size: 1.2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <!-- Loading overlay -->
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
        <div class="loading-text">Processing... Please wait</div>
    </div>

    <div class="container">
        <h1>📂 Copy Bulk Files</h1>
        
        <form method="POST" id="bulkForm" onsubmit="showLoading()">
            <div class="form-group">
                <label for="source_path">Source Directory Path:</label>
                <input type="text" id="source_path" name="source_path" 
                       value="{{ source_path }}" required
                       placeholder="C:/File_conversion/occ/output">
                <div class="info-text">Full path to the directory containing source files</div>
            </div>

            <div class="form-group">
                <label for="dest_path">Destination Directory Path:</label>
                <input type="text" id="dest_path" name="dest_path" 
                       value="{{ dest_path }}" required
                       placeholder="C:/File_conversion/bulk_conversion">
                <div class="info-text">Full path where files will be copied</div>
            </div>

            <div class="form-group">
                <label for="input_file">Input TXT File Path:</label>
                <input type="text" id="input_file" name="input_file" 
                       value="{{ input_file }}" required
                       placeholder="C:/File_conversion/IGD.txt">
                <div class="info-text">TXT file with format: oldfilename,newfilename</div>
            </div>

            <div class="button-group">
                <button type="submit" class="btn-submit">▶️ Run Copy Bulk</button>
                <button type="button" class="btn-home" onclick="window.location.href='/'">🏠 Home</button>
            </div>
        </form>

        {% if output %}
        <div class="output-box {% if success %}success{% endif %}">
            <pre id="outputPre">{{ output }}</pre>
            <div class="resize-handle" title="Drag to resize"></div>
        </div>
        <div style="text-align: center; margin-top: 10px; color: var(--text-secondary); font-size: 0.85rem;">
            💡 <strong>Tip:</strong> Drag the bottom-right corner to resize • Use scroll bars for navigation • Long lines will scroll horizontally
        </div>
        {% endif %}
    </div>

    <script>
        function showLoading() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }

        // Color-code output messages
        function colorizeOutput() {
            const outputPre = document.getElementById('outputPre');
            if (outputPre) {
                let text = outputPre.innerHTML;
                
                // Success patterns - Green (#22c55e) - Only highlight lines with emojis or specific phrases
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bCreated successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                
                // Error patterns - Red (#ef4444) - Only highlight lines with emojis or specific phrases  
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bError:.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bException\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                
                // Warning patterns - Yellow (#eab308)
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWarning:.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                
                // Info patterns - Blue (#3b82f6)
                text = text.replace(/^(.*ℹ️.*)$/gm, '<span style="color: #3b82f6;">$1</span>');
                text = text.replace(/^(.*INFO.*)$/gm, '<span style="color: #3b82f6;">$1</span>');
                
                outputPre.innerHTML = text;
            }
        }

        // Run colorization when page loads
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
</body>
</html>
'''

# Template for Bulk EXPFD page
BULK_EXPFD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bulk EXPFD Creation</title>
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --expfd-gradient: var(--primary-gradient);
            
            --bg-primary: #0f0f23;
            --bg-secondary: #1a1a2e;
            --bg-card: #16213e;
            --text-primary: #ffffff;
            --text-secondary: #b8c5d1;
            --accent: #3b82f6;
            --border: #2d3748;
            --shadow: rgba(0, 0, 0, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%);
            min-height: 100vh;
            color: var(--text-primary);
            padding: 20px;
        }

        .container {
            max-width: 900px;
            margin: 20px auto;
            background: var(--bg-card);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 20px 40px var(--shadow);
            padding: 40px;
            position: relative;
            overflow: hidden;
            animation: slideIn 0.5s ease-out;
        }

        .container::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            background: var(--expfd-gradient);
        }

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        h1 {
            background: var(--expfd-gradient);
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
            font-family: inherit;
        }

        textarea {
            min-height: 120px;
            resize: vertical;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
        }

        input[type="text"]:focus, textarea:focus {
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(250, 112, 154, 0.1);
            transform: translateY(-2px);
        }

        .info-text {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 5px;
            font-style: italic;
            opacity: 0.8;
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }

        button {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-submit {
            background: var(--expfd-gradient);
            color: white;
        }

        .btn-submit:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .btn-home {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }

        .btn-home:hover {
            background: var(--accent-color);
            color: white;
            border-color: var(--accent-color);
            transform: translateY(-3px);
        }

        .output-box {
            margin-top: 30px;
            padding: 0;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            border-left: 4px solid #2563eb;
            min-height: 450px;
            max-height: none;
            resize: both;
            overflow: auto;
            position: relative;
        }

        .output-box pre {
            padding: 20px;
            white-space: pre;
            word-wrap: normal;
            overflow-wrap: normal;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            margin: 0;
            color: var(--text-primary);
            min-width: max-content;
        }

        /* Custom scrollbar styling */
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
            background: rgba(37, 99, 235, 0.8);
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
            clip-path: polygon(100% 0, 100% 100%, 0 100%);
        }

        .resize-handle:hover {
            background: rgba(37, 99, 235, 0.6);
        }

        .success {
            border-left-color: #3b82f6;
        }

        /* Loading overlay */
        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 15, 35, 0.9);
            justify-content: center;
            align-items: center;
            z-index: 9999;
            flex-direction: column;
            gap: 20px;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(37, 99, 235, 0.3);
            border-top-color: #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .loading-text {
            color: #3b82f6;
            font-size: 1.2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
        <div class="loading-text">Processing... Please wait</div>
    </div>

    <div class="container">
        <h1>📝 Create EXPFD</h1>
        
        <form method="POST" id="expfdForm" onsubmit="showLoading()">
            <div class="form-group">
                <label for="copybook_names">Copybook File Names:</label>
                <textarea id="copybook_names" name="copybook_names" required
                       placeholder="Enter copybook names (comma-separated for multiple files)&#10;Example: file1.cpy, file2.cpy">{{ copybook_names }}</textarea>
                <div class="info-text">Enter copybook file names separated by commas. Files should exist in the copybook directory.</div>
            </div>

            <div class="form-group">
                <label for="copybook_path">Copybook Directory Path:</label>
                <input type="text" id="copybook_path" name="copybook_path" 
                       value="{{ copybook_path }}" required
                       placeholder="C:/File_conversion/copybooks">
                <div class="info-text">Directory containing the copybook files</div>
            </div>

            <div class="form-group">
                <label for="expfd_path">EXPFD Output Directory Path:</label>
                <input type="text" id="expfd_path" name="expfd_path" 
                       value="{{ expfd_path }}" required
                       placeholder="C:/File_conversion/occ/expfd">
                <div class="info-text">Directory where the EXPFD file will be created</div>
            </div>

            <div class="button-group">
                <button type="submit" class="btn-submit">▶️ Create EXPFD</button>
                <button type="button" class="btn-home" onclick="window.location.href='/'">🏠 Home</button>
            </div>
        </form>

        {% if output %}
        <div class="output-box {% if success %}success{% endif %}">
            <pre id="outputPre">{{ output }}</pre>
            <div class="resize-handle" title="Drag to resize"></div>
        </div>
        <div style="margin-top: 10px; padding: 8px; background: rgba(37, 99, 235, 0.1); border-radius: 6px; font-size: 0.85rem; color: var(--text-secondary);">
            💡 Tip: Drag the corner handle to resize the output box
        </div>
        {% endif %}
    </div>

    <script>
        function showLoading() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }
        function colorizeOutput() {
            const outputPre = document.getElementById('outputPre');
            if (outputPre) {
                let text = outputPre.innerHTML;
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bCompleted\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*Error:.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bfailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*ℹ️.*)$/gm, '<span style="color: #3b82f6;">$1</span>');
                outputPre.innerHTML = text;
            }
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
</body>
</html>
'''

# Template for Bulk EXPFD page
BULK_EXPFD_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bulk EXPFD Creation</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: #334155;
            --shadow: rgba(0, 0, 0, 0.3);
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --info-gradient: var(--primary-gradient);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: var(--bg-primary);
            min-height: 100vh;
            color: var(--text-primary);
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
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
            background: var(--info-gradient);
        }
        h1 {
            background: var(--info-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
        }
        .info-box {
            background: var(--bg-secondary);
            border-left: 4px solid var(--accent-color);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .button-group {
            display: flex;
            gap: 15px;
            margin: 30px 0;
        }
        button {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn-submit {
            background: var(--info-gradient);
            color: white;
        }
        .btn-submit:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }
        .btn-home {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }
        .btn-home:hover {
            background: var(--accent-color);
            color: white;
        }
        .output-box {
            margin-top: 30px;
            padding: 0;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            border-left: 4px solid var(--accent-color);
            min-height: 450px;
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
            min-width: max-content;
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
            background: rgba(59, 130, 246, 0.8);
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
            clip-path: polygon(100% 0, 100% 100%, 0 100%);
        }
        .resize-handle:hover {
            background: rgba(59, 130, 246, 0.6);
        }
        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 9999;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        .loading-overlay.active { display: flex; }
        .spinner {
            width: 60px;
            height: 60px;
            border: 5px solid rgba(255, 255, 255, 0.1);
            border-top: 5px solid var(--accent-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
        <div style="color: white; margin-top: 20px; font-size: 1.2rem; font-weight: 600;">Processing all copybooks... Please wait</div>
    </div>

    <div class="container">
        <h1>📚 Bulk EXPFD Creation</h1>
        
        <div class="info-box">
            <h3>ℹ️ What does this do?</h3>
            <p>This operation will process all copybook files in the copybook directory and create .expfd files for each one.</p>
            <p>Paths are read from path.txt configuration file.</p>
        </div>

        <form method="POST" onsubmit="document.getElementById('loadingOverlay').style.display='flex'">
            <div class="button-group">
                <button type="submit" class="btn-submit">▶️ Run Bulk EXPFD Creation</button>
                <button type="button" class="btn-home" onclick="window.location.href='/'">🏠 Home</button>
            </div>
        </form>

        {% if output %}
        <div class="output-box">
            <pre id="outputPre">{{ output }}</pre>
            <div class="resize-handle" title="Drag to resize"></div>
        </div>
        <div style="margin-top: 10px; padding: 8px; background: rgba(59, 130, 246, 0.1); border-radius: 6px; font-size: 0.85rem; color: var(--text-secondary);">
            💡 Tip: Drag the corner handle to resize the output box
        </div>
        {% endif %}
    </div>
    <script>
        function colorizeOutput() {
            const outputPre = document.getElementById('outputPre');
            if (outputPre) {
                let text = outputPre.innerHTML;
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bfailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                outputPre.innerHTML = text;
            }
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
</body>
</html>
'''

# Template for Bulk DataTurn page
BULK_DATATURN_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bulk DataTurn</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: #334155;
            --shadow: rgba(0, 0, 0, 0.3);
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --info-gradient: var(--primary-gradient);
        }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', 'Segoe UI', sans-serif;
            background: var(--bg-primary);
            min-height: 100vh;
            color: var(--text-primary);
            padding: 20px;
        }
        .container {
            max-width: 1000px;
            margin: 0 auto;
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
            background: var(--info-gradient);
        }
        h1 {
            background: var(--info-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
        }
        .info-box {
            background: var(--bg-secondary);
            border-left: 4px solid var(--accent-color);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }
        .button-group {
            display: flex;
            gap: 15px;
            margin: 30px 0;
        }
        button {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn-submit {
            background: var(--info-gradient);
            color: white;
        }
        .btn-submit:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }
        .btn-home {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }
        .btn-home:hover {
            background: var(--accent-color);
            color: white;
        }
        .output-box {
            margin-top: 30px;
            padding: 0;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            border-left: 4px solid var(--accent-color);
            min-height: 450px;
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
            min-width: max-content;
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
            background: rgba(59, 130, 246, 0.8);
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
            clip-path: polygon(100% 0, 100% 100%, 0 100%);
        }
        .resize-handle:hover {
            background: rgba(59, 130, 246, 0.6);
        }
        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.8);
            z-index: 9999;
            justify-content: center;
            align-items: center;
            flex-direction: column;
        }
        .loading-overlay.active { display: flex; }
        .spinner {
            width: 60px;
            height: 60px;
            border: 5px solid rgba(255, 255, 255, 0.1);
            border-top: 5px solid var(--accent-color);
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
        <div style="color: white; margin-top: 20px; font-size: 1.2rem; font-weight: 600;">Processing all EXPFD files... Please wait</div>
    </div>

    <div class="container">
        <h1>🔁 Bulk DataTurn</h1>
        
        <div class="info-box">
            <h3>ℹ️ What does this do?</h3>
            <p>This operation will run DataTurn conversion for all .expfd files in the expfd directory.</p>
            <p>Each file will be imported and then generated as DowitcherFileFormat.</p>
            <p>Paths and configuration are read from path.txt.</p>
        </div>

        <form method="POST" onsubmit="document.getElementById('loadingOverlay').style.display='flex'">
            <div class="button-group">
                <button type="submit" class="btn-submit">▶️ Run Bulk DataTurn</button>
                <button type="button" class="btn-home" onclick="window.location.href='/'">🏠 Home</button>
            </div>
        </form>

        {% if output %}
        <div class="output-box">
            <pre id="outputPre">{{ output }}</pre>
            <div class="resize-handle" title="Drag to resize"></div>
        </div>
        <div style="margin-top: 10px; padding: 8px; background: rgba(59, 130, 246, 0.1); border-radius: 6px; font-size: 0.85rem; color: var(--text-secondary);">
            💡 Tip: Drag the corner handle to resize the output box
        </div>
        {% endif %}
    </div>
    <script>
        function colorizeOutput() {
            const outputPre = document.getElementById('outputPre');
            if (outputPre) {
                let text = outputPre.innerHTML;
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bfailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                outputPre.innerHTML = text;
            }
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
</body>
</html>
'''

# Template for Bulk Conversion page
BULK_CONVERSION_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Bulk Conversion</title>
    <style>
        :root {
            /* Professional Corporate Color Palette */
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: #334155;
            --shadow: rgba(0, 0, 0, 0.3);
            
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
            --info-gradient: var(--primary-gradient);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(37, 99, 235, 0.2) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(59, 130, 246, 0.2) 0%, transparent 50%);
            min-height: 100vh;
            color: var(--text-primary);
            padding: 20px;
        }

        .container {
            max-width: 1000px;
            margin: 0 auto;
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
            background: var(--info-gradient);
        }

        h1 {
            background: var(--info-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
        }

        .info-box {
            background: var(--bg-secondary);
            border-left: 4px solid var(--accent-color);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }

        .info-box h3 {
            color: var(--accent-color);
            margin-bottom: 10px;
        }

        .info-box p {
            color: var(--text-secondary);
            margin-bottom: 10px;
        }

        form {
            margin-bottom: 30px;
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 20px;
        }

        .btn {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
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
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }

        .output-box {
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 0;
            margin-top: 30px;
            min-height: 450px;
            max-height: none;
            resize: both;
            overflow: auto;
            position: relative;
        }

        .output-box.success {
            border-color: var(--accent-color);
        }

        .output-box pre {
            padding: 20px;
            color: var(--text-primary);
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            white-space: pre;
            word-wrap: normal;
            overflow-wrap: normal;
            margin: 0;
            min-width: max-content;
        }

        /* Custom scrollbar styling */
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
            background: rgba(168, 237, 234, 0.8);
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
            clip-path: polygon(100% 0, 100% 100%, 0 100%);
        }

        .resize-handle:hover {
            background: rgba(168, 237, 234, 0.6);
        }

        .loading {
            text-align: center;
            padding: 20px;
            color: var(--accent-color);
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        /* Loading overlay */
        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 15, 35, 0.9);
            justify-content: center;
            align-items: center;
            z-index: 9999;
            flex-direction: column;
            gap: 20px;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(37, 99, 235, 0.3);
            border-top-color: #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .loading-text {
            color: #3b82f6;
            font-size: 1.2rem;
            font-weight: 600;
        }
    </style>
    <script>
        function runConversion() {
            document.getElementById('loadingOverlay').style.display = 'flex';
            const btn = document.getElementById('runBtn');
            btn.disabled = true;
            btn.textContent = 'Processing...';
            document.getElementById('conversionForm').submit();
        }
    </script>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
        <div class="loading-text">Processing... Please wait</div>
    </div>

    <div class="container">
        <h1>🔁 Bulk Conversion</h1>
        
        <div class="info-box">
            <h3>ℹ️ What does this do?</h3>
            <p>This tool processes all .ff format files in the format directory and converts the corresponding input files using Dowitcher. It will:</p>
            <ul style="color: var(--text-secondary); margin-left: 20px;">
                <li>Find all .ff files in the format directory</li>
                <li>For each .ff file, convert the matching .txt input file</li>
                <li>Save converted outputs and copy files to datamatch directories</li>
                <li>Generate detailed logs of the conversion process</li>
            </ul>
        </div>
        
        <form method="POST" id="conversionForm">
            <div class="form-group">
                <label for="app_name">Application Name</label>
                <input type="text" id="app_name" name="app_name" value="{{ app_name }}" 
                       placeholder="e.g., occ, rbs, mc" required 
                       style="width: 100%; padding: 12px; background: var(--bg-secondary); border: 1px solid var(--border); border-radius: 8px; color: var(--text-primary); font-size: 1rem;">
                <small style="color: var(--text-secondary); display: block; margin-top: 5px;">
                    Enter the application name (e.g., occ, rbs, mc). The system will automatically generate all required paths.
                </small>
            </div>
            
            <div class="button-group">
                <a href="/" class="btn btn-secondary">← Back to Main Menu</a>
                <button type="button" onclick="runConversion()" id="runBtn" class="btn btn-primary">▶️ Start Bulk Conversion</button>
            </div>
        </form>

        {% if output %}
        <div class="output-box {% if success %}success{% endif %}">
            <pre id="outputPre">{{ output }}</pre>
            <div class="resize-handle" title="Drag to resize"></div>
        </div>
        <div style="margin-top: 10px; padding: 8px; background: rgba(168, 237, 234, 0.1); border-radius: 6px; font-size: 0.85rem; color: var(--text-secondary);">
            💡 Tip: Drag the corner handle to resize the output box
        </div>
        {% endif %}
    </div>
    <script>
        function colorizeOutput() {
            const outputPre = document.getElementById('outputPre');
            if (outputPre) {
                let text = outputPre.innerHTML;
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bfailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                outputPre.innerHTML = text;
            }
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
</body>
</html>
'''

# Template for Scripts Config page
# Template for Create Folder page
CREATE_FOLDER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Create Folder Structure</title>
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            --bg-primary: #0f0f23;
            --bg-secondary: #1a1a2e;
            --bg-card: #16213e;
            --text-primary: #ffffff;
            --text-secondary: #b8c5d1;
            --accent: #3b82f6;
            --border: #2d3748;
            --shadow: rgba(0, 0, 0, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%);
            min-height: 100vh;
            color: var(--text-primary);
            padding: 20px;
        }

        .container {
            max-width: 900px;
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

        .info-box {
            background: var(--bg-secondary);
            border-left: 4px solid var(--accent-color);
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }

        .info-box h3 {
            color: var(--accent-color);
            margin-bottom: 10px;
        }

        .info-box p {
            color: var(--text-secondary);
            margin-bottom: 10px;
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
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
            transform: translateY(-2px);
        }

        .info-text {
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
            transition: all 0.3s ease;
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
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }

        .output-box {
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 0;
            margin-top: 30px;
            min-height: 450px;
            max-height: none;
            resize: both;
            overflow: auto;
            position: relative;
        }

        .output-box.success {
            border-color: var(--accent-color);
        }

        .output-box pre {
            padding: 20px;
            color: var(--text-primary);
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            white-space: pre;
            word-wrap: normal;
            overflow-wrap: normal;
            margin: 0;
            min-width: max-content;
        }

        /* Custom scrollbar styling */
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
            background: rgba(102, 126, 234, 0.8);
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
            clip-path: polygon(100% 0, 100% 100%, 0 100%);
        }

        .resize-handle:hover {
            background: rgba(102, 126, 234, 0.6);
        }

        /* Loading overlay */
        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 15, 35, 0.9);
            justify-content: center;
            align-items: center;
            z-index: 9999;
            flex-direction: column;
            gap: 20px;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(37, 99, 235, 0.3);
            border-top-color: #3b82f6;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .loading-text {
            color: #3b82f6;
            font-size: 1.2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
        <div class="loading-text">Processing... Please wait</div>
    </div>

    <div class="container">
        <h1>📁 Create Folder Structure</h1>
        
        <div class="info-box">
            <h3>ℹ️ What does this do?</h3>
            <p>This tool creates a complete folder structure for a new project with all necessary subdirectories:</p>
            <ul style="color: var(--text-secondary); margin-left: 20px;">
                <li>datamatch/source and datamatch/target</li>
                <li>input, output, and expfd folders</li>
                <li>FF_FILES/datamig/file-format</li>
                <li>copybook folder</li>
            </ul>
        </div>
        
        <form method="POST" id="createFolderForm" onsubmit="showLoading()">
            <div class="form-group">
                <label for="folder_name">Project Folder Name:</label>
                <input type="text" id="folder_name" name="folder_name" 
                       value="{{ folder_name }}" required
                       placeholder="e.g., myproject, rbs, occ">
                <div class="info-text">Enter the name for your new project folder</div>
            </div>

            <div class="form-group">
                <label for="base_path">Base Directory Path:</label>
                <input type="text" id="base_path" name="base_path" 
                       value="{{ base_path }}" required
                       placeholder="C:/File_conversion">
                <div class="info-text">Base directory where the project folder will be created</div>
            </div>

            <div class="button-group">
                <a href="/" class="btn btn-secondary">← Back to Main Menu</a>
                <button type="submit" class="btn btn-primary">▶️ Create Folders</button>
            </div>
        </form>

        {% if output %}
        <div class="output-box {% if success %}success{% endif %}">
            <pre id="outputPre">{{ output }}</pre>
            <div class="resize-handle" title="Drag to resize"></div>
        </div>
        <div style="margin-top: 10px; padding: 8px; background: rgba(102, 126, 234, 0.1); border-radius: 6px; font-size: 0.85rem; color: var(--text-secondary);">
            💡 Tip: Drag the corner handle to resize the output box
        </div>
        {% endif %}
    </div>

    <script>
        function showLoading() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }
        function colorizeOutput() {
            const outputPre = document.getElementById('outputPre');
            if (outputPre) {
                let text = outputPre.innerHTML;
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bfailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                outputPre.innerHTML = text;
            }
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
</body>
</html>
'''

# Template for Open Folders page
OPEN_FOLDERS_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Open Project Folders</title>
    <style>
        :root {
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #1e40af 0%, #2563eb 100%);
            --open-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --bg-primary: #0f0f23;
            --bg-secondary: #1a1a2e;
            --bg-card: #16213e;
            --text-primary: #ffffff;
            --text-secondary: #b8c5d1;
            --accent: #3b82f6;
            --border: #2d3748;
            --shadow: rgba(0, 0, 0, 0.3);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%);
            min-height: 100vh;
            color: var(--text-primary);
            padding: 20px;
        }

        .container {
            max-width: 900px;
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
            background: var(--open-gradient);
        }

        h1 {
            background: var(--open-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 30px;
        }

        .info-box {
            background: var(--bg-secondary);
            border-left: 4px solid #3b82f6;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 30px;
        }

        .info-box h3 {
            color: #3b82f6;
            margin-bottom: 10px;
        }

        .info-box p {
            color: var(--text-secondary);
            margin-bottom: 10px;
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
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(255, 154, 158, 0.1);
            transform: translateY(-2px);
        }

        .info-text {
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
            transition: all 0.3s ease;
        }

        .btn-primary {
            background: var(--open-gradient);
            color: white;
        }

        .btn-secondary {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 2px solid var(--border);
        }

        .btn:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(0, 0, 0, 0.2);
        }

        .output-box {
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 0;
            margin-top: 30px;
            min-height: 450px;
            max-height: none;
            resize: both;
            overflow: auto;
            position: relative;
        }

        .output-box.success {
            border-color: #3b82f6;
        }

        .output-box pre {
            padding: 20px;
            color: var(--text-primary);
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            white-space: pre;
            word-wrap: normal;
            overflow-wrap: normal;
            margin: 0;
            min-width: max-content;
        }

        /* Custom scrollbar styling */
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
            background: rgba(37, 99, 235, 0.8);
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
            clip-path: polygon(100% 0, 100% 100%, 0 100%);
        }

        .resize-handle:hover {
            background: rgba(37, 99, 235, 0.6);
        }

        /* Loading overlay */
        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 15, 35, 0.9);
            justify-content: center;
            align-items: center;
            z-index: 9999;
            flex-direction: column;
            gap: 20px;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(37, 99, 235, 0.3);
            border-top-color: #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .loading-text {
            color: #3b82f6;
            font-size: 1.2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
        <div class="loading-text">Processing... Please wait</div>
    </div>

    <div class="container">
        <h1>🗂️ Open Project Folders</h1>
        
        <div class="info-box">
            <h3>ℹ️ What does this do?</h3>
            <p>This tool opens all project folders in Windows Explorer for easy access:</p>
            <ul style="color: var(--text-secondary); margin-left: 20px;">
                <li>datamatch/source and datamatch/target</li>
                <li>input, output, and expfd folders</li>
                <li>FF_FILES/datamig/file-format</li>
                <li>copybook folder</li>
            </ul>
        </div>
        
        <form method="POST" id="openFoldersForm" onsubmit="showLoading()">
            <div class="form-group">
                <label for="folder_name">Project Folder Name:</label>
                <input type="text" id="folder_name" name="folder_name" 
                       value="{{ folder_name }}" required
                       placeholder="e.g., myproject, rbs, occ">
                <div class="info-text">Enter the name of the project folder</div>
            </div>

            <div class="form-group">
                <label for="base_path">Base Directory Path:</label>
                <input type="text" id="base_path" name="base_path" 
                       value="{{ base_path }}" required
                       placeholder="C:/File_conversion">
                <div class="info-text">Base directory containing the project folder</div>
            </div>

            <div class="button-group">
                <a href="/" class="btn btn-secondary">← Back to Main Menu</a>
                <button type="submit" class="btn btn-primary">▶️ Open All Folders</button>
            </div>
        </form>

        {% if output %}
        <div class="output-box {% if success %}success{% endif %}">
            <pre id="outputPre">{{ output }}</pre>
            <div class="resize-handle" title="Drag to resize"></div>
        </div>
        <div style="margin-top: 10px; padding: 8px; background: rgba(37, 99, 235, 0.1); border-radius: 6px; font-size: 0.85rem; color: var(--text-secondary);">
            💡 Tip: Drag the corner handle to resize the output box
        </div>
        {% endif %}
    </div>

    <script>
        function showLoading() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }
        function colorizeOutput() {
            const outputPre = document.getElementById('outputPre');
            if (outputPre) {
                let text = outputPre.innerHTML;
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bfailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                outputPre.innerHTML = text;
            }
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
</body>
</html>
'''


# Template for Copy to S3 page
COPY_S3_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Copy to AWS S3</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        :root {
            /* Professional Corporate Color Palette */
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: #334155;
            --shadow: rgba(0, 0, 0, 0.3);
            
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            color: #e0e0e0;
        }

        .container {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 16px var(--shadow);
            max-width: 800px;
            width: 100%;
        }

        h1 {
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-align: center;
        }

        .subtitle {
            text-align: center;
            color: #b0b0b0;
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .info-box {
            background: rgba(245, 87, 108, 0.1);
            border-left: 4px solid #2563eb;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 8px;
        }

        .info-box h3 {
            color: #ef4444;
            margin-bottom: 10px;
        }

        .info-box p {
            color: #d0d0d0;
            line-height: 1.6;
            margin-bottom: 8px;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #3b82f6;
            font-weight: 600;
            font-size: 1.1em;
        }

        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            font-size: 16px;
            background: rgba(255, 255, 255, 0.05);
            color: #e0e0e0;
            transition: all 0.3s ease;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #2563eb;
            background: rgba(255, 255, 255, 0.08);
            box-shadow: 0 0 20px rgba(245, 87, 108, 0.3);
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }

        button {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-back {
            background: var(--secondary-gradient);
            color: white;
        }

        .btn-back:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .btn-upload {
            background: var(--secondary-gradient);
            color: white;
        }

        .btn-upload:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .output-box {
            margin-top: 30px;
            padding: 0;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            min-height: 450px;
            max-height: none;
            resize: both;
            overflow: auto;
            position: relative;
        }

        .output-box pre {
            padding: 20px;
            color: #e0e0e0;
            white-space: pre;
            word-wrap: normal;
            overflow-wrap: normal;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
            min-width: max-content;
        }

        .success {
            border-left: 4px solid #3b82f6;
        }

        .error {
            border-left: 4px solid #2563eb;
        }

        /* Scrollbar styling */
        .output-box::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }

        .output-box::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 6px;
        }

        .output-box::-webkit-scrollbar-thumb {
            background: var(--secondary-gradient);
            border-radius: 6px;
        }

        .output-box::-webkit-scrollbar-thumb:hover {
            background: rgba(37, 99, 235, 0.8);
        }

        .output-box::-webkit-scrollbar-corner {
            background: rgba(0, 0, 0, 0.2);
        }

        .resize-handle {
            position: absolute;
            bottom: 0;
            right: 0;
            width: 20px;
            height: 20px;
            background: rgba(255, 255, 255, 0.2);
            cursor: nw-resize;
            clip-path: polygon(100% 0, 100% 100%, 0 100%);
        }

        .resize-handle:hover {
            background: rgba(37, 99, 235, 0.6);
        }

        /* Loading overlay */
        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 15, 35, 0.9);
            justify-content: center;
            align-items: center;
            z-index: 9999;
            flex-direction: column;
            gap: 20px;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(37, 99, 235, 0.3);
            border-top-color: #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .loading-text {
            color: #3b82f6;
            font-size: 1.2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
        <div class="loading-text">Processing... Please wait</div>
    </div>

    <div class="container">
        <h1>☁️ Copy to AWS S3</h1>
        <p class="subtitle">Upload Application Data to S3 Bucket</p>

        <div class="info-box">
            <h3>📋 Upload Information</h3>
            <p><strong>Source:</strong> Local application converted data folder</p>
            <p><strong>Destination:</strong> AWS S3 bucket (sandboxdee01s3att01)</p>
            <p><strong>Script:</strong> copy_s3.sh (uses AWS CLI)</p>
            <p><strong>Note:</strong> Ensure AWS credentials are configured and Git Bash/WSL is installed</p>
        </div>

        <form method="POST" id="copyS3Form" onsubmit="showLoading()">
            <div class="form-group">
                <label for="application_name">Application Name *</label>
                <input type="text" 
                       id="application_name" 
                       name="application_name" 
                       value="{{ application_name }}"
                       placeholder="Enter application name (e.g., MyApp)"
                       required>
            </div>

            <div class="button-group">
                <button type="button" class="btn-back" onclick="window.location.href='/'">
                    ← Back to Main Menu
                </button>
                <button type="submit" class="btn-upload">
                    ☁️ Upload to S3
                </button>
            </div>
        </form>

        {% if output %}
        <div class="output-box {% if success %}success{% else %}error{% endif %}">
            <pre id="outputPre">{{ output }}</pre>
            <div class="resize-handle" title="Drag to resize"></div>
        </div>
        <div style="margin-top: 10px; padding: 8px; background: rgba(37, 99, 235, 0.1); border-radius: 6px; font-size: 0.85rem; color: var(--text-secondary);">
            💡 Tip: Drag the corner handle to resize the output box
        </div>
        {% endif %}
    </div>

    <script>
        function showLoading() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }
        function colorizeOutput() {
            const outputPre = document.getElementById('outputPre');
            if (outputPre) {
                let text = outputPre.innerHTML;
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bfailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                outputPre.innerHTML = text;
            }
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
</body>
</html>
'''

# Template for FF File Mapping page
FF_MAPPING_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>FF File Mapping</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            /* Professional Corporate Color Palette */
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: #334155;
            --shadow: rgba(0, 0, 0, 0.3);
            
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
            --mapping-gradient: var(--accent-gradient);
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            color: #e0e0e0;
        }

        .container {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 16px var(--shadow);
            max-width: 900px;
            width: 100%;
        }

        h1 {
            background: var(--mapping-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-align: center;
        }

        .subtitle {
            text-align: center;
            color: #b0b0b0;
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .info-box {
            background: rgba(48, 207, 208, 0.1);
            border-left: 4px solid #3b82f6;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 8px;
        }

        .info-box h3 {
            color: #3b82f6;
            margin-bottom: 10px;
        }

        .info-box p {
            color: #d0d0d0;
            line-height: 1.6;
            margin-bottom: 5px;
            font-size: 0.95em;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #3b82f6;
            font-weight: 600;
            font-size: 1.1em;
        }

        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            font-size: 16px;
            background: rgba(255, 255, 255, 0.05);
            color: #e0e0e0;
            transition: all 0.3s ease;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #3b82f6;
            background: rgba(255, 255, 255, 0.08);
            box-shadow: 0 0 20px rgba(48, 207, 208, 0.3);
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }

        button {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-back {
            background: var(--secondary-gradient);
            color: white;
        }

        .btn-back:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .btn-submit {
            background: var(--mapping-gradient);
            color: white;
        }

        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(48, 207, 208, 0.4);
        }

        .output-box {
            margin-top: 30px;
            padding: 0;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            min-height: 450px;
            max-height: none;
            resize: both;
            overflow: auto;
            position: relative;
        }

        .output-box pre {
            padding: 20px;
            color: #e0e0e0;
            white-space: pre;
            word-wrap: normal;
            overflow-wrap: normal;
            font-family: 'Courier New', monospace;
            font-size: 14px;
            line-height: 1.6;
            min-width: max-content;
        }

        /* Custom scrollbar styling */
        .output-box::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }

        .output-box::-webkit-scrollbar-track {
            background: rgba(0, 0, 0, 0.2);
            border-radius: 6px;
        }

        .output-box::-webkit-scrollbar-thumb {
            background: rgba(37, 99, 235, 0.6);
            border-radius: 6px;
        }

        .output-box::-webkit-scrollbar-thumb:hover {
            background: rgba(37, 99, 235, 0.8);
        }

        .output-box::-webkit-scrollbar-corner {
            background: rgba(0, 0, 0, 0.2);
        }

        .resize-handle {
            position: absolute;
            bottom: 0;
            right: 0;
            width: 20px;
            height: 20px;
            background: rgba(255, 255, 255, 0.2);
            cursor: nw-resize;
            clip-path: polygon(100% 0, 100% 100%, 0 100%);
        }

        .resize-handle:hover {
            background: rgba(48, 207, 208, 0.6);
        }

        .success { border-left: 4px solid #3b82f6; }
        .error { border-left: 4px solid #2563eb; }

        /* Loading overlay */
        .loading-overlay {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(15, 15, 35, 0.9);
            justify-content: center;
            align-items: center;
            z-index: 9999;
            flex-direction: column;
            gap: 20px;
        }

        .spinner {
            width: 50px;
            height: 50px;
            border: 5px solid rgba(37, 99, 235, 0.3);
            border-top-color: #2563eb;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }

        @keyframes spin {
            to { transform: rotate(360deg); }
        }

        .loading-text {
            color: #3b82f6;
            font-size: 1.2rem;
            font-weight: 600;
        }
    </style>
</head>
<body>
    <div class="loading-overlay" id="loadingOverlay">
        <div class="spinner"></div>
        <div class="loading-text">Processing... Please wait</div>
    </div>

    <div class="container">
        <h1>🗂️ FF File Mapping</h1>
        <p class="subtitle">Map and Organize Files Based on CSV Configuration</p>

        <div class="info-box">
            <h3>📋 Mapping Information</h3>
            <p><strong>Source:</strong> Directory containing .ff and .txt files</p>
            <p><strong>Destination:</strong> Directory where files will be organized</p>
            <p><strong>CSV Format:</strong> FOLDER_NAME, FILE_NAME, DEST_FILE_NAME</p>
            <p><strong>Output Structure:</strong> Creates .ff and Converted Files subdirectories</p>
        </div>

        <form method="POST" id="ffMappingForm" onsubmit="showLoading()">
            <div class="form-group">
                <label for="source_dir">Source Directory *</label>
                <input type="text" 
                       id="source_dir" 
                       name="source_dir" 
                       value="{{ source_dir }}"
                       placeholder="D:\\File_conversion\\File_conversion\\rushabh\\ME\\output"
                       required>
            </div>

            <div class="form-group">
                <label for="dest_dir">Destination Directory *</label>
                <input type="text" 
                       id="dest_dir" 
                       name="dest_dir" 
                       value="{{ dest_dir }}"
                       placeholder="D:\\File_conversion\\File_conversion\\Application_details\\ME\\converted_data"
                       required>
            </div>

            <div class="form-group">
                <label for="csv_file">CSV Mapping File *</label>
                <input type="text" 
                       id="csv_file" 
                       name="csv_file" 
                       value="{{ csv_file }}"
                       placeholder="D:/File_conversion/File_conversion/rushabh/ME.csv"
                       required>
            </div>

            <div class="button-group">
                <button type="button" class="btn-back" onclick="window.location.href='/'">
                    ← Back to Main Menu
                </button>
                <button type="submit" class="btn-submit">
                    🚀 Run File Mapping
                </button>
            </div>
        </form>

        {% if output %}
        <div class="output-box {% if success %}success{% else %}error{% endif %}">
            <pre id="outputPre">{{ output }}</pre>
            <div class="resize-handle" title="Drag to resize"></div>
        </div>
        <div style="margin-top: 10px; padding: 8px; background: rgba(48, 207, 208, 0.1); border-radius: 6px; font-size: 0.85rem; color: var(--text-secondary);">
            💡 Tip: Drag the corner handle to resize the output box
        </div>
        {% endif %}
    </div>

    <script>
        function showLoading() {
            document.getElementById('loadingOverlay').style.display = 'flex';
        }
        function colorizeOutput() {
            const outputPre = document.getElementById('outputPre');
            if (outputPre) {
                let text = outputPre.innerHTML;
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bfailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                outputPre.innerHTML = text;
            }
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
</body>
</html>
'''

FILE_RETRIEVAL_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>File Retrieval</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: #334155;
            --shadow: rgba(0, 0, 0, 0.3);
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
        }

        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #0f172a 0%, #1e293b 100%);
            min-height: 100vh;
            display: flex;
            justify-content: center;
            align-items: center;
            padding: 20px;
            color: #e0e0e0;
        }

        .container {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 8px 16px var(--shadow);
            max-width: 900px;
            width: 100%;
        }

        h1 {
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5em;
            margin-bottom: 10px;
            text-align: center;
        }

        .subtitle {
            text-align: center;
            color: #b0b0b0;
            margin-bottom: 30px;
            font-size: 1.1em;
        }

        .info-box {
            background: rgba(48, 207, 208, 0.1);
            border-left: 4px solid #3b82f6;
            padding: 15px;
            margin-bottom: 30px;
            border-radius: 8px;
        }

        .info-box h3 {
            color: #3b82f6;
            margin-bottom: 10px;
        }

        .info-box p {
            color: #d0d0d0;
            line-height: 1.6;
            margin-bottom: 5px;
            font-size: 0.95em;
        }

        .form-group {
            margin-bottom: 25px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            color: #3b82f6;
            font-weight: 600;
            font-size: 1.1em;
        }

        input[type="text"] {
            width: 100%;
            padding: 15px;
            border: 2px solid rgba(255, 255, 255, 0.1);
            border-radius: 10px;
            font-size: 16px;
            background: rgba(255, 255, 255, 0.05);
            color: #e0e0e0;
            transition: all 0.3s ease;
        }

        input[type="text"]:focus {
            outline: none;
            border-color: #3b82f6;
            background: rgba(255, 255, 255, 0.08);
            box-shadow: 0 0 20px rgba(48, 207, 208, 0.3);
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 30px;
        }

        button {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 10px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        .btn-back {
            background: var(--secondary-gradient);
            color: white;
        }

        .btn-back:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(37, 99, 235, 0.4);
        }

        .btn-submit {
            background: var(--primary-gradient);
            color: white;
        }

        .btn-submit:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(48, 207, 208, 0.4);
        }

        .output-box {
            margin-top: 30px;
            padding: 0;
            background: rgba(0, 0, 0, 0.3);
            border-radius: 10px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            min-height: 450px;
            max-height: none;
            resize: both;
            overflow: auto;
            position: relative;
        }

        .output-box pre {
            padding: 20px;
            color: #e0e0e0;
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'Consolas', 'Monaco', monospace;
            font-size: 14px;
            line-height: 1.6;
            margin: 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 File Retrieval</h1>
        <p class="subtitle">Search and copy files from source folder to destination</p>

        <div class="info-box">
            <h3>ℹ️ Instructions:</h3>
            <p><strong>File List:</strong> Text file containing list of files to retrieve (one per line)</p>
            <p><strong>Source Folder:</strong> Folder to search recursively for files</p>
            <p><strong>Destination Folder:</strong> Folder where found files will be copied</p>
            <p><strong>Note:</strong> Script will search all subdirectories and create empty_and_missing_files.txt log</p>
        </div>

        <form method="POST" action="{{ url_for('file_retrieval_page') }}">
            <div class="form-group">
                <label for="file_list">📄 File List Path:</label>
                <input type="text" id="file_list" name="file_list" 
                       value="{{ file_list }}" 
                       placeholder="C:/File_conversion/file_list.txt" required>
            </div>

            <div class="form-group">
                <label for="source_folder">📂 Source Folder (Recursive Search):</label>
                <input type="text" id="source_folder" name="source_folder" 
                       value="{{ source_folder }}" 
                       placeholder="D:/Wave1/Drop4/BAD_DEBT/RL81B25L" required>
            </div>

            <div class="form-group">
                <label for="dest_folder">📁 Destination Folder:</label>
                <input type="text" id="dest_folder" name="dest_folder" 
                       value="{{ dest_folder }}" 
                       placeholder="D:/File_conversion/output" required>
            </div>

            <div class="button-group">
                <button type="button" class="btn-back" onclick="window.location.href='/'">
                    ← Back to Main Menu
                </button>
                <button type="submit" class="btn-submit">
                    🔍 Retrieve Files
                </button>
            </div>
        </form>

        {% if output %}
        <div class="output-box">
            <pre id="output">{{ output }}</pre>
        </div>
        {% endif %}
    </div>

    <script>
        function colorizeOutput() {
            const outputPre = document.getElementById('output');
            if (outputPre && outputPre.textContent.trim()) {
                let text = outputPre.textContent;
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*SUCCESS.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*ERROR.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*MISSING.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*EMPTY.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*WARNING.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*📄.*)$/gm, '<span style="color: #3b82f6; font-weight: 500;">$1</span>');
                outputPre.innerHTML = text;
            }
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
</body>
</html>
'''

SCRIPTS_CONFIG_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Scripts Configuration</title>
    <style>
        :root {
            /* Professional Corporate Color Palette */
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: #334155;
            --shadow: rgba(0, 0, 0, 0.3);
            
            --primary-gradient: linear-gradient(135deg, #2563eb 0%, #1e40af 100%);
            --secondary-gradient: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
            --accent-gradient: linear-gradient(135deg, #1e40af 0%, #1e3a8a 100%);
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        body {
            font-family: 'Inter', 'Segoe UI', -apple-system, BlinkMacSystemFont, sans-serif;
            background: var(--bg-primary);
            background-image: 
                radial-gradient(circle at 20% 80%, rgba(120, 119, 198, 0.3) 0%, transparent 50%),
                radial-gradient(circle at 80% 20%, rgba(255, 119, 198, 0.3) 0%, transparent 50%);
            min-height: 100vh;
            color: var(--text-primary);
            padding: 20px;
        }

        .container {
            max-width: 1000px;
            margin: 20px auto;
            background: var(--bg-card);
            backdrop-filter: blur(10px);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 20px 40px var(--shadow);
            padding: 40px;
            position: relative;
            overflow: hidden;
            animation: slideIn 0.5s ease-out;
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

        @keyframes slideIn {
            from {
                opacity: 0;
                transform: translateY(-30px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
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

        h2 {
            color: var(--accent-color);
            margin-top: 35px;
            margin-bottom: 20px;
            font-size: 1.4rem;
            border-bottom: 2px solid var(--border);
            padding-bottom: 10px;
        }

        h2:first-of-type {
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
            border-color: #3b82f6;
            box-shadow: 0 0 0 3px rgba(67, 233, 123, 0.1);
            transform: translateY(-2px);
        }

        .info-text {
            font-size: 0.85rem;
            color: var(--text-secondary);
            margin-top: 5px;
            font-style: italic;
            opacity: 0.8;
        }

        .button-group {
            display: flex;
            gap: 15px;
            margin-top: 40px;
        }

        button {
            flex: 1;
            padding: 15px 30px;
            border: none;
            border-radius: 12px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .btn-submit {
            background: var(--secondary-gradient);
            color: white;
        }

        .btn-submit:hover {
            transform: translateY(-3px);
            box-shadow: 0 10px 25px rgba(67, 233, 123, 0.4);
        }

        .btn-home {
            background: var(--bg-secondary);
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }

        .btn-home:hover {
            background: var(--accent-color);
            color: white;
            border-color: var(--accent-color);
            transform: translateY(-3px);
        }

        .output-box {
            margin-top: 30px;
            padding: 20px;
            background: var(--bg-secondary);
            border: 2px solid var(--border);
            border-radius: 12px;
            border-left: 4px solid #3b82f6;
        }

        .output-box pre {
            white-space: pre-wrap;
            word-wrap: break-word;
            font-family: 'JetBrains Mono', 'Fira Code', 'Consolas', monospace;
            font-size: 0.9rem;
            line-height: 1.6;
            margin: 0;
            color: var(--text-primary);
        }

        .success {
            border-left-color: #3b82f6;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>⚙️ Scripts Configuration</h1>
        
        <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; margin-bottom: 30px; border-left: 4px solid var(--accent-color);">
            <p style="margin: 0; color: var(--text-secondary); font-size: 0.9rem;">
                <strong style="color: var(--accent-color);">ℹ️ Note:</strong> Common paths (copybook, expfd, application, FORMAT_PATH, INPUT_PATH) 
                are automatically loaded from path.txt. Configure script-specific settings below.
            </p>
        </div>
        
        <form method="POST">
            <h2>📂 Copy Bulk Configuration</h2>
            
            <div class="form-group">
                <label for="copy_source">Source Path:</label>
                <input type="text" id="copy_source" name="copy_source" 
                       value="{{ config.get('COPY_SOURCE_PATH', '') }}" required>
                <div class="info-text">Directory containing source files to copy</div>
            </div>

            <div class="form-group">
                <label for="copy_dest">Destination Path:</label>
                <input type="text" id="copy_dest" name="copy_dest" 
                       value="{{ config.get('COPY_DEST_PATH', '') }}" required>
                <div class="info-text">Directory where files will be copied</div>
            </div>

            <div class="form-group">
                <label for="copy_input">Input File:</label>
                <input type="text" id="copy_input" name="copy_input" 
                       value="{{ config.get('COPY_INPUT_FILE', 'IGD.txt') }}" required>
                <div class="info-text">CSV file with oldfilename,newfilename pairs</div>
            </div>

            <h2>🔄 DataTurn Configuration</h2>

            <div class="form-group">
                <label for="dataturn_exe">DataTurn Executable Path:</label>
                <input type="text" id="dataturn_exe" name="dataturn_exe" 
                       value="{{ config.get('DATATURN_EXE_PATH', 'C:/Program Files/Anubex/DataTurn/bin/dataturn.exe') }}" required>
                <div class="info-text">Full path to dataturn.exe</div>
            </div>

            <div class="form-group">
                <label for="dataturn_config">Configuration File:</label>
                <input type="text" id="dataturn_config" name="dataturn_config" 
                       value="{{ config.get('DATATURN_CONFIG_FILE', 'rushabh.configuration') }}" required>
                <div class="info-text">DataTurn configuration file name (Repository, EXPFD path, and output directory use paths from path.txt)</div>
            </div>

            <h2>🔁 Bulk Conversion Configuration</h2>
            <div class="info-text" style="margin-bottom: 20px;">Bulk conversion uses application name from the form and bulk_conversion_base_PATH to generate paths dynamically. All operation logs are saved in the centralized log system (View Logs).</div>

            <div class="form-group">
                <label for="bulk_base_path">Base Path:</label>
                <input type="text" id="bulk_base_path" name="bulk_base_path" 
                       value="{{ config.get('bulk_conversion_base_PATH', 'C:/File_conversion') }}" required>
                <div class="info-text">Base directory path (e.g., C:/File_conversion). The system will append app name and subdirectories.</div>
            </div>

            <div class="form-group">
                <label for="bulk_dowitcher">Dowitcher Executable Path:</label>
                <input type="text" id="bulk_dowitcher" name="bulk_dowitcher" 
                       value="{{ config.get('BULK_DOWITCHER_PATH', 'C:/File_conversion/dowitcher.exe') }}" required>
                <div class="info-text">Full path to dowitcher.exe for bulk conversion</div>
            </div>

            <h2 style="margin-top: 30px;">☁️ AWS S3 Configuration</h2>
            
            <div class="form-group">
                <label for="s3_bucket">S3 Bucket Name:</label>
                <input type="text" id="s3_bucket" name="s3_bucket" 
                       value="{{ config.get('S3_BUCKET', 'sandboxdee01s3att01') }}" required>
                <div class="info-text">AWS S3 bucket name for file uploads</div>
            </div>

            <div class="form-group">
                <label for="s3_path_prefix">S3 Path Prefix:</label>
                <input type="text" id="s3_path_prefix" name="s3_path_prefix" 
                       value="{{ config.get('S3_PATH_PREFIX', 'file_Conversion') }}" required>
                <div class="info-text">Path prefix within S3 bucket (e.g., file_Conversion)</div>
            </div>

            <div class="form-group">
                <label for="local_data_path">Local Data Path:</label>
                <input type="text" id="local_data_path" name="local_data_path" 
                       value="{{ config.get('LOCAL_DATA_PATH', '/d/File_conversion/File_conversion/Application_details') }}" required>
                <div class="info-text">Base path for application data on local system</div>
            </div>

            <h2 style="margin-top: 30px;">🗂️ FF File Mapping Configuration</h2>
            
            <div class="form-group">
                <label for="ff_mapping_source">Source Directory:</label>
                <input type="text" id="ff_mapping_source" name="ff_mapping_source" 
                       value="{{ config.get('FF_MAPPING_SOURCE', 'D:\\File_conversion\\File_conversion\\rushabh\\ME\\output') }}" required>
                <div class="info-text">Directory containing source .ff and .txt files</div>
            </div>

            <div class="form-group">
                <label for="ff_mapping_dest">Destination Directory:</label>
                <input type="text" id="ff_mapping_dest" name="ff_mapping_dest" 
                       value="{{ config.get('FF_MAPPING_DEST', 'D:\\File_conversion\\File_conversion\\Application_details\\ME\\converted_data') }}" required>
                <div class="info-text">Directory where files will be organized</div>
            </div>

            <div class="form-group">
                <label for="ff_mapping_csv">CSV Mapping File:</label>
                <input type="text" id="ff_mapping_csv" name="ff_mapping_csv" 
                       value="{{ config.get('FF_MAPPING_CSV', 'D:/File_conversion/File_conversion/rushabh/ME.csv') }}" required>
                <div class="info-text">CSV file with format: FOLDER_NAME, FILE_NAME, DEST_FILE_NAME</div>
            </div>

            <h2 style="margin-top: 30px;">🔍 File Retrieval Configuration</h2>
            
            <div class="form-group">
                <label for="file_retrieval_list">File List Path:</label>
                <input type="text" id="file_retrieval_list" name="file_retrieval_list" 
                       value="{{ config.get('FILE_RETRIEVAL_LIST', 'C:/File_conversion/file_list.txt') }}" required>
                <div class="info-text">Text file containing list of files to retrieve (one file name per line)</div>
            </div>

            <div class="form-group">
                <label for="file_retrieval_source">Source Folder (Recursive Search):</label>
                <input type="text" id="file_retrieval_source" name="file_retrieval_source" 
                       value="{{ config.get('FILE_RETRIEVAL_SOURCE', 'D:/Wave1/Drop4/BAD_DEBT/RL81B25L') }}" required>
                <div class="info-text">Folder to search recursively for files listed in the file list</div>
            </div>

            <div class="form-group">
                <label for="file_retrieval_dest">Destination Folder:</label>
                <input type="text" id="file_retrieval_dest" name="file_retrieval_dest" 
                       value="{{ config.get('FILE_RETRIEVAL_DEST', 'D:/File_conversion/File_conversion/rushabh/automation/FILE_CONVERSION/bulk_conversion/badebt/input') }}" required>
                <div class="info-text">Folder where retrieved files will be copied to</div>
            </div>

            <div class="button-group">
                <button type="submit" class="btn-submit">💾 Save Scripts Config</button>
                <button type="button" class="btn-home" onclick="window.location.href='/update_paths'" style="background: var(--primary-gradient); color: white;">⚙️ Update path.txt</button>
                <button type="button" class="btn-home" onclick="window.location.href='/'">🏠 Home</button>
            </div>
        </form>

        {% if output %}
        <div class="output-box {% if success %}success{% endif %}">
            <pre id="outputPre">{{ output }}</pre>
        </div>
        {% endif %}
    </div>
    <script>
        function colorizeOutput() {
            const outputPre = document.getElementById('outputPre');
            if (outputPre) {
                let text = outputPre.innerHTML;
                text = text.replace(/^(.*✅.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSUCCESS\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bSuccessfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bcompleted successfully\b.*)$/gm, '<span style="color: #22c55e; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*❌.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bERROR\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bFailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bfailed\b.*)$/gm, '<span style="color: #ef4444; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*⚠️.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                text = text.replace(/^(.*\bWARNING\b.*)$/gm, '<span style="color: #eab308; font-weight: 500;">$1</span>');
                outputPre.innerHTML = text;
            }
        }
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', colorizeOutput);
        } else {
            colorizeOutput();
        }
    </script>
    </script>
</body>
</html>
'''

# Template for Update Paths page
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
        <p>This tool updates the application name in all paths in path.txt. It will:</p>
        <ul style="color: var(--text-secondary); margin-left: 20px;">
            <li>Update the application name across all configured paths</li>
            <li>Automatically modify paths for input, output, FF_FILES, copybook, expfd, and datamatch directories</li>
            <li>Preserve all other configuration settings</li>
        </ul>
        <p style="margin-top: 10px;"><strong>Example:</strong> Changing from "occ" to "rbs" will update C:/File_conversion/occ/input to C:/File_conversion/rbs/input</p>
        <p>Current application name: <span class="current-app">{{ current_app }}</span></p>
    </div>
    
    <form method="post" id="pathForm">
        <div class="form-group">
            <label for="app_name">🔤 New Application Name:</label>
            <input type="text" id="app_name" name="app_name" value="{{ app_name }}" required 
                   placeholder="Enter new application name (e.g., rbs, cbr, mc)">
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

# Log Viewer Template
LOG_VIEWER_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Log Viewer - ConvertFlow Studio</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --accent-color: #3b82f6;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: #334155;
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
            background: var(--bg-primary);
            color: var(--text-primary);
            min-height: 100vh;
            padding: 20px;
        }

        .container {
            max-width: 1400px;
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
            color: var(--primary-color);
        }

        .log-info {
            background: var(--bg-secondary);
            padding: 15px;
            border-radius: 8px;
            margin-bottom: 20px;
            border-left: 4px solid var(--accent-color);
        }

        .log-info p {
            margin: 5px 0;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .log-info .icon {
            font-size: 1.2rem;
        }

        .log-controls {
            display: flex;
            gap: 10px;
            margin-bottom: 15px;
            flex-wrap: wrap;
        }

        .btn-mini {
            padding: 10px 20px;
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 8px;
            color: var(--text-secondary);
            font-size: 0.9rem;
            cursor: pointer;
            transition: all 0.2s ease;
            text-decoration: none;
            display: inline-block;
        }

        .btn-mini:hover {
            background: var(--primary-color);
            color: white;
            transform: translateY(-2px);
        }

        .log-box {
            background: var(--bg-primary);
            border: 2px solid var(--border);
            border-radius: 12px;
            padding: 20px;
            min-height: 600px;
            max-height: 80vh;
            overflow: auto;
            font-family: 'Consolas', 'Courier New', monospace;
            font-size: 0.85rem;
            line-height: 1.6;
            white-space: pre-wrap;
            word-wrap: break-word;
        }

        .log-box::-webkit-scrollbar {
            width: 12px;
            height: 12px;
        }

        .log-box::-webkit-scrollbar-track {
            background: var(--bg-secondary);
            border-radius: 6px;
        }

        .log-box::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 6px;
        }

        .log-box::-webkit-scrollbar-thumb:hover {
            background: var(--accent-color);
        }

        .log-error {
            color: #ef4444;
        }

        .log-warning {
            color: #eab308;
        }

        .log-success {
            color: #22c55e;
        }

        .log-info {
            color: var(--text-secondary);
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>📋 Log Viewer</h1>
        
        <div class="breadcrumb">
            <a href="/">🏠 Home</a>
            <span>›</span>
            <span>Log Viewer</span>
        </div>

        <div class="log-info">
            <p><span class="icon">📁</span><strong>Log File:</strong> {{ log_filepath }}</p>
            <p><span class="icon">📊</span><strong>Showing:</strong> Last 10000 entries from today's log</p>
            <p><span class="icon">🔄</span><strong>Auto-refresh:</strong> Every 30 seconds (when enabled)</p>
        </div>

        <div class="log-controls">
            <button class="btn-mini" onclick="scrollToTop()">⬆️ Top</button>
            <button class="btn-mini" onclick="scrollToBottom()">⬇️ Bottom</button>
            <button class="btn-mini" onclick="copyLogs()">📋 Copy All</button>
            <button class="btn-mini" onclick="window.location.reload()">🔄 Refresh</button>
            <a href="/" class="btn-mini">🏠 Back to Home</a>
        </div>

        <div class="log-box" id="logBox">{{ log_content }}</div>
    </div>

    <script>
        function scrollToTop() {
            document.getElementById('logBox').scrollTop = 0;
        }

        function scrollToBottom() {
            const logBox = document.getElementById('logBox');
            logBox.scrollTop = logBox.scrollHeight;
        }

        function copyLogs() {
            const logBox = document.getElementById('logBox');
            const text = logBox.innerText;
            navigator.clipboard.writeText(text).then(() => {
                alert('Logs copied to clipboard!');
            }).catch(err => {
                console.error('Failed to copy:', err);
                alert('Failed to copy logs.');
            });
        }

        // Color-code log messages
        function colorizeLogs() {
            const logBox = document.getElementById('logBox');
            let html = logBox.textContent;
            
            // Error patterns - using word boundaries to match whole words only
            html = html.replace(/\b(ERROR|FAILED|Exception|Traceback)\b/gi, '<span class="log-error">$1</span>');
            
            // Warning patterns - using word boundaries to match whole words only
            html = html.replace(/\b(WARNING|WARN)\b/gi, '<span class="log-warning">$1</span>');
            html = html.replace(/(⚠️)/g, '<span class="log-warning">$1</span>');
            
            // Success patterns - using word boundaries to match whole words only
            html = html.replace(/\b(SUCCESS|COMPLETED)\b/gi, '<span class="log-success">$1</span>');
            html = html.replace(/(✅)/g, '<span class="log-success">$1</span>');
            
            logBox.innerHTML = html;
        }

        // Auto-scroll to bottom on load
        window.addEventListener('load', function() {
            colorizeLogs();
            scrollToBottom();
        });
    </script>
</body>
</html>
'''

@app.route('/', methods=['GET', 'POST'])
def index():
    """Main page with all script buttons"""
    if request.method == 'POST':
        action = request.form.get('action', '')
        
        if action == 'copy_bulk':
            return redirect(url_for('copy_bulk_page'))
        elif action == 'dataturn':
            return redirect(url_for('dataturn_page'))
        elif action == 'expfd_creation':
            return redirect(url_for('expfd_creation_page'))
        elif action == 'bulk_expfd':
            return redirect(url_for('bulk_expfd_page'))
        elif action == 'bulk_dataturn':
            return redirect(url_for('bulk_dataturn_page'))
        elif action == 'bulk_conversion':
            return redirect(url_for('bulk_conversion_page'))
        elif action == 'create_folder':
            return redirect(url_for('create_folder_page'))
        elif action == 'open_folders':
            return redirect(url_for('open_folders_page'))
        elif action == 'copy_s3':
            return redirect(url_for('copy_s3_page'))
        elif action == 'ff_mapping':
            return redirect(url_for('ff_mapping_page'))
        elif action == 'file_retrieval':
            return redirect(url_for('file_retrieval_page'))
        elif action == 'scripts_config':
            return redirect(url_for('scripts_config_page'))
        elif action == 'update_paths':
            return redirect(url_for('update_paths_page'))
        elif action == 'view_logs':
            return redirect(url_for('view_logs_page'))
        elif action == 'user_guide':
            return redirect(url_for('user_guide_page'))
    
    return render_template_string(MAIN_TEMPLATE)

@app.route('/copy_bulk', methods=['GET', 'POST'])
def copy_bulk_page():
    """Copy files in bulk based on CSV mapping"""
    output = ''
    success = False
    
    # Read configuration (merges path.txt and scripts_config.txt)
    config_file = os.path.join(os.getcwd(), 'scripts_config.txt')
    config = read_scripts_config(config_file)
    
    # Use COPY_SOURCE_PATH from scripts_config.txt
    source_path = config.get('COPY_SOURCE_PATH', '')
    dest_path = config.get('COPY_DEST_PATH', '')
    input_file = config.get('COPY_INPUT_FILE', 'IGD.txt')
    
    if request.method == 'POST':
        source_path = request.form.get('source_path', '').strip()
        dest_path = request.form.get('dest_path', '').strip()
        input_file = request.form.get('input_file', '').strip()
        
        if source_path and dest_path and input_file:
            output, success = run_copy_bulk(source_path, dest_path, input_file)
        else:
            output = 'Error: All fields are required.'
    
    return render_template_string(COPY_BULK_TEMPLATE, output=output, success=success,
                                 source_path=source_path, dest_path=dest_path, input_file=input_file)

@app.route('/bulk_expfd', methods=['GET', 'POST'])
def bulk_expfd_page():
    """Create EXPFD for all copybooks in bulk"""
    output = ''
    success = False
    
    if request.method == 'POST':
        # Read configuration (merges path.txt and scripts_config.txt)
        config_file = os.path.join(os.getcwd(), 'scripts_config.txt')
        config = read_scripts_config(config_file)
        
        # Run bulk EXPFD creation
        output, success = run_bulk_expfd(config)
    
    return render_template_string(BULK_EXPFD_TEMPLATE, output=output, success=success)

@app.route('/bulk_dataturn', methods=['GET', 'POST'])
def bulk_dataturn_page():
    """Run DataTurn for all EXPFD files in bulk"""
    output = ''
    success = False
    
    if request.method == 'POST':
        # Read configuration (merges path.txt and scripts_config.txt)
        config_file = os.path.join(os.getcwd(), 'scripts_config.txt')
        config = read_scripts_config(config_file)
        
        # Run bulk DataTurn
        output, success = run_bulk_dataturn(config)
    
    return render_template_string(BULK_DATATURN_TEMPLATE, output=output, success=success)

@app.route('/bulk_conversion', methods=['GET', 'POST'])
def bulk_conversion_page():
    """Run bulk conversion for all .ff files"""
    output = ''
    success = False
    app_name = ''
    
    # Read configuration (merges path.txt and scripts_config.txt)
    config_file = os.path.join(os.getcwd(), 'scripts_config.txt')
    config = read_scripts_config(config_file)
    
    # Get bulk_conversion_base_PATH from config, fallback to BASE_PATH, then to current directory
    base_path = config.get('bulk_conversion_base_PATH', config.get('BASE_PATH', os.getcwd()))
    
    if request.method == 'POST':
        app_name = request.form.get('app_name', '').strip()
        
        if app_name:
            # Run bulk conversion with app_name and base_path
            output, success = run_bulk_conversion(app_name, base_path, config)
        else:
            output = 'Error: Application name is required.'
    
    return render_template_string(BULK_CONVERSION_TEMPLATE, output=output, success=success, app_name=app_name)


@app.route('/create_folder', methods=['GET', 'POST'])
def create_folder_page():
    """Create folder structure for a new project"""
    output = ''
    success = False
    folder_name = ''
    
    # Read configuration (merges path.txt and scripts_config.txt)
    config_file = os.path.join(os.getcwd(), 'scripts_config.txt')
    config = read_scripts_config(config_file)
    
    # Get BASE_PATH from config, default to current directory if not found
    base_path = config.get('BASE_PATH', os.getcwd())
    
    if request.method == 'POST':
        folder_name = request.form.get('folder_name', '').strip()
        base_path = request.form.get('base_path', '').strip()
        
        if folder_name and base_path:
            output, success = run_create_folder(folder_name, base_path)
        else:
            output = 'Error: Folder name and base path are required.'
    
    return render_template_string(CREATE_FOLDER_TEMPLATE, output=output, success=success,
                                 folder_name=folder_name, base_path=base_path)

@app.route('/open_folders', methods=['GET', 'POST'])
def open_folders_page():
    """Open all project folders in Windows Explorer"""
    output = ''
    success = False
    folder_name = ''
    
    # Read configuration (merges path.txt and scripts_config.txt)
    config_file = os.path.join(os.getcwd(), 'scripts_config.txt')
    config = read_scripts_config(config_file)
    
    # Get BASE_PATH from config, default to current directory if not found
    base_path = config.get('BASE_PATH', os.getcwd())
    
    if request.method == 'POST':
        folder_name = request.form.get('folder_name', '').strip()
        base_path = request.form.get('base_path', '').strip()
        
        if folder_name and base_path:
            output, success = run_folder_open(folder_name, base_path)
        else:
            output = 'Error: Folder name and base path are required.'
    
    return render_template_string(OPEN_FOLDERS_TEMPLATE, output=output, success=success,
                                 folder_name=folder_name, base_path=base_path)

@app.route('/copy_s3', methods=['GET', 'POST'])
def copy_s3_page():
    """Copy application data to AWS S3"""
    output = ''
    success = False
    application_name = ''
    
    if request.method == 'POST':
        application_name = request.form.get('application_name', '').strip()
        
        if application_name:
            # Get configuration from scripts_config.txt
            config_file = os.path.join(os.getcwd(), 'scripts_config.txt')
            config_data = read_scripts_config(config_file)
            config_data['application_name'] = application_name
            
            output, success = run_copy_s3(config_data)
        else:
            output = 'Error: Application name is required.'
    
    return render_template_string(COPY_S3_TEMPLATE, output=output, success=success,
                                 application_name=application_name)

@app.route('/ff_mapping', methods=['GET', 'POST'])
def ff_mapping_page():
    """Map and organize FF files based on CSV"""
    output = ''
    success = False
    
    # Read configuration file to get default values
    config_file = os.path.join(os.getcwd(), 'scripts_config.txt')
    config_data = read_scripts_config(config_file)
    
    # Pre-fill with values from config file
    source_dir = config_data.get('FF_MAPPING_SOURCE', '')
    dest_dir = config_data.get('FF_MAPPING_DEST', '')
    csv_file = config_data.get('FF_MAPPING_CSV', '')
    
    if request.method == 'POST':
        source_dir = request.form.get('source_dir', '').strip()
        dest_dir = request.form.get('dest_dir', '').strip()
        csv_file = request.form.get('csv_file', '').strip()
        
        if all([source_dir, dest_dir, csv_file]):
            config_data['FF_MAPPING_SOURCE'] = source_dir
            config_data['FF_MAPPING_DEST'] = dest_dir
            config_data['FF_MAPPING_CSV'] = csv_file
            
            output, success = run_ff_mapping(config_data)
        else:
            output = 'Error: All fields are required.'
    
    return render_template_string(FF_MAPPING_TEMPLATE, output=output, success=success,
                                 source_dir=source_dir, dest_dir=dest_dir, csv_file=csv_file)

@app.route('/file_retrieval', methods=['GET', 'POST'])
def file_retrieval_page():
    """Search and copy files from source to destination"""
    output = ''
    success = False
    
    # Read configuration file to get default values
    config_file = os.path.join(os.getcwd(), 'scripts_config.txt')
    config_data = read_scripts_config(config_file)
    
    # Pre-fill with values from config file
    file_list = config_data.get('FILE_RETRIEVAL_LIST', 'file_list.txt')
    source_folder = config_data.get('FILE_RETRIEVAL_SOURCE', '')
    dest_folder = config_data.get('FILE_RETRIEVAL_DEST', '')
    
    if request.method == 'POST':
        file_list = request.form.get('file_list', '').strip()
        source_folder = request.form.get('source_folder', '').strip()
        dest_folder = request.form.get('dest_folder', '').strip()
        
        if all([file_list, source_folder, dest_folder]):
            config_data['FILE_RETRIEVAL_LIST'] = file_list
            config_data['FILE_RETRIEVAL_SOURCE'] = source_folder
            config_data['FILE_RETRIEVAL_DEST'] = dest_folder
            
            output, success = run_file_retrieval(file_list, source_folder, dest_folder)
        else:
            output = 'Error: All fields are required.'
    
    return render_template_string(FILE_RETRIEVAL_TEMPLATE, output=output, success=success,
                                 file_list=file_list, source_folder=source_folder, dest_folder=dest_folder)

@app.route('/scripts_config', methods=['GET', 'POST'])
def scripts_config_page():
    """Update scripts configuration file"""
    output = ''
    success = False
    
    config_file = os.path.join(os.getcwd(), 'scripts_config.txt')
    
    if request.method == 'POST':
        # Get form data - only script-specific settings
        copy_source = request.form.get('copy_source', '').strip()
        copy_dest = request.form.get('copy_dest', '').strip()
        copy_input = request.form.get('copy_input', '').strip()
        dataturn_exe = request.form.get('dataturn_exe', '').strip()
        dataturn_config = request.form.get('dataturn_config', '').strip()
        bulk_base_path = request.form.get('bulk_base_path', '').strip()
        bulk_dowitcher = request.form.get('bulk_dowitcher', '').strip()
        s3_bucket = request.form.get('s3_bucket', '').strip()
        s3_path_prefix = request.form.get('s3_path_prefix', '').strip()
        local_data_path = request.form.get('local_data_path', '').strip()
        ff_mapping_source = request.form.get('ff_mapping_source', '').strip()
        ff_mapping_dest = request.form.get('ff_mapping_dest', '').strip()
        ff_mapping_csv = request.form.get('ff_mapping_csv', '').strip()
        file_retrieval_list = request.form.get('file_retrieval_list', '').strip()
        file_retrieval_source = request.form.get('file_retrieval_source', '').strip()
        file_retrieval_dest = request.form.get('file_retrieval_dest', '').strip()
        
        try:
            # Create configuration content
            config_content = f"""# Scripts Configuration
# Note: Paths like copybook, expfd, application, FORMAT_PATH, INPUT_PATH, OUTPUT_PATH are read directly from path.txt
# Only define paths here that are NOT in path.txt

# Base Path for bulk conversion and other operations
bulk_conversion_base_PATH={bulk_base_path}

# Copy Bulk Configuration
COPY_SOURCE_PATH={copy_source}
COPY_DEST_PATH={copy_dest}
COPY_INPUT_FILE={copy_input}

# DataTurn Configuration
DATATURN_EXE_PATH={dataturn_exe}
DATATURN_CONFIG_FILE={dataturn_config}

# Bulk Conversion Configuration
# Note: Bulk conversion uses BASE_PATH and app name from the form to generate paths dynamically
# All logs are saved in the centralized logging system (logs/ConvertFlow_YYYYMMDD.log)
BULK_DOWITCHER_PATH={bulk_dowitcher}

# AWS S3 Copy Configuration
S3_BUCKET={s3_bucket}
S3_PATH_PREFIX={s3_path_prefix}
LOCAL_DATA_PATH={local_data_path}

# FF File Mapping Configuration
FF_MAPPING_SOURCE={ff_mapping_source}
FF_MAPPING_DEST={ff_mapping_dest}
FF_MAPPING_CSV={ff_mapping_csv}

# File Retrieval Configuration
FILE_RETRIEVAL_LIST={file_retrieval_list}
FILE_RETRIEVAL_SOURCE={file_retrieval_source}
FILE_RETRIEVAL_DEST={file_retrieval_dest}
"""
            
            # Write to file
            with open(config_file, 'w') as f:
                f.write(config_content)
            
            success = True
            output = '✅ Scripts configuration updated successfully!\n\n' + config_content
        except Exception as e:
            output = f'Error updating configuration: {e}\n\nFull Traceback:\n{traceback.format_exc()}'
    else:
        # Read current configuration
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                output = f.read()
        else:
            output = 'Configuration file not found. Fill in the details below to create it.'
    
    # Parse current values for form
    config = read_scripts_config(config_file) if os.path.exists(config_file) else {}
    
    return render_template_string(SCRIPTS_CONFIG_TEMPLATE, output=output, success=success, config=config)

@app.route('/update_paths', methods=['GET', 'POST'])
def update_paths_page():
    """Update application name in path.txt"""
    output = ''
    success = False
    app_name = ''
    current_app = 'occ'  # Default value
    
    # Read current application name from path.txt
    try:
        config_file = os.path.join(os.getcwd(), 'path.txt')
        if os.path.exists(config_file):
            import re
            content = open(config_file, 'r').read()
            # Match pattern like /occ/input or /rbs/output to find the app name
            match = re.search(r'/([^/]+)/(?:input|output|FF_FILES)', content)
            if match:
                current_app = match.group(1)
    except:
        pass
    
    if request.method == 'POST':
        app_name = request.form.get('app_name', '').strip()
        
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
                        
                        for line in lines:
                            if '=' in line:
                                key, value = line.split('=', 1)
                                key = key.strip()
                                original_value = value
                                
                                # Update application paths
                                if current_app in value:
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
                        
                        # Write back to path.txt
                        with open(config_file, 'w') as f:
                            f.writelines(updated_lines)
                        
                        success = True
                        output = ''.join(updated_lines)
                        output = f'✅ Successfully updated {changes_count} path(s) from "{current_app}" to "{app_name}"\n\n' + output
                        current_app = app_name  # Update current_app display
                        
            except Exception as e:
                output = f'Error updating paths: {e}\n\nFull Traceback:\n{traceback.format_exc()}'
        else:
            output = 'Error: Application name is required.'
    
    return render_template_string(UPDATE_PATHS_TEMPLATE, output=output, success=success, 
                                 app_name=app_name, current_app=current_app)

@app.route('/view_logs')
def view_logs_page():
    """Display recent log entries"""
    try:
        import datetime
        log_dir = os.path.join(os.getcwd(), 'logs')
        log_filename = f"ConvertFlow_{datetime.datetime.now().strftime('%Y%m%d')}.log"
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
            log_content = f"No log file found for today.\nLog file would be created at: {log_filepath}\n\nLogs will appear here once operations are performed."
        
        return render_template_string(LOG_VIEWER_TEMPLATE, log_content=log_content, log_filepath=log_filepath)
    except Exception as e:
        return f"Error loading logs: {str(e)}"

@app.route('/user_guide')
def user_guide_page():
    """Display the user guide"""
    try:
        # Try to read the ConvertFlow_USER_GUIDE.md file
        user_guide_path = os.path.join(os.getcwd(), 'ConvertFlow_USER_GUIDE.md')
        
        if os.path.exists(user_guide_path):
            with open(user_guide_path, 'r', encoding='utf-8') as f:
                guide_content = f.read()
        else:
            guide_content = """# User Guide Not Found

The ConvertFlow_USER_GUIDE.md file was not found in the application directory.

Please ensure the user guide file is present in the same directory as the application.

Expected location: `ConvertFlow_USER_GUIDE.md`
"""
        
        # Convert markdown to HTML for better display
        # Simple markdown conversion (headers, bold, lists)
        html_content = guide_content
        
        # Convert headers
        import re
        html_content = re.sub(r'^### (.*?)$', r'<h3>\1</h3>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^## (.*?)$', r'<h2>\1</h2>', html_content, flags=re.MULTILINE)
        html_content = re.sub(r'^# (.*?)$', r'<h1>\1</h1>', html_content, flags=re.MULTILINE)
        
        # Convert bold
        html_content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', html_content)
        
        # Convert code blocks
        html_content = re.sub(r'`([^`]+)`', r'<code>\1</code>', html_content)
        
        # Convert line breaks
        html_content = html_content.replace('\n\n', '</p><p>')
        html_content = '<p>' + html_content + '</p>'
        
        # Create the template
        USER_GUIDE_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>ConvertFlow Studio - User Guide</title>
    <style>
        :root {
            --primary-color: #2563eb;
            --secondary-color: #1e40af;
            --bg-primary: #0f172a;
            --bg-secondary: #1e293b;
            --bg-card: #1e293b;
            --text-primary: #ffffff;
            --text-secondary: #cbd5e1;
            --border: #334155;
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
            background: var(--bg-primary);
            min-height: 100vh;
            color: var(--text-primary);
            padding: 20px;
        }

        .container {
            max-width: 1200px;
            margin: 0 auto;
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            box-shadow: 0 8px 16px var(--shadow);
            padding: 40px;
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

        .header {
            display: flex;
            justify-content: space-between;
            align-items: center;
            margin-bottom: 30px;
            padding-bottom: 20px;
            border-bottom: 2px solid var(--border);
        }

        .header h1 {
            background: var(--primary-gradient);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            font-size: 2.5rem;
            font-weight: 700;
        }

        .btn-home {
            padding: 12px 24px;
            background: var(--primary-gradient);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 1rem;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
            text-decoration: none;
            display: inline-block;
        }

        .btn-home:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(37, 99, 235, 0.4);
        }

        .guide-content {
            background: var(--bg-secondary);
            border: 1px solid var(--border);
            border-radius: 12px;
            padding: 30px;
            max-height: 70vh;
            overflow-y: auto;
            line-height: 1.8;
        }

        .guide-content pre {
            background: var(--bg-primary);
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            border-left: 4px solid var(--primary-color);
            margin: 15px 0;
        }

        .guide-content h1 {
            color: var(--text-primary);
            font-size: 2rem;
            margin: 30px 0 15px 0;
            padding-bottom: 10px;
            border-bottom: 2px solid var(--border);
        }

        .guide-content h2 {
            color: var(--text-primary);
            font-size: 1.5rem;
            margin: 25px 0 12px 0;
        }

        .guide-content h3 {
            color: var(--text-secondary);
            font-size: 1.2rem;
            margin: 20px 0 10px 0;
        }

        .guide-content p {
            color: var(--text-secondary);
            margin: 10px 0;
        }

        .guide-content strong {
            color: var(--text-primary);
            font-weight: 600;
        }

        .guide-content code {
            background: var(--bg-primary);
            color: #3b82f6;
            padding: 2px 6px;
            border-radius: 4px;
            font-family: 'Consolas', monospace;
            font-size: 0.9em;
        }

        .guide-content::-webkit-scrollbar {
            width: 12px;
        }

        .guide-content::-webkit-scrollbar-track {
            background: var(--bg-primary);
            border-radius: 6px;
        }

        .guide-content::-webkit-scrollbar-thumb {
            background: var(--border);
            border-radius: 6px;
        }

        .guide-content::-webkit-scrollbar-thumb:hover {
            background: var(--primary-color);
        }

        .info-box {
            background: rgba(37, 99, 235, 0.1);
            border-left: 4px solid var(--primary-color);
            padding: 15px;
            margin: 20px 0;
            border-radius: 8px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>📖 User Guide</h1>
            <a href="/" class="btn-home">🏠 Back to Home</a>
        </div>
        
        <div class="info-box">
            <strong>💡 Tip:</strong> Use the scroll bar to navigate through the guide. Press Ctrl+F to search for specific topics.
        </div>
        
        <div class="guide-content">
''' + html_content + '''
        </div>
    </div>
</body>
</html>
'''
        
        return render_template_string(USER_GUIDE_TEMPLATE)
    except Exception as e:
        return f"Error loading user guide: {str(e)}"

if __name__ == '__main__':
    import sys
    
    # Only ask for port on first run (not on Flask reloader restart)
    if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
        # Ask user for port number
        print("\n" + "="*60)
        print("  CONVERTFLOW STUDIO - Server Configuration")
        print("="*60)
        
        default_port = 5001
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
        port = int(os.environ.get('FLASK_PORT', 5001))
    
    app.run(debug=True, port=port)
