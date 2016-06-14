#-------------------------------------------------------------------------------
# This is an automated python script to parse out the metadata from MPEG-TS
# files created by the HDHomeRun DVR record engine.
#-------------------------------------------------------------------------------
import os
import sys
import logging
import time
from time import strftime

import hdhr_path
import scripttools

if __name__ == "__main__":
	files = []
	episodes = []
	tools = scripttools.ScriptTools()
	if tools.isInteractive() == True:
		print 'Interactive mode not supported at this time... exiting...'
		sys.exit(0)

	logging.info('------------------------------------------------------------')
	logging.info('-                  HDHR TS MetaData Tool                   -')
	logging.info('-                   '+strftime("%Y-%m-%d %H:%M:%S")+'                    -')
	logging.info('------------------------------------------------------------')

	pathTools = hdhr_path.HDHomeRunPath()
	hdhr_path.shows2skip = tools.get_skip_shows()
	logging.debug('Skip Shows ' + str(hdhr_path.shows2skip))

	shows = pathTools.get_shows_in_dir(tools.get_dvr_path())
	for show in shows:
		# Check for Movies/Sporting Events - needs to go be handled differently
		if pathTools.is_special_show_type(os.path.basename(show)):
			# TODO: handle these shows - for now skip
			logging.warn('*** Movie or Sporting Event found - Skipping ***')
			continue
		if pathTools.is_skip_show(os.path.basename(show)):
			logging.warn('*** Show ' + os.path.basename(show) + 'found in skip list, skipping ***')
			continue
		
		episodes = pathTools.get_episodes_in_show(show)
		files.extend(episodes)

	for f in files:
		metaData = []
		logging.info('-----------------------------------------------')
		if pathTools.is_already_fixed(f) & (not tools.forceEnabled()):
			logging.info('SKIPPING: Already fixed ' + f)
			continue
		logging.info('Parsing: ' + f)

		# Parse the Metadata
		metaData = pathTools.parse_file_for_data(f)
		if pathTools.check_parsed_by_hdhr2plex(metaData):
			continue
		md = pathTools.extract_metadata(metaData)
		logging.debug('Ready with show: ' + str(md))

		# Might need to rename the directory to match thetvdb..
		if tools.dirRename() and (md['tvdbname'] != '') :
			logging.info('Setting showname to: ' + md['tvdbname'])
			showname = md['tvdbname']
		else:
			logging.info('Setting showname to: ' + md['show'])
			showname = md['show']

		# Ready to rename the file for easier Plex integration..
		logging.info('Renaming ' + f)
		pathTools.rename_episode(f,showname,md['season'],md['epnum'],md['eptitle'],tools.dirRename(), tools.forceEnabled())
		logging.info('Completed for : ' + f)

	logging.info('------------------------------------------------------------')
	logging.info('-              HDHR TS MetaData Tool Complete              -')
	logging.info('-                   '+strftime("%Y-%m-%d %H:%M:%S")+'                    -')
	logging.info('------------------------------------------------------------')

