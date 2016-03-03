#!/bin/sh

# Simple Post Processing Script to be called by Python scripts once
# file is ready to be modified
# Expects to be called with just 2 parameters - an input filename $1
# and an output filename $2
# Any other parameters will have to be processed by other means

# This sample post processing script will check for the existance
# of ffmpeg and if it exists ensure it can process TS input and
# MKV output. The script will simply remux the input TS file to
# an output MKV file for better processing by Plex clients. No
# video or audio conversion is done. It is assummed that if the TS
# file contains MPEG2 or MPEG4 that is the video that will be placed
# in the container. MKV is used because it is largely agnostic of
# the stream codecs

# Prep the parameters
INPUT_FILE="$1"
OUTPUT_FILE="$2"
BIN=`which ffmpeg`
CMD_RM=`which rm`
CMD_GREP=`which grep`

# Make sure we have parameters
if [ $# -eq 0 ] || [ -z "$1" ] || [ -z "$2" ] ; then
  echo "Not all arguments needed - supplied, ERROR"
  exit 1
fi

# Check for existance of ffmpeg
if [ -z "$BIN" ] ; then
  echo "No ffmpeg found - ERROR"
  exit 1
fi

# Check ffmpeg for TS and Matroska support
FORMATS=`$BIN -formats`
TSFORMAT=`echo $FORMATS | $CMD_GREP mpegts`
MKVFORMAT=`echo $FORMATS | $CMD_GREP matroska`

if [ -z "$TSFORMAT" ] || [ -z "$MKVFORMAT" ] ; then
  echo "ffmpeg is missing one of the required formats"
  exit 1
fi

# Execute the conversion
$BIN -i "$INPUT_FILE" -vcodec copy -acodec copy "$OUTPUT_FILE"

# Verify it worked and we have OUTPUT_FILE
if [ -f "$OUTPUT_FILE" ] ; then
  echo "Output is done"
else
  echo "Failed to create output"
  exit 1
fi

# Remove the input file from the system
$CMD_RM "$INPUT_FILE"

exit 0
