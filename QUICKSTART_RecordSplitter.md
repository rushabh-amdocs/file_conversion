# RecordSplitter Quick Start Guide

## Overview
Java implementation of REXX MPRECSPL for processing ASCII mainframe files with record splitting logic.

## Quick Start (Windows)

### Step 1: Compile the Program
```powershell
javac RecordSplitter.java
```

### Step 2: Generate Test Data (Optional)
```powershell
javac RecordSplitterTestDataGenerator.java
java RecordSplitterTestDataGenerator
```

This creates:
- `test_input_6084.txt` (record type 6084)
- `test_input_6064.txt` (record type 6064)
- `test_input_6044.txt` (record type 6044)

### Step 3: Run the Splitter

**Option A: Using batch file (easiest)**
```powershell
.\run_splitter.bat test_input_6084.txt sample_figlen.txt output_6084.txt 6084
```

**Option B: Direct Java command**
```powershell
java RecordSplitter test_input_6084.txt sample_figlen.txt output_6084.txt 6084
```

### Step 4: Review Output
```powershell
type output_6084.txt | more
```

## Quick Start (Linux/Unix)

### Step 1: Compile
```bash
javac RecordSplitter.java
```

### Step 2: Generate Test Data (Optional)
```bash
javac RecordSplitterTestDataGenerator.java
java RecordSplitterTestDataGenerator
```

### Step 3: Run the Splitter

**Option A: Using shell script**
```bash
chmod +x run_splitter.sh
./run_splitter.sh test_input_6084.txt sample_figlen.txt output_6084.txt 6084
```

**Option B: Direct Java command**
```bash
java RecordSplitter test_input_6084.txt sample_figlen.txt output_6084.txt 6084
```

### Step 4: Review Output
```bash
less output_6084.txt
```

## File Descriptions

| File | Description |
|------|-------------|
| `RecordSplitter.java` | Main program - converts REXX logic to Java |
| `RecordSplitterTestDataGenerator.java` | Creates test input files |
| `sample_figlen.txt` | Sample FIG length configuration |
| `run_splitter.bat` | Windows batch runner script |
| `run_splitter.sh` | Linux/Unix shell runner script |
| `RecordSplitter_README.md` | Complete documentation |

## Command Syntax

```
java RecordSplitter <input_file> <figlen_file> <output_file> [record_type]
```

**Parameters:**
- `input_file`: Your ASCII input file
- `figlen_file`: FIG length configuration (pipe-delimited)
- `output_file`: Where to write results
- `record_type`: Optional - 6084, 6064, or 6044

## Processing Example

**Input Record (Record Type 6084):**
```
[80 chars header][2-byte hex][variable data...]
```

**Output Records:**
```
RMCMFR[80 chars header]
CLS257[235 chars data]
GRPFIG[16 bytes FIG groups]
GRFI01[4 bytes group data]
FIG00@[remaining data]
FIG001[segment based on figlen]
...
```

## Record Types

| Type | Prefix | Split At | Block Size | Use Case |
|------|--------|----------|------------|----------|
| 6084 | RMCMFR | 80 bytes | 23476 | Default mainframe records |
| 6064 | RMCDBA | 60 bytes | 27998 | Database records |
| 6044 | RMCWOA | 40 bytes | 15476 | Work area records |

## Hex Values Triggering 3-Way Split

The program checks the first 2 bytes after the header. If they match these hex values, it performs a 3-way split:

```
101C, 103C, 140C, 141C, 142C, 143C, 145C, 146C,
209C, 211C, 215C, 221C, 231C, 261C, 265C, 291C,
294C, 295C, 307C, 308C, 309C, 310C, 314C, 315C,
319C, 321C, 326C, 334C, 338C, 975C
```

## FIG Length File Format

Create a pipe-delimited text file:
```
FIG001|25
FIG002|30
FIG003|15
...
```

Line number corresponds to FIG index. The number after `|` is the byte length.

## Common Use Cases

### 1. Process Production File
```powershell
java RecordSplitter production_data.txt company_figlen.txt output_split.txt 6084
```

### 2. Test New Configuration
```powershell
# Generate test data
java RecordSplitterTestDataGenerator

# Process with test config
java RecordSplitter test_input_6084.txt new_figlen.txt test_output.txt 6084
```

### 3. Batch Processing Multiple Files
**Windows:**
```batch
for %%f in (*.txt) do (
    java RecordSplitter %%f sample_figlen.txt output_%%f 6084
)
```

**Linux:**
```bash
for f in *.txt; do
    java RecordSplitter "$f" sample_figlen.txt "output_$f" 6084
done
```

## Troubleshooting

### Error: "File not found"
- Verify file paths are correct
- Use absolute paths if relative paths fail
- Check file permissions

### Error: "Java not found"
- Install JDK 8 or higher
- Ensure `java` and `javac` are in system PATH

### Incorrect Output
- Verify input file encoding (should be ASCII/ISO-8859-1)
- Check FIG length file format (pipe-delimited)
- Confirm correct record type parameter

### Output Too Large
- Normal behavior - one input record creates multiple output records
- Each FIG segment becomes a separate output line

## Performance Tips

- **Large Files**: The program processes files in chunks with progress indicators
- **Memory**: Suitable for files with millions of records
- **Encoding**: Uses ISO-8859-1 for proper byte handling

## Next Steps

1. **Read Full Documentation**: See `RecordSplitter_README.md`
2. **Customize FIG Lengths**: Edit `sample_figlen.txt` for your data
3. **Integrate**: Add to your data processing pipeline
4. **Extend**: Modify Java code for custom requirements

## Support

For detailed information:
- Full documentation: `RecordSplitter_README.md`
- Source code comments in `RecordSplitter.java`
- Original REXX code: `GB6589.REXX(MPRECSPL)`

## Version
Java 8+ compatible | ISO-8859-1 encoding | Cross-platform
