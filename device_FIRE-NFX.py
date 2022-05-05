# name=FIRE-NFX
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

from fireNFX_DEFAULTS import *

from harmonicScales import *

from fireNFX_Classes import *
from fireNFX_Defs import * 
from fireNFX_PadDefs import *
from fireNFX_Utils import * 
from fireNFX_Display import *
from fireNFX_PluginDefs import *

#region globals
_ShiftHeld = False
_AltHeld = False
_PatternCount = 0
_CurrentPattern = -1
_PatternPage = 1
_ChannelCount = 0
_CurrentChannel = -1
_PreviousChannel = -1
_ChannelPage = 1
_KnobMode = 0
_Beat = 1
_PadMap = list()
_PatternMap = list()
_ChannelMap = list()
_PlaylistMap = list()
_ShowMixer = 1
_ShowChanRack = 1
_ShowPlaylist = 1
_ShowBrowser = 1
_showText = ['OFF', 'ON']
#display menu
_ShowMenu = 0
_menuItems = ['Option 1','Option 2','Option 3','Option 4','Option 5']
_selectedItem = 0
_menuItemSelected = _selectedItem
#notes/scales
_ScaleIdx = DEFAULT_SCALE
_ScaleDisplayText = ""
_ScaleNotes = list()
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
macCloseAll = TnfxMacro("Close All", cRed)
macTogChanRack = TnfxMacro("Chan Rack", cOrange)
macTogPlaylist = TnfxMacro("Playlist", cYellow)
macTogMixer = TnfxMacro("Mixer", cWhite)
macPluginInfo = TnfxMacro("Show Plugin", cBlueDark)
macCopy = TnfxMacro("Copy", cBlueMed)
macCut = TnfxMacro("Cut", cBlueLight)
macPaste = TnfxMacro("Paste", cCyan)
_MacroList = [macCloseAll, macTogChanRack, macTogPlaylist, macTogMixer, macPluginInfo, macCopy, macCut, macPaste]
#colMacros = [ cGreen, cCyan, cBlue, cPurple, cRed, cOrange, cYellow, cWhite ]

# list of notes that are mapped to pads
_NoteMap = list()


#endregion 

#region FL MIDI API Events
def OnInit():
    prn(lvlE, 'OnInit()')

    
    # clear the Pads
    for pad in range(0,64):
        SetPadColor(pad, 0x000000, 0)

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
    UpdatePatternModeData()
    RefreshAll()
def OnDoFullRefresh():
    prn(lvlA, 'OnDoFullRefresh')    

_lastNote =-1

def OnIdle():
    global _lastNote
    if(_ShiftHeld):
        RefreshShiftedStates() 
    
    note = channels.getCurrentStepParam(getCurrChanIdx(), mixer.getSongStepPos(), pPitch)
    if (PAD_MODE in [MODE_DRUM, MODE_NOTE]):
        if(_lastNote != note):
            prn(lvlA, 'last note', _lastNote) 
            ShowNote(_lastNote, False)
            if(note > -1) and (note in _NoteMap):
                prn(lvlA, 'note', note, 'last note', _lastNote) 
                ShowNote(note, True)
            _lastNote = note
  
def OnMidiMsg(event):
    prn(lvlN, "OnMidiMsg()", event.data1, event.data2)
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
    HW_Dirty_Patterns = 1024
    
    if(HW_Dirty_LEDs & flags):
        RefreshTransport()

    if(HW_Dirty_Patterns & flags):
        prn(lvl0, 'pattern event')
        HandlePatternChanges()
    if(HW_Dirty_ChannelRackGroup & flags):
        prn(lvl0, 'channel group changed', _ChannelCount, channels.channelCount())
        HandleChannelGroupChanges()    
    if(HW_ChannelEvent & flags):
        prn(lvl0, 'channel event', _ChannelCount, channels.channelCount())
        UpdateChannelMap()  
        if (PAD_MODE == MODE_DRUM):
            RefreshDrumPads()
        elif(PAD_MODE == MODE_PATTERNS):
            RefreshChannelStrip()
    if(HW_Dirty_Colors & flags):
        prn(lvl0, 'color change event')
        if (PAD_MODE == MODE_DRUM):
            RefreshDrumPads()
        elif(PAD_MODE == MODE_PATTERNS):
            RefreshChannelStrip()
    if(HW_Dirty_Tracks & flags):
        prn(lvlA, 'track change event')
        if(PAD_MODE == MODE_PERFORM):
            UpdatePlaylistMap()
            RefreshPlaylist()
    if(HW_Dirty_Mixer_Sel & flags):
        prn(lvl0, 'mixer sel event')
def OnProjectLoad(status):
    global PAD_MODE 

    prn(lvlE, 'OnProjectLoad', status)
    # status = 0 = starting load?
    if(status == 0):
        DisplayTextAll('Project Loading', '-', 'Please Wait...')
    if(status >= 100): #finished loading
        PAD_MODE = MODE_PATTERNS
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

    # handle a pad
    if( IDPadFirst <=  ctrlID <= IDPadLast):
        padNum = ctrlID - IDPadFirst
        pMap = _PadMap[padNum]
        prn(lvlA, 'Pad Detected', padNum, _PadMap[padNum].NoteInfo.MIDINote, _NoteMap[padNum])

        if(event.data2 > 0): # pressed
            pMap.Pressed = 1
            SetPadColor(padNum, cRed, dimBright, False) # False will not save the color to the _ColorMap
        else: #released
            pMap.Pressed = 0
            SetPadColor(padNum, -1, dimDefault) # -1 will rever to the _ColorMap color

        # always handle macros
        if(padNum in pdMacros) and (pMap.Pressed): 
            event.handled = HandleMacros(pdMacros.index(padNum))
            RefreshMacros()
            return 

        # always handle macros
        if(padNum in pdNav) and (pMap.Pressed): 
            event.handled = HandleNav(padNum)
            return 

        if(padNum in pdWorkArea):
            if(PAD_MODE == MODE_DRUM): # handles on and off for PADS
                event.handled = HandlePads(event, padNum, pMap)
                return 
            elif(PAD_MODE == MODE_NOTE): # handles on and off for NOTES
                event.handled = HandlePads(event, padNum, pMap)
                return 
            elif(PAD_MODE == MODE_PERFORM): # handles on and off for PERFORMANCE
                if(pMap.Pressed == 1):
                    event.handled = HandlePlaylist(event, padNum)
                else:
                    event.handled = True 
                return 
            elif(PAD_MODE == MODE_PATTERNS): # if STEP/PATTERN mode, treat as controls and not notes...
                if(pMap.Pressed == 1): # On Pressed
                    event.handled = HandlePads(event, padNum, pMap)
                    return 
                else:
                    event.handled = True #prevents a note off message
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
    prn(lvlE, 'OnNoteOn()', utils.GetNoteName(event.data1),event.data1,event.data2)
