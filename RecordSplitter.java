import java.io.*;
import java.nio.charset.StandardCharsets;
import java.nio.file.*;
import java.util.*;

/**
 * Java implementation of REXX MPRECSPL - Record Splitter for ASCII files
 * Identifies 3 file types based on record length and applies split logic
 * 
 * Record Types:
 * - 6084: Block size 23476, Prefix: RMCMFR, splits at position 80
 * - 6064: Block size 27998, Prefix: RMCDBA, splits at position 60
 * - 6044: Block size 15476, Prefix: RMCWOA, splits at position 40
 */
public class RecordSplitter {
    
    // Configuration
    private static final int RECORD_TYPE_6084 = 6084;
    private static final int RECORD_TYPE_6064 = 6064;
    private static final int RECORD_TYPE_6044 = 6044;
    
    // Block sizes for each record type
    private static final int BLOCK_SIZE_6084 = 23476;
    private static final int BLOCK_SIZE_6064 = 27998;
    private static final int BLOCK_SIZE_6044 = 15476;
    
    // Hex values that trigger 3-way split
    private static final Set<String> SPLIT_HEX_LIST = new HashSet<>(Arrays.asList(
        "101C", "103C", "140C", "141C", "142C", "143C", "145C", "146C",
        "209C", "211C", "215C", "221C", "231C", "261C", "265C", "291C",
        "294C", "295C", "307C", "308C", "309C", "310C", "314C", "315C",
        "319C", "321C", "326C", "334C", "338C", "975C"
    ));
    
    private Map<Integer, Integer> figLengths;
    private int recordCount;
    private int outputCount;
    private int recordType;
    private int blockSize;
    
    public RecordSplitter() {
        this.figLengths = new HashMap<>();
        this.recordCount = 0;
        this.outputCount = 0;
    }
    
    /**
     * Main entry point
     */
    public static void main(String[] args) {
        if (args.length < 3) {
            System.out.println("Usage: java RecordSplitter <input_file> <figlen_file> <output_file> [record_length]");
            System.out.println("  record_length: optional, one of 6084, 6064, 6044 (auto-detected if not specified)");
            System.exit(1);
        }
        
        String inputFile = args[0];
        String figLenFile = args[1];
        String outputFile = args[2];
        Integer specifiedRecordLength = null;
        
        if (args.length > 3) {
            try {
                specifiedRecordLength = Integer.parseInt(args[3]);
            } catch (NumberFormatException e) {
                System.err.println("Invalid record length: " + args[3]);
                System.exit(1);
            }
        }
        
        RecordSplitter splitter = new RecordSplitter();
        
        try {
            splitter.process(inputFile, figLenFile, outputFile, specifiedRecordLength);
        } catch (Exception e) {
            System.err.println("Error processing file: " + e.getMessage());
            e.printStackTrace();
            System.exit(1);
        }
    }
    
    /**
     * Main processing method
     */
    public void process(String inputFile, String figLenFile, String outputFile, Integer specifiedRecordLength) throws IOException {
        // Validate input files
        validateFile(inputFile, "Input file");
        validateFile(figLenFile, "FIG length file");
        
        // Determine record type
        if (specifiedRecordLength != null) {
            recordType = specifiedRecordLength;
        } else {
            recordType = detectRecordType(inputFile);
        }
        
        // Set block size based on record type
        switch (recordType) {
            case RECORD_TYPE_6084:
                blockSize = BLOCK_SIZE_6084;
                break;
            case RECORD_TYPE_6064:
                blockSize = BLOCK_SIZE_6064;
                break;
            case RECORD_TYPE_6044:
                blockSize = BLOCK_SIZE_6044;
                break;
            default:
                blockSize = BLOCK_SIZE_6084;
                System.out.println("Unknown record type " + recordType + ", using default block size " + blockSize);
        }
        
        System.out.println("Record Type: " + recordType);
        System.out.println("Block Size: " + blockSize);
        System.out.println("Input File: " + inputFile);
        System.out.println("Output File: " + outputFile);
        System.out.println();
        
        // Read FIG lengths
        loadFigLengths(figLenFile);
        
        // Process records
        processRecords(inputFile, outputFile);
        
        System.out.println();
        System.out.println("Processing completed successfully.");
        System.out.println("Records processed: " + recordCount);
        System.out.println("Output records created: " + outputCount);
    }
    
    /**
     * Validate that a file exists
     */
    private void validateFile(String filepath, String description) throws IOException {
        File file = new File(filepath);
        if (!file.exists()) {
            throw new IOException(description + " does not exist: " + filepath);
        }
    }
    
    /**
     * Detect record type from file (simplified - can be enhanced)
     */
    private int detectRecordType(String inputFile) throws IOException {
        // In ASCII files, we might detect based on file size or first record length
        // For now, default to 6084
        System.out.println("Auto-detecting record type (defaulting to 6084)...");
        return RECORD_TYPE_6084;
    }
    
