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
import platform
import sys
import re
import time
from time import strftime
import hdhr_tsparser

HDHR_TS_METADATA_PID_BU = 0x1F
HDHR_TS_METADATA_PID_BL = 0xFA
TS_SYNC_BYTE = 0x47
TS_START_BYTE = 0x40
TS_CONTROL_BYTE = 0x10
TS_BLOCK_SIZE = 0xBC
HDHR_PID_SIZE = 0x2EFF

md_data = {}

def build_header(start, counter):
   barray = bytearray()
   barray.append(TS_SYNC_BYTE)
   if start:
       barray.append(HDHR_TS_METADATA_PID_BU | TS_START_BYTE)
   else:
       barray.append(HDHR_TS_METADATA_PID_BU)
   barray.append(HDHR_TS_METADATA_PID_BL)
   barray.append(TS_CONTROL_BYTE | counter)
   return barray

def parse_md_file(filename):
   md_tuple = ''
   for line in open(filename,'r'):
       if line.startswith('DEBUG:root:'):
           md_tuple = line[len('DEBUG:root:'):].rstrip()
           md_name, md_value = md_tuple.split('|',1)
           if ((md_name == 'EndTime')
              or (md_name == 'OriginalAirdate')
              or (md_name == 'StartTime')
              or (md_name == 'RecordStartTime')
              or (md_name == 'RecordEndTime')):
               md_data[('"%s"' % md_name)]= md_value
           else: 
               md_data[('"%s"' % md_name)]= '"%s"' % md_value
           print '== Found ' + md_name + ' with value ' + md_value
   return

def create_ts_file(filename):
   ts_filename, ts_ext = os.path.splitext(os.path.basename(filename))
   ts_filename = ts_filename + '.mpg'

   if os.path.dirname(filename):
       ts_filename = os.path.join(os.path.dirname(filename),ts_filename)

   print 'Writing the Meta Data to the TS File...'
   ts_file=open(ts_filename,'wb')
   start = True
   bytesLeft = TS_BLOCK_SIZE
   blockCtr = 0
   blocksDone = 0
   for key in sorted(md_data.keys()):
       if start:
           header = build_header(start, blockCtr)
           blockCtr = (blockCtr + 1) % 0x10
           header.append('{')
           ts_file.write(header)
           start = False
           bytesLeft = bytesLeft - 5
       else:
          print 'Separate Tuples...'
          if bytesLeft >= 1:
              ts_file.write(',')
              bytesLeft = bytesLeft - 1
          else:
              blocksDone = blocksDone + 1
              header = build_header(start, blockCtr)
              blockCtr = (blockCtr + 1) % 0x10
              ts_file.write(header)
              ts_file.write(',')
              bytesLeft = bytesLeft - 5
       
       print 'Writing Key: ' + key
       if len(key) <= bytesLeft:
           ts_file.write(bytearray(key))
           bytesLeft = bytesLeft - len(key)
       else:
           key_left = key[:bytesLeft]
           key_right = key[bytesLeft:]
           	
           if bytesLeft != 0:
               ts_file.write(key_left)
           blocksDone = blocksDone + 1
           header = build_header(start, blockCtr)
           blockCtr = (blockCtr + 1) % 0x10
           ts_file.write(header)
           bytesLeft = TS_BLOCK_SIZE - 4
           
           ts_file.write(key_right)
           bytesLeft = bytesLeft - (len(key_right))
       
       print 'Writing Separater'
       if bytesLeft >= 1:
           ts_file.write(':')
           bytesLeft = bytesLeft - 1
       else:
           blocksDone = blocksDone + 1
           header = build_header(start, blockCtr)
           blockCtr = (blockCtr + 1) % 0x10
           ts_file.write(header)
           ts_file.write(':')
           bytesLeft = bytesLeft - 5

       print 'Writing Value: ' + md_data[key]
       if len(md_data[key]) <= bytesLeft:
           ts_file.write(bytearray(md_data[key]))
           bytesLeft = bytesLeft - len(md_data[key])
       else:
           val_left = md_data[key][:bytesLeft]
           val_right = md_data[key][bytesLeft:]
           if bytesLeft != 0:
               ts_file.write(val_left)

           blocksDone = blocksDone + 1
           header = build_header(start, blockCtr)
           blockCtr = (blockCtr + 1) % 0x10
           ts_file.write(header)
           bytesLeft = bytesLeft - 4

           ts_file.write(val_right)
           bytesLeft = 188 - (len(md_data[key]) - bytesLeft)

   ts_file.write('}')
   for x in range (0 , (bytesLeft - 1)):
       ts_file.write(bytearray(b'\xFF'))
   if blocksDone < (HDHR_PID_SIZE / TS_BLOCK_SIZE):
       print 'Need to add more blocks'
       for x in range (0, (HDHR_PID_SIZE / TS_BLOCK_SIZE) - blocksDone):
           header = build_header(start, blockCtr)
           blockCtr = (blockCtr + 1) % 0x10
           ts_file.write(header)
           for y in range (0, TS_BLOCK_SIZE - 4):
               ts_file.write(bytearray(b'\xFF'))
       
   ts_file.close()
   return

if __name__ == "__main__":
    print '- HDHR TS MetaData Create Tool '+strftime("%Y-%m-%d %H:%M:%S")+'-'
    md_file = ''
    if (len(sys.argv) == 2):
        md_file=sys.argv[1]
        print 'Parsing ' + md_file
    else:
        print 'Unexpected number of parameters - please just provide single input filename.'
        print 'Usage:'
        print '  create_mdonly.py <filename>'
        print ''
        print 'Script will parse the metadata file and create a .MPG file with same name'
        sys.exit(0)

    parse_md_file(md_file)
    create_ts_file(md_file)
    print '- Complete -'
