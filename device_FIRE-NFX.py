# name=FIRE-NFX-V2
# supportedDevices=FL STUDIO FIRE

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

#import sys 



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
_menuItems = ['Option 1','Option 2','Option 3','Option 4','Option 5']
_selectedItem = 0
_menuItemSelected = _selectedItem




_menu_ProgressPadLen = ['1 beat', '1 bar', '2 bars', '4 bars']
_ProgressPadLenIdx = 1 


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

#endregion 

#region FL MIDI API Events
def OnInit():
    prn(lvlE, 'OnInit()')

    
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
    SendCC(IDKnob1, SingleColorFull)    

    InititalizePadModes()

    RefreshPageLights()             # PAD Mutes akak Page
    ResetBeatIndicators()           # 
    RefreshPadModeButtons()
    RefreshShiftAlt()
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

def ClearAllPads():
    # clear the Pads
    for pad in range(0,64):
        SetPadColor(pad, 0x000000, 0)
    
def OnDoFullRefresh():
    prn(lvlA, 'OnDoFullRefresh')    



def OnIdle():
    global _lastNote
    global _SongLen
    global _PadMode

    if(_ShiftHeld):
        RefreshShiftedStates() 
    
    if(_PadMode.Mode == MODE_PERFORM):
        if(_isAltMode):
            currSongLen = transport.getSongLength(SONGLENGTH_BARS)
            lenChanged = (currSongLen != _SongLen)
            _SongLen = currSongLen
            if(lenChanged):
                UpdateMarkerMap()
                UpdateProgressMap(True)
            RefreshProgress()

    if(DEFAULT_SHOW_PLAYBACK_NOTES): # this is note playback, make true to enable
        note = channels.getCurrentStepParam(getCurrChanIdx(), mixer.getSongStepPos(), pPitch)
        if (_PadMode.Mode in [MODE_DRUM, MODE_NOTE]):
            if(_lastNote != note):
                #prn(lvlA, 'last note', _lastNote) 
                ShowNote(_lastNote, False)
                if(note > -1) and (note in _NoteMap):
                    #prn(lvlA, 'note', note, 'last note', _lastNote) 
                    ShowNote(note, True)
                _lastNote = note
    
def OnMidiMsg(event):
    prn(lvlA, "OnMidiMsg()", event.data1, event.data2)
    
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
        # event.data1 += (self.CurrentKnobsMode - KnobsModeUser1) * 4 # so the CC is different for each user mode
        event.data1 += (_KnobMode-KM_USER1) * 4 # so the CC is different for each user mode
        prn(lvlA, 'UKM', _KnobMode, event.data1, event.data2, event.handled)
        device.processMIDICC(event)
        #event.handled = True
        prn(lvlA, 'UKM2', _KnobMode, event.data1, event.data2, event.handled)
        
        if (general.getVersion() > 9):
            BaseID = EncodeRemoteControlID(device.getPortNumber(), 0, 0)
            eventId = device.findEventID(BaseID + event.data1, 0)
            if eventId != 2147483647:
                s = device.getLinkedParamName(eventId)
                s2 = device.getLinkedValueString(eventId)
                DisplayTextAll(s, s2, '')        

def OnUpdateBeatIndicator(value):
    #prn(lvlE, 'OnUpdateBeatIndicator()')
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

def OnRefresh(flags):
    prn(lvlA, 'OnRefresh()', flags)
    #HW_Dirty_Patterns = 1024
    
    if(HW_Dirty_LEDs & flags):
        RefreshTransport()
        UpdateWindowStates()
    elif(HW_Dirty_FocusedWindow & flags):
        prn(lvlA, 'todo', 'handle focus window change')
        UpdateWindowStates()

    if(HW_Dirty_Performance & flags): # called when new channels or patterns added
        RefreshChannelStrip()
        RefreshPatternStrip()
        
    if(HW_Dirty_Patterns & flags):
        prn(lvlA, 'pattern event')
        HandlePatternChanges()
    if(HW_Dirty_ChannelRackGroup & flags):
        prn(lvlA, 'channel group changed', _ChannelCount, channels.channelCount())
        HandleChannelGroupChanges()    
    if(HW_ChannelEvent & flags):
        prn(lvlA, 'channel event', _CurrentChannel, channels.channelNumber())
        UpdateChannelMap()  
        if (_PadMode.Mode == MODE_DRUM):
            RefreshDrumPads()
        elif(_PadMode.Mode == MODE_PATTERNS):
            RefreshChannelStrip()
        elif(_PadMode.Mode == MODE_NOTE):
            RefreshNotes()

    if(HW_Dirty_Colors & flags):
        prn(lvlA, 'color change event')
        if (_PadMode.Mode == MODE_DRUM):
            RefreshDrumPads()
        elif(_PadMode.Mode == MODE_PATTERNS):
            RefreshChannelStrip()
    if(HW_Dirty_Tracks & flags):
        prn(lvlA, 'track change event')
        if(_PadMode.Mode == MODE_PERFORM):
            UpdatePlaylistMap(_isAltMode)
            RefreshPlaylist()
    if(HW_Dirty_Mixer_Sel & flags):
        prn(lvl0, 'mixer sel event')
def OnProjectLoad(status):
    #global PA5D_MODE 

    prn(lvlE, 'OnProjectLoad', status)
    # status = 0 = starting load?
    if(status == 0):
        DisplayTextAll('Project Loading', '-', 'Please Wait...')
    if(status >= 100): #finished loading
        SetPadMode()
        #UpdateMarkerMap()
        #_PadMode.Mode = MODE_PATTERNS
        RefreshPadModeButtons()        
        UpdatePatternModeData()
        RefreshAll()

def OnSendTempMsg(msg, duration):
    print('TempMsg', msg, duration)

