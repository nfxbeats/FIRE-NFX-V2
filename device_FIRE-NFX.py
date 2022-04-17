# name=FIRE-NFX

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

from fireNFX_DEFAULTS import *

from harmonicScales import *

from fireNFX_Classes import *
from fireNFX_Defs import * 
from fireNFX_PadDefs import *
from fireNFX_Utils import * 
from fireNFX_Display import *
from fireNFX_PluginDefs import *

# globals
_ShiftHeld = False
_AltHeld = False
_PatternCount = 0
_CurrentPattern = -1
_KnobMode = 0
_CurrentPage = 0 
_Beat = 1
_PadMap = list()
_PatternMap = list()
_PatternPage = 0
_ChannelPage = 0
_ShowMixer = 1
_ShowChanRack = 1
_ShowPlaylist = 1
_ShowBrowser = 1
_showText = ['OFF', 'ON']
#notes/scales
_ScaleIdx = DEFAULT_SCALE
_ScaleDisplayText = ""
_ScaleNotes = list()
_NoteIdx = DEFAULT_NOTE_NAMES.index(DEFAULT_ROOT_NOTE)
_OctaveIdx = OctavesList.index(DEFAULT_OCTAVE)
_SnapIdx = 0
_PreviousChannel = -1
_ShowChords = False
_ChordNum = -1
_ChordInvert = False
_Chord7th = False
_VelocityMin = 100
_VelocityMax = 126
_DebugPrn = True
_DebugMin = lvl0

# FL Events
def OnInit():
    prn(lvlE, 'OnInit()')
    
    #  turn off top buttons: the Pat Up/Dn, browser and Grid Nav buttons
    SendCC(IDPatternUp, SingleColorOff)
    SendCC(IDPatternDown, SingleColorOff)
    SendCC(IDBankL, SingleColorOff)
    SendCC(IDBankR, SingleColorOff)
    SendCC(IDBrowser, SingleColorOff)    

    # clear the Pads
    for pad in range(0,64):
        SetPadColor(pad, 0x000000, 0)

    # Refresh the control button states        
    # Initialize Some lights
    RefreshPageLights()           # PAD Mutes akak Page
    ResetBeatIndicators()   # 
    RefreshKnobMode()       # Top Knobs operting mode
    RefreshShiftAlt()
    UpdatePatternPadMap()
    RefreshMacros()
    UpdatePatternMap(patterns.patternNumber())
    RefreshPadModeButtons()
    RefreshTransport()


    InitDisplay()
    DisplayText(Font6x8, JustifyCenter, 0, "nfxFire", True)
    DisplayText(Font6x16, JustifyCenter, 1, "-", True)
    DisplayText(Font10x16, JustifyCenter, 2, "Version 1.0", True)
    #fun "animation"
    line = '----------------------'
    for i in range(16):
        text = line[0:i]
        DisplayText(Font6x16, JustifyCenter, 1, text, True)
        time.sleep(.05)
        
def OnIdle():
    if(_ShiftHeld):
        RefreshShifted() 

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
    prn(lvlE, 'OnRefresh()', flags)
    HW_Dirty_Patterns = 1024
    if(HW_Dirty_Patterns & flags):
        prn(lvl0, 'pattern event')
        HandlePatternChanges()
    if(HW_ChannelEvent & flags):
        prn(lvl0, 'channel event')
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
        prn(lvl0, 'track change event')
    if(HW_Dirty_Mixer_Sel & flags):
        prn(lvl0, 'mixer sel event')

def OnProjectLoad(status):
    prn(lvlE, 'OnProjectLoad', status)
    # status = 0 = starting load?
    # status = 100 = finished laoding

def OnMidiIn(event):
    global _ShiftHeld
    global _AltHeld
    global _PadMap
    

    prn(lvlE, "OnMidiIn", event.data1, event.data2)
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
        prn(lvl0, 'Pad Detected', padNum)

        if(event.data2 > 0): # pressed
            pMap.Pressed = 1
            SetPadColor(padNum, cRed, dimBright, False) # False will not save the color to the _ColorMap
        else:
            pMap.Pressed = 0
            SetPadColor(padNum, -1, dimBright) # -1 will rever to the _ColorMap color

        # always handle macros
        if(padNum in pdMacros) and (pMap.Pressed): 
            event.handled = HandleMacros(pdMacros.index(padNum))
            RefreshMacros()
            return 

        # always handle macros
        if(padNum in pdNav) and (pMap.Pressed): 
            event.handled = HandleNav(padNum)
            return 

        if(PAD_MODE == MODE_DRUM): # handles on and off for PADS
            #if ( (padNum in pdFPCA) or (padNum in pdFPCB) or (padNum in pdFPCChannels) ):
            if(padNum in pdWorkArea):
                event.handled = HandlePads(event, padNum, pMap)
                return 
        elif(PAD_MODE == MODE_NOTE): # handles on and off for NOTES
            if(padNum in pdWorkArea):
                event.handled = HandlePads(event, padNum, pMap)
                return 
        elif(PAD_MODE == MODE_PERFORM): # handles on and off for PERFORMANCE
            if(padNum in pdWorkArea):
                event.handled = True # todo: 
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
        elif( ctrlID in PadModeCtrls):
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
    else: # Released
        event.handled = True 

