#-------------------------------------------------------------------------------
# This is an automated python script to parse out the metadata from MPEG-TS
# files created by the HDHomeRun DVR record engine.
#-------------------------------------------------------------------------------
import getpass
import os
import platform
import logging
import sys
import time
from time import strftime
import hdhr_tsparser
import plextools
import hdhr_md
import scripttools

AUTO_DELETE = False
HDHR_TS_METADATA_PID = 0x1FFA

def get_files_in_dir(path):
    return [os.path.join(path,f) for f in os.listdir(path) \
           if (not os.path.islink(os.path.join(path,f))) & os.path.isfile(os.path.join(path,f)) \
              & f.endswith('.mpg')]

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

def extract_metadata(metadata):
    md = hdhr_md.HDHomeRunMD(metadata)
    md.print_metaData()

    show = md.extract_show()
    epNumber = md.extract_epNumber()
    epAirDate = md.extract_epAirDate()
    epTitle = md.extract_epTitle()
    season = md.get_season_string(show,epNumber,epAirDate,epTitle)
    episode = md.get_episode_string(show,epNumber,epAirDate,epTitle)

    logging.info('=== Extracted: show [' + show + '] Season [' + season + '] Episode: [' + episode +']')
    return {'show':show, 'season':season, 'epnum':episode, 'eptitle':epTitle}

def update_plex(dvrpath, plexpath, show, season, epnum, eptitle, filename):
    plex = plextools.PlexTools(plexpath)
    if plex.check_file_exists_in_plex(plexpath,show,season,os.path.basename(f)):
        logging.info( f + ' already exists in plex folder')
        # TODO: make sure a link exists, if not - add to duplicates list
    else:
        plex.add_season_to_plex(plexpath,show,('Season '+ season))
        plex.move_episode_to_plex(plexpath,show,season,epnum,eptitle,f)
        plex.link_episode_to_dvr(dvrpath,plexpath,show,season,epnum,eptitle,f)

if __name__ == "__main__":
    
    tools = scripttools.ScriptTools()
    if tools.isInteractive():
        print 'Interactive mode not supported at this time... exiting...'
        sys.exit(0)

    logging.info('------------------------------------------------------------')
    logging.info('-                  HDHR TS MetaData Tool                   -')
    logging.info('-                   '+strftime("%Y-%m-%d %H:%M:%S")+'                    -')
    logging.info('------------------------------------------------------------')
    files = get_files_in_dir(tools.get_dvr_path())
    
    for f in files:
        metaData = []
        logging.info('-----------------------------------------------')
        logging.info('Parsing: ' + f)
        metaData = parse_file_for_data(f)
        md = extract_metadata(metaData)
        if md['eptitle']:
            update_plex(tools.get_dvr_path(),tools.get_plex_path(),md['show'],md['season'],md['epnum'],md['eptitle'],f)
        else:
            update_plex(tools.get_dvr_path(),tools.get_plex_path(),md['show'],md['season'],md['epnum'],'',f)
        logging.info('Completed for : ' + f)

    logging.info('------------------------------------------------------------')
    logging.info('-              HDHR TS MetaData Tool Complete              -')
    logging.info('-                   '+strftime("%Y-%m-%d %H:%M:%S")+'                    -')
    logging.info('------------------------------------------------------------')

