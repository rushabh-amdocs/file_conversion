# SmartFile Converter - High-Level Architecture

```mermaid
flowchart TB
    Browser["🌐 Web Browser Port 3344"]
    
    subgraph Flask["Flask Web Application"]
        App["Flask App file.py"]
        MainPage["Main Dashboard"]
        ModifyPage["Modify Template"]
        RenamePage["Rename Template"]
        RoyPage["ROY Template"]
    end
    
    subgraph Core["Core Functions"]
        ReadPaths["read_paths"]
        RenameFunc["rename_file"]
        ModifyFunc["run_file_modify"]
        RexxFunc["run_rexx"]
        DowitcherFunc["run_dowitcher"]
    end
    
    subgraph External["External Tools"]
        FileMod["File_modify.py"]
        RexxExe["rexx.exe"]
        RexxScript["RoysEbcdicRecTypesV6.rexx"]
        DowitcherExe["dowitcher.exe"]
    end
    
    subgraph Files["File System"]
        Config["path.txt Config"]
        FormatPath["FORMAT_PATH .ff files"]
        InputPath["INPUT_PATH .txt files"]
        OutputPath["OUTPUT_PATH output"]
    end
    
    Browser -->|HTTP Request| App
    App --> MainPage
    App --> ModifyPage
    App --> RenamePage
    App --> RoyPage
    
    MainPage --> ReadPaths
    MainPage --> RenameFunc
    MainPage --> DowitcherFunc
    ModifyPage --> ModifyFunc
    RenamePage --> RenameFunc
    RoyPage --> RexxFunc
    
    ReadPaths --> Config
    RenameFunc --> FormatPath
    ModifyFunc --> FileMod
    RexxFunc --> RexxExe
    RexxFunc --> RexxScript
    DowitcherFunc --> DowitcherExe
    
    FileMod --> FormatPath
    RexxExe --> InputPath
    RexxExe --> OutputPath
    DowitcherExe --> FormatPath
    DowitcherExe --> InputPath
    DowitcherExe --> OutputPath
    
    classDef userLayer fill:#3b82f6,stroke:#1e40af,stroke-width:3px,color:#fff
    classDef flaskLayer fill:#2563eb,stroke:#1e40af,stroke-width:2px,color:#fff
    classDef coreLayer fill:#1e40af,stroke:#1e3a8a,stroke-width:2px,color:#fff
    classDef externalLayer fill:#7c3aed,stroke:#5b21b6,stroke-width:2px,color:#fff
    classDef fileLayer fill:#059669,stroke:#047857,stroke-width:2px,color:#fff
    
    class Browser userLayer
    class App,MainPage,ModifyPage,RenamePage,RoyPage flaskLayer
    class ReadPaths,RenameFunc,ModifyFunc,RexxFunc,DowitcherFunc coreLayer
    class FileMod,RexxExe,RexxScript,DowitcherExe externalLayer
    class Config,FormatPath,InputPath,OutputPath fileLayer
```

## Architecture Overview

### **1. User Interface Layer** 🌐
- Web browser interface accessible on port 3344
- Clean, modern dark blue theme with professional styling
- Real-time loading indicators for all operations
- Responsive design for desktop and mobile

### **2. Flask Web Application** 🚀
- **Main Application**: Flask server handling HTTP requests
- **Route Handlers**: Manages 9 different page templates
- **Templates**: 4 main HTML templates (Home, Modify, Rename, ROY)
- **Session Management**: Handles user interactions and form submissions

### **3. Core Business Logic** ⚙️
- **read_paths()**: Parses configuration from path.txt
- **rename_file()**: Handles file renaming with retry logic
- **run_file_modify()**: Manages file modification subprocess
- **run_rexx()**: Executes REXX conversion for EBCDIC files
- **run_dowitcher()**: Main conversion engine with multiple modes

### **4. External Tools & Scripts** 🔌
- **File_modify.py**: Python script for modifying .ff file structure
- **rexx.exe**: REXX interpreter for mainframe conversion
- **RoysEbcdicRecTypesV6.rexx**: EBCDIC to ASCII conversion script
- **dowitcher.exe**: Primary conversion tool for data transformation

### **5. File System** 💾
- **Configuration**: path.txt stores all directory paths
- **FORMAT_PATH**: Stores .ff format definition files
- **INPUT_PATH**: Contains .txt input files for processing
- **OUTPUT_PATH**: Stores converted output files
- **SOURCE/TARGET**: Folders for data comparison and validation

### **6. Main Operations** 🔄
1. **Rename .FF File**: Quick file renaming functionality
2. **Modify .FF File**: Update file structure (FB/VB types)
3. **Run Dowitcher**: Execute primary conversion
4. **Display Output**: View converted data results
5. **Run Roys Tool**: EBCDIC to ASCII conversion
6. **Display with Hex**: Technical hexadecimal view
7. **Convert Records**: Specific record range conversion
8. **Input with Hex**: Hexadecimal data input
9. **Update Paths**: Configure directory locations

## Data Flow

1. **User Request** → Browser sends HTTP request to Flask
2. **Route Processing** → Flask routes request to appropriate handler
3. **Core Logic** → Business logic functions process the request
4. **External Tools** → External executables perform conversions
5. **File Operations** → Read/write operations on file system
6. **Response** → Results returned through Flask to browser

## Key Features

- ✅ **Retry Logic**: Handles file system delays (3 retries, 0.5s delay)
- ✅ **Override Mode**: Automatically overwrites existing files
- ✅ **Error Handling**: Comprehensive try-catch blocks with detailed error messages
- ✅ **Configuration Management**: Centralized path configuration
- ✅ **Multiple Conversion Modes**: Display, convert, hex view, specific records
- ✅ **File Validation**: Checks file existence before processing
- ✅ **Professional UI**: Dark theme with loading indicators and tooltips
