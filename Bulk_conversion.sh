#!/bin/bash

FORMAT_DIR="D:/File_conversion/File_conversion/rushabh/automation/FILE_CONVERSION/bulk_conversion/RBS/format"
INPUT_DIR="D:/File_conversion/File_conversion/rushabh/automation/FILE_CONVERSION/bulk_conversion/RBS/input"
OUTPUT_DIR="D:/File_conversion/File_conversion/rushabh/automation/FILE_CONVERSION/bulk_conversion/RBS/output"
LOG_PATH="D:/File_conversion/File_conversion/rushabh/automation/FILE_CONVERSION/bulk_conversion/RBS/logCondtions.txt"
dowithcer_path="D:/File_conversion/File_conversion/rushabh/automation/FILE_CONVERSION/dowitcher.exe"
source="D:/File_conversion/File_conversion/rushabh/automation/FILE_CONVERSION/RBS/datamatch/source"
target="D:/File_conversion/File_conversion/rushabh/automation/FILE_CONVERSION/RBS/datamatch/target"

# # Function to log messages
# log_message() {
    # echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> script.log
# }
rm $source\/*	
rm $target\/*
# Color codes for console output
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# Function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> D:/File_conversion/File_conversion/rushabh/automation/FILE_CONVERSION/bulk_conversion/RBS/outputlog.txt
}

# Function to display error in red and log it
display_and_log_error() {
    echo -e "${RED}ERROR: $1${NC}"
    log_message "Error: $1"
}

# Function to display success in green and log it
display_and_log_success() {
    echo -e "${GREEN}SUCCESS: $1${NC}"
    log_message "$1"
}

# Log start time
log_message "Script started."
# # Log start time
# log_message "Script started."
export PATH="$PATH:/d/File_conversion/File_conversion/rushabh/automation/FILE_CONVERSION/"
# Loop through all .ff files in the format directory
for format_file in "$FORMAT_DIR"/*.ff; do
    # Extract the base name without extension
    base_name=$(basename "$format_file" .ff)
    
    # Construct the input file path
    input_file="$INPUT_DIR/$base_name.txt"
    
    # Check if the input file exists
    if [[ -f "$input_file" ]]; then
        # Construct the output file path
        output_file="$OUTPUT_DIR/$base_name.txt"
        
        # Run the conversion command
        $dowithcer_path --convert --code-page=CP0037 --format="$format_file" "$input_file" "$output_file" --log="$LOG_PATH"
		# Check if the command was successful
        if [[ $? -eq 0 ]]; then
            display_and_log_success "Conversion completed successfully for $base_name.txt"
        else
            display_and_log_error "Conversion failed for $base_name.txt"
		fi	
		cp $format_file $source
		cp $format_file $OUTPUT_DIR

		cp $input_file $source
		cp $output_file $target
		cp $format_file $target
       
    else
        display_and_log_error "input file $input_file not found for input file $base_name.ff."
    fi
done