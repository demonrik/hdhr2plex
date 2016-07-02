#-------------------------------------------------------------------------------
# This is an automated python script to archive recordings from HDHomeRun DVR
# to your local plex archive
#
# All configuration is provided on the command line config file
#
# Please ensure 'livedelay' is set to a sufficiently high number of seconds to
# detect when a file is currently 'live' and being updated. The script will retry
# the file stats after 'livedelay' seconds to ensure that the file isn't being
# updated - if the check fails, it will be skipped and done on the next execution
# of the script.
#
# The script will scan the DVR folder for files older than 'days2archive'. Once 
# found the script will move the file to the appropriate Plex Show/Season folder,
# rename the file inline with Plex requirements (i.e. SxxExx), and then save back
# a small metadata only file to the HDHomeRun DVR folder to prevent a duplicate
# recording. That meta data file will also contain a unique hdhr2plex tag to
# indicate that the file was processed by this script.
# Note: should days2archive be 0 - the file will always be archived.
# Should the script on scanning the DVR folder find a metadata file with the
# hdhr2plex tag it will check if the file is older than 'days2delete' and if it
# is it will then remove the metadata file  (unless days2delete is set to 0)
#
#-------------------------------------------------------------------------------

import getpass
import os
import platform
import logging
import sys
import re
import shutil
import time
from time import strftime

import hdhr_path
import scripttools
import plextools

if __name__ == "__main__":
	files = []
	episodes = []
	tools = scripttools.ScriptTools()
	if tools.isInteractive() == True:
		print 'Interactive mode not supported at this time... exiting...'
		sys.exit(0)

	logging.info('------------------------------------------------------------')
	logging.info('-                  HDHR2PLEX - archive2plex                -')
	logging.info('-                   '+strftime("%Y-%m-%d %H:%M:%S")+'                    -')
	logging.info('------------------------------------------------------------')

	pathTools = hdhr_path.HDHomeRunPath()

	hdhr_path.shows2skip = tools.get_skip_shows()
	hdhr_path.languages = tools.get_languages()
	logging.debug('Skip Shows ' + str(hdhr_path.shows2skip))
	logging.debug('Languages ' + str(hdhr_path.languages))

	shows = pathTools.get_shows_in_dir(tools.get_dvr_path())
	for show in shows:
		# Check for Movies/Sporting Events - needs to go be handled differently
		if pathTools.is_special_show_type(os.path.basename(show)):
			# TODO: handle these shows - for now skip
			logging.warn('*** Movie or Sporting Event found - Skipping ***')
			continue
		episodes = pathTools.get_episodes_in_show(show)
		files.extend(episodes)

	for f in files:
		metaData = []
		logging.info('-----------------------------------------------')
		logging.info('Parsing: ' + f)
		
		# Check if file meets the age requirements for archiving
		if not pathTools.is_older_than(f, int(tools.getDays2Archive())*24*60*60):
			logging.info('File is not yet met days to archive [' + str(int(tools.getDays2Archive())*24*60*60) + '] seconds, skipping' )
			continue

		# Parse the Metadata
		metaData = pathTools.parse_file_for_data(f)
		if pathTools.check_parsed_by_hdhr2plex(metaData):
			continue
		md = pathTools.extract_metadata(metaData)
		logging.debug('Ready with show: ' + str(md))
		
		if (pathTools.is_older_than(f,tools.getLiveDelay())):
			logging.debug('File not updated since livedelay - ok to proceed')
			
			# Prep Plex Folders
			plexTools = plextools.PlexTools(tools.get_plex_path())
			if not plexTools.check_show_in_plex(md['show']):
				logging.debug('Show does not exist in Plex - need to create it and season')
				plexTools.add_season_to_plex(md['show'],md['season'])
			else:
				if plexTools.check_season_in_plex(md['show'],md['season']):
					logging.debug('Season exists already in Plex')
				else:
					logging.debug('Season doesn\'t exist in plexpath - creating')
					plexTools.add_season_to_plex(md['show'],md['season'])
			
			# Move file to plex
			existing_filename = plexTools.find_filename(md['show'],md['season'],md['epnum'])
			plex_filename = plexTools.construct_filename(md['show'],md['season'],md['epnum'],md['eptitle'],'.mpg')
			
			if not (existing_filename == ''):
				if not existing_filename == plex_filename:
					logging.warn('File already exists for this episode - but is different filename')
					logging.warn('continuing with move of file - upto the User to resolve Plex conflicts')
					# TODO: Add option to skip and not create conflicts
				else:
					logging.warn('File already exists with same filename - Skipping')
					# TODO: Create unique filename, and move if config option set to force the move
					continue
			
			# ok to move file
			if plexTools.move_episode_to_plex(md['show'],md['season'], plex_filename, f):
				# Post Process the File
				plexTools.post_process_file(md['show'],md['season'], plex_filename, tools.getPostProc())
				# Save metadata file or softlink back
				pathTools.save_min_metadata(f,metaData)
		else:
			logging.warn(f + ' has been updated recently - skipping in case HDHR is still writing to it')
			continue

	logging.info('------------------------------------------------------------')
	logging.info('-              HDHR2PLEX - archive2plex - Complete         -')
	logging.info('-                   '+strftime("%Y-%m-%d %H:%M:%S")+'                    -')
	logging.info('------------------------------------------------------------')