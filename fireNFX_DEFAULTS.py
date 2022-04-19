from fireNFX_Colors import *
from fireNFX_Defs import NotesListFlats, NotesListSharps


# color of pads when pressed.
# valid colors are: cWhite, cBlue, cGreen, cRed, cYellow, cCyan, cPurple, cOrange, cMagenta and cOff 
DEFAULT_PAD_PRESSED_COLOR = cYellow

# color of pads when pressed.
# valid colors are: cWhite, cBlue, cGreen, cRed, cYellow, cCyan, cPurple, cOrange, cMagenta and cOff 
# use  cChannel to use the channel color
DEFAULT_ROOT_NOTE_COLOR = cBlue 

# this is an interal way to control the brightness for things like vs non active pads
# value can be 0-4 where 0 is NO DIMMING and 4 is MAX DIMMING
DEFAULT_DIM_FACTOR = 3
DEFAULT_DIM_BRIGHT = 2

# How to display notes? Use sharps (#) or flats (b)
# values can be: NotesListSharps  or NotesListFlats
DEFAULT_NOTE_NAMES = NotesListSharps

# Default Root Note. If you select NotesListSharps in the DEFAULT_NOTE_NAMES, use '#' for non natural notes. 
# otherwise use 'b' for the the flat name. ie C# vs. Db
DEFAULT_ROOT_NOTE = 'C'                      

# lowest octave (bottom row) in NOTE mode. 
# Can be a value from 1-5
DEFAULT_OCTAVE = 3                      

# The default Scale to use in NOTES mode. Can be a number from 0-9 where: 
#   0 = CHROMATIC           1 = Major/IONIAN
#   2 = DORIAN              3 = PHRYGIAN
#   4 = LYDIAN              5 = MIXOLYDIAN
#   6 = AEOLIAN/Minor       7 = LOCRIAN
#   8 = Major Pentatonic   9 = Minor Pentatonic
DEFAULT_SCALE = 0


# Whether or not to light the channel strip will indicate
# other channels that share the same mixer routing
#
DEFAULT_SHOW_CHANNEL_WITH_SHARED_MIXER_CHANNELS = True 


