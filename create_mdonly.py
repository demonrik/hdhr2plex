#-------------------------------------------------------------------------------
# Simple Tool to create a metadata only TS file for testing from metadata
# provided by user log extracts
#
#########
#
# Expected Log Format:
#    DEBUG:root:<name>|<value>
#-------------------------------------------------------------------------------
import os
import sys
import logging
import time
from time import strftime

import hdhr_tswriter

md_data = []

def parse_md_file(filename):
	md_tuple_str = ''
	for line in open(filename,'r'):
		if line.startswith('INFO:root:'):
			md_tuple_str = line[len('INFO:root:'):].rstrip()
			md_name, md_value = md_tuple_str.split('|',1)
			if ((md_name == 'EndTime')
				or (md_name == 'OriginalAirdate')
				or (md_name == 'StartTime')
				or (md_name == 'RecordStartTime')
				or (md_name == 'RecordEndTime')):
				# Time values - do nothing to the value
				logging.debug('Number detected - not modifying string')
			else: 
				md_value = '"%s"' % md_value
			md_name = '"%s"' % md_name
			#reconstruct the string
			md_tuple_str = str(md_name) + '|' + str(md_value)
			# add to metadata array
			md_data.append(md_tuple_str.split('|',1))
			print '== Found ' + str(md_name) + ' with value ' + str(md_value)
	return

if __name__ == "__main__":
	print '- HDHR TS MetaData Create Tool '+strftime("%Y-%m-%d %H:%M:%S")+'-'
	#capture any logging messages to STDOUT
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
	md_file = ''
	if (len(sys.argv) == 2):
		md_file=sys.argv[1]
		print 'Parsing ' + md_file
		parse_md_file(md_file)
		tswr = hdhr_tswriter.TSWriter(md_data)
		tswr.add_custom_md('"hdhr2plex"','1')
		tswr.create_ts_file(md_file)
	else:
		print 'Unexpected number of parameters - please just provide single input filename.'
		print 'Usage:'
		print '  create_mdonly.py <filename>'
		print ''
		print 'Script will parse the metadata file and create a .MPG file with same name'
		sys.exit(0)
	print '- Complete -'
