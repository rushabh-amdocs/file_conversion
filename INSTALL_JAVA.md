# Java Installation Guide for Windows

## Quick Install Options

### Option 1: Install via Winget (Recommended - Fastest)

Open PowerShell as Administrator and run:

```powershell
# Install OpenJDK 17 (LTS version)
winget install Microsoft.OpenJDK.17

# OR install Oracle Java 21 (Latest LTS)
winget install Oracle.JDK.21

# OR install Amazon Corretto 17
winget install Amazon.Corretto.17
```

After installation, **restart your terminal** or run:
```powershell
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

### Option 2: Install via Chocolatey

If you have Chocolatey installed:

```powershell
# Run as Administrator
choco install openjdk17
```

### Option 3: Manual Installation

#### Microsoft OpenJDK (Recommended for Windows)
1. Download from: https://learn.microsoft.com/en-us/java/openjdk/download
2. Choose: **Microsoft Build of OpenJDK 17 (LTS)** for Windows x64
3. Download the MSI installer
4. Run the installer
5. Restart PowerShell

#### Oracle Java
1. Download from: https://www.oracle.com/java/technologies/downloads/
2. Choose: **Java 17 LTS** or **Java 21 LTS**
3. Download Windows x64 Installer
4. Run the installer
5. Restart PowerShell

#### Amazon Corretto
1. Download from: https://aws.amazon.com/corretto/
2. Choose: **Amazon Corretto 17** for Windows
3. Download the MSI installer
4. Run the installer
5. Restart PowerShell

## Verify Installation

After installing, open a **new PowerShell window** and verify:

```powershell
java -version
javac -version
```

You should see output like:
```
openjdk version "17.0.x" 2024-xx-xx
OpenJDK Runtime Environment Microsoft-xxxxxxx (build 17.0.x+x)
OpenJDK 64-Bit Server VM Microsoft-xxxxxxx (build 17.0.x+x, mixed mode, sharing)
```

## Troubleshooting

### Java not recognized after installation

1. **Check Java installation path:**
```powershell
Get-ChildItem "C:\Program Files\Microsoft\" -Recurse -Filter java.exe
# OR
Get-ChildItem "C:\Program Files\Java\" -Recurse -Filter java.exe
```

2. **Manually add to PATH (if needed):**
```powershell
# Replace with your actual Java path
$javaPath = "C:\Program Files\Microsoft\jdk-17.0.x-hotspot\bin"

# Add to user PATH
[Environment]::SetEnvironmentVariable("Path", $env:Path + ";$javaPath", "User")

# Refresh current session
$env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
```

3. **Restart PowerShell** after making PATH changes

## Quick Test After Installation

Once Java is installed, test the RecordSplitter:

```powershell
# Navigate to your project
cd C:\File_conversion

# Compile the Java program
javac RecordSplitter.java

# Generate test data (using Java)
javac RecordSplitterTestDataGenerator.java
java RecordSplitterTestDataGenerator

# Run the splitter
java RecordSplitter test_input_6084.txt sample_figlen.txt output_6084.txt 6084
```

## Alternative: Use Python Version (No Java Required)

I've already created a Python version that works identically. Use this if you prefer not to install Java:

```powershell
# Generate test data
python generate_test_data.py

# Run the splitter
python record_splitter.py test_input_6084.txt sample_figlen.txt output_6084.txt 6084
```

## Recommended: Microsoft OpenJDK via Winget

This is the easiest and fastest method:

```powershell
# Run as Administrator
winget install Microsoft.OpenJDK.17

# Close and reopen PowerShell, then verify
java -version
javac -version
```

## Next Steps

After Java is installed:
1. ✅ Verify with `java -version` and `javac -version`
2. ✅ Compile: `javac RecordSplitter.java`
3. ✅ Generate test data: `java RecordSplitterTestDataGenerator`
4. ✅ Run: `java RecordSplitter test_input_6084.txt sample_figlen.txt output_6084.txt 6084`

---

**Note:** Both Java and Python versions provide identical functionality. Choose based on your preference or existing infrastructure.