    /**
     * Load FIG lengths from configuration file
     */
    private void loadFigLengths(String figLenFile) throws IOException {
        System.out.println("Reading and processing FIG LENGTH file...");
        
        List<String> lines = Files.readAllLines(Paths.get(figLenFile), StandardCharsets.UTF_8);
        
        for (int i = 0; i < lines.size(); i++) {
            String line = lines.get(i);
            // Parse format: something | length
            if (line.contains("|")) {
                String[] parts = line.split("\\|");
                if (parts.length >= 2) {
                    try {
                        int length = Integer.parseInt(parts[1].trim());
                        figLengths.put(i + 1, length); // 1-based index like REXX
                    } catch (NumberFormatException e) {
                        System.err.println("Warning: Invalid FIG length at line " + (i + 1) + ": " + line);
                    }
                }
            }
        }
        
        System.out.println("Read " + lines.size() + " records from FIG LENGTH file");
        System.out.println();
    }
    
    /**
     * Process all records from input file
     */
    private void processRecords(String inputFile, String outputFile) throws IOException {
        System.out.println("Reading and processing input file...");
        
        List<String> outputRecords = new ArrayList<>();
        
        try (BufferedReader reader = new BufferedReader(
                new InputStreamReader(new FileInputStream(inputFile), StandardCharsets.ISO_8859_1))) {
            
            String line;
            while ((line = reader.readLine()) != null) {
                recordCount++;
                processRecord(line, outputRecords);
                
                // Progress indicator every 10000 records
                if (recordCount % 10000 == 0) {
                    System.out.println("Processed " + recordCount + " records...");
                }
            }
        }
        
        // Write output file
        System.out.println("Writing output file...");
        writeOutputFile(outputFile, outputRecords);
        System.out.println("Wrote " + outputRecords.size() + " records to output file");
    }
    
    /**
     * Process a single record
     */
    private void processRecord(String record, List<String> outputRecords) {
        String currentRec = record;
        
        // Step 1: Handle initial prefix based on record type
        String part0;
        String prefix1;
        
        switch (recordType) {
            case RECORD_TYPE_6084:
                if (record.length() >= 80) {
                    part0 = record.substring(0, 80);
                    currentRec = record.substring(80);
                    prefix1 = "RMCMFR";
                    outputRecords.add(prefix1 + part0);
                    outputCount++;
                }
                break;
            case RECORD_TYPE_6064:
                if (record.length() >= 60) {
                    part0 = record.substring(0, 60);
                    currentRec = record.substring(60);
                    prefix1 = "RMCDBA";
                    outputRecords.add(prefix1 + part0);
                    outputCount++;
                }
                break;
            case RECORD_TYPE_6044:
                if (record.length() >= 40) {
                    part0 = record.substring(0, 40);
                    currentRec = record.substring(40);
                    prefix1 = "RMCWOA";
                    outputRecords.add(prefix1 + part0);
                    outputCount++;
                }
                break;
        }
        
        // Step 2: Check hex value of first 2 bytes
        if (currentRec.length() >= 2) {
            byte[] first2Bytes = currentRec.substring(0, 2).getBytes(StandardCharsets.ISO_8859_1);
            String hexValue = bytesToHex(first2Bytes);
            String hexNumeric = hexValue.substring(0, Math.min(3, hexValue.length()));
            
            // Check if hex value triggers 3-way split
            if (SPLIT_HEX_LIST.contains(hexValue)) {
                splitRecord3Way(currentRec, hexNumeric, outputRecords);
            } else {
                writeRecordAsIs(currentRec, hexNumeric, outputRecords);
            }
        } else {
            // Record too short, write as-is with default hex
            writeRecordAsIs(currentRec, "000", outputRecords);
        }
    }
    
    /**
     * Split record into 3 parts based on hex value
     */
    private void splitRecord3Way(String currentRec, String hexNumeric, List<String> outputRecords) {
        int recLen = currentRec.length();
        
        // Part 1: First 235 bytes with prefix
        if (recLen >= 235) {
            String part1 = currentRec.substring(0, 235);
            String prefix1 = "CLS" + String.format("%03d", Integer.parseInt(hexNumeric, 16));
            outputRecords.add(prefix1 + part1);
            outputCount++;
            
            // Part 2 and 3: Process FIG data
            if (recLen > 235) {
                String remaining = currentRec.substring(235);
                processFigData(remaining, outputRecords);
            }
        } else {
            // Record shorter than 235, treat as write-as-is
            writeRecordAsIs(currentRec, hexNumeric, outputRecords);
        }
    }
    
