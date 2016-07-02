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
languages = {}

class HDHomeRunPath:
	try:
		basestring  # attempt to evaluate basestring
		def isstr(s):
			return isinstance(s, basestring)
	except NameError:
		def isstr(s):
			return isinstance(s, str)

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
	
	def is_skip_show(self, showname):
		if not shows2skip:
			return False
		for show in shows2skip:
			if showname.lower() == show.replace('"','').lower():
				logging.debug('Skip show found ' + showname)
				return True
		return False
	
	def get_season_from_epnumber(self, epNumber):
		season = '00'
		if self.isstr(epNumber):
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
		if languages:
			langStr = ""
			if len(languages) > 1:
				for lang in languages:
					langStr += lang + ','
			else:
				langStr = languages[0]
			hdhr_thetvdb.languages = langStr
		md.print_metaData()
	
		show = md.extract_show()
		epNumber = md.extract_epNumber()
		epAirDate = md.extract_epAirDate()
		epTitle = md.extract_epTitle()
		season = episode = name = ''
	
		# Need to workaround some bad titles that US TV and thetvdb.com are in conflict for.
		if not self.is_skip_show(show):
			tvdbEpData = db.getTVDBInfo(show,epAirDate,epTitle,epNumber)
			season = tvdbEpData['season_num']
			episode = tvdbEpData['episode_num']
			name =  tvdbEpData['seriesname']
			
			# fix for double episode
			if 'episode2_num' in tvdbEpData:
				episode = episode + 'E' + tvdbEpData['episode2_num']
			
			if name == season == episode == '':
				logging.debug('Got nothing from thetvdb, so going to have to fall back to whatever was provided by SD')
				return {'show':show, 'tvdbname':'', 'season':self.get_season_from_epnumber(epNumber), 'epnum':epNumber, 'eptitle':epTitle}
			else:
				logging.info('=== Extracted from thetvdb for [' + show + ']: seriesname [' + name + '] Season [' + season + '] Episode: [' + episode +']')
				return {'show':show, 'tvdbname':name, 'season':season, 'epnum':('S'+season+'E'+episode), 'eptitle':epTitle}
		else:
			logging.debug('*** Show [' + show + '] marked for special handling - and will not use theTvDb.com')
			season = self.get_season_from_epnumber(epNumber)
			return {'show':show, 'tvdbname':'', 'season':season, 'epnum':epNumber, 'eptitle':epTitle}
	
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
		tswr = hdhr_tswriter.TSWriter(metadata)
		tswr.add_custom_md('"hdhr2plex"','1')
		tswr.create_ts_file(filename)
		return
		
	def is_special_show_type(self, showname):
		logging.info('Checking Show ' + showname + ' is not Movie or Sporting Event')
		if (showname == hdhr_type_movies) or (showname == hdhr_type_sports):
			return True
		return False
		
	def fix_title(self, epTitle):
		newTitle = str.replace(epTitle,'/','_')
		return newTitle
	
	def fix_filename(self, show, season, episode, epTitle):
		basename = show + '-' + episode
		newTitle = self.fix_title(epTitle)
		if newTitle == '':
			return basename + '.mpg'
		else:
			return basename + '-' + newTitle + '.mpg'
	
	def is_already_fixed(self, filename):
		# Checking file is form of <show>-S<season number>E<episode number>[- title]
		# where title is optional, but must have show, season and episode numbers
		regexPatSearch = re.compile(r'-S\d+E\d+-')
		if regexPatSearch.search(filename):
			logging.debug('Matched SxxExx in filename: ' + filename)
			return True
		#Check for double episode pattern
		regexPatSearch = re.compile(r'-S\d+E\d+E\d+-')
		if regexPatSearch.search(filename):
			logging.debug('Matched SxxExxExx in filename: ' + filename)
			return True
			
		return False
	
	def rename_episode(self, filename, show, season, episode, epTitle, renameDir, force):
		if not epTitle:
			epTitle = ''
		base_name = os.path.basename(filename)
	
		# shouldn't need to recheck, but may as well..
		if (base_name == self.fix_filename(show, season, episode, epTitle)) & (not force):
			logging.warn('Filename '+ base_name + ' already fixed')
		else:
			dir_name = os.path.dirname(filename)
			if renameDir:
				parentDir = os.path.dirname(dir_name)
				oldShowDir = os.path.basename(dir_name)
				logging.debug('parent path: [' + parentDir + '] with show [' + oldShowDir + '] comparing to [' + show + ']')
				if not oldShowDir == show:
					dir_name = os.path.join(parentDir, show)
					logging.debug('Setting output path to: ' + dir_name)
					if not os.path.exists(dir_name):
						logging.debug(' Creating new folders for: ' + dir_name)
						os.makedirs(dir_name)
    
    		new_name = os.path.join(dir_name, self.fix_filename(show, season, episode, epTitle))
    		logging.debug('replacing ' + filename + ' with ' + new_name)
    		os.rename(filename,new_name)