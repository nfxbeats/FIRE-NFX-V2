# name=FIRE-NFX-V2
# supportedDevices=FL STUDIO FIRE
#
# author: Nelson F. Fernandez Jr. <nfxbeats@gmail.com>
#
# develoment started:   11/24/2021
# first public beta:    07/13/2022
#
# thanks to: HDSQ, TayseteDj, CBaum83, DAWNLIGHT, Jaimezin, a candle, Miro and Image-Line
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

# fix
widPlugin = 5
widPluginEffect = 6
widPluginGenerator = 7

# not safe to use as of Aug 20, 2022
# import _thread 
# _task = True
# def task(a,b):
#     while (_task) and (a < b):
#         a += 1
#         print('working...', a)
#         time.sleep(1)
#     print('done')
# def startTask():
#     id = _thread.start_new_thread(task, (0,100))
#     print('task started', id)

from harmonicScales import *
from fireNFX_DefaultSettings import *
from fireNFX_Classes import *
from fireNFX_Defs import * 
from fireNFX_PadDefs import *
from fireNFX_Utils import * 
from fireNFX_Display import *
from fireNFX_PluginDefs import *


#region globals
dimDim = Settings.DIM_DIM
dimDefault = Settings.DIM_NORMAL
dimBright = Settings.DIM_BRIGHT
dimFull = 0


_debugprint = Settings.SHOW_PRN
_rectTime = Settings.DISPLAY_RECT_TIME_MS
_ShiftHeld = False
_FLChannelFX = False
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
if(Settings.TOGGLE_CR_AND_BROWSER):
    _ShowBrowser = 0

_ShowPianoRoll = 0
_ShowChannelEditor = 0
_ShowCSForm = 0
_showText = ['OFF', 'ON']

_WalkerChanIdx = -1

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
_ScaleIdx = Settings.SCALE
_ScaleDisplayText = ""
_ScaleNotes = list()
_lastNote =-1
_NoteIdx = Settings.NOTE_NAMES.index(Settings.ROOT_NOTE)
_NoteRepeat = False
_NoteRepeatLengthIdx = BeatLengthsDefaultOffs
_isRepeating = False

_SnapIdx = InitialSnapIndex
_OctaveIdx = OctavesList.index(Settings.OCTAVE)
_ShowChords = False
_ChordNum = -1
_ChordInvert = 0 # 0 = none, 1 = 1st, 2 = 2nd
_ChordTypes = ['Normal', '1st Inv', '2nd Inv']
_Chord7th = False
_VelocityMin = 100
_VelocityMax = 126
_DebugPrn = True
_DebugMin = lvlD


# MACROS DEFINED HERE
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
    global _task
    _task = False
    time.sleep(1)
    
    #print('deInit')

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

    # no event I know of to hook into song length change so I'll check here
    if(_PadMode.Mode == MODE_PERFORM) and (_isAltMode):
        CheckAndHandleSongLenChanged()

    # determines if we need show note playback
    if(Settings.SHOW_PLAYBACK_NOTES):
        if(transport.isPlaying() or transport.isRecording()):
            if(_PadMode.Mode in [MODE_DRUM, MODE_NOTE]):
                HandleShowNotesOnPlayback()


def getNoteForChannel(chanIdx):
    return channels.getCurrentStepParam(chanIdx, mixer.getSongStepPos(), pPitch)

def HandleShowNotesOnPlayback():
    global _PadMode
    global  _lastNote
    if (_PadMode.Mode in [MODE_DRUM, MODE_NOTE]):
        note = getNoteForChannel(getCurrChanIdx()) # channels.getCurrentStepParam(getCurrChanIdx(), mixer.getSongStepPos(), pPitch)
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
    global _PadMode
    global _isAltMode
    #print('OnRefresh', flags)
    if(flags == HW_CustomEvent_ShiftAlt):
        # called by HandleShiftAlt
        RefreshShiftAltButtons()
        # if(_ShiftHeld):
        #     RefreshShiftedStates() 
        if(_DoubleTap) and (_ShiftHeld):
            ShowScriptDebug()

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
            if(not isFPCActive()):
                _PadMode = modeDrumAlt
                _isAltMode = True
                SetPadMode()
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

_tempMsg = ''
_tempMsg2 = ''
def OnSendTempMsg(msg, duration):
    global _tempMsg 
    global _tempMsg2 
    _tempMsg = msg
    # if(' - ' in msg):
    #     _tempMsg = msg
    #     print('TempMsg', "[{}]".format(_tempMsg), duration, 'inMenu', ui.isInPopupMenu())
    # else:
    #     _tempMsg2 = msg
    #     print('TempMsg2', "[{}]".format(_tempMsg2), duration, 'inMenu', ui.isInPopupMenu())

def isKnownPlugin():
    return getCurrChanPluginID() in _knownPlugins.keys()

