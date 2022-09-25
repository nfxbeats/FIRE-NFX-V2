# fireNFX_DEFAULTS.py
#
# DO NOT CHANGE THE FOLLOWING IMPORT LINES

from fireNFX_Colors import *
from fireNFX_Defs import NotesListFlats, NotesListSharps

#
#   Rules:
#
#   hastag lines # are comments. READ THEM to understand the values you need to provide for the setting below it.
#
#   lines with a DEFAULT_XXXX value can be edited after the = symbol to set that value
#
#   True or False values must be spelled exactly as "True" or "False". using true/TRUE or false/FALSE will not work.
#
#   valid colors are: 
#       cWhite, cBlue, cGreen, cRed, cYellow, cCyan, cPurple, cOrange, cMagenta and cOff 
#
#
#____________ OK TO EDIT AFTER THIS LINE______________

# color of pads when pressed.
DEFAULT_PAD_PRESSED_COLOR = cRed

# color of pads when pressed.
# use  cChannel to use the channel color
DEFAULT_ROOT_NOTE_COLOR = cBlue

# this is an interal way to control the brightness for things like vs non active pads
# value can be 0-5 where 0 is NO DIMMING and 5 is MAX DIMMING
DEFAULT_DIM_DIM = 4
DEFAULT_DIM_FACTOR = 3
DEFAULT_DIM_BRIGHT = 1

# How to display notes? Use sharps (#) or flats (b)
# values can be: NotesListSharps  or NotesListFlats
DEFAULT_NOTE_NAMES = NotesListSharps

# Default Root Note. If you select NotesListSharps in the DEFAULT_NOTE_NAMES, use '#' for non natural notes. 
# otherwise use 'b' for the the flat name. ie 'C#' for NotesListSharps or 'Db' for NotesListFlats
DEFAULT_ROOT_NOTE = 'C'                      

# lowest octave (bottom row) in NOTE mode. 
# Can be a value from 1-5
DEFAULT_OCTAVE = 3                      

# The default Scale to use in NOTES mode. Can be a number from 0-9 where: 
#   0 = CHROMATIC           1 = Major/IONIAN
#   2 = DORIAN              3 = PHRYGIAN
#   4 = LYDIAN              5 = MIXOLYDIAN
#   6 = AEOLIAN/Minor       7 = LOCRIAN
#   8 = Major Pentatonic    9 = Minor Pentatonic
DEFAULT_SCALE = 0

# when True, it will show all pads that have the same/repeated note mappings when octave notes overflow
DEFAULT_SHOW_ALL_MATCHING_CHORD_NOTES = False 

# Whether or not to light the channel strip will indicate
# other channels that share the same mixer routing
DEFAULT_SHOW_CHANNEL_WITH_SHARED_MIXER_CHANNELS = True 

# in NOTE mode, this will show what note is playing on playback (limited to mono - ie one note at a time)
DEFAULT_SHOW_PLAYBACK_NOTES = True 

# after a close all you have the core windows re-open automatically
DEFAULT_REOPEN_WINDOWS_AFTER_CLOSE_ALL = True 

# markers created by the script will have this prefix 
DEFAULT_MARKER_PREFIX_TEXT = "nfx#"  

# shows extra info I use when debugging. may affect performance when True
DEFAULT_SHOW_PRN = False 

# when true, will display 4x4 banks in ALT+DRUM mode. otherwise it uses octave strips in Row4..Row1 order
DEFAULT_ALT_DRUM_MODE_BANKS = True 

# how long to keep the red boxes alive in FL Studio. in milliseconds, so 5000 would be 5 seconds, 0 = No display
DEFAULT_DISPLAY_RECT_TIME_MS = 5000

# undo macro behavior:  0 = undo multiple times, 1 = undo last only. 
DEFAULT_UNDO_STYLE = 0

# This number is how many fast or slow the knob wheel moves the value. This number represents how precise the knob will be
# lower numbers are faster but less precise. higher numbers are slower but more precise.
DEFAULT_BROWSER_STEPS = 64          # default
DEFAULT_SHIFT_BROWSER_STEPS = 128   # when SHIFT is held
DEFAULT_ALT_BROWSER_STEPS = 8       # when ALT is held
