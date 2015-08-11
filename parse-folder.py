#-------------------------------------------------------------------------------
# This is an automated python script to parse out the metadata from MPEG-TS
# files created by the HDHomeRun DVR record engine.
#-------------------------------------------------------------------------------
import getpass
import os
import ConfigParser
import argparse
import platform
import logging
import sys
import unicodedata
import time
from time import strftime
import datetime
import hdhr_tsparser
import tvdb_api

AUTO_DELETE = False
HDHR_TS_METADATA_PID = 0x1FFA

LOGLEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

hdhr_args_list = ['--config','--autodelete','--interactive','--logfile','--loglevel']

hdhr_cfg_main = 'HDHR-DVR'
hdhr_cfg_path_dvr = 'dvrpath'
hdhr_cfg_path_plex = 'plexpath'
hdhr_cfg_skip_shows = 'skipshows'
hdhr_cfg_loglevel = 'loglevel'
hdhr_cfg_logfile = 'logfile'
hdhr_cfg_autodelete = 'autodelete'

def print_metaData(metaData):
    for md in metaData:
        print md[0].replace('"',""), '|', md[1].replace('"',"")

def get_files_in_dir(path):
    return [os.path.join(path,f) for f in os.listdir(path) if os.path.isfile(os.path.join(path,f)) & f.endswith('.mpg')]

def parse_file_for_data(filename):
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

def get_season_combinations(season):
    leading_zero = True
    season_title = 'Season'
    season_str = []
    season_num = int(season)

    season_str.append(season_title + str(season_num).zfill(2))
    season_str.append(season_title + ' ' + str(season_num).zfill(2))
    if (season_num < 10):
        season_str.append(season_title + str(season_num).zfill(1))
        season_str.append(season_title + ' ' + str(season_num).zfill(1))
    
    logging.debug('Creating season combination strings for season: ' + str(season_str))
    return season_str

def check_show_in_plex(plexpath, show, season, filename):
    #Check plexpath exists
    if not os.path.exists(plexpath):
        logging.info('Plex Path ' + plexpath + ' does not exist.')
        return False
    #now check for the show
    if not os.path.exists(os.path.join(plexpath,show)):
        logging.info('Show ' + show +  ' does not exist in path ' + plexpath)
        return False

    #what about this season
    #Season can take form , Season XX, SeasonXX, SeasonX
    seasons = get_season_combinations(season)
    season_check = False
    for s in seasons:
        if os.path.exists(os.path.join(plexpath,show,s)):
            season_check |= True

    if not season_check:
        logging.info('Season ' + s +  ' does not exist in show ' + show + ' for path ' + plexpath)
        return False

    #and finally does the episode exist
    if not os.path.exists(os.path.join(plexpath,show,season,filename)):
        logging.info('Episode ' + filename + ' for Season ' + season +  ' does not exist in show ' + show + ' for path ' + plexpath)
        return False
    return True

def extract_show(metaData):
    for md in metaData:
        if md[0] == '"DisplayGroupTitle"' :
            return md[1].replace('"',"")

def extract_epNumber(metaData):
    for md in metaData:
        if md[0] == '"EpisodeNumber"' :
            return md[1].replace('"',"")

def extract_epTitle(metaData):
    for md in metaData:
        if md[0] == '"EpisodeTitle"' :
            return md[1].replace('"',"")

def extract_epAirDate(metaData):
    for md in metaData:
        if md[0] == '"OriginalAirdate"' :
            return md[1].replace('"',"")

def get_episode_string(showname,epNumber,epAirdate,epTitle):
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
                epData = tvdb[showname][series][ep]
                ep_date = datetime.datetime.strptime(epData['firstaired'],'%Y-%m-%d')
                check_date = datetime.datetime.utcfromtimestamp(int(epAirdate))
                if ep_date == check_date:
                    logging.debug('MATCHED Season [' + str(series) + '] Episode [' + str(ep) + ']')
                    episode_str = 'E' + str(ep)
                    return episode_str
    return episode_str


def get_season_string(showname,epNumber,epAirdate,epTitle):
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
                epData = tvdb[showname][season][ep]
                ep_date = datetime.datetime.strptime(epData['firstaired'],'%Y-%m-%d')
                check_date = datetime.datetime.utcfromtimestamp(int(epAirdate))
                if ep_date == check_date:
                    logging.debug('MATCHED Season [' + str(season) + '] Episode [' + str(ep) + ']')
                    season_str = str(season)
                    return season_str
    return season_str