def OnNoteOn(event):
    prn(lvlE, 'OnNoteOn()', utils.GetNoteName(event.data1),event.data1,event.data2)
           
def OnNoteOff(event):
    prn('OnNoteOff()', utils.GetNoteName(event.data1),event.data1,event.data2)

def GetPatternMapActive():
    return _PatternMap[_CurrentPattern-1]

# handlers
def HandleChannelStrip(padNum, isChannelStripMute):
    global _PatternMap
    global _PreviousChannel

    if(isChannelStripMute):
        idx = pdChanStripMutes.index(padNum)
    else:
        idx = pdChanStrip.index(padNum)

    prevChanIdx = channels.channelNumber()
    patMap = GetPatternMapActive() # _PatternMap[_CurrentPattern-1] # 0 - based
    nfxChannels = patMap.Channels 
    selChanIdx = nfxChannels[idx].FLIndex
    #prn(lvlH, 'handle chanstrip', padNum, 'patt', _CurrentPattern, 'prevChanIdx', prevChanIdx, 'new chan', selChanIdx)

    if(prevChanIdx == selChanIdx): # if it's already on the channel, toggle the windows
        if (isChannelStripMute):
            ShowPianoRoll(-1, True) #not patMap.ShowPianoRoll)
        else:
            ShowChannelEditor(-1, True) #not patMap.ShowChannelEditor)
    else: #'new' channel, close the previous windows first
        ShowPianoRoll(0, False, False)
        ShowChannelEditor(0, False, False)
        #channels.selectChannel(selChanIdx, 1)
        channels.deselectAll
        channels.selectOneChannel(selChanIdx)
        #ui.crDisplayRect(0, selChanIdx, 0, 1, 10000, CR_ScrollToView + CR_HighlightChannels)
        
        if (_PreviousChannel == selChanIdx): # what to activate on second press 
            if (isChannelStripMute):
                ShowPianoRoll(patMap.ShowPianoRoll, True)
            elif (_PreviousChannel == selChanIdx):
                ShowChannelEditor(patMap.ShowChannelEditor, True)
            
        _PreviousChannel = selChanIdx

    #RefreshPatterns(_CurrentPattern)
    RefreshDisplay()
    return True




def HandlePads(event, padNum, pMap):  
    #prn(lvlH, 'HandlePads', _CurrentPattern)

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
            if(padNum in pdMutes):
                event.handled = HandleMuteButtons(padNum)
            elif(padNum in pdChanStrip):
                event.handled = HandleChannelStrip(padNum, False)   
            elif(padNum in pdChanStripMutes):
                event.handled = HandleChannelStrip(padNum, True)   
            elif(pMap.FLPattern > 0): # I dont think this is correct....
                if(_CurrentPattern != pMap.FLPattern):
                    patterns.jumpToPattern(pMap.FLPattern)
                    ui.hideWindow(widPianoRoll)
                    ui.hideWindow(5) #widPlugin
                elif(_AltHeld): # already on this pattern, check if alt is held    
                    CopyPattern(pMap.FLPattern)

    return True

def HandleNav(padIdx):
    #prn(lvlH, 'HandleNav', padIdx)

    if(PAD_MODE == MODE_NOTE):
        if(padIdx == pdOctaveNext):
            NavOctavesList(-1)
        elif(padIdx == pdOctavePrev):
            NavOctavesList(1)
        elif(padIdx == pdScaleNext):
            NavScalesList(1)
        elif(padIdx == pdScalePrev):
            NavScalesList(-1)
        elif(_ScaleIdx > 0): #not chromatic so it usable.
            if(padIdx == pdRootNoteNext):
                NavNotesList(-1)
            elif(padIdx == pdRootNotePrev):
                NavNotesList(1)            
        RefreshNotes()


    if(PAD_MODE == MODE_PATTERNS):
        if(padIdx in pdPresetNav):
            ShowChannelEditor(1, True)
            if(padIdx == 0):
                ui.previous()
            else:
                ui.next()
        RefreshDisplay()
    
    return True 

    
