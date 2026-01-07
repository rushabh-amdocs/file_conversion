#!/usr/bin/env python3
"""
Test data generator for RecordSplitter
Creates sample input files with different record types for testing
"""

def pad_right(text: str, length: int) -> str:
    """Pad string to specified length with spaces"""
    if len(text) >= length:
        return text[:length]
    return text + ' ' * (length - len(text))


def create_fig_group_data() -> str:
    """Create 16 bytes of FIG group data"""
    # Setting some groups active (non-zero hex values)
    fig_bytes = bytes([
        0xF1, 0x02, 0x00, 0x04,
        0x05, 0x00, 0x00, 0x08,
        0x00, 0x0A, 0x00, 0x0C,
        0x00, 0x00, 0x0F, 0x10
    ])
    return fig_bytes.decode('latin-1')


def create_fig_data() -> str:
    """Create sample FIG data"""
    # Add data for active FIG groups
    group_data = [
        bytes([0xA1, 0xB2, 0xC3, 0xD4]),  # Group 1
        bytes([0xE1, 0xF2, 0x03, 0x14]),  # Group 4
        bytes([0x25, 0x36, 0x47, 0x58]),  # Group 5
        bytes([0x69, 0x7A, 0x8B, 0x9C]),  # Group 8
        bytes([0xAD, 0xBE, 0xCF, 0xD0]),  # Group 10
        bytes([0xE1, 0xF2, 0x03, 0x14]),  # Group 12
        bytes([0x25, 0x36, 0x47, 0x58]),  # Group 15
        bytes([0x69, 0x7A, 0x8B, 0x9C])   # Group 16
    ]
    
    fig_data = ''.join(group.decode('latin-1') for group in group_data)
    fig_data += pad_right("FIG SEGMENT DATA FOR TESTING PURPOSES WITH VARIOUS LENGTHS", 500)
    
    return fig_data


def generate_test_file_6084(filename: str):
    """Generate test file for record type 6084"""
    with open(filename, 'w', encoding='latin-1') as f:
        # Record 1: With 3-way split trigger (hex 101C)
        rec1 = pad_right("HEADER DATA FOR RECORD TYPE 6084 - RECORD 001", 80)
        rec1 += '\x10\x1C'  # Hex 101C
        rec1 += pad_right("DATA SEGMENT FOR 235 BYTES PART 1 TESTING WITH VARIOUS CHARACTERS", 235)
        rec1 += create_fig_group_data()
        rec1 += create_fig_data()
        f.write(rec1 + '\n')
        
        # Record 2: Without split trigger (hex 205C - not in list)
        rec2 = pad_right("HEADER DATA FOR RECORD TYPE 6084 - RECORD 002", 80)
        rec2 += '\x20\x5C'  # Hex 205C (not in split list)
        rec2 += pad_right("NORMAL DATA PROCESSING WITHOUT SPLIT", 100)
        f.write(rec2 + '\n')
        
        # Record 3: With another split trigger (hex 209C)
        rec3 = pad_right("HEADER DATA FOR RECORD TYPE 6084 - RECORD 003", 80)
        rec3 += '\x20\x9C'  # Hex 209C
        rec3 += pad_right("ANOTHER DATA SEGMENT FOR TESTING 3-WAY SPLIT FUNCTIONALITY", 235)
        rec3 += create_fig_group_data()
        rec3 += create_fig_data()
        f.write(rec3 + '\n')
    
    print(f"Generated {filename} (3 records)")


def generate_test_file_6064(filename: str):
    """Generate test file for record type 6064"""
    with open(filename, 'w', encoding='latin-1') as f:
        # Record 1: With split trigger
        rec1 = pad_right("HEADER DATA FOR RECORD TYPE 6064 - TEST 001", 60)
        rec1 += '\x14\x0C'  # Hex 140C
        rec1 += pad_right("DATA FOR 6064 TYPE RECORDS WITH SPLIT", 235)
        rec1 += create_fig_group_data()
        rec1 += create_fig_data()
        f.write(rec1 + '\n')
        
        # Record 2: Without split trigger
        rec2 = pad_right("HEADER DATA FOR RECORD TYPE 6064 - TEST 002", 60)
        rec2 += '\x30\x4C'  # Hex 304C (not in list)
        rec2 += pad_right("STANDARD PROCESSING", 80)
        f.write(rec2 + '\n')
    
    print(f"Generated {filename} (2 records)")


def generate_test_file_6044(filename: str):
    """Generate test file for record type 6044"""
    with open(filename, 'w', encoding='latin-1') as f:
        # Record 1: With split trigger
        rec1 = pad_right("HEADER FOR 6044 TYPE - REC 001", 40)
        rec1 += '\x21\x1C'  # Hex 211C
        rec1 += pad_right("6044 DATA SEGMENT FOR PROCESSING", 235)
        rec1 += create_fig_group_data()
        rec1 += create_fig_data()
        f.write(rec1 + '\n')
        
        # Record 2: Without split trigger
        rec2 = pad_right("HEADER FOR 6044 TYPE - REC 002", 40)
        rec2 += '\x40\x5C'  # Hex 405C (not in list)
        rec2 += pad_right("REGULAR DATA", 60)
        f.write(rec2 + '\n')
    
    print(f"Generated {filename} (2 records)")


def main():
    """Main entry point"""
    print("Generating test data for RecordSplitter...")
    
    generate_test_file_6084("test_input_6084.txt")
    generate_test_file_6064("test_input_6064.txt")
    generate_test_file_6044("test_input_6044.txt")
    
    print("\nTest files generated successfully!")
    print("  - test_input_6084.txt")
    print("  - test_input_6064.txt")
    print("  - test_input_6044.txt")
    print("\nUse these files with record_splitter.py:")
    print("  python record_splitter.py test_input_6084.txt sample_figlen.txt output_6084.txt 6084")


if __name__ == '__main__':
    main()
