# fireNFX_DefaultSettings.py
#
# This file describes the available settings you can control.
# Do not edit this file. It will be overwritten on updates.
#
#  THIS FILE GETS OVERWRITTEN.
#  TO PROPERLY SET YOUR OWN DEFAULTS, EDIT and READ the file: fireNFX_Settings.py
#
#   Rules:
#
#   hastag lines # are comments. READ THEM to understand the values you need to provide for the setting below it.
#
#   True or False values must be spelled exactly as "True" or "False". using true/TRUE or false/FALSE will not work.
#
#   valid colors are: 
#       cWhite, cBlue, cGreen, cRed, cYellow, cCyan, cPurple, cOrange, cMagenta and cOff 
#
from fireNFX_Colors import *
from fireNFX_Defs import NotesListFlats, NotesListSharps
class TnfxDefaultSettings:
    def __init__(self) -> None:
        # color of pads when pressed.
        self.PAD_PRESSED_COLOR = cYellow

        # color of pads when pressed.
        # use  cChannel to use the channel color
        self.ROOT_NOTE_COLOR = cChannel

        # this is an interal way to control the brightness for things like vs non active pads
        # value can be 0-5 where 0 is NO DIMMING and 5 is MAX DIMMING
        self.DIM_DIM = 4
        self.DIM_NORMAL = 3
        self.DIM_BRIGHT = 1

        # How to display notes? Use sharps (#) or flats (b)
        # values can be: NotesListSharps  or NotesListFlats
        self.NOTE_NAMES = NotesListSharps

        # Default Root Note. If you select NotesListSharps in the   self.NOTE_NAMES, use '#' for non natural notes. 
        # otherwise use 'b' for the the flat name. ie 'C#' for NotesListSharps or 'Db' for NotesListFlats
        self.ROOT_NOTE = 'C'                      

        # lowest octave (bottom row) in NOTE mode. 
        # Can be a value from 1-5
        self.OCTAVE = 3                      

        # The default Scale to use in NOTES mode. Can be a number from 0-9 where: 
        #   0 = CHROMATIC           1 = Major/IONIAN
        #   2 = DORIAN              3 = PHRYGIAN
        #   4 = LYDIAN              5 = MIXOLYDIAN
        #   6 = AEOLIAN/Minor       7 = LOCRIAN
        #   8 = Major Pentatonic    9 = Minor Pentatonic
        self.SCALE = 0

        # when True, it will show all pads that have the same/repeated note mappings when octave notes overflow
        self.SHOW_ALL_MATCHING_CHORD_NOTES = False 

        # Whether or not to light the channel strip will indicate
        # other channels that share the same mixer routing
        self.SHOW_CHANNEL_WITH_SHARED_MIXER_CHANNELS = False

        # in NOTE mode, this will show what note is playing on playback (limited to mono - ie one note at a time)
        self.SHOW_PLAYBACK_NOTES = False

        # after a close all you have the core windows re-open automatically
        self.REOPEN_WINDOWS_AFTER_CLOSE_ALL = False

        # markers created by the script will have this prefix 
        self.MARKER_PREFIX_TEXT = "{}-Marker"  

        # shows extra info I use when debugging. may affect performance when True
        self.SHOW_PRN = False 

        # when true, will display 4x4 banks in ALT+DRUM mode. otherwise it uses octave strips in Row4..Row1 order
        self.ALT_DRUM_MODE_BANKS = True 

        # how long to keep the red boxes alive in FL Studio. in milliseconds, so 5000 would be 5 seconds, 0 = No display
        self.DISPLAY_RECT_TIME_MS = 5000

        # undo macro behavior:  0 = undo multiple times, 1 = undo last only. 
        self.UNDO_STYLE = 0

        # This number is how many fast or slow the knob wheel moves the value. This number represents how precise the knob will be
        # lower numbers are faster but less precise. higher numbers are slower but more precise.
        self.BROWSER_STEPS = 64          # default
        self.SHIFT_BROWSER_STEPS = 128   # when SHIFT is held
        self.ALT_BROWSER_STEPS = 8       # when ALT is held


        # this will set the naming style used when navigating to a new pattern
        # example, say your new pattern was number 11:  
        #   "Pattern {}" will name it:  Pattern 11
        #   "{}-Pattern" will name it:  11-Pattern 
        #
        self.PATTERN_NAME = "{}-Pattern" #  the {} will be replaced with the pattern number

        # this affects how the scripts reacts when you scroll to an empty pattern
        # can be True or False. 
        # when True, it will show the prompt to name a pattern.
        # when False, it will use the   self.PATTERN_NAME (above) value to name the pattern
        # 
        self.PROMPT_NAME_FOR_NEW_PATTERN = False

        # when True, This will close the Channel Rack when you select Browser. And reopen it when done.
        #            it also makes the ChannelRack WIndow act as a toggle between the it and the Browser
        # This allows you to have the detached ChannelRack overlaid on the Browser to save screen space.
        # and toggle between the two
        self.TOGGLE_CR_AND_BROWSER = False

        # When switching to Mixer, it changes to Mixer Knobs, Channel Rack changes to Channel Knobs
        self.AUTO_SWITCH_KNOBMODE = True

        # when switching to the browser, it forces to UDLR nav to show.
        self.FORCE_UDLR_ON_BROWSER = False 

        # a short delay when navigating FL menus - to allow the menu time to draw.
        self.MENU_DELAY = 0.025

        # some plugins will auto map the user1 and user2 knobs. ex: FLEX would have them mapped to the Macros
        # when auto mapped, they are locked in to that parameter for that specific plugin.
        # Set this to False to prevent them from auto mapping.
        self.AUTO_MAP_KNOWN_PARAMS_TO_USER_KNOBS = True

        self.STARTUP_TEXT_TOP = "-={ FIRE-NFX-V2 }=-"
        self.STARTUP_TEXT_BOT = "Version 2.0"
        self.STARTUP_FL_HINT = 'FIRE-NFX-V2 loaded.'

        self.DBL_TAP_DELAY_MS = 220
        self.DBL_TAP_ZOOM = 4

        self.GLOBAL_CONTROL_NAME = 'GLOBAL CTRL'

        self.SHOW_PIANO_ROLL_MACROS = False


# DO NOT EDIT BELOW:
Settings = TnfxDefaultSettings()
try:
    from fireNFX_UserSettings import TnfxUserSettings
    Settings = TnfxUserSettings()
    print('User settings found.')
except ImportError:
    print('User settings NOT found. Using defaults.')# Failed to import - assume they don't have custom settings