    /**
     * Process FIG data (extract flags and split by FIG lengths)
     */
    private void processFigData(String remaining, List<String> outputRecords) {
        if (remaining.length() < 16) {
            return;
        }
        
        // Extract first 16 bytes (FIG group flags)
        String first16Bytes = remaining.substring(0, Math.min(16, remaining.length()));
        outputRecords.add("GRPFIG" + first16Bytes);
        outputCount++;
        
        byte[] figGrpBytes = first16Bytes.getBytes(StandardCharsets.ISO_8859_1);
        String figGrpHex = bytesToHex(figGrpBytes);
        
        // Parse FIG group flags
        int[] figGrp = new int[32]; // 1-indexed, so we use 32
        for (int j = 0; j < Math.min(31, figGrpHex.length()); j++) {
            figGrp[j + 1] = Character.digit(figGrpHex.charAt(j), 16);
        }
        
        // Process each FIG group
        int currentPos = 16; // Start after 16-byte header
        int figIndex = 1;
        int[] fig = new int[218]; // FIG flags array (1-indexed)
        
        for (int grp = 1; grp <= 31; grp++) {
            if (figGrp[grp] != 0) {
                // This group is active, read next 4 bytes
                if (currentPos + 4 <= remaining.length()) {
                    String figData = remaining.substring(currentPos, currentPos + 4);
                    byte[] figBytes = figData.getBytes(StandardCharsets.ISO_8859_1);
                    String figHex = bytesToHex(figBytes);
                    
                    outputRecords.add("GRFI" + String.format("%02d", grp) + figData);
                    outputCount++;
                    
                    // Populate 7 FIG flags
                    for (int figNum = 0; figNum < 7 && figNum < figHex.length(); figNum++) {
                        fig[figIndex] = Character.digit(figHex.charAt(figNum), 16);
                        figIndex++;
                    }
                    
                    currentPos += 4;
                } else {
                    System.err.println("Warning: Record " + recordCount + " Group " + grp + 
                                     " insufficient data at position " + currentPos);
                    figIndex += 7;
                }
            } else {
                // Group not active, skip 7 FIG flags
                figIndex += 7;
            }
        }
        
        // Part 3: Process remaining data based on FIG flags
        if (currentPos < remaining.length()) {
            String part3 = remaining.substring(currentPos);
            processFigFlags(part3, fig, outputRecords);
        }
    }
    
    /**
     * Process FIG flags and split records accordingly
     */
    private void processFigFlags(String part3, int[] fig, List<String> outputRecords) {
        if (part3.length() > 0) {
            outputRecords.add("FIG00@" + part3);
            outputCount++;
        }
        
        String remainingPart3 = part3;
        
        for (int figIndex = 1; figIndex <= 131 && remainingPart3.length() > 0; figIndex++) {
            if (fig[figIndex] == 1) {
                Integer extLen = figLengths.get(figIndex);
                if (extLen == null) {
                    continue; // Skip if no length defined
                }
                
                if (remainingPart3.length() >= extLen) {
                    String figData = remainingPart3.substring(0, extLen);
                    
                    // Special handling for FIG 100
                    if (figIndex == 100) {
                        if (figData.length() > 8 && figData.charAt(8) == '0') {
                            outputRecords.add("FIG" + String.format("%03d", figIndex) + figData);
                            outputCount++;
                        } else {
                            outputRecords.add("FIG10E" + figData);
                            outputCount++;
                        }
                    } else {
                        outputRecords.add("FIG" + String.format("%03d", figIndex) + figData);
                        outputCount++;
                    }
                    
                    remainingPart3 = remainingPart3.substring(extLen);
                }
            }
        }
    }
    
    /**
     * Write record as-is with prefix
     */
    private void writeRecordAsIs(String currentRec, String hexNumeric, List<String> outputRecords) {
        try {
            String prefix = "CLS" + String.format("%03d", Integer.parseInt(hexNumeric, 16));
            outputRecords.add(prefix + currentRec);
            outputCount++;
        } catch (NumberFormatException e) {
            String prefix = "CLS000";
            outputRecords.add(prefix + currentRec);
            outputCount++;
        }
    }
    
    /**
     * Write output records to file
     */
    private void writeOutputFile(String outputFile, List<String> records) throws IOException {
        try (BufferedWriter writer = new BufferedWriter(
                new OutputStreamWriter(new FileOutputStream(outputFile), StandardCharsets.ISO_8859_1))) {
            for (String record : records) {
                writer.write(record);
                writer.newLine();
            }
        }
    }
    
    /**
     * Convert bytes to hex string
     */
    private String bytesToHex(byte[] bytes) {
        StringBuilder sb = new StringBuilder();
        for (byte b : bytes) {
            sb.append(String.format("%02X", b & 0xFF));
        }
        return sb.toString();
    }
}
