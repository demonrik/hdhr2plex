#-------------------------------------------------------------------------------
# HDHomerun HDHR Discover API
#-------------------------------------------------------------------------------
import os
import logging
import json
import urllib

hdhr_deviceID = 'DeviceID'
hdhr_localIP = 'LocalIP'
hdhr_baseURL = 'BaseURL'
hdhr_discoverURL = 'DiscoverURL'
hdhr_lineupURL = 'LineupURL'
hdhr_storageURL = 'StorageURL'

hdhr_name = 'FriendlyName'

hdhr_modelNum = 'ModelNumber'
hdhr_fwName = 'FirmwareName'
hdhr_fwVer = 'FirmwareVersion'
hdhr_devAuth = 'DeviceAuth'
hdhr_tuners = 'TunerCount'

hdhr_ver = 'Version'
hdhr_storageID = 'StorageID'
hdhr_freespace = 'FreeSpace'

class HDHRDiscover:
	__devices = []
	
	def __init__(self):
		url = 'http://ipv4.my.hdhomerun.com/discover'
		response = urllib.urlopen(url)
		data = json.loads(response.read())
		hdhrs_found = len(data)
		logging.debug('found ' + str(hdhrs_found) + ' HDHomerun devices')
		for hdhr_info in data:
			self.__devices.append(HDHomeRun(hdhr_info))

	def getAuthStr(self):
		authStr = ''
		for device in self.__devices:
			if device.isHttpDev:
				if not device.isDVR:
					authStr += device.getAuth()
		logging.debug('final authstr ' + authStr)
		return authStr
		
	def getStorageDevices(self):
		devices = []
		for device in self.__devices:
			if device.isDVR:
				devices.append(device)
		return devices


class HDHomeRun:
	
	def __init__(self, hdhr_data):
		self.isHttpDev = False
		self.isDVR = False
		self.hdhr_discoverURL = None
		self.hdhr_storageURL = None
		self.devAuth = None;
		
		for key in hdhr_data.keys():
			if key == hdhr_deviceID:
				self.hdhr_deviceID = hdhr_data[hdhr_deviceID]
			if key == hdhr_localIP:
				self.hdhr_localIP = hdhr_data[hdhr_localIP]
			if key == hdhr_baseURL:
				self.hdhr_baseURL = hdhr_data[hdhr_baseURL]
			if key == hdhr_discoverURL:
				self.hdhr_discoverURL = hdhr_data[hdhr_discoverURL]
			if key == hdhr_lineupURL:
				self.hdhr_lineupURL = hdhr_data[hdhr_lineupURL]
			if key == hdhr_storageURL:
				self.hdhr_storageURL = hdhr_data[hdhr_storageURL]
			if key == hdhr_storageID:
				self.hdhr_storageID = hdhr_data[hdhr_storageID]
				self.hdhr_deviceID = hdhr_data[hdhr_storageID]

		if self.hdhr_discoverURL == None:
			logging.info('HDHR Device ' + self.hdhr_deviceID + ' is not supported by DVR project - skipping')
			return
		
		if self.hdhr_discoverURL != None:
			self.isHttpDev = True
			response = urllib.urlopen(self.hdhr_discoverURL)
			dev_data = json.loads(response.read())
			logging.info('HDHR Device ' + self.hdhr_deviceID + ' is HTTP Capable')
			for key in dev_data.keys():
				if key == hdhr_name:
					self.hdhr_name = dev_data[hdhr_name]
				if key == hdhr_modelNum:
					self.hdhr_modelNum = dev_data[hdhr_modelNum]
				if key == hdhr_fwName:
					self.hdhr_fwName = dev_data[hdhr_fwName]
				if key == hdhr_fwVer:
					self.hdhr_fwVer = dev_data[hdhr_fwVer]
				if key == hdhr_devAuth:
					self.hdhr_devAuth = dev_data[hdhr_devAuth]
				if key == hdhr_tuners:
					self.hdhr_tuners = dev_data[hdhr_tuners]
				if key == hdhr_ver:
					self.hdhr_ver = dev_data[hdhr_ver]
				if key == hdhr_freespace:
					self.hdhr_freespace = dev_data[hdhr_freespace]

		if self.hdhr_storageURL != None:
			logging.info('HDHR Device ' + self.hdhr_deviceID + ' is DVR Engine')
			self.isDVR = True
	
	def getModel(self):
		if self.isHttpDev:
			return self.hdhr_modelNum
		else:
			return 'Not HHTP DVR'
	
	def getID(self):
		if self.isHttpDev:
			return self.hdhr_deviceID
		else:
			return 'Not HHTP DVR'
	
	def getAuth(self):
		if self.isHttpDev:
			return self.hdhr_devAuth
		else:
			return 'Not HHTP DVR'
	
	def getStorageURL(self):
		if self.isDVR:
			return self.hdhr_storageURL
		else:
			return 'Not DVR Engine'
	