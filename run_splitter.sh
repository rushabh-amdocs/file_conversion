#!/bin/bash
# Shell script to compile and run RecordSplitter
# Usage: ./run_splitter.sh <input_file> <figlen_file> <output_file> [record_length]

echo "========================================"
echo "RecordSplitter - Java Shell Runner"
echo "========================================"
echo ""

# Check if Java is installed
if ! command -v java &> /dev/null; then
    echo "ERROR: Java is not installed or not in PATH"
    echo "Please install Java 8 or higher"
    exit 1
fi

if ! command -v javac &> /dev/null; then
    echo "ERROR: Java compiler (javac) is not installed or not in PATH"
    echo "Please install JDK 8 or higher"
    exit 1
fi

# Check if source file exists
if [ ! -f "RecordSplitter.java" ]; then
    echo "ERROR: RecordSplitter.java not found"
    echo "Please ensure the Java source file is in the current directory"
    exit 1
fi

# Compile the Java program
echo "Compiling RecordSplitter.java..."
javac RecordSplitter.java
if [ $? -ne 0 ]; then
    echo "ERROR: Compilation failed"
    exit 1
fi
echo "Compilation successful!"
echo ""

# Check command line arguments
if [ $# -lt 3 ]; then
    echo "Usage: $0 <input_file> <figlen_file> <output_file> [record_length]"
    echo ""
    echo "Example: $0 input.txt sample_figlen.txt output.txt 6084"
    echo ""
    exit 1
fi

# Check if input file exists
if [ ! -f "$1" ]; then
    echo "ERROR: Input file not found: $1"
    exit 1
fi

# Check if FIG length file exists
if [ ! -f "$2" ]; then
    echo "ERROR: FIG length file not found: $2"
    exit 1
fi

# Run the program
echo "Running RecordSplitter..."
echo ""
echo "Input File:  $1"
echo "FigLen File: $2"
echo "Output File: $3"
if [ ! -z "$4" ]; then
    echo "Record Type: $4"
fi
echo ""
echo "========================================"
echo ""

if [ -z "$4" ]; then
    java RecordSplitter "$1" "$2" "$3"
else
    java RecordSplitter "$1" "$2" "$3" "$4"
fi

if [ $? -ne 0 ]; then
    echo ""
    echo "========================================"
    echo "ERROR: Processing failed"
    echo "========================================"
    exit 1
fi

echo ""
echo "========================================"
echo "Processing completed successfully!"
echo "========================================"
echo ""
echo "Output file created: $3"
echo ""
