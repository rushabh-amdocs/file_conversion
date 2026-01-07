/* REXX */
sProgramName = 'RoysEbcdicRecTypesV6.rexx'
signal 0000_Control
/*  - Author                : Roy Mathur
    - Date written          : November 2024
    - REXX Interpreter      : ooREXX - https://www.oorexx.org/ (this must be installed to run this program)
    - Command-Line Arguments: see the below 0110_Display_Syntax routine
    - Purpose               : Display the keys and record lengths for an EBCDIC file.

    Modifications:
        2024-12-11 - added command-line parms.
        2024-12-23 - renamed to version 2.
                   - added logic to prompt the user for the starting position of the key
        2024-12-27 - added logic to write out the ebcdic file as ebcdic hex.
        2025-01-10 - added logic to split a file by a number of records.
                   - renamed to version 4.
        2025-01-13 - added logic to convert COMP and COMP-3 keys to Display, so they are readable in the output csv file.
        2025-01-15 - renamed to version 5.
                   - added logic to identify the last non-space character per line to see the real record length per record type.
        2025-02-03 - renamed to version 6.
                   - changed so hex file will contain the RDW.

    Future Enhancements:
*/
/* '....x....1....x....2....x....3....x....4....x....5....x....6....x....7....x....8....x....9....x....0' */
0000_Control:


    parse lower arg args
    
    call 0100_Parms
    call 1000_Init
    call 2000_Main
    call 9000_Done
    exit

0100_Parms:
    swRdw = 0
    iFileName = ''
    recFm = ''
    recLen = ''
    keyBeg = ''
    keyPic = ''
    
    i = 1
    do while (i <= words(args))
        w = word(args,i)
        Select
            when w = '--usage'  then call 0110_Display_Syntax
            when w = '--rdw'    then swRdw = 1
            when w = '--file'   then do
                        i = i + 1
                        iFileName = word(args,i)
                      end
            when w = '--recfm'  then do
                        i = i + 1
                        recFm = word(args,i)
                      end
            when w = '--reclen' then do
                        i = i + 1
                        recLen = word(args,i)
                      end
            when w = '--keybeg' then do
                        i = i + 1
                        keyBeg = word(args,i)
                      end
            when w = '--keypic' then do
                        i = i + 1
                        keyPic = word(args,i)
                      end
            otherwise do
                        say 'Error: Invalid Command-Line parm: 'w'. Terminating program.'
                        exit
                      end
        end
        i = i + 1
    end
    return

0110_Display_Syntax:
    say 'Program Name:' sProgramName
    say
    say 'How to execute examples:'
    say '  ooRexx 'sProgramName' --usage'
    say '  ooRexx 'sProgramName' --rdw --file "path\file.txt" --recfm V --reclen 6229 --keybeg 1 --keypic "X(3)"'
    say '  ooRexx 'sProgramName' --file "path\file.txt" --recfm F --reclen 80 --keybeg 1 --keypic "X(5)"'
    say
    say 'Command-Line parameters:'
    say '  --usage  = Program will display Command-Line syntax'
    say '  --rdw    = Program will expect the first 4 bytes of each record to contain the record length bytes'
    say '  --file   = Full path to the input EBCDIC file'
    say '  --recfm  = Record format: F (Fixed) or V (Variable)'
    say '  --reclen = Record length (numeric)'
    say '  --keybeg = Starting position of the key (numeric)'
    say '  --keypic = Key PIC clause (e.g., "X(3)" or "S9(5) COMP")'
    say
    exit

