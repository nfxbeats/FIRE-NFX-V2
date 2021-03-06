# name=FIRE-NFX-V2
# supportedDevices=FL STUDIO FIRE
#
# author: Nelson F. Fernandez Jr. <nfxbeats@gmail.com>
#
# develoment started:   11/24/2021
# first public beta:    07/13/2022
#
# thanks to: HDSQ, TayseteDj, DAWNLIGHT, a candle, Miro and Image-Line
# 
#

import device
import midi
import channels
import patterns
import utils
import time
import ui 
import transport 
import mixer 
import general
import plugins 
import playlist
import arrangement

from harmonicScales import *

from fireNFX_DEFAULTS import *
from fireNFX_Classes import *
from fireNFX_Defs import * 
from fireNFX_PadDefs import *
from fireNFX_Utils import * 
from fireNFX_Display import *
from fireNFX_PluginDefs import *

#region globals
_debugprint = DEFAULT_SHOW_PRN
_rectTime = DEFAULT_DISPLAY_RECT_TIME_MS
_ShiftHeld = False
_AltHeld = False
_PatternCount = 0
_CurrentPattern = -1
_PatternPage = 1
_ChannelCount = 0
_CurrentChannel = -1
_PreviousChannel = -1
_isAltMode = False
_isShiftMode = False 
_ChannelPage = 1
_KnobMode = 0
_Beat = 1
_PadMap = list()
_PatternMap = list()
_PatternSelectedMap = list()
_ChannelMap = list()
_ChannelSelectedMap = list()
_PlaylistMap = list()
_PlaylistSelectedMap = list()
_MarkerMap = list()
_ProgressMapSong = list()
_ProgressMapPatterns = list()
_ShowMixer = 1
_ShowChanRack = 1
_ShowPlaylist = 1
_ShowBrowser = 1
_ShowPianoRoll = 0
_ShowChannelEditor = 0
_ShowCSForm = 0
_showText = ['OFF', 'ON']

#display menu
_ShowMenu = 0
_menuItems = []
_chosenItem = 0
_menuItemSelected = _chosenItem
_menuHistory = []
MAXLEVELS = 2
_menuBackText = '<back>'
_ProgressPadLenIdx = 1 

_knownPlugins = {}

_DirtyChannelFlags = 0

HW_CustomEvent_ShiftAlt = 0x20000

lyBanks = 0
lyStrips = 1
_Layouts = ['Banks', 'Strips']

#notes/scales
_ScaleIdx = DEFAULT_SCALE
_ScaleDisplayText = ""
_ScaleNotes = list()
_lastNote =-1
_NoteIdx = DEFAULT_NOTE_NAMES.index(DEFAULT_ROOT_NOTE)
_NoteRepeat = False
_NoteRepeatLengthIdx = BeatLengthsDefaultOffs
_isRepeating = False

_SnapIdx = InitialSnapIndex
_OctaveIdx = OctavesList.index(DEFAULT_OCTAVE)
_ShowChords = False
_ChordNum = -1
_ChordInvert = 0 # 0 = none, 1 = 1st, 2 = 2nd
_ChordTypes = ['Normal', '1st Inv', '2nd Inv']
_Chord7th = False
_VelocityMin = 100
_VelocityMax = 126
_DebugPrn = True
_DebugMin = lvlD
macCloseAll = TnfxMacro("Close All", getShade(cCyan, shDim) )
macTogChanRack = TnfxMacro("Chan Rack", cCyan)
macTogPlaylist = TnfxMacro("Playlist", cCyan)
macTogMixer = TnfxMacro("Mixer", cCyan)
#macPluginInfo = TnfxMacro("Show Plugin", getShade(cYellow, shNorm))
macUndo = TnfxMacro("Undo", getShade(cYellow, shNorm) )
macCopy = TnfxMacro("Copy", getShade(cBlue, shLight))
macCut = TnfxMacro("Cut", getShade(cMagenta, shNorm) )
macPaste = TnfxMacro("Paste", getShade(cGreen, shLight))
_MacroList = [macCloseAll, macTogChanRack, macTogPlaylist, macTogMixer, macUndo, macCopy, macCut, macPaste]
#colMacros = [ cGreen, cCyan, cBlue, cPurple, cRed, cOrange, cYellow, cWhite ]

# list of notes that are mapped to pads
_NoteMap = list()
_NoteMapDict = {}
#_FPCNotesDict = {}


_SongLen  = -1
_ScrollTo = True # used to determine when to scroll to the channel/pattern

#endregion 

#region FL MIDI API Events
def OnInit():
    global _ScrollTo 

    _ScrollTo = True
    ClearAllPads()

    # Refresh the control button states        
    # Initialize Some lights
    RefreshKnobMode()       # Top Knobs operting mode

    #  turn off top buttons: the Pat Up/Dn, browser and Grid Nav buttons
    SendCC(IDPatternUp, SingleColorOff)
    SendCC(IDPatternDown, SingleColorOff)
    SendCC(IDBankL, SingleColorOff)
    SendCC(IDBankR, SingleColorOff)
    SendCC(IDBrowser, SingleColorOff)    

    InititalizePadModes()

    RefreshPageLights()             # PAD Mutes akak Page
    ResetBeatIndicators()           # 
    RefreshPadModeButtons()
    RefreshShiftAltButtons()
    RefreshTransport()    


    InitDisplay()
    line = '----------------------'
    DisplayText(Font6x8, JustifyCenter, 0, "-={ FIRE-NFX }=-", True)
    DisplayText(Font6x16, JustifyCenter, 1, '+', True)
    DisplayText(Font10x16, JustifyCenter, 2, "Version 2.0", True)
    #fun "animation"
    for i in range(16):
        text = line[0:i]
        DisplayText(Font6x16, JustifyCenter, 1, text, True)
        time.sleep(.05)

    # Init some data
    RefreshAll()
    _ScrollTo = False  

_shuttingDown = False
def OnDeInit():
    
    global _shuttingDown
    _shuttingDown = True
    
    DisplayTextAll(' ', ' ', ' ')    
    DeInitDisplay()

    # turn of the lights and go to bed...
    ClearAllPads()
    SendCC(IDKnobModeLEDArray, 16)
    for ctrlID in getNonPadLightCtrls():
        SendCC(ctrlID, 0)
    


def ClearAllPads():
    # clear the Pads
    for pad in range(0,64):
        SetPadColor(pad, 0x000000, 0)
    
def OnDoFullRefresh():
    RefreshAll() 

def OnIdle():
    if(_shuttingDown):
        return 

    #if(_ShiftHeld):
    #    RefreshShiftedStates() 
   
    # no event I know of to hook into song length change so I'll check here
    if(_PadMode.Mode == MODE_PERFORM) and (_isAltMode):
        CheckAndHandleSongLenChanged()

    if(transport.isPlaying() or transport.isRecording()):
        if(_PadMode.Mode in [MODE_DRUM, MODE_NOTE]):
            HandleShowNotesOnPlayback()

def HandleShowNotesOnPlayback():
    global _PadMode
    global  _lastNote
    if(DEFAULT_SHOW_PLAYBACK_NOTES): # this is note playback, make true to enable
        if (_PadMode.Mode in [MODE_DRUM, MODE_NOTE]):
            note = channels.getCurrentStepParam(getCurrChanIdx(), mixer.getSongStepPos(), pPitch)
            if(_lastNote != note):
                ShowNote(_lastNote, False)
                if(note > -1) and (note in _NoteMap):
                    ShowNote(note, True)
                _lastNote = note

def CheckAndHandleSongLenChanged():
    global _lastNote
    global _SongLen
    currSongLen = transport.getSongLength(SONGLENGTH_BARS)
    if(currSongLen != _SongLen): # song length has changed
        UpdateMarkerMap()
        UpdateProgressMap(True)
    _SongLen = currSongLen
    RefreshProgress()
    
def OnMidiMsg(event):
    if(event.data1 in KnobCtrls) and (_KnobMode in [KM_USER1, KM_USER2]): # user defined knobs
        # this code from the original script with slight modification:
        data2 = event.data2
        event.inEv = event.data2
        if event.inEv >= 0x40:
            event.outEv = event.inEv - 0x80
        else:
            event.outEv = event.inEv
        event.isIncrement = 1

        event.handled = False # user modes, free
        event.data1 += (_KnobMode-KM_USER1) * 4 # so the CC is different for each user mode
        device.processMIDICC(event)
        
        if (general.getVersion() > 9):
            BaseID = EncodeRemoteControlID(device.getPortNumber(), 0, 0)
            eventId = device.findEventID(BaseID + event.data1, 0)
            if eventId != 2147483647:
                s = device.getLinkedParamName(eventId)
                s2 = device.getLinkedValueString(eventId)
                DisplayTextAll(s, s2, '')        

def OnUpdateBeatIndicator(value):
    global _Beat
    if(not transport.isPlaying()):
        RefreshTransport()
        ResetBeatIndicators()
        return
    
    if(value == 0):
        SendCC(IDPlay, IDColPlayOn)
    elif(value == 1):
        SendCC(IDPlay, IDColPlayOnBar)
        _Beat = 0
    elif(value == 2):
        SendCC(IDPlay, IDColPlayOnBeat)
        _Beat += 1

    if _Beat > len(BeatIndicators):
        _Beat = 0

    isLastBar = transport.getSongPos(SONGLENGTH_BARS) == transport.getSongLength(SONGLENGTH_BARS)

    for i in range(0, len(BeatIndicators) ):
        
        if(_Beat >= i):
            if(isLastBar):
                SendCC(BeatIndicators[i], SingleColorHalfBright) # red
            else:
                SendCC(BeatIndicators[i], SingleColorFull) # green
        else:
            SendCC(BeatIndicators[i], SingleColorOff)

def OnDirtyChannel(chan, flags):
    global _DirtyChannelFlags
    # Called on channel rack channel(s) change, 
    # 'index' indicates channel that changed or -1 when all channels changed
    # NOTE PER DOCS: 
    #     collect info about 'dirty' channels here but do not handle channels(s) refresh, 
    #     wait for OnRefresh event with HW_ChannelEvent flag    
    #
    # CE_New	0	new channel is added
    # CE_Delete	1	channel deleted
    # CE_Replace	2	channel replaced
    # CE_Rename	3	channel renamed
    # CE_Select	4	channel selection changed    
    _DirtyChannelFlags = flags

def OnRefresh(flags):
    if(flags == HW_CustomEvent_ShiftAlt):
        # called by HandleShiftAlt
        RefreshShiftAltButtons()
        if(_ShiftHeld):
            RefreshShiftedStates() 
        else:
            RefreshPadModeButtons()
            RefreshTransport()            
        return # no more processing needed.
    
    if(HW_Dirty_LEDs & flags):
        RefreshTransport()
        UpdateWindowStates()
    elif(HW_Dirty_FocusedWindow & flags):
        UpdateWindowStates()

    if(HW_Dirty_Performance & flags): # called when new channels or patterns added
        RefreshChannelStrip()
        RefreshPatternStrip()
        
    if(HW_Dirty_Patterns & flags):
        CloseBrowser()
        HandlePatternChanges()
    if(HW_Dirty_ChannelRackGroup & flags):
        HandleChannelGroupChanges()    
    if(HW_ChannelEvent & flags):
        # _DirtyChannelFlags should have the specific CE_xxxx flags if needed
        # https://www.image-line.com/fl-studio-learning/fl-studio-online-manual/html/midi_scripting.htm#OnDirtyChannelFlag
        CloseBrowser()
        UpdateChannelMap()  
        if (_PadMode.Mode == MODE_DRUM):
            RefreshDrumPads()
        elif(_PadMode.Mode == MODE_PATTERNS):
            scrollTo = _CurrentChannel != channels.channelNumber()
            RefreshChannelStrip(scrollTo)
        elif(_PadMode.Mode == MODE_NOTE):
            RefreshNotes()

    if(HW_Dirty_Colors & flags):
        if (_PadMode.Mode == MODE_DRUM):
            RefreshDrumPads()
        elif(_PadMode.Mode == MODE_PATTERNS):
            RefreshChannelStrip()
    if(HW_Dirty_Tracks & flags):
        if(_PadMode.Mode == MODE_PERFORM):
            UpdatePlaylistMap(_isAltMode)
            RefreshPlaylist()
    if(HW_Dirty_Mixer_Sel & flags):
        pass

def OnProjectLoad(status):
    # status = 0 = starting load?
    if(status == 0):
        DisplayTextAll('Project Loading', '-', 'Please Wait...')
    if(status >= 100): #finished loading
        SetPadMode()
        #UpdateMarkerMap()
        RefreshPadModeButtons()        
        UpdatePatternModeData()
        RefreshAll()

def OnSendTempMsg(msg, duration):
    #print('TempMsg', msg, duration)
    pass

def isKnownPlugin():
    return getCurrChanPluginID() in _knownPlugins.keys()