_prevCtrlID = 0
_proctime = 0
_DoubleTap = False
def OnMidiIn(event):
    global _ShiftHeld
    global _AltHeld
    global _PadMap
    global _proctime
    global _prevCtrlID
    global _DoubleTap

    ctrlID = event.data1 # the low level hardware id of a button, knob, pad, etc

    if(event.data2 > 0):
        prevtime = _proctime
        _proctime = time.monotonic_ns() // 1000000
        elapsed = _proctime-prevtime
        if (_prevCtrlID == ctrlID):
            #print(ctrlID, _prevCtrlID, 'proc', _proctime, prevtime, 'elapsed', elapsed)
            _DoubleTap = (elapsed < 220)
        else:
            _prevCtrlID = ctrlID
            _DoubleTap = False
        #print('dbltap', _DoubleTap)

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
        pName, plugin = getCurrChanPlugin()
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
            col = Settings.PAD_PRESSED_COLOR

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
                event.handled = HandlePads(event, padNum)
                return 
            elif(_PadMode.Mode == MODE_NOTE): # handles on and off for NOTES
                event.handled = HandlePads(event, padNum)
                return 
            elif(_PadMode.Mode == MODE_PERFORM): # handles on and off for PERFORMANCE
                if(pMap.Pressed == 1):
                    event.handled = HandlePlaylist(event, padNum)
                else:
                    event.handled = True 
                return 
            elif(_PadMode.Mode == MODE_PATTERNS): # if STEP/PATTERN mode, treat as controls and not notes...
                if(pMap.Pressed == 1): # On Pressed
                    event.handled = HandlePads(event, padNum)
                    return 
                else:
                    event.handled = True #prevents a note off message
                    return 

        if(not isNoNav()):
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
        if(_AltHeld):
            patterns.setPatternColor(patterns.patternNumber(), channels.getChannelColor(newChanIdx))
            # 
            for plt in _PlaylistMap:
                if(plt.ChanIdx == newChanIdx):
                    playlist.setTrackColor(plt.FLIndex, channels.getChannelColor(newChanIdx))
                    UpdatePlaylistMap(_isAltMode)
                    break

            RefreshAll()
            return True

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

        #close previous windows
        channels.showEditor(oldChanIdx, 0)   
        channels.showCSForm(oldChanIdx, 0)
        UpdateWindowStates()

        if(ui.getVisible(widPianoRoll)): #closes previous instance
            ShowPianoRoll(1, True, False, newChanIdx)

    if(not _ShiftHeld):
        mixerTrk = channels.getTargetFxTrack(newChanIdx)
        mixer.setTrackNumber(mixerTrk, curfxScrollToMakeVisible)
        ui.crDisplayRect(0, newChanIdx, 0, 1, _rectTime, CR_ScrollToView + CR_HighlightChannels)
        ui.miDisplayRect(mixerTrk, mixerTrk, _rectTime, CR_ScrollToView)

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
        newSongPos = prgMap[padOffs].SongPosAbsTicks
        transport.setSongPos(newSongPos, SONGLENGTH_ABSTICKS)
    else:
        # bar number
        newSongPos = getAbsTicksFromBar(prgMap.BarNumber) 
        transport.setSongPos(newSongPos, SONGLENGTH_ABSTICKS)

    if(_AltHeld):
        markerOffs = padOffs + 1
        arrangement.addAutoTimeMarker(prgMap.SongPosAbsTicks, Settings.MARKER_PREFIX_TEXT.format(markerOffs))

    if(_ShiftHeld):
        select = True
        if( arrangement.selectionEnd() > -1 ): #already selected so lets deselect
            select = False
            
        if(len(prgMap.Markers) > 0):
            newSongPos = prgMap.Markers[0].SongPosAbsTicks
        else:
            newSongPos = prgMap[padOffs].SongPosAbsTicks
        transport.setSongPos(newSongPos, SONGLENGTH_ABSTICKS)
        selEnd = transport.getSongLength(SONGLENGTH_ABSTICKS)
        # select to the next marker or song end
        arrangement.jumpToMarker(1, select)
        pos = transport.getSongPos(SONGLENGTH_ABSTICKS)
        addedEndMarker = False
        if pos > newSongPos: # if there is another marker later in time we can use it for the end of selection
            selEnd = pos
        else:
            arrangement.addAutoTimeMarker(selEnd, 'END') # add temp end marker
            addedEndMarker = True
        
        transport.setSongPos(newSongPos, SONGLENGTH_ABSTICKS)
        transport.markerSelJog(0)

        if addedEndMarker:
            arrangement.addAutoTimeMarker(selEnd, 'END') # remove temp end marker
        
    RefreshAllProgressAndMarkers()

    return True

def HandlePads(event, padNum):  
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
                    patt, pMap = getPatternNumFromPad(padNum)
                    #print('v', patt, pMap)
                    if(pMap != None):
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
    
    if(macIdx == 4):
        if(Settings.UNDO_STYLE == 0):
            general.undoUp()
        else:
            general.undo()
    elif(macIdx == 1):
        ShowChannelRack(-1)
        if(Settings.TOGGLE_CR_AND_BROWSER):
            if(_ShowChanRack == 0):
                ui.showWindow(widBrowser)
            RefreshBrowserDisplay()    
    elif(macIdx == 2):
        ShowPlaylist(-1)
    elif(macIdx == 3):
        ShowMixer(-1)        
    elif(macIdx == 0):
        DisplayTimedText('Reset Windows')
        transport.globalTransport(FPT_F12, 1)  # close all...

        # enable the following lines to have it re-open windows 
        if(Settings.REOPEN_WINDOWS_AFTER_CLOSE_ALL):
            ShowBrowser(1)
            ShowMixer(1)
            ShowChannelRack(1)
            ShowPlaylist(1)
        #else:
        #    ShowMixer(0)
        #    ShowChannelRack(0)
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
            _isRepeating = True
            setSnapMode(BeatLengthSnap[_NoteRepeatLengthIdx])
            ms = getBeatLenInMS(BeatLengthDivs[_NoteRepeatLengthIdx])
            device.repeatMidiEvent(event, ms, ms)
    
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
    if(len(_ChannelMap) != channels.channelCount()):
        UpdateChannelMap()
    channelMap = _ChannelMap
    return channelMap

def getPatternMap():
    if(len(_PatternMap) != patterns.patternCount() ):
        UpdatePatternMap()

    patternMap = _PatternMap
    if(_isAltMode):
        patternMap = _PatternSelectedMap
    return patternMap

