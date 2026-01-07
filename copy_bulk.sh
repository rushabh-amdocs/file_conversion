#!/bin/bash

# Specify the folder path
folder_path="D:/File_conversion/File_conversion/rushabh/automation/FILE_CONVERSION/RBS/output"
distination_folder="D:\File_conversion\File_conversion\rushabh\automation\FILE_CONVERSION\bulk_conversion\RBS\format"

# Input file variable
INPUT_FILE="IGD.txt"

# Color codes for console output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log file for errors
ERROR_LOG="copylog.txt"

# Function to log error messages to file
log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$ERROR_LOG"
}

# Function to log messages to file
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$ERROR_LOG"
}

# Function to display error in red and log it
display_and_log_error() {
    echo -e "${RED}ERROR: $1${NC}"
    log_error "$1"
}

# Function to display success in green
display_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
}

# Function to display info in blue
display_info() {
    echo -e "${BLUE}INFO: $1${NC}"
}

# Function to display warning in yellow
display_warning() {
    echo -e "${YELLOW}WARNING: $1${NC}"
}

# Initialize counters
total_files=0
success_count=0
error_count=0

# Initialize/clear the error log
> "$ERROR_LOG"
log_message "Copy script started"
display_info "Starting file copy process..."

# Check if the input file exists
if [ ! -f "$INPUT_FILE" ]; then
  display_and_log_error "$INPUT_FILE not found!"
  exit 1
fi

# Check if source directory exists
if [ ! -d "$folder_path" ]; then
  display_and_log_error "Source directory not found: $folder_path"
  exit 1
fi

# Create destination directory if it doesn't exist
if [ ! -d "$distination_folder" ]; then
  mkdir -p "$distination_folder"
  display_info "Created destination directory: $distination_folder"
  log_message "Created destination directory: $distination_folder"
fi

# Read each line from the input file
while IFS=, read -r oldfilename newfilename; do
  # Trim any leading or trailing whitespace from filenames
  oldfilename=$(echo "$oldfilename" | xargs)
  newfilename=$(echo "$newfilename" | xargs)
  
  # Skip empty lines
  if [[ -z "$oldfilename" || -z "$newfilename" ]]; then
    continue
  fi
  
  ((total_files++))
  
  # Construct the full paths
  oldfilepath="$folder_path/$oldfilename"
  newfilepath="$distination_folder/$newfilename"
  # Check if the old file exists
  if [ -f "$oldfilepath" ]; then
    # Create a copy of the file with the new filename
    if cp "$oldfilepath" "$newfilepath"; then
      display_success "Copied $oldfilename to $newfilename"
      log_message "SUCCESS: Copied $oldfilepath to $newfilepath"
      ((success_count++))
    else
      display_and_log_error "Failed to copy $oldfilename to $newfilename"
      ((error_count++))
    fi
  else
    display_and_log_error "Source file $oldfilename not found at $oldfilepath"
    ((error_count++))
  fi
done < "$INPUT_FILE"

# Final summary
echo
display_info "========== OPERATION SUMMARY =========="
display_info "Total files processed: $total_files"
display_success "Successful copies: $success_count"
if [ $error_count -gt 0 ]; then
    display_and_log_error "Failed operations: $error_count"
else
    display_info "Failed operations: 0"
fi

log_message "Copy script completed - Total: $total_files, Success: $success_count, Errors: $error_count"

if [ $error_count -eq 0 ]; then
    display_success "All files have been copied successfully!"
else
    display_warning "Some files failed to copy. Check $ERROR_LOG for details."
fi

echo
display_info "Detailed log available at: $ERROR_LOG"