000100**-------------------------------------------------------------**         
000200**                                                             **         
000300**    MODULE: RD01AVH   -   CASH VOUCHER                       **         
000400**                                                             **         
000500**    LENGTH:   1000                                           **         
000600**                                                             **         
000700**    UPDATE:                                                  **         
000800**            03/09/98  RBN  ADDED CASH-ADJ-DESC-CODE          **         
000900**                                 CASH-OCA-IND                **         
001000**            04/06/98  RBN  CHANGED CASH-JOURNAL-ID-456 TO    **         
001100**                                 CASH-JOURNAL-FILLER         **         
001200**            04/22/98  RBN  RCBP                              **         
001300**            06/29/98  MDC  RCBP ADD PROJ CONVERGENCE FIELDS  **         
001400**            08/19/98  MDC  RCBP REMOVE PROJ CONVERG FIELDS   **         
001500**            07/16/99  JRM  ADDED SERIAL NUMBER FOR CE4 TRANS **         
001600**            01/11/01  MDC  ADDED INDICATOR FOR OCSSK ACCTS   **         
001700**            01/12/01  JRM  ADDED FIELDS FOR UNE              **         
001710**            04/12/02  MJS  ADDED TRANS-ID FIELD              **         
001711**            11/15/02  BC   RENAME TRANS-ID FIELD             **         
001712**            09/17/03  CF   ADDED CUID/SCREEN/UNAPP CORR CUID **         
001713**            08/09/04  MC   ADDED CBR SOLUTION FIELDS         **         
001714**            01/23/06  ZDE  ADDED OVERAGE ACCT IND            **         
001715**            03/14/07  RS   ADD FIELDS FOR CAPM. CASH-66891.  **         
001716**            08/29/07  RK   ADD FIELDS FOR SOD.  CASH-90352.  **         
001717**            05/30/12  MK   ADD FIELDS FOR PID #240771 UCS.   **         
001800**-------------------------------------------------------------**   
       01 test.