def getPatternNumFromPad(padNum):
    patternMap = getPatternMap()
    pattIdx = -1
    pattNum = -1
    pattOffset = getPatternOffsetFromPage()
    patternStripA, patternStripB = getPatternPads()
    if(padNum in patternStripA):
        pattIdx = patternStripA.index(padNum)
    elif(padNum in patternStripB):
        pattIdx = patternStripB.index(padNum)
    newPatIdx = pattIdx + pattOffset
    if(newPatIdx < len(patternMap)):
        if(pattIdx >= 0):
            if( len(patternMap) >= (newPatIdx + 1) ):
                pattNum = patternMap[newPatIdx].FLIndex
        if(pattIdx > -1):
            return pattNum, patternMap[newPatIdx]
    else:
        return patterns.patternNumber(), None

def HandlePatternStrip(padNum):
    global _PatternMap
    global _PatternSelectedMap

    patternStripA, patternStripB = getPatternPads()
    pattNum, pMap = getPatternNumFromPad(padNum)
    if(pattNum == -1):
        return True

    if(patterns.patternNumber() != pattNum): 
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
                UpdatePatternModeData() 
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
    # elif(_AltHeld):
    #     if(ctrlID == IDPatternUp):
    #         DisplayTimedText('vZoom Out')
    #         ui.verZoom(2)
    #         SetTop()
    #     else:
    #         DisplayTimedText('vZoom In')
    #         ui.verZoom(-2)
    #         SetTop()
    else:
        newPattern = patterns.patternNumber() + moveby
        #print('newpat', newPattern, patterns.patternCount())
        if( 0 <= newPattern <= patterns.patternCount()):   #if it's a valid spot then move it
            patterns.jumpToPattern(newPattern)
        else:
            setPatternName = False
            if(Settings.PROMPT_NAME_FOR_NEW_PATTERN):
                patterns.findFirstNextEmptyPat(FFNEP_FindFirst)
                # if we dont have a valid name, use the DEFAULT
                if(patterns.patternNumber() > patterns.patternCount() ):
                    setPatternName = True
            else:
                patterns.findFirstNextEmptyPat(FFNEP_DontPromptName)
                setPatternName = True 
            
            if(setPatternName):
                newPatt = patterns.patternNumber()
                pattName = Settings.PATTERN_NAME.format(newPatt)
                patterns.setPatternName(newPatt, pattName)

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
    SetKnobMode()
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
    recEventID = channels.getRecEventId(chanNum)

    if(ctrlID == IDSelect) and (useparam != None): # tweaking via Select Knob

        if(not _FLChannelFX) and (isGenPlug()): # for plugins/generators
            recEventID += REC_Chan_Plugin_First

        knobres = 1/64
        shiftres = 1/128
        altres = 1/8
        if(Settings.BROWSER_STEPS >= 1):
            knobres = 1/Settings.BROWSER_STEPS
        if(Settings.SHIFT_BROWSER_STEPS >= 1):
            shiftres = 1/Settings.SHIFT_BROWSER_STEPS
        if(Settings.ALT_BROWSER_STEPS >= 1):
            altres = 1/Settings.ALT_BROWSER_STEPS

        if (useparam.StepsAfterZero > 0):
            knobres = 1/useparam.StepsAfterZero
        if(_ShiftHeld):
            knobres = shiftres
        elif(_AltHeld):
            knobres = altres
        return HandleKnobReal(recEventID + useparam.Offset,  event.outEv, useparam.Caption + ': ', useparam.Bipolar, 0, knobres)


    if _KnobMode == KM_CHANNEL :
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
        pluginName, plugin = getCurrChanPlugin()
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
    #UpdateMarkerMap()                
    UpdateProgressMap(False)
    RefreshProgress()

_ShiftLock = False 
_AltLock = False 

def HandleShiftAlt(event, ctrlID):
    global _ShiftHeld
    global _AltHeld
    global _ShiftLock
    global _AltLock

    if(ctrlID == IDShift):
        _ShiftHeld = (event.data2 > 0)
        _ShiftLock = _DoubleTap
    elif(ctrlID == IDAlt):
        _AltHeld = (event.data2 > 0)
        _AltLock = _DoubleTap
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
            if(checkFLVersionAtLeast('20.99.0')):
                if(playlist.getPerformanceModeState() == 1): # in performance mode
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
    global _turnOffMetronomeOnNextPlay
    if(event.data1 == IDPatternSong):
        if(_ShiftHeld):
            pass
        else:
            transport.setLoopMode()

    if(event.data1 == IDPlay):
        if _turnOffMetronomeOnNextPlay and ui.isMetronomeEnabled():
            _turnOffMetronomeOnNextPlay = False
            transport.globalTransport(FPT_Metronome, 1)
        if(transport.isPlaying()):
            transport.stop()
            ResetBeatIndicators()
        else:
            transport.start()

    if(event.data1 == IDStop):
        transport.stop()
        ResetBeatIndicators()
        UpdateMarkerMap()
        transport.setSongPos(0.0)
        RefreshModes()

    if(event.data1 == IDRec):
        transport.record()

    RefreshTransport()
    

    return True 

_turnOffMetronomeOnNextPlay = False 
def HandleShifted(event):
    global _turnOffMetronomeOnNextPlay
    ctrlID = event.data1
    if(ctrlID == IDAccent):
        pass 
    elif(ctrlID == IDSnap):
        transport.globalTransport(FPT_Snap, 1)
    elif(ctrlID == IDTap):
        if(ui.isMetronomeEnabled()):
            transport.globalTransport(FPT_TapTempo, 1)
        else:
            transport.globalTransport(FPT_Metronome, 1)
            _turnOffMetronomeOnNextPlay = True 
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

