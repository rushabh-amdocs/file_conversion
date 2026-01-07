#!/usr/bin/env python3
"""
Multi-folder File Copy Script with Comprehensive Logging

This script reads file names from a text file, searches for them across a 
source folder and its subdirectories, and copies them to a destination folder 
with detailed logging.
"""

import os
import shutil
import datetime
from pathlib import Path

# =============================================================================
# CONFIGURATION - MODIFY THESE VALUES
# =============================================================================
FILE_LIST_PATH = r"file_list.txt"
SOURCE_FOLDER = r"D:\Wave1\Drop4\BAD_DEBT\RL81B25L"  # Single source folder with nested subfolders
DESTINATION_FOLDER = r"D:\File_conversion\File_conversion\rushabh\automation\FILE_CONVERSION\bulk_conversion\badebt\input"
#DESTINATION_FOLDER = r"D:/File_conversion/File_conversion/rushabh/automation/FILE_CONVERSION/UWFE/input"
LOG_FILE = r"file_copy_log.txt"
EMPTY_MISSING_LOG = os.path.join(DESTINATION_FOLDER, "empty_and_missing_files.txt")

# =============================================================================
# COLOR CODES FOR CONSOLE OUTPUT
# =============================================================================
class Colors:
    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    END = '\033[0m'

def log_and_print(message, color=None, log_only=False):
    """Log message to file and optionally print to console with color"""
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_message = f"[{timestamp}] {message}"
    
    # Write to log file
    with open(LOG_FILE, 'a', encoding='utf-8') as log_file:
        log_file.write(log_message + '\n')
    
    # Print to console if not log_only
    if not log_only:
        if color:
            print(f"{color}{message}{Colors.END}")
        else:
            print(message)