def OnMidiIn(event):
    global _ShiftHeld
    global _AltHeld
    global _PadMap
    

    prn(lvlA, "OnMidiIn", event.data1, event.data2)
    #if (event.status == midi.MIDI_NOTEON) & (event.data2 <= 0) :
    #   event.status = midi.MIDI_NOTEOFF
    #    event.data2 = 0


    ctrlID = event.data1 # the low level hardware id of a button, knob, pad, etc

    # handle shift/alt
    if(ctrlID in [IDAlt, IDShift]):
        HandleShiftAlt(event, ctrlID)
        event.handled = True
        return

    if(ctrlID in KnobCtrls) and (_KnobMode in [KM_USER1, KM_USER2]):
        # short cutting these to be processed in OnMidiMsg() to use processMIDICC per the docs
        if (event.status in [MIDI_NOTEON, MIDI_NOTEOFF]): # to prevent the mere touching of the knob generating a midi note event.
            event.handled = True
        return

    # handle a pad
    if( IDPadFirst <=  ctrlID <= IDPadLast):
        padNum = ctrlID - IDPadFirst
        pMap = _PadMap[padNum]
        #prn(lvlA, 'Pad Detected', padNum, _PadMap[padNum].NoteInfo.MIDINote, _NoteMap[padNum])

        cMap = getColorMap()
        col = cMap[padNum].PadColor
        if (col == cOff):
            col = cRed

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
    prn(lvl0, 'Non Pad detected')
    # here we will get a message for on (press) and off (release), so we need to
    # determine where it's best to handle. For example, the play button should trigger 
    # immediately on press and ignore on release, so we code it that way

    if(event.data2 > 0): # Pressed
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
    prn(lvlA, 'OnNoteOn()', utils.GetNoteName(event.data1),event.data1,event.data2)

def OnNoteOff(event):
    prn(lvlA, 'OnNoteOff()', utils.GetNoteName(event.data1),event.data1,event.data2)

#endregion 

#region Handlers
def HandleChannelStrip(padNum, isChannelStripB):
    global _PatternMap
    global _ChannelMap
    global _CurrentChannel 
    global _PreviousChannel
    global _ChannelCount

    prevChanIdx = getCurrChanIdx() # channels.channelNumber()
    pageOffset = getChannelOffsetFromPage()
    padOffset = 0

    if(padNum in pdChanStripA):
        padOffset = pdChanStripA.index(padNum)
    elif(padNum in pdChanStripB):
        padOffset = pdChanStripB.index(padNum)
    
    chanIdx = padOffset + pageOffset
    channelMap = getChannelMap()
    channel = TnfxChannel(-1, "")
    if(chanIdx < len(channelMap) ):
        channel = channelMap[chanIdx]
    

    #pMap = _PadMap[padNum]
    newChanIdx = channel.FLIndex # pMap.FLIndex
    prn(lvlA, 'HandleChannelStrip', chanIdx, prevChanIdx, newChanIdx, _ShowPianoRoll)
    if (newChanIdx > -1): #is it a valid chan number?
        if(newChanIdx == prevChanIdx): # if it's already on the channel, toggle the windows
            if (isChannelStripB):
                ShowPianoRoll(-1, True) 
            else:
                ShowChannelEditor(-1, True) 
        else: #'new' channel, close the previous windows first
            prn(lvlA, 'hi')
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

    prn(lvlA, '----------------selectAndShowChan', newChanIdx, oldChanIdx, getCurrChanIdx(), 'CS', _ShowCSForm, 'CE', _ShowChannelEditor)


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

    mixerTrk = channels.getTargetFxTrack(newChanIdx)
    mixer.setTrackNumber(mixerTrk, curfxScrollToMakeVisible)
    ui.crDisplayRect(0, newChanIdx, 0, 1, 5000, CR_ScrollToView + CR_HighlightChannels)
    ui.miDisplayRect(mixerTrk, mixerTrk, 5000, CR_ScrollToView)

def HandlePatternStripOld(padNum):
    prn(lvlH, 'HandlePatternStrip()')
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
    prn(lvlA, 'HandlePlaylist()')

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
    prn(lvlA, prgMap)
    
    # 0..1  
    # newSongPos = padOffs / len(pdProgress)

    # ABS Ticks
    if(_ProgressPadLenIdx == 0):
        newSongPos = _ProgressMapSong[padOffs].SongPosAbsTicks
        transport.setSongPos(newSongPos, SONGLENGTH_ABSTICKS)
    else:
        # bar number
        
        #newSongPos = prgMap.BarNumber * getBeatLenInMS(0)
        #transport.setSongPos(newSongPos, SONGLENGTH_MS)
        newSongPos = getAbsTicksFromBar(prgMap.BarNumber) 
        prn(lvlA, "jumping to Bar", prgMap.BarNumber, _ProgressPadLenIdx, newSongPos)
        transport.setSongPos(newSongPos, SONGLENGTH_ABSTICKS)

    if(_AltHeld):
        markerOffs = padOffs + 1
        arrangement.addAutoTimeMarker(prgMap.SongPosAbsTicks, DEFAULT_MARKER_PREFIX_TEXT + str(markerOffs))

    if(_ShiftHeld):
        prn(lvlA, '', 'Selecting bars..')    
        
    RefreshAllProgressAndMarkers()

    return True

def HandlePads(event, padNum, pMap):  
    prn(lvlH, 'HandlePads', _CurrentPattern)

    # 'perfomance'  pads will need a pressed AND release...

    if(_PadMode.Mode == MODE_DRUM):
        if (padNum in DrumPads()):
            return HandleDrums(event, padNum)

    elif(_PadMode.Mode == MODE_NOTE):
        if(padNum in pdWorkArea):
            return HandleNotes(event, padNum)
        

    # some pads we only need on pressed event
    if(event.data2 > 0): # On Pressed

        #macros are handled in OnMidiIn

        #mode specific
        if(_PadMode.Mode == MODE_NOTE):
            if(padNum in pdNav):
                HandleNav(padNum)
        if(_PadMode.Mode == MODE_DRUM):
            if(padNum in pdFPCChannels):
                HandleDrums(event, padNum)
        elif(_PadMode.Mode == MODE_PATTERNS):
            if(padNum in pdPatternStripA):
                if(_AltHeld):
                    CopyPattern(pMap.FLIndex)
                else:
                    event.handled = HandlePatternStrip(padNum)
            elif(padNum in pdPatternStripB):
                event.handled = HandlePatternStrip(padNum)
            elif(padNum in pdChanStripA):
                event.handled = HandleChannelStrip(padNum, False)   
            elif(padNum in pdChanStripB):
                event.handled = HandleChannelStrip(padNum, True)


    return True

