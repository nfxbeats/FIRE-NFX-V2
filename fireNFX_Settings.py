# This is the user setting file that will allow you set some custom parameters.
#
# To use this file, it must be renamed to exactly: "fireNFX_UserSettings.py"
# and exist in the same folder as the other scripts.
#
# Be sure to only edit the part below where marked "OK TO EDIT..."
# 
# DO NOT CHANGE THESE LINES:
from fireNFX_DefaultSettings import *
from fireNFX_Colors import *
from fireNFX_Defs import NotesListFlats, NotesListSharps
class TnfxUserSettings(TnfxDefaultSettings):
    def __init__(self) -> None:
        super().__init__()

        # For explanation and list of ALL available settings see: fireNFX_DefaultSettings.py
        #
        # keep indentation as-is to function properly
        #
        # OK TO EDIT THE FOLLOWING:
        self.PAD_PRESSED_COLOR = cRed
        self.SHOW_PLAYBACK_NOTES = True 
        self.REOPEN_WINDOWS_AFTER_CLOSE_ALL = True
        self.MARKER_PREFIX_TEXT = "{}-Marker"  #  the {} will be replaced with the bar number
        self.PATTERN_NAME = "{}-Pattern" #  the {} will be replaced with the pattern number
        self.AUTO_SWITCH_KNOBMODE = True