1000_Init:
    sDateTime = date('S')'-'Time()
    say
    say 'Start DateTime:' sDateTime
    say 
    say 'This program will read in an EBCDIC variable file with or without an RDW length bytes, count some unmappable characters, write a file containing all unique keys and the number of records with that key, and write a file where each EBCDIC record is written as a separate record using carriage-return.'
    say
    
    EBCDIC_1047 =   '000102030405060708090A0B0C0D0E0F'x || , 
                    '101112131415161718191A1B1C1D1E1F'x || ,
                    '202122232425262728292A2B2C2D2E2F'x || ,
                    '303132333435363738393A3B3C3D3E3F'x || ,
                    '404142434445464748494A4B4C4D4E4F'x || ,
                    '505152535455565758595A5B5C5D5E5F'x || ,
                    '606162636465666768696A6B6C6D6E6F'x || ,
                    '707172737475767778797A7B7C7D7E7F'x || ,
                    '808182838485868788898A8B8C8D8E8F'x || ,
                    '909192939495969798999A9B9C9D9E9F'x || ,
                    'A0A1A2A3A4A5A6A7A8A9AAABACADAEAF'x || ,
                    'B0B1B2B3B4B5B6B7B8B9BABBBCBDBEBF'x || ,
                    'C0C1C2C3C4C5C6C7C8C9CACBCCCDCECF'x || ,
                    'D0D1D2D3D4D5D6D7D8D9DADBDCDDDEDF'x || ,
                    'E0E1E2E3E4E5E6E7E8E9EAEBECEDEEEF'x || ,
                    'F0F1F2F3F4F5F6F7F8F9FAFBFCFDFEFF'x 
    ASCII_924 =     '000102039C09867F978D8E0B0C0D0E0F'x || ,
                    '101112139D8508871819928F1C1D1E1F'x || ,
                    '80818283840A171B88898A8B8C050607'x || ,
                    '909116939495960498999A9B14159E1A'x || ,
                    '20A0E2E4E0E1E3E5E7F1A22E3C282B7C'x || ,
                    '26E9EAEBE8EDEEEFECDF21242A293B5E'x || ,
                    '2D2FC2C4C0C1C3C5C7D1A62C255F3E3F'x || ,
                    'F8C9CACBC8CDCECFCC603A2340273D22'x || ,
                    'D8616263646566676869ABBBF0FDFEB1'x || ,
                    'B06A6B6C6D6E6F707172AABAE6B8C6A4'x || ,
                    'B57E737475767778797AA1BFD05BDEAE'x || ,
                    'ACA3A5B7A9A7B6BCBDBEDDA8AF5DB4D7'x || ,
                    '7B414243444546474849ADF4F6F2F3F5'x || ,
                    '7D4A4B4C4D4E4F505152B9FBFCF9FAFF'x || ,
                    '5CF7535455565758595AB2D4D6D2D3D5'x || ,
                    '30313233343536373839B3DBDCD9DA9F'x

    /*------------------------------------*
     * Get EBCDIC file from command-line or prompt
     *------------------------------------*/
     if iFileName = '' then do
        parse pull iFileName
     end
     if iFileName = '' then do
        iFileName = FileNameDialog(,,"*.*",load,"Select EBCDIC File")
     end