_lastBrowserFolder = ''
def HandleSelectWheel(event, ctrlID):
    global _menuItemSelected
    global _menuItems
    global _chosenItem
    global _lastBrowserFolder 

    jogNext = 1
    jogPrev = 127


    if(ui.getFocused(widBrowser)):
        if(ctrlID == IDSelect):
            caption = ''
            if(event.data2 == jogNext):
                #ui.down()
                caption = ui.navigateBrowserMenu(1, _ShiftHeld)
            elif(event.data2 == jogPrev):
                #ui.up()
                caption = ui.navigateBrowserMenu(0, _ShiftHeld)
            
            RefreshBrowserDisplay(caption)

            # ftype = ui.getFocusedNodeFileType()
            # actions = ''
            # if(ftype <= -100):
            #     actions = '[]'
            # else:
            #     actions = '[] S+[] A+[]'
            # DisplayTimedText2('Browser', caption, actions )
        elif(ctrlID == IDSelectDown):
            if(ui.getFocusedNodeFileType() <= -100):
                _lastBrowserFolder = '>' + ui.getFocusedNodeCaption()
                ui.enter()
            else:
                ui.selectBrowserMenuItem() # brings up menu
                if(_ShiftHeld) or (_AltHeld):
                    ui.down()
                    if(_AltHeld):
                        ui.down()
                    ui.enter()            
        return True 
    elif(not _ShowMenu):
        if(ctrlID == IDSelectDown):
            #HandleBrowserButton()
            ui.enter()
        else:
            numIdx = -1
            name = ''
            window = ''

            if(event.data2 == jogNext):
                if(ui.getFocused(widMixer)):
                    if (not _ShiftHeld):
                        ui.right()
                    else:
                        ui.down()
                else:
                    if (not _ShiftHeld):
                        ui.down()
                    else:
                        ui.right()

            elif(event.data2 == jogPrev):
                if(ui.getFocused(widMixer)):
                    if (not _ShiftHeld):
                        ui.left()
                    else:
                        ui.up()
                else:
                    if(not _ShiftHeld):
                        ui.up()
                    else:
                        ui.left()
            
            time.sleep(0.02) # if no delay, it reads the previous info
            
            if(ui.getFocused(widMixer)):
                window = 'Mixer'    
                numIdx = mixer.trackNumber()
                name = mixer.getTrackName(numIdx) 
            elif(ui.getFocused(widChannelRack)):
                window = 'Channel Rack'
                numIdx = getCurrChanIdx()
                name = channels.getChannelName(numIdx)
            elif(ui.getFocused(widPlaylist)):
                window = 'Playlist'
            elif(ui.getFocused(widPianoRoll)):
                window = 'Piano Roll'

            if(numIdx > -1):                    
                DisplayTimedText2(window, "{}-{}".format(numIdx, name), '')
            else:
                DisplayTimedText2(window, '', '')
                
           
        return True

    ShowMenuItems()
    paramName, plugin = getCurrChanPlugin()
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
                #groupName = list(plugin.ParameterGroups.keys())[_menuHistory[0]]
                groupName =  plugin.getGroupNames()[_menuHistory[0]]
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
    global _ShowMenu 
    global _menuItems
    global _menuItemSelected
    global _menuHistory
    global _FLChannelFX
    global _ShowBrowser

    # in a menu
    if (ui.isInPopupMenu()):
        ui.closeActivePopupMenu()

    # regular File browser....
    if(not _ShiftHeld) and (not _AltHeld) and (not _ShowMenu):
        if(_ShowBrowser == 1):
            ShowBrowser(0)
            if (Settings.TOGGLE_CR_AND_BROWSER):
                ShowChannelRack(1)
            
        else:
            if (Settings.TOGGLE_CR_AND_BROWSER):
                ShowChannelRack(0)
            ShowBrowser(1)

        RefreshBrowserDisplay()
        RefreshWindowStates()
        
        return True

    #
    # para /settings menus    
    _ShowMenu = not _ShowMenu
    if(_ShowMenu):
        _FLChannelFX = _ShiftHeld
        _menuHistory.clear()
        _menuItemSelected = 0
        SendCC(IDBrowser, SingleColorFull)  #SingleColorHalfBright
        ShowMenuItems()
        if(_FLChannelFX):
            channels.showEditor(getCurrChanIdx(), 1) 
            ui.right()
    else:
        if(_FLChannelFX):
            channels.showEditor(getCurrChanIdx(), 0) 
        _FLChannelFX = False
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
        NavigateFLMenu('', _AltHeld)
    elif(padIndex == pdUp):
        if(ui.isInPopupMenu()) and (ui.getFocused(widBrowser)) and (_ShiftHeld): 
            print('x')
            NavigateFLMenu(',UUUUE')
        else:
            ui.up()
    elif(padIndex == pdDown):
        if(ui.isInPopupMenu()) and (ui.getFocused(widBrowser)) and (_ShiftHeld): 
            print('y')
            NavigateFLMenu(',UUUE')
        else:
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
    prn(lvlA, 'RefreshAll')
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
        UpdatePatternModeData()
        # if(True) and (not transport.isPlaying()):
        #     UpdatePlaylistMap(False, True)
        #     playlist.deselectAll()
        #     playlist.selectTrack(1)
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
        SendCC(IDAlt, SingleColorFull)
    # elif(_AltLock):
    #     SendCC(IDAlt, SingleColorHalfBright)
    else:
        SendCC(IDAlt, SingleColorOff)

    if(_ShiftHeld):
        RefreshShiftedStates()
        RefreshChannelStrip(False)
    # elif(_ShiftLock):
    #     SendCC(IDShift, DualColorHalfBright2)
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
    prn(lvlA, 'RefreshMacros') 
    if isNoMacros():
        return 

    for pad in pdMacros:
        idx = pdMacros.index(pad)
        #color =  colMacros[idx]
        SetPadColor(pad, _MacroList[idx].PadColor, dimDefault)

    UpdateWindowStates()
    #RefreshWindowStates()

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
                if(Settings.ROOT_NOTE_COLOR == cChannel):
                    color = FLColorToPadColor(channels.getChannelColor(getCurrChanIdx()))
                else:
                    color = Settings.ROOT_NOTE_COLOR

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

        #if(Settings.ALT_DRUM_MODE_BANKS == False):
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
            if(isGenPlug(chan)): # _ChannelMap[chan].ChannelType == CT_GenPlug):
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