def OnNoteOff(event):
    prn(lvlE, 'OnNoteOff()', utils.GetNoteName(event.data1),event.data1,event.data2)
#endregion 

#region Handlers
def HandleChannelStrip(padNum, isChannelStripB):
    global _PatternMap
    global _ChannelMap
    global _CurrentChannel 
    global _PreviousChannel
    global _ChannelCount

    prevChanIdx = getCurrChanIdx() # channels.channelNumber()
    pMap = _PadMap[padNum]
    newChanIdx = pMap.FLIndex

    prn(lvlA, 'HandleChannelStrip', prevChanIdx, newChanIdx)
    if (newChanIdx > -1): #is it a valid chan number?
        if(newChanIdx == prevChanIdx): # if it's already on the channel, toggle the windows
            prn(lvlA, 'sameChan', newChanIdx, _ChannelMap[prevChanIdx].ShowChannelEditor)
            if (isChannelStripB):
                ShowPianoRoll(-1, True) #not patMap.ShowPianoRoll)
            else:
                ShowChannelEditor(-1, True) #not patMap.ShowChannelEditor)
        else: #'new' channel, close the previous windows first
            prn(lvlA, 'newChan', newChanIdx, 'prevChan', prevChanIdx)
            #close and reset the previous
            #if(ui.getVisible(widPianoRoll)):
            #    ui.hideWindow(widPianoRoll)
            ShowPianoRoll(0, True)
            ShowChannelSettings(0, True)
            ShowChannelEditor(0, True)
            #_ChannelMap[prevChanIdx].ShowChannelEditor = 0
            #_ChannelMap[prevChanIdx].ShowCSForm = 0
            #_ChannelMap[prevChanIdx].ShowPianoRoll = 0

            channels.deselectAll
            
            channels.selectOneChannel(newChanIdx)
            mixerTrk = channels.getTargetFxTrack(newChanIdx)
            ui.crDisplayRect(0, newChanIdx, 0, 1, 5000, CR_ScrollToView + CR_HighlightChannels)
            ui.miDisplayRect(mixerTrk, mixerTrk, 5000, CR_ScrollToView)
            #if (_PreviousChannel == newChanIdx): # what to activate on second press 
            #    if (isChannelStripB):
            ##        ShowPianoRoll(-1, True)
            #    elif (_PreviousChannel == newChanIdx):
            #        ShowChannelEditor(-1, True)
            #_PreviousChannel = newChanIdx

    _CurrentChannel = getCurrChanIdx() # channels.channelNumber()
    _ChannelCount = channels.channelCount()
    RefreshDisplay()
    return True

def HandlePatternStrip(padNum):
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
            ShowPianoRoll(0, False, False)
            ShowChannelEditor(0, False, False)
            patterns.deselectAll()
            patterns.jumpToPattern(newPatNum)
            #ui.crDisplayRect(0, selChanIdx, 0, 1, 10000, CR_ScrollToView + CR_HighlightChannels)

    #RefreshPatterns(_CurrentPattern)
    _CurrentChannel = getCurrChanIdx() # channels.channelNumber()
    _ChannelCount = channels.channelCount()
    RefreshDisplay()
    return True
def HandlePlaylist(event, padNum):
    prn(lvlA, 'HandlePlaylist()')

    flIdx = _PadMap[padNum]
    
    if(padNum in pdPlaylistStripA) or (padNum in pdPlaylistStripB):       
        flIdx = _PadMap[padNum].FLIndex
        playlist.selectTrack(flIdx)
    
    if(padNum in pdPlaylistMutesA) or (padNum in pdPlaylistMutesB):
        prn(lvlA, 'playlist.muteTrack(', _PadMap[padNum].FLIndex, ')', padNum)
        flIdx = _PadMap[padNum].FLIndex
        playlist.muteTrack(flIdx)
    
    UpdatePlaylistMap()
    RefreshPlaylist()
    return True
def HandlePads(event, padNum, pMap):  
    prn(lvlH, 'HandlePads', _CurrentPattern)

    # 'perfomance'  pads will need a pressed AND release...

    if(PAD_MODE == MODE_DRUM):
        if (padNum in pdFPCA) or (padNum in pdFPCB):
            return HandleDrums(event, padNum)

    elif(PAD_MODE == MODE_NOTE):
        if(padNum in pdWorkArea):
            return HandleNotes(event, padNum)
        

    # some pads we only need on pressed event
    if(event.data2 > 0): # On Pressed

        #macros are handled in OnMidiIn

        #mode specific
        if(PAD_MODE == MODE_NOTE):
            if(padNum in pdNav):
                HandleNav(padNum)
        if(PAD_MODE == MODE_DRUM):
            if(padNum in pdFPCChannels):
                HandleDrums(event, padNum)
        elif(PAD_MODE == MODE_PATTERNS):
            if(padNum in pdPatternStripA):
                if(_AltHeld):
                    CopyPattern(pMap.FLIndex)
                else:
                    event.handled = HandlePatternStripA(padNum)
            elif(padNum in pdPatternStripB):
                event.handled = HandlePatternStripA(padNum)
            elif(padNum in pdChanStripA):
                event.handled = HandleChannelStrip(padNum, False)   
            elif(padNum in pdChanStripB):
                event.handled = HandleChannelStrip(padNum, True)


    return True