--iFileName = 'C:\Users\roymat\Downloads\RF01.PFB15.IRN (1).txt'
    if iFileName = '' then do
        say 'No file name entered. Ending program.'
        exit
    end
    say 'input Filename=<'iFileName'>'
    iFile = .Stream~new(iFileName) 
    iFLen = iFile~chars
    iData = iFile~charin(1,iFLen)

    /*------------------------------------*
     * Create the report file
     *------------------------------------*/
    parse var sProgramName sPgmName '.' sPgmExt
    -- rName = iFileName'-'sPgmName'-'translate(sDateTime,'.',':')'.csv'
    rName = iFileName'-'sPgmName'.csv'
    if SysFileExists(rName) then rc = SysFileDelete(rName)
    rFile = .Stream~new(rName)

    -- oName = iFileName'-'sPgmName'-'translate(sDateTime,'.',':')'-ebcdic2ascii.txt'
    oName = iFileName'-'sPgmName'-ebcdic2ascii.txt'
    if SysFileExists(oName) then rc = SysFileDelete(oName)
    oFile = .Stream~new(oName)
    oFile~open("write")
    
    -- hName = iFileName'-'sPgmName'-'translate(sDateTime,'.',':')'-ebcdicHex.txt'
    hName = iFileName'-'sPgmName'-ebcdicHex.txt'
    if SysFileExists(hName) then rc = SysFileDelete(hName)
    hFile = .Stream~new(hName)

    /*------------------------------------*
     * Get record format from command-line or prompt
     *------------------------------------*/
     if swRdw = 0 then do
        if recFm = '' then do
            parse pull recFm
        end
        if recFm = '' then do
            say "Is the file Fixed-length or Variable-length (enter F or V):"
            pull recFm
        end
        recFm = upper(recFm)
        select
            when recFm = 'F' then nop
            when recFm = 'V' then swRdw = 1
            otherwise do
                        say 'Invalid entry. Ending program.'
                        exit
                      end
        end
     end

    /*------------------------------------*
     * Get the record length from command-line or prompt
     *------------------------------------*/
     if recLen = '' then do
        parse pull recLen
     end
     if recLen = '' then do
        say "Enter the record length (ex: 80):"
        pull recLen
     end
     if recLen = '' then do
        say 'No record length entered. Ending program.'
        exit
     end
     if datatype(recLen,'N') = 0 then do
        say 'Record length entered is not numeric. Ending program.'
        exit
     end

    /*------------------------------------*
     * Get the starting position of the key from command-line or prompt
     *------------------------------------*/
     if keyBeg = '' then do
        parse pull keyBeg
     end
     if keyBeg = '' then do
        say "Enter the starting position of the key:"
        pull keyBeg
     end
     if keyBeg = '' then do
        say 'No Key starting position entered. Ending program.'
        exit
     end
     if datatype(KeyBeg,'N') = 0 then do
        say 'Key starting position entered is not numeric. Ending program.'
        exit
     end

    /*------------------------------------*
     * Get the key's PIC clause from command-line or prompt
     *------------------------------------*/
     if keyPic = '' then do
        parse pull keyPic
     end
     if keyPic = '' then do
        say "Enter the key's PIC clause (ex: X(3) or S9(5) COMP):"
        pull keyPic
     end
     if keyPic = '' then do
        say 'No Key PIC clause entered. Ending program.'
        exit
     end
     keyPic = upper(keyPic)
     parse var keyPic fldType '(' fldLen ')' fldRest
     if fldRest = 'COMP' then do
        if fldLen >= 1 & fldLen <= 4 then
            fldLen = 2
        else if fldLen > 4 & fldLen < 8 then
            fldLen = 4
     end
     else if fldRest = 'COMP-3' then do
        fldLen = (fldLen + 1) % 2
     end

    /*------------------------------------*
     * Get the split count from stdin (skip this prompt for web UI)
     *------------------------------------*/
     splitMax = -1
     /* Commenting out split count prompt for web UI compatibility
     say "Enter the split count (if you enter nothing then the file will not be split):"
     pull splitMax
     if splitMax = '' then splitMax = -1
     if datatype(splitMax,'N') = 0 then do
        say 'Split count is not numeric. Ending program.'
        exit
     end
     */

     return