def  RefreshKnobMode():
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
        muteColorA = cNotMuted # cNotMuted is dimWhite
        muteColorB = cNotMuted

        plMapA = plMapToShow[plStartIdx + padOffs]
        flIdxA = plMapA.FLIndex 
        if(playlist.isTrackSelected(flIdxA)):
            dimA = dimBright
        SetPadColor(padTrackA, plMapA.Color, dimA) 
        _PadMap[padTrackA].Color = plMapA.Color
        _PadMap[padTrackA].FLIndex = flIdxA
        if(playlist.isTrackMuted(flIdxA)):
            muteColorA = cMuted
        SetPadColor(padMuteA, muteColorA, dimBright) 
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
                muteColorB = cMuted 
            SetPadColor(padMuteB, muteColorB, dimBright) 
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
        
        dimA = dimDim
        dimB = dimDim

        if(currChan == channel.FLIndex):
            if(ui.getFocused(widPlugin) or ui.getFocused(widPluginGenerator)):
                dimA = dimFull
            elif(ui.getVisible(widPlugin) or ui.getVisible(widPluginGenerator)):
                dimA = dimBright
            if(ui.getFocused(widPianoRoll)):
                dimB = dimFull
            elif(ui.getVisible(widPianoRoll)):
                dimB = dimDim
            SetPadColor(padAIdx, channel.Color, dimA)
            SetPadColor(padBIdx, cWhite, dimB)
        else:
            SetPadColor(padAIdx, channel.Color, dimA)
            SetPadColor(padBIdx, cDimWhite, dimB)
        
        if(channel.FLIndex >= 0):
            if(_ShiftHeld): # Shifted will display Mute states
                col = cNotMuted
                if(_KnobMode == KM_MIXER):
                    if (channel.Mixer.FLIndex > -1):
                        if(mixer.isTrackMuted(channel.Mixer.FLIndex)):
                            col = cMuted
                else:
                    if(channels.isChannelMuted(channel.FLIndex)):
                        col = cMuted

                SetPadColor(padBIdx, col, dimBright) #cWhite, dimBright
            elif(currMixerNum == channels.getTargetFxTrack(channel.FLIndex)): 
                #not Shifted
                if(currChan == channel.FLIndex):
                    SetPadColor(padBIdx, cWhite, dimDefault)
                else:
                    SetPadColor(padBIdx, cDimWhite, dimDefault)
            else: #not shifted and not an fx track match
                SetPadColor(padBIdx, cOff, dimDefault)
        else:
            SetPadColor(padBIdx, cOff, dimDefault)

    #SelectAndShowChannel(currChan)
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
    # chanName = channels.getChannelName(chanIdx)
    # mixerName = mixer.getTrackName(mixer.trackNumber())
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
            SetPadColor(pad, cBlue, dimDefault)
        elif(pad == pdTab):
            SetPadColor(pad, cCyan, dimBright)
        elif(pad == pdEsc):
            SetPadColor(pad, cRed, dimDefault)
        elif(pad == pdEnter):
            SetPadColor(pad, cGreen, dimDefault)
        else:
            SetPadColor(pad, cWhite, dimDefault)


def RefreshProgress():
    progMap = []
    if(transport.getLoopMode() == 0): # PATTERN
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

def UpdatePlaylistMap(selectedOnly = False, mapExtra = True):
    global _PlaylistMap
    global _PlaylistSelectedMap
    global _PadMap

    _PlaylistMap.clear()
    _PlaylistSelectedMap.clear()
    blankTracks = 0

    for plt in range(playlist.trackCount()):
        flIdx = plt + 1
        color = FLColorToPadColor( playlist.getTrackColor(flIdx) )
        name = playlist.getTrackName(flIdx)
        # if(name[:6] == "Track "):
        #     blankTracks += 1
        # else:
        #     blankTracks == 0

        plMap = TnfxPlaylistTrack(flIdx, name, color)
        plMap.Muted = playlist.isTrackMuted(flIdx)
        plMap.Selected = playlist.isTrackSelected(flIdx)

        # if(mapExtra) and (not transport.isPlaying()):
        #     playlist.deselectAll()
        #     playlist.selectTrack(flIdx)
        #     chanIdx = channels.channelNumber()
        #     mixerIdx = mixer.trackNumber()
        #     plMap.ChanIdx = chanIdx
        #     plMap.MixerIdx = mixerIdx
            
        _PlaylistMap.append(plMap)
        if(plMap.Selected):
            _PlaylistSelectedMap.append(plMap)
        
        # if(blankTracks > 9): # the max number of sequential "Track " (blank Tracks)
        #     break 
    
    if(mapExtra):
        playlist.deselectAll()
        playlist.selectTrack(1)

def UpdatePatternMap():
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
    # selBarStart = getBarFromAbsTicks(selStart)
    # selBarEnd =  getBarFromAbsTicks(selEnd)
    # if(selEnd > -1): #this will be -1 if nothing selected
    #     songLenAbsTicks = selEnd - selStart
    #     songLenBars = selBarEnd - selBarStart
    # else:
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
        transport.setSongPos(1) # by starting at the end, we wrap around and find the first marker
        for m in range(markerCount):
            markerNum = arrangement.jumpToMarker(1, False)
            while (markerNum > m): #workaround
                markerNum = arrangement.jumpToMarker(-1, False)
            markerName = arrangement.getMarkerName(markerNum)
            markerTime = arrangement.currentTime(1) # returns in ticks
            m = TnfxMarker(markerNum, markerName, markerTime)
            _MarkerMap.append(m)

