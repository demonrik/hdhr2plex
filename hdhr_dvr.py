#-------------------------------------------------------------------------------
# HDHomerun HDHR DVR API
#-------------------------------------------------------------------------------
import os
import platform
import logging
import sys
import json
import urllib

import hdhr_discover

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


class HDHRRecording:
	def __init__(self, data):
		self.Category = ''
		self.ChannelAffiliate = ''
		self.ChannelImageURL = ''
		self.ChannelName = ''
		self.ChannelNumber = ''
		self.EndTime = 0
		self.EpisodeNumber = ''
		self.EpisodeTitle = ''
		self.FirstAiring = 0
		self.ImageURL = ''
		self.OriginalAirDate = 0
		self.ProgramID = ''
		self.RecordEndTime = 0
		self.RecordStartTime = 0
		self.SeriesID = ''
		self.StartTime = 0
		self.Synopsis = ''
		self.Title = ''
		self.DisplayGroupID = ''
		self.PlayURL = ''
		self.CmdURL = ''
		
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
			return str(len(self.recKeys)) + ' keys | Title: ' + self.Title + ' SeriesID: ' + self.SeriesID + ' Episode: ' + self.EpisodeNumber
		except AttributeError:
			return str(len(self.recKeys)) + ' keys | Title: ' + self.Title + ' SeriesID: ' + self.SeriesID
	
	def getFullString(self):
		retStr = '----------------------------------------'\
			+ '\nSeriesID: ' + self.SeriesID \
			+ '\n Category: ' + self.Category \
			+ '\n DisplayGroupID: ' + self.DisplayGroupID \
			+ '\n Title: ' + self.Title \
			+ '\n ChannelName: ' + self.ChannelName \
			+ '\n ChannelNumber ' + self.ChannelNumber \
			+ '\n ChannelAffiliate: ' + self.ChannelAffiliate \
			+ '\n ProgramID ' + self.ProgramID \
			+ '\n EpisodeNumber ' + self.EpisodeNumber \
			+ '\n EpisodeTitle ' + self.EpisodeTitle \
			+ '\n OriginalAirdate ' + str(self.OriginalAirdate) \
			+ '\n FirstAiring ' + str(self.FirstAiring) \
			+ '\n Synopsis ' + self.Synopsis
		return retStr

	def getKeys(self):
		return self.recKeys
		
	def getSeriesID(self):
		return self.SeriesID


class HDHRDVR:	
	def __init__(self):
		self.hdhr_list = hdhr_discover.HDHRDiscover()
		return
	
	def getRecordings(self):
		entries = []
		engines = self.hdhr_list.getStorageDevices()
		for engine in engines:
			logging.debug('Processing ' + engine.getID() + ' for recordings')
			response = urllib.urlopen(engine.getStorageURL())
			data = json.loads(response.read())
			for recording in data:
				entry = HDHRRecording(recording)
				entries.append(entry)
		return entries
		
	def getRules(self):
		authStr = hdhr_list.getAuthStr()
		logging.debug('Fetching Rules list with AuthStr: ' + authStr)
		return
		
	def getSeriesRecordings(self, seriesID):
		entries = []
		recordings = self.getRecordings()
		for recording in recordings:
			if recording.getSeriesID() == seriesID:
				entries.append(recording)
		return entries
	
	