def HandleNav(padIdx):
    global _NoteRepeat
    #prn(lvlH, 'HandleNav', padIdx)
    if(PAD_MODE == MODE_NOTE):
        if(padIdx in pdShowChanPads):
            if(padIdx == pdShowChanEditor):
                ShowChannelEditor(-1, True)
            elif(padIdx == pdShowChanPianoRoll):
                ShowPianoRoll(-1, True)
        elif(padIdx == pdOctaveNext):
            NavOctavesList(-1)
        elif(padIdx == pdOctavePrev):
            NavOctavesList(1)
        elif(padIdx == pdScaleNext):
            NavScalesList(1)
        elif(padIdx == pdScalePrev):
            NavScalesList(-1)
#        elif(_ScaleIdx > 0): #not chromatic so it usable.
        elif(padIdx == pdRootNoteNext):
            NavNotesList(-1)
        elif(padIdx == pdRootNotePrev):
            NavNotesList(1)            
        RefreshNotes()

    if(PAD_MODE == MODE_DRUM):
        if(padIdx == pdNoteRepeatLength):
            NavNoteRepeatLength(1)
            prn(lvlA, 'rpt len', BeatLengthNames[_NoteRepeatLengthIdx])
        if(padIdx == pdNoteRepeat):
            _NoteRepeat = not _NoteRepeat
            prn(lvlA, 'Note Repeat: ', _NoteRepeat)
            if(_isRepeating):
                device.stopRepeatMidiEvent()
        if(padIdx in pdShowChanPads):
            if(padIdx == pdShowChanEditor):
                ShowChannelEditor(-1, True)
            elif(padIdx == pdShowChanPianoRoll):
                ShowPianoRoll(-1, True)

    if(PAD_MODE == MODE_PATTERNS):
        if(padIdx in pdUDLR):
            HandleUDLR(padIdx)
        if(padIdx in pdPresetNav):
            ShowChannelEditor(1, True)
            if(padIdx == pdPresetPrev):
                ui.previous()
            elif(padIdx == pdPresetNext):
                ui.next()

        RefreshDisplay()
    
    return True 
def HandleMacros(macIdx):
    chanNum = channels.selectedChannel(0, 0, 0)
    macro = _MacroList[macIdx]

    if(macIdx == 4):
        ShowPluginInfo(chanNum)
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
        #ShowBrowser(1)
        ShowChannelRack(0)
        ShowPlaylist(0)
        ShowMixer(0)
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

    prn(lvlA, 'HandleNotes', padNum, event.data1, event.data2)


    chanNum = _PadMap[padNum].ItemIndex
    event.data1 = _PadMap[padNum].NoteInfo.MIDINote

    if(0 < event.data2 < _VelocityMin):
        event.data2 = _VelocityMin
    elif(event.data2 > _VelocityMin):
        event.data2 = _VelocityMax

    
    #if(_NoteRepeat) and (not _isRepeating):
    #    device.repeatMidiEvent(event, 300, 300)
    ##    _isRepeating = True
    #elif(_NoteRepeat) and (event.data2 == 0):
    #    device.stopRepeatMidiEvent()
    #    _isRepeating = False
    

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
    chanNum = _PadMap[padNum].ItemIndex
    prn(lvlA, 'handle drums', 'in', event.data1, 'out', _PadMap[padNum].NoteInfo.MIDINote, 'Note Rpt', _NoteRepeat, _isRepeating)
    if(padNum in pdFPCA) or (padNum in pdFPCB):

        # do the note repeat BEFORE changing the note.
        if(_NoteRepeat):
            if(event.data2 == 0):
                device.stopRepeatMidiEvent()
                _isRepeating = False
            elif(not _isRepeating):
                ms = GetBeatLenInMS(BeatLengthDivs[6])
                device.repeatMidiEvent(event, 0, ms)
                _isRepeating = True

        #set the note to the one used by FPC Pad
        event.data1 = _PadMap[padNum].NoteInfo.MIDINote

        # even out some velocities
        if(90 > event.data2 > 1 ):
            event.data2 = 90
        elif(110 > event.data2 > 64):
            event.data2 = 110
        elif(event.data2 > 110):
            event.data2 = 120


        return False # false to continue processing

    elif(chanNum > -1):
        channels.selectOneChannel(chanNum)
        ShowChannelEditor(1, False)
        RefreshDisplay()
        return True 
    else:
        return True # mark as handled to prevent processing
def HandlePatternStripA(padNum):
    #pattIdx = pdPatternStripA.index(padNum)
    #patt = _PatternMap[pattIdx]
    patt = _PadMap[padNum].FLIndex
    if(patterns.patternNumber() != patt): # patt.FLIndex):
        patterns.jumpToPattern(patt)
    return True 
def HandlePatternStripB(padNum):
    pattIdx = pdPatternStripB.index(padNum)
    patt = _PatternMap[pattIdx]
    if(patterns.patternNumber() != patt.FLIndex):
        patterns.jumpToPattern(patt.FLIndex)
    return True 
def HandleChannelGroupChanges():
    UpdatePatternModeData()
    RefreshAll()    
def HandlePatternChanges():
    global _PatternCount
    global _CurrentPattern
    global _CurrentPage 

    prn(lvlH, 'HandlePatternChanges()')

    if (_PatternCount > 0) and  (PAD_MODE == MODE_PATTERNS): # do pattern mode
        currPattern = patterns.patternNumber()
        if(_PatternCount != patterns.patternCount()):
            prn(lvl0, 'pattern added/removed')
            _PatternCount = patterns.patternCount()
            currPattern = patterns.patternNumber()
            _CurrentPattern = patterns.patternNumber()
            UpdatePatternModeData() # was UpdatePatternMap(_CurrentPattern)             # was UpdatePatternPadMap()
        else:
            prn(lvl0, 'selected pattern changed', currPattern)
            if _CurrentPattern != currPattern:
                currPattern = patterns.patternNumber()
                _CurrentPattern = patterns.patternNumber()
                UpdatePatternModeData(_CurrentPattern) # was UpdatePatternMap(_CurrentPattern) 
        RefreshPatternStrip()
            

    if(patterns.patternCount() == 0) and (_CurrentPattern == 1): # empty project, set to 1
        _PatternCount = 1

    RefreshDisplay()
