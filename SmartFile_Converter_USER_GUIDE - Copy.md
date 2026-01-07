# SmartFile Converter - User Guide

## Welcome! 🎉

Welcome to **SmartFile Converter**! This guide will help you understand how to use this powerful tool to convert and process your data files - even if you're not a technical expert.

---

## Table of Contents

1. [What is SmartFile Converter?](#what-is-smartfile-converter)
2. [Getting Started](#getting-started)
3. [Main Features](#main-features)
4. [Step-by-Step Instructions](#step-by-step-instructions)
5. [Understanding the Interface](#understanding-the-interface)
6. [Common Tasks](#common-tasks)
7. [Troubleshooting](#troubleshooting)
8. [Tips & Best Practices](#tips--best-practices)

---

## What is SmartFile Converter?

**SmartFile Converter** is a user-friendly tool that helps you:

- **Convert data files** from one format to another
- **Rename and organize** your data files
- **Process EBCDIC files** (a special mainframe data format)
- **Create and modify** file format definitions
- **View and analyze** your data in different ways

Think of it as a Swiss Army knife for working with mainframe data files!

---

## Getting Started

### Step 1: Launch the Application

1. **Double-click** on `SmartFile_Converter.exe`
2. A web page will automatically open in your default browser
3. You'll see the main dashboard with a clean blue interface

### Step 2: First Look

When you open the application, you'll see:
- **File name field** - Where you enter the name of your file
- **Records field** (optional) - For processing specific record ranges
- **Multiple buttons** - Each button performs a different task
- **Output area** - Shows the results of your operations

---

## Main Features

### 🎯 Quick Reference - What Each Button Does

| Button | What It Does | When to Use It |
|--------|-------------|----------------|
| **Create EXPFD** | Creates a format definition from copybook files | Starting a new conversion project |
| **Run DataTurn** | Generates file format files automatically | After creating EXPFD files |
| **Rename .FF File** | Changes the name of your format file | When you need to organize or update file names |
| **Modify .FF File** | Changes file type settings (FB/VB) | When file format needs adjustment |
| **Run Dowitcher** | Converts EBCDIC data to readable format | Main conversion operation |
| **Display Output** | Shows converted data on screen | Reviewing your converted data |
| **Run Roy's Tool** | Processes EBCDIC files with special rules | Complex EBCDIC conversions |
| **Display with Hex** | Shows data with hexadecimal codes | Troubleshooting or technical analysis |
| **Convert Records** | Converts only specific record numbers | Processing partial data sets |
| **Input with Hex** | Shows input data with hex codes | Analyzing source data |
| **Update Paths** | Changes folder locations for files | Setting up or reconfiguring the tool |
| **View Logs** | Shows history of all operations | Tracking what was done or debugging |

---

## Step-by-Step Instructions

### Task 1: Converting a Data File (Most Common Task)

**What you need:**
- Your data file (e.g., `mydata.txt`) in the input folder
- A format file (`.ff`) with the same name

**Steps:**

1. **Enter the file name** in the "File name" field (without the `.ff` extension)
   - Example: If your file is `customer.ff`, just type `customer`

2. **Click "Run Dowitcher"** button

3. **Wait** - You'll see a "Processing... Please wait" message

4. **Check the output** - The results will appear in the output area at the bottom
   - ✅ Look for "Successfully" messages
   - ❌ If you see errors, check the [Troubleshooting](#troubleshooting) section

5. **Your converted file** will be in the output folder!

---

### Task 2: Creating Format Files from Copybooks

**What you need:**
- Copybook files in the copybook folder

**Steps:**

1. **Enter a name** for your EXPFD file in the "File name" field

2. **Click "Create EXPFD"** button

3. The tool will:
   - Read your copybook files
   - Remove unnecessary information
   - Create a clean EXPFD file

4. **Check the output** for success messages

5. **Next step:** Click "Run DataTurn" to generate the format file

---

### Task 3: Viewing Your Data

**To see what's in your converted file:**

1. **Enter the file name** (without `.ff`)

2. **Optionally**, specify which records to view:
   - For first 100 records: type `1-100`
   - For records 50 to 150: type `50-150`
   - Leave blank to view all records

3. **Click "Display Output"**

4. **Review the data** in the output area
   - You can scroll through it
   - Use the resize handle in the bottom-right corner to make it bigger

---

### Task 4: Renaming a Format File

**Steps:**

1. **Click "Rename .FF File"** button

2. A new page will open with two fields:
   - **Current file name** - Enter the current name (without `.ff`)
   - **New file name** - Enter what you want to rename it to (without `.ff`)

3. **Click "Rename File"** button

4. **Check the output** for confirmation

5. **Click "← Back to Main Menu"** to return to the main screen

---

### Task 5: Modifying File Settings

**When to use:** If your file format needs to be changed (Fixed Block vs Variable Block)

**Steps:**

1. **Click "Modify .FF File"** button

2. Fill in the information:
   - **File name** - Enter your file name (without `.ff`)
   - **File Type** - Choose:
     - `F - Fixed Block (FB)` - All records are the same length
     - `V - Variable Block (VB)` - Records can be different lengths
   - **Condition Test Type** - Choose:
     - `S - Single Condition` - Simple file structure
     - `M - Multiple Conditions` - Complex file with different record types

3. **Click "✏️ Execute Modification"**

4. **Check the output** for success

---

## Understanding the Interface

### Main Dashboard

```
┌─────────────────────────────────────────┐
│      SmartFile Converter                │
├─────────────────────────────────────────┤
│  📁 File name: [____________]           │
│  📊 Records: [____________] (optional)  │
├─────────────────────────────────────────┤
│  [Create EXPFD]  [Run DataTurn]        │
│  [Rename .FF]    [Modify .FF]          │
│  [Run Dowitcher] [Display Output]      │
│  [Run Roy's Tool] [Display with Hex]   │
│  [Convert Records] [Input with Hex]    │
│  [Update Paths]   [View Logs]          │
├─────────────────────────────────────────┤
│  📤 Command Output:                     │
│  ┌───────────────────────────────────┐ │
│  │ Results appear here...            │ │
│  │                                   │ │
│  └───────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

### Output Area Features

- **Scrolling**: Use scrollbars to navigate long output
- **Resizing**: Drag the bottom-right corner to make it bigger or smaller
- **Copy/Paste**: You can select and copy text from the output

---

## Common Tasks

### ✅ Processing a New File

1. Create EXPFD → 2. Run DataTurn → 3. Run Dowitcher

### ✅ Quick File Conversion

1. Enter file name → 2. Click "Run Dowitcher"

### ✅ Checking Results

1. Enter file name → 2. Click "Display Output"

### ✅ Debugging Issues

1. Click "View Logs" → 2. Look for error messages

### ✅ Processing Only Part of a File

1. Enter file name → 2. Enter record range (e.g., `1-1000`) → 3. Click "Convert Records"

---

## Troubleshooting

### Problem: "File not found" Error

**Solution:**
- Check that your file is in the correct folder
- Verify the file name (no typos!)
- Don't include the `.ff` or `.txt` extension when typing the name

### Problem: "Path does not exist" Error

**Solution:**
- Click "Update Paths" button
- Verify all folder paths are correct
- Make sure folders exist on your computer

### Problem: Output Shows Errors

**Solution:**
1. Click "View Logs" to see detailed information
2. Look for the most recent error messages
3. Check that all required files are in place:
   - Input file in input folder
   - Format file (`.ff`) in format folder
   - Copybook files (if needed) in copybook folder

### Problem: Application Won't Start

**Solution:**
- Make sure `SmartFile_Converter.exe` is in the correct folder
- Check that all required files are present in the application folder
- Try running as Administrator (right-click → Run as Administrator)

### Problem: Conversion Results Look Wrong

**Solution:**
- Verify you're using the correct format file (`.ff`)
- Check file type setting (F for Fixed, V for Variable)
- Try "Display with Hex" to see raw data

---

## Tips & Best Practices

### 💡 General Tips

1. **Always start with small test files** before processing large datasets

2. **Use meaningful file names** 
   - Good: `customer_data_2024`
   - Avoid: `file1`, `test`, `new`

3. **Check the output after each operation** - Don't assume it worked!

4. **Keep the logs** - Click "View Logs" regularly to track your work

5. **Organize your folders** - Keep input, output, and format files in their proper locations

### 💡 Record Range Tips

- Use ranges for testing: `1-10` to see first 10 records
- Process in batches for large files: `1-10000`, then `10001-20000`, etc.
- Leave blank to process all records

### 💡 Performance Tips

- **Be patient** - Large files can take several minutes to process
- **Don't close the browser** while "Processing... Please wait" is showing
- **One operation at a time** - Wait for each task to complete before starting another

### 💡 Safety Tips

- **Keep backups** of your original files before conversion
- **Test with sample data** first
- **Review the output** before relying on converted data

---

## Understanding File Formats

### What is a .FF File?

A `.ff` (File Format) file tells the converter:
- How your data is organized
- What each field means
- How to read and convert the data

Think of it as a "translation dictionary" for your data.

### What is EBCDIC?

EBCDIC is an old character encoding used on mainframe computers. This tool converts EBCDIC data into readable text (ASCII) that modern computers can understand.

### What is a Copybook?

A copybook is a file that describes the structure of your data - like a blueprint. The tool uses copybooks to understand how to process your files.

---

## Logging and History

### Viewing Logs

1. **Click "View Logs"** button on the main screen
2. You'll see a list of all log files organized by date
3. Click any log file to view its contents
4. Logs show:
   - Timestamps of operations
   - Commands that were run
   - Success/failure status
   - Detailed output and error messages

### Why Logs Are Important

- **Tracking**: See what operations were performed and when
- **Debugging**: Find out exactly what went wrong
- **Audit**: Keep a record of all file processing activities
- **Learning**: Understand how the tool works by reviewing successful operations

### Log Files Location

All logs are saved in the `logs` folder with names like:
- `SmartFile_Converter_20241116.log` (date-based naming)

---

## Folder Structure

The application uses several folders to organize files:

```
Application Folder/
├── SmartFile_Converter.exe  ← The program you run
├── path.txt                  ← Configuration file (folder locations)
├── logs/                     ← Log files for troubleshooting
├── input/                    ← Put your source data files here
├── output/                   ← Converted files appear here
├── FORMAT_PATH/              ← Format files (.ff) go here
├── copybook/                 ← Copybook definition files
└── expfd/                    ← Generated EXPFD files
```

**Important:** Don't delete or rename these folders!

---

## Configuration (Advanced)

### Updating Paths

If you need to change where files are stored:

1. **Click "Update Paths"** button
2. A configuration page will open
3. Update any paths that need changing
4. **Click "Save Configuration"**
5. The tool will now use your new folder locations

### What Paths Mean

- **INPUT_PATH**: Where your source data files are located
- **OUTPUT_PATH**: Where converted files will be saved
- **FORMAT_PATH**: Where `.ff` format files are stored
- **COPYBOOK**: Where copybook files are located
- **EXPFD**: Where generated EXPFD files go

---

## Getting Help

### If You're Stuck

1. **Check this guide** - Use the Table of Contents to find your topic
2. **View the logs** - Often shows exactly what went wrong
3. **Try the Troubleshooting section** - Common problems and solutions
4. **Ask for help** - Contact your system administrator or support team

### What Information to Provide When Asking for Help

- What you were trying to do
- The exact error message you received
- The contents of the most recent log file
- The file name you were working with

---

## Frequently Asked Questions (FAQ)

**Q: Do I need to include `.ff` when I type the file name?**  
A: No! Just type the base name. For example, if your file is `customer.ff`, just type `customer`

**Q: Can I process multiple files at once?**  
A: No, process one file at a time for best results.

**Q: What happens to my original files?**  
A: They are not modified. Converted files are saved separately in the output folder.

**Q: How do I know if the conversion worked?**  
A: Check the output area for ✅ success messages, and use "Display Output" to review the converted data.

**Q: Why does processing take so long?**  
A: Large files require more time to process. The tool is working through each record carefully.

**Q: Can I close the application while it's processing?**  
A: No! Wait for the "Processing complete" message before closing.

**Q: Where can I find my converted files?**  
A: In the OUTPUT_PATH folder (usually the `output` folder in the application directory).

**Q: What if I made a mistake?**  
A: You can re-run any operation. Your original files are safe and unchanged.

---

## Quick Start Checklist

For your first conversion:

- [ ] Double-click `SmartFile_Converter.exe`
- [ ] Wait for the web page to open
- [ ] Put your data file in the `input` folder
- [ ] Put the matching `.ff` file in the `FORMAT_PATH` folder
- [ ] Type the file name (without `.ff`)
- [ ] Click "Run Dowitcher"
- [ ] Wait for processing to complete
- [ ] Check the output for success messages
- [ ] Find your converted file in the `output` folder
- [ ] Click "View Logs" to see details

---

## Summary

**SmartFile Converter** makes it easy to:

✅ Convert mainframe data files to modern formats  
✅ Process EBCDIC files without technical knowledge  
✅ View and analyze your data  
✅ Track all operations with detailed logs  
✅ Work with complex file formats simply  

Remember: **Take it slow, read the messages, and check your results!**

---

## Support

**Powered by Astadia TEAM**

For additional assistance, please contact your system administrator or the Astadia support team.

---

**Version:** 1.0  
**Last Updated:** November 2024  
**Compatible with:** SmartFile_Converter.exe

---

*This guide is designed to be printed, saved as PDF, or viewed on screen. Keep it handy whenever you're working with SmartFile Converter!*
