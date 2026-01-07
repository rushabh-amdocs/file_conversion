# RecordSplitter - Java Implementation of REXX MPRECSPL

## Overview

This Java application replicates the functionality of the REXX MPRECSPL program for ASCII files. It identifies three file types based on record length and applies sophisticated split logic to process mainframe data files.

## Features

### Record Type Detection
The program supports three record types based on record length:

| Record Type | Block Size | Prefix   | Split Position |
|------------|-----------|----------|----------------|
| 6084       | 23476     | RMCMFR   | 80             |
| 6064       | 27998     | RMCDBA   | 60             |
| 6044       | 15476     | RMCWOA   | 40             |

### Processing Logic

1. **Initial Split**: Based on record type, extracts initial portion with appropriate prefix
2. **Hex Value Detection**: Examines first 2 bytes of remaining data
3. **Conditional Processing**:
   - If hex value matches predefined list: Performs 3-way split
   - Otherwise: Writes record as-is with prefix

### 3-Way Split Logic

When triggered by specific hex values, records are split into:

1. **Part 1**: First 235 bytes with `CLS` prefix
2. **Part 2**: FIG group flags (16 bytes) with `GRPFIG` prefix
3. **Part 3**: Variable-length FIG data segments based on configuration

### Hex Values Triggering 3-Way Split

```
101C, 103C, 140C, 141C, 142C, 143C, 145C, 146C,
209C, 211C, 215C, 221C, 231C, 261C, 265C, 291C,
294C, 295C, 307C, 308C, 309C, 310C, 314C, 315C,
319C, 321C, 326C, 334C, 338C, 975C
```

## Usage

### Compilation

```bash
javac RecordSplitter.java
```

### Execution

```bash
java RecordSplitter <input_file> <figlen_file> <output_file> [record_length]
```

**Parameters:**
- `input_file`: Path to ASCII input file to process
- `figlen_file`: Path to FIG length configuration file
- `output_file`: Path for output file
- `record_length`: (Optional) Specify record type: 6084, 6064, or 6044

### Examples

#### Auto-detect record type:
```bash
java RecordSplitter input.txt figlen.txt output.txt
```

#### Specify record type:
```bash
java RecordSplitter input.txt figlen.txt output.txt 6084
```

#### Windows PowerShell:
```powershell
java RecordSplitter C:\data\input.txt C:\config\figlen.txt C:\output\result.txt 6064
```

## FIG Length Configuration File Format

The FIG length file should contain pipe-delimited records:

```
FIG001|25
FIG002|30
FIG003|15
...
```

Format: `<description>|<length>`

Each line defines the length for a FIG segment (1-based index matching line number).

## Output Format

The program generates multiple output records from each input record:

### Prefixes Used:

- `RMCMFR` / `RMCDBA` / `RMCWOA`: Initial record portion (based on type)
- `CLS###`: Classification record (### = hex value in decimal)
- `GRPFIG`: FIG group flags (16 bytes)
- `GRFI##`: FIG group data (## = group number 01-31)
- `FIG###`: Individual FIG segment (### = FIG index 001-131)
- `FIG10E`: Special handling for FIG 100
- `FIG00@`: Remaining FIG data

## Key Differences from REXX Version

### ASCII vs EBCDIC
- Uses `ISO-8859-1` encoding for ASCII files
- Hex conversion adapted for ASCII character set
- Line-oriented reading (vs fixed-block in mainframe)

### File Handling
- Standard Java I/O instead of TSO/MVS ALLOCATE
- Buffered reading for efficiency
- Automatic file creation (no explicit allocation needed)

### Memory Management
- Reads entire file into memory for processing
- Suitable for large files with progress indicators
- Uses ArrayList for dynamic output collection

## Implementation Details

### Character Encoding
```java
StandardCharsets.ISO_8859_1
```
Used for proper byte-to-hex conversion of ASCII data.

### Hex Conversion
```java
private String bytesToHex(byte[] bytes) {
    StringBuilder sb = new StringBuilder();
    for (byte b : bytes) {
        sb.append(String.format("%02X", b & 0xFF));
    }
    return sb.toString();
}
```

### Record Processing Flow
```
Input Record
    ↓
Extract Initial Portion (by record type)
    ↓
Check First 2 Bytes (Hex)
    ↓
    ├─→ Match Split List? → 3-Way Split
    │                           ├─→ Part 1 (235 bytes)
    │                           ├─→ Part 2 (FIG groups)
    │                           └─→ Part 3 (FIG segments)
    │
    └─→ No Match → Write As-Is with CLS prefix
```

## Error Handling

The program includes comprehensive error handling:

- File existence validation
- Record length verification
- FIG length parsing with warnings
- Graceful handling of short records
- Progress indicators for large files

## Performance Considerations

- **Progress Indicators**: Updates every 10,000 records
- **Buffered I/O**: Efficient file reading/writing
- **Memory**: Suitable for files with millions of records
- **Encoding**: ISO-8859-1 for binary-safe ASCII processing

## Troubleshooting

### Issue: Incorrect hex values detected
**Solution**: Verify input file encoding is ASCII/ISO-8859-1

### Issue: Missing FIG segments in output
**Solution**: Check FIG length configuration file format (pipe-delimited)

### Issue: Output file too large
**Solution**: Normal behavior - one input record generates multiple output records

### Issue: "Invalid record length" error
**Solution**: Use valid record type (6084, 6064, or 6044) or omit for auto-detection

## Sample Data Flow

### Input Record (Record Type 6084):
```
[80 bytes header][2-byte hex: 101C][235 bytes data][16 bytes FIG groups][variable FIG data]
```

### Output Records:
```
RMCMFR[80 bytes header]
CLS257[235 bytes data]
GRPFIG[16 bytes FIG groups]
GRFI01[4 bytes group 1 data]
GRFI05[4 bytes group 5 data]
FIG00@[remaining data]
FIG001[segment 1]
FIG015[segment 15]
...
```

## Extending the Program

### Adding New Record Types
Modify the switch statement in `process()` method:
```java
case RECORD_TYPE_XXXX:
    blockSize = BLOCK_SIZE_XXXX;
    break;
```

### Adding New Hex Values
Update the `SPLIT_HEX_LIST` Set:
```java
private static final Set<String> SPLIT_HEX_LIST = new HashSet<>(Arrays.asList(
    "101C", "103C", ..., "NEWVALUE"
));
```

### Custom FIG Processing
Modify the `processFigFlags()` method to implement custom logic.

## Version Compatibility

- **Java Version**: Java 8 or higher
- **Character Encoding**: ISO-8859-1 (Latin-1)
- **Line Separators**: Platform-independent (uses `newLine()`)

## License

This is a conversion of mainframe REXX code to Java for ASCII file processing.

## Author

Converted from REXX MPRECSPL to Java for ASCII file compatibility.

## Support

For issues or questions:
1. Verify input file format matches expected structure
2. Check FIG length configuration file
3. Review console output for warnings
4. Examine first few output records for correctness