def OnMidiIn(event):
    global _ShiftHeld
    global _AltHeld
    global _PadMap
    
    ctrlID = event.data1 # the low level hardware id of a button, knob, pad, etc
    # handle shift/alt
    if(ctrlID in [IDAlt, IDShift]):
        HandleShiftAlt(event, ctrlID)
        event.handled = True
        return

    if(ctrlID in KnobCtrls) and (_KnobMode in [KM_USER1, KM_USER2]):
        if (event.status in [MIDI_NOTEON, MIDI_NOTEOFF]): # to prevent the mere touching of the knob generating a midi note event.
            event.handled = True
        
        # check if we have predefined user knob settings, if NOT shortcut out 
        # to be processed by OnMidiMsg() to use processMIDICC per the docs
        pName, plugin = getCurrentChannelPlugin()
        if(plugin == None): # invalid plugin
            return

        hasParams = False
        if(_KnobMode == KM_USER1):
            hasParams = len( [a for a in plugin.User1Knobs if a.Offset > -1]) > 0
        elif(_KnobMode == KM_USER2):
            hasParams = len( [a for a in plugin.User2Knobs if a.Offset > -1]) > 0

        if(not hasParams):
            return

    # handle a pad
    if( IDPadFirst <=  ctrlID <= IDPadLast):
        padNum = ctrlID - IDPadFirst
        pMap = _PadMap[padNum]

        cMap = getColorMap()
        col = cMap[padNum].PadColor
        if (col == cOff):
            col = DEFAULT_PAD_PRESSED_COLOR

        if(event.data2 > 0): # pressed
            pMap.Pressed = 1
            SetPadColor(padNum, col, dimBright, False) # False will not save the color to the _ColorMap
            #AnimOff(padNum, col, 255, 0)
        else: #released
            pMap.Pressed = 0
            #AnimOn(padNum, col, 255, 0)
            SetPadColor(padNum, -1, dimDefault) # -1 will rever to the _ColorMap color

        #PROGRESS BAR
        if(_isAltMode):
            if(_PadMode.Mode == MODE_PERFORM):
                if(padNum in pdProgress) and (pMap.Pressed == 1):
                    event.handled = HandleProgressBar(padNum)
                    return 

        padsToHandle = pdWorkArea
        if(isNoNav()):
            padsToHandle = pdAllPads
        
        #if(padNum in pdWorkArea):
        if(padNum in padsToHandle):
            if(_PadMode.Mode == MODE_DRUM): # handles on and off for PADS
                event.handled = HandlePads(event, padNum, pMap)
                return 
            elif(_PadMode.Mode == MODE_NOTE): # handles on and off for NOTES
                event.handled = HandlePads(event, padNum, pMap)
                return 
            elif(_PadMode.Mode == MODE_PERFORM): # handles on and off for PERFORMANCE
                if(pMap.Pressed == 1):
                    event.handled = HandlePlaylist(event, padNum)
                else:
                    event.handled = True 
                return 
            elif(_PadMode.Mode == MODE_PATTERNS): # if STEP/PATTERN mode, treat as controls and not notes...
                if(pMap.Pressed == 1): # On Pressed
                    event.handled = HandlePads(event, padNum, pMap)
                    return 
                else:
                    event.handled = True #prevents a note off message
                    return 

        # always handle macros
        if(padNum in pdMacros) and (pMap.Pressed): 
            event.handled = HandleMacros(pdMacros.index(padNum))
            RefreshMacros()
            return 

        # always handle nav
        if(padNum in pdNav) and (pMap.Pressed): 
            event.handled = HandleNav(padNum)
            return 


    # handle other "non" Pads
    # here we will get a message for on (press) and off (release), so we need to
    # determine where it's best to handle. For example, the play button should trigger 
    # immediately on press and ignore on release, so we code it that way
    if(event.data2 > 0) and (not event.handled): # Pressed
        if(_ShiftHeld):
            HandleShifted(event)

        if( ctrlID in PadModeCtrls):
            event.handled = HandlePadMode(event) 
        elif( ctrlID in TransportCtrls ):
            event.handled = HandleTransport(event)
        elif( ctrlID in PageCtrls): # defined as [IDMute1, IDMute2, IDMute3, IDMute4]
            event.handled = HandlePage(event, ctrlID)  
        elif( ctrlID == KnobModeCtrlID):
            event.handled = HandleKnobMode()
        elif( ctrlID in KnobCtrls):
            event.handled = HandleKnob(event, ctrlID)
        elif( ctrlID in PattUpDnCtrls):
            event.handled = HandlePattUpDn(ctrlID)
        elif( ctrlID in GridLRCtrls):
            event.handled = HandleGridLR(ctrlID)
        elif( ctrlID == IDBrowser ):
            event.handled = HandleBrowserButton()
        elif(ctrlID in SelectWheelCtrls):
            event.handled = HandleSelectWheel(event, ctrlID)
    else: # Released
        event.handled = True 

def OnNoteOn(event):
    #prn(lvlA, 'OnNoteOn()', utils.GetNoteName(event.data1),event.data1,event.data2)
    pass

def OnNoteOff(event):
    #prn(lvlA, 'OnNoteOff()', utils.GetNoteName(event.data1),event.data1,event.data2)
    pass

#endregion 

#region Handlers
def HandleChannelStrip(padNum): #, isChannelStripB):
    global _PatternMap
    global _ChannelMap
    global _CurrentChannel 
    global _PreviousChannel
    global _ChannelCount

    prevChanIdx = getCurrChanIdx() # channels.channelNumber()
    pageOffset = getChannelOffsetFromPage()
    padOffset = 0

    chanApads, chanBPads = getChannelPads()

    if(padNum in chanApads):
        padOffset = chanApads.index(padNum)
        isChannelStripB = False
    elif(padNum in chanBPads):
        padOffset = chanBPads.index(padNum)
        isChannelStripB = True

    chanIdx = padOffset + pageOffset
    channelMap = getChannelMap()
    channel = TnfxChannel(-1, "")
    if(chanIdx < len(channelMap) ):
        channel = channelMap[chanIdx]

    newChanIdx = channel.FLIndex # pMap.FLIndex
    newMixerIdx = channel.Mixer.FLIndex
    if (newChanIdx > -1): #is it a valid chan number?
        if(_ShiftHeld): # we do the mutes when SHIFTed
            if(_KnobMode == KM_MIXER):
                mixer.muteTrack(newMixerIdx)
                ui.miDisplayRect(newMixerIdx, newMixerIdx, _rectTime, CR_ScrollToView)
                RefreshChannelStrip(False)
            else:
                channels.muteChannel(newChanIdx)
                ui.crDisplayRect(0, newChanIdx, 0, 1, _rectTime, CR_ScrollToView + CR_HighlightChannelMute) # CR_HighlightChannels + 
                RefreshChannelStrip(False)
        else: 
            #not SHIFTed
            if(newChanIdx == prevChanIdx): # if it's already on the channel, toggle the windows
                if (isChannelStripB):
                    ShowPianoRoll(-1, True) 
                else:
                    ShowChannelEditor(-1, True) 
            else: #'new' channel, close the previous windows first
                SelectAndShowChannel(newChanIdx)

    _CurrentChannel = getCurrChanIdx() # channels.channelNumber()
    _ChannelCount = channels.channelCount()

    RefreshDisplay()
    return True

def SelectAndShowChannel(newChanIdx, keepPRopen = True):
    global _CurrentChannel
    global _ShowCSForm
    global _ShowChannelEditor
    global _ShowPianoRoll

    oldChanIdx = getCurrChanIdx()

    if(newChanIdx < 0) or (oldChanIdx < 0):
        return

    channels.selectOneChannel(newChanIdx)
    _CurrentChannel = newChanIdx
    
    if( oldChanIdx != newChanIdx):
        _ShowChannelEditor = False
        _ShowCSForm = False
        #channels.deselectAll()

        #close previous windows
        channels.showEditor(oldChanIdx, 0)   
        channels.showCSForm(oldChanIdx, 0)
        UpdateWindowStates()

        if(ui.getVisible(widPianoRoll)): #closes previous instance
            #if(keepPRopen == False):
            #    ShowPianoRoll(0, True)
            ShowPianoRoll(1, True, False, newChanIdx)

    if(not _ShiftHeld):
        mixerTrk = channels.getTargetFxTrack(newChanIdx)
        mixer.setTrackNumber(mixerTrk, curfxScrollToMakeVisible)
        ui.crDisplayRect(0, newChanIdx, 0, 1, _rectTime, CR_ScrollToView + CR_HighlightChannels)
        ui.miDisplayRect(mixerTrk, mixerTrk, _rectTime, CR_ScrollToView)

def HandlePatternStripOld(padNum):
    global _PatternMap
    global _CurrentPattern

    prevPattNum = patterns.patternNumber()
    pMap = _PadMap[padNum]
    newPatNum = pMap.FLIndex

    if (newPatNum > 0): #is it a valid pattern number?
        if(newPatNum == prevPattNum): # if it's already on the pattern, toggle the windows
            if (padNum in pdPatternStripB):
                ShowPianoRoll(-1, True) 
            else:
                ShowChannelEditor(-1, True) 
        else: #'new' channel, close the previous windows first
            UpdateWindowStates()
            if (_ShowPianoRoll):
                ShowPianoRoll(0, True)
            if(_ShowCSForm):
                ShowChannelSettings(0, True)
            if(_ShowChannelEditor):
                ShowChannelEditor(0, True)            
            patterns.deselectAll()
            patterns.jumpToPattern(newPatNum)

    #RefreshPatterns(_CurrentPattern)
    _CurrentChannel = getCurrChanIdx() # channels.channelNumber()
    _ChannelCount = channels.channelCount()
    RefreshDisplay()
    return True

def HandlePlaylist(event, padNum):
    flIdx = _PadMap[padNum]

    if(padNum in pdPlaylistStripA):       
        flIdx = _PadMap[padNum].FLIndex
        playlist.selectTrack(flIdx)
    if(padNum in pdPlaylistMutesA):
        flIdx = _PadMap[padNum].FLIndex
        playlist.muteTrack(flIdx)

    if(not _isAltMode):
        if(padNum in pdPlaylistStripB):       
            flIdx = _PadMap[padNum].FLIndex
            playlist.selectTrack(flIdx)
        if(padNum in pdPlaylistMutesB):
            flIdx = _PadMap[padNum].FLIndex
            playlist.muteTrack(flIdx)
    
    UpdatePlaylistMap(_isAltMode)
    RefreshPlaylist()
    return True

def HandleProgressBar(padNum):
    padOffs = pdProgress.index(padNum)
    prgMap = _ProgressMapSong[padOffs]
    # ABS Ticks
    if(_ProgressPadLenIdx == 0):
        newSongPos = _ProgressMapSong[padOffs].SongPosAbsTicks
        transport.setSongPos(newSongPos, SONGLENGTH_ABSTICKS)
    else:
        # bar number
        newSongPos = getAbsTicksFromBar(prgMap.BarNumber) 
        transport.setSongPos(newSongPos, SONGLENGTH_ABSTICKS)

    if(_AltHeld):
        markerOffs = padOffs + 1
        arrangement.addAutoTimeMarker(prgMap.SongPosAbsTicks, DEFAULT_MARKER_PREFIX_TEXT + str(markerOffs))

    if(_ShiftHeld):
        #prn(lvlA, '', 'Selecting bars..')    
        pass        
        
    RefreshAllProgressAndMarkers()

    return True

def HandlePads(event, padNum, pMap):  
    # 'perfomance'  pads will need a pressed AND release...
    if(_PadMode.Mode == MODE_DRUM):
        if (padNum in DrumPads()):
            return HandleDrums(event, padNum)
    elif(_PadMode.Mode == MODE_NOTE):
        if(padNum in pdWorkArea):
            return HandleNotes(event, padNum)
        

    # some pads we only need on pressed event
    if(event.data2 > 0): # On Pressed

        # macros are handled in OnMidiIn

        #mode specific
        if(_PadMode.Mode == MODE_NOTE):
            if(padNum in pdNav):
                HandleNav(padNum)
        if(_PadMode.Mode == MODE_DRUM):
            if(padNum in pdFPCChannels):
                HandleDrums(event, padNum)
        elif(_PadMode.Mode == MODE_PATTERNS):
            apads, bpads = getPatternPads()
            chanapads, chanbpads = getChannelPads()
            if(padNum in apads): # was in pdPatternStripA
                if(_AltHeld):
                    CopyPattern(pMap.FLIndex)
                else:
                    event.handled = HandlePatternStrip(padNum)
            elif(padNum in bpads):
                event.handled = HandlePatternStrip(padNum)
            elif(padNum in chanapads):
                event.handled = HandleChannelStrip(padNum) #, False)   
            elif(padNum in chanbpads):
                event.handled = HandleChannelStrip(padNum) #, True)


    return True

def HandleNav(padIdx):
    global _NoteRepeat
    global _SnapIdx
    hChanPads = _PadMode.NavSet.ChanNav
    hPresetNav = _PadMode.NavSet.PresetNav
    hUDLR = _PadMode.NavSet.UDLRNav
    hSnapNav = _PadMode.NavSet.SnapNav
    hNoteRepeat = _PadMode.NavSet.NoteRepeat
    hScaleNav = _PadMode.NavSet.ScaleNav
    hOctaveNav = _PadMode.NavSet.OctaveNav 
    hLayoutNav = _PadMode.NavSet.LayoutNav

    #if(_PadMode.Mode == MODE_PERFORM): # not used by this mode
    #    return

    if(hChanPads):
        if(padIdx in pdShowChanPads):
            if(padIdx == pdShowChanEditor):
                ShowChannelEditor(-1, True)
            elif(padIdx == pdShowChanPianoRoll):
                ShowPianoRoll(-1, True)

    if(hPresetNav):
        if(padIdx in pdPresetNav):
            ShowChannelEditor(1, True)
            if(padIdx == pdPresetPrev):
                ui.previous()
            elif(padIdx == pdPresetNext):
                ui.next()

    if(hSnapNav):
        if(padIdx in pdSnapNav):
            HandleSnapNav(padIdx)
    elif(hLayoutNav):
        if(padIdx == pdLayoutPrev):
            NavLayout(-1)
        elif(padIdx == pdLayoutNext):
            NavLayout(1)

    if(hNoteRepeat):
        if(padIdx == pdNoteRepeatLength):
            NavNoteRepeatLength(1)
        if(padIdx == pdNoteRepeat):
            ToggleRepeat()

    if(hUDLR):
        if(padIdx in pdUDLR):
            HandleUDLR(padIdx)

    if(hOctaveNav) or (hScaleNav):
        if(padIdx == pdOctaveNext):
            NavOctavesList(-1)
        elif(padIdx == pdOctavePrev):
            NavOctavesList(1)
        if(hScaleNav):
            if(padIdx == pdScaleNext):
                NavScalesList(1)
            elif(padIdx == pdScalePrev):
                NavScalesList(-1)
            elif(padIdx == pdRootNoteNext):
                NavNotesList(-1)
            elif(padIdx == pdRootNotePrev):
                NavNotesList(1)         

    if(_PadMode.Mode == MODE_NOTE):
        RefreshNotes()
    elif(_PadMode.Mode == MODE_DRUM):
        RefreshDrumPads()
    RefreshNavPads()
    
    return True 

def ToggleRepeat():
    global _NoteRepeat
    _NoteRepeat = not _NoteRepeat
    DisplayTimedText('Note Rpt: ' + _showText[_NoteRepeat])
    if(_isRepeating):
        device.stopRepeatMidiEvent()

def HandleSnapNav(padIdx):
    if(padIdx == pdSnapUp):
        ui.snapMode(-1)  # dec by 1
    else:
        ui.snapMode(1)  # inc by 1
    _SnapIdx = SnapModesList.index(ui.getSnapMode())
    DisplaySnap(_SnapIdx)

def DisplaySnap(_SnapIdx):
    DisplayTextTop('Snap:')
    DisplayTimedText(SnapModesText[_SnapIdx])

def HandleMacros(macIdx):

    if(_PadMode.NavSet.MacroNav == False):
        return 
    
    #if(_PadMode.Mode == MODE_PERFORM): # not used by this mode
    #    return

    chanNum = channels.selectedChannel(0, 0, 0)
    macro = _MacroList[macIdx]

    if(macIdx == 4):
        general.undoUp()
    elif(macIdx == 1):
        ShowChannelRack(-1)        
    elif(macIdx == 2):
        ShowPlaylist(-1)
    elif(macIdx == 3):
        ShowMixer(-1)        
    elif(macIdx == 0):
        DisplayTimedText('Reset Windows')
        transport.globalTransport(FPT_F12, 1)  # close all...
        # enable the following lines to have it re-open windows 
        if(DEFAULT_REOPEN_WINDOWS_AFTER_CLOSE_ALL):
            #ShowBrowser(1)
            ShowMixer(1)
            ShowChannelRack(1)
            ShowPlaylist(1)
        #else:
        #    ShowMixer(0)
            ShowChannelRack(0)
        #    ShowPlaylist(0)

    elif(macIdx == 5):
        DisplayTimedText('Copy')
        ui.copy()
    elif(macIdx == 6):
        DisplayTimedText('Cut')
        ui.cut()
    elif(macIdx == 7):
        DisplayTimedText('Paste')
        ui.paste()
    else:
        return False 

    return True 
