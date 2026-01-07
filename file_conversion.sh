#!/bin/bash

chmod +x file_conversion.sh
chmod +x RoysEbcdicRecTypesV6.rexx
export PATH=$PATH:/d/File_conversion/File_conversion/rushabh/automation/FILE_CONVERSION/
# Function to rename the latest file in the folder
rename_latest_file() {
    folder_path="$1"
    new_name="$2"

    # Find the latest file in the folder
    latest_file=$(ls -t "$folder_path" | head -n 1)

    # Check if there are any files in the folder
    if [ -z "$latest_file" ]; then
        echo "No files found in the folder."
        return
    fi
    # Rename the file
    mv "$folder_path/$latest_file" "$folder_path/$new_name.ff"
    echo "Renamed '$latest_file' to '$new_name.ff'"
}
declare -A paths

# Read paths from the text file and assign to predefined variables

# Predefined variables
FORMAT_PATH=""
INPUT_PATH=""
OUTPUT_PATH=""
LOG_PATH=""
target=""
source=""
NOTEPAD_PATH=""
csv_file=""

# Read paths from the text file and assign to predefined variables
while IFS='=' read -r var_name folder_path; do
	if [ "$var_name" = "FORMAT_PATH" ]; then
        FORMAT_PATH="$folder_path"
		FORMAT_PATH=$(echo "$FORMAT_PATH" | tr -d '\r')
		
    elif [ "$var_name" = "INPUT_PATH" ]; then
        INPUT_PATH="$folder_path"
		INPUT_PATH=$(echo "$INPUT_PATH" | tr -d '\r')
    elif [ "$var_name" = "OUTPUT_PATH" ]; then
        OUTPUT_PATH="$folder_path"
		OUTPUT_PATH=$(echo "$OUTPUT_PATH" | tr -d '\r')
    elif [ "$var_name" = "LOG_PATH" ]; then
        LOG_PATH="$folder_path"
		LOG_PATH=$(echo "$LOG_PATH" | tr -d '\r')
    elif [ "$var_name" = "target" ]; then
        target="$folder_path"
		target=$(echo "$target" | tr -d '\r')
    elif [ "$var_name" = "CSV_file" ]; then
        csv_file="$csv_file"
		csv_file=$(echo "$csv_file" | tr -d '\r')
    elif [ "$var_name" = "source" ]; then
        source="$folder_path"
		source=$(echo "$source" | tr -d '\r')
    elif [ "$var_name" = "NOTEPAD_PATH" ]; then
        NOTEPAD_PATH="$folder_path"
		NOTEPAD_PATH=$(echo "$NOTEPAD_PATH" | tr -d '\r')
    fi
done < path.txt

# Example usage of the variables
echo "FORMAT_PATH:$FORMAT_PATH"
echo "INPUT_PATH: $INPUT_PATH"
echo "OUTPUT_PATH: $OUTPUT_PATH"
echo "LOG_PATH: $LOG_PATH"
echo "target: $target"
echo "source: $source"
echo "NOTEPAD_PATH: $NOTEPAD_PATH"


# folder_path="/C/rushabh/automation/FILE CONVERSION/FF_FILES/datamig/file-format"
# folder_path="/C/rushabh/automation/FILE CONVERSION/"
read -p "Enter the file name without .ff extension : " new_name
# read -p "Do you want to rename the .FF file(yes/no): " rename
# if [ "$rename" = "yes" ]; then
	# rename_latest_file "$FORMAT_PATH" "$new_name"
# fi
chmod +w "$(dirname "$FORMAT_PATH")"
chmod +w "$(dirname "$OUTPUT_PATH")"

# read -p "Do you want to modify the ff file (yes/no): " modify
# if [ "$modify" = "yes" ]; then
	# python File_modify.py $new_name
# fi