def initialize_log():
    """Initialize the log file with header"""
    # Create destination folder if it doesn't exist
    os.makedirs(DESTINATION_FOLDER, exist_ok=True)
    
    # Clear and initialize log file
    with open(LOG_FILE, 'w', encoding='utf-8') as log_file:
        log_file.write("="*80 + '\n')
        log_file.write("MULTI-FOLDER FILE COPY SCRIPT LOG\n")
        log_file.write("="*80 + '\n')
        log_file.write(f"Started at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        log_file.write(f"File list: {FILE_LIST_PATH}\n")
        log_file.write(f"Destination: {DESTINATION_FOLDER}\n")
        log_file.write(f"Source folder (recursive): {SOURCE_FOLDER}\n")
        log_file.write("="*80 + '\n\n')

def read_file_list():
    """Read the list of files from the input text file"""
    if not os.path.exists(FILE_LIST_PATH):
        log_and_print(f"ERROR: File list not found: {FILE_LIST_PATH}", Colors.RED)
        return []
    
    try:
        with open(FILE_LIST_PATH, 'r', encoding='utf-8') as file:
            files = [line.strip() for line in file.readlines() if line.strip()]
        
        log_and_print(f"INFO: Read {len(files)} file names from {FILE_LIST_PATH}", Colors.BLUE)
        return files
    
    except Exception as e:
        log_and_print(f"ERROR: Failed to read file list: {str(e)}", Colors.RED)
        return []

def find_file_in_folders(filename):
    """Search for a file recursively in the source folder and all subdirectories"""
    found_files = []
    
    if not os.path.exists(SOURCE_FOLDER):
        log_and_print(f"ERROR: Source folder does not exist: {SOURCE_FOLDER}", Colors.RED, log_only=True)
        return found_files
    
    try:
        log_and_print(f"INFO: Searching for '{filename}' in {SOURCE_FOLDER} and all subdirectories...", Colors.CYAN, log_only=True)
        
        # Search recursively through all directories and subdirectories
        for root, dirs, files in os.walk(SOURCE_FOLDER):
            if filename in files:
                full_path = os.path.join(root, filename)
                found_files.append(full_path)
                log_and_print(f"INFO: Found '{filename}' at: {full_path}", Colors.CYAN, log_only=True)
    
    except Exception as e:
        log_and_print(f"ERROR: Failed to search in folder {SOURCE_FOLDER}: {str(e)}", Colors.RED, log_only=True)
    
    return found_files

def check_file_status(file_path):
    """Check if file exists and is not empty"""
    if not os.path.exists(file_path):
        return "missing"
    
    try:
        file_size = os.path.getsize(file_path)
        if file_size == 0:
            return "empty"
        else:
            return "valid"
    except Exception:
        return "error"

def copy_file_to_destination(source_path, filename):
    """Copy file to destination folder"""
    try:
        destination_path = os.path.join(DESTINATION_FOLDER, filename)
        
        # Check if file already exists and log it
        if os.path.exists(destination_path):
            log_and_print(f"INFO: File already exists in destination, replacing: {filename}", Colors.CYAN, log_only=True)
        
        # Copy file (this will replace if it already exists)
        shutil.copy2(source_path, destination_path)
        
        return True, destination_path
    
    except Exception as e:
        log_and_print(f"ERROR: Failed to copy file: {str(e)}", Colors.RED, log_only=True)
        return False, None

def save_empty_and_missing_files(empty_file_list, missing_file_list):
    """Save empty and missing file names to a single text file with separate sections"""
    
    try:
        with open(EMPTY_MISSING_LOG, 'w', encoding='utf-8') as log_file:
            # Write empty files section
            log_file.write("EMPTY FILES\n")
            log_file.write("=" * 50 + "\n\n")
            if empty_file_list:
                for filename in empty_file_list:
                    log_file.write(f"{filename}\n")
            else:
                log_file.write("No empty files found.\n")
            
            # Add separator between sections
            log_file.write("\n\n")
            
            # Write missing files section
            log_file.write("MISSING FILES\n")
            log_file.write("=" * 50 + "\n\n")
            if missing_file_list:
                for filename in missing_file_list:
                    log_file.write(f"{filename}\n")
            else:
                log_file.write("No missing files found.\n")
        
        log_and_print(f"INFO: Empty and missing files list saved to: {EMPTY_MISSING_LOG}", Colors.CYAN, log_only=True)
    except Exception as e:
        log_and_print(f"ERROR: Failed to save empty and missing files list: {str(e)}", Colors.RED, log_only=True)

def process_files():
    """Main processing function"""
    # Initialize counters
    total_files = 0
    found_files = 0
    copied_files = 0
    missing_files = 0
    empty_files = 0
    error_files = 0
    
    # Initialize lists to track empty and missing files
    empty_file_list = []
    missing_file_list = []
    
    # Read file list
    file_list = read_file_list()
    if not file_list:
        return
    
    total_files = len(file_list)
    log_and_print(f"INFO: Starting to process {total_files} files...", Colors.BLUE)
    
    # Process each file
    for i, filename in enumerate(file_list, 1):
        log_and_print(f"\n[{i}/{total_files}] Processing: {filename}", Colors.PURPLE)
        
        # Find file in source folders
        found_paths = find_file_in_folders(filename)
        
        if not found_paths:
            # File not found in any folder
            missing_files += 1
            missing_file_list.append(filename)
            log_and_print(f"MISSING: {filename} - File not found in any source folder", Colors.RED)
            continue
        
        found_files += 1
        
        # If multiple copies found, use the first one and log others
        if len(found_paths) > 1:
            log_and_print(f"INFO: Multiple copies found for {filename}:", Colors.YELLOW, log_only=True)
            for path in found_paths:
                log_and_print(f"  - {path}", Colors.YELLOW, log_only=True)
            log_and_print(f"INFO: Using first copy: {found_paths[0]}", Colors.YELLOW, log_only=True)
        
        source_path = found_paths[0]
        
        # Check file status
        status = check_file_status(source_path)
        
        if status == "empty":
            empty_files += 1
            empty_file_list.append(filename)
            log_and_print(f"EMPTY: {filename} - File is empty (0 bytes)", Colors.YELLOW)
            log_and_print(f"INFO: Source path: {source_path}", Colors.CYAN, log_only=True)
            continue
        
        elif status == "error":
            error_files += 1
            log_and_print(f"ERROR: {filename} - Cannot read file status", Colors.RED)
            continue
        
        # File is valid, copy it
        success, dest_path = copy_file_to_destination(source_path, filename)
        
        if success:
            copied_files += 1
            file_size = os.path.getsize(source_path)
            log_and_print(f"SUCCESS: {filename} - Copied successfully ({file_size} bytes)", Colors.GREEN)
            log_and_print(f"INFO: Source: {source_path}", Colors.CYAN, log_only=True)
            log_and_print(f"INFO: Destination: {dest_path}", Colors.CYAN, log_only=True)
        else:
            error_files += 1
            log_and_print(f"ERROR: {filename} - Copy operation failed", Colors.RED)
    
    # Save empty and missing files to single text file
    save_empty_and_missing_files(empty_file_list, missing_file_list)
    
    # Print final summary
    print("\n" + "="*80)
    log_and_print("OPERATION SUMMARY:", Colors.BOLD)
    log_and_print(f"Total files requested: {total_files}", Colors.BLUE)
    log_and_print(f"Files found: {found_files}", Colors.CYAN)
    log_and_print(f"Files copied successfully: {copied_files}", Colors.GREEN)
    log_and_print(f"Missing files: {missing_files}", Colors.RED)
    log_and_print(f"Empty files: {empty_files}", Colors.YELLOW)
    log_and_print(f"Error files: {error_files}", Colors.RED)
    print("="*80)
    
    log_and_print(f"\nScript completed at: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", Colors.BLUE)
    log_and_print(f"Detailed log saved to: {LOG_FILE}", Colors.CYAN)
    
    # Show information about the file created
    if empty_files > 0 or missing_files > 0:
        log_and_print(f"Empty and missing files list saved to: {EMPTY_MISSING_LOG}", Colors.CYAN)

def get_folder_statistics():
    """Get statistics about the folder structure"""
    total_dirs = 0
    total_files = 0
    max_depth = 0
    
    try:
        for root, dirs, files in os.walk(SOURCE_FOLDER):
            total_dirs += 1
            total_files += len(files)
            level = root.replace(SOURCE_FOLDER, '').count(os.sep)
            max_depth = max(max_depth, level)
        
        return total_dirs, total_files, max_depth
    except Exception:
        return 0, 0, 0

def show_complete_folder_structure():
    """Show complete folder structure without depth limitation"""
    print(f"\n{Colors.BLUE}📁 Complete folder structure (all levels):{Colors.END}")
    try:
        folder_count = 0
        for root, dirs, files in os.walk(SOURCE_FOLDER):
            level = root.replace(SOURCE_FOLDER, '').count(os.sep)
            indent = '  ' * level
            folder_name = os.path.basename(root) if level > 0 else os.path.basename(SOURCE_FOLDER)
            print(f"{indent}{folder_name}/ ({len(files)} files, {len(dirs)} subdirs)")
            folder_count += 1
            
            # Limit display for very large structures
            if folder_count > 50:
                print(f"{indent}... (showing first 50 folders, but search will cover ALL folders)")
                break
                
    except Exception as e:
        print(f"{Colors.YELLOW}⚠️  Could not show folder structure: {e}{Colors.END}")

def main():
    """Main function"""
    print("="*80)
    print(f"{Colors.BOLD}🔧 MULTI-FOLDER FILE COPY SCRIPT{Colors.END}")
    print("="*80)
    
    # Initialize log
    initialize_log()
    
    # Validate configuration
    print(f"📂 File list: {FILE_LIST_PATH}")
    print(f"📁 Destination: {DESTINATION_FOLDER}")
    print(f"📂 Source folder (recursive): {SOURCE_FOLDER}")
    print(f"📋 Log file: {LOG_FILE}")
    
    # Check if source folder exists
    if not os.path.exists(SOURCE_FOLDER):
        print(f"{Colors.RED}❌ ERROR: Source folder not found: {SOURCE_FOLDER}{Colors.END}")
        return
    
    # Check if file list exists
    if not os.path.exists(FILE_LIST_PATH):
        print(f"{Colors.RED}❌ ERROR: File list not found: {FILE_LIST_PATH}{Colors.END}")
        return
    
    # Get folder statistics
    total_dirs, total_files, max_depth = get_folder_statistics()
    print(f"\n{Colors.CYAN}📊 Folder Statistics:{Colors.END}")
    print(f"   Total directories to search: {total_dirs}")
    print(f"   Total files in source: {total_files}")
    print(f"   Maximum folder depth: {max_depth} levels")
    
    # Automatically show complete folder structure
    #show_complete_folder_structure()
    
    # Start processing
    print(f"\n{Colors.GREEN}🚀 Starting file processing across ALL {total_dirs} directories...{Colors.END}")
    process_files()

if __name__ == "__main__":
    main()