def parse_config_file(args,config_file):
    global logging
    global dvr_path
    global plex_path
    global skip_list
    
    config = ConfigParser.ConfigParser()
    if args.config: 
        config.read(args.config)
    else:
        config.read(config_file)
    
    sections = {}

    # Parse out the config info from the config file
    for section_name in config.sections():
        sections[section_name] = {}
        for name, value in config.items(section_name):
            sections[section_name][name] = value

    if hdhr_cfg_main in sections.keys():
        if sections[hdhr_cfg_main][hdhr_cfg_path_dvr]:
            dvr_path = sections[hdhr_cfg_main][hdhr_cfg_path_dvr]
        #ensure we have trailing path seperator
        if not dvr_path.endswith(os.sep):
            dvr_path+=os.sep
        print 'Processing DVR files from: ', dvr_path
        
        if sections[hdhr_cfg_main][hdhr_cfg_path_plex]:
            plex_path = sections[hdhr_cfg_main][hdhr_cfg_path_plex]
        #ensure we have trailing path seperator
        if not plex_path.endswith(os.sep):
            plex_path+=os.sep
        print 'Processing Plex files from: ', plex_path
        
        # Extract Logging Information
        loglevel = 'warning'
        if args.loglevel:
            loglevel = args.loglevel
        else:
            if sections[hdhr_cfg_main][hdhr_cfg_loglevel]:
                loglevel = sections[hdhr_cfg_main][hdhr_cfg_loglevel]

        print 'Log Level is set to: ', loglevel

        if args.logfile:
            logfile = args.logfile
            logging.basicConfig(filename=logfile,
                                level=LOGLEVELS.get(loglevel, logging.WARNING))
        else:
            if sections[hdhr_cfg_main][hdhr_cfg_logfile]:
                logfile = sections[hdhr_cfg_main][hdhr_cfg_logfile]
                logging.basicConfig(filename=logfile,
                                    level=LOGLEVELS.get(loglevel, logging.WARNING))
            else:
                # Need to setup stdout error handler
                logging.basicConfig(stream=sys.stdout,
                                    level=LOGLEVELS.get(loglevel, logging.WARNING))
        print 'Logging to: ', logfile

if __name__ == "__main__":
    interactive = False;
    arg_parser = argparse.ArgumentParser(description='Process command line args')
    for n in hdhr_args_list:
        arg_parser.add_argument(n)
  
    args = arg_parser.parse_args()
    if args.config:
        if os.path.exists(args.config): 
            parse_config_file(args,None)
        else:
            print "Config file specified not found - " + args.config
            interactive = True
    else:
        if os.path.exists('my.conf'):
            parse_config_file(args,'my.conf')
        else:
            print "No config file found - reverting to interactive"
            interactive = True

    # user can always override the settings.            
    if args.interactive:
        interactive = True

    if interactive:
        print 'Interactive mode not supported at this time... exiting...'
        sys.exit(0)

    logging.info('------------------------------------------------------------')
    logging.info('-                  HDHR TS MetaData Tool                   -')
    logging.info('-                   '+strftime("%Y-%m-%d %H:%M:%S")+'                    -')
    logging.info('------------------------------------------------------------')
    
    files = get_files_in_dir(dvr_path)
    for f in files:
        metaData = []
        logging.info('-----------------------------------------------')
        logging.info('Parsing: ' + f)
        logging.info('-----------------------------------------------')
        metaData = parse_file_for_data(f)
        show = extract_show(metaData)
        epNumber = extract_epNumber(metaData)
        epTitle = extract_epTitle(metaData)
        epAirDate = extract_epAirDate(metaData)
        season = get_season_string(show,epNumber,epAirDate,epTitle)
        episode = get_episode_string(show,epNumber,epAirDate,epTitle)
        logging.info('=== Extracted: ')
        logging.info('= show: ' + show)
        logging.info('= Guide episode: ' + epNumber)
        logging.info('= airdate: ' + epAirDate)
        if epTitle: 
            logging.info('= title: ' + epTitle)
        logging.info('= Season: ' + season)
        logging.info('= Episode: ' + episode)
        logging.info(' ===')
        if check_show_in_plex(plex_path,show,season,os.path.basename(f)):
            logging.info( f + ' already exists in plex folder')
        
        

