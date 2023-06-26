@echo off
for /F "tokens=*" %%A in  (files.TXT) do  (
   ECHO Processing %%A.... 
   CALL python3 -m BG3_Dialog_Parser --loc-file "D:\Games\BG3 Datamining\english.xml" --unpack-dir "D:\Games\BG3 Datamining\.Modders multitool 0.8.3\UnpackedData" --dialog-file %%A
)
@echo on