def HandleMacros(macIdx):
    chanNum = channels.selectedChannel(0, 0, 1)

    if(macIdx == 0):
        ShowBrowser(-1)
    elif(macIdx == 1):
        ShowChannelRack(-1)        
    elif(macIdx == 2):
        ShowPlaylist(-1)
    elif(macIdx == 3):
        ShowMixer(-1)        
    elif(macIdx == 4):
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

    prn(lvlH, 'HandleNotes', padNum, event.data1, event.data2)


    chanNum = _PadMap[padNum].ItemIndex
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
            chan = channels.channelNumber()
            HandleChord(chan, chordNum, noteOn, noteVelocity, _Chord7th, _ChordInvert)
        elif(padNum in pdChordFuncs) and (event.data2 > 0):
            if (padNum == pd7th): 
                _Chord7th = not _Chord7th
                DisplayTimedText("7th: " + _showText[_Chord7th])
            elif(padNum == pdInv):
                _ChordInvert =  not _ChordInvert
                DisplayTimedText("Inverted: " + _showText[_ChordInvert])
            return True 

    return False # to continue processing regular notes

def HandleDrums(event, padNum):
    chanNum = _PadMap[padNum].ItemIndex
    prn(lvlH, 'handle drums', 'in', event.data1, 'out', _PadMap[padNum].NoteInfo.MIDINote)
    if(padNum in pdFPCA) or (padNum in pdFPCB):
        event.data1 = _PadMap[padNum].NoteInfo.MIDINote
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


def HandleMuteButtons(padNum):
    btnIdx = pdMutes.index(padNum)
    patt = _PatternMap[btnIdx+1]
    if(patterns.patternNumber() == patt.FLIndex):
        prn(lvl0, 'show piano roll')
    else:
        # close any piano roll
        patterns.jumpToPattern(patt.FLIndex)
    return True 

def HandlePatternChanges():
    global _PatternCount
    global _CurrentPattern
    global _CurrentPage 

    prn(lvlH, 'HandlePatternChanges()')

    if (_PatternCount > 0) and  (PAD_MODE == MODE_PATTERNS): # do pattern mode
        currPattern = patterns.patternNumber()
        if(_PatternCount != patterns.patternCount()):
            #prn(lvl0, 'pattern added/removed')
            _PatternCount = patterns.patternCount()
            currPattern = patterns.patternNumber()
            UpdatePatternPadMap()
        else:
            #prn(lvl0, 'selected pattern changed', currPattern)
            if _CurrentPattern != currPattern:
                currPattern = patterns.patternNumber()
                RefreshPatternPads()
        _CurrentPattern = patterns.patternNumber()
        
        UpdatePatternMap(_CurrentPattern) 

    if(patterns.patternCount() == 0) and (currPattern == 1): # empty project, set to 1
        _PatternCount = 1

    RefreshDisplay()

def RefreshDisplay():
    chanName = channels.getChannelName(channels.channelNumber())
    mixerName = mixer.getTrackName(mixer.trackNumber())
    patName = patterns.getPatternName(patterns.patternNumber())
    
    toptext = ''
    bottext = ''
    pm = "[" + PadModeNames[PAD_MODE] + "] "
    
    if(PAD_MODE == MODE_NOTE) and (_ShowChords):
        pm = "[" + PadModeNames[PAD_MODE]+ "(CHORD)] "

    um = KnobModeShortNames[_KnobMode]
    toptext = pm 
    midtext = 'Patt: ' + patName 
    bottext = 'Chan: ' + chanName 

    if(PAD_MODE == MODE_NOTE):
        midtext = 'Scale: ' + _ScaleDisplayText

    DisplayTextTop(toptext)
    DisplayTextMiddle(midtext)
    DisplayTextBottom(bottext)

def HandlePattUpDn(ctrlID):
    prn(lvlH, 'HandlePattUpDn()', ctrlID)
    if(_AltHeld):
        if(ctrlID == IDPatternUp):
            DisplayTimedText('vZoom Out')
            ui.verZoom(2)
        else:
            DisplayTimedText('vZoom In')
            ui.verZoom(-2)
    else:
        moveby = 1
        if(ctrlID == IDPatternUp):
            moveby = - 1
        newPattern = _CurrentPattern + moveby
        if( 0 <= newPattern <= _PatternCount):   #if it's a valid spot then move it
            patterns.jumpToPattern(newPattern)

    return True 

def HandleGridLR(ctrlID):
    prn(lvlH, 'HandleGridLR()', ctrlID)
    if(_AltHeld):
        if(ctrlID == IDBankL):
            DisplayTimedText('hZoom Out')
            ui.horZoom(2)
        else:
            DisplayTimedText('hZoom In')
            ui.horZoom(-2)
    return True

def HandleKnobMode():
    #prn(lvlH, 'HandleKnobMode()')
    NextKnobMode()
    return True