001900     05  CASH-IDENTIFICATION.                                     1-3     
002000         10  CASH-RECORD-TYPE        PIC  X(1).                   1       
002100             88  VOUCHER-RECIRC            VALUE '2'.                     
002200             88  UNAPPLY-ACTIVITY          VALUE '3'.                     
002300             88  PYMT-WARNING              VALUE '4'.                     
002400             88  VCHR-POSTING-ACTIVITY     VALUE '5'.                     
002500             88  POSTING-ACTIVITY          VALUE '5'.                     
002600             88  UNE-ACTIVITY              VALUE '8'.                     
002700         10  CASH-CARD-TYPE          PIC  X(1).                   2       
002800             88  VOUCHER                   VALUE '2'.                     
002900             88  COIN-VOUCHER              VALUE '6'.                     
003000             88  VALID-VCHR-CARD-TYPE      VALUE '1' '2' '3' '4'          
003100                                                 '6' '7' '8' ' '.         
003200         10  CASH-TRANS-TYPE         PIC  X(1).                   3       
003300             88  EXPEDITED-BILLING         VALUE '0'.                     
003400             88  PAYMENT-TRANSFER          VALUE '1'.                     
003500             88  CANCELLED-TOLL            VALUE '2'.                     
003600             88  DISHONORED-CHECK          VALUE '3'.                     
003700             88  TELEGRAM-CHARGE-BACK      VALUE '4'.                     
003800             88  5040-ADJUSTMENT           VALUE '5'.                     
003900             88  ACCOUNTING-TRANSFER       VALUE '6'.                     
004000             88  ACCOUNTING-ADJUSTMENT     VALUE '7'.                     
004100             88  WRITE-OFF-COLL-AND-JRNL   VALUE '8'.                     
004200             88  OTHER-VOUCHER             VALUE '9'.                     
004300             88  CREDIT-CARD-CHARGEBACK    VALUE 'L'.                     
004400             88  VCHR-OFFSET-PYMNT-WO-ACCT VALUE 'Q'.                     
004500             88  WRITE-OFF-JRNL            VALUE 'S'.                     
004600             88  WRITE-OFF-COLL            VALUE 'T'.                     
004610             88  CLEAR-SOLD-ACCT-VCHR      VALUE 'Z'.                     
004700             88  VALID-VCHR-TRANS-TYPE     VALUE '0' '1' '2' '3'          
004800                                               '4' '5' '6' '7'            
004900                                               '8' '9' 'L' 'Q'            
005000                                               'S' 'T' 'Z'.               
005100     05  CASH-ACCT-KEY.                                           4-16    
005200         10  CASH-NPA                PIC  X(3).                   4-6     
005300         10  CASH-NNX.                                            7-9     
005400             15  CASH-NNX-1            PIC  X(1).                 7       
005500                 88  CRIS-ACCT        VALUE '0' THRU '9' 'M'              
005600                                            'U' 'V' 'W' 'X'               
005700                                            'Q' 'Z' 'H' 'Y'.              
005800                 88  POSSIBLE-UNE-ACCT VALUE 'Q'.                         
005900             15  CASH-NNX-2            PIC  X(2).                 8-9     
006000         10  CASH-LINE-NUM           PIC  X(4).                   10-13   
006100         10  CASH-CUST-CODE          PIC  X(3).                   14-16   
006200     05  CASH-SORT-CODE            PIC  X(1).                     17      
006300     05  CASH-SESSION-KEY.                                        18-33   
006400         88  CASH-NOT-A-SESSION    VALUE '0000000000000000'.              
006500         10  CASH-SESSION-ORIGIN            PIC X(2).             18-19   
006600             88  ATT-MECH-ORIGINATED-ADJ    VALUE '01'.                   
006700             88  RCD-MECH-ORIGINATED-ADJ    VALUE '02'.                   
006800             88  EC-PAPER-ONLINE-ADJ        VALUE '03'.                   
006900             88  EC-PAPER-TARTAN-ADJ        VALUE '04'.                   
007000             88  BOC-ONLINE-ADJ             VALUE '05'.                   
007100             88  BOC-TARTAN-ADJ             VALUE '06'.                   
007200             88  BOC-MECH-ADJ               VALUE '07'.                   
007300             88  IDB-PRIME-ADJ              VALUE '08'.                   
007400         10  CASH-SESSION-NUMBER.                                 20-33   
007500             15  CASH-SESSION-DATE          PIC X(6).             20-25   
007600             15  CASH-SESSION-TIME          PIC X(8).             26-33   
007700     05  CASH-ATT-IDB-DATA                                        18-33   
007800             REDEFINES CASH-SESSION-KEY.                                  
007900         10  CASH-ATT-IDB-INV-NUM           PIC X(2).             18-19   
008000         10  CASH-ATT-IDB-OBLIG-ID          PIC X(8).             20-27   
008100         10  CASH-ATT-IDB-SEND-RAO          PIC X(3).             28-30   
008200         10  CASH-ATT-IDB-BILL-RAO          PIC X(3).             31-33   
008300     05  CASH-FLEX-INV-DATA                                       18-33   
008400             REDEFINES CASH-SESSION-KEY.                                  
008500         10  CASH-FLEX-INV-NUM              PIC X(2).             18-19   
008600         10  CASH-FLEX-OBLIG-ID             PIC X(8).             20-27   
008700         10  CASH-FLEX-SEND-RAO             PIC X(3).             28-30   
008800         10  CASH-FLEX-BILL-RAO             PIC X(3).             31-33   
008900     05  CASH-SESSION-SEQ-NUMB              PIC 9(5).             34-38   
009000         88  ADVICE-RECORD                  VALUE 1 THRU 99999.           
009100     05  CASH-REJECT-REASON                 PIC X(3).             39-41   
009200         88  VOUCHER-POSTED                 VALUE ZEROES.                 
009300     05  CASH-FINAL-INDICATOR      PIC  X(1).                     42      
009400         88  FINAL-VOUCHER               VALUE '8'.                       
009500     05  CASH-CRED-CLS             PIC  X(1).                     43      
009600     05  CASH-RES-BUS-IND          PIC  X(1).                     44      
009700     05  CASH-BATCH-INFO.                                         45-56   
009800         10  CASH-BO                 PIC X(4).                    45-48   
009900           88 CASH-BO-IS-CMR         VALUE                                
010000           'GA3 ' 'NC3 '.                                                 
010100         10  FILLER REDEFINES CASH-BO.                            45-48   
010200             15  CASH-BO-12          PIC X(2).                    45-46   
010300             15  CASH-BO-34          PIC X(2).                    47-48   
010400         10  FILLER REDEFINES CASH-BO.                            45-48   
010500             15  CASH-BO-13          PIC X(3).                    45-47   
010600             15  FILLER              PIC X(1).                    48      
010700         10  FILLER REDEFINES CASH-BO.                            45-48   
010800             15  CASH-BO-1           PIC X(1).                    45      
010900             15  CASH-BO-2           PIC X(1).                    46      
011000             15  CASH-BO-3           PIC X(1).                    47      
011100             15  CASH-BO-4           PIC X(1).                    48      
011200         10  CASH-BATCH-NUMBER.                                   49-52   
011300             15  CASH-BATCH-NUM-13   PIC X(3).                    49-51   
011400             15  CASH-BATCH-NUM-4    PIC X(1).                    52      
011500         10  CASH-BATCH-DATE         PIC S9(6)    COMP-3.         53-56   
011600     05  CASH-AMOUNT               PIC S9(9)V9(2) COMP-3.         57-62   
011700         88  DEBIT-VOUCHER         VALUE +0.00 THRU +999999999.99.        
011800     05  CASH-SITE-IND             PIC  X(1).                     63      
011900     05  CASH-REPORT-CODE          PIC  X(1).                     64      
012000         88  MIC-NON-FRAUD               VALUE '3'.                       
012100         88  UNBILLABLE-FRAUD            VALUE '4'.                       
012200         88  MIC-UNBILLABLE-FRAUD        VALUE '5'.                       
012300         88  RETIRED-EMPLOYEE            VALUE '7'.                       
012400         88  STUDY-CODE-8                VALUE '8'.                       
012500         88  STUDY-CODE-9                VALUE '9'.                       
012600         88  EXCHG-COMP-UNCOLL           VALUE 'A'.                       
012700         88  EXCHG-SVC-FLT               VALUE 'B'.                       
012800         88  EXCHG-REBILL-CO-ERROR       VALUE 'C'.                       
012900         88  TOLL-COMP-UNCOLL            VALUE 'D'.                       
013000         88  TOLL-SVC-FLT                VALUE 'E'.                       
013100         88  TOLL-REBILL-CO-ERROR        VALUE 'F'.                       
013200         88  BILL-ITEMIZATION-VCHR       VALUE 'L'.                       
013300         88  RECOURSE-FOR-CARRIER        VALUE 'R'.                       
013400         88  DEREG-SERVICES              VALUE 'U'.                       
013500     05  CASH-COIN-DATA.                                          65-74   
013600         10  CASH-SEQUENCE-NUM.                                   65-71   
013700             15  CASH-ROUTE-NUM          PIC  X(3).               65-67   
013800             15  CASH-STOP-NUM           PIC  X(4).               68-71   
013900         10  CASH-GROUP-NUM              PIC  X(3).               72-74   
014000     05  CASH-ATT-IDB-ERROR-DATA                                  65-74   
014100             REDEFINES CASH-COIN-DATA.                                    
014200         10  CASH-ATT-IDB-IC-ACCT        PIC  X(8).               65-72   
014300         10  CASH-ATT-IDB-IC-DIV-ID      PIC  X(2).               73-74   
014400     05  CASH-FLEX-INV-ERROR-DATA                                 65-74   
014500             REDEFINES CASH-COIN-DATA.                                    
014600         10  CASH-FLEX-ACCT              PIC  X(8).               65-72   
014700         10  CASH-FLEX-DIV-ID            PIC  X(2).               73-74   
014800     05  CASH-DATE-1.                                             75-80   
014900         10  CASH-DATE1-YY           PIC  X(2).                   75-76   
015000         10  CASH-DATE1-MM           PIC  X(2).                   77-78   
015100         10  CASH-DATE1-DD           PIC  X(2).                   79-80   
015200     05  CASH-FLEX-INV-EXTRACT-DATE                               75-80   
015300             REDEFINES CASH-DATE-1.                                       
015400         10  FILLER                      PIC X(6).                75-80   
015500     05  CASH-ATT-IDB-IC-EXTRACT-DATE                             75-80   
015600             REDEFINES CASH-DATE-1.                                       
015700         10  FILLER                      PIC X(6).                75-80   
015800     05  CASH-DATE-2.                                             81-86   
015900         10  CASH-DATE2-YY           PIC  X(2).                   81-82   
016000         10  CASH-DATE2-MM           PIC  X(2).                   83-84   
016100         10  CASH-DATE2-DD           PIC  X(2).                   85-86   
016200     05  CASH-FLEX-BILLING-DATE                                   81-86   
016300             REDEFINES CASH-DATE-2.                                       
016400         10  FILLER                      PIC X(6).                81-86   
016500     05  CASH-DATE-3.                                             87-92   
016600         10  CASH-DATE3-YY           PIC  X(2).                   87-88   
016700         10  CASH-DATE3-MM           PIC  X(2).                   89-90   
016800         10  CASH-DATE3-DD           PIC  X(2).                   91-92   
016900     05  CASH-REASON-CODE          PIC  X(3).                     93-95   
017000     05  CASH-ACCT-DATA.                                          96-221  
017100         10  CASH-AC1                  PIC  X(3).                 96-98   
017200             88  UPPER-STRATA-UNCOLL-AC1                                  
017300                 VALUE  'LL0' 'MM0' 'NN0' 'LX0' 'MA0' 'MB0'               
017400                        'ND0' 'ME0' 'MF0' 'MG0' 'RE1'.                    
017500         10  CASH-AC1-REPORT-CODE      PIC  X(1).                 99      
017600         10  CASH-AC1-REASON-CODE      PIC  X(3).                 100-102 
017700         10  CASH-AC1-AMOUNT           PIC S9(7)V9(2) COMP-3.     103-107 
017800         10  CASH-AC1-USOC             PIC  X(5).                 108-112 
017900         10  CASH-AC1-DENIABLE         PIC  X(1).                 113     
018000             88  DENIABLE-AC1       VALUE 'Y'.                            
018100             88  NON-DENIABLE-AC1   VALUE 'N'.                            
018200         10  CASH-AC1-CSS-PPS          PIC  X(2).                 114-115 
018300         10  CASH-AC1-COLL-RPT-LN      PIC  X(1).                 116     
018400         10  CASH-AC2                  PIC  X(3).                 117-119 
018500         10  CASH-AC2-REPORT-CODE      PIC  X(1).                 120     
018600         10  CASH-AC2-REASON-CODE      PIC  X(3).                 121-123 
018700         10  CASH-AC2-AMOUNT           PIC S9(7)V9(2) COMP-3.     124-128 
018800         10  CASH-AC2-USOC             PIC  X(5).                 129-133 
018900         10  CASH-AC2-DENIABLE         PIC  X(1).                 134     
019000             88  DENIABLE-AC2       VALUE 'Y'.                            
019100             88  NON-DENIABLE-AC2   VALUE 'N'.                            
019200         10  CASH-AC2-CSS-PPS          PIC  X(2).                 135-136 
019300         10  CASH-AC2-COLL-RPT-LN      PIC  X(1).                 137     
019400         10  CASH-AC3                  PIC  X(3).                 138-140 
019500         10  CASH-AC3-REPORT-CODE      PIC  X(1).                 141     
019600         10  CASH-AC3-REASON-CODE      PIC  X(3).                 142-144 
019700         10  CASH-AC3-AMOUNT           PIC S9(7)V9(2) COMP-3.     145-149 
019800         10  CASH-AC3-USOC             PIC  X(5).                 150-154 
019900         10  CASH-AC3-DENIABLE         PIC  X(1).                 155     
020000             88  DENIABLE-AC3       VALUE 'Y'.                            
020100             88  NON-DENIABLE-AC3   VALUE 'N'.                            
020200         10  CASH-AC3-CSS-PPS          PIC  X(2).                 156-157 
020300         10  CASH-AC3-COLL-RPT-LN      PIC  X(1).                 158     
020400         10  CASH-AC4                  PIC  X(3).                 159-161 
020500         10  CASH-AC4-REPORT-CODE      PIC  X(1).                 162     
020600         10  CASH-AC4-REASON-CODE      PIC  X(3).                 163-165 
020700         10  CASH-AC4-AMOUNT           PIC S9(7)V9(2) COMP-3.     166-170 
020800         10  CASH-AC4-USOC             PIC  X(5).                 171-175 
020900         10  CASH-AC4-DENIABLE         PIC  X(1).                 176     
021000             88  DENIABLE-AC4       VALUE 'Y'.                            
021100             88  NON-DENIABLE-AC4   VALUE 'N'.                            
021200         10  CASH-AC4-CSS-PPS          PIC  X(2).                 177-178 
021300         10  CASH-AC4-COLL-RPT-LN      PIC  X(1).                 179     
021400         10  CASH-AC5                  PIC  X(3).                 180-182 
021500         10  CASH-AC5-REPORT-CODE      PIC  X(1).                 183     
021600         10  CASH-AC5-REASON-CODE      PIC  X(3).                 184-186 
021700         10  CASH-AC5-AMOUNT           PIC S9(7)V9(2) COMP-3.     187-191 
021800         10  CASH-AC5-USOC             PIC  X(5).                 192-196 
021900         10  CASH-AC5-DENIABLE         PIC  X(1).                 197     
022000             88  DENIABLE-AC5       VALUE 'Y'.                            
022100             88  NON-DENIABLE-AC5   VALUE 'N'.                            
022200         10  CASH-AC5-CSS-PPS          PIC  X(2).                 198-199 
022300         10  CASH-AC5-COLL-RPT-LN      PIC  X(1).                 200     
022400         10  CASH-AC6                  PIC  X(3).                 201-203 
022500         10  CASH-AC6-REPORT-CODE      PIC  X(1).                 204     
022600         10  CASH-AC6-REASON-CODE      PIC  X(3).                 205-207 
022700         10  CASH-AC6-AMOUNT           PIC S9(7)V9(2) COMP-3.     208-212 
022800         10  CASH-AC6-USOC             PIC  X(5).                 213-217 
022900         10  CASH-AC6-DENIABLE         PIC  X(1).                 218     
023000             88  DENIABLE-AC6       VALUE 'Y'.                            
023100             88  NON-DENIABLE-AC6   VALUE 'N'.                            
023200         10  CASH-AC6-CSS-PPS          PIC  X(2).                 219-220 
023300         10  CASH-AC6-COLL-RPT-LN      PIC  X(1).                 221     
023400     05  CASH-CHARGE-NBR.                                         222-231 
023500         10  CASH-CHRG-NBR-NPA     PIC X(3).                      222-224 
023600         10  CASH-CHRG-NBR-CO      PIC X(3).                      225-227 
023700         10  CASH-CHRG-NBR-LINE    PIC X(4).                      228-231 
023800     05  CASH-CIRCUIT-NBR          PIC X(45).                     232-276 
023900     05  CASH-PEND-CLAIM-NBR       PIC X(12).                     277-288 
024000     05  CASH-DISCONNECT-DATE.                                    289-296 
024100         10  CASH-DISC-DATE-YYYY   PIC X(4).                      289-292 
024200         10  CASH-DISC-DATE-MM     PIC X(2).                      293-294 
024300         10  CASH-DISC-DATE-DD     PIC X(2).                      295-296 
024400     05  CASH-SUB-ENTITY-CODE      PIC X(6).                      297-302 
024500     05  CASH-FLEX-SUB-CIC-DATA                                   297-302 
024600             REDEFINES CASH-SUB-ENTITY-CODE.                              
024700         10  CASH-SUB-CIC-FILLER   PIC X(2).                      297-298 
024800         10  CASH-FLEX-SUB-CIC     PIC X(4).                      299-302 
024900     05  CASH-SECONDARY-ENTITY-CODE                               297-302 
025000             REDEFINES CASH-SUB-ENTITY-CODE.                              
025100         10  FILLER                PIC X(6).                      297-302 
025200     05  CASH-OCA-IND              PIC X(1).                      303     
025300     05  CASH-RISK-PORTFOLIO       PIC X(8).                      304-311 
025400     05  CASH-RISK-RPT-GRP         PIC X(8).                      312-319 
025500     05  CASH-GEO-DATA.                                           320-334 
025600         10  CASH-GEO-STATE-CODE   PIC X(2).                      320-321 
025700         10  CASH-GEO-COUNTY-CODE  PIC X(3).                      322-324 
025800         10  CASH-GEO-CITY-CODE    PIC X(4).                      325-328 
025900         10  CASH-GEO-FILLER       PIC X(3).                      329-331 
026000         10  CASH-GEO-TAX-TYPE     PIC X(2).                      332-333 
026100         10  CASH-GEO-AUTH-CODE    PIC X(1).                      334     
026200     05  CASH-SETTLE-RATE          PIC S9(7)V9(2) COMP-3.         335-339 
026300     05  CASH-SETTLE-RATE-X REDEFINES CASH-SETTLE-RATE            335-339 
026400                                   PIC X(5).                              
026500     05  CASH-ADJ-DESC-CODE        PIC X(5).                      340-344 
026600     05  CASH-FILLER1              PIC X(2).                      345-346 
026700     05  CASH-RELEASE-IND          PIC X(1).                      347     
026800         88  CASH-REL-96-3         VALUE 'A'.                             
026900     05  CASH-TAR-CODES.                                          348-353 
027000         10  CASH-CITY-TAR         PIC  X(3).                     348-350 
027100         10  CASH-CNTY-TAR         PIC  X(3).                     351-353 
027200     05  CASH-ENTITY-CODE.                                        354-359 
027300         10  CASH-JOURNAL-ID.                                     354-356 
027400             15  CASH-JRNL-1       PIC  X(1).                     354     
027500             15  CASH-JRNL-2       PIC  X(2).                     355-356 
027600         10  CASH-JOURNAL-FILLER   PIC  X(3).                     357-359 
027700     05  CASH-CK-CHRG-IND          PIC  X(1).                     360     
027800     05  CASH-TRACK-PCR            PIC  X(1).                     361     
027900     05  CASH-CARR-ADJ-IND         PIC  X(1).                     362     
028000     05  CASH-NUM-CARR-ADJ-CALLS   PIC  X(4).                     363-366 
028100     05  CASH-SERVICE-CODE.                                       367-369 
028200         10  CASH-SVC-CODE-2CHAR     PIC  X(2).                   367-368 
028300             88  COIN-SEMI-PUBLIC  VALUE '31' '35'.                       
028400             88  COIN-PUBLIC       VALUE '32' '33' '34'.                  
028500             88  COIN-CPE          VALUE '3A' '3B' '3C'                   
028600                                         '3D' '3E' '3F'                   
028700                                         '3G' '3H' '3I'                   
028800                                         '3J' '3K' '3L'                   
028900                                         '3M' '3N' '3P'.                  
029000         10  CASH-SVC-CODE-3CHAR     PIC  X(1).                   369     
029100     05  CASH-BANK-JRNL-DATA.                                     370-383 
029200         10  CASH-BANK-NUMBER      PIC  X(6).                     370-375 
029300         10  CASH-RESP-CODE        PIC  X(8).                     376-383 
029900     05  CASH-LTS-INDICATOR        PIC  X(1).                     384     
030000     05  CASH-LARGE-USER-DATA.                                    385-411 
030100         10  CASH-DI-CODE          PIC  X(25).                    385-409 
030200         10  CASH-VCHR-NO          PIC  X(2).                     410-411 
030300     05  CASH-CONCESSION-CODE      PIC  X(3).                     412-414 
030400     05  CASH-DIRECTORY-BOOK-NUMBER                               415-421 
030500                                   PIC  X(7).                             
030600     05  CASH-RESELLER-IND         PIC  X(1).                     422     
030700     05  CASH-RESALE-INDS.                                        423-428 
030800         10  CASH-RESALE-FED       PIC  X(1).                     423     
030900         10  CASH-RESALE-STATE     PIC  X(1).                     424     
031000         10  CASH-RESALE-CNTY      PIC  X(1).                     425     
031100         10  CASH-RESALE-CITY      PIC  X(1).                     426     
031200         10  CASH-RESALE-FRAN      PIC  X(1).                     427     
031300         10  CASH-RESALE-GRS       PIC  X(1).                     428     
031400     05  CASH-BAD-DEBT-IND         PIC  X(1).                     429     
031500     05  CASH-P10-IND              PIC  X(1).                     430     
031600     05  CASH-C10-IND              PIC  X(1).                     431     
031700     05  CASH-BALANCE-DUE          PIC  X(10).                    432-441 
031800     05  APPROVAL-IND         PIC  X.                        442     
031900         88  APPR-BANKRUPT-ACCT-5031             VALUE '1'.               
032000         88  APPR-FED-POL-CAMPGN-ACCT-5031       VALUE '2'.               
032100         88  APPR-STATE-LOCAL-POL-ACCT-5031      VALUE '3'.               
032200         88  APPR-OFFICIAL-ACCT-5031             VALUE '4'.               
032300     05  CASH-BASIC-CLASS-SERV     PIC  X(5).                     443-447 
032400     05  CASH-EARNING-NUM.                                        448-460 
032500         10  CASH-EARN-NPA         PIC X(3).                      448-450 
032600         10  CASH-EARN-CO          PIC X(3).                      451-453 
032700         10  CASH-EARN-LINE        PIC X(4).                      454-457 
032800         10  CASH-EARN-CC          PIC X(3).                      458-460 
032900     05  CASH-FLEX-INV-CHARGE-NUM                                 448-460 
033000             REDEFINES CASH-EARNING-NUM.                                  
033100         10  CASH-FLEX-NPA         PIC X(3).                      448-450 
033200         10  CASH-FLEX-CO          PIC X(3).                      451-453 
033300         10  CASH-FLEX-LINE        PIC X(4).                      454-457 
033400         10  CASH-FLEX-CC          PIC X(3).                      458-460 
033500     05  CASH-DISCONNECT-RSN       PIC X(2).                      461-462 
033600     05  CASH-TRANSFER-URB-AMOUNT  PIC S9(7)V9(2) COMP-3.         463-467 
033700     05  CASH-RAO                  PIC X(3).                      468-470 
033800     05  CASH-IDB-IND              PIC X(1).                      471     
033900     05  CASH-TRANS-FROM-NUM.                                     472-484 
034000         10  CASH-FROM-NPA         PIC X(3).                      472-474 
034100         10  CASH-FROM-CO          PIC X(3).                      475-477 
034200         10  CASH-FROM-LINE        PIC X(4).                      478-481 
034300         10  CASH-FROM-CC          PIC X(3).                      482-484 
034400     05  CASH-TRANSFER-PREV-URB-AMOUNT  PIC S9(7)V9(2) COMP-3.    485-489 
034500     05  CASH-BUS-UNIT-IND         PIC X(10).                     490-499 
034600     05  CASH-ETET-IND             PIC X(1).                      500     
034700     05  CASH-CBA-NUM              PIC X(13).                     501-513 
034800     05  CASH-CBA-BP-YYMMDD        PIC X(6).                      514-519 
034900     05  CASH-LPA-CARRIER-ID       PIC X(6).                      520-525 
035000     05  CASH-LPA-BUS-OFFICE       PIC X(4).                      526-529 
035100     05  CASH-LPA-BATCH-NUM        PIC X(4).                      530-533 
035200     05  CASH-LPA-TRANS-TYPE       PIC X(1).                      534     
035300     05  CASH-LPA-POST-DATE-MMDD   PIC X(4).                      535-538 
035400     05  CASH-LPA-PEND-CLAIM-NUM   PIC X(12).                     539-550 
035500     05  CASH-LPA-AMOUNT           PIC S9(9)V9(2) COMP-3.         551-556 
035600     05  CASH-LPA-BILL-DATE-YYMMDD PIC X(6).                      557-562 
035700     05  CASH-OFE-IND              PIC X(1).                      563     
035800     05  CASH-SERIAL-NUMBER        PIC X(7).                      564-570 
035900     05  CASH-OCASK-IND            PIC X(1).                      571     
036000     05  CASH-UNE-DISCHK-RSN-CODE  PIC X(3).                      572-574 
036000     05  CAPM-DISCHK-RSN-CODE                                     572-574 
036000                REDEFINES CASH-UNE-DISCHK-RSN-CODE PIC X(3).      572-574 
036100     05  CASH-UNE-MULTI-IND        PIC X(1).                      575     
036200     05  CASH-UNE-OMIT-IND         PIC X(1).                      576     
036300     05  CASH-VCHR-TRANS-ID        PIC X(12).                     577-588 
036301     05  FILLER REDEFINES CASH-VCHR-TRANS-ID.                     577-588 
036302         10 CASH-VCH-CAPM-ITEM-SEQ-NUM        PIC X(04).          577-580 
036303         10 CASH-VCH-CAPM-RC                  PIC X(03).          581-583 
036304         10 FILLER                            PIC X(05).          584-588 
036305     05  CASH-ORIGINATOR-CUID      PIC X(8).                      589-596 
036306     05  CASH-AUDITOR-CUID         PIC X(8).                      597-604 
036307     05  CASH-SCREEN               PIC X(4).                      605-608 
036308     05  CASH-UNAPP-CORR-CUID      PIC X(8).                      609-616 
036309     05  CASH-CBR-TC-IND           PIC X(9).                      617-625 
036310     05  CASH-CBR-CR-LIA-IND       PIC X(3).                      626-628 
036311     05  CASH-CBR-AC               PIC X(3).                      629-631 
036312     05  CASH-CBR-SEQ              PIC X(1).                      632     
036313     05  CASH-BOCRIS-VCHR-NUM      PIC X(9).                      633-641 
036314     05  CASH-OVERAGE-ACCT-IND     PIC X(1).                      642     
036320     05  CASH-VCH-CAPM-REF-NUMBER             PIC X(20).          643-662 
036330     05  CASH-VCH-CAPM-ENTRY-SOURCE           PIC X(08).          663-670 
036340     05  CASH-VCH-CAPM-SYSID                  PIC X(03).          671-673 
036350     05  CASH-VCH-CAPM-DIVID                  PIC X(03).          674-676 
036360     05  CASH-VCH-CAPM-BATCH-NUM              PIC X(05).          677-681 
036370     05  CASH-VCH-CAPM-TRANS-SEQ-NUM          PIC X(06).          682-687 
036380     05  CASH-VCH-CAPM-TRANS-TYPE             PIC X(03).          688-690 
036381     05  CASH-VCH-CAPM-PAYMENT-MEDIA          PIC X(01).          691     
036382     05  CASH-VCH-BUY-OCA-ID                  PIC X(02).          692-693 
036383     05  CASH-FILLER2              PIC X(307).                    694-1000