def HandleNav(padIdx):
    global _NoteRepeat
    global _SnapIdx
    prn(lvlA, 'HandleNav', padIdx, _PadMode.NavSet.NoteRepeat )
    hChanPads = _PadMode.NavSet.ChanNav
    hPresetNav = _PadMode.NavSet.PresetNav
    hUDLR = _PadMode.NavSet.UDLRNav
    hSnapNav = _PadMode.NavSet.SnapNav
    hNoteRepeat = _PadMode.NavSet.NoteRepeat
    hScaleNav = _PadMode.NavSet.ScaleNav
    hOctaveNav = _PadMode.NavSet.OctaveNav 

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

    if(hNoteRepeat):
        if(padIdx == pdNoteRepeatLength):
            NavNoteRepeatLength(1)
        if(padIdx == pdNoteRepeat):
            ToggleRepeat()

    if(hUDLR):
        if(padIdx in pdUDLR):
            HandleUDLR(padIdx)

    if(hOctaveNav) or (hScaleNav):
        #print('handle octave')
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

    #prn(lvlA, 'HandleNotes', padNum, event.data1, event.data2)


    event.data1 = _PadMap[padNum].NoteInfo.MIDINote

    if(0 < event.data2 < _VelocityMin):
        event.data2 = _VelocityMin
    elif(event.data2 > _VelocityMin):
        event.data2 = _VelocityMax

    
    if(_ShowChords):
        if (padNum in pdChordBar):
            #prn(lvlA, 'Chords', padNum)
            chordNum = pdChordBar.index(padNum)+1
            noteOn = (event.data2 > 0)
            noteVelocity = event.data2
            chan = getCurrChanIdx() # channels.channelNumber()
            HandleChord(chan, chordNum, noteOn, noteVelocity, _Chord7th, _ChordInvert)
            return True
        elif(padNum in pdChordFuncs) and (event.data2 > 0):
            prn(lvlA, 'ChordFunc', padNum)
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
            #prn(lvlA, 'ChordInv', _ChordInvert)
            
            return True 

    return False # to continue processing regular notes

def HandleDrums(event, padNum):
    global _isRepeating
    prn(lvlA, 'handle drums', 'in', event.data1, 'out', _PadMap[padNum].NoteInfo.MIDINote, 'Note Rpt', _NoteRepeat, _isRepeating)
    
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
            prn(lvlA, 'rpt', _NoteRepeatLengthIdx, BeatLengthNames[_NoteRepeatLengthIdx], ms, snap)
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
        prn(lvlA, 'updating note value')
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
    #patt = _PadMap[padNum].FLIndex
    patternMap = getPatternMap()
    pattIdx = -1
    pattOffset = getPatternOffsetFromPage()
    
    if(padNum in pdPatternStripA):
        pattIdx = pdPatternStripA.index(padNum)
    elif(padNum in pdPatternStripB):
        pattIdx = pdPatternStripB.index(padNum)

    pattNum = patternMap[pattIdx + pattOffset].FLIndex 
    print('pat', pattNum, pattIdx)
    if(patterns.patternNumber() != pattNum): # patt.FLIndex):
        if(padNum in pdPatternStripA):
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

def HandlePatternChanges():
    global _PatternCount
    global _CurrentPattern
    global _CurrentPage 

    #prn(lvlH, 'HandlePatternChanges()')

    if (_PatternCount > 0) and (_PadMode.Mode == MODE_PATTERNS): # do pattern mode
        
        if(_PatternCount != patterns.patternCount()):
            prn(lvlA, 'pattern added/removed')
            _PatternCount = patterns.patternCount()
            UpdatePatternModeData() 
        else:
            prn(lvlA, 'selected pattern changed', patterns.patternNumber())
            if _CurrentPattern != patterns.patternNumber():
                UpdatePatternModeData(patterns.patternNumber()) 
            else:
                UpdatePatternModeData() 
        _CurrentPattern = patterns.patternNumber()
        RefreshPatternStrip()
        

    if(patterns.patternCount() == 0) and (_CurrentPattern == 1): # empty project, set to 1
        _PatternCount = 1

    RefreshDisplay()

def HandlePattUpDn(ctrlID):
    #prn(lvlA, 'HandlePattUpDn()', ctrlID, _ShiftHeld, _AltHeld, _CurrentChannel)

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
            SetPlaylistTop()
        else:
            DisplayTimedText('vZoom In')
            ui.verZoom(-2)
            SetPlaylistTop()
    else:
        newPattern = patterns.patternNumber() + moveby
        if( 0 <= newPattern <= patterns.patternCount()):   #if it's a valid spot then move it
            patterns.jumpToPattern(newPattern)
    
    RefreshDisplay()
    RefreshNavPads()

    return True 

def HandleGridLR(ctrlID):
    prn(lvlA, 'HandleGridLR()', ctrlID)
    if(_AltHeld):
        if(ctrlID == IDBankL):
            DisplayTimedText('hZoom Out')
            ui.horZoom(2)
            SetPlaylistTop()
        else:
            DisplayTimedText('hZoom In')
            ui.horZoom(-2)
            SetPlaylistTop()
    else:
        if(ctrlID == IDBankL):
            NavSetList(-1)
        elif(ctrlID == IDBankR):
            NavSetList(1)
        RefreshModes()
    return True

def HandleKnobMode():
    #prn(lvlH, 'HandleKnobMode()')
    NextKnobMode()
    RefreshDisplay()
    return True

