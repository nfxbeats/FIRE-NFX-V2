from midi import *
import transport
import ui
import general
import channels 
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
    NavigateFLMenu(',R,DR,DDDE,E')    

def TransposePROctaveUp():
    NavigateFLMenu(',RR,DDDDDDDDDDDE')    

def TransposePROctaveDown():
    NavigateFLMenu(',RR,DDDDDDDDDDDDE')    

def QuickQuantize():
    #NavigateFLMenu(',R,DR,DDDDE')    
    channels.quickQuantize(channels.channelNumber())

def QuickPRFix():
    QuickQuantize()
    Articulate()
    

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
macTogChanRack = TnfxMacro("Chan Rack", cCyan) # internal
macTogPlaylist = TnfxMacro("Playlist", cCyan) # internal 
macTogMixer = TnfxMacro("Mixer", cCyan) # internal
# 
macUndo = TnfxMacro("Undo", getShade(cYellow, shNorm), Undo )
macCopy = TnfxMacro("Copy", getShade(cBlue, shLight), ui.copy)
macCut = TnfxMacro("Cut", getShade(cMagenta, shNorm), ui.cut )
macPaste = TnfxMacro("Paste", getShade(cGreen, shLight), ui.paste)

# misc
macShowScriptWindow         = TnfxMacro("Script Window", cWhite, ShowScriptOutputWindow)
macZoom                     = TnfxMacro("Zoom", cWhite, ZoomSelection)

#Piano Roll
macQuickQuantize            = TnfxMacro("Quantize", getShade(cGreen, shLight), QuickQuantize)
macQuickPRFix               = TnfxMacro("Quant / Art", getShade(cGreen, shNorm), QuickPRFix)
macTransposePROctaveUp      = TnfxMacro("Octave Up", getShade(cBlue, shLight), TransposePROctaveUp)
macTransposePROctaveDown    = TnfxMacro("Octave Down", getShade(cBlue, shDark), TransposePROctaveDown)
_PianoRollMacros = [macQuickQuantize, macQuickPRFix, macTransposePROctaveUp, macTransposePROctaveDown]

# master macro list
_MacroList = [macCloseAll,  macTogChanRack, macTogPlaylist, macTogMixer, 
              macUndo,      macCopy,        macCut,         macPaste ]






