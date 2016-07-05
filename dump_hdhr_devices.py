#-------------------------------------------------------------------------------
# Simple Tool to dump te discovered HDHRs and their info
#
#-------------------------------------------------------------------------------
import os
import platform
import logging
import sys
import time
from time import strftime

import hdhr_discover

if __name__ == "__main__":
	print '- HDHR Device Discover Dump Tool '+strftime("%Y-%m-%d %H:%M:%S")+'-'
	logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)
	hdhrDiscover = hdhr_discover.HDHRDiscover()
	hdhrDiscover.getAuthStr()
	print '- Complete -'
