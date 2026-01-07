# ConvertFlow Studio - User Guide

## Welcome to ConvertFlow Studio! 🚀

ConvertFlow Studio is a simple, easy-to-use tool that helps you manage and convert data files without needing any technical knowledge. This guide will walk you through everything step-by-step in plain English.

---

## 📋 Table of Contents
1. [What You'll Need Before Starting](#what-youll-need-before-starting)
2. [Installation - Super Easy!](#installation---super-easy)
3. [Starting the Program](#starting-the-program)
4. [Understanding the Main Screen](#understanding-the-main-screen)
5. [Using Each Tool](#using-each-tool)
6. [Viewing Your Work Logs](#viewing-your-work-logs)
7. [Common Questions & Solutions](#common-questions--solutions)
8. [Getting Help](#getting-help)

---

## What You'll Need Before Starting

### Computer Requirements
- **Windows Computer** - Windows 10 or newer is best
- **Enough Storage Space** - At least 500 MB free on your computer
- **Internet Browser** - Chrome, Firefox, or Edge (the ones you already have!)

### Files You'll Need
- **ConvertFlow.exe** - This is the main program file
- **Your Data Files** - The files you want to work with

That's it! No complicated installation, no extra software needed.

---

## Installation - Super Easy!

### Step 1: Get the Program
1. Locate the **ConvertFlow.exe** file (it might be in your Downloads folder)
2. Move it to a folder where you want to keep it (like `C:\ConvertFlow\` or `D:\MyTools\`)

### Step 2: You're Done!
There's no installation! The program is ready to use right away.

---

## Starting the Program

### How to Launch ConvertFlow

1. **Find the ConvertFlow.exe file** on your computer
2. **Double-click it** - just like opening any other program
3. You'll see a **black window** appear - don't close this!
4. The window will ask you: "Enter port number to run the server (default: 5000)"
   - **Just press Enter** - this uses the default setting which works great
   - OR type a different number if someone told you to use a specific port
5. Your web browser will **automatically open** and show the ConvertFlow homepage
6. If the browser doesn't open by itself:
   - Open your browser manually (Chrome, Firefox, or Edge)
   - Type this in the address bar: `http://localhost:5000`
   - Press Enter

### What You'll See
A clean, blue-themed page with colorful buttons - this is your control center!

### How to Stop the Program
When you're done working:
- **Close the black window** that appeared when you started the program
- OR click inside the black window and press `Ctrl` + `C` on your keyboard

---

## Understanding the Main Screen

When you open ConvertFlow, you'll see 10 colorful buttons arranged in two columns. Each button opens a different tool.

### Left Column (6 Buttons)

1. **📁 Create Folder Structure**
   - Makes all the folders you need for a new project
   
2. **📂 Copy Bulk Files**
   - Copies many files at once
   
3. **🔁 Bulk DataTurn**
   - Runs DataTurn processing on your files
   
4. **🗂️ FF File Mapping**
   - Organizes your format files

5. **🔍 File Retrieval**
   - Searches for and copies files from nested folders
   
6. **⚙️ Scripts Configuration**
   - Changes program settings

### Right Column (5 Buttons)

1. **🗂️ Open Project Folders**
   - Opens all your project folders at once
   
2. **📚 Bulk EXPFD**
   - Creates EXPFD files from copybooks
   
3. **🔄 Bulk Conversion**
   - Converts your data files
   
4. **☁️ Copy to AWS S3**
   - Uploads files to cloud storage
   
5. **📋 View Logs**
   - Shows you what the program has been doing

Don't worry if some of these names sound technical - we'll explain each one simply!

---

## Using Each Tool

### 1. 📁 Create Folder Structure

**What does it do?**  
Creates all the folders you need for a new project, all organized and ready to use.

**When should I use it?**  
When you're starting a brand new project and need a proper folder setup.

**How to use it:**

1. Click the **"Create Folder Structure"** button
2. You'll see two boxes to fill in:
   - **Folder Name**: Type the name of your project (example: "CustomerData" or "Project2025")
   - **Base Path**: Type where you want to create these folders (example: "C:/MyProjects" or "D:/Work")
3. Click the blue **"Create Folders"** button
4. Wait a moment - you'll see a success message!
5. Click **"Back to Main Menu"** to return to the home screen

**What folders will be created?**
- `input` - Put your original files here
- `output` - Your converted files will appear here
- `expfd` - Special files storage
- `copybook` - Copybook files go here
- `FF_FILES` - Format files storage
- `datamatch/source` - For comparing data
- `datamatch/target` - For comparing data

**Example:**  
If you enter "MyProject" as the folder name and "C:/Work" as the base path, you'll get:
```
C:/Work/MyProject/
  ├── input/
  ├── output/
  ├── expfd/
  └── ... (all other folders)
```

---

### 2. 🗂️ Open Project Folders

**What does it do?**  
Opens all your project folders in Windows Explorer so you can see them all at once.

**When should I use it?**  
When you want to quickly access all your project folders without clicking through them one by one.

**How to use it:**

1. Click **"Open Project Folders"**
2. Fill in the two boxes:
   - **Folder Name**: Your project name (same as when you created it)
   - **Base Path**: Where your project is located
3. Click **"Open Folders"**
4. Windows Explorer will pop up showing all your folders!

**Tip:** This is super handy when you need to drag and drop files into the right folders.

---

### 3. 📂 Copy Bulk Files

**What does it do?**  
Copies many files from one place to another and can rename them automatically based on a list you provide.

**When should I use it?**  
When you have lots of files to copy and you want to save time instead of copying them one by one.

**How to use it:**

**First, prepare your list:**
1. Create a simple text file (use Notepad)
2. List your files like this:
   ```
   OldFileName1.txt, NewFileName1.txt
   OldFileName2.dat, NewFileName2.dat
   OriginalFile.csv, RenamedFile.csv
   ```
3. Save this file somewhere (like "C:/MyFiles/filelist.txt")

**Then use the tool:**
1. Click **"Copy Bulk Files"**
2. Fill in the three boxes:
   - **Source Path**: Where your original files are (example: "C:/SourceFolder")
   - **Destination Path**: Where you want to copy them to (example: "C:/Work/MyProject/input")
   - **Input File**: Your list file (example: "C:/MyFiles/filelist.txt")
3. Click **"Copy Files"**
4. Watch as the program copies and renames each file!
5. You'll see messages showing:
   - ✅ Green for successful copies
   - ❌ Red for any problems

**Important Note:** Make sure the file names in your list match exactly with the real file names!

---

### 4. 📚 Bulk EXPFD

**What does it do?**  
Converts copybook files into EXPFD files automatically.

**When should I use it?**  
When you have copybook files that need to be converted to EXPFD format.

**How to use it:**

1. **First**: Put all your copybook files in the `copybook` folder
2. Click **"Bulk EXPFD"**
3. Click the blue **"Create EXPFD Files"** button
4. Wait while the program processes your files
5. When it's done, your EXPFD files will be in the `expfd` folder

**What to expect:**
- The program will process each copybook file one by one
- You'll see success messages for each file
- The EXPFD files will have the same names as your copybook files

---

### 5. 🔁 Bulk DataTurn

**What does it do?**  
Runs DataTurn processing on your EXPFD files to create format definitions.

**When should I use it?**  
After creating EXPFD files, when you need to generate format files.

**Requirements:**
- DataTurn must be installed on your computer
- EXPFD files must be ready in the `expfd` folder
- The program must know where DataTurn is installed (set in Configuration)

**How to use it:**

1. Make sure your EXPFD files are in the `expfd` folder
2. Click **"Bulk DataTurn"**
3. Click **"Run DataTurn"**
4. The program will process each EXPFD file
5. Format files will appear in the `FF_FILES` folder

**Note:** This might take a while if you have many files. Be patient!

---

### 6. 🔄 Bulk Conversion

**What does it do?**  
Converts your data files from one format to another using format definitions.

**When should I use it?**  
When you have data files that need to be converted (like changing from mainframe format to modern format).

**Requirements:**
- Your data files must be in the `input` folder
- Format files (.ff files) must be in the `FF_FILES/` folder
- Dowitcher must be installed

**How to use it:**

1. Put your data files in the `input` folder
2. Make sure your format files are ready
3. Click **"Bulk Conversion"**
4. Fill in:
   - **Application Name**: Your project name (like "occ" or "CustomerData")
   - **Base Path**: Where your project is located
5. Click **"Convert All Files"**
6. Wait while files are converted
7. Converted files will appear in the `output` folder

**What you'll see:**
- ✅ Success messages for files that converted properly
- ❌ Error messages if something went wrong
- ⚠️ Warnings if files were skipped

---

### 7. � File Retrieval

**What does it do?**  
Searches through folders and all their subfolders to find specific files you're looking for, then copies them to one place.

**When should I use it?**  
When you need to find files that are scattered across many nested folders, or when you have a list of files to collect from a complex folder structure.

**Real-World Example:**  
Imagine you have 100 files buried in a folder that has 50 subfolders, each with their own subfolders. Instead of manually clicking through each folder to find your files, this tool searches everything automatically!

**How to use it:**

**Step 1: Create your file list**
1. Open Notepad
2. Type the names of files you want to find, one per line:
   ```
   CustomerData.txt
   Invoice2025.csv
   Report_January.xlsx
   ```
3. Save as `file_list.txt`

**Step 2: Use the tool**
1. Click **"File Retrieval"**
2. Fill in three boxes:
   - **File List Path**: Where you saved `file_list.txt` (example: `C:/MyFiles/file_list.txt`)
   - **Source Folder**: The main folder to search in (example: `D:/Wave1/Drop4/BAD_DEBT`)
     - The tool will search this folder AND all folders inside it!
   - **Destination Folder**: Where to copy the files you find (example: `C:/CollectedFiles`)
3. Click **"Retrieve Files"**
4. Wait while the tool searches (may take a minute for large folders)

**What you'll see:**
- ✅ **SUCCESS**: Files that were found and copied
- ❌ **MISSING**: Files that couldn't be found anywhere
- ⚠️ **EMPTY**: Files that were found but are empty (0 bytes)

**Bonus Feature:**
A special file called `empty_and_missing_files.txt` will be created in your destination folder. It lists:
- All files that were empty
- All files that couldn't be found

This is helpful for tracking down problems!

**Tips:**
- Make sure file names in your list are spelled exactly right
- The search looks through ALL subfolders, no matter how deep
- If a file exists in multiple places, the first one found will be copied
- Large folders with many subfolders will take longer to search

---

### 8. �🗂️ FF File Mapping

**What does it do?**  
Organizes and copies format files based on a mapping list you provide.

**When should I use it?**  
When you need to organize format files from different sources or rename them according to a plan.

**How to use it:**

**First, create a CSV file:**
1. Open Excel or Notepad
2. Create columns: Folder Name, File Name, Destination Name
3. Example:
   ```
   Project1, Format1.ff, ProcessedFormat1.ff
   Project2, Format2.ff, ProcessedFormat2.ff
   ```
4. Save as CSV file

**Then use the tool:**
1. Click **"FF File Mapping"**
2. The settings should already be configured
3. Click **"Map Files"**
4. Files will be copied and organized per your mapping

---

### 9. ☁️ Copy to AWS S3

**What does it do?**  
Uploads your files to Amazon's cloud storage (AWS S3).

**When should I use it?**  
When you need to back up files to the cloud or share them with others via AWS.

**Requirements:**
- AWS account
- AWS CLI installed on your computer
- AWS credentials configured

**How to use it:**

1. Click **"Copy to AWS S3"**
2. Fill in:
   - **Local Path**: The folder on your computer (example: "C:/Work/MyProject/output")
   - **S3 Path**: The cloud location (example: "s3://my-bucket-name/project-files/")
3. Click **"Upload to S3"**
4. Watch the upload progress
5. You'll see confirmation when it's complete

**Important:** The S3 path must start with "s3://" and include your bucket name!

**Note:** If you're not sure about AWS settings, ask your IT department for help.

---

### 10. ⚙️ Scripts Configuration

**What does it do?**  
Lets you change program settings and update paths without editing files manually.

**When should I use it?**  
- When you first set up the program
- When file locations change
- When switching between different projects

**How to use it:**

1. Click **"Scripts Configuration"**
2. You'll see many settings boxes with paths and file locations
3. Update any settings you need to change
4. Click **"Save Scripts Config"** at the bottom
5. The program will save your changes

**Common Settings:**
- **Copy Source Path**: Where to copy files from
- **Copy Destination Path**: Where to copy files to
- **DataTurn Path**: Where DataTurn is installed
- **Dowitcher Path**: Where Dowitcher is located
- **File Retrieval Settings**: File list location, search folder, and destination
- **FF File Mapping**: Source, destination, and CSV mapping file
- **AWS S3 Settings**: Cloud storage paths

**Special Feature - Update Application Name:**

If you need to switch from one project to another (like from "occ" to "rbs"):
1. In Scripts Configuration, click **"⚙️ Update path.txt"**
2. Enter the new **Application Name** (example: change "occ" to "rbs")
3. Click **"Update All Paths"**
4. All your paths will automatically update to use the new name!

---

### 11. 📋 View Logs

**What does it do?**  
Shows you a record of everything the program has done - successes, errors, and everything in between.

**When should I use it?**  
- To check if operations completed successfully
- To find out what went wrong if something failed
- To see a history of all your work

**How to use it:**

1. Click **"View Logs"**
2. You'll see the log display with color-coded messages:
   - 🟢 **Green** = Success! Everything worked
   - 🔴 **Red** = Error - something went wrong
   - 🟡 **Orange** = Warning - pay attention
   - 🔵 **Blue** = Information

**Helpful Buttons:**
- **⬆️ Top** - Jump to the beginning of the logs
- **⬇️ Bottom** - Jump to the most recent logs
- **📋 Copy All** - Copy all logs to your clipboard (to paste in an email, for example)
- **🔄 Refresh** - Reload the logs to see the latest updates

**Reading the Logs:**

Each log entry shows:
- **Time**: When something happened
- **Action**: What the program was doing
- **Result**: Whether it worked or not
- **Details**: More information if needed

Example log entry:
```
2025-11-16 10:30:45 - Copy Bulk Files - SUCCESS
Copied 15 files from C:/Source to C:/Destination
```

**Tips:**
- If something isn't working, check the logs first
- You can use Ctrl+F to search for specific words
- The most recent activity is at the bottom

---

## Viewing Your Work Logs

### Why Logs Are Important

Think of logs as a diary of everything ConvertFlow does. They help you:
- Confirm work was completed
- Find out why something didn't work
- Keep track of when you did things
- Troubleshoot problems

### Understanding Log Messages

**Success Messages (Green):**
```
✅ Operation completed successfully
✅ All files copied
✅ Conversion finished
```
These mean everything worked perfectly!

**Error Messages (Red):**
```
❌ File not found
❌ Permission denied
❌ Conversion failed
```
These mean something went wrong and needs attention.

**Warning Messages (Orange):**
```
⚠️ File already exists, skipped
⚠️ Some files couldn't be processed
```
These mean the program continued but you should be aware of something.

**Information Messages (Blue):**
```
ℹ️ Processing file 1 of 10
ℹ️ Starting conversion
```
These are just updates about what's happening.

---

## Common Questions & Solutions

### "The program won't start!"

**Try these solutions:**
1. Make sure you double-clicked ConvertFlow.exe
2. Check if another program is using port 5000:
   - When it asks for a port number, type `8080` instead and press Enter
3. Run the program as Administrator:
   - Right-click ConvertFlow.exe
   - Choose "Run as administrator"
4. Check if your antivirus blocked it - add an exception if needed

---

### "My browser didn't open automatically"

**No problem! Do this:**
1. Open your browser manually (Chrome, Firefox, or Edge)
2. In the address bar, type: `http://localhost:5000`
3. Press Enter
4. You should see ConvertFlow!

---

### "I can't find my files after conversion"

**Check these places:**
1. Look in the `output` folder of your project
2. Check the logs to see if conversion was successful
3. Verify the **Base Path** and **Application Name** are correct
4. Make sure you're looking in the right project folder

---

### "I get 'File not found' errors"

**Common causes and fixes:**

1. **Wrong file path**
   - Check spelling carefully
   - Use forward slashes `/` not backslashes `\`
   - Example: Use `C:/MyFolder/file.txt` not `C:\MyFolder\file.txt`

2. **File doesn't exist**
   - Open Windows Explorer and verify the file is really there
   - Check if the file name matches exactly (including uppercase/lowercase)

3. **Wrong folder**
   - Double-check you're pointing to the correct location
   - Use "Open Project Folders" to verify folder structure

---

### "DataTurn or Dowitcher isn't working"

**Steps to fix:**

1. **Verify it's installed:**
   - Open Command Prompt (search for "cmd" in Windows)
   - Type the full path to the program
   - If it runs, it's installed correctly

2. **Check the path in Configuration:**
   - Go to Scripts Configuration
   - Find the DataTurn Path or Dowitcher Path setting
   - Make sure it points to the correct location
   - Example: `C:/Program Files/DataTurn/dataturn.exe`

3. **Check permissions:**
   - Make sure the program has permission to run
   - Try running ConvertFlow as Administrator

---

### "AWS S3 upload fails"

**What to check:**

1. **AWS CLI installed?**
   - Open Command Prompt
   - Type: `aws --version`
   - If you see an error, AWS CLI needs to be installed

2. **AWS credentials set up?**
   - In Command Prompt, type: `aws configure`
   - Enter your AWS Access Key and Secret Key
   - Ask your IT department if you don't have these

3. **Correct S3 path?**
   - Must start with `s3://`
   - Include your bucket name
   - Example: `s3://my-company-bucket/project-files/`

4. **Internet connection working?**
   - Make sure you're connected to the internet
   - Check if you can access other websites

---

### "Files aren't copying in Copy Bulk"

**Troubleshooting steps:**

1. **Check your input file:**
   - Open it in Notepad
   - Each line should have: `SourceFile.txt, DestinationFile.txt`
   - Make sure there's a comma between the names

2. **Verify source files exist:**
   - Go to the source folder in Windows Explorer
   - Confirm all files listed in your input file are there

3. **Check destination folder:**
   - Make sure it exists
   - Check you have permission to write files there

4. **Look at the logs:**
   - Click "View Logs"
   - Find the Copy Bulk operation
   - Read the error messages for specific problems

---

### "I need to switch between projects (like 'occ' to 'rbs')"

**Easy way to do this:**

1. Click **Scripts Configuration** ⚙️
2. Click **"⚙️ Update path.txt"**
3. In the "Application Name" box, type the new name (like "rbs")
4. Click **"Update All Paths"**
5. Done! All your paths now use the new project name

**What this does:**
- Changes all occurrences of the old name (like "occ") to the new name (like "rbs")
- Updates all paths automatically
- Saves you from editing each path manually

---

### "The logs aren't showing new activity"

**Quick fixes:**

1. Click the **🔄 Refresh** button
2. Wait a few seconds and refresh again
3. If still not updating, restart ConvertFlow

---

### "I accidentally closed the black window"

**What happened:**
The black window is the program's "engine" - closing it stops ConvertFlow.

**How to fix:**
1. Simply double-click ConvertFlow.exe again
2. It will restart and you can continue working
3. Just don't close that black window while working!

---

### "Can I work on multiple projects at once?"

**Unfortunately, no.**  
ConvertFlow works with one project at a time. To switch projects:
1. Finish what you're doing with the current project
2. Use Scripts Configuration to update to the new project
3. Start working with the new project

---

## Getting Help

### If You're Stuck

**Look at the logs first:**
- Click "View Logs"
- Look for red error messages
- Read what they say - they often explain the problem

**Check this guide:**
- Use Ctrl+F to search for keywords
- Look in "Common Questions & Solutions"

**Ask your IT team:**
- Show them the error message from the logs
- Tell them what you were trying to do
- Mention which button you clicked

**Contact Support:**
- Email: support@astadia.com
- Include:
  - What you were trying to do
  - The error message (copy from logs)
  - Your project name and paths

---

## Tips for Success

### Before You Start Any Operation:

1. **Make backups** - Copy your important files to a safe place first
2. **Check your paths** - Make sure all folders and file locations are correct
3. **Test with a small batch** - Try a few files first before processing hundreds
4. **Read the logs** - Check them after each operation to ensure success

### Good Habits:

- **Keep your project folders organized** - Don't mix different projects
- **Use clear, simple names** - Avoid spaces and special characters in folder names
- **Check logs regularly** - Catch problems early
- **Save your configuration** - After setting up, save your Scripts Configuration

### File Naming Tips:

✅ **Good names:**
- `customer_data_2025.txt`
- `ProjectABC_input.dat`
- `format_file_01.ff`

❌ **Avoid:**
- `my file.txt` (has space)
- `project#1.dat` (has special character)
- `very_long_name_that_goes_on_and_on_and_on.txt` (too long)

---

## Keyboard Shortcuts

While using ConvertFlow in your browser:

- **Ctrl + F** - Find text on the page
- **Ctrl + C** - Copy selected text
- **Ctrl + V** - Paste
- **F5** - Refresh the page
- **Alt + ←** - Go back to previous page

---

## Final Words

**You don't need to be technical to use ConvertFlow!**

Take it one step at a time:
1. Start with simple operations like creating folders
2. Learn by doing - try things out
3. Check the logs to see what happened
4. Ask for help when you need it

**Remember:**
- The program can't break your computer
- Your original files are safe as long as you keep backups
- Mistakes can be fixed
- The logs are your friend - they explain everything

**Happy Converting!** 🎉

---

*ConvertFlow Studio - Making Data Conversion Simple*

*User Guide Version 1.0 - November 2025*  
*Created by Astadia Team*

---

## Quick Reference Card

**Starting:**
1. Double-click ConvertFlow.exe
2. Press Enter for default port
3. Use the program in your browser

**Most Common Tasks:**

| What I Want to Do | Which Button to Click |
|-------------------|----------------------|
| Create new project folders | 📁 Create Folder Structure |
| Copy many files | 📂 Copy Bulk Files |
| Convert data files | 🔄 Bulk Conversion |
| Open project folders | 🗂️ Open Project Folders |
| Check if things worked | 📋 View Logs |
| Change settings | ⚙️ Scripts Configuration |
| Upload to cloud | ☁️ Copy to AWS S3 |

**Getting Help:**
- Check logs first
- Read this guide


**Emergency:**
- Close black window to stop program
- Restart by double-clicking ConvertFlow.exe again

---

*Print this guide or keep it handy for reference!*