def HandleKnob(event, ctrlID):
    event.inEv = event.data2
    if event.inEv >= 0x40:
        event.outEv = event.inEv - 0x80
    else:
        event.outEv = event.inEv
    event.isIncrement = 1
    value = event.outEv

    prn(lvlH, 'HandleKnob()', event.data1, event.data2, ctrlID, channels.channelNumber(), _KnobMode)

    if _KnobMode == UM_CHANNEL :
        chanNum = channels.channelNumber()
        recEventID = channels.getRecEventId(chanNum)
        if chanNum > -1: # -1 is none selected
            # check if a pad is being held for the FPC params
            pMapPressed = next((x for x in _PadMap if x.Pressed == 1), None) 
            heldPadIdx = -1
            if(pMapPressed != None):
                if(pMapPressed.PadIndex in pdFPCA):
                    heldPadIdx = pdFPCA.index(pMapPressed.PadIndex)
                elif(pMapPressed.PadIndex in pdFPCB):
                    heldPadIdx = pdFPCB.index(pMapPressed.PadIndex) + 64 # internal offset for FPC Params Bank B

            if ctrlID == IDKnob1:
                if(PAD_MODE == MODE_DRUM) and (heldPadIdx > -1) and (isFPCActive()):
                    return HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Volume.Offset + heldPadIdx, event.outEv, ppFPC_Volume.Caption, ppFPC_Volume.Bipolar)
                else:
                    return HandleKnobReal(recEventID + REC_Chan_Vol,  value, 'Channel Volume', False)

            elif ctrlID == IDKnob2:
                if(PAD_MODE == MODE_DRUM) and (heldPadIdx > -1) and (isFPCActive()):
                    return HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Pan.Offset + heldPadIdx, event.outEv, ppFPC_Pan.Caption, ppFPC_Pan.Bipolar)
                else:
                    return HandleKnobReal(recEventID + REC_Chan_Pan, value, 'Channel Pan', True)

            elif ctrlID == IDKnob3:
                if(PAD_MODE == MODE_DRUM) and (heldPadIdx > -1) and (isFPCActive()):
                    return HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Tune.Offset + heldPadIdx, event.outEv, ppFPC_Tune.Caption, ppFPC_Tune.Bipolar)
                else:
                    return HandleKnobReal(recEventID + REC_Chan_FCut, value, 'Channel Filter', False)

            elif ctrlID == IDKnob4:
                return HandleKnobReal(recEventID + REC_Chan_FRes, value, 'Channel Resonance', False)

            else:
                return True 
    elif _KnobMode == UM_MIXER :
        mixerNum = mixer.trackNumber()
        mixerName = mixer.getTrackName(mixerNum) 
        recEventID = mixer.getTrackPluginId(mixerNum, 0)
        if not ((mixerNum < 0) | (mixerNum >= mixer.getTrackInfo(TN_Sel)) ): # is one selected?
            if ctrlID == IDKnob1:
                return HandleKnobReal(recEventID + REC_Mixer_Vol,  value, mixerName + ' Vol', False)
            elif ctrlID == IDKnob2:
                return HandleKnobReal(recEventID + REC_Mixer_Pan,  value, mixerName + ' Pan', True)
            elif ctrlID == IDKnob3:
                return HandleKnobReal(recEventID + REC_Mixer_EQ_Gain,  value, mixerName + ' EQ Lo', True)
            elif ctrlID == IDKnob4:
                return HandleKnobReal(recEventID + REC_Mixer_EQ_Gain + 2,  value, mixerName + ' EQ Hi', True)
    else: 
        return True    
    
def HandleKnobReal(recEventIDIndex, value, Name, Bipolar):
    knobres = 1/64
    currVal = device.getLinkedValue(recEventIDIndex)
    #prn(lvlH, 'HandleKnobReal', Name, value,  recEventIDIndex, Bipolar, currVal, knobres) 
    #general.processRECEvent(recEventIDIndex, value, REC_MIDIController)
    mixer.automateEvent(recEventIDIndex, value, REC_MIDIController, 0, 1, knobres) 
    currVal = device.getLinkedValue(recEventIDIndex)
    DisplayBar(Name, currVal, Bipolar)
    return True

def HandlePage(event, ctrlID):
    global _ShowChords
    global _PatternPage
    global _ChannelPage


    #differnt modes use these differently
    if(PAD_MODE == MODE_PATTERNS):
        if(ctrlID == IDPage0): # Pat page 0
            _PatternPage = 1
        elif(ctrlID == IDPage1):
            _PatternPage = 2
        elif(ctrlID == IDPage2):
            _ChannelPage = 1
            RefreshChannelStrip()
        elif(ctrlID == IDPage3):
            _ChannelPage = 2
            RefreshChannelStrip()
    
        HandlePatternChanges()
        RefreshPageLights()

    elif(PAD_MODE == MODE_NOTE) and (ctrlID == IDPage0): 
        if(_ScaleIdx > 0):
            _ShowChords = not _ShowChords
        else:    
            _ShowChords = False
        RefreshNotes()


    prn(lvlH, 'HandlePage()', ctrlID, _CurrentPage)
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
    #prn(lvlH, 'HandlePadMode')
    global PAD_MODE
    oldPadMode = PAD_MODE
    ctrlID = event.data1 

    if(ctrlID == IDStepSeq):
        PAD_MODE = MODE_PATTERNS
        
    elif(ctrlID == IDNote):
        PAD_MODE = MODE_NOTE
    elif(ctrlID == IDDrum):
        PAD_MODE = MODE_DRUM
    elif(ctrlID == IDPerform):
        PAD_MODE = MODE_PERFORM

    RefreshPadModeButtons() # lights the button

    if(oldPadMode != PAD_MODE):
        ClearPadMaps()

    RefreshAll()
    return True

