0. When first setting it up:
	in "BG3_Dialog_Parser.bat" change the localization file path (atm it's "D:\Games\BG3 Datamining\english.xml") and the unpacked files path (atm "D:\Games\BG3 Datamining\.Modders multitool 0.8.3\UnpackedData") (Gustav and Shared should be unpacked)
	
	
1. Write dialogue file paths for everything you want parsed into "files.txt". One path per line, WITH quotation marks, like:
"D:\Games\BG3 Datamining\.Modders multitool 0.8.3\UnpackedData\Gustav\Mods\Gustav\Story\Dialogs\Camp\Campfire_Moments\CAMP_HalsinsReturn_CFM.lsj"
	You can get the paths by SHIFT+right click on the file > Copy as path.
	If you select several files, make it ALT+SHIFT+rightclick.
	You can search for all .lsj file in your explorer if you want to get the files from a folder's subfolders.

2. Open Command Prompt
	press Win+R, type cmd

2a. Navigate to the .bat file and run it.
	If it's not on the C drive, switch to the correct drive:
		d:
	Navigate to the folder with the .bat file. For me it's:
		cd "D:\Games\BG3 Datamining\!BG3_Dialog_Parser"
	Run the .bat file
		BG3_Dialog_Parser.bat
