import java.io.*;
import java.nio.charset.StandardCharsets;

/**
 * Test data generator for RecordSplitter
 * Creates sample input files with different record types for testing
 */
public class RecordSplitterTestDataGenerator {
    
    public static void main(String[] args) throws IOException {
        System.out.println("Generating test data for RecordSplitter...");
        
        // Generate test files for each record type
        generateTestFile6084("test_input_6084.txt");
        generateTestFile6064("test_input_6064.txt");
        generateTestFile6044("test_input_6044.txt");
        
        System.out.println("\nTest files generated successfully!");
        System.out.println("  - test_input_6084.txt");
        System.out.println("  - test_input_6064.txt");
        System.out.println("  - test_input_6044.txt");
        System.out.println("\nUse these files with run_splitter script:");
        System.out.println("  run_splitter.bat test_input_6084.txt sample_figlen.txt output_6084.txt 6084");
    }
    
    /**
     * Generate test file for record type 6084
     */
    private static void generateTestFile6084(String filename) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(filename), StandardCharsets.ISO_8859_1))) {
            
            // Record 1: With 3-way split trigger (hex 101C)
            StringBuilder rec1 = new StringBuilder();
            rec1.append(padRight("HEADER DATA FOR RECORD TYPE 6084 - RECORD 001", 80));
            rec1.append("\u0010\u001C"); // Hex 101C
            rec1.append(padRight("DATA SEGMENT FOR 235 BYTES PART 1 TESTING WITH VARIOUS CHARACTERS", 235));
            rec1.append(createFigGroupData()); // 16 bytes FIG group
            rec1.append(createFigData()); // Variable FIG data
            writer.write(rec1.toString());
            writer.newLine();
            
            // Record 2: Without split trigger (hex 205C - not in list)
            StringBuilder rec2 = new StringBuilder();
            rec2.append(padRight("HEADER DATA FOR RECORD TYPE 6084 - RECORD 002", 80));
            rec2.append("\u0020\\"); // Hex 205C (not in split list)
            rec2.append(padRight("NORMAL DATA PROCESSING WITHOUT SPLIT", 100));
            writer.write(rec2.toString());
            writer.newLine();
            
            // Record 3: With another split trigger (hex 209C)
            StringBuilder rec3 = new StringBuilder();
            rec3.append(padRight("HEADER DATA FOR RECORD TYPE 6084 - RECORD 003", 80));
            rec3.append("\u0020\u009C"); // Hex 209C
            rec3.append(padRight("ANOTHER DATA SEGMENT FOR TESTING 3-WAY SPLIT FUNCTIONALITY", 235));
            rec3.append(createFigGroupData());
            rec3.append(createFigData());
            writer.write(rec3.toString());
            writer.newLine();
            
            System.out.println("Generated " + filename + " (3 records)");
        }
    }
    
    /**
     * Generate test file for record type 6064
     */
    private static void generateTestFile6064(String filename) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(filename), StandardCharsets.ISO_8859_1))) {
            
            // Record 1: With split trigger
            StringBuilder rec1 = new StringBuilder();
            rec1.append(padRight("HEADER DATA FOR RECORD TYPE 6064 - TEST 001", 60));
            rec1.append("\u0014\u000C"); // Hex 140C
            rec1.append(padRight("DATA FOR 6064 TYPE RECORDS WITH SPLIT", 235));
            rec1.append(createFigGroupData());
            rec1.append(createFigData());
            writer.write(rec1.toString());
            writer.newLine();
            
            // Record 2: Without split trigger
            StringBuilder rec2 = new StringBuilder();
            rec2.append(padRight("HEADER DATA FOR RECORD TYPE 6064 - TEST 002", 60));
            rec2.append("\u0030L"); // Hex 304C (not in list)
            rec2.append(padRight("STANDARD PROCESSING", 80));
            writer.write(rec2.toString());
            writer.newLine();
            
            System.out.println("Generated " + filename + " (2 records)");
        }
    }
    
    /**
     * Generate test file for record type 6044
     */
    private static void generateTestFile6044(String filename) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(filename), StandardCharsets.ISO_8859_1))) {
            
            // Record 1: With split trigger
            StringBuilder rec1 = new StringBuilder();
            rec1.append(padRight("HEADER FOR 6044 TYPE - REC 001", 40));
            rec1.append("\u0021\u001C"); // Hex 211C
            rec1.append(padRight("6044 DATA SEGMENT FOR PROCESSING", 235));
            rec1.append(createFigGroupData());
            rec1.append(createFigData());
            writer.write(rec1.toString());
            writer.newLine();
            
            // Record 2: Without split trigger
            StringBuilder rec2 = new StringBuilder();
            rec2.append(padRight("HEADER FOR 6044 TYPE - REC 002", 40));
            rec2.append("@\\"); // Hex 405C (not in list)
            rec2.append(padRight("REGULAR DATA", 60));
            writer.write(rec2.toString());
            writer.newLine();
            
            System.out.println("Generated " + filename + " (2 records)");
        }
    }
    
    /**
     * Create 16 bytes of FIG group data
     */
    private static String createFigGroupData() {
        // Create sample FIG group flags (16 bytes)
        // Setting some groups active (non-zero hex values)
        byte[] figBytes = {
            (byte)0xF1, (byte)0x02, (byte)0x00, (byte)0x04,
            (byte)0x05, (byte)0x00, (byte)0x00, (byte)0x08,
            (byte)0x00, (byte)0x0A, (byte)0x00, (byte)0x0C,
            (byte)0x00, (byte)0x00, (byte)0x0F, (byte)0x10
        };
        return new String(figBytes, StandardCharsets.ISO_8859_1);
    }
    
    /**
     * Create sample FIG data
     */
    private static String createFigData() {
        StringBuilder figData = new StringBuilder();
        
        // Add data for active FIG groups using byte arrays for proper encoding
        byte[][] groupData = {
            {(byte)0xA1, (byte)0xB2, (byte)0xC3, (byte)0xD4}, // Group 1
            {(byte)0xE1, (byte)0xF2, (byte)0x03, (byte)0x14}, // Group 4
            {(byte)0x25, (byte)0x36, (byte)0x47, (byte)0x58}, // Group 5
            {(byte)0x69, (byte)0x7A, (byte)0x8B, (byte)0x9C}, // Group 8
            {(byte)0xAD, (byte)0xBE, (byte)0xCF, (byte)0xD0}, // Group 10
            {(byte)0xE1, (byte)0xF2, (byte)0x03, (byte)0x14}, // Group 12
            {(byte)0x25, (byte)0x36, (byte)0x47, (byte)0x58}, // Group 15
            {(byte)0x69, (byte)0x7A, (byte)0x8B, (byte)0x9C}  // Group 16
        };
        
        for (byte[] group : groupData) {
            figData.append(new String(group, StandardCharsets.ISO_8859_1));
        }
        
        // Add some actual FIG segment data (this would be split by FIG lengths)
        figData.append(padRight("FIG SEGMENT DATA FOR TESTING PURPOSES WITH VARIOUS LENGTHS", 500));
        
        return figData.toString();
    }
    
    /**
     * Pad string to specified length with spaces
     */
    private static String padRight(String str, int length) {
        if (str.length() >= length) {
            return str.substring(0, length);
        }
        StringBuilder sb = new StringBuilder(str);
        while (sb.length() < length) {
            sb.append(' ');
        }
        return sb.toString();
    }
}
