# File Conversion Studio

**Version:** 2.0  
**Developer:** Astadia TEAM  
**Last Updated:** November 14, 2025

---

## 📋 Overview

File Conversion Studio is a powerful web-based application designed to simplify mainframe file conversion and management tasks. It provides an intuitive interface for converting EBCDIC files to ASCII format, managing file formats, and performing various file operations without requiring command-line expertise.

---

## 🚀 Quick Start

### Prerequisites

- **Windows Operating System** (Windows 10 or later recommended)
- **Python 3.8+** (if running from source)
- **dowitcher.exe** - File conversion utility (included)

### Installation

#### Option 1: Using the Executable (Recommended for End Users)

1. Download `file_conversion.exe`
2. Place it in your desired folder (e.g., `C:\File_conversion`)
3. Ensure the following files are in the same directory:
   - `dowitcher.exe`
   - `path.txt`
4. Double-click `file_conversion.exe` to start the server
5. **Configure Port**: When prompted, enter a port number or press Enter to use the default (3355)
   - Valid port range: 1-65535
   - Common ports: 3355 (default), 5000, 8080, 3000
   - If port is in use, choose a different one
6. Open your web browser and navigate to the URL shown (e.g., `http://localhost:3355`)

**Note**: The application will display the server URL after starting. Use this exact URL in your browser.

#### Option 2: Running from Source

```bash
# Navigate to the project directory
cd C:\File_conversion

# Install required dependencies
pip install flask

# Run the application
python workflows.py
```

When prompted, enter your preferred port number or press Enter for default (3355).

The application will start a local web server. Access it using the URL displayed in the terminal (e.g., `http://localhost:3355`)

---

## 📁 Project Structure

```
C:\File_conversion\
│
├── file_conversion.exe          # Main executable
├── workflows.py                 # Main application file (if running from source)
├── dowitcher.exe                # File conversion utility
├── path.txt                     # Configuration file with paths
├── README.md                    # Technical documentation
├── USER_GUIDE.md                # Detailed user guide
│
├── logs\                        # Application logs (auto-created)
│   └── workflows_YYYYMMDD.log
│
├── occ\                         # OCC application folder (example)
│   ├── input\                   # Input files (.txt)
│   ├── output\                  # Converted output files
│   ├── FF_FILES\
│   │   └── datamig\
│   │       └── file-format\    # Format files (.ff)
│   ├── datamatch\
│   │   ├── source\             # Source files for comparison
│   │   └── target\             # Target files for comparison
│   ├── copybook\               # Copybook files
│   └── expfd\                  # EXPFD files
│
├── rbs\                         # RBS application folder (example)
│   └── (same structure as occ)
│
└── mc\                          # MC application folder (example)
    └── (same structure as occ)
```

---

## ⚙️ Configuration

### Port Configuration

When starting the application, you'll be prompted to enter a port number:

```
============================================================
  FILE CONVERSION STUDIO - Server Configuration
============================================================

Enter port number to run the server (default: 3355):
```

**Options**:
- Press **Enter** to use default port 3355
- Enter a **custom port** number (1-65535)
- Common alternatives: 5000, 8080, 3000, 8000

**Why configure the port?**
- Default port may be in use by another application
- Corporate networks may restrict certain ports
- Multiple instances can run on different ports
- Some users prefer specific port numbers

**After starting**:
- The application displays: `Running on http://127.0.0.1:XXXX`
- Use this URL in your web browser
- Both `localhost` and `127.0.0.1` work

### path.txt Configuration

The `path.txt` file contains default paths for the application. Edit this file to match your setup:

```
FORMAT_PATH=C:/File_conversion/occ/FF_FILES/datamig/file-format
INPUT_PATH=C:/File_conversion/occ/input
OUTPUT_PATH=C:/File_conversion/occ/output
LOG_PATH=C:/File_conversion/logs
target=C:/File_conversion/occ/datamatch/target
source=C:/File_conversion/occ/datamatch/source
CSV_file=C:/File_conversion/occ.csv
copybook=C:/File_conversion/occ/copybook
expfd=C:/File_conversion/occ/expfd
application=C:/File_conversion/occ
all_file=paths
```

**Note:** Use forward slashes `/` even on Windows for path separators.

---

## 🎯 Features

### 1. **Create Folder Structure** 📁
- Automatically creates standardized folder structure for new applications
- Creates: input, output, FF_FILES, datamatch, source, target folders
- Ensures consistency across projects

### 2. **Open Project Folders** 🗂️
- Opens all relevant folders in Windows Explorer simultaneously
- Quick access to input, output, format files, source, and target folders

