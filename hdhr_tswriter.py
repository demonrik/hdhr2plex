#-------------------------------------------------------------------------------
# HDHomerun MetaData TS File Writer
#-------------------------------------------------------------------------------
import os
import logging

HDHR_TS_METADATA_PID_BU = 0x1F
HDHR_TS_METADATA_PID_BL = 0xFA
TS_SYNC_BYTE = 0x47
TS_START_BYTE = 0x40
TS_CONTROL_BYTE = 0x10
TS_BLOCK_SIZE = 0xBC
HDHR_PID_SIZE = 0x2EFF

class TSWriter:
	md_data = {}
	
	def build_md_dict(self, metadata):
		for md in metadata:
			if ((md[0] == '"EndTime"')
				or (md[0] == '"OriginalAirdate"')
				or (md[0] == '"StartTime"')
				or (md[0] == '"RecordStartTime"')
				or (md[0] == '"RecordEndTime"')
				or (md[0] == '"FirstAiring"')):
				self.md_data[md[0]]=md[1].replace('"',"")
			else:
				self.md_data[md[0]]= md[1]
	
	def __init__(self, metadata):
		self.build_md_dict(metadata)
		
	def add_custom_md(self, key, value):
		self.md_data.update({key:value})
		
	def build_header(self, start, counter):
		barray = bytearray()
		barray.append(TS_SYNC_BYTE)
		if start:
			barray.append(HDHR_TS_METADATA_PID_BU | TS_START_BYTE)
		else:
			barray.append(HDHR_TS_METADATA_PID_BU)
		barray.append(HDHR_TS_METADATA_PID_BL)
		barray.append(TS_CONTROL_BYTE | counter)
		return barray
	
	def create_ts_file(self, filename):
		ts_filename, ts_ext = os.path.splitext(os.path.basename(filename))
		ts_filename = ts_filename + '.mpg'
	
		if os.path.dirname(filename):
			ts_filename = os.path.join(os.path.dirname(filename),ts_filename)
	
		logging.info('Writing the Meta Data to the TS File...')
		ts_file=open(ts_filename,'wb')
		start = True
		bytesLeft = TS_BLOCK_SIZE
		blockCtr = 0
		blocksDone = 0
		for key in sorted(self.md_data.keys()):
			if start:
				header = self.build_header(start, blockCtr)
				blockCtr = (blockCtr + 1) % 0x10
				header.append('{')
				logging.debug('Writing the Header to the TS File...')
				ts_file.write(header)
				start = False
				bytesLeft = bytesLeft - 5
			else:
				logging.debug('Separate Tuples...')
				if bytesLeft >= 1:
					ts_file.write(',')
					bytesLeft = bytesLeft - 1
				else:
					blocksDone = blocksDone + 1
					header = self.build_header(start, blockCtr)
					blockCtr = (blockCtr + 1) % 0x10
					logging.debug('Writing the Header to the TS File...')
					ts_file.write(header)
					ts_file.write(',')
					bytesLeft = bytesLeft - 5

			logging.debug('Writing the Key: ' + key)
			if len(key) <= bytesLeft:
				ts_file.write(bytearray(key))
				bytesLeft = bytesLeft - len(key)
			else:
				key_left = key[:bytesLeft]
				key_right = key[bytesLeft:]
				if bytesLeft != 0:					ts_file.write(key_left)
				blocksDone = blocksDone + 1
				header = self.build_header(start, blockCtr)
				blockCtr = (blockCtr + 1) % 0x10
				logging.debug('Writing the Header to the TS File...')
				ts_file.write(header)
				bytesLeft = TS_BLOCK_SIZE - 4
				ts_file.write(key_right)
				bytesLeft = bytesLeft - (len(key_right))
		   
			logging.debug('Writing the Separator :')
			if bytesLeft >= 1:
				ts_file.write(':')
				bytesLeft = bytesLeft - 1
			else:
				blocksDone = blocksDone + 1
				header = self.build_header(start, blockCtr)
				blockCtr = (blockCtr + 1) % 0x10
				ts_file.write(header)
				ts_file.write(':')
				bytesLeft = bytesLeft - 5
	
			logging.debug('Writing Value: ' + self.md_data[key])
			if len(self.md_data[key]) <= bytesLeft:
				ts_file.write(bytearray(self.md_data[key]))
				bytesLeft = bytesLeft - len(self.md_data[key])
			else:
				val_left = self.md_data[key][:bytesLeft]
				val_right = self.md_data[key][bytesLeft:]
				if bytesLeft != 0:
					ts_file.write(val_left)
	
				blocksDone = blocksDone + 1
				header = self.build_header(start, blockCtr)
				blockCtr = (blockCtr + 1) % 0x10
				ts_file.write(header)
				bytesLeft = bytesLeft - 4
	
				ts_file.write(val_right)
				bytesLeft = 188 - (len(self.md_data[key]) - bytesLeft)
	
		ts_file.write('}')
		logging.debug('Padding out the final TS frame')
		for x in range (0 , (bytesLeft - 1)):
			ts_file.write(bytearray(b'\xFF'))
		
		logging.debug('Padding out the TS Program to ensure the file is right size')
		while (blocksDone < 63):
			blocksDone = blocksDone + 1
			bytesLeft = 184
			header = self.build_header(start, blockCtr)
			blockCtr = (blockCtr + 1) % 0x10
			ts_file.write(header)
			for x in range (0 , bytesLeft):
				ts_file.write(bytearray(b'\xFF'))

		ts_file.close()
		return
