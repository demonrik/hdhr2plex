#-------------------------------------------------------------------------------
# Simple Tool to dump the Recordings List from the HDHR DVR
#
#########
#
#-------------------------------------------------------------------------------
import os
import platform
import logging
import sys
import json
import urllib
import time
from time import strftime

DVR_IPADDR = '192.168.1.145'
DVR_PORT = '62090'

hdhr_recinfo_Category =  'Category'
hdhr_recinfo_ChannelAffiliate =  'ChannelAffiliate'
hdhr_recinfo_ChannelImageURL =  'ChannelImageURL'
hdhr_recinfo_ChannelName =  'ChannelName'
hdhr_recinfo_ChannelNumber =  'ChannelNumber'
hdhr_recinfo_EndTime =  'EndTime'
hdhr_recinfo_EpisodeNumber =  'EpisodeNumber'
hdhr_recinfo_EpisodeTitle =  'EpisodeTitle'
hdhr_recinfo_FirstAiring =  'FirstAiring'
hdhr_recinfo_ImageURL =  'ImageURL'
hdhr_recinfo_OriginalAirdate =  'OriginalAirdate'
hdhr_recinfo_ProgramID =  'ProgramID'
hdhr_recinfo_RecordEndTime =  'RecordEndTime'
hdhr_recinfo_RecordStartTime =  'RecordStartTime'
hdhr_recinfo_SeriesID =  'SeriesID'
hdhr_recinfo_StartTime =  'StartTime'
hdhr_recinfo_Synopsis =  'Synopsis'
hdhr_recinfo_Title =  'Title'
hdhr_recinfo_DisplayGroupID =  'DisplayGroupID'
hdhr_recinfo_PlayURL =  'PlayURL'
hdhr_recinfo_CmdURL =  'CmdURL'


class HDHomeRun:
	def __init__(self, hdhr_data):
		self.hdhr_base = hdhr_data['BaseURL']
		self.hdhr_storage = hdhr_data['StorageURL']
		self.hdhr_space = hdhr_data['FreeSpace']
		self.hdhr_name = hdhr_data['FriendlyName']
		self.hdhr_version = hdhr_data['Version']
	
	def getBaseURL(self):
		return self.hdhr_base
	
	def getStorageURL(self):
		return self.hdhr_storage
	
	def getSpace(self):
		return self.hdhr_space
	
	def getName(self):
		return self.hdhr_name
	
	def getVersion(self):
		return self.hdhr_version

class Recording:
	def __init__(self, data):
		self.recKeys = data.keys()
		for key in data.keys():
			if key == hdhr_recinfo_Category:
				self.Category = data[hdhr_recinfo_Category]
			if key == hdhr_recinfo_ChannelAffiliate:
				self.ChannelAffiliate = data[hdhr_recinfo_ChannelAffiliate]
			if key == hdhr_recinfo_ChannelImageURL:
				self.ChannelImageURL = data[hdhr_recinfo_ChannelImageURL]
			if key == hdhr_recinfo_ChannelName:
				self.ChannelName = data[hdhr_recinfo_ChannelName]
			if key == hdhr_recinfo_ChannelNumber:
				self.ChannelNumber = data[hdhr_recinfo_ChannelNumber]
			if key == hdhr_recinfo_EndTime:
				self.EndTime = data[hdhr_recinfo_EndTime]
			if key == hdhr_recinfo_EpisodeNumber:
				self.EpisodeNumber = data[hdhr_recinfo_EpisodeNumber]
			if key == hdhr_recinfo_EpisodeTitle:
				self.EpisodeTitle = data[hdhr_recinfo_EpisodeTitle]
			if key == hdhr_recinfo_FirstAiring:
				self.FirstAiring = data[hdhr_recinfo_FirstAiring]
			if key == hdhr_recinfo_ImageURL:
				self.ImageURL = data[hdhr_recinfo_ImageURL]
			if key == hdhr_recinfo_OriginalAirdate:
				self.OriginalAirdate = data[hdhr_recinfo_OriginalAirdate]
			if key == hdhr_recinfo_ProgramID:
				self.ProgramID = data[hdhr_recinfo_ProgramID]
			if key == hdhr_recinfo_RecordEndTime:
				self.RecordEndTime = data[hdhr_recinfo_RecordEndTime]
			if key == hdhr_recinfo_RecordStartTime:
				self.RecordStartTime = data[hdhr_recinfo_RecordStartTime]
			if key == hdhr_recinfo_SeriesID:
				self.SeriesID = data[hdhr_recinfo_SeriesID]
			if key == hdhr_recinfo_StartTime:
				self.StartTime = data[hdhr_recinfo_StartTime]
			if key == hdhr_recinfo_Synopsis:
				self.Synopsis = data[hdhr_recinfo_Synopsis]
			if key == hdhr_recinfo_Title:
				self.Title = data[hdhr_recinfo_Title]
			if key == hdhr_recinfo_DisplayGroupID:
				self.DisplayGroupID = data[hdhr_recinfo_DisplayGroupID]
			if key == hdhr_recinfo_PlayURL:
				self.PlayURL = data[hdhr_recinfo_PlayURL]
			if key == hdhr_recinfo_CmdURL:
				self.CmdURL = data[hdhr_recinfo_CmdURL]
	
	def getRecordingStr(self):
		try:
			return str(len(self.recKeys)) + ' keys | Title: ' + self.Title + ' Episode: ' + self.EpisodeNumber
		except AttributeError:
			return str(len(self.recKeys)) + ' keys | Title: ' + self.Title
	def getKeys(self):
		return self.recKeys

def discoverDVR():
	url = 'http://' + DVR_IPADDR + ':' + DVR_PORT + '/discover.json'
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	hdhr_dvr = HDHomeRun(data)
	print 'Found ' + hdhr_dvr.getName() \
		+ ' version: ' + hdhr_dvr.getVersion() \
		+ ' with ' + str(hdhr_dvr.getSpace()) + ' free space'
	return hdhr_dvr.getStorageURL()

def discoverRecordings(url):
	response = urllib.urlopen(url)
	data = json.loads(response.read())
	newKeys = {}
	prevKeys = None
	for recording in data:
		entry = Recording(recording)
		newKeys = entry.getKeys()
		if prevKeys != None:
			a = set(prevKeys)
			b = set(newKeys)
			addedKeys = b - a
			removedKeys = a - b
			if addedKeys or removedKeys:
				print 'Recording Metadata Added: ' + str(list(addedKeys)) + ' Removed: ' + str(list(removedKeys))
		else:
			print newKeys
		prevKeys = newKeys		
		print entry.getRecordingStr()
	return
	

if __name__ == "__main__":
	print '- HDHR Recordings Dump Tool '+strftime("%Y-%m-%d %H:%M:%S")+'-'
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
	md_file = ''
	recordingsURL = discoverDVR()
	print 'Processing following URL for recordings' + recordingsURL
	discoverRecordings(recordingsURL)
	print '- Complete -'