def HandleKnob(event, ctrlID):
    if(event.isIncrement != 1):
        event.inEv = event.data2
        if event.inEv >= 0x40:
            event.outEv = event.inEv - 0x80
        else:
            event.outEv = event.inEv
        event.isIncrement = 1

    value = event.outEv

    prn(lvlH, 'HandleKnob()', event.data1, event.data2, ctrlID, getCurrChanIdx(), _KnobMode)

    if _KnobMode == KM_CHANNEL :
        chanNum = getCurrChanIdx() #  channels.channelNumber()
        
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
    else: 
        if (event.status in [MIDI_NOTEON, MIDI_NOTEOFF]):
            event.handled = True
        return True # these knobs will be handled in OnMidiMsg prior to this.


def HandleKnobReal(recEventIDIndex, value, Name, Bipolar):
    knobres = 1/64
    currVal = device.getLinkedValue(recEventIDIndex)
    #prn(lvlH, 'HandleKnobReal', Name, value,  recEventIDIndex, Bipolar, currVal, knobres) 
    #general.processRECEvent(recEventIDIndex, value, REC_MIDIController)
    mixer.automateEvent(recEventIDIndex, value, REC_MIDIController, 0, 1, knobres) 
    currVal = device.getLinkedValue(recEventIDIndex)
    valstr = device.getLinkedValueString(recEventIDIndex)
    #DisplayTextTop('Value: ' + valstr )
    DisplayBar2(Name, currVal, valstr, Bipolar)
    return True

def HandlePage(event, ctrlID):
    prn(lvlH, 'HandlePage()', ctrlID)
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
    
    #prn(lvlH, 'HandleShiftAlt()')
    if(ctrlID == IDShift):
        _ShiftHeld = (event.data2 > 0)
    elif(ctrlID == IDAlt):
        _AltHeld = (event.data2 > 0)

    RefreshShiftAlt()

def HandlePadMode(event):
    global _isAltMode
    global _isShiftMode
    global _PadMode 

    #prn(lvlH, 'HandlePadMode')
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
            print(_PadMode.Name)
            

    elif(_AltHeld) and (_ShiftHeld): # Shift modes
        _isShiftMode = True 
        _isAltMode = True
        prn(lvl0, 'Shift+Alt Modes not ready')

    SetPadMode()

    return True
def HandleTransport(event):
    prn(lvlH, 'HandleTransport', event.data1)
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
    prn(lvlH, 'HandleShifted', event.data1)
    ctrlID = event.data1
    if(ctrlID == IDAccent):
        prn(lvl0, 'accent')
    elif(ctrlID == IDSnap):
        transport.globalTransport(FPT_Snap, 1)
    elif(ctrlID == IDTap):
        transport.globalTransport(FPT_TapTempo, 1)
    elif(ctrlID == IDOverview):
        prn(lvl0, 'overview')
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
    global _selectedItem

    prn(lvlA, 'HandleSelectWheel', ctrlID, event.data1, event.data2) 
    ShowMenuItems()
    jogNext = 1
    jogPrev = 127
    if(ctrlID == IDSelect):
        if(event.data2 == jogNext) and (_menuItemSelected < (len(_menuItems)-1) ):
            #prn(lvlA, 'mi', _menuItemSelected, '->', _menuItemSelected + 1 )
            _menuItemSelected += 1
        elif(event.data2 == jogPrev) and (_menuItemSelected > 0):
            _menuItemSelected += -1
        ShowMenuItems()
        return True 
    if(ctrlID == IDSelectDown):
        _selectedItem = _menuItemSelected
        return True 
def HandleBrowserButton():
    #global _ShowBrowser
    # using to trigger the menu for now
    global _ShowMenu 
    global _menuItems
    global _menuItemSelected

    _ShowMenu = not _ShowMenu
    prn(lvlA, 'Browser (MENU)', _ShowMenu, _menuItems[0], plugins.getName(_CurrentChannel))
    if(_ShowMenu):
        SendCC(IDBrowser, SingleColorHalfBright) 
        if( plugins.getPluginName(_CurrentChannel) == 'Strum GS-2'):
            prn(lvlA, 'Strum GS-2')
            _menuItems = ['Keyboard', 'Guitar', 'Loop']
            _menuItemSelected = 0
        ShowMenuItems()
    else:
        SendCC(IDBrowser, SingleColorOff) 
        RefreshDisplay()
    return True   
def HandleChord(chan, chordNum, noteOn, noteVelocity, play7th, playInverted):
    #prn(lvlA, 'HandleChord()', chordNum, noteVelocity)
    global _ChordNum
    global _ChordInvert
    global _Chord7th
    play7th = _Chord7th
    playInverted = _ChordInvert
    realScaleIdx = ScalesList[_ScaleIdx][0]

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
        #prn(lvlA, '..............chord', chordName, play7th, playInverted )
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
    prn(lvlA, 'HandleUDLR', padIndex)
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
    prn(lvlR, 'RefreshAll()')
    RefreshPageLights()
    RefreshModes()
    RefreshMacros()
    RefreshNavPads()
    RefreshDisplay()
    #FlushColorMap()
    return 

def RefreshModes():
    prn(lvlR, 'RefreshModes()')
    if(_PadMode.Mode == MODE_DRUM):
        RefreshDrumPads()
    elif(_PadMode.Mode == MODE_PATTERNS):
        UpdatePatternModeData(patterns.patternNumber())
        RefreshPatternStrip() 
        RefreshChannelStrip()
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

