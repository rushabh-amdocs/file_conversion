import re
from datetime import datetime
import os
 
def remove_88_and_values(copybook_content):
    keep_lines = []
    skip_mode = False
 
    lines = copybook_content.splitlines()
 
    for i, line in enumerate(lines):
        # Remove values in columns 01 to 06
        line = ' ' * 6 + line[6:]
        # Truncate the line after column 72
        line = line[:72]
        stripped = line[7:72].lstrip()  # Check only between columns 8 to 72
 
        # Check if line starts with level 88
        if re.match(r'^88\b', stripped):
            skip_mode = True
            continue
 
        # If skipping, continue skipping until a new valid level number is found
        if skip_mode:
            if re.match(r'^\s*(01|02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42|43|44|45|46|47|48|49|77)\b', stripped):
                skip_mode = False
            else:
                continue
 
        if not skip_mode:
            keep_lines.append(line)
 
    return '\n'.join(keep_lines)

def adjust_01_level(copybook_content):
    """
    Moves lines starting with '01' to the 8th column if they are not already there.
    """
    lines = copybook_content.splitlines()
    adjusted_lines = []

    for line in lines:
        # Skip comment lines
        if line.strip().startswith('*') or re.match(r'^\d{6}\*', line.strip()):
            adjusted_lines.append(line)
            continue

        # Check if the line contains '01' starting at a position greater than 8
        stripped_line = line.lstrip()
        if stripped_line.startswith('01') and not line[7:9].strip() == '01':
            # Move the entire line to start at the 8th column
            adjusted_line = ' ' * 7 + stripped_line
            adjusted_lines.append(adjusted_line)
        else:
            adjusted_lines.append(line)

    return '\n'.join(adjusted_lines) 
def process_copybooks(copybook_names, output_path):
    def extract_columns(copybook_content):
        extracted_lines = []
        for line in copybook_content.splitlines():
            if not line.strip().startswith('*') and not re.match(r'^\d{6}\*', line.strip()):
                # Check if there is a value at column 8 and replace it with '01' if it's not '01'
                if line[7:9].strip():
                    modified_line = '01' + line[9:72]
                else:
                    modified_line = line[7:72]
                extracted_lines.append(modified_line)
        return extracted_lines
 
    def find_first_01_level_value(extracted_lines):
        for line in extracted_lines:
            if line[:2] == '01':  # Check if the line starts with '01'
                return line[4:65].lstrip().split()[0].rstrip('.')  # Ignore leading spaces and extract the first word
        return None  # Return None if no line starts with '01'
 
 
    def check_and_replace_values(copybook_content):
        lines = copybook_content.splitlines()
        modified_lines = []
        lowest_column_position = None  # Variable to store the lowest column position

        for line in lines:
            # Keep the if statement as it is for comment part
            if not line.strip().startswith('*') and not re.match(r'^\d{6}\*', line.strip()):
                # Check if '01' is present at the 8th column
                if line[7:9].strip() == '01':
                    return lines  # Keep all data as it is and exit the function

                # Focus on columns 8 to 72
                stripped = line[7:72].lstrip()
                match = re.match(r'^(02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42|43|44|45|46|47|48|49|77)\b', stripped)
                if match:
                    # Note the starting column position
                    column_position = line.find(match.group(0))
                    # Ignore positions between columns 01 to 07
                    if column_position >= 7 and (lowest_column_position is None or column_position < lowest_column_position):
                        lowest_column_position = column_position

        # Replace values at the lowest column position and its next column with '01'
        for line in lines:
            if not line.strip().startswith('*') and not re.match(r'^\d{6}\*', line.strip()):
                if lowest_column_position is not None:
                    # Check if the line starts at the lowest column position
                    stripped = line[7:72].lstrip()
                    match = re.match(r'^(02|03|04|05|06|07|08|09|10|11|12|13|14|15|16|17|18|19|20|21|22|23|24|25|26|27|28|29|30|31|32|33|34|35|36|37|38|39|40|41|42|43|44|45|46|47|48|49|77)\b', stripped)
                    if match and line.find(match.group(0)) == lowest_column_position:
                        # Replace values at the lowest column position and its next column with '01'
                        modified_line = line[:7] + '01' + line[lowest_column_position + 2:]
                        modified_lines.append(modified_line)
                    else:
                        modified_lines.append(line)
                else:
                    modified_lines.append(line)
            else:
                modified_lines.append(line)

        return modified_lines
 
    all_extracted_data = []
    first_01_level_value = None
    header_lines = []
 
    for index, copybook_name in enumerate(copybook_names):
        try:
            with open(copybook_name, 'r') as f:
                copybook_content = f.read()
        except FileNotFoundError:
            print(f"Error: The file '{copybook_name}' was not found.")
            continue
        except IOError:
            print(f"Error: An error occurred while reading the file '{copybook_name}'.")
            continue
 
       # Remove level 88 and its values before processing
        filtered_content = remove_88_and_values(copybook_content)

    # Adjust the position of '01' level to the 8th column
        adjusted_content = adjust_01_level(filtered_content)
 
        modified_content = check_and_replace_values(adjusted_content)
        extracted_data = extract_columns('\n'.join(modified_content))
        all_extracted_data.extend(extracted_data)
 
        if index == 0:
            first_01_level_value = find_first_01_level_value(extracted_data)
            current_timestamp = datetime.now().strftime("%a %b %d %H:%M:%S %Z %Y")
            header_lines = [
                f"      * Generated by python on {current_timestamp}",
                f"      * Original source file: {os.path.basename(copybook_name)}",
                f"      * Original SELECT source file: {os.path.basename(copybook_name)}",
                f"        SELECT {os.path.splitext(os.path.basename(copybook_name))[0]} ASSIGN TO RA-G099."
            ]
 
    output_filename = os.path.join(output_path, f"{os.path.splitext(os.path.basename(copybook_name))[0]}.expfd")
    try:
        with open(output_filename, 'w') as f:
            for line in header_lines:
                f.write(line + '\n')
            for line in all_extracted_data:
                formatted_line = ' ' * 7 + line.ljust(65)
                f.write(formatted_line + '\n')
    except IOError:
        print(f"Error: An error occurred while writing to the file '{output_filename}'.")
        return
 
    print(f"Your expfd has been created from '{output_filename}'")
 
def main():
    # Retrieve paths from path.txt
    variables = {}
    with open('path.txt', 'r') as file:
        for line in file:
            name, value = line.strip().split('=')
            variables[name] = value
 
    expfd = variables['expfd']
    copybook_path = variables['copybook']
 
    # Prompt user for copybook names
    copybook_names_input = input("Enter the copybook names (comma-separated for multiple files): ")
    copybook_names = [os.path.join(copybook_path, name.strip()) for name in copybook_names_input.split(',')]
    process_copybooks(copybook_names, expfd)
 
if __name__ == "__main__":
    main()
 