def RefreshAll():
    RefreshPads()
    RefreshModes()
    RefreshDisplay()
    RefreshMacros()
    RefreshNavPads()

def RefreshModes():
    if(PAD_MODE == MODE_DRUM):
        RefreshDrumPads()
    elif(PAD_MODE == MODE_PATTERNS):
        RefreshPatternPads() 
    elif(PAD_MODE == MODE_NOTE):
        RefreshNotes()

def RefreshPatternPads():
    # time.sleep(0.2)
    UpdatePatternPadMap()
    UpdatePatternMap(_CurrentPattern)
    RefreshMacros()
    RefreshNavPads()
    prn(lvlR, 'RefreshPatternPads()')

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
    RefreshShifted()
    event.handled = True 


# Refresh
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
        RefreshShifted()
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

def RefreshShifted():
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
        color = colMacros[idx]
        SetPadColor(pad, color, dimDefault)

def RefreshNavPads():
    # mode specific
    showPresetNav = False
    showNoteRepeat = False

    for pad in pdNav :
        SetPadColor(pad, cOff, dimDefault)

    if(PAD_MODE == MODE_NOTE):
        for pad in pdNoteFuncs:
            idx = pdNoteFuncs.index(pad)
            color = colNoteFuncs[idx]
            SetPadColor(pad, color, dimDefault)
    elif (PAD_MODE == MODE_DRUM):
        showPresetNav = True
        showNoteRepeat = True
    elif (PAD_MODE == MODE_PATTERNS):    
        showPresetNav = True

    if(showPresetNav):
        for pad in pdPresetNav :
            idx = pdPresetNav.index(pad)
            color = colPresetNav[idx]
            SetPadColor(pad, color, dimDefault)

    if(showNoteRepeat):
        SetPadColor(pdNoteRepeat, colNoteRepeat, dimDefault)


def RefreshPageLights():
    prn(lvlR, 'RefreshPageLights()', _ShowChords, _PatternPage, _ChannelPage)
    SendCC(IDPage0, SingleColorOff)
    SendCC(IDPage1, SingleColorOff)
    SendCC(IDPage2, SingleColorOff)
    SendCC(IDPage3, SingleColorOff)                    
    if(PAD_MODE == MODE_NOTE):
        if(_ShowChords):
            SendCC(IDPage0, SingleColorHalfBright)
    if(PAD_MODE == MODE_PATTERNS):
        #pattern page
        if(_PatternPage == 0):
            SendCC(IDPage0, SingleColorFull)
        elif(_PatternPage == 1):
            SendCC(IDPage1, SingleColorFull)
        #channel page
        if(_ChannelPage == 0):
            SendCC(IDPage2, SingleColorFull)
        elif(_ChannelPage == 1):
            SendCC(IDPage3, SingleColorFull)

def isChromatic():
    return (_ScaleIdx == 0) #chromatic

def RefreshNotes():
    global _PadMap

    prn(lvlR, 'RefreshNotes()', 'isChomatic', isChromatic(), 'SHowChords', _ShowChords)

    if(_ShowChords) and (not isChromatic()):
        RefreshPageLights()

    if(isChromatic()):
        rootNote = 0
        showRoot = False
    else:
        rootNote = _NoteIdx
        showRoot = True 

    baseOctave = OctavesList[_OctaveIdx]

    GetScaleGrid(_ScaleIdx, rootNote, baseOctave) #this will populate _PadMap.NoteInfo

    for p in pdWorkArea:
        color = cDimWhite
        dim = dimDefault-2

        #prn(lvl0, utils.GetNoteName(_PadMap[p].NoteInfo.MIDINote), _PadMap[p].NoteInfo.IsRootNote )
        if(isChromatic()): #chromatic,
            if(len(utils.GetNoteName(_PadMap[p].NoteInfo.MIDINote) ) > 2): # is black key?
                color = cOff
            else:
                color = cWhite 
        else: #non chromatic
            if(_PadMap[p].NoteInfo.IsRootNote) and (showRoot):
                if(DEFAULT_ROOT_NOTE_COLOR == cChannel):
                    color = PadColorFromFLColor(channels.getChannelColor(channels.channelNumber()))
                else:
                    color = DEFAULT_ROOT_NOTE_COLOR

        if(_ShowChords) and (p in pdChordBar):
            SetPadColor(p, cBlueMed, dim)
        elif(_ShowChords) and (p in pdChordFuncs):
            offs = pdChordFuncs.index(p)
            SetPadColor(p, colChordFuncs[offs], dim)
            if(_Chord7th) and (offs == pd7th):
                SetPadColor(p, colChordFuncs[pdChordFuncs.index(p)], dimDefault)
            if(_ChordInvert) and (offs == pdInv):
                SetPadColor(p, colChordFuncs[pdChordFuncs.index(p)], dimDefault)
        else:
            SetPadColor(p, color, dim)

    # set the specific mode related funcs here

    RefreshMacros() 
    RefreshNavPads()

