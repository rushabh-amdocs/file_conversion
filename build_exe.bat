@echo off
echo ============================================
echo Building File Conversion Tool Executable
echo ============================================
echo.

REM Prompt user for executable name
set /p EXE_NAME="Enter the name for the executable (without .exe): "
if "%EXE_NAME%"=="" (
    echo Error: Executable name cannot be empty!
    pause
    exit /b 1
)

REM Prompt user for script name
set /p SCRIPT_NAME="Enter the Python script name (e.g., file.py): "
if "%SCRIPT_NAME%"=="" (
    echo Error: Script name cannot be empty!
    pause
    exit /b 1
)

REM Check if script file exists
if not exist "%SCRIPT_NAME%" (
    echo Error: Script file '%SCRIPT_NAME%' not found!
    pause
    exit /b 1
)

echo.
echo Configuration:
echo   Executable Name: %EXE_NAME%.exe
echo   Script Name: %SCRIPT_NAME%
echo.

REM Install PyInstaller if not already installed
echo Checking PyInstaller installation...
python -c "import PyInstaller" 2>nul
if errorlevel 1 (
    echo PyInstaller not found. Installing...
    python -m pip install pyinstaller
) else (
    echo PyInstaller is already installed.
)
echo.

REM Clean previous builds
echo Cleaning previous builds...
if exist "build" rmdir /s /q "build"
if exist "dist" rmdir /s /q "dist"
if exist "%EXE_NAME%.spec" del /f "%EXE_NAME%.spec"
echo.

REM Build the executable
echo Building executable...
python -m PyInstaller --onefile ^
    --name %EXE_NAME% ^
    --icon=NONE ^
    --hidden-import=flask ^
    --hidden-import=werkzeug ^
    --hidden-import=jinja2 ^
    --hidden-import=click ^
    --hidden-import=itsdangerous ^
    --hidden-import=markupsafe ^
    --collect-all flask ^
    --console ^
    %SCRIPT_NAME%


echo.
if exist "dist\%EXE_NAME%.exe" (
    echo ============================================
    echo Build Successful!
    echo ============================================
    echo Executable location: dist\%EXE_NAME%.exe
    echo.
    echo To run: dist\%EXE_NAME%.exe
    echo The Flask server will start on http://127.0.0.1:5000
) else (
    echo ============================================
    echo Build Failed!
    echo ============================================
    echo Please check the error messages above.
)
echo.
pause
