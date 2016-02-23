#-------------------------------------------------------------------------------
# Utilities for processing the HDHR DVR Path
#-------------------------------------------------------------------------------
import os
import logging
import re
import time
from time import strftime
import datetime

import hdhr_tsparser
import hdhr_tswriter
import hdhr_md
import hdhr_thetvdb


HDHR_TS_METADATA_PID = 0x1FFA

hdhr_type_movies = 'Movies'
hdhr_type_sports = 'Sporting Events'


shows2skip = {}

class HDHomeRunPath:
	def __init__(self):
		return

	# QNAP NAS adds thumbnails with it's media scanner - so will skip that dir
	# TODO: Make skip dirs configurable
	def get_shows_in_dir(self, path):
		return [os.path.join(path,f) for f in os.listdir(path) \
			if (not ".@__thumb" in f) & os.path.isdir(os.path.join(path,f))]
	
	def get_episodes_in_show(self, path):
		return [os.path.join(path,f) for f in os.listdir(path) \
			if (not os.path.islink(os.path.join(path,f))) & os.path.isfile(os.path.join(path,f)) \
			& f.endswith('.mpg')]

	def parse_file_for_data(self, filename):
		parser = hdhr_tsparser.TSParser(filename)
		payloads = 0
		tempMD = []
		pid_found = False
		for b in parser.read_next_section():
			payloads+=1
			header = parser.parse_ts_header(b)
			if parser.header_contains_pid(header,HDHR_TS_METADATA_PID):
				# found a matching program ID - need to reconstruct the payload
				tempMD += parser.extract_payload(b)
				pid_found = True
			else:
				# Didn't find HDHR MetaData PID.. so break if we found already
				if pid_found == True:
					break
		return parser.extract_metadata(tempMD)
	
	def isSpecialShow(self, showname):
		if not shows2skip:
			return False
		for show in shows2skip:
			if showname.lower() == show.replace('"','').lower():
				logging.debug('Skip show found ' + showname)
				return True
		return False
	
	def get_season_from_epnumber(self, epNumber):
		season = '00'
		if len(re.findall('S\d{2}E\d{2}',epNumber)) > 0:
			season = re.findall('S\d{2}',epNumber)[0].replace('S','')
		return season
		
	def check_parsed_by_hdhr2plex(self, metadata):
		md = hdhr_md.HDHomeRunMD(metadata)
		if not (md.extract_hdhr2plex() == ''):
			logging.debug('File already modified by hdhr2plex - value exists in metadata')
			return True
		return False
	
	def extract_metadata(self, metadata):
		md = hdhr_md.HDHomeRunMD(metadata)
		db = hdhr_thetvdb.TVDBMatcher()
		md.print_metaData()
	
		show = md.extract_show()
		epNumber = md.extract_epNumber()
		epAirDate = md.extract_epAirDate()
		epTitle = md.extract_epTitle()
		season = episode = name = ''
	
		# Need to workaround some bad titles that US TV and thetvdb.com are in conflict for.
		if not self.isSpecialShow(show):
			tvdbEpData = db.getTVDBInfo(show,epAirDate,epTitle,epNumber)
			season = tvdbEpData['season_num']
			episode = tvdbEpData['episode_num']
			name =  tvdbEpData['seriesname']
			if name == season == episode == '':
				logging.debug('Got nothing from thetvdb, so going to have to fall back to whatever was provided by SD')
				return {'show':show, 'season':self.get_season_from_epnumber(epNumber), 'epnum':epNumber, 'eptitle':epTitle}
			else:
				logging.info('=== Extracted from thetvdb for [' + show + ']: seriesname [' + name + '] Season [' + season + '] Episode: [' + episode +']')
				return {'show':name, 'season':season, 'epnum':('S'+season+'E'+episode), 'eptitle':epTitle}
		else:
			logging.debug('*** Show [' + show + '] marked for special handling - and will not use theTvDb.com')
			season = self.get_season_from_epnumber(epNumber)
			return {'show':show, 'season':season, 'epnum':epNumber, 'eptitle':epTitle}
	
	def is_older_than(self, filename, numSecs):
		fmtime = datetime.datetime.fromtimestamp(os.stat(filename).st_mtime)
		last_time = int((datetime.datetime.utcnow() - fmtime).total_seconds())
		
		logging.debug(filename + ' was modified ' + str(fmtime) + ' time is now: ' + str(datetime.datetime.utcnow()) + ' difference is ' + str(last_time) + ' seconds')
		if last_time < int(numSecs):
			return False;
		else:
			return True;
			
	def save_min_metadata(self,filename,metadata):
		logging.info('Resaving metadata as ' + filename)
		md = hdhr_md.HDHomeRunMD(metadata)
		tswr = hdhr_tswriter.TSWriter(metadata)
		tswr.add_custom_md('"hdhr2plex"','1')
		tswr.create_ts_file(filename)
		return
		
	def is_special_show_type(self, showname):
		logging.info('Checking Show ' + showname + ' is not Movie or Sporting Event')
		if (showname == hdhr_type_movies) or (showname == hdhr_type_sports):
			return True
		return False