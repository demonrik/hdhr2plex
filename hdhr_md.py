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
                            logging.debug('MATCHED Season [' + str(season) + '] Episode [' + str(ep) + ']')
                            episodeNum = epData['episodenumber']
                            return {'seriesname':seriesname, 'season_num':str(season).zfill(2), 'episode_num':str(episodeNum).zfill(2)}
                        else:
                            logging.debug('No match in ' + epData['episodenumber'] + ' for airdate ' + epAirdate)
        # fail safe - return what we have - even if not complete
        return {'seriesname':seriesname, 'season_num':str(season).zfill(2), 'episode_num':str(episodeNum).zfill(2)}

    def getTVDBInfo(self, showname, epAirdate) :
        logging.debug('searching for [' + showname + '] [' + epAirdate + ']')
        epData = self.lookup_episode_bydate(showname, epAirdate)
        return {'seriesname':epData['seriesname'], 'season_num':epData['season_num'], 'episode_num':epData['episode_num']}
        	
    def resolve_season_string(self, epNumber, tvdbSeasonNum, tvdbEpisodeNum):
        season_str = '00'
        if epNumber and epNumber[0] == 'S':
            season_str = epNumber[1:3]
        else:
            season_str = tvdbSeasonNum
        return season_str

    def resolve_season_string(self, epNumber, tvdbSeasonNum, tvdbEpisodeNum):
        episode_str = '00'
        if epNumber and epNumber[3] == 'E':
            episode_str = epNumber[4:6]
        else:
            episode_str = tvdbEpisodeNum
        return episode_str