def RefreshShiftAlt():
    if(_AltHeld):
        SendCC(IDAlt, SingleColorFull)
    elif(_isAltMode):
        SendCC(IDAlt, SingleColorHalfBright)
    else:
        SendCC(IDAlt, SingleColorOff)

    if(_ShiftHeld):
        RefreshShiftedStates()
    else:  
        SendCC(IDShift, DualColorOff)
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

    SendCC(IDShift, DualColorFull1)

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
    
    
    RefreshGridLR()        

    if(isNoNav()):
        return

    for pad in pdNav :
        SetPadColor(pad, cOff, dimDefault)
    
    if(showUDLRNav):
        RefreshUDLR()
        return 

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
            SetPadColor(pdNoteRepeatLength, colNoteRepeatLength, dimBright)
        else:
            SetPadColor(pdNoteRepeat, colNoteRepeat, dimDim)
            SetPadColor(pdNoteRepeatLength, colNoteRepeatLength, dimDefault)

    if(showSnapNav):
        SetPadColor(pdSnapUp, colSnapUp, dimDefault)
        SetPadColor(pdSnapDown, colSnapDown, dimDefault)

def RefreshPageLights(clearOnly = False):
    global _PadMode
    #prn(lvlR, 'RefreshPageLights(',clearOnly,')', _ShowChords, _PatternPage, _ChannelPage)
    
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

    #prn(lvlA, 'RefreshNotes()', 'isChomatic', isChromatic(), 'SHowChords', _ShowChords)

    #if(_ShowChords) and (not isChromatic()):
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
        #prn(lvl0, utils.GetNoteName(_PadMap[p].NoteInfo.MIDINote), _PadMap[p].NoteInfo.IsRootNote )
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
        colors = [cWhite, cCyan, cBlue, cOrange]
        changeEvery = 16
            
        if(DEFAULT_ALT_DRUM_MODE_BANKS == False):
            changeEvery = 12

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
    #RefreshDisplay()

def RefreshKnobMode():
    LEDVal = IDKnobModeLEDVals[_KnobMode] | 16
    #prn(lvlA, 'RefreshKnobMode. knob mode is', _KnobMode, 'led bit', IDKnobModeLEDVals[_KnobMode], 'val', LEDVal)
    SendCC(IDKnobModeLEDArray, LEDVal)

def RefreshPlaylist():
    prn(lvlA, 'RefreshPlaylist()')
    #global _PlaylistMap
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

def RefreshChannelStrip(): # was (patMap: TnfxPattern, nfxMixer):
    global _ChannelMap
    global _CurrentChannel
    global _PatternMap
    global _PadMap

    #only run when in paatern mode
    if(_PadMode.Mode != MODE_PATTERNS):
        return 

    if(len(_ChannelMap) == 0):
        return

    # determine the offset. 
    channelsPerPage = len(pdPatternStripA)
    pageOffset = getChannelOffsetFromPage() 

    channelMap = _ChannelMap


    prn(lvlA, 'RefreshChannelStrip()')

    currChan = getCurrChanIdx() # channels.channelNumber()
    currMixerNum = channels.getTargetFxTrack(currChan)

    for padOffset in range(channelsPerPage):
        chanIdx = padOffset + pageOffset
        padAIdx = pdChanStripA[padOffset]
        padBIdx = pdChanStripB[padOffset]
        channel = TnfxChannel(-1,'')
        if(chanIdx < len(channelMap)):
            channel = channelMap[chanIdx]
        
        if(currChan == channel.FLIndex):
            SetPadColor(padAIdx, channel.Color, dimBright)
        else:
            SetPadColor(padAIdx, channel.Color, dimDefault)

        if(channel.FLIndex >= 0):
            if(currMixerNum == channels.getTargetFxTrack(channel.FLIndex)):
                if(currChan == channel.FLIndex):
                    SetPadColor(padBIdx, cDimWhite, dimBright)
                else:
                    SetPadColor(padBIdx, cDimWhite, dimDefault)
            else:
                SetPadColor(padBIdx, cOff, dimDefault)
        else:
            SetPadColor(padBIdx, cOff, dimDefault)


    # for padIdx in pdChanStripA:
    #     pMap = _PadMap[padIdx]
    #     if(pMap.FLIndex < 0):
    #         SetPadColor(padIdx,cOff , 0)
    #     else:
    #         SetPadColor(padIdx, pMap.Color, dimDefault)
    
    # for padIdx in pdChanStripB:
    #     pMap = _PadMap[padIdx]  
    #     if(pMap.FLIndex < 0):
    #         SetPadColor(padIdx, cOff , 0)
    #     else:
    #         if(currMixerNum == channels.getTargetFxTrack(pMap.FLIndex)):
    #             SetPadColor(padIdx, cDimWhite, dimBright)
    #         else:
    #             SetPadColor(padIdx, cDimWhite, dimDefault)

    prn(lvlA, 'RefreshChanStrip', currChan)

    SelectAndShowChannel(currChan)
    RefreshNavPads()
    
    # idx = 0
    # #for chan in range(channels.channelCount()):
    # for padNum in pdChanStripA:
    #     pMap = _PadMap[padNum]
    #     chan = pMap.FLIndex
    #     # check if there is room on the channel strip
    #     if(idx <= len(pdChanStripA)): 
    #         # below needed for HandleChannelStrip()
    #         dim = dimDefault
    #         muteColor = cOff  
    #         padColor = cOff 
    #         if(chan > -1):
    #             #if(channels.getChannelType(chan) in [CT_GenPlug, CT_Sampler, CT_Layer]):
    #             padColor = FLColorToPadColor(channels.getChannelColor(chan))
    #             muteColor = cDimWhite
    #             if(channels.isChannelSelected(chan)):
    #                 dim = dimBright
    #                 muteColor = cWhite
    #         pMap.Color = padColor
    #         mutepadIdx = pdChanStripB[idx]
    #         SetPadColor(padNum, padColor, dim)
    #         SetPadColor(mutepadIdx, muteColor, dim) 
    #         idx += 1

def getChannelOffsetFromPage():
    # returns the index of the first pattern to show on the pattern strip based on the active page
    return (_ChannelPage-1) * len(pdChanStripA)

def getPatternOffsetFromPage():
    # returns the index of the first pattern to show on the pattern strip based on the active page
    return (_PatternPage-1) * len(pdPatternStripA)

