# *HDHR2PLEX*  
A small project called to develop some python scripts to aid in archiving [SiliconDust](http://www.silicondust.comhttp://www.silicondust.com) HDHomerun DVR recordings to plex.
It uses the [thetvdb]([http://www.thetvdb.com]) for season and episode information for when the guide from SiliconDust doesn't.

**_Prerequisites_**  
- Python (2.6+)  
- tvdb_api [tvdb_api](https://github.com/dbr/tvdb_api/)


**_Current Status_**  
At this stage scripts are still in development and dependent on updates from SiliconDust.  
The *archive2plex.py* will parse the HDHR recordings folder, match the series and episodes to thetvdb and then archive the files to Plex folder depending on settings in the configuration file.
The *fix_filenames.py* iterates through all the files in the HDHR recordings folder, scans the TS file for meta data and then does a look up on thetvdb for missing info before renaming the file to match Plex requirements (and optionally the folder).  
The *create_mdonly.py* provides a simple script to take the output metadata from the logfiles and generate a valid MPG for testing.  
The *dump_md.py* scans an MPG file for the HDHR metadata section and dumps to STDOUT  

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
The main configuration details are stored in a section titled  [HDHR-DVR]
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
- name of section that contains a list of the shows to skip.

forceshows:
- name of section that contains a list of the skipshows.

livedelay:
- number of seconds that the file should be untouched/unmodified before parsing

days2delete:
- days to delete the metadata file once created.. Note: if you add a show to 'forceshows' the original HDHR file will be deleted even though it was skipped for parsing. Set to 0 to disable.

days2archive:
- days to expire before files are moved from HDHR to Plex. Set to 0 to make it immediate.

*** Skipping Shows ***
Some shows you just don't want to backup to Plex, and some shows cause issues and you want to skip them.
To do so just create a section matching the name provided in the configuration files 'skipshows' parameter and the scripts will parse the list.
Each entry must have a unique key. Recommendation is simply to number the entries, For Example

[skip_shows]
1: "Masterpiece Classic"
2: "Masterpiece"
3: "The Tonight Show with Jimmy Fallon"
4: "Masterchef"

*** Force Shows ***
Some of the shows in your skip list you want to force the scripts to remove once days2delete are expired.
But because they are in the skip list, they won't be processed.
To bring them back into consideration for deleting add the shows to a new section matching the name provided in the configuration files 'forceshows' forceshows
Each entry must have a unique key. Recommendation is simply to number the entries, For Example

[force_shows]
1: "Hell's Kitchen"
