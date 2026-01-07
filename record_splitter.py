#!/usr/bin/env python3
"""
RecordSplitter - Python implementation of REXX MPRECSPL
Processes ASCII files with record splitting logic based on record type and hex values

Record Types:
- 6084: Block size 23476, Prefix: RMCMFR, splits at position 80
- 6064: Block size 27998, Prefix: RMCDBA, splits at position 60  
- 6044: Block size 15476, Prefix: RMCWOA, splits at position 40
"""

import sys
import os
from typing import List, Dict, Optional

class RecordSplitter:
    """Main class for processing and splitting records"""
    
    # Record type constants
    RECORD_TYPE_6084 = 6084
    RECORD_TYPE_6064 = 6064
    RECORD_TYPE_6044 = 6044
    
    # Block sizes for each record type
    BLOCK_SIZES = {
        6084: 23476,
        6064: 27998,
        6044: 15476
    }
    
    # Hex values that trigger 3-way split
    SPLIT_HEX_LIST = {
        '101C', '103C', '140C', '141C', '142C', '143C', '145C', '146C',
        '209C', '211C', '215C', '221C', '231C', '261C', '265C', '291C',
        '294C', '295C', '307C', '308C', '309C', '310C', '314C', '315C',
        '319C', '321C', '326C', '334C', '338C', '975C'
    }
    
    def __init__(self):
        self.fig_lengths: Dict[int, int] = {}
        self.record_count = 0
        self.output_count = 0
        self.record_type = 0
        self.block_size = 0
        
    def process(self, input_file: str, figlen_file: str, output_file: str, 
                specified_record_length: Optional[int] = None):
        """Main processing method"""
        
        # Validate input files
        self._validate_file(input_file, "Input file")
        self._validate_file(figlen_file, "FIG length file")
        
        # Determine record type
        if specified_record_length:
            self.record_type = specified_record_length
        else:
            self.record_type = self._detect_record_type(input_file)
        
        # Set block size
        self.block_size = self.BLOCK_SIZES.get(self.record_type, 23476)
        
        print(f"Record Type: {self.record_type}")
        print(f"Block Size: {self.block_size}")
        print(f"Input File: {input_file}")
        print(f"Output File: {output_file}")
        print()
        
        # Load FIG lengths
        self._load_fig_lengths(figlen_file)
        
        # Process records
        self._process_records(input_file, output_file)
        
        print()
        print("Processing completed successfully.")
        print(f"Records processed: {self.record_count}")
        print(f"Output records created: {self.output_count}")
        
    def _validate_file(self, filepath: str, description: str):
        """Validate that a file exists"""
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"{description} does not exist: {filepath}")
    
    def _detect_record_type(self, input_file: str) -> int:
        """Detect record type from file"""
        print("Auto-detecting record type (defaulting to 6084)...")
        return self.RECORD_TYPE_6084
    
    def _load_fig_lengths(self, figlen_file: str):
        """Load FIG lengths from configuration file"""
        print("Reading and processing FIG LENGTH file...")
        
        with open(figlen_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for i, line in enumerate(lines, start=1):
            line = line.strip()
            if '|' in line:
                parts = line.split('|')
                if len(parts) >= 2:
                    try:
                        length = int(parts[1].strip())
                        self.fig_lengths[i] = length
                    except ValueError:
                        print(f"Warning: Invalid FIG length at line {i}: {line}")
        
        print(f"Read {len(lines)} records from FIG LENGTH file")
        print()
    
    def _process_records(self, input_file: str, output_file: str):
        """Process all records from input file"""
        print("Reading and processing input file...")
        
        output_records = []
        
        with open(input_file, 'r', encoding='latin-1') as f:
            for line in f:
                # Remove trailing newline
                line = line.rstrip('\n\r')
                self.record_count += 1
                self._process_record(line, output_records)
                
                # Progress indicator
                if self.record_count % 10000 == 0:
                    print(f"Processed {self.record_count} records...")
        
        # Write output file
        print("Writing output file...")
        self._write_output_file(output_file, output_records)
        print(f"Wrote {len(output_records)} records to output file")
    
    def _process_record(self, record: str, output_records: List[str]):
        """Process a single record"""
        current_rec = record
        
        # Step 1: Handle initial prefix based on record type
        if self.record_type == self.RECORD_TYPE_6084:
            if len(record) >= 80:
                part0 = record[:80]
                current_rec = record[80:]
                output_records.append('RMCMFR' + part0)
                self.output_count += 1
        elif self.record_type == self.RECORD_TYPE_6064:
            if len(record) >= 60:
                part0 = record[:60]
                current_rec = record[60:]
                output_records.append('RMCDBA' + part0)
                self.output_count += 1
        elif self.record_type == self.RECORD_TYPE_6044:
            if len(record) >= 40:
                part0 = record[:40]
                current_rec = record[40:]
                output_records.append('RMCWOA' + part0)
                self.output_count += 1
        
        # Step 2: Check hex value of first 2 bytes
        if len(current_rec) >= 2:
            first_2_bytes = current_rec[:2].encode('latin-1')
            hex_value = first_2_bytes.hex().upper()
            hex_numeric = hex_value[:min(3, len(hex_value))]
            
            # Check if hex value triggers 3-way split
            if hex_value in self.SPLIT_HEX_LIST:
                self._split_record_3_way(current_rec, hex_numeric, output_records)
            else:
                self._write_record_as_is(current_rec, hex_numeric, output_records)
        else:
            # Record too short, write as-is
            self._write_record_as_is(current_rec, '000', output_records)
    
    def _split_record_3_way(self, current_rec: str, hex_numeric: str, 
                           output_records: List[str]):
        """Split record into 3 parts based on hex value"""
        rec_len = len(current_rec)
        
        # Part 1: First 235 bytes with prefix
        if rec_len >= 235:
            part1 = current_rec[:235]
            try:
                prefix1 = f"CLS{int(hex_numeric, 16):03d}"
            except ValueError:
                prefix1 = "CLS000"
            output_records.append(prefix1 + part1)
            self.output_count += 1
            
            # Part 2 and 3: Process FIG data
            if rec_len > 235:
                remaining = current_rec[235:]
                self._process_fig_data(remaining, output_records)
        else:
            # Record shorter than 235, treat as write-as-is
            self._write_record_as_is(current_rec, hex_numeric, output_records)
    
    def _process_fig_data(self, remaining: str, output_records: List[str]):
        """Process FIG data (extract flags and split by FIG lengths)"""
        if len(remaining) < 16:
            return
        
        # Extract first 16 bytes (FIG group flags)
        first_16_bytes = remaining[:16]
        output_records.append('GRPFIG' + first_16_bytes)
        self.output_count += 1
        
        fig_grp_bytes = first_16_bytes.encode('latin-1')
        fig_grp_hex = fig_grp_bytes.hex().upper()
        
        # Parse FIG group flags (1-indexed)
        fig_grp = [0] * 32
        for j in range(min(31, len(fig_grp_hex))):
            try:
                fig_grp[j + 1] = int(fig_grp_hex[j], 16)
            except ValueError:
                fig_grp[j + 1] = 0
        
        # Process each FIG group
        current_pos = 16
        fig_index = 1
        fig = [0] * 218  # FIG flags array (1-indexed)
        
        for grp in range(1, 32):
            if fig_grp[grp] != 0:
                # This group is active, read next 4 bytes
                if current_pos + 4 <= len(remaining):
                    fig_data = remaining[current_pos:current_pos + 4]
                    fig_bytes = fig_data.encode('latin-1')
                    fig_hex = fig_bytes.hex().upper()
                    
                    output_records.append(f'GRFI{grp:02d}' + fig_data)
                    self.output_count += 1
                    
                    # Populate 7 FIG flags
                    for fig_num in range(min(7, len(fig_hex))):
                        try:
                            fig[fig_index] = int(fig_hex[fig_num], 16)
                        except ValueError:
                            fig[fig_index] = 0
                        fig_index += 1
                    
                    current_pos += 4
                else:
                    print(f"Warning: Record {self.record_count} Group {grp} "
                          f"insufficient data at position {current_pos}")
                    fig_index += 7
            else:
                # Group not active, skip 7 FIG flags
                fig_index += 7
        
        # Part 3: Process remaining data based on FIG flags
        if current_pos < len(remaining):
            part3 = remaining[current_pos:]
            self._process_fig_flags(part3, fig, output_records)
    
    def _process_fig_flags(self, part3: str, fig: List[int], 
                          output_records: List[str]):
        """Process FIG flags and split records accordingly"""
        if len(part3) > 0:
            output_records.append('FIG00@' + part3)
            self.output_count += 1
        
        remaining_part3 = part3
        
        for fig_index in range(1, min(132, len(fig))):
            if fig[fig_index] == 1 and len(remaining_part3) > 0:
                ext_len = self.fig_lengths.get(fig_index)
                if ext_len is None:
                    continue
                
                if len(remaining_part3) >= ext_len:
                    fig_data = remaining_part3[:ext_len]
                    
                    # Special handling for FIG 100
                    if fig_index == 100:
                        if len(fig_data) > 8 and fig_data[8] == '0':
                            output_records.append(f'FIG{fig_index:03d}' + fig_data)
                            self.output_count += 1
                        else:
                            output_records.append('FIG10E' + fig_data)
                            self.output_count += 1
                    else:
                        output_records.append(f'FIG{fig_index:03d}' + fig_data)
                        self.output_count += 1
                    
                    remaining_part3 = remaining_part3[ext_len:]
    
    def _write_record_as_is(self, current_rec: str, hex_numeric: str, 
                           output_records: List[str]):
        """Write record as-is with prefix"""
        try:
            prefix = f"CLS{int(hex_numeric, 16):03d}"
        except ValueError:
            prefix = "CLS000"
        output_records.append(prefix + current_rec)
        self.output_count += 1
    
    def _write_output_file(self, output_file: str, records: List[str]):
        """Write output records to file"""
        with open(output_file, 'w', encoding='latin-1') as f:
            for record in records:
                f.write(record + '\n')


def main():
    """Main entry point"""
    if len(sys.argv) < 4:
        print("Usage: python record_splitter.py <input_file> <figlen_file> <output_file> [record_length]")
        print("  record_length: optional, one of 6084, 6064, 6044 (auto-detected if not specified)")
        sys.exit(1)
    
    input_file = sys.argv[1]
    figlen_file = sys.argv[2]
    output_file = sys.argv[3]
    specified_record_length = None
    
    if len(sys.argv) > 4:
        try:
            specified_record_length = int(sys.argv[4])
        except ValueError:
            print(f"Invalid record length: {sys.argv[4]}")
            sys.exit(1)
    
    splitter = RecordSplitter()
    
    try:
        splitter.process(input_file, figlen_file, output_file, specified_record_length)
    except Exception as e:
        print(f"Error processing file: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