2000_Main:
    i = 0
    cnt = 0
    iKeys = 0
    recs = 0
    iEbcdicRecords = 0
    splitFileCounter = 0
    splitCount = splitMax
    iAsciiX0A = 0           /* Line Feeds */
    iAsciiX85 = 0           /* Next Lines */
    iEbcdicX00 = 0          /* Low-Values */
    iEbcdicX04 = 0          /* SEL/EOT */
    iEbcdicX0C = 0          /* Form Feeds */
    iEbcdicX0D = 0          /* Carriage Return */
    iEbcdicX0F = 0          /* Shift In */
    iEbcdicX10 = 0          /* Data Link Escape */
    iEbcdicX15 = 0          /* New Lines */
    iEbcdicX25 = 0          /* Line Feeds */
    iEbcdicXFF = 0          /* High-Values */
    do while (i < iFLen & cnt < 999999999999)
        recs = recs + 1
        if recs > 1000 then do
            say 'Processing record #: 'cnt'   'date('S')'-'Time()
            recs = 0
        end
        if swRdw = 1 then do
            iRdw = substr(iData,i+1,2)                  /* extract RDW bytes */
            iDataLen = x2d(c2x(iRdw))                   /* convert number from Binary to Decimal */
            iLine = substr(iData,i+5,iDataLen)          /* extract only the record's data */
            iFullLine = substr(iData,i+1, iDataLen+4)   /* extract the RDW and record's data */
        end
        else do
            iDataLen = recLen
            iLine = substr(iData,i+1,iDataLen)      /* extract the record's data */
            iFullLine = iLine
        end
        
        /* count specific hex characters */
        iAsciiX0A        = iAsciiX0A        + countstr('0A'x,iLine)
        iAsciiX85        = iAsciiX85        + countstr('85'x,iLine)
        iEbcdicX00       = iEbcdicX00       + countstr('00'x,iLine)
        iEbcdicX04       = iEbcdicX04       + countstr('04'x,iLine)
        iEbcdicX0C       = iEbcdicX0C       + countstr('0C'x,iLine)
        iEbcdicX0D       = iEbcdicX0D       + countstr('0D'x,iLine)
        iEbcdicX0F       = iEbcdicX0F       + countstr('0F'x,iLine)
        iEbcdicX10       = iEbcdicX10       + countstr('10'x,iLine)
        iEbcdicXFF       = iEbcdicXFF       + countstr('FF'x,iLine)
        iEbcdicX15       = iEbcdicX15       + countstr('15'x,iLine)
        iEbcdicX25       = iEbcdicX25       + countstr('25'x,iLine)
        
        /* extract the key (record-type) and convert it to ASCII */
        iKey = substr(iLine,keyBeg,fldLen)
        if fldRest = '' then
            oKey = translate(iKey,ASCII_924,EBCDIC_1047)
        else if fldRest = 'COMP-3' then 
            oKey = substr(c2x(iKey),1,5)
        else if fldRest = 'COMP' then 
            oKey = c2d(iKey)
        else do
            oKey = '[error] Invalid datatype: 'fldRest'. Program ending.'
            exit
        end
        
        /* convert the record to ASCII */
        iEbcdicRecords = iEbcdicRecords + 1
        oLine = translate(iLine,ASCII_924,EBCDIC_1047)

        /* determine the record length after striping spaces and low-values from the right of the line */
        stripLen = length(strip(strip(oLine,'t','00'x),'t',' '))
        
        /* find key and keep a count of how many records each key has */
        swFnd = 0
        do j = 1 to iKeys
            if aKeys.j = oKey then do
                swFnd = 1
                aCnts.j = aCnts.j + 1
                aSLen.j = max(aSLen.j, stripLen)
                leave
            end
        end
        if swFnd = 0 then do
            iKeys = iKeys + 1
            aKeys.iKeys = oKey
            aSLen.iKeys = stripLen
            if swRdw = 1 then aLens.iKeys = iDataLen - 4
            else              aLens.iKeys = iDataLen
            aCnts.iKeys = 1
        end

        /* write out the ASCII line */
        ofile~lineout(oLine)
            
        /* split file */
        if splitMax > -1 then do
            splitCount = splitCount + 1
            if splitCount > splitMax then do
                splitCount = 0
                splitFileCounter = splitFileCounter + 1
                sName = iFileName'-'sPgmName'-split'splitFileCounter'.txt'
                if SysFileExists(sName) then rc = SysFileDelete(sName)
                sFile = .Stream~new(sName)
            end
            sFile~lineout(iLine)
        end
            
        /* convert the record to EBCDIC HEX and write it out */
        hLine = c2x(iFullLine)
        hFile~lineout(hLine)
        
        i = i + iDataLen
        cnt = cnt + 1
    end

    /* write out key counts file */
    rFile~lineout('StripRecLen is the maximum number of characters in a line after all trailing spaces and low-values have been removed')
    rFile~lineout('RecordType,RecordLength,StripRecLen,NumberOfRecords')
    do j = 1 to iKeys
       rFile~lineout(aKeys.j','aLens.j','aSLen.j','aCnts.j)
    end
    return

9000_Done:
    iFile~close()
    rFile~close()
    oFile~close()
    hFile~close()

    /* display totals */
    say
    say 'EBCDIC Records          =' iEbcdicRecords
    say
    say 'Common hex codes:'
    say "   Low-Values        '00'x =" iEbcdicX00
    say "   Form-Feeds        '0C'x =" iEbcdicX0C
    say "   Carriage-Returns  '0D'x =" iEbcdicX0D
    say "   Shift-In          '0F'x =" iEbcdicX0F
    say "   Data-Link-Escape  '10'x =" iEbcdicX10
    say "   High-Values       'FF'x =" iEbcdicXFF          "(Converted to '9F'x)"
    say
    say 'EBCDIC hex codes:'
    say "   SEL/EOT           '04'x =" iEbcdicX04
    say "   New-Lines         '15'x =" iEbcdicX15
    say "   Line-Feeds        '25'x =" iEbcdicX25
    say
    say 'ASCII hex codes:'
    say "   Line-Feeds        '0A'x =" iAsciiX0A
    say "   Next-Lines        '85'x =" iAsciiX85
    say 
    say 'Report file    :' rName
    say 'Output file    :' oName
    say 'EBCDIC Hex file:' hName
    if splitMax > -1 then 
        say 'Split file.....:' iFileName'-'sPgmName'-split*.txt         ('splitFileCounter' files)'
    say
    say 'End  DateTime:' Date('S')'-'Time()
    return

::requires "ooDialog.cls"
