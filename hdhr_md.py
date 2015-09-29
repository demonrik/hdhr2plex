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

    def lookup_episode_bydate(self, getEp, showname, epAirdate):
        logging.info('Finding Episode/Season details by showname and airdate')
        logging.debug('Connecting to theTVdb.com')
        tvdb = tvdb_api.Tvdb()
        logging.debug('Finding the shows with the name ' + showname)

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
                        logging.debug('Skipping...')
                    else:
                        ep_date = datetime.datetime.strptime(epData['firstaired'],'%Y-%m-%d')
                        check_date = datetime.datetime.utcfromtimestamp(int(epAirdate))
                        if ep_date == check_date:
                            logging.debug('MATCHED Season [' + str(season) + '] Episode [' + str(ep) + ']')
                            logging.debug('show: ' + seriesname + ' season: ' + epData['seasonnumber'] + ' episode: ' + epData['episodenumber'])
                            logging.debug(epData.keys())
#                            if getEp == True:
#                                episode_str = str(ep)
#                                return episode_str
#                            else:
#                                season_str = str(season).zfill(2)
#                                return season_str
                            return {'seriesname':seriesname, 'season_num':str(season).zfill(2), 'episode_num':str(epData['episodenumber']).zfill(2)}
                        else:
                            logging.debug('No match in ' + epData['episodenumber'] + ' for airdate ' + epAirdate)
        # fail safe - return noting and cause an error...
        return
            
    def get_episode_string(self, showname,epNumber,epAirdate,epTitle):
        episode_str = '00'
        if epNumber and epNumber[3] == 'E':
            episode_str = epNumber[4:6]
        else:
            episode_data = self.lookup_episode_bydate(True, showname, epAirdate)
            episode_str = episode_data['episode_num']
        return episode_str
        
    def get_season_string(self, showname,epNumber,epAirdate,epTitle):
        season_str = '00'
        if epNumber and epNumber[0] == 'S':
            season_str = epNumber[1:3]
        else:
            episode_data = self.lookup_episode_bydate(False, showname, epAirdate)
            season_str = episode_data['season_num']
        return season_str
