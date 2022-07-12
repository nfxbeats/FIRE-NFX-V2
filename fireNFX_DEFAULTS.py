from fireNFX_Colors import *
from fireNFX_Defs import NotesListFlats, NotesListSharps


#   valid colors are: cWhite, cBlue, cGreen, cRed, cYellow, cCyan, cPurple, cOrange, cMagenta and cOff 
#

# color of pads when pressed.
DEFAULT_PAD_PRESSED_COLOR = cYellow

# color of pads when pressed.
# use  cChannel to use the channel color
DEFAULT_ROOT_NOTE_COLOR = cBlue 

# this is an interal way to control the brightness for things like vs non active pads
# value can be 0-4 where 0 is NO DIMMING and 4 is MAX DIMMING
DEFAULT_DIM_FACTOR = 3
DEFAULT_DIM_BRIGHT = 1

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
#   8 = Major Pentatonic    9 = Minor Pentatonic
DEFAULT_SCALE = 0

DEFAULT_SHOW_ALL_MATCHING_CHORD_NOTES = False # when True, it will show all pads that have the same note mappings.


# Whether or not to light the channel strip will indicate
# other channels that share the same mixer routing
#
DEFAULT_SHOW_CHANNEL_WITH_SHARED_MIXER_CHANNELS = True # will display the channels that have a common mixer number with the selected channel

DEFAULT_SHOW_PLAYBACK_NOTES = True # in NOTE mode, this will show what note is playing on playback (limited to mono - ie one note at a time)

DEFAULT_REOPEN_WINDOWS_AFTER_CLOSE_ALL = True # after a close all you have the core windows re-open automatically

DEFAULT_MARKER_PREFIX_TEXT = "nfx#"  # markers created by the script will have this prefix 

DEFAULT_SHOW_PRN = True # shows extra info I use when debugging. may affect performance when True

DEFAULT_ALT_DRUM_MODE_BANKS = True # when true, will display four banks in Al DRUM mode. otherwise it uses Row4..Row1 order

