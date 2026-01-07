#!/bin/bash
# Bash script to upload application data to S3
# Parameters: APPLICATION_NAME S3_BUCKET S3_PATH_PREFIX LOCAL_BASE_PATH

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if parameters are provided
if [ $# -eq 4 ]; then
    # Parameters provided via command line
    application_name="$1"
    s3_bucket="$2"
    s3_path_prefix="$3"
    local_base_path="$4"
    
    echo -e "${YELLOW}===========================================================${NC}"
    echo -e "${GREEN}AWS S3 Upload Script${NC}"
    echo -e "${YELLOW}===========================================================${NC}"
    echo -e "${GREEN}Received Parameters:${NC}"
    echo -e "  Application Name: ${YELLOW}$application_name${NC}"
    echo -e "  S3 Bucket: ${YELLOW}$s3_bucket${NC}"
    echo -e "  S3 Path Prefix: ${YELLOW}$s3_path_prefix${NC}"
    echo -e "  Local Base Path: ${YELLOW}$local_base_path${NC}"
    echo ""
else
    # No parameters - prompt user for application name
    echo -e "${GREEN}Enter the application name: ${NC}"
    read application_name
    
    # Use default values
    s3_bucket="sandboxdee01s3att01"
    s3_path_prefix="file_Conversion"
    local_base_path="/d/File_conversion/File_conversion/Application_details"
fi

# Set local and S3 paths
local_path="$local_base_path/$application_name/Converted_data"
s3_path="s3://$s3_bucket/$s3_path_prefix/$application_name/"

echo -e "${GREEN}Uploading files from:${NC}"
echo -e "  Local: ${YELLOW}$local_path${NC}"
echo -e "  To S3: ${YELLOW}$s3_path${NC}"
echo ""

# Count files to be copied
file_count=$(find "$local_path" -type f | wc -l)
echo -e "${GREEN}Total files to copy: $file_count${NC}"

# Run AWS S3 cp command
if aws s3 cp "$local_path" "$s3_path" --recursive; then
    echo -e "${GREEN}Files copied successfully! Total files copied: $file_count${NC}"
else
    echo -e "${RED}File copy failed. Please check the paths and AWS credentials.${NC}"
fi
