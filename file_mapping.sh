#!/bin/bash
 
# Define the source and destination directories
SOURCE_DIR="D:\File_conversion\File_conversion\Rupali\ME\output"
DESTINATION_DIR="D:\File_conversion\File_conversion\Application_details\ME\converted_data"
CSV_FILE="D:/File_conversion/File_conversion/Rupali/ME.csv"

# Color codes for console output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Log file for errors and operations
LOG_FILE="file_move_log.txt"

# Function to log messages to file
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> "$LOG_FILE"
}

# Function to log error messages to file
log_error() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: $1" >> "$LOG_FILE"
}

# Function to display and log error in red
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

# Initialize/clear the log file
> "$LOG_FILE"
log_message "File move script started"
display_info "Starting file organization process..."

# Check if CSV file exists
if [ ! -f "$CSV_FILE" ]; then
    display_and_log_error "CSV file not found: $CSV_FILE"
    exit 1
fi

# Check if source directory exists
if [ ! -d "$SOURCE_DIR" ]; then
    display_and_log_error "Source directory not found: $SOURCE_DIR"
    exit 1
fi

# Create destination directory if it doesn't exist
if [ ! -d "$DESTINATION_DIR" ]; then
    mkdir -p "$DESTINATION_DIR"
    display_info "Created destination directory: $DESTINATION_DIR"
    log_message "Created destination directory: $DESTINATION_DIR"
fi

# Initialize counters
total_files=0
success_count=0
error_count=0

# Read the CSV file into an array to avoid subshell issues
mapfile -t csv_lines < <(tail -n +2 "$CSV_FILE")

# Process each line
for line in "${csv_lines[@]}"; do
    # Parse CSV line
    IFS=',' read -r FOLDER_NAME FILE_NAME DEST_FILE_NAME <<< "$line"
    
    # Trim whitespace
    FOLDER_NAME=$(echo "$FOLDER_NAME" | xargs)
    FILE_NAME=$(echo "$FILE_NAME" | xargs)
    DEST_FILE_NAME=$(echo "$DEST_FILE_NAME" | xargs)
    
    # Skip empty lines
    if [[ -z "$FOLDER_NAME" || -z "$FILE_NAME" || -z "$DEST_FILE_NAME" ]]; then
        continue
    fi
    
    ((total_files++))
 
    # Create destination folders if they don't exist
    mkdir -p "$DESTINATION_DIR/$FOLDER_NAME/.ff"
    mkdir -p "$DESTINATION_DIR/$FOLDER_NAME/Converted Files"
 
    # Copy .ff files
    if [[ "$FILE_NAME" == *.ff ]]; then
        source_file="$SOURCE_DIR/$FILE_NAME"
        dest_file="$DESTINATION_DIR/$FOLDER_NAME/.ff/$DEST_FILE_NAME"
        
        if [ -f "$source_file" ]; then
            if cp "$source_file" "$dest_file"; then
                display_success "Copied .ff file: $FILE_NAME → $FOLDER_NAME/.ff/$DEST_FILE_NAME"
                log_message "SUCCESS: Copied $source_file to $dest_file"
                ((success_count++))
            else
                display_and_log_error "Failed to copy .ff file: $FILE_NAME to $FOLDER_NAME/.ff/$DEST_FILE_NAME"
                ((error_count++))
            fi
        else
            display_and_log_error "Source .ff file not found: $source_file"
            ((error_count++))
        fi
    fi
 
    # Copy .txt files
    if [[ "$FILE_NAME" == *.txt ]]; then
        source_file="$SOURCE_DIR/$FILE_NAME"
        dest_file="$DESTINATION_DIR/$FOLDER_NAME/Converted Files/$DEST_FILE_NAME"
        
        if [ -f "$source_file" ]; then
            if cp "$source_file" "$dest_file"; then
                display_success "Copied .txt file: $FILE_NAME → $FOLDER_NAME/Converted Files/$DEST_FILE_NAME"
                log_message "SUCCESS: Copied $source_file to $dest_file"
                ((success_count++))
            else
                display_and_log_error "Failed to copy .txt file: $FILE_NAME to $FOLDER_NAME/Converted Files/$DEST_FILE_NAME"
                ((error_count++))
            fi
        else
            display_and_log_error "Source .txt file not found: $source_file"
            ((error_count++))
        fi
    fi
    
    # Handle files that are neither .ff nor .txt
    if [[ "$FILE_NAME" != *.ff && "$FILE_NAME" != *.txt ]]; then
        display_warning "Skipped unsupported file type: $FILE_NAME"
        log_message "WARNING: Skipped unsupported file type: $FILE_NAME"
    fi
done
 
# Final summary
echo
display_info "========== OPERATION SUMMARY =========="
display_info "Total files processed: $total_files"
display_success "Successful operations: $success_count"
if [ $error_count -gt 0 ]; then
    display_and_log_error "Failed operations: $error_count"
else
    display_info "Failed operations: 0"
fi

log_message "File move script completed - Total: $total_files, Success: $success_count, Errors: $error_count"

if [ $error_count -eq 0 ]; then
    display_success "All files have been moved successfully!"
else
    display_warning "Some files failed to move. Check $LOG_FILE for details."
fi

echo
display_info "Detailed log available at: $LOG_FILE"