def HandlePattUpDn(ctrlID):
    prn(lvlA, 'HandlePattUpDn()', ctrlID, _ShiftHeld, _AltHeld, _CurrentChannel)

    moveby = 1
    if(ctrlID == IDPatternUp):
        moveby = -1

    if(_ShiftHeld):
        newChanIdx = getCurrChanIdx() + moveby
        if(0 <= newChanIdx < _ChannelCount):
            channels.selectOneChannel(newChanIdx)
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
        newPattern = _CurrentPattern + moveby
        if( 0 <= newPattern <= _PatternCount):   #if it's a valid spot then move it
            patterns.jumpToPattern(newPattern)
    
    RefreshDisplay()
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
    return True
def HandleKnobMode():
    #prn(lvlH, 'HandleKnobMode()')
    NextKnobMode()
    RefreshDisplay()
    return True
def HandleKnob(event, ctrlID):
    event.inEv = event.data2
    if event.inEv >= 0x40:
        event.outEv = event.inEv - 0x80
    else:
        event.outEv = event.inEv
    event.isIncrement = 1
    value = event.outEv

    prn(lvlH, 'HandleKnob()', event.data1, event.data2, ctrlID, getCurrChanIdx(), _KnobMode)

    if _KnobMode == UM_CHANNEL :
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
                if(PAD_MODE == MODE_DRUM) and (heldPadIdx > -1) and (isFPCActive()):
                    return HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Volume.Offset + heldPadIdx, event.outEv, ppFPC_Volume.Caption, ppFPC_Volume.Bipolar)
                else:
                    ui.crDisplayRect(0, chanNum, 0, 1, 10000, CR_ScrollToView + CR_HighlightChannelPanVol)
                    return HandleKnobReal(recEventID + REC_Chan_Vol,  value, 'Ch Vol: ' + chanName, False)
                    

            elif ctrlID == IDKnob2:
                if(PAD_MODE == MODE_DRUM) and (heldPadIdx > -1) and (isFPCActive()):
                    return HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Pan.Offset + heldPadIdx, event.outEv, ppFPC_Pan.Caption, ppFPC_Pan.Bipolar)
                else:
                    ui.crDisplayRect(0, chanNum, 0, 1, 10000, CR_ScrollToView + CR_HighlightChannelPanVol)
                    return HandleKnobReal(recEventID + REC_Chan_Pan, value, 'Ch Pan: ' + chanName, True)

            elif ctrlID == IDKnob3:
                if(PAD_MODE == MODE_DRUM) and (heldPadIdx > -1) and (isFPCActive()):
                    return HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Tune.Offset + heldPadIdx, event.outEv, ppFPC_Tune.Caption, ppFPC_Tune.Bipolar)
                else:
                    return HandleKnobReal(recEventID + REC_Chan_FCut, value, 'Ch Flt: ' + chanName, False)

            elif ctrlID == IDKnob4:
                return HandleKnobReal(recEventID + REC_Chan_FRes, value, 'Ch Res: ' + chanName, False)

            else:
                return True 
    elif _KnobMode == UM_MIXER :
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
        return True    
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
    #differnt modes use these differently   
    if(PAD_MODE == MODE_PATTERNS):
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
        

    elif(PAD_MODE == MODE_NOTE) and (ctrlID == IDPage0): 
        if(_ScaleIdx > 0):
            _ShowChords = not _ShowChords
        else:    
            _ShowChords = False
            # make the mute led turn red
        RefreshNotes()

    RefreshPageLights()
    RefreshDisplay()
    return True
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
    prn(lvlH, 'HandlePadMode')
    ctrlID = event.data1 

    if(ctrlID == IDStepSeq):
        newPadMode = MODE_PATTERNS
    elif(ctrlID == IDNote):
        newPadMode = MODE_NOTE
    elif(ctrlID == IDDrum):
        newPadMode = MODE_DRUM
    elif(ctrlID == IDPerform):
        newPadMode = MODE_PERFORM

    SetPadMode(newPadMode)

    return True
def HandleTransport(event):
    prn(lvlH, 'HandleTransport', event.data1)
    if(event.data1 == IDPatternSong):
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
        chordName += chordTypes[ ((_ScaleIdx + chordNum) % 7)-1 ]

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
        PlayMIDINote(chan, note, noteVelocity)
        PlayMIDINote(chan, note3, noteVelocity)
        PlayMIDINote(chan, note5, noteVelocity)
        PlayMIDINote(chan, note3inv, noteVelocity)
        PlayMIDINote(chan, note5inv, noteVelocity)
        PlayMIDINote(chan, note7, noteVelocity)
def HandleUDLR(padIndex):
    prn(lvlA, 'HandleUDLR', padIndex)
    if(padIndex == pdUp):
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
    if(PAD_MODE == MODE_DRUM):
        RefreshDrumPads()
    elif(PAD_MODE == MODE_PATTERNS):
        UpdatePatternModeData(patterns.patternNumber())
        RefreshPatternStrip() 
        RefreshChannelStrip()
    elif(PAD_MODE == MODE_NOTE):
        RefreshNotes()
    elif(PAD_MODE == MODE_PERFORM):
        prn(lvlA, "TODO: RefreshModes() for PERFORM")
        UpdatePlaylistMap()
        RefreshPlaylist()
def RefreshPadModeButtons():
    SendCC(IDStepSeq, DualColorOff)
    SendCC(IDNote, DualColorOff)
    SendCC(IDDrum, DualColorOff)
    SendCC(IDPerform, DualColorOff)
    if(PAD_MODE == MODE_PATTERNS):
        SendCC(IDStepSeq, DualColorFull2)
    elif(PAD_MODE == MODE_NOTE):
        SendCC(IDNote, DualColorFull2)
    elif(PAD_MODE == MODE_DRUM):
        SendCC(IDDrum, DualColorFull2)
    elif(PAD_MODE == MODE_PERFORM):
        SendCC(IDPerform, DualColorFull2)
def RefreshShiftAlt():
    if(_AltHeld):
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
def RefreshPads():
    for pad in range(0,64):
        SetPadColor(pad, _PadMap[pad].Color, dimDefault) 
def RefreshMacros():
    for pad in pdMacros:
        idx = pdMacros.index(pad)
        #color =  colMacros[idx]
        SetPadColor(pad, _MacroList[idx].Color, dimDefault)