def HandleNotes(event, padNum):
    global _ChordInvert
    global _Chord7th
    global _isRepeating

    event.data1 = _PadMap[padNum].NoteInfo.MIDINote

    if(0 < event.data2 < _VelocityMin):
        event.data2 = _VelocityMin
    elif(event.data2 > _VelocityMin):
        event.data2 = _VelocityMax

    
    if(_ShowChords):
        if (padNum in pdChordBar):
            chordNum = pdChordBar.index(padNum)+1
            noteOn = (event.data2 > 0)
            noteVelocity = event.data2
            chan = getCurrChanIdx() # channels.channelNumber()
            HandleChord(chan, chordNum, noteOn, noteVelocity, _Chord7th, _ChordInvert)
            return True
        elif(padNum in pdChordFuncs) and (event.data2 > 0):
            chordType = '' # normal
            if (padNum == pd7th): 
                _Chord7th = not _Chord7th
                if(_Chord7th):
                    chordType += '7th'
            elif(padNum == pdInv1):
                _ChordInvert = 1 
                chordType += ' 1st Inv'
            elif(padNum == pdInv2):
                _ChordInvert = 2
                chordType += ' 2nd Inv'
            elif(padNum == pdNormal): 
                _ChordInvert = 0
            
            RefreshNotes()
            DisplayTimedText(chordType)
            return True 

    return False # to continue processing regular notes

def HandleDrums(event, padNum):
    global _isRepeating
    # even out some velocities
    if(90 > event.data2 > 1 ):
        event.data2 = 90
    elif(110 > event.data2 > 64):
        event.data2 = 110
    elif(event.data2 > 110):
        event.data2 = 120

    # do the note repeat BEFORE changing the note so the note is retriggered properly
    if(_NoteRepeat):
        if(event.data2 < 32): # min velocity is 32, so anything below that s/b note off
            device.stopRepeatMidiEvent()
            _isRepeating = False
        elif(not _isRepeating):
            ms = getBeatLenInMS(BeatLengthDivs[_NoteRepeatLengthIdx])
            snap = BeatLengthSnap[_NoteRepeatLengthIdx]
            setSnapMode(snap)
            device.repeatMidiEvent(event, ms, ms)
            _isRepeating = True
    
    # FPC Quick select
    if(not _isAltMode) and (padNum in pdFPCChannels):
        chanNum = _PadMap[padNum].ItemIndex
        if(chanNum > -1): # it's an FPC quick select
            SelectAndShowChannel(chanNum)
            ShowChannelEditor(1, False)
            RefreshDisplay()

    #shoudl return the pads list
    pads = DrumPads() 

    if(padNum in pads):
        event.data1 = _PadMap[padNum].NoteInfo.MIDINote
        return False
    else:
        return True # mark as handled to prevent processing

def getChannelMap():
    channelMap = _ChannelMap
    #if(_isAltMode):
    #    channelMap = _ChannelSelectedMap
    return channelMap

def getPatternMap():
    patternMap = _PatternMap
    if(_isAltMode):
        patternMap = _PatternSelectedMap
    return patternMap

def HandlePatternStrip(padNum):
    global _PatternMap
    global _PatternSelectedMap
    patternMap = getPatternMap()
    pattIdx = -1
    pattOffset = getPatternOffsetFromPage()
    patternStripA, patternStripB = getPatternPads()


    if(padNum in patternStripA):
        pattIdx = patternStripA.index(padNum)
    elif(padNum in patternStripB):
        pattIdx = patternStripB.index(padNum)
    pattNum = -1

    if( len(patternMap) >= pattIdx + pattOffset + 1):
        pattNum = patternMap[pattIdx + pattOffset].FLIndex
    else:
        return True # nothing else to do


    if(patterns.patternNumber() != pattNum): # patt.FLIndex):
        if(padNum in patternStripA):
            patterns.jumpToPattern(pattNum)
        else:
            if(_isAltMode):
                patterns.jumpToPattern(pattNum)
            else:
                if(patterns.isPatternSelected(pattNum)):
                    patterns.selectPattern(pattNum, 0)
                else:
                    patterns.selectPattern(pattNum, 1)
            UpdatePatternModeData()                
            RefreshPatternStrip()

    return True 

def HandleChannelGroupChanges():
    UpdatePatternModeData()
    RefreshAll()    

def CloseBrowser():
    if(_ShowMenu):
        HandleBrowserButton()

def HandlePatternChanges():
    global _PatternCount
    global _CurrentPattern
    global _CurrentPage 

    if (_PatternCount > 0) and (_PadMode.Mode == MODE_PATTERNS): # do pattern mode
        
        if(_PatternCount != patterns.patternCount()):
            _PatternCount = patterns.patternCount()
            UpdatePatternModeData() 
            RefreshPatternStrip()

        else:
            if _CurrentPattern != patterns.patternNumber():
                UpdatePatternModeData(patterns.patternNumber()) 
                RefreshPatternStrip(True)
            else:
                UpdatePatternModeData() 
                RefreshPatternStrip()

        _CurrentPattern = patterns.patternNumber()
        
        

    if(patterns.patternCount() == 0) and (_CurrentPattern == 1): # empty project, set to 1
        _PatternCount = 1

    RefreshDisplay()

def HandlePattUpDn(ctrlID):
    moveby = 1
    if(ctrlID == IDPatternUp):
        moveby = -1

    if(_ShiftHeld):
        newChanIdx = getCurrChanIdx() + moveby
        if(0 <= newChanIdx < _ChannelCount):
            SelectAndShowChannel(newChanIdx) 
    elif(_AltHeld):
        if(ctrlID == IDPatternUp):
            DisplayTimedText('vZoom Out')
            ui.verZoom(2)
            SetTop()
        else:
            DisplayTimedText('vZoom In')
            ui.verZoom(-2)
            SetTop()
    else:
        newPattern = patterns.patternNumber() + moveby
        if( 0 <= newPattern <= patterns.patternCount()):   #if it's a valid spot then move it
            patterns.jumpToPattern(newPattern)
    
    RefreshDisplay()
    RefreshNavPads()

    return True 

def HandleGridLR(ctrlID):
    global _ScrollTo

    if(_AltHeld):
        if(ctrlID == IDBankL):
            DisplayTimedText('hZoom Out')
            ui.horZoom(2)
            SetTop()
        else:
            DisplayTimedText('hZoom In')
            ui.horZoom(-2)
            SetTop()
    else:
        if(ctrlID == IDBankL):
            NavSetList(-1)
        elif(ctrlID == IDBankR):
            NavSetList(1)
        _ScrollTo = True
        RefreshModes()
    return True

def HandleKnobMode():
    NextKnobMode()
    RefreshDisplay()
    return True

def HandleKnob(event, ctrlID, useparam = None):
    if(event.isIncrement != 1):
        event.inEv = event.data2
        if event.inEv >= 0x40:
            event.outEv = event.inEv - 0x80
        else:
            event.outEv = event.inEv
        event.isIncrement = 1

    value = event.outEv

    chanNum = getCurrChanIdx() #  channels.channelNumber()



    if(ctrlID == IDSelect) and (useparam != None): # tweaking via Select Knob
        recEventID = channels.getRecEventId(getCurrChanIdx()) + REC_Chan_Plugin_First
        knobres = 1/32
        if (useparam.StepsAfterZero > 0):
            knobres = 1/useparam.StepsAfterZero
        if(_ShiftHeld):
            knobres = 1/128
        elif(_AltHeld):
            knobres = 1/8
        return HandleKnobReal(recEventID + useparam.Offset,  event.outEv, useparam.Caption + ': ', useparam.Bipolar, 0, knobres)


    if _KnobMode == KM_CHANNEL :
        recEventID = channels.getRecEventId(chanNum)
        if chanNum > -1: # -1 is none selected
            # check if a pad is being held for the FPC params
            pMapPressed = next((x for x in _PadMap if x.Pressed == 1), None) 
            heldPadIdx = -1
            chanName = channels.getChannelName(chanNum)

            if(pMapPressed != None):
                if(pMapPressed.PadIndex in pdFPCA):
                    heldPadIdx = pdFPCA.index(pMapPressed.PadIndex)
                elif(pMapPressed.PadIndex in pdFPCB):
                    heldPadIdx = pdFPCB.index(pMapPressed.PadIndex) + 64 # internal offset for FPC Params Bank B

            if ctrlID == IDKnob1:
                if(_PadMode.Mode == MODE_DRUM) and (heldPadIdx > -1) and (isFPCActive()):
                    return HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Volume.Offset + heldPadIdx, event.outEv, ppFPC_Volume.Caption, ppFPC_Volume.Bipolar)
                else:
                    ui.crDisplayRect(0, chanNum, 0, 1, 10000, CR_ScrollToView + CR_HighlightChannelPanVol)
                    return HandleKnobReal(recEventID + REC_Chan_Vol,  value, 'Ch Vol: ' + chanName, False)
                    

            elif ctrlID == IDKnob2:
                if(_PadMode.Mode == MODE_DRUM) and (heldPadIdx > -1) and (isFPCActive()):
                    return HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Pan.Offset + heldPadIdx, event.outEv, ppFPC_Pan.Caption, ppFPC_Pan.Bipolar)
                else:
                    ui.crDisplayRect(0, chanNum, 0, 1, 10000, CR_ScrollToView + CR_HighlightChannelPanVol)
                    return HandleKnobReal(recEventID + REC_Chan_Pan, value, 'Ch Pan: ' + chanName, True)

            elif ctrlID == IDKnob3:
                if(_PadMode.Mode == MODE_DRUM) and (heldPadIdx > -1) and (isFPCActive()):
                    return HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Tune.Offset + heldPadIdx, event.outEv, ppFPC_Tune.Caption, ppFPC_Tune.Bipolar)
                else:
                    return HandleKnobReal(recEventID + REC_Chan_FCut, value, 'Ch Flt: ' + chanName, False)

            elif ctrlID == IDKnob4:
                return HandleKnobReal(recEventID + REC_Chan_FRes, value, 'Ch Res: ' + chanName, False)

            else:
                return True 
    elif _KnobMode == KM_MIXER :
        mixerNum = mixer.trackNumber()
        mixerName = mixer.getTrackName(mixerNum) 
        recEventID = mixer.getTrackPluginId(mixerNum, 0)
        if not ((mixerNum < 0) | (mixerNum >= mixer.getTrackInfo(TN_Sel)) ): # is one selected?
            if ctrlID == IDKnob1:
                return HandleKnobReal(recEventID + REC_Mixer_Vol,  value, 'Mx Vol: ' + mixerName , False)
            elif ctrlID == IDKnob2:
                return HandleKnobReal(recEventID + REC_Mixer_Pan,  value, 'Mx Pan: '+ mixerName, True)
            elif ctrlID == IDKnob3:
                return HandleKnobReal(recEventID + REC_Mixer_EQ_Gain,  value, 'Mx EQLo: '+ mixerName, True)
            elif ctrlID == IDKnob4:
                return HandleKnobReal(recEventID + REC_Mixer_EQ_Gain + 2,  value, 'Mix EQHi: '+ mixerName, True)
    elif(isKnownPlugin()):
        knobParam = None
        recEventID = channels.getRecEventId(getCurrChanIdx()) + REC_Chan_Plugin_First
        pluginName, plugin = getCurrentChannelPlugin()
        if(plugin == None): # invalid plugin
            return True

        knobOffs = ctrlID - IDKnob1
        if(_KnobMode == KM_USER1):
            knobParam = plugin.User1Knobs[knobOffs]
            knobParam.Caption = plugin.User1Knobs[knobOffs].Caption
        if(_KnobMode == KM_USER2):
            knobParam = plugin.User2Knobs[knobOffs]
            knobParam.Caption = plugin.User2Knobs[knobOffs].Caption
        if(  knobParam.Offset > -1  ): # valid offset?
            return HandleKnobReal(recEventID + knobParam.Offset,  event.outEv, knobParam.Caption + ': ', knobParam.Bipolar)
        return True

        # for knob in range(4):
        #     knobID = IDKnob1 + knob
        #     if(ctrlID == knobID):
        #         param = knobParams[knob]
        #         hasParam = param.Offset > -1  # valid offset?
        #         #print('KM2, Has Param:', hasParam, 'knobID', knobID )
        #         if( hasParam ):
        #             #print('KM3', param.Caption, param.Offset)
        #             return HandleKnobReal(recEventID + param.Offset,  event.outEv, param.Caption + ': ', param.Bipolar)
        #             #return HandleKnobReal(recEventID + param.Offset,  value,  param.Caption + ': ',  param.Bipolar, param.StepsAfterZero)
        #             # turn HandleKnobReal(recEventID + REC_Mixer_Vol,  value, 'Mx Vol: ' + mixerName , False)
        #         else:
        #             return True 
    else:  #user modes..
        if (event.status in [MIDI_NOTEON, MIDI_NOTEOFF]):
            event.handled = True
        return True # these knobs will be handled in OnMidiMsg prior to this.


def HandleKnobReal(recEventIDIndex, value, Name, Bipolar, stepsAfterZero = 0, knobres = 1/64):
    #knobres = 1/64
    if(stepsAfterZero > 0):
        knobres = 1/stepsAfterZero
    currVal = device.getLinkedValue(recEventIDIndex)
    #general.processRECEvent(recEventIDIndex, value, REC_MIDIController) #doesnt use knobres
    mixer.automateEvent(recEventIDIndex, value, REC_MIDIController, 0, 1, knobres) 
    currVal = device.getLinkedValue(recEventIDIndex)
    valstr = device.getLinkedValueString(recEventIDIndex)
    DisplayBar2(Name, currVal, valstr, Bipolar)
    return True

def HandlePage(event, ctrlID):
    global _ShowChords
    global _PatternPage
    global _ChannelPage
    global _ProgressPadLenIdx

    #differnt modes use these differently   
    if(_PadMode.Mode == MODE_PATTERNS):
        if(ctrlID == IDPage0): # Pat page 0
            PatternPageNav(-1) #_PatternPage = 1
        elif(ctrlID == IDPage1):
            PatternPageNav(1) #_PatternPage = 2
        elif(ctrlID == IDPage2):
            ChannelPageNav(-1)
        elif(ctrlID == IDPage3):
            ChannelPageNav(1)
        RefreshPageLights()
        RefreshModes()
        #HandlePatternChanges()
        #RefreshPatternPads()
        

    elif(_PadMode.Mode == MODE_NOTE) and (ctrlID == IDPage0): 
        if(_ScaleIdx > 0):
            _ShowChords = not _ShowChords
        else:    
            _ShowChords = False
            # make the mute led turn red
        RefreshNotes()

    elif(_PadMode.Mode == MODE_PERFORM):
        if(_isAltMode):        
            pdLen = len(pdProgress)
            songLen = transport.getSongLength(SONGLENGTH_BARS)
            if(ctrlID == IDPage0):
                _ProgressPadLenIdx = 0 
            elif(ctrlID == IDPage1):
                _ProgressPadLenIdx = 1
            elif(ctrlID == IDPage2):
                _ProgressPadLenIdx = 2
            elif(ctrlID == IDPage3):
                _ProgressPadLenIdx = 3
            RefreshAllProgressAndMarkers()
        
        

    RefreshPageLights()
    RefreshDisplay()
    return True

def RefreshAllProgressAndMarkers():
    UpdateMarkerMap()                
    UpdateProgressMap(False)
    RefreshProgress()

