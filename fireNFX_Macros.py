from midi import *
import transport
import ui
import general
from fireNFX_Classes import TnfxMacro
from fireNFX_Colors import *
from fireNFX_DefaultSettings import Settings
from fireNFX_Utils import getShade, shDark, shDim, shLight, shNorm, NavigateFLMenu

# code for macros
def Undo():
    if(Settings.UNDO_STYLE == 0):
        general.undoUp()
    else:
        general.undo()    

def ZoomSelection(zoomVal = Settings.DBL_TAP_ZOOM):
    zStr = 'DDDDDDDD'[0:zoomVal]
    NavigateFLMenu(',DRDDDDDR,DD,{}E'.format(zStr) )

def Articulate():
    NavigateFLMenu(',R,DR,DDDE')    

def QuickQuantize():
    NavigateFLMenu(',R,DR,DDDDE')    

def ShowScriptOutputWindow():
    ui.showWindow(widChannelRack)       # make CR the active window so it pulls up the main menu
    NavigateFLMenu(',LLLLDDDDDDDDDDE')  # series of keys to pass

def CloseAll():
    transport.globalTransport(FPT_F12, 1)  # close all...
    if(Settings.REOPEN_WINDOWS_AFTER_CLOSE_ALL):
        ui.showWindow(widBrowser)
        ui.showWindow(widChannelRack)
        ui.showWindow(widPlaylist)
        ui.showWindow(widMixer)

# BUILT-IN MACROS DEFINED HERE
# 
macCloseAll = TnfxMacro("Close All", getShade(cCyan, shDim), CloseAll) # special 
macTogChanRack = TnfxMacro("Chan Rack", cCyan)
macTogPlaylist = TnfxMacro("Playlist", cCyan)
macTogMixer = TnfxMacro("Mixer", cCyan)
#
macUndo = TnfxMacro("Undo", getShade(cYellow, shNorm), Undo )
macCopy = TnfxMacro("Copy", getShade(cBlue, shLight), ui.copy)
macCut = TnfxMacro("Cut", getShade(cMagenta, shNorm), ui.cut )
macPaste = TnfxMacro("Paste", getShade(cGreen, shLight), ui.paste)
#
macShowScriptWindow = TnfxMacro("Script Window", cWhite, ShowScriptOutputWindow)
macZoom = TnfxMacro("Zoom", cWhite, ZoomSelection)
macZoom = TnfxMacro("Zoom", cWhite, ZoomSelection)
macZoom = TnfxMacro("Zoom", cWhite, ZoomSelection)


# master macro list
_MacroList = [macCloseAll,  macTogChanRack, macTogPlaylist, macTogMixer, 
              macUndo,      macCopy,        macCut,         macPaste ]