def RefreshDrumPads():
    global _PadMap
    
    if( isFPCActive() ):  # Show Custom FPC Colors
        PAD_Count =	0	#Retrieve number of pad parameters supported by plugin
        PAD_Semitone =	1	#Retrieve semitone for pad specified by padIndex
        PAD_Color =	2	#Retrieve color for pad specified by padIndex    

        chanIdx = channels.channelNumber()    

        # FPC A Pads
        fpcpadIdx = 0
        semitone = 0
        color = cOff
        dim =  dimDefault
        for p in pdFPCA:
            color = plugins.getPadInfo(chanIdx, -1, PAD_Color, fpcpadIdx) # plugins.getColor(chanIdx, -1, GC_Semitone, fpcpadIdx)
            semitone = plugins.getPadInfo(chanIdx, -1, PAD_Semitone, fpcpadIdx)
            #prn(lvl0, fpcpadIdx, 'semitone', semitone , 'color', color)
            _PadMap[p].FPCColor = PadColorFromFLColor(color)
            _PadMap[p].NoteInfo.MIDINote = semitone 
            SetPadColor(p, _PadMap[p].FPCColor, dim)
            fpcpadIdx += 1 # NOTE! will be 16 when we exit the for loop, the proper first value for the B Pads loop...
        # FPC B Pads
        for p in pdFPCB:
            color = plugins.getPadInfo(chanIdx, -1, PAD_Color, fpcpadIdx) 
            semitone = plugins.getPadInfo(chanIdx, -1, PAD_Semitone, fpcpadIdx) 
            _PadMap[p].FPCColor = PadColorFromFLColor(color)
            _PadMap[p].NoteInfo.MIDINote = semitone 
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
            if(plugins.getPluginName(chan, -1, 0) == "FPC"):
                padNum = pdFPCChannels[idx]
                padColor = PadColorFromFLColor(channels.getChannelColor(chan))
                if(channels.channelNumber() == chan):
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

def UpdatePatternPadMap():
    prn(lvl0, 'UpdatePatternPadMap()')
    global _PadMap
    global _PatternMap
    global _PatternCount

    _PatternCount = patterns.patternCount()
    
    if(len(_PatternMap) != _PatternCount):
        UpdatePatternMap(-1)
        _PatternCount = patterns.patternCount()

    if(PAD_MODE == MODE_PATTERNS): # Pattern mode, set the pattern buttons
        ClearPadMaps()
        pageLen = len(pdPatterns)
        pageOffs = _CurrentPage * pageLen 
        for patt in range(0, pageLen): # _PatternCount ):
            pattNum = patt + pageOffs
            if(pattNum < _PatternCount):
                FLPattNum = pattNum+1
                padIdx = pdPatterns[patt] # 0 based
                padColor = PadColorFromFLColor(patterns.getPatternColor(FLPattNum)) # FL is 1-based
                _PatternMap[pattNum].Color = padColor
                pMap = TnfxPadMap(padIdx, FLPattNum, padColor, "")
                _PadMap[padIdx] = pMap
                # add the corresponding mute btn
                padIdx = pdMutes[patt]
        RefreshPatternPads() 

def UpdatePatternMap(pattNum):
    global _PatternMap
    #prn(lvlU, 'UpdatePatternMap', pattNum, len(_PatternMap))

    chanNum = channels.channelNumber()
    mixNum = channels.getTargetFxTrack(chanNum)
    nfxMixer = TnfxMixer(mixNum, mixer.getTrackName(mixNum))

    if(pattNum < 0):  #ENUMERATE ALL PATTERNS
        _PatternMap.clear()
        for pat in range(_PatternCount):
            patMap = TnfxPattern(pat, patterns.getPatternName(pat))
            patMap.Color = patterns.getPatternColor(pat)
            patMap.Mixer = nfxMixer
            _PatternMap.append(patMap)
    else: #update the current pattern's channels map only
        RefreshChannelStrip()     
        


#misc functions 
def isFPCActive():
    chanIdx = channels.channelNumber()
    pluginName = plugins.getPluginName(chanIdx, -1, 0)      
    return (pluginName == 'FPC') 