def HandleShiftAlt(event, ctrlID):
    global _ShiftHeld
    global _AltHeld
    
    if(ctrlID == IDShift):
        _ShiftHeld = (event.data2 > 0)
    elif(ctrlID == IDAlt):
        _AltHeld = (event.data2 > 0)

    OnRefresh(HW_CustomEvent_ShiftAlt)
    



def HandlePadMode(event):
    global _isAltMode
    global _isShiftMode
    global _PadMode 

    ctrlID = event.data1 
    newPadMode = _PadMode.Mode

    if(not _AltHeld) and (not _ShiftHeld): #normal pad mode switch
        _isShiftMode = False
        _isAltMode = False
        if(ctrlID == IDStepSeq):
            _PadMode = modePattern
        elif(ctrlID == IDNote):
            _PadMode = modeNote
        elif(ctrlID == IDDrum):
            _PadMode = modeDrum
        elif(ctrlID == IDPerform):
            _PadMode = modePerform
    elif(_AltHeld) and (not _ShiftHeld): # Alt modes
        _isShiftMode = False
        _isAltMode = True 
        if(ctrlID == IDStepSeq):
            _PadMode = modePatternAlt
        if(ctrlID == IDNote):
            _PadMode = modeNoteAlt
        if(ctrlID == IDDrum):
            _PadMode = modeDrumAlt
        if(ctrlID == IDPerform): #force a refresh on the pl tack bar A to clear it
            _PadMode = modePerformAlt
            

    elif(_AltHeld) and (_ShiftHeld): # Shift modes
        _isShiftMode = True 
        _isAltMode = True

    SetPadMode()

    return True
def HandleTransport(event):
    if(event.data1 == IDPatternSong):
        if(_ShiftHeld):
            pass
        else:
            transport.setLoopMode()

    if(event.data1 == IDPlay):
        if(transport.isPlaying()):
            transport.stop()
            ResetBeatIndicators()
        else:
            transport.start()

    if(event.data1 == IDStop):
        transport.stop()
        ResetBeatIndicators()

    if(event.data1 == IDRec):
        transport.record()

    RefreshTransport()
    

    return True 

def HandleShifted(event):
    ctrlID = event.data1
    if(ctrlID == IDAccent):
        pass 
    elif(ctrlID == IDSnap):
        transport.globalTransport(FPT_Snap, 1)
    elif(ctrlID == IDTap):
        transport.globalTransport(FPT_TapTempo, 1)
    elif(ctrlID == IDOverview):
        pass 
    elif(ctrlID == IDMetronome):
        transport.globalTransport(FPT_Metronome, 1)
    elif(ctrlID == IDWait):
        transport.globalTransport(FPT_WaitForInput, 1)
    elif(ctrlID == IDCount):
        transport.globalTransport(FPT_CountDown, 1)
    elif(ctrlID == IDLoop):
        transport.globalTransport(FPT_LoopRecord, 1)
    
    RefreshShiftedStates()
    event.handled = True 

def HandleSelectWheel(event, ctrlID):
    global _menuItemSelected
    global _menuItems
    global _chosenItem

    if(not _ShowMenu):
        if(ctrlID == IDSelectDown):
            HandleBrowserButton()
        return True

    ShowMenuItems()
    jogNext = 1
    jogPrev = 127
    paramName, plugin = getCurrentChannelPlugin()
    if(plugin == None): # invalid plugin
        return True

    if(ctrlID == IDSelectDown):
        _chosenItem = _menuItemSelected
        itemstr = _menuItems[_menuItemSelected]
        if(_menuItems[_menuItemSelected] == _menuBackText) or (len(_menuHistory) == MAXLEVELS):
            _menuItemSelected = _menuHistory.pop()
        else:
            if(len(_menuHistory) < MAXLEVELS): 
                _menuHistory.append(_menuItemSelected) 
                _menuItemSelected = 0

            if(len(_menuHistory) == MAXLEVELS):
                groupName = list(plugin.ParameterGroups.keys())[_menuHistory[0]]
                plugin.TweakableParam = plugin.ParameterGroups[groupName][_chosenItem]

        _chosenItem = _menuItemSelected

        if(len(_menuHistory) == MAXLEVELS) and (plugin.TweakableParam != None):
            return HandleKnob(event, IDSelect, plugin.TweakableParam)
        else:
            ShowMenuItems()
            return True 

                
    
    elif(ctrlID == IDSelect):

        if(len(_menuHistory) == MAXLEVELS) and (plugin.TweakableParam != None):
            return HandleKnob(event, ctrlID, plugin.TweakableParam)

        if(event.data2 == jogNext) and (_menuItemSelected < (len(_menuItems)-1) ):
            _menuItemSelected += 1
            if(_menuItemSelected > len(_menuItems)-1):
                _menuItemSelected = 0
        elif(event.data2 == jogPrev): # and (_menuItemSelected > 0):
            _menuItemSelected += -1
            if(_menuItemSelected < 0):
                _menuItemSelected = len(_menuItems)-1

        ShowMenuItems()
        return True 



def HandleBrowserButton():
    #global _ShowBrowser
    # using to trigger the menu for now
    global _ShowMenu 
    global _menuItems
    global _menuItemSelected
    global _menuHistory

    _ShowMenu = not _ShowMenu
    if(_ShowMenu):
        _menuHistory.clear()
        _menuItemSelected = 0
        SendCC(IDBrowser, DualColorFull2)  #SingleColorHalfBright
        ShowMenuItems()
    else:
        SendCC(IDBrowser, SingleColorOff) 
        RefreshDisplay()
    return True

def HandleChord(chan, chordNum, noteOn, noteVelocity, play7th, playInverted):
    global _ChordNum
    global _ChordInvert
    global _Chord7th
    play7th = _Chord7th
    playInverted = _ChordInvert
    realScaleIdx = ScalesList[_ScaleIdx]

    if (GetScaleNoteCount(realScaleIdx) != 7): #if not enough notes to make full chords, do not do anything
        return 

    chordTypes = ['','m','m','','','m','dim']
    chordName = ''

    note =  -1  #the target root note
    note3 = -1
    note5 = -1
    note7 = -1
    note5inv = -1  
    note3inv = -1  
    offset = 0

    if(0 < chordNum < 8): #if a chord, then use the _ScaleNotes to find the notes
        offset = GetScaleNoteCount(realScaleIdx) + (chordNum-1)
        note = _ScaleNotes[offset]
        note3 = _ScaleNotes[offset + 2]
        note5 = _ScaleNotes[offset + 4]
        note7 = _ScaleNotes[offset + 6]
        note7inv = _ScaleNotes[offset - 1]
        note3inv = _ScaleNotes[offset - 5] 
        note5inv = _ScaleNotes[offset - 3] 
        chordName = NotesList[note % 12]
        chordName += chordTypes[ ((_ScaleIdx + chordNum) % 7)-2 ]

    if(noteOn):
        #
        _ChordNum = chordNum
        chordinv = ''


        if(playInverted == 1):
            chordinv = '1st.Inv'
            PlayMIDINote(chan, note3inv, noteVelocity)
            PlayMIDINote(chan, note5inv, noteVelocity)
            if(play7th):
                chordName += '7 '
                PlayMIDINote(chan, note7inv, noteVelocity)                 
            PlayMIDINote(chan, note, noteVelocity)
        elif(playInverted == 2):
            chordinv = '2nd.Inv'
            PlayMIDINote(chan, note5inv, noteVelocity)
            if(play7th):
                chordName += '7 '
                PlayMIDINote(chan, note7inv, noteVelocity)                 
            PlayMIDINote(chan, note, noteVelocity)
            PlayMIDINote(chan, note3, noteVelocity)
        else:
            PlayMIDINote(chan, note, noteVelocity)
            PlayMIDINote(chan, note3, noteVelocity)
            PlayMIDINote(chan, note5, noteVelocity)
            if(play7th):
                chordName += '7 '
                PlayMIDINote(chan, note7, noteVelocity)                 

        # RefreshNotes()
        RefreshChordType()
        DisplayTimedText2('Chord:',  chordName, chordinv)

    else:
        # turn off the chord
        PlayMIDINote(chan, note3inv, noteVelocity)
        PlayMIDINote(chan, note5inv, noteVelocity)
        PlayMIDINote(chan, note7, noteVelocity)
        PlayMIDINote(chan, note, noteVelocity)
        PlayMIDINote(chan, note3, noteVelocity)
        PlayMIDINote(chan, note5, noteVelocity)

def HandleUDLR(padIndex):
    if(padIndex == pdTab):
        ui.selectWindow(0)
    elif(padIndex == pdShiftTab):
        ui.selectWindow(1)
    elif(padIndex == pdUp):
        ui.up()
    elif(padIndex == pdDown):
        ui.down()
    elif(padIndex == pdLeft):
        ui.left()
    elif(padIndex == pdRight):
        ui.right()
    elif(padIndex == pdEsc):
        ui.escape()
    elif(padIndex == pdEnter):
        ui.enter()
    else:
        return False 
    return True
#endregion 

#region Refresh
def RefreshAll():
    RefreshPageLights()
    RefreshModes()
    RefreshMacros()
    RefreshNavPads()
    RefreshDisplay()
    return 

def RefreshModes():
    global _ScrollTo
    if(_PadMode.Mode == MODE_DRUM):
        RefreshDrumPads()
    elif(_PadMode.Mode == MODE_PATTERNS):
        UpdatePatternModeData(patterns.patternNumber())
        UpdatePatternModeData()
        RefreshPatternStrip(_ScrollTo) 
        RefreshChannelStrip(_ScrollTo)
        _ScrollTo = False
    elif(_PadMode.Mode == MODE_NOTE):
        RefreshNotes()
    elif(_PadMode.Mode == MODE_PERFORM):
        UpdatePlaylistMap(_isAltMode)
        RefreshPlaylist()
        if(_isAltMode):
            UpdateMarkerMap()
            UpdateProgressMap()


         
def RefreshPadModeButtons():
    SendCC(IDStepSeq, DualColorOff)
    SendCC(IDNote, DualColorOff)
    SendCC(IDDrum, DualColorOff)
    SendCC(IDPerform, DualColorOff)



    if(_PadMode.Mode == MODE_PATTERNS):
        SendCC(IDStepSeq, DualColorFull2)
    elif(_PadMode.Mode == MODE_NOTE):
        SendCC(IDNote, DualColorFull2)
    elif(_PadMode.Mode == MODE_DRUM):
        SendCC(IDDrum, DualColorFull2)
    elif(_PadMode.Mode == MODE_PERFORM):
        SendCC(IDPerform, DualColorFull2)

def RefreshShiftAltButtons():
    if(_AltHeld):
        SendCC(IDAlt, SingleColorFull)
    elif(_isAltMode):
        SendCC(IDAlt, SingleColorHalfBright)
    else:
        SendCC(IDAlt, SingleColorOff)

    if(_ShiftHeld):
        RefreshShiftedStates()
        RefreshChannelStrip(False)
    else:  
        SendCC(IDShift, DualColorOff)
        RefreshChannelStrip(False)
        RefreshPadModeButtons()
        RefreshTransport()

def RefreshTransport():
    if(transport.getLoopMode() == SM_Pat):
        SendCC(IDPatternSong, IDColPattMode)
    else:
        SendCC(IDPatternSong, IDColSongMode)

    if(transport.isPlaying()):
        SendCC(IDPlay, IDColPlayOn)
    else:
        SendCC(IDPlay, IDColPlayOff)

    SendCC(IDStop, IDColStopOff)

    if(transport.isRecording()):
        SendCC(IDRec, IDColRecOn)
    else:
        SendCC(IDRec, IDColRecOff)

def RefreshShiftedStates():
    ColOn = DualColorFull2 
    ColOff = DualColorOff

    if(_ShiftHeld):
        SendCC(IDShift, DualColorFull1)
    else:
        SendCC(IDShift, ColOff)

    SendCC(IDAccent, ColOff)
    SendCC(IDSnap, ColOff)
    SendCC(IDTap, ColOff)
    SendCC(IDOverview, ColOff)
    SendCC(IDPatternSong, ColOff)
    SendCC(IDPlay, ColOff)
    SendCC(IDStop, ColOff)
    SendCC(IDRec, ColOff)

    if(ui.getSnapMode() != Snap_None):
        SendCC(IDSnap, ColOn)

    if(ui.isMetronomeEnabled()):
        SendCC(IDPatternSong, ColOn)

    if(ui.isStartOnInputEnabled()):
        SendCC(IDWait, ColOn)

    if(ui.isPrecountEnabled()):
        SendCC(IDCount, ColOn)
    if(ui.isLoopRecEnabled()):
        SendCC(IDLoop, ColOn)

def RefreshPadsFromPadMap():
    for pad in range(0,64):
        SetPadColor(pad, _PadMap[pad].Color, dimDefault) 

def RefreshMacros():
    if isNoMacros():
        return 

    for pad in pdMacros:
        idx = pdMacros.index(pad)
        #color =  colMacros[idx]
        SetPadColor(pad, _MacroList[idx].PadColor, dimDefault)

    UpdateWindowStates()
    RefreshWindowStates()

def RefreshMarkers():
    for pad in pdMarkers:
        idx = pdMarkers.index(pad)
        SetPadColor(pad, getShade(cOrange, shDim), dimDefault)

def RefreshNavPads():
    global _PadMode
    # mode specific
    showPresetNav = _PadMode.NavSet.PresetNav 
    showNoteRepeat = _PadMode.NavSet.NoteRepeat
    showUDLRNav = _PadMode.NavSet.UDLRNav
    showChanWinNav = _PadMode.NavSet.ChanNav
    showSnapNav = _PadMode.NavSet.SnapNav
    showScaleNav = _PadMode.NavSet.ScaleNav
    showOctaveNav = _PadMode.NavSet.OctaveNav
    showLayoutNav = _PadMode.NavSet.LayoutNav
    
    
    RefreshGridLR()        

    if(isNoNav()):
        return

    for pad in pdNav :
        SetPadColor(pad, cOff, dimDefault)
    
    if(showUDLRNav):
        RefreshUDLR()
        return 

    # these two are exclusive as they use the same pads in diff modes
    if(showScaleNav):
        for idx, pad in enumerate(pdNoteFuncs):
            color = colNoteFuncs[idx]
            SetPadColor(pad, color, dimDefault)
    elif(showOctaveNav) and (not showNoteRepeat): 
        SetPadColor(pdOctaveNext, colOctaveNext, dimDefault)
        SetPadColor(pdOctavePrev, colOctavePrev, dimDefault)
        

    if(showPresetNav):
        for idx, pad in enumerate(pdPresetNav):
            color = colPresetNav[idx]
            SetPadColor(pad, color, dimDefault)

    if(showChanWinNav):
        SetPadColor(pdShowChanEditor, _ChannelMap[getCurrChanIdx()].Color, dimBright)
        SetPadColor(pdShowChanPianoRoll, cWhite, dimDefault)

    if(showNoteRepeat):
        if(_NoteRepeat):
            SetPadColor(pdNoteRepeat, colNoteRepeat, dimBright)
            SetPadColor(pdNoteRepeatLength, colNoteRepeatLength, dimDim)
        else:
            SetPadColor(pdNoteRepeat, colNoteRepeat, dimDefault)
            SetPadColor(pdNoteRepeatLength, colNoteRepeatLength, dimDim)

    # these two are exclusive as they use the same pads in diff modes
    if(showSnapNav):
        SetPadColor(pdSnapUp, colSnapUp, dimDefault)
        SetPadColor(pdSnapDown, colSnapDown, dimDim)
    elif(showLayoutNav):
        SetPadColor(pdLayoutPrev, colLayoutPrev, dimDefault)
        SetPadColor(pdLayoutNext, colLayoutNext, dimDefault)


