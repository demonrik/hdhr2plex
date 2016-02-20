#-------------------------------------------------------------------------------
# Script Tools - Argument and Config File Parser
#-------------------------------------------------------------------------------
import os
import ConfigParser
import argparse
import platform
import logging

LOGLEVELS = {'debug': logging.DEBUG,
          'info': logging.INFO,
          'warning': logging.WARNING,
          'error': logging.ERROR,
          'critical': logging.CRITICAL}

hdhr_args_list = ['--config','--interactive','--logfile','--loglevel']

hdhr_cfg_main = 'HDHR-DVR'
hdhr_cfg_path_dvr = 'dvrpath'
hdhr_cfg_path_plex = 'plexpath'
hdhr_cfg_loglevel = 'loglevel'
hdhr_cfg_logfile = 'logfile'
hdhr_cfg_renameDir = 'renamedir'
hdhr_cfg_renameFile = 'renamefile'
hdhr_cfg_link2plex = 'link2plex'
hdhr_cfg_link2dvr = 'link2dvr'
hdhr_cfg_metasave = 'metasave'
hdhr_cfg_forceUpdate = 'forceupdate'
hdhr_cfg_skip_shows = 'skipshows'
hdhr_cfg_liveDelay = 'livedelay'
hdhr_cfg_days2archive = 'days2archive'
hdhr_cfg_days2delete = 'days2delete'



class ScriptTools:

    def __init__(self):
        self.interactive = False
        self.dvr_path = ''
        self.plex_path = ''
        self.renameDir = False
        self.renameFile = False
        self.force = False
        self.link2plex = False
        self.link2dvr = False
        self.savemd = False
        self.livedelay = 0
        self.days2delete = 0
        self.days2archive = 14

        arg_parser = argparse.ArgumentParser(description='Process command line args')
        for n in hdhr_args_list:
            arg_parser.add_argument(n)
        self.args = arg_parser.parse_args()
    
        if self.args.config:
            if os.path.exists(self.args.config): 
                self.parse_config_file(None)
            else:
                print "Config file specified not found - " + self.args.config
                self.interactive = True
        else:
            if os.path.exists('my.conf'):
                self.parse_config_file('my.conf')
            else:
                print "No config file found - reverting to interactive"
                self.interactive = True
    
        # user can always override the settings.            
        if self.args.interactive:
            self.interactive = True

    def parse_config_file(self,config_file):
        global logging
        global dvr_path
        global plex_path
        
        config = ConfigParser.ConfigParser()
        if self.args.config: 
            config.read(self.args.config)
        else:
            config.read(config_file)
        
        sections = {}
    
        # Parse out the config info from the config file
        for section_name in config.sections():
            sections[section_name] = {}
            for name, value in config.items(section_name):
                sections[section_name][name] = value
    
        if not hdhr_cfg_main in sections.keys():
            print 'have in valid config file - stopping'
            return

        for key in sections[hdhr_cfg_main].keys():
            if key == hdhr_cfg_path_dvr:
                self.dvr_path = sections[hdhr_cfg_main][hdhr_cfg_path_dvr]
                #ensure we have trailing path seperator
                if not self.dvr_path.endswith(os.sep):
                    self.dvr_path+=os.sep
                print 'Processing DVR files from: ', self.dvr_path
            
            if key == hdhr_cfg_path_plex:
                self.plex_path = sections[hdhr_cfg_main][hdhr_cfg_path_plex]
                #ensure we have trailing path seperator
                if not self.plex_path.endswith(os.sep):
                    self.plex_path+=os.sep
                print 'Processing Plex files from: ', self.plex_path

            if key == hdhr_cfg_link2plex:
                if sections[hdhr_cfg_main][hdhr_cfg_link2plex] == 'True':
                    self.link2plex = True
                print 'Link DVR file to Plex: ', self.link2plex

            if key == hdhr_cfg_link2dvr:
                if sections[hdhr_cfg_main][hdhr_cfg_link2dvr] == 'True':
                    self.link2dvr = True
                print 'Link Plex file to DVR (Assumes move to Plex): ', self.link2dvr

            if key == hdhr_cfg_metasave:
                if sections[hdhr_cfg_main][hdhr_cfg_metasave] == 'True':
                    self.savemd = True
                print 'Extract and Save MetaData (Assumes move to Plex): ', self.savemd

            if key == hdhr_cfg_renameDir:
                if sections[hdhr_cfg_main][hdhr_cfg_renameDir] == 'True':
                    self.renameDir = True
                print 'Rename Directory to match TVDB show name: ', self.renameDir

            if key == hdhr_cfg_renameFile:
                if sections[hdhr_cfg_main][hdhr_cfg_renameFile] == 'True':
                    self.renameFile = True
                print 'Rename Files Enabled: ', self.renameFile

            if key == hdhr_cfg_forceUpdate:
                if sections[hdhr_cfg_main][hdhr_cfg_forceUpdate] == 'True':
                    self.force = True
                print 'Force Updates Enabled: ', self.force

            if key == hdhr_cfg_skip_shows:
                self.skip_list = sections[hdhr_cfg_main][hdhr_cfg_skip_shows]
                print 'Setting up Skip Shows: ', self.skip_list

            if key == hdhr_cfg_liveDelay:
                self.livedelay = sections[hdhr_cfg_main][hdhr_cfg_liveDelay]
                print 'Live Delay: ', self.livedelay

            if key == hdhr_cfg_days2archive:
                self.days2archive = sections[hdhr_cfg_main][hdhr_cfg_days2archive]
                print 'Days Until Archive: ', self.days2archive

            if key == hdhr_cfg_days2delete:
                self.days2delete = sections[hdhr_cfg_main][hdhr_cfg_days2delete]
                print 'Days Until Delete: ', self.days2delete

        # Extract Logging Information
        loglevel = 'warning'
        if self.args.loglevel:
            loglevel = self.args.loglevel
        else:
            if sections[hdhr_cfg_main][hdhr_cfg_loglevel]:
                loglevel = sections[hdhr_cfg_main][hdhr_cfg_loglevel]

        print 'Log Level is set to: ', loglevel

        if self.args.logfile:
            logfile = self.args.logfile
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

    def get_skip_shows(self):
        return self.skip_list
    
    def get_dvr_path(self):
        return self.dvr_path

    def get_plex_path(self):
        return self.plex_path

    def isInteractive(self):
        return self.interactive
        
    def fileRename(self):
        return self.renameFile

    def dirRename(self):
        return self.renameDir

    def forceEnabled(self):
        return self.force
        
    def move2plex(self):
        return (self.link2dvr or self.savemd)

    def saveMeta(self):
        return self.savemd
    
    def getLiveDelay(self):
    	return self.livedelay
    
    def getDays2Archive(self):
    	return self.days2archive
    	
    def getDays2Delete(self):
    	return self.days2delete