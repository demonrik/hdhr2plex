#-------------------------------------------------------------------------------
# HDHomerun thetvdb API metadata matcher
#-------------------------------------------------------------------------------
import os
import logging
import re
import time
from time import strftime
import datetime
import tvdb_api


class TVDBMatcher:
	def __init__(self):
		return
	
	def isSeriesNameAllowed(self, showname, seriesname):
		if showname == seriesname:
			return True;
		else:
			# check for 'showname (something)'
			if len(re.findall('^' + showname + '\s\(\S+\)', seriesname))>0:
				logging.debug('Found alternative name [' + seriesname + '] for ' + showname)
				return True;
			return False;
	
	def lookup_episode_bydate(self, showname, epAirdate):
		epCandidates = []
		logging.info('Finding Episode/Season details by showname and airdate')
		logging.debug('Connecting to theTVdb.com')
		tvdb = tvdb_api.Tvdb()
		logging.debug('Finding the shows with the name ' + showname)
		seriesname = ''
		season = 0
		episodeNum = 0

		allseries = tvdb.search(showname)
		
		for x in range(len(allseries)):
			seriesname = allseries[x]['seriesname']
			if self.isSeriesNameAllowed(showname,seriesname):
				logging.debug('Checking SeriesName ' + seriesname + ' for matching episode')
			else:
				continue;
			show = tvdb[seriesname]
			for season in show:
				seasondata = tvdb[seriesname][season]
				for ep in seasondata:
					epData = seasondata[ep]
					if not epData['firstaired']:
						logging.debug('No air date for episode ' + seriesname + '|' + epData['episodenumber'] + '- might need to rely on date from file?')
					else:
						ep_date = datetime.datetime.strptime(epData['firstaired'],'%Y-%m-%d')
						check_date = datetime.datetime.utcfromtimestamp(int(epAirdate))
						if ep_date == check_date:
							logging.info('MATCHED Season [' + str(season) + '] Episode [' + str(ep) + ']')
							epCandidates.append(epData)
						else:
							logging.debug('No match in ' + epData['episodenumber'] + ' for airdate ' + epAirdate)
		return epCandidates

	def getTVDBSeriesName(self, showname, seriesID):
		logging.debug('Connecting to theTVdb.com')
		tvdb = tvdb_api.Tvdb()
		logging.debug('Finding the shows with the ID ' + seriesID)
		allseries = tvdb.search(showname)
		for x in range(len(allseries)):
			if allseries[x]['seriesid'] == seriesID:
				logging.debug('Found the show ' + allseries[x]['seriesname'] + ' matching with the ID ' + seriesID)
				return allseries[x]['seriesname']
		return ''


	def getTVDBInfo(self, showname, epAirdate, epTitle, epNumber) :
		logging.debug('searching for [' + showname + '] [' + epAirdate + ']')
		seriesname = showname
		epCandidates = self.lookup_episode_bydate(showname, epAirdate)
		numCandidates = len(epCandidates)
		logging.debug('Found ' + str(numCandidates) + ' Candidates shows to check...')
		if numCandidates >= 1:
			for ep in epCandidates:
				if (epTitle and (epTitle == ep['episodename'])):
					logging.info(ep['seasonnumber'] + '|' + ep['episodenumber'] + '|' + ep['episodename'] + ' is best match')
					seriesname = self.getTVDBSeriesName(showname, ep['seriesid']);
					return {'seriesname':seriesname, 'season_num':str(ep['seasonnumber']).zfill(2), 'episode_num':str(ep['episodenumber']).zfill(2)}
				else:
					continue
			logging.debug('No best Match - settling for first match')
			return {'seriesname':self.getTVDBSeriesName(showname,epCandidates[0]['seriesid']), 'season_num':epCandidates[0]['seasonnumber'], 'episode_num':epCandidates[0]['episodenumber']}
		# if nothing matched need to just return some dummy data
		logging.debug('No candidates found - setting it to blanks')
		return {'seriesname':'', 'season_num':'', 'episode_num':''}
			