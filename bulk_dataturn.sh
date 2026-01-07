#!/bin/bash

# Read only required paths from the text file
while IFS='=' read -r var_name folder_path; do
    case "$var_name" in
        "application")
            output_path=$(echo "$folder_path" | tr -d '\r')
            ;;
        "expfd")
            expfd=$(echo "$folder_path" | tr -d '\r')
            ;;
    esac
done < path.txt

# Define variables
REPO_NAME="$output_path/repo/repoCBR2"
IMPORT_SCHEMA_TYPE="FILE2FILE"
GENERATION_TARGET="DowitcherFileFormat"
GENERATION_OUTPUT_DIR="$output_path/FF_FILES/"
CONFIG_FILE="rushabh.configuration"

# Define the path to dataturnw.exe
DATATURNW_PATH="C:/Program Files/Anubex/DataTurn/bin/dataturn.exe"

export PATH="$PATH:/c/Program Files/Anubex/DataTurn/bin/"

# Process each .expfd file in the expfd directory
for expfd_file in "$expfd"/*.expfd; do
    # Extract the file name without the extension
    expfd_name=$(basename "$expfd_file" .expfd)

    IMPORT_SCHEMA_NAME="$expfd_name"
    IMPORT_FILE="$expfd_name.expfd"  # Pass only the filename, not the full path

    # Run the first command
    "$DATATURNW_PATH" --repository-name $REPO_NAME --import-data --input-dir $expfd --import-schema-type $IMPORT_SCHEMA_TYPE --import-schema-name $IMPORT_SCHEMA_NAME $IMPORT_FILE --initialize --create-repository --configuration-file $CONFIG_FILE

    # Run the second command
    "$DATATURNW_PATH" --generate --repository-name $REPO_NAME --generation-target $GENERATION_TARGET --generation-output-directory $GENERATION_OUTPUT_DIR --configuration-file $CONFIG_FILE

    # Remove the repository after processing the file
    rm -rf $REPO_NAME
done