def RefreshNavPads():
    # mode specific
    showPresetNav = False
    showNoteRepeat = False
    showUDLRNav = False
    showChanWinNav = False

    for pad in pdNav :
        SetPadColor(pad, cOff, dimDefault)

    if(PAD_MODE == MODE_NOTE):
        for pad in pdNoteFuncs:
            idx = pdNoteFuncs.index(pad)
            color = colNoteFuncs[idx]
            SetPadColor(pad, color, dimDefault)
            showChanWinNav = True
    elif (PAD_MODE == MODE_DRUM):
        showPresetNav = True
        showNoteRepeat = True
        showChanWinNav = True
    elif (PAD_MODE == MODE_PATTERNS):    
        showPresetNav = True
        RefreshUDLR()

    if(showPresetNav):
        for pad in pdPresetNav :
            idx = pdPresetNav.index(pad)
            color = colPresetNav[idx]
            SetPadColor(pad, color, dimDefault)

    if(showChanWinNav):
        for pad in pdShowChanPads:
            idx = pdShowChanPads.index(pad)
            color = colShowChanPads[idx]
            SetPadColor(pad, color, dimDefault)

    if(showNoteRepeat):
        SetPadColor(pdNoteRepeat, colNoteRepeat, dimDefault)

def RefreshPageLights(clearOnly = False):
    prn(lvlR, 'RefreshPageLights(',clearOnly,')', _ShowChords, _PatternPage, _ChannelPage)
    
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

    if(PAD_MODE == MODE_NOTE):
        if(_ShowChords):
            SendCC(IDPage0, SingleColorHalfBright)
    elif(PAD_MODE == MODE_PATTERNS):
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
                color = cDimWhite-1
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
                SetPadColor(p, cBlueMed, dimDefault)
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
        SetPadColor(pd7th, cYellow, 4) # extra dim
    if(_ChordInvert == 1):
        SetPadColor(pdInv1, cWhite, dimDefault)
    elif(_ChordInvert == 2):
        SetPadColor(pdInv2, cWhite, dimDefault)
    else:
        SetPadColor(pdNormal, cWhite, dimDefault)

def RefreshDrumPads():
    global _PadMap

    chanIdx = getCurrChanIdx() # channels.channelNumber()
    cMap = _ChannelMap[chanIdx]
    isFPC = False
    if(cMap.ChannelType == CT_GenPlug):
        isFPC = (plugins.getPluginName(chanIdx, -1, 0) == "FPC")

    if( isFPC ):  # Show Custom FPC Colors
        PAD_Count =	0	#Retrieve number of pad parameters supported by plugin
        PAD_Semitone =	1	#Retrieve semitone for pad specified by padIndex
        PAD_Color =	2	#Retrieve color for pad specified by padIndex    

#        chanIdx = getCurrChanIdx() # channels.channelNumber()    

        # FPC A Pads
        fpcpadIdx = 0
        semitone = 0
        color = cOff
        dim =  dimDefault
        for p in pdFPCA:
            color = plugins.getPadInfo(chanIdx, -1, PAD_Color, fpcpadIdx) # plugins.getColor(chanIdx, -1, GC_Semitone, fpcpadIdx)
            semitone = plugins.getPadInfo(chanIdx, -1, PAD_Semitone, fpcpadIdx)
            #prn(lvl0, fpcpadIdx, 'semitone', semitone , 'color', color)
            _PadMap[p].FPCColor = FLColorToPadColor(color)
            _PadMap[p].NoteInfo.MIDINote = semitone 
            _NoteMap[p] = semitone 
            SetPadColor(p, _PadMap[p].FPCColor, dim)
            fpcpadIdx += 1 # NOTE! will be 16 when we exit the for loop, the proper first value for the B Pads loop...
        # FPC B Pads
        for p in pdFPCB:
            color = plugins.getPadInfo(chanIdx, -1, PAD_Color, fpcpadIdx) 
            semitone = plugins.getPadInfo(chanIdx, -1, PAD_Semitone, fpcpadIdx) 
            _PadMap[p].FPCColor = FLColorToPadColor(color)
            _PadMap[p].NoteInfo.MIDINote = semitone 
            _NoteMap[p] = semitone 
            SetPadColor(p, _PadMap[p].FPCColor, dim)
            fpcpadIdx += 1 # continue 
    else:
        for p in pdFPCA:
            SetPadColor(p, cOff, dimDefault)
            _PadMap[p].Color = cOff
        for p in pdFPCB:
            SetPadColor(p, cOff, dimDefault)
            _PadMap[p].Color = cOff


    # refresh the 'channel area' where fpc instances are shown
    idx = 0
    #clear the existing channel area
    for p in pdFPCChannels:
        SetPadColor(p, cOff, dimDefault)
        _PadMap[p].Color = cOff

    #find the fpc channels
    for chan in range(channels.channelCount()):
        # check if there is room
        if(idx < len(pdFPCChannels)): 
            if(_ChannelMap[chan].ChannelType == CT_GenPlug):
                if(plugins.getPluginName(chan, -1, 0) == "FPC"):
                    if(not isFPC): #if an FPC is not selected, choose the first one
                        channels.selectOneChannel(chan)
                        isFPC = True
                    padNum = pdFPCChannels[idx]
                    padColor = FLColorToPadColor(channels.getChannelColor(chan))
                    if(getCurrChanIdx()  == chan):
                        SetPadColor(padNum, padColor, dimBright)
                    else:
                        SetPadColor(padNum, padColor, dimDefault)
                    _PadMap[padNum].Color = padColor
                    _PadMap[padNum].ItemIndex = chan 
                    idx += 1
    RefreshMacros() 
    RefreshNavPads()
    RefreshDisplay()
def RefreshKnobMode():
    LEDVal = IDKnobModeLEDVals[_KnobMode] | 16
    #prn(lvlR, 'RefreshKnobMode. knob mode is', _CurrentKnobMode, 'led bit', IDKnobModeLEDVals[_CurrentKnobMode], 'val', LEDVal)
    SendCC(IDKnobModeLEDArray, LEDVal)
