@echo off
REM Batch script to compile and run RecordSplitter
REM Usage: run_splitter.bat <input_file> <figlen_file> <output_file> [record_length]

echo ========================================
echo RecordSplitter - Java Batch Runner
echo ========================================
echo.

REM Check if Java is installed
java -version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Java is not installed or not in PATH
    echo Please install Java 8 or higher
    pause
    exit /b 1
)

REM Check if source file exists
if not exist "RecordSplitter.java" (
    echo ERROR: RecordSplitter.java not found
    echo Please ensure the Java source file is in the current directory
    pause
    exit /b 1
)

REM Compile the Java program
echo Compiling RecordSplitter.java...
javac RecordSplitter.java
if errorlevel 1 (
    echo ERROR: Compilation failed
    pause
    exit /b 1
)
echo Compilation successful!
echo.

REM Check command line arguments
if "%~1"=="" (
    echo Usage: run_splitter.bat ^<input_file^> ^<figlen_file^> ^<output_file^> [record_length]
    echo.
    echo Example: run_splitter.bat input.txt sample_figlen.txt output.txt 6084
    echo.
    pause
    exit /b 1
)

if "%~2"=="" (
    echo ERROR: FIG length file not specified
    echo Usage: run_splitter.bat ^<input_file^> ^<figlen_file^> ^<output_file^> [record_length]
    pause
    exit /b 1
)

if "%~3"=="" (
    echo ERROR: Output file not specified
    echo Usage: run_splitter.bat ^<input_file^> ^<figlen_file^> ^<output_file^> [record_length]
    pause
    exit /b 1
)

REM Check if input file exists
if not exist "%~1" (
    echo ERROR: Input file not found: %~1
    pause
    exit /b 1
)

REM Check if FIG length file exists
if not exist "%~2" (
    echo ERROR: FIG length file not found: %~2
    pause
    exit /b 1
)

REM Run the program
echo Running RecordSplitter...
echo.
echo Input File:  %~1
echo FigLen File: %~2
echo Output File: %~3
if not "%~4"=="" (
    echo Record Type: %~4
)
echo.
echo ========================================
echo.

if "%~4"=="" (
    java RecordSplitter "%~1" "%~2" "%~3"
) else (
    java RecordSplitter "%~1" "%~2" "%~3" "%~4"
)

if errorlevel 1 (
    echo.
    echo ========================================
    echo ERROR: Processing failed
    echo ========================================
    pause
    exit /b 1
)

echo.
echo ========================================
echo Processing completed successfully!
echo ========================================
echo.
echo Output file created: %~3
echo.

pause
