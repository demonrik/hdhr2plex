#-------------------------------------------------------------------------------
# This is an automated python script to parse out the metadata from MPEG-TS
# files created by the HDHomeRun DVR record engine.
#-------------------------------------------------------------------------------
import getpass
import os
import platform
import logging
import sys
import re
import time
from time import strftime
import hdhr_tsparser
import plextools
import hdhr_md
import scripttools

HDHR_TS_METADATA_PID = 0x1FFA
shows2skip = {}

# QNAP NAS adds thumbnails with it's media scanner - so will skip that dir
# TODO: Make skip dirs configurable
def get_shows_in_dir(path):
    return [os.path.join(path,f) for f in os.listdir(path) \
           if (not ".@__thumb" in f) & os.path.isdir(os.path.join(path,f))]

def get_episodes_in_show(path):
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

def isSpecialShow(showname):
	  
    if not shows2skip:
        return False
    for show in shows2skip:
        if showname.lower() == show.replace('"','').lower():
            logging.debug('Skip show found ' + showname)
            return True
    return False

def extract_metadata(metadata):
    md = hdhr_md.HDHomeRunMD(metadata)
    md.print_metaData()

    show = md.extract_show()
    epNumber = md.extract_epNumber()
    epAirDate = md.extract_epAirDate()
    epTitle = md.extract_epTitle()
    
    # Need to workaround some bad titles that US TV and thetvdb.com are in conflict for.
    if not isSpecialShow(show):
        tvdbEpData = md.getTVDBInfo(show,epAirDate,epTitle,epNumber)
        season = tvdbEpData['season_num']
        episode = tvdbEpData['episode_num']
        logging.info('=== Extracted: show [' + show + '] Season [' + season + '] Episode: [' + episode +']')
        return {'show':show, 'season':season, 'epnum':episode, 'eptitle':epTitle, 'tvdbname':tvdbEpData['seriesname'], 'special':False}
    else:
        logging.debug('*** Show [' + show + '] marked for special handling - and will not use theTvDb.com')
        return {'show':show, 'season':'-', 'epnum':epNumber, 'eptitle':epTitle, 'tvdbname':show, 'special':True}

def fix_title(epTitle):
    newTitle = str.replace(epTitle,'/','_')
    return newTitle

def fix_filename(show, season, episode, epTitle, special):
    basename = show + '-' + episode
    if not special:
        basename = show + '-S' + season + 'E' + episode

    newTitle = fix_title(epTitle)
    if newTitle == '':
        return basename + '.mpg'
    else:
        return basename + '-' + newTitle + '.mpg'

def is_already_fixed(filename):
    # Checking file is form of <show>-S<season number>E<episode number>[- title]
    # where title is optional, but must have show, season and episode numbers
    
    regexPatSearch = re.compile(r'-S\d+E\d+-')
    if regexPatSearch.search(filename):
        logging.debug('Matched SxxExx in filename: ' + filename)
        return True
    
    return False

def rename_episode(filename, show, season, episode, epTitle, special, renameDir, force):
    if not epTitle:
        epTitle = ''
    base_name = os.path.basename(filename)

    # shouldn't need to recheck, but may as well..
    if (base_name == fix_filename(show, season, episode, epTitle,special)) & (not force):
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

        new_name = os.path.join(dir_name, fix_filename(show, season, episode, epTitle,special))
        logging.debug('replacing ' + filename + ' with ' + new_name)
        os.rename(filename,new_name)

def move_to_plex(filename, plexpath, showname, season, episode, eptitle, special, force):
    logging.info('Moving ' + f + ' to Plex at ' + plexpath)
    return
    
def link_dvr_to_plex():
    logging.info('linking DVR File to Plex')
    return

def link_plex_to_dvr():
    logging.info('linking Plex File to DVR')
    return
    
def save_min_metadata(f,metadata):
    logging.info('Resaving metadata as ' + f)
    return

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
    shows = get_shows_in_dir(tools.get_dvr_path())

    for show in shows:
        episodes = get_episodes_in_show(show)
        files.extend(episodes)

    shows2skip = tools.get_skip_shows().split(',')
    logging.debug('Skip Shows ' + str(shows2skip))
    
    for f in files:
        if is_already_fixed(f) & (not tools.forceEnabled()):
            logging.info('SKIPPING: Already fixed ' + f)
            continue
        metaData = []
        logging.info('-----------------------------------------------')
        logging.info('Parsing: ' + f)
        metaData = parse_file_for_data(f)
        md = extract_metadata(metaData)
        if tools.dirRename():
            logging.info('Setting showname to: ' + md['tvdbname'])
            showname = md['tvdbname']
        else:
            logging.info('Setting showname to: ' + md['show'])
            showname = md['show']
        
        if tools.get_plex_path() and tools.move2plex():
            move_to_plex(f,tools.get_plex_path(),showname,md['season'],md['epnum'],md['eptitle'],md['special'],tools.forceEnabled())
            if tools.link2dvr:
                link_plex_to_dvr()
            elif tools.saveMeta():
                save_min_metadata(f,md)
        else:
            logging.info('Renaming ' + f)
            rename_episode(f,showname,md['season'],md['epnum'],md['eptitle'],md['special'],tools.dirRename(), tools.forceEnabled())
        logging.info('Completed for : ' + f)

    logging.info('------------------------------------------------------------')
    logging.info('-              HDHR TS MetaData Tool Complete              -')
    logging.info('-                   '+strftime("%Y-%m-%d %H:%M:%S")+'                    -')
    logging.info('------------------------------------------------------------')