def RefreshPlaylist():
    prn(lvlA, 'RefreshPlaylist()')
    global _PlaylistMap
    global _PadMap
    plLen = len(pdPlaylistStripA)
    plPage = 0
    plStartIdx = (plLen * plPage)

    if(len(_PlaylistMap) == 0):
        return 

    for padOffs in range(plLen): #gives me 0..12
        padTrackA = pdPlaylistStripA[padOffs]
        padTrackB = pdPlaylistStripB[padOffs]
        padMuteA  = pdPlaylistMutesA[padOffs]
        padMuteB  = pdPlaylistMutesB[padOffs]
        plMapA = _PlaylistMap[plStartIdx + padOffs]
        plMapB = _PlaylistMap[plStartIdx + padOffs + plLen]
        flIdxA = plMapA.FLIndex 
        flIdxB = plMapB.FLIndex
        dimA = dimDefault
        dimB = dimDefault
        muteColorA = cDimWhite
        muteColorB = cDimWhite

        if(playlist.isTrackSelected(flIdxA)):
            dimA = dimBright
        if(playlist.isTrackSelected(flIdxB)):
            dimB = dimBright
        SetPadColor(padTrackA, plMapA.Color, dimA) 
        SetPadColor(padTrackB, plMapB.Color, dimB) 
        _PadMap[padTrackA].Color = plMapA.Color
        _PadMap[padTrackB].Color = plMapB.Color
        _PadMap[padTrackA].FLIndex = flIdxA
        _PadMap[padTrackB].FLIndex = flIdxB

        if(playlist.isTrackMuted(flIdxA)):
            muteColorA = cOff 
        if(playlist.isTrackMuted(flIdxB)):
            muteColorB = cOff 
        SetPadColor(padMuteA, muteColorA, dimDefault) 
        SetPadColor(padMuteB, muteColorB, dimDefault) 
        _PadMap[padMuteA].Color = muteColorA
        _PadMap[padMuteB].Color = muteColorB
        _PadMap[padMuteA].FLIndex = flIdxA
        _PadMap[padMuteB].FLIndex = flIdxB
def RefreshChannelStrip(): # was (patMap: TnfxPattern, nfxMixer):
    global _ChannelMap
    global _CurrentChannel
    global _PatternMap
    global _PadMap

    _CurrentChannel = getCurrChanIdx() # channels.channelNumber()
    prn(lvlR, 'RefreshChannelStrip()')
    if(len(_ChannelMap) == 0):
        return

    for padIdx in pdChanStripA:
        pMap = _PadMap[padIdx]
        if(pMap.FLIndex < 0):
            SetPadColor(padIdx,cOff , 0)
        else:
            SetPadColor(padIdx, pMap.Color, dimDefault)
    
    for padIdx in pdChanStripB:
        pMap = _PadMap[padIdx]  
        if(pMap.FLIndex < 0):
            SetPadColor(padIdx, cOff , 0)
        else:
            SetPadColor(padIdx, cDimWhite, dimDefault)
    
    currChan = getCurrChanIdx() # channels.channelNumber()
    prn(lvlA, 'RfereshChanStrip', currChan)
    
  #  if(channels.getChannelType in [CT_Sampler, CT_Hybrid, CT_GenPlug, CT_AudioClip]):
    mixerIdx = channels.getTargetFxTrack(currChan)
    mixer.deselectAll()
    mixer.selectTrack(mixerIdx)

    idx = 0
    #for chan in range(channels.channelCount()):
    for padNum in pdChanStripA:
        pMap = _PadMap[padNum]
        chan = pMap.FLIndex
        # check if there is room on the channel strip
        if(idx <= len(pdChanStripA)): 
            # below needed for HandleChannelStrip()
            dim = dimDefault
            muteColor = cOff  
            padColor = cOff 
            if(chan > -1):
                #if(channels.getChannelType(chan) in [CT_GenPlug, CT_Sampler, CT_Layer]):
                padColor = FLColorToPadColor(channels.getChannelColor(chan))
                muteColor = cDimWhite
                if(channels.isChannelSelected(chan)):
                    dim = dimBright
                    muteColor = cWhite
            pMap.Color = padColor
            mutepadIdx = pdChanStripB[idx]
            SetPadColor(padNum, padColor, dim)
            SetPadColor(mutepadIdx, muteColor, dim) 
            idx += 1
def RefreshPatternStrip():
    prn(lvlR, 'RefreshPatternStrip', _PatternPage)
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
            SetPadColor(pMap.PadIndex, pMap.Color, dimDefault)
            if(pMap.Color != cOff):
                SetPadColor(mutePadIdx, cDimWhite, 4)
            else:
                SetPadColor(mutePadIdx, cOff, 4)
def RefreshPatternPads2():
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
                SetPadColor(mutePadIdx, cDimWhite, 4)
            else:
                SetPadColor(mutePadIdx, cOff, 4)
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
    pm = PadModeShortNames[PAD_MODE] + " - " + um
    toptext = pm 
    sPatNum = str(patterns.patternNumber())
    midtext = sPatNum + '. ' + patName 
    bottext = chanTypes[cMap.ChannelType] + ': ' + cMap.Name

    if(PAD_MODE == MODE_PATTERNS):
        toptext = pm + '      ' 
        if(KnobModeShortNames[_KnobMode] in ['Mi']):
            toptext = pm + '     ' # on less space
        if(KnobModeShortNames[_KnobMode] in ['U1', 'U2']):
            toptext = pm + '    ' # on less space
        toptext = toptext + str(_PatternPage) + ' - ' + str(_ChannelPage)

    if(PAD_MODE == MODE_NOTE):
        midtext = '' + _ScaleDisplayText
        if(_ShowChords):
            toptext = pm + " - CHO"

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
        if(pad == pdEsc):
            SetPadColor(pad, cRed, dimDefault)
        elif(pad == pdEnter):
            SetPadColor(pad, cGreen, dimDefault)
        else:
            SetPadColor(pad, cDimWhite, dimDefault)

#endregion 

