#!/bin/bash

# Prompt the user for the folder name
echo "Please enter the folder name:"
read folder_name

# Create the main folder and subfolders
mkdir -p "$folder_name/datamatch/source"
mkdir -p "$folder_name/datamatch/target"
mkdir -p "$folder_name/input"
mkdir -p "$folder_name/expfd"
mkdir -p "$folder_name/output"
mkdir -p "$folder_name/FF_FILES/datamig/file-format"
mkdir -p "$folder_name/copybook"

echo "Folders created successfully!"