# Dowitcher command
dowitcher_execution() {
		
		local FORMAT_PATH="$1"
		local INPUT_PATH="$2"
		local OUTPUT_PATH="$3"
		local LOG_PATH="$4"
		local source="$5"
		local target="$6"
		local NOTEPAD_PATH="$7"
		local new_name="$8"
     



		DOWITCHER_CMD="dowitcher.exe --convert --code-page=CP0037 --format=\"$FORMAT_PATH/$new_name.ff\" \"$INPUT_PATH/$new_name.txt\" \"$OUTPUT_PATH/$new_name.txt\" --log=\"$LOG_PATH\""
		ADDITIONAL_CMD="dowitcher.exe --display --code-page=CP0037 --format=\"$FORMAT_PATH/$new_name.ff\" \"$OUTPUT_PATH/$new_name.txt\""

		# Execute the dowitcher command and check for errors
		if eval $DOWITCHER_CMD; then
			echo "Dowitcher command executed successfully." >> "$LOG_PATH"
		else
			echo "Error executing dowitcher command." >> "$LOG_PATH"	
			exit 1
		fi

		# Check if notepad files exist, if not create them
		if [ ! -f "$NOTEPAD_PATH" ]; then
			touch "$NOTEPAD_PATH"
		fi
		# Convert paths to Windows format with single backslashes
		CMD_FORMAT_PATH=$(echo $FORMAT_PATH | sed 's|/|\\|g')
		CMD_INPUT_PATH=$(echo $INPUT_PATH | sed 's|/|\\|g')
		CMD_OUTPUT_PATH=$(echo $OUTPUT_PATH | sed 's|/|\\|g')
		CMD_LOG_PATH=$(echo $LOG_PATH | sed 's|/|\\|g')

		# Append the dowitcher commands to the notepad files
		echo "dowitcher.exe --convert --code-page=CP0037 --format=\"$CMD_FORMAT_PATH\\$new_name.ff\" \"$CMD_INPUT_PATH\\$new_name.txt\" \"$CMD_OUTPUT_PATH\\$new_name.txt\" --log=\"$CMD_LOG_PATH\"" >> "$NOTEPAD_PATH"
		echo "dowitcher.exe --display --code-page=CP0037 --format=\"$CMD_FORMAT_PATH\\$new_name.ff\" \"$CMD_OUTPUT_PATH\\$new_name.txt\"" >> "$NOTEPAD_PATH"
		echo "dowitcher.exe --display --source --include-hex --include-field-number --include-field-offset --trace-format-selection --code-page=CP0037 --format=\"$CMD_FORMAT_PATH\\$new_name.ff\" \"$CMD_INPUT_PATH\\$new_name.txt\"" >> "$NOTEPAD_PATH"


		# Copy files to the specified directories
	    rm $source\/*	
		rm $target\/*
		cp "$OUTPUT_PATH/$new_name.txt" $target
		cp "$FORMAT_PATH/$new_name.ff" $target
		cp "$FORMAT_PATH/$new_name.ff" $source
		cp "$INPUT_PATH/$new_name.txt" $source
		cp "$FORMAT_PATH/$new_name.ff" $OUTPUT_PATH
}



#Dowitcher command for particular record 
dowitcher_execution_records() {
		
		local FORMAT_PATH="$1"
		local INPUT_PATH="$2"
		local OUTPUT_PATH="$3"
		local LOG_PATH="$4"
		local source="$5"
		local target="$6"
		local NOTEPAD_PATH="$7"
		local new_name="$8"
		local records="$9"
		DOWITCHER_CMD="dowitcher.exe --convert --code-page=CP0037 --format=\"$FORMAT_PATH/$new_name.ff\" \"$INPUT_PATH/$new_name.txt\" \"$OUTPUT_PATH/$new_name.txt\" --log=\"$LOG_PATH\" --records="$records""

		# Execute the dowitcher command and check for errors
		if eval $DOWITCHER_CMD; then
			echo "Dowitcher command executed successfully." >> "$LOG_PATH"
		else
			echo "Error executing dowitcher command." >> "$LOG_PATH"	
			exit 1
		fi

		# Copy files to the specified directories
		#rm $source\/*	
		#rm $target\/*
		cp "$OUTPUT_PATH/$new_name.txt" $target
		cp "$FORMAT_PATH/$new_name.ff" $target
		cp "$FORMAT_PATH/$new_name.ff" $source
		cp "$INPUT_PATH/$new_name.txt" $source
		cp "$FORMAT_PATH/$new_name.ff" $OUTPUT_PATH
}

# read -p "Do you want to run dowitcher command the the .FF file(yes/no): " dowit

# if [ "$dowit" = "yes" ]; then
	# dowitcher_execution "$FORMAT_PATH" "$INPUT_PATH" "$OUTPUT_PATH" "$LOG_PATH" "$source" "$target" "$NOTEPAD_PATH" "$new_name"
# fi


		
# Dowitcher display
dowitcher_display(){
	local FORMAT_PATH="$1"
	local OUTPUT_PATH="$2"
	local records="$3"
	local new_name="$4"
	display_command="dowitcher.exe --display --code-page=CP0037 --format=\"$FORMAT_PATH/$new_name.ff\" \"$OUTPUT_PATH/$new_name.txt\" --records="$records""
	if eval $display_command; then
			echo "Dowitcher command executed successfully." >> "$LOG_PATH"
		else
			echo "Error executing dowitcher command." >> "$LOG_PATH"	
			exit 1
		fi
}
dowitcher_display_with_hex(){
	local FORMAT_PATH="$1"
	local OUTPUT_PATH="$2"
	local records="$3"
	local new_name="$4"
	display_command="dowitcher.exe --display --code-page=CP0037 --format=\"$FORMAT_PATH/$new_name.ff\" \"$OUTPUT_PATH/$new_name.txt\" --records="$records" --include-hex "  
	if eval $display_command; then
			echo "Dowitcher command executed successfully." >> "$LOG_PATH"
		else
			echo "Error executing dowitcher command." >> "$LOG_PATH"	
			exit 1
		fi
}

dowitcher_display_input_with_hex(){
	local FORMAT_PATH="$1"
	local INPUT_PATH="$2"
	local records="$3"
	local new_name="$4"
	display_command="dowitcher.exe --display --source --include-hex --include-field-number --include-field-offset  --code-page=CP0037 --format=\"$FORMAT_PATH/$new_name.ff\" \"$INPUT_PATH/$new_name.txt\" --records="$records" --include-hex "  
	if eval $display_command; then
			echo "Dowitcher command executed successfully." >> "$LOG_PATH"
		else
			echo "Error executing dowitcher command." >> "$LOG_PATH"	
			exit 1
		fi
}

# read -p "Do you want to run display command the the .FF file(yes/no): " dis

# if [ "$dis" = "yes" ]; then
		# read -p "Enter no of records for display:"  records
		# dowitcher_display "$FORMAT_PATH" "$OUTPUT_PATH" "$records" "$new_name"
# fi

while true; do
    echo "Choose an option:"
    echo "1. Rename the .FF file"
    echo "2. Modify the .FF file"
    echo "3. Run dowitcher command on the .FF file"
    echo "4. Run command to display output on the .FF file"
	echo "5. Run Roys tool"
	echo "6. Run command to display output with hex on the .FF file"
	echo "7. Run dowitcher command on the .FF file for conversion of particular records"
	echo "8. Run command to display input with hex on the .FF file "

    read -p "Enter your choice (1/2/3/4/5/6/7/8): " choice

    case "$choice" in
        1)
            rename_latest_file "$FORMAT_PATH" "$new_name"
            ;;
        2)
            rename_latest_file "$FORMAT_PATH" "$new_name"
			python File_modify.py $new_name
            ;;
        3)
            dowitcher_execution "$FORMAT_PATH" "$INPUT_PATH" "$OUTPUT_PATH" "$LOG_PATH" "$source" "$target" "$NOTEPAD_PATH" "$new_name"
            ;;
        4)
		    read -p "Enter no of records for display:"  records
            dowitcher_display "$FORMAT_PATH" "$OUTPUT_PATH" "$records" "$new_name"
            ;;
		5)
			rexx RoysEbcdicRecTypesV6.rexx
			;;
		6)
		    read -p "Enter no of records for display:"  records
            dowitcher_display_with_hex "$FORMAT_PATH" "$OUTPUT_PATH" "$records" "$new_name"
            ;;
        7)
		    read -p "Enter no of records that you want to convert :"  records
            dowitcher_execution_records "$FORMAT_PATH" "$INPUT_PATH" "$OUTPUT_PATH" "$LOG_PATH" "$source" "$target" "$NOTEPAD_PATH" "$new_name" "$records"
            ;;
		8)
		    read -p "Enter no of records that you want to display :"  records
            dowitcher_display_input_with_hex "$FORMAT_PATH" "$INPUT_PATH" "$records" "$new_name"
            ;;
        *)
            echo "Invalid choice. Please select 1, 2, 3,4,5,6,7or 8."
            ;;
    esac

    read -p "Do you want to select another option? (yes/no): " again
    if [ "$again" != "yes" ]; then
        break
    fi
done