#region Updates / Resets
def UpdatePatternModePadMap():
    prn(lvlU, 'UpdatePatternModePadMap()')
    global _PadMap
    global _PatternMap
    global _PatternCount

    #if(len(_PatternMap) != _PatternCount):
    #    UpdatePatternMap(-1)

    if(PAD_MODE == MODE_PATTERNS): # Pattern mode, set the pattern buttons

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
            pattIdx = padOffset + patPageOffs           # the pattern to represent

            chanPadIdxA = pdChanStripA[padOffset]       # the pad to light up
            chanPadIdxB = pdChanStripB[padOffset]       # the secondary pad
            chanIdx = padOffset + chanPageOffset        # the channel to represent at this pad

            if(pattIdx < _PatternCount):
                flIdx = pattIdx + 1 # fl patterns are 1 based
                padColor = FLColorToPadColor(patterns.getPatternColor(flIdx)) # FL is 1-based
                _PatternMap[pattIdx].Color = padColor
                _PatternMap[pattIdx].FLIndex = flIdx

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
def UpdatePatternMapOld(pattNum):
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
            prn(lvl0, '_PatternMap added ', patMap.FLIndex, patMap.Color)
    else: #update the current pattern's channels map only
        RefreshChannelStrip()     
def UpdatePlaylistMap():
    prn(lvlA, 'UpdatePlaylistMap')
    global _PlaylistMap
    global _PadMap

    _PlaylistCount = playlist.trackCount()
    _PlaylistMap.clear()
    for plt in range(_PlaylistCount):
        flIdx = plt + 1
        color = FLColorToPadColor( playlist.getTrackColor(flIdx) )
        name = playlist.getTrackName(flIdx)
        plMap = TnfxPlaylistTrack(flIdx, name, color)
        plMap.Muted = playlist.isTrackMuted(flIdx)
        plMap.Selected = playlist.isTrackSelected(flIdx)
        _PlaylistMap.append(plMap)
def UpdatePatternMap(pattNum):
    prn(lvlU, 'UpdatePatternMap', pattNum)
    global _PatternMap
    global _PatternCount
    global _CurrentPattern
    _PatternCount = patterns.patternCount()
    _PatternMap.clear()
    for pat in range(_PatternCount):
        patMap = TnfxPattern(pat, patterns.getPatternName(pat))
        patMap.Color = patterns.getPatternColor(pat)
        _PatternMap.append(patMap)
    _CurrentPattern = patterns.patternNumber()
def UpdateChannelMap():
    prn(lvlU, 'UpdateChannelMap()')
    global _ChannelMap
    global _ChannelCount
    global _CurrentChannel
    _ChannelCount = channels.channelCount()
    _ChannelMap.clear()
    for chan in range(_ChannelCount):
        chanMap = TnfxChannel(chan, channels.getChannelName(chan))
        chanMap.Color = channels.getChannelColor(chan)
        chanMap.ChannelType = channels.getChannelType(chan)
        chanMap.GlobalIndex = channels.getChannelIndex(chan)
        _ChannelMap.append(chanMap)
    _CurrentChannel = getCurrChanIdx() # channels.channelNumber()
def UpdatePatternModeData(pattNum = -1):
    global _CurrentChannel
    global _ChannelCount
    ResetPadMaps(False)
    UpdatePatternMap(pattNum)
    UpdateChannelMap()
    UpdatePatternModePadMap()
def ResetBeatIndicators():
    for i in range(0, len(BeatIndicators) ):
        SendCC(BeatIndicators[i], SingleColorOff)
#endregion 

#region Helper function 
def isFPCActive():
    chanIdx = getCurrChanIdx() # channels.channelNumber()
    if(_ChannelMap[chanIdx].ChannelType == CT_GenPlug):
        pluginName = plugins.getPluginName(chanIdx, -1, 0)      
        return (pluginName == 'FPC') 
    else:
        return False
def CopyPattern(FLPattern):
    prn(lvl0, 'copy pattern')
    ui.showWindow(widChannelRack)
    chanIdx = getCurrChanIdx() # channels.channelNumber()
    channels.selectOneChannel(chanIdx)
    ui.copy 
    name = patterns.getPatternName(FLPattern)
    color = patterns.getPatternColor(FLPattern)
    patterns.findFirstNextEmptyPat(FFNEP_DontPromptName)
    newpat = patterns.patternNumber()
    patterns.setPatternName(newpat, name)
    patterns.setPatternColor(newpat, color)
    channels.selectOneChannel(chanIdx)
    ui.paste 
    prn(lvl0, '---- copy pattern')
def ResetPadMaps(bUpdatePads = False):
    global _PadMap
    global _NoteMap
    _PadMap.clear()
    _NoteMap.clear()
    for padIdx in range(0, 64):
        _PadMap.append(TnfxPadMap(padIdx, -1, 0x000000, ""))
        _NoteMap.append(-1)
    if(bUpdatePads):
        RefreshPads()
def isChromatic():
    return (_ScaleIdx == 0) #chromatic
def GetScaleGrid(newModeIdx=0, rootNote=0, startOctave=2):
    global _PadMap 
#    global _keynote 
    global _ScaleNotes 
    global _ScaleDisplayText
    global _ScaleIdx
    global _NoteMap


    _faveNoteIdx = rootNote
    _ScaleIdx = newModeIdx
    harmonicScale = ScalesList[_ScaleIdx][0]
    noteHighlight = ScalesList[_ScaleIdx][1]
    _ScaleNotes.clear()

    # get lowest octave line
    gridlen = 12
    lineGrid = [[0] for y in range(gridlen)]
    notesInScale = GetScaleNoteCount(harmonicScale)
    
    
    #build the lowest <gridlen> notes octave and transpose up from there
    BuildNoteGrid(lineGrid, gridlen, 1, rootNote, startOctave, harmonicScale)

    # first I make a 5 octave list of notes to refernce later
    for octave in range(0, 5):
        for note in range(0, notesInScale):
            _ScaleNotes.append(lineGrid[note][0] + (12*octave) )

    # next I fill in the notes from the bottom to top
    for colOffset in range(0, gridlen):
        for row in range(0, 4): # 3
            if(notesInScale < 6): 
                noteVal = lineGrid[colOffset][0] + (24*row) # for pentatonic scales 
            else:
                noteVal = lineGrid[colOffset][0] + (12*row)
            revRow = 3-row  # reverse to go from bottom to top
            rowOffset = 16 * revRow  # 0,16,32,48
            padIdx = rowOffset + colOffset

            if(row == 3): # and (GetScaleNoteCount(scale) == 7): #chord row
                _PadMap[padIdx].NoteInfo.MIDINote = noteVal
                _PadMap[padIdx].NoteInfo.ChordNum = colOffset + 1
            else:
                _PadMap[padIdx].NoteInfo.MIDINote = noteVal
                _PadMap[padIdx].NoteInfo.ChordNum = -1
            
            _NoteMap[padIdx] = noteVal

            _PadMap[padIdx].NoteInfo.IsRootNote = (colOffset % notesInScale) == 0 # (colOffset == 0) or (colOffset == notesInScale)

    _ScaleDisplayText = NotesList[_faveNoteIdx] + str(startOctave) + " " + HarmonicScaleNamesT[harmonicScale]
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
def SetPadMode(newPadMode):
    global PAD_MODE
    oldPadMode = PAD_MODE

    if(oldPadMode != newPadMode):
        PAD_MODE = newPadMode
        if(PAD_MODE == MODE_PATTERNS):
            UpdatePatternModeData()
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
#endregion

