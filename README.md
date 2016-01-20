# *HDHR2PLEX*  
A small project called to develop some python scripts to aid in archiving [SiliconDust](http://www.silicondust.comhttp://www.silicondust.com) HDHomerun DVR recordings to plex.
It uses the [thetvdb]([http://www.thetvdb.com]) for season and episode information for when the guide from SiliconDust doesn't.

**_Prerequisites_**  
- Python (2.6+)  
- tvdb_api [tvdb_api](https://github.com/dbr/tvdb_api/)


**_Current Status_**  
At this stage scripts are still in development and dependent on updates from SiliconDust.  
The *parse-folder.py* is now parked once Silicondust added the feature for the DVR recorder to save to separate folders. I will hopefully get to this again soon.  
The *fix_filenames.py* iterates through all the files in the HDHR recordings folder, scans the TS file for meta data and then does a look up on thetvdb for missing info before renaming the file to match Plex requirements (and optionally the folder).  
The *create_mdonly.py* provides a simple script to take the output metadata from the logfiles and generate a valid MPG for testing.  

**_Tested Platforms_**  
QNAP-x51 with QTS 4.1.4/4.2  (linux)

**_Usage_**  
```sh
$ python fix-filenames.py --config <config file>
```
```sh
$ python ./create_mdonly.py <metadata file>
```


**_Config File_**  
all the configuration details are stored in a section titled  [HDHR-DVR]
the parameters include

logfile:  
- location of the log file to output to - leave blank to print to STDOUT  

loglevel:  
- logging level to use [debug, info, warn, error, critical]  

dvrpath:  
- Path to the HDHomerun DVR recordings (whatever you set RecordPath to)  

plexpath:
- Path to the where Plex will scan for the HDHomerun recordings

renamefile:
- Set to True to rename the file

renamedir:
- Set to True to move the file to a folder with the correct showname

forceupdate:
- force the script to update every file found - disables the skipping

winaction:
- Not implemented at this time