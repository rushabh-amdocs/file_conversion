import os
import csv
import sys


# Function to rename fillers in the XML content
def rename_fillers(lines):
    filler_count = 1
    modified_lines = []
    for line in lines:
        if 'name="FILLER"' in line:
            modified_lines.append(line.replace('name="FILLER"', f'name="FILLER{filler_count}"'))
            filler_count += 1
        else:
            modified_lines.append(line)
    return modified_lines


# Function to allow blanks in the XML content
def allow_blanks(lines):
    modified_lines = []
    for line in lines:
        if 'type="PS"' in line:
            modified_lines.append(line.replace('type="PS"', 'type="PS" allow-blanks="yes"'))
        elif 'type="NU"' in line:
            modified_lines.append(line.replace('type="NU"', 'type="NU" allow-blanks="yes"'))
        elif 'type="NUE"' in line:
            modified_lines.append(line.replace('type="NUE"', 'type="NUE" allow-blanks="yes"'))
        elif 'type="NS"' in line:
            modified_lines.append(line.replace('type="NS"', 'type="NSE" allow-blanks="yes"'))
        elif 'type="NSE"' in line:
            modified_lines.append(line.replace('type="NSE"', 'type="NSE" allow-blanks="yes"'))
        else:
            modified_lines.append(line)
    return modified_lines

import csv

def add_conditions_from_csv_multi(lines, csv_file):
    conditions = {}

    # Read the CSV file and store conditions in a dictionary
    try:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                record_format = row['record_format']
                condition = f'''  <condition>
      <test>
        <{row['con']} offset="{row['offset']}" size="{row['size']}" type="{row['type']}" /><value>{row['value']}</value>
      </test>
    </condition>\n'''
                if record_format not in conditions:
                    conditions[record_format] = []
                conditions[record_format].append(condition)
    except FileNotFoundError:
        print(f"Error: The file {csv_file} was not found.")
        return lines
    except Exception as e:
        print(f"Error: {e}")
        return lines

    # Add conditions to the lines if record format is present in the input text file
    modified_lines = []
    for line in lines:
        modified_lines.append(line)
        if '<record-format' in line and 'name="' in line:
            record_format_name = line.split('name="')[1].split('"')[0]
            if record_format_name in conditions:
                for condition in conditions[record_format_name]:
                    modified_lines.append(condition)
    return modified_lines

#Function to add condition for each record format from CSV file if present in the input text file
def add_conditions_from_csv_single(lines, csv_file):
    conditions = {}

    # Read the CSV file and store conditions in a dictionary
    try:
        with open(csv_file, 'r') as file:
            reader = csv.DictReader(file)
            for row in reader:
                record_format = row['record_format']
                test = f'''      <test>
        <{row['con']} offset="{row['offset']}" size="{row['size']}" type="{row['type']}" /><value>{row['value']}</value>
      </test>\n'''
                if record_format not in conditions:
                    conditions[record_format] = []
                conditions[record_format].append(test)
    except FileNotFoundError:
        print(f"Error: The file {csv_file} was not found.")
        return lines
    except Exception as e:
        print(f"Error: {e}")
        return lines

    # Add conditions to the lines if record format is present in the input text file
    modified_lines = []
    for line in lines:
        modified_lines.append(line)
        if '<record-format' in line and 'name="' in line:
            record_format_name = line.split('name="')[1].split('"')[0]
            if record_format_name in conditions:
                condition = '  <condition>\n' + ''.join(conditions[record_format_name]) + '  </condition>\n'
                modified_lines.append(condition)
    return modified_lines



# Function to modify FB file type
def modify_FB(file_path, csv_file, output_path, condition_type):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    max_size = None
    modified_lines = []

    for line in lines:
        if '<fixed-length' in line:
            max_size = line.split('length="')[1].split('"')[0]
        if '<mf-variable' in line:
            modified_lines.append(f'<!-- {line.strip()} -->\n')
            modified_lines.append(f'      <line-based nul-escapes="yes" max-size="{max_size}"/>\n')
        elif 'type="AE"' in line and 'name="FILLER"' in line:
            modified_lines.append(line.replace('type="AE"', 'type="A"'))
        else:
            modified_lines.append(line)

    modified_lines = rename_fillers(modified_lines)
    modified_lines = allow_blanks(modified_lines)
    if condition_type == "S":
        modified_lines = add_conditions_from_csv_single(modified_lines, csv_file)
    elif condition_type == "M":
        modified_lines = add_conditions_from_csv_multi(modified_lines, csv_file)

    with open(file_path, 'w') as file:
        file.writelines(modified_lines)


# Function to modify VB file type
def modify_VB(file_path, csv_file, output_path, condition_type):
    with open(file_path, 'r') as file:
        lines = file.readlines()

    max_size = None
    modified_lines = []

    for line in lines:
        if '<fixed-length' in line:
            modified_lines.append(f'<!-- {line.strip()} -->\n')
            max_size = line.split('length="')[1].split('"')[0]
            modified_lines.append(f'      <mvs-variable blocked="no" delimiter="no" zip="no" lrecl="{max_size}"/>\n')
        elif '<mf-variable' in line:
            modified_lines.append(f'<!-- {line.strip()} -->\n')
            modified_lines.append(f'      <line-based nul-escapes="yes" max-size="{max_size}"/>\n')
        elif 'type="AE"' in line and 'name="FILLER"' in line:
            modified_lines.append(line.replace('type="AE"', 'type="A"'))
        else:
            modified_lines.append(line)

    modified_lines = rename_fillers(modified_lines)
    modified_lines = allow_blanks(modified_lines)
    if condition_type == "S":
        modified_lines = add_conditions_from_csv_single(modified_lines, csv_file)
    elif condition_type == "M":
        modified_lines = add_conditions_from_csv_multi(modified_lines, csv_file)
    with open(file_path, 'w') as file:
        file.writelines(modified_lines)


# Modify the XML content in the specified text file
# ff_file_path1='C:/Users/rushasha/OneDrive - AMDOCS/Documents/new python/FIle Conversion'
# output_path='C:/Users/rushasha/OneDrive - AMDOCS/Documents/new python/FIle Conversion/output.ff'
# ff_file='test1.ff'
# ff_file_path = ff_file_path1 +'/' + ff_file  # Replace with the actual path to your .ff file
# csv_file_path = 'C:/Users/rushasha/OneDrive - AMDOCS/Documents/new python/FIle Conversion/test.csv' 

 # Read variables from the text file
variables = {}

with open('path.txt', 'r') as file:
     for line in file:
         name, value = line.strip().split('=')
         variables[name] = value

ff_file_path1 = variables['FORMAT_PATH']
output_path = variables['OUTPUT_PATH']
ff_file=sys.argv[1]+ ".ff"
csv_file_path = variables['CSV_file']

ff_file_path = ff_file_path1 + '/' + ff_file

# Read filetype and condition_type from stdin (passed by file.py)
filetype = input().strip()  # First line: File type (F/V)
condition_type = input().strip()  # Second line: Condition type (S/M)

if filetype == "F":
    modify_FB(ff_file_path, csv_file_path, output_path, condition_type)
elif filetype == "V":
    modify_VB(ff_file_path, csv_file_path, output_path, condition_type)
print("The FF file has been modified and saved " + ff_file )