#region Nav helpers
def NextKnobMode():
    global _KnobMode
    prn(lvl0, 'next knob mode. was', _KnobMode)

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
def NavScalesList(val):
    global _ScaleIdx
    _ScaleIdx += val
    if( _ScaleIdx > (len(ScalesList)-1) ):
        _ScaleIdx = 0
    elif( _ScaleIdx < 0 ):
        _ScaleIdx = len(ScalesList)-1
    prn(lvl0, 'Scale: ' , _ScaleIdx,  ScalesList[_ScaleIdx][0])        
def NavSnap(val):
    global _SnapIdx
    _SnapIdx += val
    if(_SnapIdx < 0):
        _SnapIdx = len(SnapModesList) - 1
    elif(_SnapIdx > (len(SnapModesList) - 1) ): 
        _SnapIdx = 0
    newMode = SnapModesList[_SnapIdx]
    setSnapMode( newMode )  
    DisplayTextAll('Snap:', SnapModes[newMode], '')   
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
def ShowPianoRoll(showVal, bSave, bUpdateDisplay = False):
    global _PatternMap 
    currVal = 0

    if(len(_PatternMap) > 0):
        selPat = GetPatternMapActive() # _PatternMap[_CurrentPattern-1]  # 0 based
        currVal = selPat.ShowPianoRoll

    ui.showWindow(widChannelRack)
    chanNum = channels.selectedChannel(0, 0, 0)
#    ui.openEventEditor(channels.getRecEventId(
#        chanNum) + REC_Chan_PianoRoll, EE_PR)

    if(showVal == -1):  # toggle
        if(currVal == 0):
            showVal = 1
        else:
            showVal = 0

    if(showVal == 1):
        ui.showWindow(widPianoRoll)
        if(bSave):
            if(len(_PatternMap) > 0):
                selPat.ShowPianoRoll = 1
    else:
        ui.hideWindow(widPianoRoll)
        if(bSave):
            if(len(_PatternMap) > 0):
                selPat.ShowPianoRoll = 0

    if(showVal == 0): # make CR active
        ui.showWindow(widChannelRack)

    if(bUpdateDisplay):
        DisplayTimedText('Piano Roll: ' + _showText[showVal])
def ShowChannelSettings(showVal, bSave, bUpdateDisplay = False):
    global _PatternMap
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
        ui.showWindow(widChannelRack)

    if(bUpdateDisplay):
        DisplayTimedText('Chan Sett: ' + _showText[showVal])

    if(bSave):
        if(len(_PatternMap) > 0):
            selPat.ShowChannelSettings = showVal
def ShowChannelEditor(showVal, bSave, bUpdateDisplay = False):
    global _ChannelMap

    if(len(_ChannelMap) <= 0):
        return

    ui.showWindow(widChannelRack)
    chanNum =  channels.selectedChannel(0, 0, 0)
    chanType = channels.getChannelType(chanNum)
    showEditor = _ChannelMap[chanNum].ShowChannelEditor
    showCSForm = _ChannelMap[chanNum].ShowCSForm
    prn(lvlA, 'ShowChanEditor', showVal, showEditor, showCSForm)
    

    if( chanType in [CT_Hybrid, CT_GenPlug] ):
        currVal = showEditor
    elif(chanType in [CT_Layer, CT_AudioClip, CT_Sampler, CT_AutoClip]):
        currVal = showCSForm

    if(showVal == -1):  # toggle
        if(currVal <= 0): #might be -1 initially
            showVal = 1
        else:
            showVal = 0

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
        ui.showWindow(widChannelRack)

def ShowPlaylist(showVal, bUpdateDisplay = False):
    global _ShowPlaylist

    isShowing = ui.getVisible(widPlaylist)
    isFocused = ui.getFocused(widPlaylist)

    if(showVal == -1): # toggle
        #if(_ShowMixer == 1):
        if(isShowing == 1) and (isFocused == 1):
            showVal = 0
        else:
            showVal = 1
    
    if(showVal == 1):        
        ui.showWindow(widPlaylist)
    else:
        ui.hideWindow(widPlaylist)
    
    _ShowPlaylist = showVal    

    if(bUpdateDisplay): 
        DisplayTimedText('Playlist: ' + _showText[showVal])

def ShowMixer(showVal, bUpdateDisplay = False):
    global _ShowMixer

    isShowing = ui.getVisible(widMixer)
    isFocused = ui.getFocused(widMixer)

    if(showVal == -1): # toggle
        #if(_ShowMixer == 1):
        if(isShowing == 1) and (isFocused == 1):
            showVal = 0
        else:
            showVal = 1

    if(showVal == 1):
        ui.showWindow(widMixer)
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
        if(isShowing) and (isFocused): # only hide when has focus to allow us to activate windows  for copy/cut/paste
            showVal = 0
        else:
            showVal = 1

    if(showVal == 1):
        ui.showWindow(widChannelRack)
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
    prefix = prnLevels[lvl][1]
    if(_DebugPrn and (lvl >= _DebugMin)) or (lvl == lvlA):
        print(prefix, *objects)    

def SetPlaylistTop():
    ui.scrollWindow(widPlaylist, 1)
    ui.scrollWindow(widPlaylist, 1, 1)

def ShowNote(note, isOn = True):
    print('ShowNote', note, isOn)
    if(note == -1):
        return
    if(note in _NoteMap):
        padIdx = _NoteMap.index(note)
        dim = dimDefault
        if(isOn):
            dim = dimFull
        SetPadColor(padIdx,  getPadColor(padIdx), dim)
 