### 3. **Run Dowitcher (Convert to ASCII)** 🔧
- Converts EBCDIC files to ASCII format
- Uses format files (.ff) to define record structure
- Copies files to source/target folders for comparison

### 4. **Bulk Conversion** 📦
- Converts multiple files in one operation
- Processes all .txt files in input folder
- Shows detailed progress and success/error/skipped counts
- Color-coded results for easy identification

### 5. **Display Output** 👁️
- View converted output files
- Display specific records or ranges
- Easy verification of conversion results

### 6. **Display with Hex** 🔢
- View output with hexadecimal representation
- Useful for debugging data issues
- Shows both ASCII and hex values

### 7. **Particular Records** 📋
- Convert specific records from input files
- Use record ranges (e.g., 1-10 or 5)
- Selective conversion for testing

### 8. **Input Display Hex** 📄
- View input files with hex representation
- Includes field numbers and offsets
- Helps understand source data structure

### 9. **Update Paths** ⚙️
- Update configuration paths through web interface
- No need to edit text files manually
- Validates path changes

### 10. **View Logs** 📋
- View application logs directly in browser
- Shows last 10,000 log entries
- Date-based log files
- Track all operations and errors

---

## 🎨 User Interface Features

### Resizable Output Screens
- Drag bottom-right corner to resize output areas
- Horizontal and vertical scrolling
- Customizable view for large outputs

### Control Buttons
- **⬆️ Top**: Scroll to top of output
- **⬇️ Bottom**: Scroll to bottom of output
- **🔄 Reset Size**: Reset to default size
- **🗑️ Clear**: Clear output content
- **📋 Copy**: Copy output to clipboard

### Color-Coded Results
- 🟢 **Green**: Success messages
- 🔴 **Red**: Errors and skipped files
- 🟡 **Orange**: Warnings
- 🔵 **Blue**: Information messages

---

## 📊 Logging

All operations are logged to date-based log files in the `logs/` folder:
- **Format**: `workflows_YYYYMMDD.log`
- **Location**: `C:\File_conversion\logs\`
- **Content**: Timestamps, operations, commands, outputs, success/failure status
- **Retention**: Last 10,000 log entries displayed in web viewer
- **Access**: View logs through the application using the "View Logs" button

---

## 🔧 Troubleshooting

### Application Won't Start
- Ensure port is not in use by another application
- Try a different port number when prompted
- Check that `dowitcher.exe` is in the same folder
- Verify Python is installed (if running from source)
- Run as Administrator if permission errors occur

### Conversion Fails
- Verify format file (.ff) exists for the input file
- Check input file exists in the input folder
- Review logs for detailed error messages
- Ensure paths in `path.txt` are correct

### Files Not Found
- Verify folder structure matches configuration
- Check file names match exactly (case-sensitive)
- Ensure format files have .ff extension
- Ensure input files have .txt extension

### Browser Can't Connect
- Ensure the application is running (terminal window is open)
- Use the exact URL shown in the terminal (e.g., `http://localhost:3355`)
- Try `http://127.0.0.1:XXXX` instead of localhost (replace XXXX with your port)
- Check firewall settings
- Verify the port number matches what was configured at startup

---

## 🔒 Security Notes

- Application runs on localhost only (127.0.0.1)
- Not accessible from external networks by default
- For production use, configure proper authentication and HTTPS
- Keep logs directory secure as it contains operation details

---

## 📞 Support

For issues or questions:
- Check the **User Guide** for detailed instructions
- Review log files in the `logs/` folder
- Contact: Astadia TEAM

---

## 📄 License

Proprietary - Astadia TEAM  
All rights reserved.

---

## 🔄 Version History

### Version 2.0 (November 14, 2025)
- **Removed unused features**: Cleaned up Roy's EBCDIC Tool and FF Modify functions
- **Enhanced logging**: Log viewer now shows last 10,000 entries (increased from 100)
- **Improved branding**: Renamed to "File Conversion Studio" throughout
- **Code optimization**: Reduced codebase by ~550 lines (12% reduction)
- **Streamlined interface**: Focused on core conversion and management features
- **Better documentation**: Updated README and comprehensive user guide

### Version 1.0 (November 2025)
- Initial release
- Web-based interface for file conversion
- Bulk conversion support
- Multiple display modes
- Comprehensive logging
- Resizable output screens
- Color-coded results
- Unified logging system

---

## 🙏 Acknowledgments

- **Dowitcher** - File conversion utility
- **REXX** - Roy's EBCDIC tool interpreter
- **Flask** - Web framework
- **Astadia TEAM** - Development and support
