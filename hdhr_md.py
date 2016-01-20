#-------------------------------------------------------------------------------
# HDHomerun MetaData Parser
#-------------------------------------------------------------------------------
import os
import logging
import time
from time import strftime
import datetime
import tvdb_api


class HDHomeRunMD:
    def __init__(self, metadata):
        self.metaData = metadata

    def print_metaData(self):
        for md in self.metaData:
            logging.debug(md[0].replace('\"',"") + '|' + md[1].replace('\"',""))
    
    def extract_show(self):
        for md in self.metaData:
            if md[0] == '"DisplayGroupTitle"' :
                return md[1].replace('"',"")

    def extract_subshow(self):
        for md in self.metaData:
            if md[0] == '"DisplayGroupTitle"' :
                return md[1].replace('"',"")
            
    def extract_epNumber(self):
        for md in self.metaData:
            if md[0] == '"EpisodeNumber"' :
                return md[1].replace('"',"")
    
    def extract_epTitle(self):
        for md in self.metaData:
            if md[0] == '"EpisodeTitle"' :
                return md[1].replace('"',"")
    
    def extract_epAirDate(self):
        for md in self.metaData:
            if md[0] == '"OriginalAirdate"' :
                return md[1].replace('"',"")
     
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
            logging.debug('Checking Series ' + seriesname + ' for matching episode')
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
        epData = {}
        seriesname = showname
        epCandidates = self.lookup_episode_bydate(showname, epAirdate)
        numCandidates = len(epCandidates)
        logging.debug('Found ' + str(numCandidates) + ' Candidates shows to check...')
        if epCandidates >= 1:
           for ep in epCandidates:
               logging.debug(ep['seriesid'] + '|' + ep['seasonnumber'] + '|' + ep['episodenumber'] + '|' + ep['episodename'] + ' checking')
               if epTitle == ep['episodename']:
                   logging.info(ep['seasonnumber'] + '|' + ep['episodenumber'] + '|' + ep['episodename'] + ' is best match')
                   epData.update(ep)
                   seriesname = self.getTVDBSeriesName(showname, ep['seriesid']);
           return {'seriesname':seriesname, 'season_num':str(ep['seasonnumber']).zfill(2), 'episode_num':str(ep['episodenumber']).zfill(2)}
        # if nothing matched need to just return some dummy data
        return {'seriesname':seriesname, 'season_num':'00', 'episode_num':epNumber}
        
        	