def RefreshPageLights(clearOnly = False):
    global _PadMode
    SendCC(IDPage0, SingleColorOff)
    SendCC(IDPage1, SingleColorOff)
    SendCC(IDPage2, SingleColorOff)
    SendCC(IDPage3, SingleColorOff)                    
    SendCC(IDTrackSel1, SingleColorOff)    
    SendCC(IDTrackSel2, SingleColorOff)    
    SendCC(IDTrackSel3, SingleColorOff)    
    SendCC(IDTrackSel4, SingleColorOff)    

    if(clearOnly):
        return 

    if(_PadMode.Mode == MODE_NOTE):
        if(_ShowChords):
            SendCC(IDPage0, SingleColorHalfBright)
    elif(_PadMode.Mode == MODE_PERFORM):
        if(_PadMode.IsAlt):
            SendCC(IDPage0 + _ProgressPadLenIdx, SingleColorHalfBright)
    elif(_PadMode.Mode == MODE_PATTERNS):
        #pattern page
        if(_PatternPage > 0):
            SendCC(IDPage0, SingleColorFull)
        if(_PatternPage > 1):
            SendCC(IDTrackSel1, SingleColorFull)
        if(_PatternPage > 2):
            SendCC(IDPage1, SingleColorFull)
        if(_PatternPage > 3):
            SendCC(IDTrackSel2, SingleColorFull)

        #channel page
        if(_ChannelPage > 0):
            SendCC(IDPage2, SingleColorFull)
        if(_ChannelPage > 1):
            SendCC(IDTrackSel3, SingleColorFull)
        if(_ChannelPage > 2):
            SendCC(IDPage3, SingleColorFull)
        if(_ChannelPage > 3):
            SendCC(IDTrackSel4, SingleColorFull)
        
            
def RefreshNotes():
    global _PadMap
    global _NoteMap

    RefreshPageLights()

    if(isChromatic()):
        rootNote = 0 # C
        showRoot = False
    else:
        rootNote = _NoteIdx
        showRoot = True 

    baseOctave = OctavesList[_OctaveIdx]

    GetScaleGrid(_ScaleIdx, rootNote, baseOctave) #this will populate _PadMap.NoteInfo

    for p in pdWorkArea:
        color = cDimWhite
        if(isChromatic()): #chromatic,
            if(len(utils.GetNoteName(_PadMap[p].NoteInfo.MIDINote) ) > 2): # is black key?
                color = cDimWhite #-1
            else:
                color = cWhite 
        else: #non chromatic
            if(_PadMap[p].NoteInfo.IsRootNote) and (showRoot):
                if(DEFAULT_ROOT_NOTE_COLOR == cChannel):
                    color = FLColorToPadColor(channels.getChannelColor(getCurrChanIdx()))
                else:
                    color = DEFAULT_ROOT_NOTE_COLOR

        if(_ShowChords):
            if(p in pdChordBar):
                SetPadColor(p, cBlue, dimDefault)
            elif(p in pdChordFuncs):
                SetPadColor(p, cOff, dimDefault)
            else:
                SetPadColor(p, color, dimDefault)

            RefreshChordType()

        else:
            SetPadColor(p, color, dimDefault)
                

    # set the specific mode related funcs here

    RefreshMacros() 
    RefreshNavPads()
    RefreshDisplay()

def RefreshChordType():
    if(_Chord7th):
        SetPadColor(pd7th, cYellow, dimBright)
    else:
        SetPadColor(pd7th, cYellow, dimDim) # extra dim
    if(_ChordInvert == 1):
        SetPadColor(pdInv1, cWhite, dimDefault)
    elif(_ChordInvert == 2):
        SetPadColor(pdInv2, cWhite, dimDefault)
    else:
        SetPadColor(pdNormal, cWhite, dimDefault)

def RefreshDrumPads():
    global _PadMap
    global _NoteMapDict
    _NoteMapDict.clear()
    chanIdx = getCurrChanIdx() 
    pads = DrumPads()

    if(_isAltMode): # function in NON FPC mode
        colors = [cWhite, cCyan, cBlue, cOrange, cGreen, cYellow]
        changeEvery = 16

        if(_PadMode.LayoutIdx  == lyStrips):
            changeEvery = 12

        #if(DEFAULT_ALT_DRUM_MODE_BANKS == False):
        #    changeEvery = 12

        for idx, p in enumerate(pads):
            rootNote = 12 # 12 = C1 ?
            startnote = rootNote + (OctavesList[_OctaveIdx] * 12) 
            MapNoteToPad(p, startnote + idx)
            colIdx =  idx//changeEvery
            SetPadColor(p, colors[colIdx], dimDefault)

    else: # FPC mode
        #do this first to force it to change to an FPC instance if available.
        RefreshFPCSelector()
        # _FPCNotesDict.clear()
        
        if( isFPCActive()):  # Show Custom FPC Colors
            PAD_Semitone =	1	#Retrieve semitone for pad specified by padIndex
            PAD_Color =	2	#Retrieve color for pad specified by padIndex    

            # FPC A Pads
            #fpcpadIdx = 0
            semitone = 0
            color = cOff
            dim =  dimDefault
            for idx, p in enumerate(pads): #pdFPCA:
                color = plugins.getPadInfo(chanIdx, -1, PAD_Color, idx) #fpcpadIdx) # plugins.getColor(chanIdx, -1, GC_Semitone, fpcpadIdx)
                semitone = plugins.getPadInfo(chanIdx, -1, PAD_Semitone, idx) #fpcpadIdx)
                MapNoteToPad(p, semitone)
                SetPadColor(p, FLColorToPadColor(color), dim)
            #     fpcpadIdx += 1 # NOTE! will be 16 when we exit the for loop, the proper first value for the B Pads loop...
            # # FPC B Pads
            # for p in pdFPCB: #NOTE! fpcpadIdx s/b 16 when entering this loop
            #     color = plugins.getPadInfo(chanIdx, -1, PAD_Color, fpcpadIdx) 
            #     semitone = plugins.getPadInfo(chanIdx, -1, PAD_Semitone, fpcpadIdx) 
            #     MapNoteToPad(p, semitone)
            #     #_PadMap[p].NoteInfo.MIDINote = semitone 
            #     #_NoteMap[p] = semitone 
            #     SetPadColor(p, FLColorToPadColor(color), dim)
            #     fpcpadIdx += 1 # continue 
        else: # 
            for p in pads:
                SetPadColor(p, cOff, dimDefault)
                _PadMap[p].Color = cOff

    RefreshMacros() 
    RefreshNavPads()

def MapNoteToPad(padNum, note):
    global _NoteMap
    global _PadMap
    global _NoteMapDict

    if(note in _NoteMapDict):
        _NoteMapDict[note].append(padNum)
    else:
        _NoteMapDict[note] = [padNum]
    
    # maintain these here for now
    _PadMap[padNum].NoteInfo.MIDINote = note
    _NoteMap[padNum] = note
    

def RefreshFPCSelector():
    # refresh the 'channel area' where fpc instances are shown
    idx = 0

    #clear the existing channel area
    for p in pdFPCChannels:
        SetPadColor(p, cOff, dimDefault)
        _PadMap[p].Color = cOff
        _PadMap[p].ItemIndex = -1

    #find the fpc channels
    for chan in range(channels.channelCount()):
        # check if there is room
        if(idx < len(pdFPCChannels)): 
            if(_ChannelMap[chan].ChannelType == CT_GenPlug):
                if(plugins.getPluginName(chan, -1, 0) == "FPC"):
                    if(not isFPCActive()): #if an FPC is not selected, choose the first one
                        SelectAndShowChannel(chan)
                    padNum = pdFPCChannels[idx]
                    padColor = FLColorToPadColor(channels.getChannelColor(chan))
                    if(getCurrChanIdx()  == chan):
                        SetPadColor(padNum, padColor, dimBright)
                    else:
                        SetPadColor(padNum, padColor, dimDefault)
                    _PadMap[padNum].Color = padColor
                    _PadMap[padNum].ItemIndex = chan 
                    idx += 1

def RefreshKnobMode():
    LEDVal = IDKnobModeLEDVals[_KnobMode] | 16
    SendCC(IDKnobModeLEDArray, LEDVal)

def RefreshPlaylist():
    global _PadMap
    global pdPlaylistStripA
    global pdPlaylistStripB
    global pdPlaylistMutesA
    global pdPlaylistMutesB 

    plPage = 0

    pdPlaylistStripA = pdWorkAreaRowA
    pdPlaylistMutesA = pdWorkAreaRowB
    pdPlaylistStripB = pdWorkAreaRowC
    pdPlaylistMutesB = pdWorkAreaRowD

    if(isNoNav()):
        pdPlaylistStripA = pdRowA
        pdPlaylistMutesA = pdRowB
        pdPlaylistStripB = pdRowC
        pdPlaylistMutesB = pdRowD


    plLen = len(pdPlaylistStripA)
    plMapToShow = _PlaylistMap

    if(_isAltMode):
        plMapToShow = _PlaylistSelectedMap
        if(len(_PlaylistSelectedMap) <  len(pdPlaylistStripA) ):
            plLen = len(_PlaylistSelectedMap)

    plStartIdx = (plLen * plPage)

    if(len(plMapToShow) == 0):
        return 

    for padOffs in range(plLen): #gives me 0..12 or 0..selected when less than 12
        padTrackA = pdPlaylistStripA[padOffs]
        padMuteA  = pdPlaylistMutesA[padOffs]
        padTrackB = pdPlaylistStripB[padOffs]
        padMuteB  = pdPlaylistMutesB[padOffs]
        dimA = dimDefault
        dimB = dimDefault
        muteColorA = cDimWhite
        muteColorB = cDimWhite

        plMapA = plMapToShow[plStartIdx + padOffs]
        flIdxA = plMapA.FLIndex 
        if(playlist.isTrackSelected(flIdxA)):
            dimA = dimBright
        SetPadColor(padTrackA, plMapA.Color, dimA) 
        _PadMap[padTrackA].Color = plMapA.Color
        _PadMap[padTrackA].FLIndex = flIdxA
        if(playlist.isTrackMuted(flIdxA)):
            muteColorA = cOff 
        SetPadColor(padMuteA, muteColorA, dimDefault) 
        _PadMap[padMuteA].Color = muteColorA
        _PadMap[padMuteA].FLIndex = flIdxA

        if(not _isAltMode):
            plMapB = plMapToShow[plStartIdx + padOffs + plLen]
            flIdxB = plMapB.FLIndex
            if(playlist.isTrackSelected(flIdxB)):
                dimB = dimBright
            SetPadColor(padTrackB, plMapB.Color, dimB) 
            _PadMap[padTrackB].Color = plMapB.Color
            _PadMap[padTrackB].FLIndex = flIdxB
            if(playlist.isTrackMuted(flIdxB)):
                muteColorB = cOff 
            SetPadColor(padMuteB, muteColorB, dimDefault) 
            _PadMap[padMuteB].Color = muteColorB
            _PadMap[padMuteB].FLIndex = flIdxB
        else:
            RefreshProgress()

