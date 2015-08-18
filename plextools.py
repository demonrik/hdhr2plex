#-------------------------------------------------------------------------------
# MPEG-TS Parser
#-------------------------------------------------------------------------------
import os
import logging
import shutil
import platform

class PlexTools:
    def __init__(self, plexpath):
        self.plexpath = plexpath

    def get_season_combinations(self, season):
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
    
    def check_show_in_plex(self, plexpath, show):
        #check for the show
        if not os.path.exists(os.path.join(plexpath,show)):
            logging.info('Show ' + show +  ' does not exist in path ' + plexpath)
            return False
        return True
    
    def check_episode_in_plex(self, plexpath, show, season, filename):
        if not os.path.exists(os.path.join(plexpath,show,season,filename)):
            logging.info('Episode ' + filename + ' for Season ' + season +  ' does not exist in show ' + show + ' for path ' + plexpath)
            return False
        return True
    
    def check_season_in_plex(self, plexpath, show, season):
        #Season can take form , Season XX, SeasonXX, SeasonX
        seasons = self.get_season_combinations(season)
        valid_season = ''
        season_check = False
        for s in seasons:
            if os.path.exists(os.path.join(plexpath,show,s)):
                season_check |= True
                valid_season = s
    
        if not season_check:
            logging.info('Season ' + season +  ' does not exist in show ' + show + ' for path ' + plexpath)
            return ''
        return valid_season
    
    def check_file_exists_in_plex(self, plexpath, show, season, filename):
        #Check plexpath exists
        if not os.path.exists(plexpath):
            logging.info('Plex Path ' + plexpath + ' does not exist.')
            return False
        if not self.check_show_in_plex(plexpath, show):
            return False
        season_str = self.check_season_in_plex(plexpath, show, season)
        if season_str == '':
            return False
        if not self.check_episode_in_plex(plexpath, show, season_str, filename):
            return False
    
    def add_season_to_plex(self, plexpath, show, season):
        #Check plexpath exists
        if not os.path.exists(plexpath):
            logging.info('Plex Path ' + plexpath + ' does not exist.')
            return False
    
        #now check for the show and add if not existing
        if not os.path.exists(os.path.join(plexpath,show)):
            logging.info('Adding Show ' + show +  ' to ' + plexpath)
            os.makedirs(os.path.join(plexpath,show))
        
        #finally check if the Season Path exists
        if not os.path.exists(os.path.join(plexpath, show, season)):
            logging.info('Adding ' + season +  ' to ' + show + ' in ' + plexpath)
            os.makedirs(os.path.join(plexpath,show, season))
    
    def fix_filename(self, show, season, epnum, eptitle):
        return show + ' - S' + season + epnum + ' - ' + eptitle + '.mpg'
    
    def move_episode_to_plex(self, plexpath,show,season,epnum,eptitle,filename):
        if not os.path.exists(os.path.join(plexpath, show, 'Season ' + season)):
            logging.debug('Can\'t move episode - [' + os.path.join(plexpath, show, 'Season ' + season) + '] doesn\'t exist')
            return False
        # does link already exists
        # renaming output filename
        outfile =  self.fix_filename(show, season, epnum, eptitle)
        logging.info('Renaming moved file to: ' + outfile)
        # TODO: does file already exist?
        # move file
        logging.info('Moving [' + filename + '] to [' + os.path.join(plexpath, show, 'Season ' + season, outfile))
        if platform.system() == 'Windows':
            logging.warn('Moving is not supported at this time on Windows')
        else:
            logging.info('Doing the Move')
            shutil.move(filename,os.path.join(plexpath, show, 'Season ' + season, outfile))

        # TODO: rename file to include SxxExx if not already existing
        # return final file location
        
    def link_episode_to_dvr(self, dvrpath, plexpath,show,season,epnum,eptitle,filename):
        if not os.path.exists(os.path.join(plexpath, show, 'Season ' + season)):
            logging.debug('Can\'t Link episode - [' + os.path.join(plexpath, show, 'Season ' + season) + '] doesn\'t exist')
            return False
        # does link already exist
        # create relative link if possible
        common_path = os.path.commonprefix([dvrpath, plexpath])
        rel_plex_path = os.path.relpath(plexpath,dvrpath)
        logging.info('Identified common path in files: '+common_path)
        logging.info('Updating Plex Path to: '+rel_plex_path)
        # link file back to DVR folder
        logging.info('Linking [' + os.path.join(rel_plex_path, show, 'Season ' + season, self.fix_filename(show, season, epnum, eptitle)) + '] to [' + filename )
        if platform.system() == 'Windows':
            logging.warn('Linking is not supported at this time on Windows')
        else:
            logging.info('Doing the link')
            os.symlink(os.path.join(rel_plex_path, show, 'Season ' + season, self.fix_filename(show, season, epnum, eptitle)),filename)


