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
            
    def get_episode_string(self, showname,epNumber,epAirdate,epTitle):
        episode_str = '00'
        if epNumber[3] == 'E':
            episode_str = epNumber[3:6]
        else:
            # going to have to search for it
            tvdb = tvdb_api.Tvdb()
            show = tvdb[showname]
            for series in show:
                seriesdata = tvdb[showname][series]
                for ep in seriesdata:
                    epData = seriesdata[ep]
                    ep_date = datetime.datetime.strptime(epData['firstaired'],'%Y-%m-%d')
                    check_date = datetime.datetime.utcfromtimestamp(int(epAirdate))
                    if ep_date == check_date:
                        logging.debug('MATCHED Season [' + str(series) + '] Episode [' + str(ep) + ']')
                        episode_str = 'E' + str(ep)
                        return episode_str
        return episode_str
        
    def get_season_string(self, showname,epNumber,epAirdate,epTitle):
        season_str = '00'
        if epNumber[0] == 'S':
            season_str = epNumber[1:3]
        else:
            # going to have to search for it
            tvdb = tvdb_api.Tvdb()
            show = tvdb[showname]
            for season in show:
                seasondata = tvdb[showname][season]
                for ep in seasondata:
                    epData = seasondata[ep]
                    ep_date = datetime.datetime.strptime(epData['firstaired'],'%Y-%m-%d')
                    check_date = datetime.datetime.utcfromtimestamp(int(epAirdate))
                    if ep_date == check_date:
                        logging.debug('MATCHED Season [' + str(season) + '] Episode [' + str(ep) + ']')
                        season_str = str(season).zfill(2)
                        return season_str
        return season_str
