# ConvertFlow Studio

[![Version](https://img.shields.io/badge/version-1.0-blue.svg)](https://github.com/astadia/convertflow)
[![Platform](https://img.shields.io/badge/platform-Windows-lightgrey.svg)](https://www.microsoft.com/windows)

**ConvertFlow Studio** is a comprehensive web-based application designed to simplify mainframe data file conversion, management, and processing workflows. Built with Flask and designed for ease of use, ConvertFlow provides an intuitive interface for handling complex data transformation tasks.

---

## 🌟 Features

### Core Functionality
- **📁 Folder Structure Management** - Automatically create standardized project folder hierarchies
- **📂 Bulk File Operations** - Copy and rename multiple files efficiently using CSV mappings
- **� File Retrieval** - Search and retrieve files recursively from nested folder structures
- **�📚 EXPFD Creation** - Convert copybook files to EXPFD format in bulk
- **🔁 DataTurn Integration** - Process EXPFD files using DataTurn automation
- **🔄 Bulk Conversion** - Transform mainframe data files using format definitions
- **🗂️ File Mapping** - Organize and map files based on CSV configurations
- **☁️ AWS S3 Integration** - Upload files directly to Amazon S3
- **⚙️ Configuration Management** - Centralized settings and path configuration
- **📋 Real-time Logging** - Comprehensive activity logging with live viewing

### User Experience
- Modern, responsive web interface
- Real-time operation feedback
- Color-coded success/error messages
- Detailed operation logs
- No technical knowledge required

---

## 📋 Table of Contents

- [System Requirements](#-system-requirements)
- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Configuration](#-configuration)
- [Usage](#-usage)
- [Architecture](#-architecture)
- [Building the Executable](#-building-the-executable)
- [Troubleshooting](#-troubleshooting)
- [Support](#-support)

---

## 💻 System Requirements

### Minimum Requirements
- **Operating System:** Windows 10 or later (64-bit)
- **RAM:** 4 GB minimum, 8 GB recommended
- **Disk Space:** 500 MB for application, additional space for data processing
- **Browser:** Modern web browser (Chrome, Firefox, Edge)
- **Python:** 3.8 or later (for development/source version)

### Optional Dependencies
- **DataTurn:** Required for Bulk DataTurn operations
- **AWS CLI:** Required for S3 upload functionality
- **Dowitcher:** Required for Bulk Conversion operations

---

## 📦 Installation

### Option 1: Standalone Executable (Recommended for End Users)

1. **Download** the `ConvertFlow.exe` file
2. **Place** it in your preferred directory (e.g., `C:\ConvertFlow\`)
3. **Double-click** to run - no installation needed!

### Option 2: From Source (For Developers)

```bash
# Navigate to the project directory
cd C:\File_conversion

# Install required packages
pip install flask

# Run the application
python scripts_ui.py
```

### Required Python Packages
```
Flask>=2.3.0
```

---

## 🚀 Quick Start

### Running the Application

#### Using the Executable
```bash
# Navigate to the directory
cd C:\ConvertFlow

# Run the application
ConvertFlow.exe

# When prompted, press Enter to use default port (5000)
# Or enter a custom port number
```

#### Using Python
```bash
python scripts_ui.py
```

### First-Time Setup

1. **Start the application** - Your browser will open automatically to `http://localhost:5000`
2. **Configure paths** - Click on "Scripts Configuration" ⚙️
3. **Update settings** - Set your base path and application name
4. **Save configuration** - Click "Save Scripts Config"
5. **You're ready!** - Start using the features

---

## ⚙️ Configuration

### Configuration Files

ConvertFlow uses two main configuration files:

#### 1. `path.txt` - Core Path Configuration
Located in the application directory, contains essential paths:

```ini
# Application Configuration
application=C:/File_conversion/occ
basepath=C:/File_conversion

# Directory Paths
input=C:/File_conversion/occ/input
output=C:/File_conversion/occ/output
expfd=C:/File_conversion/occ/expfd
copybook=C:/File_conversion/occ/copybook
FF_FILES=C:/File_conversion/occ/FF_FILES/datamig/file-format
datamatch_source=C:/File_conversion/occ/datamatch/source
datamatch_target=C:/File_conversion/occ/datamatch/target
```

#### 2. `scripts_config.txt` - Script-Specific Settings
Contains tool-specific configurations:

```ini
# Copy Bulk Configuration
COPY_SOURCE_PATH=C:/SourceData
COPY_DEST_PATH=C:/File_conversion/occ/input
COPY_INPUT_FILE=C:/File_conversion/IGD.txt

# DataTurn Configuration
DATATURN_EXE_PATH=C:/Program Files/Anubex/DataTurn/bin/dataturn.exe
DATATURN_CONFIG_FILE=rushabh.configuration

# Bulk Conversion Configuration
BULK_DOWITCHER_PATH=C:/File_conversion/dowitcher.exe

# FF Mapping Configuration
FF_MAPPING_CSV=C:/File_conversion/IGD.csv
FF_MAPPING_SOURCE=C:/File_conversion/mc/FF_FILES

# File Retrieval Configuration
FILE_RETRIEVAL_LIST=C:/File_conversion/file_list.txt
FILE_RETRIEVAL_SOURCE=D:/Wave1/Drop4/BAD_DEBT/RL81B25L
FILE_RETRIEVAL_DEST=D:/File_conversion/output/retrieved

# AWS S3 Configuration
S3_LOCAL_PATH=C:/File_conversion/occ
S3_BUCKET_PATH=s3://my-bucket/data/
```

### Updating Configuration

**Via Web Interface:**
1. Navigate to **Scripts Configuration** ⚙️
2. Update the desired fields
3. Click **Save Scripts Config**

**Manual Editing:**
1. Open `scripts_config.txt` in a text editor
2. Update the values
3. Save the file
4. Restart ConvertFlow

### Changing Application Name

To switch between different applications (e.g., "occ" to "rbs"):

1. Go to **Scripts Configuration** ⚙️
2. Click **⚙️ Update path.txt**
3. Enter the new **Application Name**
4. Click **Update All Paths**

---

## 📖 Usage

### Feature Walkthroughs

#### Create Folder Structure 📁

Creates a complete project folder hierarchy for your application.

**Steps:**
1. Click **Create Folder Structure**
2. Enter **Folder Name** (e.g., "NewProject")
3. Enter **Base Path** (e.g., "C:/File_conversion")
4. Click **Create Folders**

**Output:**
```
project_name/
├── input/
├── output/
├── expfd/
├── copybook/
├── datamatch/
│   ├── source/
│   └── target/
└── FF_FILES/
    └── datamig/
        └── file-format/
```

---

#### Open Project Folders 🗂️

Quickly opens all project folders in Windows Explorer.

**Steps:**
1. Click **Open Project Folders**
2. Enter **Folder Name** (your project name)
3. Enter **Base Path**
4. Click **Open Folders**

---

#### Copy Bulk Files 📂

Copies and renames multiple files based on a CSV mapping file.

**Input File Format** (`files.txt`):
```csv
SourceFile1.txt, TargetFile1.txt
SourceFile2.dat, TargetFile2.dat
OldName.csv, NewName.csv
```

**Steps:**
1. Click **Copy Bulk Files**
2. Set **Source Path**, **Destination Path**, and **Input File**
3. Click **Copy Files**

---

#### File Retrieval 🔍

Searches recursively through nested folders to find and copy specific files.

**Input File Format** (`file_list.txt`):
```
File1.txt
File2.dat
File3.csv
```
(One file name per line)

**Steps:**
1. Create a text file listing the files you want to find
2. Click **File Retrieval**
3. Set:
   - **File List Path** - Path to your list file
   - **Source Folder** - Root folder to search (searches all subfolders)
   - **Destination Folder** - Where to copy found files
4. Click **Retrieve Files**

**Output:**
- Successfully copied files
- List of missing files
- List of empty files (0 bytes)
- Log file: `empty_and_missing_files.txt` created in destination folder

**Use Cases:**
- Finding files scattered across deep folder hierarchies
- Batch collecting files from multiple subdirectories
- Validating file existence before processing
3. Click **Copy Files**
4. Review the output for success/error messages

---

#### Bulk EXPFD 📚

Processes all copybook files to generate EXPFD files.

**Steps:**
1. Place copybook files in the copybook directory
2. Click **Bulk EXPFD**
3. Click **Create EXPFD Files**
4. EXPFD files will be generated in the expfd directory

---

#### Bulk DataTurn 🔁

Runs DataTurn on all EXPFD files to create format definitions.

**Prerequisites:**
- DataTurn must be installed
- EXPFD files must exist in the expfd directory
- DataTurn path configured correctly in scripts_config.txt

**Steps:**
1. Click **Bulk DataTurn**
2. Click **Run DataTurn**
3. Wait for processing to complete
4. Check FF_FILES directory for output

---

#### Bulk Conversion 🔄

Converts mainframe data files using format definitions.

**Prerequisites:**
- Input files in the input directory
- Format files (.ff) in FF_FILES/datamig/file-format
- Dowitcher executable configured

**Steps:**
1. Click **Bulk Conversion**
2. Enter **Application Name** and **Base Path**
3. Click **Convert All Files**
4. Converted files appear in the output directory

---

#### FF File Mapping 🗂️

Organizes format files based on CSV configuration.

**CSV Format** (`mapping.csv`):
```csv
FolderName, FileName, DestinationName
Project1, Format1.ff, ProcessedFormat1.ff
Project2, Format2.ff, ProcessedFormat2.ff
```

**Steps:**
1. Create mapping CSV file
2. Click **FF File Mapping**
3. Click **Map Files**
4. Files are copied and renamed per mapping

---

#### Copy to AWS S3 ☁️

Uploads files to Amazon S3.

**Prerequisites:**
- AWS CLI installed and configured
- Valid AWS credentials

**Steps:**
1. Click **Copy to AWS S3**
2. Enter **Local Path** and **S3 Path**
   - S3 Path format: `s3://bucket-name/folder/`
3. Click **Upload to S3**
4. Monitor upload progress

---

#### View Logs 📋

Displays comprehensive operation logs with real-time updates.

**Features:**
- Real-time log updates
- Color-coded messages (Success ✅, Error ❌, Warning ⚠️)
- Search and filter capabilities
- Copy to clipboard
- Scroll controls

**Steps:**
1. Click **View Logs**
2. Use controls to navigate:
   - **⬆️ Top** - Jump to start
   - **⬇️ Bottom** - Jump to end
   - **📋 Copy All** - Copy logs
   - **🔄 Refresh** - Reload logs

---

## 🏗️ Architecture

### Technology Stack

- **Backend:** Flask (Python)
- **Frontend:** HTML5, CSS3, JavaScript
- **Logging:** Python logging module with file handlers
- **File Operations:** Python standard library (os, shutil, glob)
- **Subprocess Management:** Python subprocess module

### Project Structure

```
ConvertFlow/
├── scripts_ui.py          # Main Flask application (5896 lines)
├── path.txt               # Core path configuration
├── scripts_config.txt     # Script-specific settings
├── ConvertFlow_README.md  # This file
├── ConvertFlow_USER_GUIDE.md  # User documentation
└── logs/                  # Application logs
    └── scripts_ui_YYYYMMDD.log
```

### Logging System

- **File-based logging** with automatic rotation
- **Timestamp-based** log files: `scripts_ui_YYYYMMDD.log`
- **Structured log entries** with operation details
- **Real-time flushing** for immediate log updates
- **HTML-safe** log storage for web display
- **Auto-detection** of most recent log file
- **Syntax highlighting** with word-boundary matching

---

## 🔨 Building the Executable

### Using PyInstaller

ConvertFlow can be compiled into a standalone executable:

#### Prerequisites
```bash
pip install pyinstaller
```

#### Build Command
```bash
pyinstaller --onefile --name ConvertFlow --noconsole scripts_ui.py
```

#### Build Options Explained
- `--onefile` - Creates a single executable file
- `--name ConvertFlow` - Names the output executable
- `--noconsole` - Hides the console window (optional)

#### Advanced Build with Data Files
```bash
pyinstaller --onefile ^
  --name ConvertFlow ^
  --add-data "path.txt;." ^
  --add-data "scripts_config.txt;." ^
  scripts_ui.py
```

#### Build Output
The executable will be created in the `dist/` folder:
```
dist/
└── ConvertFlow.exe
```

### Distribution Package

Create a distribution package with:

```
ConvertFlow_Distribution/
├── ConvertFlow.exe
├── path.txt
├── scripts_config.txt
├── ConvertFlow_USER_GUIDE.md
└── ConvertFlow_README.md
```

---

## 🐛 Troubleshooting

### Common Issues

#### Issue: Application won't start
**Symptoms:** ConvertFlow.exe doesn't launch or crashes immediately

**Solutions:**
- Check if port 5000 is already in use
- Try specifying a different port (e.g., 8080)
- Run as Administrator
- Check antivirus isn't blocking the application
- Verify configuration files (path.txt, scripts_config.txt) exist

---

#### Issue: "File not found" errors
**Symptoms:** Operations fail with file path errors

**Solutions:**
- Verify all paths in Scripts Configuration
- Use forward slashes (/) in paths, not backslashes (\)
- Ensure files exist at specified locations
- Check file permissions
- Verify application name is correct

---

#### Issue: DataTurn/Dowitcher not working
**Symptoms:** Bulk operations fail with executable errors

**Solutions:**
- Verify the executable paths in Scripts Configuration
- Ensure DataTurn/Dowitcher are properly installed
- Check that executables have correct permissions
- Try running the executables manually to test
- Check if executables are blocked by antivirus

---

#### Issue: Browser doesn't open automatically
**Symptoms:** Application starts but no browser window

**Solutions:**
- Manually navigate to `http://localhost:5000`
- Check your default browser settings
- Try a different browser
- Check firewall settings
- Verify the port number shown in the console

---

#### Issue: AWS S3 upload fails
**Symptoms:** S3 operations return errors

**Solutions:**
- Verify AWS CLI is installed: `aws --version`
- Check AWS credentials: `aws configure`
- Verify S3 bucket path format: `s3://bucket-name/path/`
- Check internet connection
- Verify IAM permissions for S3 access
- Test AWS CLI manually: `aws s3 ls`

---

#### Issue: Logs not updating
**Symptoms:** Log viewer shows old data or no data

**Solutions:**
- Click the **🔄 Refresh** button
- Check if logs directory exists
- Verify write permissions to logs folder
- Restart the application
- Check for disk space issues

---

#### Issue: Copy Bulk fails silently
**Symptoms:** Files not copied, no error messages

**Solutions:**
- Verify CSV file format (comma-separated)
- Check source files exist
- Verify destination path has write permissions
- Review logs for detailed error messages
- Ensure CSV file uses proper encoding (UTF-8)

---

### Debug Mode

To run in debug mode for troubleshooting:

1. If using source, edit `scripts_ui.py`:
```python
# Find the line at the end:
app.run(host='0.0.0.0', port=port)

# Change to:
app.run(host='0.0.0.0', port=port, debug=True)
```

2. Run the application
3. Check console for detailed error messages
4. Check logs directory for log files

---

## 💬 Support

### Getting Help

**For Users:**
- Consult the [ConvertFlow User Guide](ConvertFlow_USER_GUIDE.md)
- Check the [Troubleshooting](#-troubleshooting) section
- Review application logs in View Logs

**For Developers:**
- Check the [Architecture](#-architecture) section
- Review inline code documentation in scripts_ui.py
- Examine log files for debugging

### Contact

**Astadia Team**
- Email: support@astadia.com
- Website: https://www.astadia.com

---

## 📄 License

Copyright © 2025 Astadia Team. All rights reserved.

This software is proprietary and confidential. Unauthorized copying, distribution, or use of this software, via any medium, is strictly prohibited.

---

## 🔄 Version History

### Version 1.0 (November 2025)
- Initial release of ConvertFlow Studio
- 10 integrated tools for mainframe data processing
- Web-based user interface with modern design
- Real-time logging with immediate flush
- Auto-detection of most recent log file
- Syntax highlighting with word-boundary matching
- Configuration management via web interface
- Update Paths feature for easy application switching
- Comprehensive error handling and validation
- AWS S3 integration
- DataTurn automation
- Bulk file processing capabilities

---

## 📚 Additional Resources

### Related Documentation
- [ConvertFlow User Guide](ConvertFlow_USER_GUIDE.md) - Detailed user instructions
- [Flask Documentation](https://flask.palletsprojects.com/)
- [PyInstaller Manual](https://pyinstaller.org/en/stable/)
- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)

---

## ⚠️ Important Notes

### Security Considerations
- Store AWS credentials securely
- Use environment variables for sensitive data
- Restrict access to configuration files
- Review logs regularly for unauthorized access
- Change default port if needed for security

### Performance Tips
- Process files in batches for better performance
- Monitor disk space during operations
- Close unnecessary applications during large conversions
- Use SSD storage for faster processing
- Keep input/output directories on same drive when possible

### Backup Recommendations
- Always backup source files before processing
- Keep configuration files in version control
- Regularly backup logs for audit purposes
- Use AWS S3 for offsite backups
- Test restore procedures periodically

---

**ConvertFlow Studio - Simplifying Data Conversion**

*Powered by Astadia Team*

---

*Last Updated: November 2025*  
*Version: 1.0*  
*Document Version: 1.0*