def RefreshPatternStrip():
    # should rely upon _PatternMap or _PatternMapSelected only. should not trly upon _PadMap
    # should use _PatternPage accordingly 
    global _PatternPage

    if (_PadMode.Mode != MODE_PATTERNS):
        return 

    patternMap = getPatternMap()

    # determine the offset. 
    patternsPerPage = len(pdPatternStripA)
    pageOffset = getPatternOffsetFromPage() #(_PatternPage-1) * patternsPerPage # 



    if(len(patternMap) < pageOffset): #check if we need to reset the paging when something is out of range
        _PatternPage = 0
        PatternPageNav(-99999)
        pageOffset = getPatternOffsetFromPage()  

    #print(*patternMap, sep='\n')
    #print('pageOffset', pageOffset, len(patternMap))

    for padOffset in range(0, patternsPerPage):
        patternIdx = padOffset + pageOffset
        padIdx = pdPatternStripA[padOffset]
        mutePadIdx = pdPatternStripB[padOffset]
        #print('>>>', padOffset, patternIdx, 'pageOffset', pageOffset)
        if(padOffset < patternsPerPage) and (patternIdx < len(patternMap)): # room to use an available pattern?
            pattern = patternMap[patternIdx] 
            if(patterns.patternNumber() == pattern.FLIndex): #current pattern
                SetPadColor(padIdx, pattern.Color, dimBright)
                SetPadColor(mutePadIdx, cWhite, dimBright)
            else:
                if(pattern.Selected):
                    SetPadColor(padIdx, pattern.Color, dimDefault)
                    SetPadColor(mutePadIdx, cDimWhite, dimBright)
                else:
                    SetPadColor(padIdx, pattern.Color, dimDim)
                    SetPadColor(mutePadIdx, cOff, dimDim)
        else: #not used
            SetPadColor(padIdx, cOff, dimDim)
            SetPadColor(mutePadIdx, cOff, dimDim)            

        
        


def RefreshPatternStrip3():
    # this function should rely upon _PadMap only. _PadMap should be updated - via UpdatePatternMap() - prior to call when needed
    # 
    #prn(lvlR, 'RefreshPatternStrip', _PatternPage)
    if (_PadMode.Mode != MODE_PATTERNS):
        return 

    patternsPerPage = len(pdPatternStripA)
    for i in range(0, patternsPerPage):
        padIdx = pdPatternStripA[i]
        mutePadIdx = pdPatternStripB[i]
        padMap = _PadMap[padIdx] 
        patMap = _PatternMap[padMap.FLIndex-1] # 0-based
        #prn(lvlA, padIdx, padMap.FLIndex, patMap.FLIndex)
        if(patterns.patternNumber() == padMap.FLIndex): #current pattern
            SetPadColor(padMap.PadIndex, padMap.Color, dimBright)
            SetPadColor(mutePadIdx, cWhite, dimBright)
        else:
            if(patMap.Selected):
                SetPadColor(padMap.PadIndex, padMap.Color, dimDefault)
                SetPadColor(mutePadIdx, cDimWhite, dimBright)
            else:
                if(not _isAltMode):
                    SetPadColor(padMap.PadIndex, padMap.Color, dimDim)
                    SetPadColor(mutePadIdx, cOff, dimDim)

def RefreshPatternStripOrig():
    
    #prn(lvlR, 'RefreshPatternStrip', _PatternPage)
    if (_PadMode.Mode != MODE_PATTERNS):
        return 

    patternsPerPage = len(pdPatternStripA) 
    for i in range(0, patternsPerPage):
        padIdx = pdPatternStripA[i]
        mutePadIdx = pdPatternStripB[i]
        pMap = _PadMap[padIdx] # 0-based
        #prn(lvlA, padIdx, pMap.FLIndex, pMap.Color)
        if(patterns.patternNumber() == pMap.FLIndex): #current pattern
            SetPadColor(pMap.PadIndex, pMap.Color, dimBright)
            SetPadColor(mutePadIdx, cWhite, dimBright)
        else:
            if(patterns.isPatternSelected(patterns.patternNumber())):
                SetPadColor(pMap.PadIndex, pMap.Color, dimBright)
            else:
                SetPadColor(pMap.PadIndex, pMap.Color, dimDim)
            if(pMap.Color != cOff):
                SetPadColor(mutePadIdx, cDimWhite, dimDim)
            else:
                SetPadColor(mutePadIdx, cOff, dimDim)


def RefreshPatternPads2_OBS():
    prn(lvlR, 'RefreshPatternPads()', _PatternPage)
    patternsPerPage = len(pdPatternStripA) 
    for i in range(0, patternsPerPage):
        padIdx = pdPatternStripA[i]
        mutePadIdx = pdPatternStripB[i]
        pMap = _PadMap[padIdx] # 0 based
        flPattNum = pMap.FLIndex
        color = pMap.Color
        padIdx = pMap.PadIndex
        #pMap = _PadMap[padIdx] # 0-based
        if(patterns.patternNumber() == flPattNum): #current pattern
            SetPadColor(padIdx, color, dimBright)
            SetPadColor(mutePadIdx, cWhite, dimBright)
        else:
            SetPadColor(padIdx, color, dimDefault)
            if(color != cOff):
                SetPadColor(mutePadIdx, cDimWhite, dimDim)
            else:
                SetPadColor(mutePadIdx, cOff, dimDim)
def RefreshDisplay():
    global _menuItemSelected

    prn(lvlA, "RefreshDisplay()")
    _menuItemSelected = _selectedItem # reset this for the next menu
    chanIdx = getCurrChanIdx() # 
    chanName = channels.getChannelName(chanIdx)
    mixerName = mixer.getTrackName(mixer.trackNumber())
    patName = patterns.getPatternName(patterns.patternNumber())
    cMap = _ChannelMap[chanIdx]
    
