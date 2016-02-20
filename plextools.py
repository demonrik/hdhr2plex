#-------------------------------------------------------------------------------
# MPEG-TS Parser
#-------------------------------------------------------------------------------
import os
import logging
import re
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
	
	def check_show_in_plex(self, show):
		#check for the show
		if not os.path.exists(os.path.join(self.plexpath,show)):
			logging.info('Show ' + show +  ' does not exist in path ' + self.plexpath)
			return False
		return True
	
	def check_season_in_plex(self, show, season):
		#Season can take form , Season XX, SeasonXX, SeasonX
		seasons = self.get_season_combinations(season)
		valid_season = ''
		season_check = False
		for s in seasons:
			if os.path.exists(os.path.join(self.plexpath,show,s)):
				season_check |= True
				valid_season = s
	
		if not season_check:
			logging.info('Season ' + season +  ' does not exist in show ' + show + ' for path ' + self.plexpath)
			return ''
		return valid_season
	
	def add_season_to_plex(self, show, season):
		#Check plexpath exists
		if not os.path.exists(self.plexpath):
			logging.info('Plex Path ' + self.plexpath + ' does not exist.')
			return False
	
		#now check for the show and add if not existing
		if not os.path.exists(os.path.join(self.plexpath,show)):
			logging.info('Adding Show ' + show +  ' to ' + self.plexpath)
			os.makedirs(os.path.join(self.plexpath,show))
		
		#finally check if the Season Path exists
		if not os.path.exists(os.path.join(self.plexpath, show, 'Season ' + season)):
			logging.info('Adding Season ' + season +  ' to ' + show + ' in ' + self.plexpath)
			os.makedirs(os.path.join(self.plexpath,show, 'Season ' + season))
	
	def move_episode_to_plex(self, show, season, plexfile, oldfile):
		# Check plexpath exists
		if not os.path.exists(self.plexpath):
			logging.error('Plex Path ' + self.plexpath + ' does not exist.')
			return False
		# Check the show exists
		if not self.check_show_in_plex(show):
			logging.debug('Plex does not contain show [' + show + ']  - Can\'t move file')
			return False
		# Check the Season exists in the show
		season_str = self.check_season_in_plex(show, season)
		if season_str == '':
			logging.debug('Plex does not contain season [' + season + '] for show [' + show + '] so can\t move file')
			return False
		
		logging.info('Moving [' + oldfile + '] to [' + os.path.join(self.plexpath, show, season_str, plexfile))
		shutil.move(oldfile,os.path.join(self.plexpath, show, season_str, plexfile))
		return True
		
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

	def construct_filename(self, show, season, episodenum, eptitle, extension):
		#check season for 'Season'
		season_str = re.match('Season\s', season)
		if season_str == '':
			logging.debug('no season string found')
		filename = show + '-' + episodenum + '-' + eptitle + extension
		return filename

	def get_episodes_in_season(self, show, season):
		path = os.path.join(self.plexpath, show, season)
		return [os.path.join(path,f) for f in os.listdir(path) \
			if (not os.path.islink(os.path.join(path,f))) & os.path.isfile(os.path.join(path,f))]

	def find_filename(self, show, season, episodenum):
		logging.debug('Checking for existing filename in Plex matching [' + show + '][' + season + '][' + episodenum + ']')
		filename = ''
		# Check plexpath exists
		if not os.path.exists(self.plexpath):
			logging.error('Plex Path ' + self.plexpath + ' does not exist.')
			return filename
		# Check the show exists
		if not self.check_show_in_plex(show):
			logging.debug('Plex does not contain show [' + show + '] so no file to find')
			return filename
		# Check the Season exists in the show
		season_str = self.check_season_in_plex(show, season)
		if season_str == '':
			logging.debug('Plex does not contain season [' + season + '] for show [' + show + '] so no file to find')
			return filename
		
		# Is there any file matching the episodenumber
		files = self.get_episodes_in_season(show, season_str)
		logging.debug('Checking ' + str(len(files)))
		for f in files:
			logging.debug('Checking ' + f + ' for SxxExx match to ' + episodenum)
			epnum = re.findall('S\d{2}E\d{2}', f)
			if (len(epnum) > 0) and (epnum[0] == episodenum):
				logging.debug('Found filename for episode ' + episodenum)
				filename = f
		
		return filename
		
		
		
		