def RefreshChannelStrip(scrollToChannel = False):
    global _ChannelMap
    global _CurrentChannel
    global _PatternMap
    global _ChannelPage
    global _PadMap

    #only run when in paatern mode
    if(_PadMode.Mode != MODE_PATTERNS):
        return 

    if(len(_ChannelMap) == 0):
        return
    
    if len(_ChannelMap) != channels.channelCount():
        UpdateChannelMap()

    channelMap = _ChannelMap
    currChan = getCurrChanIdx() # 
    currMixerNum = channels.getTargetFxTrack(currChan)

    # determine the offset. 
    channelsPerPage = getChannelModeLength()
    pageOffset = getChannelOffsetFromPage() 
    pageNum = (currChan // channelsPerPage) + 1

    channelStripA, channelStripB = getChannelPads()

    # is the current channel visible and do we care?
    if(scrollToChannel) and (pageNum != _ChannelPage):
        if(_ChannelPage != pageNum):
            _ChannelPage = pageNum 
            ChannelPageNav(0)
            pageOffset = getChannelOffsetFromPage()    

    for padOffset in range(channelsPerPage):
        chanIdx = padOffset + pageOffset
        padAIdx = channelStripA[padOffset]
        padBIdx = channelStripB[padOffset]
        channel = TnfxChannel(-1,'')
        if(chanIdx < len(channelMap)):
            channel = channelMap[chanIdx]
        
        if(currChan == channel.FLIndex):
            SetPadColor(padAIdx, channel.Color, dimBright)
        else:
            SetPadColor(padAIdx, channel.Color, dimDefault)
        
        if(channel.FLIndex >= 0):
            if(_ShiftHeld): # Shifted will display Mute states
                col = cMuteOff
                if(_KnobMode == KM_MIXER):
                    if (channel.Mixer.FLIndex > -1):
                        if(mixer.isTrackMuted(channel.Mixer.FLIndex)):
                            col = cMuteOn
                else:
                    if(channels.isChannelMuted(channel.FLIndex)):
                        col = cMuteOn

                SetPadColor(padBIdx, col, dimDefault)
            elif(currMixerNum == channels.getTargetFxTrack(channel.FLIndex)): 
                #not Shifted
                if(currChan == channel.FLIndex):
                    SetPadColor(padBIdx, cWhite, dimBright)
                else:
                    SetPadColor(padBIdx, cDimWhite, dimDefault)
            else: #not shifted and not an fx track match
                SetPadColor(padBIdx, cOff, dimDefault)
        else:
            SetPadColor(padBIdx, cOff, dimDefault)

    SelectAndShowChannel(currChan)
    RefreshNavPads()

def getChannelOffsetFromPage():
    # returns the index of the first pattern to show on the pattern strip based on the active page
    chanAStrip, chanBStrip = getChannelPads()
    return (_ChannelPage-1) * len(chanAStrip)

def getPatternOffsetFromPage():
    # returns the index of the first pattern to show on the pattern strip based on the active page
    pattAStrip, pattBStrip = getPatternPads()
    return (_PatternPage-1) * len(pattAStrip)

def getChannelPads(): 
    if(isNoNav()):
        return pdChanStripANoNav, pdChanStripBNoNav
    return pdChanStripA, pdChanStripB

def getPatternPads():
    if(isNoNav()):
        return pdPatternStripANoNav, pdPatternStripBNoNav
    return pdPatternStripA, pdPatternStripB

def getPatternModeLength():
    return len(getPatternPads()[0])

def getChannelModeLength():
    a, b = getChannelPads()
    return len(a)

def RefreshPatternStrip(scrollToChannel = False):
    # should rely upon _PatternMap or _PatternMapSelected only. should not trly upon _PadMap
    # should use _PatternPage accordingly 
    global _PatternPage

    if (_PadMode.Mode != MODE_PATTERNS):
        return 

    patternMap = getPatternMap()

    # determine the offset. 
    pageOffset = getPatternOffsetFromPage() 

    patternStripA, patternStripB = getPatternPads()
    patternsPerPage = getPatternModeLength()

    # is the current pattern visible and do we care?
    if(scrollToChannel):
        currPat = patterns.patternNumber()
        pageNum = (currPat // (patternsPerPage+1)) + 1
        if(_PatternPage != pageNum):
            _PatternPage = pageNum 
            PatternPageNav(0)
            pageOffset = getPatternOffsetFromPage()
            
    for padOffset in range(0, patternsPerPage):
        patternIdx = padOffset + pageOffset
        padIdx = patternStripA[padOffset]
        padBIdx = patternStripB[padOffset]
        if(padOffset < patternsPerPage) and (patternIdx < len(patternMap)): # room to use an available pattern?
            pattern = patternMap[patternIdx] 
            if(patterns.patternNumber() == pattern.FLIndex): #current pattern
                SetPadColor(padIdx, pattern.Color, dimBright)
                SetPadColor(padBIdx, cWhite, dimBright)
            else:
                if(pattern.Selected):
                    SetPadColor(padIdx, pattern.Color, dimDefault)
                    SetPadColor(padBIdx, cDimWhite, dimBright)
                else:
                    SetPadColor(padIdx, pattern.Color, dimDim)
                    SetPadColor(padBIdx, cOff, dimDim)
        else: #not used
            SetPadColor(padIdx, cOff, dimDim)
            SetPadColor(padBIdx, cOff, dimDim)            


def RefreshDisplay():
    global _menuItemSelected

    if _shuttingDown:
        return

    _menuItemSelected = _chosenItem # reset this for the next menu
    chanIdx = getCurrChanIdx() # 
    chanName = channels.getChannelName(chanIdx)
    mixerName = mixer.getTrackName(mixer.trackNumber())
    patName = patterns.getPatternName(patterns.patternNumber())
    cMap = _ChannelMap[chanIdx]
    
    chanTypes = ['S', 'H', 'V', 'L', 'C', 'A']
    
    toptext = ''
    bottext = ''
    um = KnobModeShortNames[_KnobMode] 
    pm = PadModeShortNames[_PadMode.Mode] + " - " + um
    toptext = pm 
    sPatNum = str(patterns.patternNumber())
    midtext = sPatNum + '. ' + patName 
    bottext = chanTypes[cMap.ChannelType] + ': ' + cMap.Name

    if(_PadMode.Mode == MODE_PATTERNS):
        toptext = pm + '     ' 
        if(KnobModeShortNames[_KnobMode] in ['Mi']):
            toptext = pm + '    ' # on less space
        if(KnobModeShortNames[_KnobMode] in ['U1', 'U2']):
            toptext = pm + '   ' # on less space
        toptext = toptext + str(_PatternPage) + ' - ' + str(_ChannelPage)

    if(_PadMode.Mode == MODE_NOTE):
        midtext = '' + _ScaleDisplayText
        if(_ShowChords):
            toptext = pm + " - ChB"

    DisplayTextTop(toptext)
    DisplayTextMiddle(midtext)
    DisplayTextBottom(bottext)

    prn(lvlD, '  |-------------------------------------')
    prn(lvlD, '  | ', toptext)
    prn(lvlD, '  | ', midtext)
    prn(lvlD, '  | ', bottext)
    prn(lvlD, '  |-------------------------------------')
def RefreshUDLR():
    for pad in pdUDLR:
        if(pad == pdShiftTab):
            SetPadColor(pad, cCyan, dimDefault)
        elif(pad == pdTab):
            SetPadColor(pad, cCyan, dimBright)
        elif(pad == pdEsc):
            SetPadColor(pad, cRed, dimDefault)
        elif(pad == pdEnter):
            SetPadColor(pad, cGreen, dimDefault)
        else:
            SetPadColor(pad, cWhite, dimDefault)


def RefreshProgress():
    progMap = list()

    if(transport.getLoopMode == 0): # PATTERN
        progMap.extend(_ProgressMapPatterns)
    else:
        progMap.extend(_ProgressMapSong)

    for pPad in progMap:
        if(pPad.SongPosAbsTicks <= transport.getSongPos(SONGLENGTH_ABSTICKS)): #which pads have 'played'?
            if(pPad.BarNumber == transport.getSongPos(SONGLENGTH_BARS)):
                SetPadColor(pPad.PadIndex, getShade(cYellow, shNorm), dimBright)
            else:
                SetPadColor(pPad.PadIndex, getShade(pPad.Color, shNorm), dimBright)
        else: # not yet played
            SetPadColor(pPad.PadIndex, getShade(pPad.Color, shNorm), dimDim)



def RefreshProgressOrig():
    
    colorOn = cWhite
    colorDim = cDimWhite
    if(transport.isRecording()):
        colorDim = getShade(cRed, shDark)
        colorOn = cRed

#    if(transport.isPlaying()):
    progressLen = len(pdProgress)
    songPos = transport.getSongPos()
    songPosTicks = transport.getSongPos()
    progressPos = int(progressLen * songPos)

    for p in range(progressLen):
        if(p <= progressPos) and (transport.isPlaying()):
            SetPadColor(pdProgress[p], colorOn, dimDefault)
        else:
            SetPadColor(pdProgress[p], colorDim, dimDefault)

#endregion 

#region Updates / Resets
def UpdatePadMap():
    if(_PadMode.Mode == MODE_PATTERNS):
        UpdatePadMapForPatterns()
        UpdatePatternModeData()
        

def UpdatePadMapForPatterns():
    # should use the _patternMap instead of calls to pattern.XXX finctions
    global _PadMap
    global _PatternMap
    global _PatternSelectedMap
    global _PatternCount


    if(_PadMode.Mode == MODE_PATTERNS): # Pattern mode, set the pattern buttons

        # temp map 
        patternMap = getPatternMap()

        if(len(_PadMap) == 0):
            ResetPadMaps(False)

        # patterns
        patternStripA, patternStripB = getPatternPads()
        chanStripA, chanStripB = getChannelPads()
        pageLen = getPatternModeLength()
        patPageOffs = (_PatternPage-1) * pageLen # first page will = 0
        chanPageOffset = (_ChannelPage-1) * pageLen # first page will = 0

        for padOffset in range(0, pageLen): 

            #defaults
            padColor = cOff 
            flIdx = -1

            pattAPadIdx = patternStripA[padOffset]    # the pad to light up
            pattBPadIdx = patternStripB[padOffset]    # the secondary pad
            pattIdx = padOffset + patPageOffs           # the pattern in _PatternMap to represent

            chanPadIdxA = chanStripA[padOffset]       # the pad to light up
            chanPadIdxB = chanStripA[padOffset]       # the secondary pad
            chanIdx = padOffset + chanPageOffset        # the channel to represent at this pad

            if(pattIdx <= len(patternMap)): # when true, there is data to use
                flIdx = pattIdx + 1 # fl patterns are 1 based
                padColor = patternMap[pattIdx].Color # FLColorToPadColor(patterns.getPatternColor(flIdx)) 
                #if we have the object, then place it
                _PadMap[pattAPadIdx].ItemObject = patternMap[pattIdx]
                _PadMap[pattAPadIdx].ItemIndex = pattIdx
                _PadMap[pattBPadIdx].ItemObject = patternMap[pattIdx]
                _PadMap[pattBPadIdx].ItemIndex = pattIdx

            _PadMap[pattAPadIdx].Color = padColor
            _PadMap[pattAPadIdx].FLIndex = flIdx
            _PadMap[pattBPadIdx].Color = cDimWhite
            _PadMap[pattBPadIdx].FLIndex = flIdx

            # channels
            padColor = cOff 
            flIdx = -1
            if(chanIdx < (_ChannelCount) ):
                flIdx = chanIdx # fl channels are 0 based 
                padColor = FLColorToPadColor(channels.getChannelColor(flIdx))

            _PadMap[chanPadIdxA].Color = padColor
            _PadMap[chanPadIdxA].FLIndex = flIdx
            _PadMap[chanPadIdxB].Color = cDimWhite
            _PadMap[chanPadIdxB].FLIndex = flIdx 

        RefreshPatternStrip() 
        
def UpdatePatternMapOld_OBS(pattNum):
    global _PatternMap
    global _PatternCount

    chanNum = getCurrChanIdx() # channels.channelNumber()
    mixNum = channels.getTargetFxTrack(chanNum)
    nfxMixer = TnfxMixer(mixNum, mixer.getTrackName(mixNum))
    _PatternCount = patterns.patternCount()

    if(pattNum < 0):  #ENUMERATE ALL PATTERNS
        _PatternMap.clear()
        for pat in range(_PatternCount):
            patMap = TnfxPattern(pat, patterns.getPatternName(pat))
            patMap.Color = patterns.getPatternColor(pat)
            patMap.Mixer = nfxMixer
            _PatternMap.append(patMap)
    else: #update the current pattern's channels map only
        RefreshChannelStrip()     

def UpdatePlaylistMap(selectedOnly = False):
    global _PlaylistMap
    global _PlaylistSelectedMap
    global _PadMap

    _PlaylistMap.clear()
    _PlaylistSelectedMap.clear()

    for plt in range(playlist.trackCount()):
        flIdx = plt + 1
        color = FLColorToPadColor( playlist.getTrackColor(flIdx) )
        name = playlist.getTrackName(flIdx)
        plMap = TnfxPlaylistTrack(flIdx, name, color)
        plMap.Muted = playlist.isTrackMuted(flIdx)
        plMap.Selected = playlist.isTrackSelected(flIdx)
        _PlaylistMap.append(plMap)
        if(plMap.Selected):
            _PlaylistSelectedMap.append(plMap)

def UpdatePatternMap(pattNum):
    # this function should read ALL patterns from FL and have update two global lists of type <TnfxPattern>:
    #   1. _PatternMap - all of the patterns from FL
    #   2. _PatternSelectedMap - the selected patterns from FL . includes the currently active pattern
    #
    #   This function is needed by: UpdatePadMap(), getPatternMap() 
    #
    global _PatternMap
    global _PatternCount
    global _CurrentPattern
    global __PatternSelectedMap

    _PatternCount = patterns.patternCount()
    _PatternMap.clear()
    _PatternSelectedMap.clear()

    for pat in range(1,_PatternCount+1): # FL patterns start at 1
        patMap = TnfxPattern(pat, patterns.getPatternName(pat))
        patMap.Color = FLColorToPadColor(patterns.getPatternColor(pat))  
        patMap.Selected = patterns.isPatternSelected(pat)
        _PatternMap.append(patMap)
        if(patMap.Selected):
            _PatternSelectedMap.append(patMap)

    _CurrentPattern = patterns.patternNumber()

def UpdateProgressMap(autodetect = True):
    global _ProgressMapSong
    global _ProgressMapPatterns
    global _ProgressPadLenIdx

    newMap = list()

    #todo: need to be aware of song pode/patt mode here?
    progressLen = len(pdProgress) 
    songLenAbsTicks = transport.getSongLength(SONGLENGTH_ABSTICKS)
    padLen = 100/progressLen 
    songLenBars = transport.getSongLength(SONGLENGTH_BARS)

    selStart = arrangement.selectionStart()
    selEnd = arrangement.selectionEnd()
    selBarStart = getBarFromAbsTicks(selStart)
    selBarEnd =  getBarFromAbsTicks(selEnd)
    if(selEnd > -1): #this will be -1 if nothing selected
        songLenAbsTicks = selEnd - selStart
        songLenBars = selBarEnd - selBarStart
    else:
        selBarStart = 0 # 
        selStart = 0


    if(autodetect):
        if(songLenBars <= 32):
            _ProgressPadLenIdx = 1
        elif(songLenBars <= 64):
            _ProgressPadLenIdx = 2
        elif(songLenBars <= 128):
            _ProgressPadLenIdx = 3

    padBarLen = 1
    if(_ProgressPadLenIdx == 0): # 1 beat
        padAbsLen = songLenAbsTicks/progressLen + 1
        padBarLen = 0 #getBeatLenInMS(1)
    else:
        padAbsLen = getAbsTicksFromBar(2) * padBarLen # get the start of bar 2 aka the length of 1 bar in ticks times the number of bars
        if(_ProgressPadLenIdx == 1): # 1 bars
            padBarLen = 1
        elif(_ProgressPadLenIdx == 2): # 2 bars
            padBarLen = 2
        elif(_ProgressPadLenIdx == 3): # 4 bars
            padBarLen = 4

    for padIdx in range(progressLen):
        progressPosAbsTicks = int(padIdx * padAbsLen)  + selStart # returns 0..SONGLENGTH_ABSTICKS

        progressPos =  (padIdx * padLen) # shoudl return 0..(1 - padLen)

        nextAbsTick = progressPosAbsTicks  + padAbsLen # was  int( (padIdx+1) * padAbsLen )
        progBarNumber = (padBarLen * padIdx) + 1  #    

        progPad = TnfxProgressStep(pdProgress[padIdx], cWhite, progressPos, progressPosAbsTicks, progBarNumber)
        

        if(progressPosAbsTicks < songLenAbsTicks ):
            #determine what markers are in this range.
            for marker in _MarkerMap:
                if(progressPosAbsTicks <= marker.SongPosAbsTicks < nextAbsTick):
                    if(progressPosAbsTicks == marker.SongPosAbsTicks): # or ((progressPosAbsTicks+1 == marker.SongPosAbsTicks)): # I need to fix my math
                        progPad.Color = cGreen
                    else:
                        progPad.Color = cOrange

                    progPad.Markers.append(marker)

        else:
            progPad.BarNumber = -1
            progPad.Color = cOff # getShade(cRed, shDark)
            progPad.SongPosAbsTicks = -1
        
        newMap.append(progPad)

    if(transport.getLoopMode() == 0): # pattern mode
        _ProgressMapPatterns.clear()
        _ProgressMapPatterns.extend(newMap)
    else: # song mode
        _ProgressMapSong.clear()
        _ProgressMapSong.extend(newMap)



def UpdateMarkerMap():
    global _MarkerMap

    return

    # should only run when not playing
    if(transport.isPlaying()):
        return 

    _MarkerMap.clear()
    transport.stop()
    transport.setSongPos(1) # 3nd of song will force the marker to restart at beginning
    
    prevNum = -1
    markerCount = 0
    for i in range(100):
        if(arrangement.getMarkerName(i) != ""):
            markerCount += 1
        else:
            break

    if(markerCount > 0):
        transport.setSongPos(1)
        for m in range(markerCount):
            markerNum = arrangement.jumpToMarker(1, False)
            while (markerNum > m): #workaround
                markerNum = arrangement.jumpToMarker(-1, False)

        #while(markerNum > prevNum):
            markerName = arrangement.getMarkerName(markerNum)
            markerTime = arrangement.currentTime(1) # returns in ticks
            m = TnfxMarker(markerNum, markerName, markerTime)
            _MarkerMap.append(m)
        #    prevNum = markerNum
        #   markerNum = arrangement.jumpToMarker(1, False)

    
def UpdateChannelMap():
    global _ChannelMap
    global _ChannelCount
    global _CurrentChannel
    global _ChannelSelectedMap

    _ChannelCount = channels.channelCount()
    _ChannelMap.clear()
    _ChannelSelectedMap.clear()

    for chan in range(_ChannelCount):
        chanMap = TnfxChannel(chan, channels.getChannelName(chan))
        chanMap.Color = FLColorToPadColor( channels.getChannelColor(chan) )
        chanMap.ChannelType = channels.getChannelType(chan)
        chanMap.GlobalIndex = channels.getChannelIndex(chan)
        chanMap.Selected = channels.isChannelSelected(chan)
        mixerNum = channels.getTargetFxTrack(chan)
        mixer = TnfxMixer(mixerNum, '')
        chanMap.Mixer = mixer
        _ChannelMap.append(chanMap)
        if(chanMap.Selected):
            _ChannelSelectedMap.append(chanMap)

def UpdatePatternModeData(pattNum = -1):
    global _CurrentChannel
    global _ChannelCount
    ResetPadMaps(False)
    UpdatePatternMap(pattNum)
    UpdateChannelMap()
    #UpdatePadMap()

def ResetBeatIndicators():
    for i in range(0, len(BeatIndicators) ):
        SendCC(BeatIndicators[i], SingleColorOff)
#endregion 

#region Helper function 
def isFPCChannel(chanIdx):
    if(_ChannelMap[chanIdx].ChannelType == CT_GenPlug):
        pluginName = plugins.getPluginName(chanIdx, -1, 0)      
        return (pluginName == 'FPC')     

def isFPCActive():
    chanIdx = getCurrChanIdx() # channels.channelNumber()
    return isFPCChannel(chanIdx)

def CopyChannel(chanIdx):
    ShowChannelRack(1)
    chanIdx = getCurrChanIdx() # channels.channelNumber()
    SelectAndShowChannel(chanIdx)
    ui.copy
    name = channels.getChannelName(chanIdx)
    color = channels.getChannelColor(chanIdx)
    # crap, cant be done - no way to insert a channel via API
    return 


def CopyPattern(FLPattern):
    ui.showWindow(widChannelRack)
    chanIdx = getCurrChanIdx() # channels.channelNumber()
    SelectAndShowChannel(chanIdx)
    ui.copy 
    name = patterns.getPatternName(FLPattern)
    color = patterns.getPatternColor(FLPattern)
    patterns.findFirstNextEmptyPat(FFNEP_DontPromptName)
    newpat = patterns.patternNumber()
    patterns.setPatternName(newpat, name)
    patterns.setPatternColor(newpat, color)
    SelectAndShowChannel(chanIdx)
    ui.paste 
    

def ResetPadMaps(bUpdatePads = False):
    global _PadMap
    global _NoteMap
    _PadMap.clear()
    _NoteMap.clear()
    _NoteMapDict.clear()
    for padIdx in range(0, 64):
        _PadMap.append(TnfxPadMap(padIdx, -1, 0x000000, ""))
        _NoteMap.append(-1) # populates later on GetScaleGrid call along with the _NoteMapDict
    if(bUpdatePads):
        RefreshPadsFromPadMap()

def isChromatic():
    return (_ScaleIdx == 0) #chromatic

def GetScaleGrid(newModeIdx=0, rootNote=0, startOctave=2):
    global _PadMap 
    global _ScaleNotes 
    global _ScaleDisplayText
    global _ScaleIdx
    global _NoteMap
    global __NoteMapDict


    _faveNoteIdx = rootNote
    _ScaleIdx = newModeIdx
    harmonicScale = ScalesList[_ScaleIdx]
    gridlen = 12

    _ScaleNotes.clear()

    if(_isAltMode) and (_PadMode.Mode == MODE_DRUM):
        harmonicScale = ScalesList[0]
        gridlen = 64

    # get lowest octave line
    lineGrid = [[0] for y in range(gridlen)] # init with 0
    notesInScale = GetScaleNoteCount(harmonicScale)
       
    #build the lowest <gridlen> notes octave and transpose up from there
    BuildNoteGrid(lineGrid, gridlen, 1, rootNote, startOctave, harmonicScale)

    # first I make a 5 octave list of notes to refernce later
    for octave in range(0, 5):
        for note in range(0, notesInScale):
            _ScaleNotes.append(lineGrid[note][0] + (12*octave) )

    # next I fill in the notes from the bottom to top
    _NoteMapDict.clear()

    if(_PadMode.Mode == MODE_NOTE):
        for colOffset in range(0, gridlen):
            for row in range(0, 4): # 3
                
                if(notesInScale < 6): 
                    noteVal = lineGrid[colOffset][0] + (24*row) # for pentatonic scales 
                else:
                    noteVal = lineGrid[colOffset][0] + (12*row)
                revRow = 3-row  # reverse to go from bottom to top
                rowOffset = 16 * revRow  # rows start on 0,16,32,48
                padIdx = rowOffset + colOffset

                MapNoteToPad(padIdx, noteVal)
                if(row == 3): # and (GetScaleNoteCount(scale) == 7): #chord row
                    _PadMap[padIdx].NoteInfo.ChordNum = colOffset + 1
                else:
                    _PadMap[padIdx].NoteInfo.ChordNum = -1
                
                _NoteMap[padIdx] = noteVal

                if(_PadMap[padIdx].NoteInfo.ChordNum < 0): # not a chord pad, so its ok
                    if(noteVal not in _NoteMapDict.keys()): 
                        _NoteMapDict[noteVal] = [padIdx]
                    elif(DEFAULT_SHOW_ALL_MATCHING_CHORD_NOTES):
                        if(padIdx not in _NoteMapDict[noteVal]):
                            _NoteMapDict[noteVal].append(padIdx)

                _PadMap[padIdx].NoteInfo.IsRootNote = (colOffset % notesInScale) == 0 # (colOffset == 0) or (colOffset == notesInScale)

        _ScaleDisplayText = NotesList[_faveNoteIdx] + str(startOctave) + " " + HarmonicScaleNamesT[harmonicScale]

def PlayMIDINote(chan, note, velocity):   
    if(chan > -1):
        if(velocity > 0):
            channels.midiNoteOn(chan, note, velocity)
            ShowNote(note, True)
        else:
            channels.midiNoteOn(chan, note, 0)
            ShowNote(note, False)

#endregion 

#region setters/getters
def GetPatternMapActive():
    return _PatternMap[_CurrentPattern-1]

def GetChannelMapActive():
    return _ChannelMap[_CurrentChannel-1]

def SetPadMode():
    RefreshShiftAltButtons()
    if(_PadMode.Mode == MODE_PATTERNS):
        UpdatePatternModeData()
    elif(_PadMode.Mode == MODE_PERFORM):
        ClearAllPads()
        if(_isAltMode):
            UpdateMarkerMap()
            UpdateProgressMap()
            RefreshProgress()
    elif(_PadMode.Mode == MODE_DRUM):
        RefreshNavPads()

    RefreshPadModeButtons() # lights the button
    RefreshAll()

def getCurrChanIdx():
    return channels.selectedChannel()
    globalIdx = channels.channelNumber()
    res = -1
    for cMap in _ChannelMap:
        if(cMap.GlobalIndex == globalIdx):
            res = cMap.FLIndex
    return res 

def XgetCurrChannelPluginName():
    return plugins.getPluginName(getCurrChanIdx(), -1, 0)

def getCurrChanPluginID():
    name, plugin = getCurrentChannelPlugin()
    if(plugin == None):
        return ""
    return plugin.getID()

def getCurrChannelPluginNames():
    return plugins.getPluginName(getCurrChanIdx(), -1, 0), plugins.getPluginName(getCurrChanIdx(), -1, 1)

NOSUPPTEXT = "UNSUPPORTED"
def getCurrentChannelPlugin():
    plugin = getPlugin("")
    if plugin == None:
        return NOSUPPTEXT, None
    return plugin.getID(), plugin


#endregion

#region Nav helpers
def NextKnobMode():
    global _KnobMode
    _KnobMode += 1
    if(_KnobMode > 3):
        _KnobMode = 0    
    RefreshKnobMode()

def PatternPageNav(moveby):
    global _PatternPage
    pageSize = getPatternModeLength()
    newPage = _PatternPage + moveby 
    #if(newPage > 4):
    #    newPage = 4
    if(newPage < 1):
        newPage = 1
    pageOffs = (newPage-1) * pageSize # first page will = 0
    if(0 <= pageOffs <= _PatternCount ): # allow next page when there are patterns to show
        _PatternPage = newPage
    RefreshPageLights()

def ChannelPageNav(moveby):
    global _ChannelPage
    pageSize = getPatternModeLength()
    newPage = _ChannelPage + moveby 
    #if(newPage > 4):
    #    newPage = 4
    if(newPage < 1):
        newPage = 1
    pageOffs = (newPage-1) * pageSize # first page will = 0
    if(0 <= pageOffs <= _ChannelCount ): # allow next page when there are patterns to show
        _ChannelPage = newPage
    RefreshPageLights()
    ui.crDisplayRect(0, pageOffs, 0, pageSize, _rectTime, CR_ScrollToView + CR_HighlightChannelName)


def NavNotesList(val):
    global _NoteIdx
    _NoteIdx += val
    if( _NoteIdx > (len(NotesList)-1)  ):
        _NoteIdx = 0
    elif( _NoteIdx < 0 ):
        _NoteIdx = len(NotesList)-1



def NavLayout(val):
    global _PadMode
    oldIdx = _PadMode.LayoutIdx
    newIdx = (oldIdx + val) % len(_Layouts)

    _PadMode.LayoutIdx = newIdx 


def NavOctavesList(val):
    global _OctaveIdx
    _OctaveIdx += val
    if( _OctaveIdx > (len(OctavesList)-1) ):
        _OctaveIdx = 0
    elif( _OctaveIdx < 0 ):
        _OctaveIdx = len(OctavesList)-1


def NavSetList(val):
    global _PadMode 

    newNavSetIdx = _PadMode.AllowedNavSetIdx + val 
    
    if(newNavSetIdx > (len(_PadMode.AllowedNavSets)-1)):
        newNavSetIdx = 0
    elif(newNavSetIdx < 0):
        newNavSetIdx = len(_PadMode.AllowedNavSets)-1

    _PadMode.NavSet = TnfxNavigationSet( _PadMode.AllowedNavSets[newNavSetIdx])
    _PadMode.AllowedNavSetIdx = newNavSetIdx 
    RefreshGridLR()

    RefreshMacros()
    RefreshNavPads()

def RefreshGridLR():
    navSet = _PadMode.NavSet.Index
    SendCC(IDLeft, SingleColorOff)
    SendCC(IDRight, SingleColorOff)

    if(navSet in [nsDefault, nsDefaultDrum] ):
        SendCC(IDLeft, SingleColorFull)
    elif(navSet in [nsScale, nsDefaultDrumAlt]):
        SendCC(IDRight, SingleColorFull)
    elif(navSet == nsUDLR):
        SendCC(IDLeft, SingleColorFull)
        SendCC(IDRight, SingleColorFull)


def NavScalesList(val):
    global _ScaleIdx
    _ScaleIdx += val
    if( _ScaleIdx > (len(ScalesList)-1) ):
        _ScaleIdx = 0
    elif( _ScaleIdx < 0 ):
        _ScaleIdx = len(ScalesList)-1

def NavNoteRepeatLength(val):
    global _NoteRepeatLengthIdx
    _NoteRepeatLengthIdx += val
    if(_NoteRepeatLengthIdx > (len(BeatLengthDivs) -1) ):
        _NoteRepeatLengthIdx = 0
    elif(_NoteRepeatLengthIdx < 0):
        _NoteRepeatLengthIdx = len(BeatLengthDivs) - 1
    DisplayTimedText2('Repeat Note', BeatLengthNames[_NoteRepeatLengthIdx], '')
#endregion


#region UI Helpers
def ShowPianoRoll(showVal, bSave, bUpdateDisplay = False, chanIdx = -1):
    global _PatternMap 
    currVal = 0

    if(len(_PatternMap) > 0):
        selPat = GetPatternMapActive() # _PatternMap[_CurrentPattern-1]  # 0 based
        currVal = selPat.ShowPianoRoll
    
    isShowing = ui.getVisible(widPianoRoll)
    isFocused = ui.getFocused(widPianoRoll)

    if(showVal <= 0) and (isShowing) and (chanIdx == -1):
        ui.hideWindow(widPianoRoll)

    #if(showVal == 1):
    #    ShowChannelRack(1, True)
    
    #ui.showWindow(widChannelRack)
    #chanNum = channels.selectedChannel(0, 0, 0)

#    ui.openEventEditor(channels.getRecEventId(
#        chanNum) + REC_Chan_PianoRoll, EE_PR)

    if(showVal == -1):  # toggle
        if(currVal == 0):
            showVal = 1
        else:
            showVal = 0

    if(showVal == 1):
        if(chanIdx == -1):
            ui.showWindow(widPianoRoll)
        else:
            ui.openEventEditor(channels.getRecEventId(chanIdx) + REC_Chan_PianoRoll, EE_PR)

        if(bSave):
            if(len(_PatternMap) > 0):
                selPat.ShowPianoRoll = 1
    else:
        ui.hideWindow(widPianoRoll)
        if(bSave):
            if(len(_PatternMap) > 0):
                selPat.ShowPianoRoll = 0

    #if(showVal == 0): # make CR active
    #    ShowChannelRack(_ShowChanRack)
        

    if(bUpdateDisplay):
        DisplayTimedText('Piano Roll: ' + _showText[showVal])

def ShowChannelSettings(showVal, bSave, bUpdateDisplay = False):
    global _PatternMap
    global _ShowCSForm
    currVal = 0

    if(len(_PatternMap) > 0):
        selPat = GetPatternMapActive() # _PatternMap[_CurrentPattern-1]  # 0 based
        currVal = selPat.ShowChannelSettings

    if(showVal == -1):  # toggle
        if(currVal == 0):
            showVal = 1
        else:
            showVal = 0
    
    chanNum = channels.selectedChannel(0, 0, 0)
    channels.showCSForm(chanNum, showVal)
    if(showVal == 0): # make CR active
        ShowChannelRack(_ShowChanRack)
        _ShowCSForm = False
    else:
        _ShowCSForm = True

    if(bUpdateDisplay):
        DisplayTimedText('Chan Sett: ' + _showText[showVal])

    if(bSave):
        if(len(_PatternMap) > 0):
            selPat.ShowChannelSettings = showVal

def ShowChannelEditor(showVal, bSave, bUpdateDisplay = False):
    global _ChannelMap
    global _ShowChannelEditor

    if(len(_ChannelMap) <= 0):
        return

    ShowChannelRack(1)
    chanNum =  channels.selectedChannel(0, 0, 0)
    chanType = channels.getChannelType(chanNum)
    showEditor = _ChannelMap[chanNum].ShowChannelEditor
    showCSForm = _ChannelMap[chanNum].ShowCSForm
    
    if( chanType in [CT_Hybrid, CT_GenPlug] ):
        currVal = showEditor
    elif(chanType in [CT_Layer, CT_AudioClip, CT_Sampler, CT_AutoClip]):
        currVal = showCSForm

    if(showVal == -1):  # toggle
        if(currVal <= 0): #might be -1 initially
            showVal = 1
            _ShowChannelEditor = True 
        else:
            showVal = 0
            _ShowChannelEditor = False 

    if( chanType in [CT_Hybrid, CT_GenPlug] ):
        channels.showEditor(chanNum, showVal)
        if(bSave):
            _ChannelMap[chanNum].ShowChannelEditor = showVal
    elif(chanType in [CT_Layer, CT_AudioClip, CT_Sampler, CT_AutoClip]):
        channels.showCSForm(chanNum, showVal)
        if(bSave):
            _ChannelMap[chanNum].ShowCSForm = showVal

    if(bUpdateDisplay):
        DisplayTextBottom('ChanEdit: ' + _showText[showVal])

    if(showVal == 0): # make CR active when closed
        ShowChannelRack(_ShowChanRack)


def ShowPlaylist(showVal, bUpdateDisplay = False):
    global _ShowPlaylist
    
    isShowing = ui.getVisible(widPlaylist)
    isFocused = ui.getFocused(widPlaylist)

    if(isShowing == 1) and (isFocused == 1) and (showVal <= 0):
        showVal = 0
    else:
        showVal = 1
    
    if(showVal == 1):        
        ui.showWindow(widPlaylist)
        ui.setFocused(widPlaylist)
    else:
        ui.hideWindow(widPlaylist)
    
    _ShowPlaylist = showVal    

    if(bUpdateDisplay): 
        DisplayTimedText('Playlist: ' + _showText[showVal])

def ShowMixer(showVal, bUpdateDisplay = False):
    global _ShowMixer

    isShowing = ui.getVisible(widMixer)
    isFocused = ui.getFocused(widMixer)

    #if(showVal == -1): # toggle
        #if(_ShowMixer == 1):
    if(isShowing == 1) and (isFocused == 1) and (showVal <= 0):
        showVal = 0
    else:
        showVal = 1

    if(showVal == 1):
        ui.showWindow(widMixer)
        ui.setFocused(widMixer)
    else:
        ui.hideWindow(widMixer)

    _ShowMixer = showVal    

    if(bUpdateDisplay): 
        DisplayTimedText('Mixer: ' + _showText[showVal])

def ShowChannelRack(showVal, bUpdateDisplay = False):
    global _ShowChanRack 

    isShowing = ui.getVisible(widChannelRack)
    isFocused = ui.getFocused(widChannelRack)

    if(showVal == -1): #toggle
        if(isShowing):
            showVal = 0
            if(not isFocused):      # if not focused already, activate it
                showVal = 1
        else:
            showVal = 1

    if(showVal == 1):
        ui.showWindow(widChannelRack)
        ui.setFocused(widChannelRack)
    else:
        ui.hideWindow(widChannelRack)

    _ShowChanRack = showVal

    if(bUpdateDisplay):
        DisplayTimedText('Chan Rack: ' + _showText[showVal])

def ShowBrowser(showVal, bUpdateDisplay = False):
    global _ShowBrowser

    #temp until bug gets fixed.
    DisplayTimedText('Browser: NYI')
    return 

    isShowing = ui.getVisible(widBroswer)
    isFocused = ui.getFocused(widBroswer)

    if(showVal == -1): # toggle
        if(isShowing == 1) and (isFocused == 1):
            showVal = 0
        else:
            showVal = 1

    if(showVal == 1):
        ui.showWindow(widBrowser)
    else:
        ui.hideWindow(widBrowser)

    _ShowBrowser = showVal
    
    if(bUpdateDisplay):
        DisplayTimedText('Browser: ' + _showText[showVal])


def UpdateMenuItems(level):
    global _menuItems
    pluginName, plugin = getCurrentChannelPlugin()
    if(not plugins.isValid(channels.selectedChannel())):
        _menuItems.clear()
        _menuItems.append('UNSUPPORTED')
        return 
#    print('l', level, pluginName, plugin)
    if(level == 0):
        _menuItems = list(plugin.ParameterGroups.keys()) #['Set Params']
    elif(level == 1):
        group = list(plugin.ParameterGroups.keys())[_menuHistory[level-1]]
        _menuItems = plugin.getParamNamesForGroup(group)
    if(level > 0) and (_menuBackText not in _menuItems):
        _menuItems.append(_menuBackText)

def ShowMenuItems():
    global _menuItems
    pageLen = 3 # display is 3 lines tall
    selPage = _menuItemSelected//pageLen
    selItemOffs = _menuItemSelected % pageLen    
    pageFirstItemOffs = (selPage * pageLen) 
    
    level = len(_menuHistory)
    UpdateMenuItems(level)
    maxItem = len(_menuItems)-1
    displayText = ['','','']

    for i in range(0,3):
        item = i + pageFirstItemOffs
        if(item < maxItem):
            preText = ' '
            if(_menuItemSelected == item):
                preText = '-->'
        elif(item == maxItem):
            preText = ''
            if(_menuItemSelected == item):
                preText = '-->'
                if(level > 0):
                    preText = '<--'
        
        if(level == MAXLEVELS):
            displayText[i] = "[" + _menuItems[item].upper() + "]" 
        elif(item < len(_menuItems)):
            if(_menuItems[item] == NOSUPPTEXT):
                preText = ''
            displayText[i] = preText + _menuItems[item]
        else:
            displayText[i] = ''

    DisplayTextAll(displayText[0], displayText[1], displayText[2])
    
def ShowMenuItems2():
    pageLen = 3 # display is 3 lines tall
    selPage = int(_menuItemSelected/pageLen) # 
    selItemOffs = _menuItemSelected % pageLen    #
    pageFirstItemOffs = (selPage * pageLen)       # 
    maxItem = len(_menuItems)
    displayText = ['','','']
    
    for i in range(0,3):
        item = i + pageFirstItemOffs
        if(item < maxItem):
            preText = '...'
            if(_menuItemSelected == item):
                preText = '-->'
            displayText[i] = preText + _menuItems[item]

    DisplayTextAll(displayText[0], displayText[1], displayText[2])
#endregion

# work area/utility        
def prn(lvl, *objects):
    if(not _debugprint):
        return
    prefix = prnLevels[lvl][1]
    if(_DebugPrn and (lvl >= _DebugMin)) or (lvl == lvlA):
        print(prefix, *objects)    

def SetTop():
    if(ui.getFocused(widPlaylist)):
        SetPlaylistTop()
    elif(ui.getFocused(widPianoRoll)):
        SetPianoRollTop()

def SetPlaylistTop():
    ui.scrollWindow(widPlaylist, 1)
    ui.scrollWindow(widPlaylist, 1, 1)

def SetPianoRollTop():
    ui.scrollWindow(widPianoRoll, 1)
    ui.scrollWindow(widPianoRoll, 1, 1)


def ShowNote(note, isOn = True):
    if(note == -1):
        return

    dim = dimDefault
    if(isOn):
        dim = dimFull
    
    noteDict = _NoteMapDict
    
    if(note in noteDict):
        pads = noteDict[note]
        for pad in pads:
            SetPadColor(pad,  getPadColor(pad), dim)

def UpdateWindowStates():
    global _ShowPlaylist
    global _ShowChanRack
    global _ShowMixer
    global _ShowBrowser
    global _ShowPianoRoll
    global _ShowChannelEditor
    global _ShowCSForm

    if isNoMacros():
        return 

    chanIdx = getCurrChanIdx()

    _ShowMixer = ui.getVisible(widMixer)
    _ShowPlaylist = ui.getVisible(widPlaylist)
    _ShowChanRack = ui.getVisible(widChannelRack)
    _ShowBrowser = ui.getVisible(widBrowser)
    _ShowPianoRoll = ui.getVisible(widPianoRoll)
    
    if(chanIdx >= len(_ChannelMap)):
        UpdateChannelMap()

    _ShowChannelEditor = _ChannelMap[chanIdx].ShowChannelEditor
    _ShowCSForm = _ChannelMap[chanIdx].ShowCSForm

    RefreshWindowStates()

def RefreshWindowStates():

    if isNoMacros():
        return 

    if(_ShowChanRack):
        shd = shDark
        if(ui.getFocused(widChannelRack)):
            shd = shLight
        SetPadColor(pdMacros[1], getShade(_MacroList[1].PadColor, shd), dimFull)
    else:
        SetPadColor(pdMacros[1], getShade(_MacroList[1].PadColor, shDark), dimDefault)

    if(_ShowPlaylist):
        shd = shDark
        if(ui.getFocused(widPlaylist)):
            shd = shLight
        SetPadColor(pdMacros[2], getShade(_MacroList[2].PadColor, shd), dimFull)
    else:
        SetPadColor(pdMacros[2], getShade(_MacroList[2].PadColor, shDark), dimDefault)

    if(_ShowMixer):
        shd = shDark
        if(ui.getFocused(widMixer)):
            shd = shLight
        SetPadColor(pdMacros[3], getShade(_MacroList[3].PadColor, shd), dimFull)
    else:
        SetPadColor(pdMacros[3], getShade(_MacroList[3].PadColor, shDark), dimDefault)

    
def setSnapMode(newmode):
    i = 0
    mode = ui.getSnapMode()
    while(mode < newmode):
        ui.snapMode(1)  # inc by 1
        mode = ui.getSnapMode()
        i += 1
        if i > 100:
            return
    while(mode > newmode):
        ui.snapMode(-1)  # inc by 1
        mode = ui.getSnapMode()
        i += 1
        if i > 100:
            return 

modePattern = TnfxPadMode('Pattern', MODE_PATTERNS, IDStepSeq, False)
modePatternAlt = TnfxPadMode('Pattern Alt', MODE_PATTERNS, IDStepSeq, True)
modeNote = TnfxPadMode('Note', MODE_NOTE, IDNote, False)
modeNoteAlt = TnfxPadMode('Note Alt', MODE_NOTE, IDNote, True)
modeDrum = TnfxPadMode('Drum', MODE_DRUM, IDDrum, False)
modeDrumAlt = TnfxPadMode('Drum Alt', MODE_DRUM, IDDrum, True)
modePerform = TnfxPadMode('Perform', MODE_PERFORM, IDPerform, False)
modePerformAlt = TnfxPadMode('Perform Alt', MODE_PERFORM, IDPerform, True)

def isNoNav():
    return _PadMode.NavSet.NoNav

def isNoMacros():
    return (_PadMode.NavSet.MacroNav == False) or (isNoNav())



def DrumPads():
    return getDrumPads(_isAltMode, isNoNav(), _PadMode.LayoutIdx)

def NotePads():
    if(isNoNav()):
        return pdAllPads
    else:
        return pdWorkArea

def InititalizePadModes():
    global _PadMode 
    global modePattern
    global modePatternAlt
    global modeNote
    global modeNoteAlt
    global modeDrum
    global modeDrumAlt
    global modePerform
    global modePerformAlt


    # _PadMode will be assigned one of these on mode change
    modePattern.NavSet = TnfxNavigationSet(nsDefault)
    modePattern.AllowedNavSets = [nsDefault, nsUDLR, nsNone]

    modePatternAlt.NavSet = TnfxNavigationSet(nsDefault)
    modePatternAlt.AllowedNavSets = [nsDefault, nsUDLR, nsNone]

    modeNote.NavSet = TnfxNavigationSet(nsScale)
    modeNote.AllowedNavSets = [nsScale, nsDefault, nsUDLR]

    modeNoteAlt.NavSet = TnfxNavigationSet(nsScale)
    modeNoteAlt.AllowedNavSets = [nsScale, nsDefault, nsUDLR]

    modeDrum.NavSet = TnfxNavigationSet(nsDefaultDrum)
    modeDrum.AllowedNavSets = [nsDefaultDrum, nsUDLR]

    modeDrumAlt.NavSet = TnfxNavigationSet(nsDefaultDrumAlt)
    modeDrumAlt.AllowedNavSets = [nsDefaultDrumAlt, nsDefaultDrum, nsUDLR, nsNone]

    modePerform.NavSet = TnfxNavigationSet(nsNone)
    modePerform.AllowedNavSets = [nsNone, nsDefault, nsUDLR]

    modePerformAlt.NavSet = TnfxNavigationSet(nsNone)
    modePerformAlt.AllowedNavSets = [nsNone, nsDefault, nsUDLR]

    _PadMode = modePattern

def SetChannelParam(offset, value):
    plugins.setParamValue(value, offset, getCurrChanIdx(), -1)

def clonePluginParams(srcPlugin, destPlugin):
    # enumerate the plugins list. no deepcopy :(  
    for param in srcPlugin.Parameters:
        newParam = TnfxParameter(param.Offset, param.Caption, param.Value, param.ValueStr, param.Bipolar, param.StepsAfterZero)
        if(newParam.Caption in ['?', ''] and newParam.Offset > -1):
            if(plugins.isValid(channels.selectedChannel())):
                newParam.Caption = plugins.getParamName(newParam.Offset, channels.selectedChannel(), -1) # -1 denotes not mixer

        destPlugin.addParamToGroup(param.GroupName, newParam)
    for knob in range(4):
        param1 = srcPlugin.User1Knobs[knob] 
        param2 = srcPlugin.User2Knobs[knob] 
        newParam1 = TnfxParameter(param1.Offset, param1.Caption, param1.Value, param1.ValueStr, param1.Bipolar, param1.StepsAfterZero)
        newParam2 = TnfxParameter(param2.Offset, param2.Caption, param2.Value, param2.ValueStr, param2.Bipolar, param2.StepsAfterZero)

        if(param1.Caption in ['?', ''] and param1.Offset > -1):
            if(plugins.isValid(channels.selectedChannel())):
                newParam1.Caption = plugins.getParamName(param1.Offset, channels.selectedChannel(), -1) # -1 denotes not mixer

        if(param2.Caption in ['?', ''] and param2.Offset > -1):
            if(plugins.isValid(channels.selectedChannel())):
                newParam2.Caption = plugins.getParamName(param2.Offset, channels.selectedChannel(), -1) # -1 denotes not mixer

        destPlugin.assignParameterToUserKnob(KM_USER1, knob, newParam1 )
        destPlugin.assignParameterToUserKnob(KM_USER2, knob, newParam2 )
    return destPlugin

def getPlugin(pluginName):
    ''' Loads the plugin from either (in this order):

        1) from _knownPlugins if it exists
        2) from customized TnfxPLugin (ie. FLKeys, FLEX) if exists. add entry to _knownPlugins
        3) real-time loading of params with non empty names. adds an entry to _knownPlugins
        
        NOTE: passing an empty string will load the current channel's plugin
    '''
    global _knownPlugins

    if(not plugins.isValid(channels.selectedChannel())):
        return None 

    basePluginName, userPluginName = getCurrChannelPluginNames()
    pl = TnfxChannelPlugin(basePluginName, userPluginName) # in case we don't find one later...

    if(pl.getID() in _knownPlugins.keys()):
        return _knownPlugins[pl.getID()]
    
    if(basePluginName in CUSTOM_PLUGINS.keys()):
        clonePluginParams(CUSTOM_PLUGINS[basePluginName], pl)
    else:
        pl = getPluginInfo(-1)
    
    #print('pl', pl)
            
    _knownPlugins[pl.getID()] = pl
    return pl 

