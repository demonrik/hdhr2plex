#-------------------------------------------------------------------------------
# Simple Tool to dump the meta data from an SD HDHomeRun DVR TS (.mpg) File
#
#########
#
#-------------------------------------------------------------------------------
import os
import platform
import logging
import sys
import time
from time import strftime

import hdhr_tsparser
import hdhr_md

HDHR_TS_METADATA_PID = 0x1FFA

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

if __name__ == "__main__":
	print '- HDHR TS MetaData Dump Tool '+strftime("%Y-%m-%d %H:%M:%S")+'-'
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
	md_file = ''
	
	if (len(sys.argv) == 2):
		md_file=sys.argv[1]
		print 'Parsing ' + md_file
		metaData = parse_file_for_data(md_file)
		md = hdhr_md.HDHomeRunMD(metaData)
		md.print_metaData()
	else:
		print 'Unexpected number of parameters - please just provide single input filename.'
		print 'Usage:'
		print '  dump_md.py <filename>'
		print ''
		print 'Script will parse the TS file for the SD program, extrat the metadata and'
		print 'dump to stdout'
		sys.exit(0)

	print '- Complete -'