def CopyPattern(FLPattern):
    prn(lvl0, 'copy pattern')
    ui.showWindow(widChannelRack)
    chanIdx = channels.channelNumber()
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

def RefreshPatternPads():
    prn(lvlR, 'RefreshPatternPads()', _PatternPage)
    patternsPerPage = len(pdPatterns) 
    for i in range(0, patternsPerPage):
        padIdx = pdPatterns[i]
        mutePadIdx = pdMutes[i]
        pMap = _PadMap[padIdx] # 0-based
        if(patterns.patternNumber() == pMap.FLPattern): #current pattern
            SetPadColor(pMap.PadIndex, pMap.Color, dimBright)
            SetPadColor(mutePadIdx, cWhite, dimBright)
        else:
            SetPadColor(pMap.PadIndex, pMap.Color, dimDefault)
            if(pMap.Color != cOff):
                SetPadColor(mutePadIdx, cDimWhite, 4)
            else:
                SetPadColor(mutePadIdx, cOff, 4)

def ClearPadMaps():
    global _PadMap
    _PadMap.clear()
    for padIdx in range(0, 64):
        _PadMap.append(TnfxPadMap(padIdx, -1, 0x000000, ""))
    RefreshPads()


def NextKnobMode():
    global _KnobMode
    prn(lvl0, 'next knob mode. was', _KnobMode)

    _KnobMode += 1
    
    if(_KnobMode > 3):
        _KnobMode = 0    

    RefreshKnobMode()

def RefreshChannelStrip(): # was (patMap: TnfxPattern, nfxMixer):
    global _PatternMap
    global _CurrentPattern

    _CurrentPattern = patterns.patternNumber()
    prn(lvlR, 'RefreshChannelStrip()', 'Pattern', _CurrentPattern, len(_PatternMap))
    if(len(_PatternMap) == 0):
        return

    patMap = GetPatternMapActive() # _PatternMap[_CurrentPattern-1]
    patMap.Channels.clear()

    for padIdx in pdChanStrip:
        SetPadColor(padIdx, cOff, 0)
    
    for padIdx in pdChanStripMutes:
        SetPadColor(padIdx, cOff, 0)
    
    currChan = channels.channelNumber()
    mixerIdx = channels.getTargetFxTrack(currChan)
    mixer.deselectAll()
    mixer.selectTrack(mixerIdx)

    idx = 0
    padColor = cOff
    #enum channels with same mixNum
    for chan in range(channels.channelCount()):
        if(channels.getTargetFxTrack(chan) > 0): # == mixerIdx):
            padColor = PadColorFromFLColor(channels.getChannelColor(chan))

        # check if there is room on the channel strip
        if(idx < len(pdChanStrip)): 
            # below needed for HandleChannelStrip()
            nfxChannel = TnfxChannel(chan, channels.getChannelName(chan))
            nfxChannel.Mixer = TnfxMixer(mixerIdx, "")
            nfxChannel.Color = padColor 
            patMap.Channels.append(nfxChannel)
            padIdx = pdChanStrip[idx]
            mutepadIdx = pdChanStripMutes[idx]
            dim = dimDefault
            if(channels.isChannelSelected(chan)):
                dim = dimBright
            SetPadColor(padIdx, padColor, dim)
            SetPadColor(mutepadIdx, cWhite, dim) 
            idx += 1

    RefreshDisplay()
    #RefreshNavPads()

def ResetBeatIndicators():
    for i in range(0, len(BeatIndicators) ):
        SendCC(BeatIndicators[i], SingleColorOff)

def ShowPianoRoll(showVal, bSave, bUpdateDisplay = False):
    global _PatternMap 
    currVal = 0

    if(len(_PatternMap) > 0):
        selPat = GetPatternMapActive() # _PatternMap[_CurrentPattern-1]  # 0 based
        currVal = selPat.ShowPianoRoll

    ui.showWindow(widChannelRack)
    chanNum = channels.selectedChannel(0, 0, 1)
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


    #prn(lvl0, 'ShowPR: ', _Patterns[selPatIdx].ShowPianoRoll)

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
    
    chanNum = channels.selectedChannel(0, 0, 1)
    channels.showCSForm(chanNum, showVal)
    if(showVal == 0): # make CR active
        ui.showWindow(widChannelRack)

    if(bUpdateDisplay):
        DisplayTimedText('Chan Sett: ' + _showText[showVal])

    if(bSave):
        if(len(_PatternMap) > 0):
            selPat.ShowChannelSettings = showVal
    #prn(lvl0, 'ShowCS: ', _Patterns[selPatIdx].ShowChannelSettings)