_WalkerName = 'Walker'    

def UpdateChannelMap():
    global _ChannelMap
    global _ChannelCount
    global _CurrentChannel
    global _ChannelSelectedMap
    global _WalkerChanIdx

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

        if(chanMap.Name == _WalkerName):
            _WalkerChanIdx = chanMap.FLIndex

        _ChannelMap.append(chanMap)
        if(chanMap.Selected):
            _ChannelSelectedMap.append(chanMap)

def UpdatePatternModeData():
    global _CurrentChannel
    global _ChannelCount
    ResetPadMaps(False)
    UpdatePatternMap()
    UpdateChannelMap()
    #UpdatePadMap()

def ResetBeatIndicators():
    for i in range(0, len(BeatIndicators) ):
        SendCC(BeatIndicators[i], SingleColorOff)

#endregion 

#region Helper function 
def isFPCChannel(chanIdx):
    if(isGenPlug(chanIdx)): #_ChannelMap[chanIdx].ChannelType == CT_GenPlug):
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
    global _ScrollTo
    ui.showWindow(widChannelRack)
    chanIdx = getCurrChanIdx() # channels.channelNumber()
    SelectAndShowChannel(chanIdx)
    ui.copy 
    name = patterns.getPatternName(FLPattern)
    color = patterns.getPatternColor(FLPattern)
    patterns.findFirstNextEmptyPat(FFNEP_DontPromptName)
    newpat = patterns.patternNumber()
    if("#" in name):
        name = name.split('#')[0]
    name += "#{}".format(newpat)
    patterns.setPatternName(newpat, name)
    patterns.setPatternColor(newpat, color)
    patterns.jumpToPattern(newpat)
    SelectAndShowChannel(chanIdx)
    ui.paste 
    _ScrollTo = True
    RefreshModes()    
    

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
                    elif(Settings.SHOW_ALL_MATCHING_CHORD_NOTES):
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

# def GetChannelMapActive():
#     return _ChannelMap[_CurrentChannel-1]

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

def getCurrChanPluginID():
    name, plugin = getCurrChanPlugin()
    if(plugin == None):
        return ""
    return plugin.getID()

def getCurrChanPluginNames():
    return plugins.getPluginName(getCurrChanIdx(), -1, 0), plugins.getPluginName(getCurrChanIdx(), -1, 1)


def getCurrChanPlugin():
    plName = ""
    if(_FLChannelFX):
        plName = FLEFFECTS
    plugin = getPlugin(plName)
    if plugin == None:
        return NOSUPPTEXT, None
    return plugin.getID(), plugin


#endregion

#region Nav helpers
def SetKnobMode(mode=-1):
    global _KnobMode
    if(mode == -1):
        _KnobMode += 1
    else:
        _KnobMode = mode
    if(-1 < _KnobMode > 3): #if(_KnobMode > 3):
        _KnobMode = KM_CHANNEL    
    #print('km', _KnobMode)
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

def ForceNavSet(navSet):
    if(navSet in _PadMode.AllowedNavSets):
        newIdx = _PadMode.AllowedNavSets.index(navSet)
        ForceNavSetIdx(newIdx)

def ForceNavSetIdx(navSetIdx):
    global _PadMode
    navset = _PadMode.AllowedNavSets[navSetIdx]
    _PadMode.NavSet = TnfxNavigationSet(navset)
    _PadMode.AllowedNavSetIdx = navSetIdx 
    RefreshGridLR()
    RefreshMacros()
    RefreshNavPads()
    RefreshModes()



def NavSetList(val):
    global _PadMode 

    newNavSetIdx = _PadMode.AllowedNavSetIdx + val 
    
    if(newNavSetIdx > (len(_PadMode.AllowedNavSets)-1)):
        newNavSetIdx = 0
    elif(newNavSetIdx < 0):
        newNavSetIdx = len(_PadMode.AllowedNavSets)-1

    ForceNavSetIdx(newNavSetIdx)
    # _PadMode.NavSet = TnfxNavigationSet( _PadMode.AllowedNavSets[newNavSetIdx])
    # _PadMode.AllowedNavSetIdx = newNavSetIdx 
    # RefreshGridLR()

    # RefreshMacros()
    # RefreshNavPads()

def RefreshGridLR():
    navSet = _PadMode.NavSet.NavSetID
    SendCC(IDLeft, SingleColorOff)
    SendCC(IDRight, SingleColorOff)

    if(navSet in [nsDefault, nsDefaultDrum] ):
        SendCC(IDLeft, SingleColorHalfBright)
    elif(navSet in [nsScale, nsDefaultDrumAlt]):
        SendCC(IDRight, SingleColorHalfBright)
    elif(navSet == nsUDLR):
        SendCC(IDLeft, SingleColorHalfBright)
        SendCC(IDRight, SingleColorHalfBright)

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

    RefreshChannelStrip()

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

    RefreshChannelStrip()

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

    RefreshChannelStrip()

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

