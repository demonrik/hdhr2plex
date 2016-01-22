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
- Path to the HDHomerun DVR recordings Folder (whatever you set RecordPath to)  

plexpath:
- Path to the Folder where Plex will scan for the HDHomerun recordings

link2plex:
- Set to True to link the DVR file to your Plex folder. i.e. files are not to be exported to Plex Folder

link2dvr:
- Set to True to indicate that the script should move the file from the DVR folder to the Plex Folder, rename to meet the TVDB lookups and link the resulting file back to the DVR folder under the original filename

metasave:
- Set to True to indicate that the script should move the file from the DVR folder to the Plex Folder, rename to meet the TVDB lookups, but save the extracted meta data from the DVR file back to the DVR folder to prevent repeat recordings.

renamefile:
- Set to True to rename the file

renamedir:
- Set to True to move the file to a folder with the correct showname

forceupdate:
- force the script to update every file found - disables the skipping

skipshows:
- A number of shows cause issues with thetvdb.com and will prevent matches, and thus cause strange behaviour with the script, or even crashes. If you encounter such a show add it here.
The show name must be in double quotes, i.e. "Masterpiece"
Separate each show with a comma, i.e. "Masterpeice","That other Show"