def ShowChannelEditor(showVal, bSave, bUpdateDisplay = False):
    global _PatternMap
    currVal = 0

    if(len(_PatternMap) > 0):
        selPat =  GetPatternMapActive() # _PatternMap[_CurrentPattern-1]  # 0 based
        currVal = selPat.ShowChannelEditor

    if(showVal == -1):  # toggle
        if(currVal == 0):
            showVal = 1
        else:
            showVal = 0

    ui.showWindow(widChannelRack)
    chanNum = channels.selectedChannel(0, 0, 1)
    channels.showEditor(chanNum, showVal)

    if(bUpdateDisplay):
        DisplayTextBottom('Chan Editor: ' + _showText[showVal])

    if(showVal == 0): # make CR active
        ui.showWindow(widChannelRack)

    if(bSave):
        if(len(_PatternMap) > 0):
            selPat.ShowChannelEditor = showVal

def ShowPlaylist(showVal, bUpdateDisplay = False):
    global _ShowPlaylist

    if(showVal == -1): # toggle
        if(_ShowPlaylist == 1):
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

    if(showVal == -1): # toggle
        if(_ShowMixer == 1):
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

    if(showVal == -1): #toggle
        if(_ShowChanRack == 1):
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

    if(showVal == -1): #toggle
        if(_ShowBrowser == 1):
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

def GetScaleGrid(newModeIdx=0, rootNote=0, startOctave=2):
    global _PadMap 
#    global _keynote 
    global _ScaleNotes 
    global _ScaleDisplayText
    global _ScaleIdx


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

            _PadMap[padIdx].NoteInfo.IsRootNote = (colOffset % notesInScale) == 0 # (colOffset == 0) or (colOffset == notesInScale)

    _ScaleDisplayText = NotesList[_faveNoteIdx] + str(startOctave) + " " + HarmonicScaleNamesT[harmonicScale]
    #prn(lvl0, 'Scale:',_ScaleDisplayText)
    RefreshDisplay() #    DisplayTimedText('Scale: ' + _ScaleDisplayText)

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

def HandleChord(chan, chordNum, noteOn, noteVelocity, play7th, playInverted):
    prn(lvlH, 'HandleChord()', chan, chordNum, noteVelocity, play7th, playInverted )
    global _ChordNum
    global _ChordInvert
    global _Chord7th

    if (GetScaleNoteCount(_ScaleIdx) != 7): #if not enough notes to make full chords, do not do anything
        return 

    chordTypes = ['','m','m','','','m','dim']
    chordName = ''

    note =  -1#the target root note
    note3 = -1
    note5 = -1
    note7 = -1
    note5inv = -1    
    offset = 0

    if(0 < chordNum < 8): #if a chord, then use the _ScaleNotes to find the notes
        offset = GetScaleNoteCount(_ScaleIdx) + (chordNum-1)
        note = _ScaleNotes[offset]
        note3 = _ScaleNotes[offset + 2]
        note5 = _ScaleNotes[offset + 4]
        note7 = _ScaleNotes[offset + 6]
        note5inv = _ScaleNotes[offset - 3] 
        chordName = NotesList[note % 12]
        chordName += chordTypes[ ((_ScaleIdx + chordNum) % 7)-1 ]
        #prn(lvl0, 'chord', chordNum, _ScaleIdx)

    if(noteOn):
        #
        PlayMIDINote(chan, note, noteVelocity)
        PlayMIDINote(chan, note3, noteVelocity)

        _ChordNum = chordNum
        _ChordInvert = playInverted
        _Chord7th = play7th

        if(play7th):
            chordName += '7'
            PlayMIDINote(chan, note7, noteVelocity)        

        if(playInverted):
            chordName += ' inv'
            PlayMIDINote(chan, note5inv, noteVelocity)
        else:
            PlayMIDINote(chan, note5, noteVelocity)


        DisplayTimedText('Chord: ' + chordName)

    else:
        # turn off the chord
        PlayMIDINote(chan, note, noteVelocity)
        PlayMIDINote(chan, note3, noteVelocity)
        PlayMIDINote(chan, note5, noteVelocity)
        
        if(playInverted):
            PlayMIDINote(chan, note5inv, noteVelocity)
        if(play7th):            
            PlayMIDINote(chan, note7, noteVelocity)

        _ChordInvert = False
        _ChordNum = -1
        _Chord7th = play7th

        
def PlayMIDINote(chan, note, velocity):
    prn(lvl0, 'Chan', chan, 'Note Value:', utils.GetNoteName(note), note, velocity)
    if(chan > -1):
        if(velocity > 0):
            channels.midiNoteOn(chan, note, velocity)
            #ShowNote(note, True)
        else:
            channels.midiNoteOn(chan, note, -1)
            #ShowNote(note, False)

def prn(lvl, *objects):
    prefix = prnLevels[lvl][1]
    if(_DebugPrn and (lvl >= _DebugMin)) or (lvl == lvlA):
        print(prefix, *objects)    

    