#    chanTypes = ['SMP', 'HYB', 'GEN', 'LYR', 'CLP', 'AUT']
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

    #prn(lvlU, 'UpdatePatternModePadMap()')
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
        pageLen = len(pdPatternStripA)
        patPageOffs = (_PatternPage-1) * pageLen # first page will = 0
        chanPageOffset = (_ChannelPage-1) * pageLen # first page will = 0

        for padOffset in range(0, pageLen): 

            #defaults
            padColor = cOff 
            flIdx = -1

            pattAPadIdx = pdPatternStripA[padOffset]    # the pad to light up
            pattBPadIdx = pdPatternStripB[padOffset]    # the secondary pad
            pattIdx = padOffset + patPageOffs           # the pattern in _PatternMap to represent

            chanPadIdxA = pdChanStripA[padOffset]       # the pad to light up
            chanPadIdxB = pdChanStripB[padOffset]       # the secondary pad
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
    prn(lvlU, 'UpdatePatternMap', pattNum, len(_PatternMap))

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
            prn(lvlA, '_PatternMap added ', patMap.FLIndex, patMap.Color)
    else: #update the current pattern's channels map only
        RefreshChannelStrip()     

def UpdatePlaylistMap(selectedOnly = False):
    prn(lvlA, 'UpdatePlaylistMap')
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
    prn(lvlU, 'UpdatePatternMap', pattNum)
    global _PatternMap
    global _PatternCount
    global _CurrentPattern
    global __PatternSelectedMap

    _PatternCount = patterns.patternCount()
    _PatternMap.clear()
    _PatternSelectedMap.clear()

    for pat in range(1,_PatternCount+1): # FL patterns start at 1
        patMap = TnfxPattern(pat, patterns.getPatternName(pat))
        patMap.Color = FLColorToPadColor(patterns.getPatternColor(pat))  # patterns.getPatternColor(pat)
        patMap.Selected = patterns.isPatternSelected(pat)
        _PatternMap.append(patMap)
        if(patMap.Selected):
            _PatternSelectedMap.append(patMap)
        #prn(lvlA, '... added ', patMap)

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
    prn(lvlA, 'Selection:', selStart, selEnd, selBarStart , selBarEnd)
    if(selStart > -1):
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
        padBarLen = 0 #getBeatLenInMS(1)
    elif(_ProgressPadLenIdx == 1): # 1 bars
        padBarLen = 1
    elif(_ProgressPadLenIdx == 2): # 2 bars
        padBarLen = 2
    elif(_ProgressPadLenIdx == 3): # 4 bars
        padBarLen = 4

    if(_ProgressPadLenIdx == 0):
        padAbsLen = songLenAbsTicks/progressLen + 1
    else:
        padAbsLen = getAbsTicksFromBar(2) * padBarLen # get the start of bar 2 aka the length of 1 bar in ticks times the number of bars

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
                    #prn(lvlA, 'added marker to pad', padIdx, '...',  progressPosAbsTicks, ' >= ', marker.SongPosAbsTicks, ' < ', nextAbsTick)

        else:
            progPad.BarNumber = -1
            progPad.Color = cOff # getShade(cRed, shDark)
            progPad.SongPosAbsTicks = -1
        
        prn(lvlA, 'added progress pad', progPad)
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
    prn(lvlU, 'UpdateChannelMap()')
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
        _ChannelMap.append(chanMap)
        print('...added', chanMap)
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
    prn(lvl0, 'copy pattern')
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
    prn(lvl0, '---- copy pattern')

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
#    global _keynote 
    global _ScaleNotes 
    global _ScaleDisplayText
    global _ScaleIdx
    global _NoteMap
    global __NoteMapDict


    _faveNoteIdx = rootNote
    _ScaleIdx = newModeIdx
    harmonicScale = ScalesList[_ScaleIdx][0]
    noteHighlight = ScalesList[_ScaleIdx][1]
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
                    # MapNoteToPad(padIdx, noteVal)
                    #_PadMap[padIdx].NoteInfo.MIDINote = noteVal
                    _PadMap[padIdx].NoteInfo.ChordNum = colOffset + 1
                else:
                    #MapNoteToPad(padIdx, noteVal)
                    #_PadMap[padIdx].NoteInfo.MIDINote = noteVal
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
    # elif(_PadMode.Mode == MODE_DRUM):
    #     pads = DrumPads()
    #     for noteOffs, padIdx in enumerate(pads):
    #         noteVal = lineGrid[0][0] + noteOffs
    #         MapNoteToPad(padIdx, noteVal)
    #         #_PadMap[padIdx].NoteInfo.MIDInote = noteVal
    #         _PadMap[padIdx].NoteInfo.IsRootNote = (noteOffs % notesInScale) == 0
            
    #         #if(noteVal not in _NoteMapDict.keys()):     # if key dopesnt exist,
    #         #    _NoteMapDict[noteVal] = [padIdx]        # create it
    #         #elif(padIdx not in _NoteMapDict[noteVal]):  # else
    #         #    _NoteMapDict[noteVal].append(padIdx)    # add it to the existing list
            
                
            
    #prn(lvl0, 'Scale:',_ScaleDisplayText)
    #RefreshDisplay() #    DisplayTimedText('Scale: ' + _ScaleDisplayText)

def PlayMIDINote(chan, note, velocity):   
    prn(lvlA, 'Chan', chan, 'Note Value:', utils.GetNoteName(note), note, velocity)
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
    
    RefreshShiftAlt()
    print('ok', _PadMode.Name)

    if(_PadMode.Mode == MODE_PATTERNS):
        UpdatePatternModeData()
    elif(_PadMode.Mode == MODE_PERFORM):
        ClearAllPads()
        if(_isAltMode):
            print('ok2')
            UpdateMarkerMap()
            UpdateProgressMap()
            RefreshProgress()

    RefreshPadModeButtons() # lights the button

    print('ok3')
    RefreshAll()
    print('ok4')