_resetAutoHide = False
_prevNavSet = -1
def ShowBrowser(showVal, bUpdateDisplay = False):
    global _ShowBrowser
    global _resetAutoHide
    global _prevNavSet

    _resetAutoHide = (ui.isBrowserAutoHide()==1) or _resetAutoHide
    wasHidden = not ui.getVisible(widBrowser) # curr value
    hasFocus = ui.getFocused(widBrowser)

    if(_resetAutoHide):
        ui.setBrowserAutoHide(False)  # if hidden it will become visible

    if(showVal == -1): # toggle
        if(hasFocus):
            showVal = 0
        else:
            showVal = 1        
        
    if(showVal == 1):
        if(Settings.TOGGLE_CR_AND_BROWSER):
            ui.hideWindow(widChannelRack)  
        ui.showWindow(widBrowser)
        _ShowBrowser = 1
        if(Settings.FORCE_UDLR_ON_BROWSER):
            _prevNavSet = _PadMode.NavSet.NavSetID
            ForceNavSet(nsUDLR)

    else:
        if(_resetAutoHide):
            ui.setBrowserAutoHide(True)
            ui.hideWindow(widBrowser)
            _resetAutoHide = False
        ShowChannelRack(1) # to take focus off the Browser
        _ShowBrowser = 0
        if(Settings.FORCE_UDLR_ON_BROWSER):
            if(_prevNavSet > -1):
                ForceNavSet(_prevNavSet)
                _prevNavSet = -1
    
    if(bUpdateDisplay):
        DisplayTimedText('Browser: ' + _showText[showVal])


_menuAssign = TnfxMenuItems('Assign Knobs', 0)
_menuAssign.addSubItem( TnfxMenuItems('Knob-1') )
_menuAssign.addSubItem( TnfxMenuItems('Knob-2') )
_menuAssign.addSubItem( TnfxMenuItems('Knob-3') )
_menuAssign.addSubItem( TnfxMenuItems('Knob-4') )
_menuParams = TnfxMenuItems('Browse Params', 0)
_menus = []
_menus.append(_menuAssign)
_menus.append(_menuParams)

def UpdateMenuItems(level):
    global _menuItems
    pluginName, plugin = getCurrChanPlugin()
    if(plugin == None):
        _menuItems.clear()
        _menuItems.append('UNSUPPORTED')
        return 
    if(level == 0):
        _menuItems = plugin.getGroupNames() # list(plugin.ParameterGroups.keys()) #['Set Params']
        _menuItems.append('[Assign Knobs]')
    elif(level == 1):
        selText = _menuItems[_menuItemSelected]
        if(selText == '[Assign Knobs]'):
            _menuItems = ['Knob-1', 'Knob-2', 'Knob-3', 'Knob-4',]
        else:
            group = plugin.getGroupNames()[_menuHistory[level-1]]
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
            pass
            #displayText[i] = "[" + _menuItems[item].upper() + "]" 
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
    
    prn(lvlA, 'UpdateWindowStates')

    _ShowMixer = ui.getVisible(widMixer)
    _ShowPlaylist = ui.getVisible(widPlaylist)
    _ShowChanRack = ui.getVisible(widChannelRack)
    _ShowBrowser = ui.getFocused(widBrowser)
    if(Settings.TOGGLE_CR_AND_BROWSER) and (_ShowBrowser):
        if _ShowChanRack == 1:
            ShowChannelRack(0)
    _ShowPianoRoll = ui.getVisible(widPianoRoll)

    if(Settings.AUTO_SWITCH_KNOBMODE):
        if(ui.getFocused(widMixer)):
            SetKnobMode(KM_MIXER) 
        if(ui.getFocused(widChannelRack)):
            SetKnobMode(KM_CHANNEL) 
        
    
    if isNoMacros():
        return 

    chanIdx = getCurrChanIdx()
    if(chanIdx >= len(_ChannelMap)):
        UpdateChannelMap()

    _ShowChannelEditor = _ChannelMap[chanIdx].ShowChannelEditor
    _ShowCSForm = _ChannelMap[chanIdx].ShowCSForm

    RefreshWindowStates()

def RefreshBrowserDisplay(caption = ''):
    if(ui.getFocused(widBrowser)):
        ftype = ui.getFocusedNodeFileType()
        actions = ''
        if(caption == ''):
            caption = ui.getFocusedNodeCaption()
        if(ftype <= -100):
            actions = '[Open/Close]'
        else:
            actions = '[]  S[]  A[]'
        DisplayTimedText2('Browser', caption, actions )
    else:
        RefreshDisplay()



def RefreshBrowserButton():
    if(ui.getFocused(widBrowser)):
        SendCC(IDBrowser, SingleColorHalfBright)
        RefreshBrowserDisplay()
    elif(_ShowMenu):
        SendCC(IDBrowser, SingleColorFull)
    else:
        SendCC(IDBrowser, SingleColorOff)  # 

def RefreshWindowStates():
    prn(lvlA, 'RefreshWindowStates')

    RefreshChannelStrip()
    RefreshBrowserButton()

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

def SetChannelFXParam(offset, value):
    chanNum = getCurrChanIdx()
    recEventID = channels.getRecEventId(chanNum)    
    return general.processRECEvent(recEventID + offset, value, REC_UpdateValue)

def GetChannelFXParam(offset):
    chanNum = getCurrChanIdx()
    recEventID = channels.getRecEventId(chanNum)    
    value = 0
    return general.processRECEvent(recEventID + offset, value, REC_GetValue)


def getChannelType(chan = -1):
    if(chan < 0):
        chan = getCurrChanIdx()
    return channels.getChannelType(chan)

def isGenPlug(chan = -1):
    return (getChannelType(chan) in [CT_GenPlug])

def isSampler(chan = -1):
    return (getChannelType(chan) in [CT_Sampler])

def isAudioClip(chan = -1):
    return (getChannelType(chan) in [CT_AudioClip])

