#-------------------------------------------------------------------------------
# MPEG-TS Parser
#-------------------------------------------------------------------------------
import sys
import struct
import binascii
import ctypes
import io

class TSParser:
    def __init__(self, filename):
        self.filename = filename
        self.index = 0
        self.tssize = 188

    def read_next_section(self):
        with open(self.filename, "rb") as f:
            f.seek(self.index)
            while True:
                chunk = f.read(self.tssize)
                self.index += 188
                if chunk:
                    yield chunk
                else:
                    break

    def parse_ts_header(self, section):
        return struct.unpack_from('>I',section[0:4],0)[0]

    def header_contains_pid(self, header, pid):
        lpid = (header & 0x001FFF00) >> 8
        if lpid == pid:
            return True

    def extract_payload(self, section):
        payload = struct.unpack_from('184s',section,4)
        return payload

    def extract_metadata(self, payload):
        # need to build up a string
        tempData = ''
        mdString = ''
        metaData = []
        if payload[0][0] == '{' :
            # we have a start
            for md in payload :
                if md[0] != 0xFF:
                    tempData += md
                    
            # find stop } in string
            stopIndex = tempData.find('}')
            if stopIndex > 0:
                mdString = tempData[1:stopIndex]
            
            # Need to fix up the string to make the split into a tuple list easier
            # if only SD would add string demarkers to stringified numbers..
            mdString = mdString.replace('","','"|"')
            mdString = mdString.replace(',"','"|"')
            mdString = mdString.replace('":"','","')
            mdString = mdString.replace('":','","')
            
            # Now to create the tuple list
            mdTuples = mdString.split('|')
            for t in mdTuples:
                metaData.append(t.split(','))
        return metaData