def getCurrChanIdx():
    return channels.selectedChannel()
    globalIdx = channels.channelNumber()
    res = -1
    for cMap in _ChannelMap:
        if(cMap.GlobalIndex == globalIdx):
            res = cMap.FLIndex
    return res 

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
    pageSize = len(pdPatternStripA)
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
    pageSize = len(pdPatternStripA)
    newPage = _ChannelPage + moveby 
    #if(newPage > 4):
    #    newPage = 4
    if(newPage < 1):
        newPage = 1
    pageOffs = (newPage-1) * pageSize # first page will = 0
    prn(lvlA, 'ChannelPageNav', _ChannelCount, pageOffs)
    if(0 <= pageOffs <= _ChannelCount ): # allow next page when there are patterns to show
        _ChannelPage = newPage
    ui.crDisplayRect(0, pageOffs, 0, pageSize, 5000, CR_ScrollToView + CR_HighlightChannelName)
    RefreshPageLights()
def NavNotesList(val):
    global _NoteIdx
    _NoteIdx += val
    if( _NoteIdx > (len(NotesList)-1)  ):
        _NoteIdx = 0
    elif( _NoteIdx < 0 ):
        _NoteIdx = len(NotesList)-1
    prn(lvl0, 'Root Note: ',  NotesList[_NoteIdx])

def NavOctavesList(val):
    global _OctaveIdx
    _OctaveIdx += val
    if( _OctaveIdx > (len(OctavesList)-1) ):
        _OctaveIdx = 0
    elif( _OctaveIdx < 0 ):
        _OctaveIdx = len(OctavesList)-1
    prn(lvl0, 'Octave: ' , OctavesList[_OctaveIdx])    

def NavSetList(val):
    global _PadMode 

    prn(lvlA, 'NavSetList', _PadMode.AllowedNavSetIdx, val, 'Allowed', *_PadMode.AllowedNavSets )
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

    if(navSet == nsDefault):
        SendCC(IDLeft, SingleColorFull)
    elif(navSet == nsScale):
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
    prn(lvl0, 'Scale: ' , _ScaleIdx,  ScalesList[_ScaleIdx][0])        

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
    #prn(lvlA, 'ShowChanEditor', showVal, showEditor, showCSForm)
    
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

    prn(lvlA, 'ShowChanEditor', bSave, showVal, _ChannelMap[chanNum].ShowChannelEditor, _ChannelMap[chanNum].ShowCSForm )

    if(bUpdateDisplay):
        DisplayTextBottom('ChanEdit: ' + _showText[showVal])

    if(showVal == 0): # make CR active when closed
        ShowChannelRack(_ShowChanRack)


def ShowPlaylist(showVal, bUpdateDisplay = False):
    global _ShowPlaylist
    
    prn(lvlA, 'ShowPlaylist', showVal, bUpdateDisplay)

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
        #if(_ShowChanRack == 1) and (isFocused): #if not focused, activate it
        if(isShowing) and (isFocused) and (showVal == 0): # only hide when has focus to allow us to activate windows  for copy/cut/paste
            showVal = 0
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

def ShowMenuItems():
    pageLen = 3 # display is 3 lines tall
    selPage = int(_menuItemSelected/pageLen) # 
    selItemOffs = _menuItemSelected % pageLen    #
    pageFirstItemOffs = (selPage * pageLen)       # 
    maxItem = len(_menuItems)
    displayText = ['','','']
    
    for i in range(0,3):
        item = i + pageFirstItemOffs
        if(item < maxItem):
            preText = '.. '
            if(_menuItemSelected == item):
                preText = '-->'
            displayText[i] = preText + _menuItems[item]
            prn(lvlA, displayText[i])

    DisplayTextAll(displayText[0], displayText[1], displayText[2])
    
def ShowMenuItems():
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
            prn(lvlA, displayText[i])

    DisplayTextAll(displayText[0], displayText[1], displayText[2])
#endregion

# work area/utility        
def prn(lvl, *objects):
    if(not _debugprint):
        return
    prefix = prnLevels[lvl][1]
    if(_DebugPrn and (lvl >= _DebugMin)) or (lvl == lvlA):
        print(prefix, *objects)    

def SetPlaylistTop():
    ui.scrollWindow(widPlaylist, 1)
    ui.scrollWindow(widPlaylist, 1, 1)

def ShowNote(note, isOn = True):
    #print('ShowNote', note, isOn)
    if(note == -1):
        return

    dim = dimDefault
    if(isOn):
        dim = dimFull
    
    noteDict = _NoteMapDict
    #if(_PadMode.Mode == MODE_DRUM) and (isFPCActive()):
    #    noteDict = _NoteMapDict
    
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
    prn(lvlA, 'Snap', newmode)
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
    return getDrumPads(_isAltMode, isNoNav())

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
    modePattern.AllowedNavSets = [nsDefault, nsUDLR]

    modePatternAlt.NavSet = TnfxNavigationSet(nsDefault)
    modePatternAlt.AllowedNavSets = [nsDefault, nsUDLR]

    modeNote.NavSet = TnfxNavigationSet(nsScale)
    modeNote.AllowedNavSets = [nsScale, nsDefault, nsUDLR]

    modeNoteAlt.NavSet = TnfxNavigationSet(nsScale)
    modeNoteAlt.AllowedNavSets = [nsScale, nsDefault, nsUDLR]

    modeDrum.NavSet = TnfxNavigationSet(nsDefault)
    modeDrum.AllowedNavSets = [nsDefault, nsUDLR]

    modeDrumAlt.NavSet = TnfxNavigationSet(nsDefault2)
    modeDrumAlt.AllowedNavSets = [nsDefault2, nsDefault, nsUDLR, nsNone]

    modePerform.NavSet = TnfxNavigationSet(nsNone)
    modePerform.AllowedNavSets = [nsNone, nsDefault, nsUDLR]

    modePerformAlt.NavSet = TnfxNavigationSet(nsNone)
    modePerformAlt.AllowedNavSets = [nsNone, nsDefault, nsUDLR]

    _PadMode = modePattern