def getPlugin(pluginName):
    ''' Loads the plugin from either (in this order):

        1) from _knownPlugins if it exists
        2) from customized TnfxPLugin (ie. FLKeys, FLEX) if exists. add entry to _knownPlugins
        3) real-time loading of params with non empty names. adds an entry to _knownPlugins
        
        NOTE: passing an empty string will load the current channel's plugin
    '''
    global _knownPlugins

    if(pluginName == "") and (isSampler()):
        return plSampler

    if(pluginName == FLEFFECTS):
        plFLChanFX.ChannelType = getChannelType()
        return plFLChanFX

    if(not plugins.isValid(channels.selectedChannel())):
        return None 

    basePluginName, userPluginName = getCurrChanPluginNames()
    pl = TnfxChannelPlugin(basePluginName, userPluginName) # in case we need a new instance

    if(pl.getID() in _knownPlugins.keys()):
        return _knownPlugins[pl.getID()]
    
    if(basePluginName in CUSTOM_PLUGINS.keys()):
        pl = CUSTOM_PLUGINS[basePluginName].copy() #clonePluginParams(CUSTOM_PLUGINS[basePluginName], pl)
    else:
        pl = getPluginInfo(-1)
    
    _knownPlugins[pl.getID()] = pl
    return pl 

def getChannelRecEventID():
    chanNum = getCurrChanIdx()
    return channels.getRecEventId(chanNum)

arp1 = 1446
arp2= 1232
arp4 = 1024
arp8 = 820
arp16 = 648
arp32 = 502 # 450
arpTimes = {'Beat': arp1, 'Half-Beat':arp2, '4th-Beat':arp4, '8th-Beat':arp8, '16th-Beat':arp16, '32nd-Beat': arp32}

def SetArp(enabled, arpTime = 1024, arpRange = 1, arpRepeat = 2):
    if(enabled):
        SetChannelFXParam(REC_Chan_Arp_Mode, 1)
        SetChannelFXParam(REC_Chan_Arp_Time, arpTime)
        SetChannelFXParam(REC_Chan_Arp_Range, arpRange)
        SetChannelFXParam(REC_Chan_Arp_Repeat, arpRepeat)
    else:
        SetChannelFXParam(REC_Chan_Arp_Mode, 0)

# plFLChanFX.addParamToGroup('ARPEGGIATOR', TnfxParameter( REC_Chan_Arp_Mode, 'ARP Mode', 0, '', False)) # NO Value return
# plFLChanFX.addParamToGroup('ARPEGGIATOR', TnfxParameter( REC_Chan_Arp_Time, 'ARP Time', 0, '', False))
# plFLChanFX.addParamToGroup('ARPEGGIATOR', TnfxParameter( REC_Chan_Arp_Gate, 'ARP Gate', 0, '', False))
# plFLChanFX.addParamToGroup('ARPEGGIATOR', TnfxParameter( REC_Chan_Arp_Range, 'ARP Range', 0, '', False))
# plFLChanFX.addParamToGroup('ARPEGGIATOR', TnfxParameter( REC_Chan_Arp_Repeat, 'ARP Repeat', 0, '', False))
# plFLChanFX.addParamToGroup('ARPEGGIATOR', TnfxParameter( REC_Chan_Arp_Chord, 'ARP Chord', 0, '', False)) # NO Value return 

def OnMidiOutMsg(event):
    #	Called for short MIDI out messages sent from MIDI Out plugin - 
    # (event properties are limited to: handled, status, data1, data2, port, midiId, midiChan, midiChanEx)
    print('MidiOutMsg:', event.handled, event.status, event.data1, event.data2, event.port, event.midiId, event.midiChan, event.midiChanEx )

def OpenMainMenu(menuName = 'Patterns'):
    res = False
    NavigateFLMenu('', False)
    msg = _tempMsg

    if(msg == menuName):
        return True
    
    for i in range(20):
        ui.left()
        time.sleep(Settings.MENU_DELAY)
        msg = _tempMsg
        match1 = 'Menu - {}'.format(menuName)
        match2 = '{} -'.format(menuName)
        if(msg.startswith(match1)) or (msg.startswith(match2)):
            res = True
            break
    return res

def ClonePattern():
    NavigateFLMainMenu('Patterns', 'Clone')

def MenuNavTo(menuItemStartsWith, verticalNav = True, hasMenuItems = False):
    visitedMenuItems = []
    matched = False
    msg = ''
    res = False 
    while (not matched):
        msg = _tempMsg   # getting a copy of this value in case it changes
        matched = msg.startswith(menuItemStartsWith)
        if(not matched):
            if verticalNav:
                ui.down()
            else:
                ui.right
            time.sleep(Settings.MENU_DELAY)
        else:
            if(hasMenuItems):
                ui.right()
            else:
                ui.enter()
        if (msg not in visitedMenuItems):        
            visitedMenuItems.append(msg)
        else:
            res = True
            break
    return True

def NavMainMenu(mainMenu = 'File', subMenuNav = ['New']):
    if OpenMainMenu(mainMenu):
        lastItem = subMenuNav[-1]
        print(lastItem)
        for menuItem in subMenuNav:
            print('>', menuItem)
            if not MenuNavTo(menuItem, True, (menuItem != lastItem)):
                return False
        return True        
    else:
        return False

      




def NavigateFLMainMenu(menu1 = 'Patterns', menu2 = 'Clone', menu3 = ''):
    visited = []
    OpenMainMenu(menu1)
    if(not ui.isInPopupMenu()):
        ui.down()
        time.sleep(0.25)
    match = '{} - {}'.format(menu1, menu2)
    matched = False
    msg = ''
    while (not matched):
        msg = _tempMsg   # getting a copy of this value in case it changes
        #print('tm looking for ', "[{}]".format(match))
        matched = msg.startswith(match)
        if(not matched):
            #print('up', msg)
            ui.down()
            time.sleep(Settings.MENU_DELAY)
        else:
            ui.enter()
        if (msg not in visited):        
            #print('adding', msg)
            visited.append(msg)
        else:
            break

    return matched, msg, _tempMsg, (msg in visited)


    menuMoves = MainMenu.get(firstMenu)
    NavigateFLMenu(firstMenu)

