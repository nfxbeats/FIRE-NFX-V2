# name=NFX Test

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
_CurrentKnobMode = 0
_CurrentPage = 0 
_Beat = 1
_PadMap = list()
_PatternMap = list()
_ShowMixer = 1
_ShowChanRack = 1
_ShowPlaylist = 1
_ShowBrowser = 1
_showText = ['OFF', 'ON']


# FL Events
def OnInit():
    #print('OnInit')

    SetPage(0)
    ResetBeatIndicators()
    RefreshKnobMode()

    SendCC(IDPatternUp, SingleColorOff)
    SendCC(IDPatternDown, SingleColorOff)
    SendCC(IDBankL, SingleColorOff)
    SendCC(IDBankR, SingleColorOff)
    SendCC(IDBrowser, SingleColorOff)    

    for pad in range(0,64):
        SetPadColor(pad, 0x000000, 0)
        
    
    RefreshPadModeButtons()
    RefreshTransport()
    RefreshShiftAlt()

    InitDisplay()
    DisplayTextTop("nfxTest")

    RefreshPatternPadMap()
    RefreshMacros()
    RefreshPatternMap(patterns.patternNumber())

    ShowPlaylist(1)

def OnIdle():
    if(_ShiftHeld):
        RefreshShifted() 

def OnMidiMsg(event):
    print("OnMidiMsg", event.data1, event.data2)

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

def OnRefresh(flags):
    #print('refresh', flags)
    HW_Dirty_Patterns = 1024
    if(HW_Dirty_Patterns & flags):
        print('pattern event')
        HandlePatternChanges()
    if(HW_ChannelEvent & flags):
        print('channel event')
        if (PAD_MODE == MODE_DRUM):
            RefreshDrumPads()
        elif(PAD_MODE == MODE_PATTERNS):
            RefreshChannelStrip()
    if(HW_Dirty_Colors & flags):
        print('color change event')
        if (PAD_MODE == MODE_DRUM):
            RefreshDrumPads()
        elif(PAD_MODE == MODE_PATTERNS):
            RefreshChannelStrip()

    if(HW_Dirty_Tracks & flags):
        print('track change event')
    if(HW_Dirty_Mixer_Sel & flags):
        print('mixer sel event')

def OnProjectLoad(status):
    print('OnProjectLoad', status)
    # status = 0 = starting load?
    # status = 100 = finished laoding

def OnMidiIn(event):
    global _ShiftHeld
    global _AltHeld
    global _PadMap
    

    print("OnMidiIn", event.data1, event.data2)
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
        #print('Pad Detected', padNum)

        if(event.data2 > 0): # pressed
            pMap.Pressed = 1
        else:
            pMap.Pressed = 0

        if(PAD_MODE == MODE_DRUM): # handles on and off
            event.handled = HandlePads(event, padNum, pMap)
        
        # if STEP/PATTERN mode, treat as controls and not notes...
        if(PAD_MODE == MODE_PATTERNS):
            if(pMap.Pressed == 1): # On Pressed
                event.handled = HandlePads(event, padNum, pMap)
            else:
                event.handled = True #prevents a note off message

    # handle other
    #print('Non Pad detected')
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
    print ('Note On', utils.GetNoteName(event.data1),event.data1,event.data2)
           
def OnNoteOff(event):
    print ('Note Off', utils.GetNoteName(event.data1),event.data1,event.data2)

def GetActivePatternMap():
    return _PatternMap[_CurrentPattern-1]

# handlers
def HandleChannelStrip(padNum, isChannelStripMute):
    global _PatternMap

    if(isChannelStripMute):
        idx = pdChanStripMutes.index(padNum)
    else:
        idx = pdChanStrip.index(padNum)

    prevChanIdx = channels.channelNumber()
    patMap = GetActivePatternMap() # _PatternMap[_CurrentPattern-1] # 0 - based
    nfxChannels = patMap.Channels 
    selChanIdx = nfxChannels[idx].FLIndex
    #print('handle chanstrip', padNum, 'patt', _CurrentPattern, 'prevChanIdx', prevChanIdx, 'new chan', selChanIdx)

    if(prevChanIdx == selChanIdx): # if it's already on the channel, toggle the windows
        if (isChannelStripMute):
            ShowPianoRoll(-1, True) #not patMap.ShowPianoRoll)
        else:
            ShowChannelEditor(-1, True) #not patMap.ShowChannelEditor)
    else: #'new' channel, close the previous windows first
        ShowPianoRoll(0, False)
        ShowChannelEditor(0, False)
        channels.selectOneChannel(selChanIdx)
        if (isChannelStripMute):
            ShowPianoRoll(patMap.ShowPianoRoll, True)
        else:
            ShowChannelEditor(patMap.ShowChannelEditor, True)

    #RefreshPatterns(_CurrentPattern)
    RefreshPatternDisplay()
    return True

    print('handle pads', padNum)
def HandlePads(event, padNum, pMap):
    print('HandlePads', _CurrentPattern)
    # some pads will need a pressed AND release...
    if(PAD_MODE == MODE_DRUM):
        if (padNum in pdFPCA) or (padNum in pdFPCB) or (padNum in pdFPCChannels):
            return HandleDrums(event, padNum)
        else:
            return True 

    # some pads we only need on pressed event
    if(event.data2 > 0): # On Pressed
        if(padNum in pdPresetNav):
            padIdx = pdPresetNav.index(padNum)
            HandlePresetNav(padIdx)
            return True

        if(padNum in pdMacroStrip):
            macIdx = pdMacroStrip.index(padNum)
            HandleMacros(macIdx)
            return True 

        if(PAD_MODE == MODE_PATTERNS):
            if(padNum in pdMutes):
                event.handled = HandleMuteButtons(padNum)
            elif(padNum in pdChanStrip):
                event.handled = HandleChannelStrip(padNum, False)   
            elif(padNum in pdChanStripMutes):
                event.handled = HandleChannelStrip(padNum, True)   
            elif(pMap.FLPattern > 0): # I dont think this is correct....
                #if(event.data2 > 0): # On Press only
                if(_CurrentPattern != pMap.FLPattern):
                    patterns.jumpToPattern(pMap.FLPattern)
                    ui.hideWindow(widPianoRoll)
                    ui.hideWindow(5) #widPlugin
                elif(_AltHeld): # already on this pattern, check if alt is held    
                    CopyPattern(pMap.FLPattern)

    return True

def HandlePresetNav(padIdx):
    print('presetNav', padIdx)
    ShowChannelEditor(1, True)
    #ui.setFocused(5) #widPlugin
    if(padIdx == 0):
        ui.previous()
    else:
        ui.next()
    RefreshPatternDisplay()

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
        ShowBrowser(1)
        ShowChannelRack(1)
        ShowPlaylist(1)
        ShowMixer(1)
    elif(macIdx == 5):
        DisplayTimedText('Copy')
        ui.copy()
    elif(macIdx == 6):
        DisplayTimedText('Cut')
        ui.cut()
    elif(macIdx == 7):
        DisplayTimedText('Paste')
        ui.paste()


def HandleDrums(event, padNum):
    chanNum = _PadMap[padNum].ItemIndex
#    print('handle drums', 'in', event.data1, 'out', _PadMap[padNum].MIDINote)
    if(padNum in pdFPCA) or (padNum in pdFPCB):
        event.data1 = _PadMap[padNum].MIDINote
        if(90 > event.data2 > 1 ):
            event.data2 = 90
        elif(110 > event.data2 > 64):
            event.data2 = 110
        elif(event.data2 > 110):
            event.data2 = 120
        return False # false to continue processing
    elif(chanNum > -1):
        print('x', chanNum)
        channels.selectOneChannel(chanNum)
        ShowChannelEditor(1, False)
        RefreshPatternDisplay()
        return True 
    else:
        return True # mark as handled to prevent processing


def HandleMuteButtons(padNum):
    btnIdx = pdMutes.index(padNum)
    patt = _PatternMap[btnIdx+1]
    if(patterns.patternNumber() == patt.FLIndex):
        print('show piano roll')
    else:
        # close any piano roll
        patterns.jumpToPattern(patt.FLIndex)
    return True 

def HandlePatternChanges():
    global _PatternCount
    global _CurrentPattern

    if (_PatternCount > 0) and  (PAD_MODE == MODE_PATTERNS): # do pattern mode
        currPattern = patterns.patternNumber()
        chanNum = channels.channelNumber()
        print('Refresh Patterns', patterns.patternCount(), currPattern, _PatternCount)

        if(_PatternCount != patterns.patternCount()):
            print('pattern added/removed')
            _PatternCount = patterns.patternCount()
            currPattern = patterns.patternNumber()
            RefreshPatternPadMap()
        else:
            print('selected pattern changed', currPattern)
            if _CurrentPattern != currPattern:
                currPattern = patterns.patternNumber()
                UpdatePatternPads()
        _CurrentPattern = patterns.patternNumber()
        
        RefreshPatternMap(_CurrentPattern) 

    if(patterns.patternCount() == 0) and (currPattern == 1): # empty project, set to 1
        _PatternCount = 1

    RefreshPatternDisplay()

def RefreshPatternDisplay():
    DisplayTextTop(patterns.getPatternName(patterns.patternNumber()))
    DisplayTimedText(channels.getChannelName(channels.channelNumber()))

def HandlePattUpDn(ctrlID):
    #print('handle pattupdn')
    if(_AltHeld):
        if(ctrlID == IDPatternUp):
            DisplayTimedText('vZoom Out')
            ui.verZoom(2)
        else:
            DisplayTimedText('vZoom In')
            ui.verZoom(-2)
    return True 

def HandleGridLR(ctrlID):
    if(_AltHeld):
        if(ctrlID == IDBankL):
            DisplayTimedText('hZoom Out')
            ui.horZoom(2)
        else:
            DisplayTimedText('hZoom In')
            ui.horZoom(-2)
    return True

def HandleKnobMode():
    #print('handle mode')
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

    #print('handle knob', event.data1, event.data2, ctrlID, channels.channelNumber())
    if _CurrentKnobMode == UM_CHANNEL :
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
                    heldPadIdx = pdFPCB.index(pMapPressed.PadIndex)+64 # internal offset for FPC Params Bank B


            if ctrlID == IDKnob1:
                if(PAD_MODE == MODE_DRUM):
                    if(heldPadIdx > -1) and (isFPCActive()):
                        return HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Volume.Offset + heldPadIdx, event.outEv, ppFPC_Volume.Caption, ppFPC_Volume.Bipolar)
                else:
                    return HandleKnobReal(recEventID + REC_Chan_Vol,  value, 'Channel Volume', False)

            elif ctrlID == IDKnob2:
                if(PAD_MODE == MODE_DRUM):
                    if(heldPadIdx > -1) and (isFPCActive()):
                        return HandleKnobReal(recEventID + REC_Chan_Plugin_First + ppFPC_Pan.Offset + heldPadIdx, event.outEv, ppFPC_Pan.Caption, ppFPC_Pan.Bipolar)
                else:
                    return HandleKnobReal(recEventID + REC_Chan_Pan, value, 'Channel Pan', True)
            elif ctrlID == IDKnob3:
                return HandleKnobReal(recEventID + REC_Chan_FCut, value, 'Channel Filter', False)
            elif ctrlID == IDKnob4:
                return HandleKnobReal(recEventID + REC_Chan_FRes, value, 'Channel Resonance', False)
            else:
                return True 
    elif _CurrentKnobMode == UM_MIXER :
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
    #print('HandleKnobReal', Name, value,  recEventIDIndex, Bipolar, currVal, knobres) 
    #general.processRECEvent(recEventIDIndex, value, REC_MIDIController)
    mixer.automateEvent(recEventIDIndex, value, REC_MIDIController, 0, 1, knobres) 
    currVal = device.getLinkedValue(recEventIDIndex)
    DisplayBar(Name, currVal, Bipolar)
    return True

def HandlePage(event, ctrlID):
    SetPage(PageCtrls.index(ctrlID))
    #print('handlepage', _CurrentPage)
    return True

def HandleShiftAlt(event, ctrlID):
    global _ShiftHeld
    global _AltHeld
    
    #print('shift/alt')
    if(ctrlID == IDShift):
        _ShiftHeld = (event.data2 > 0)
    elif(ctrlID == IDAlt):
        _AltHeld = (event.data2 > 0)

    RefreshShiftAlt()

def HandlePadMode(event):
    #print('padmode')
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

    if(PAD_MODE == MODE_DRUM):
        RefreshDrumPads()
    elif(PAD_MODE == MODE_PATTERNS):
        RefreshPatternPads() 

    return True

def RefreshPatternPads():
    # time.sleep(0.2)
    RefreshPatternPadMap()
    RefreshPatternMap(_CurrentPattern)
    RefreshMacros()
    RefreshPresetNav()
    print('RefreshPatternPads')

def HandleTransport(event):
    #print('.....Transport OnPress', event.data1)
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
    print('Shifted', event.data1)
    ctrlID = event.data1
    if(ctrlID == IDAccent):
        print('accent')
    elif(ctrlID == IDSnap):
        transport.globalTransport(FPT_Snap, 1)
    elif(ctrlID == IDTap):
        transport.globalTransport(FPT_TapTempo, 1)
    elif(ctrlID == IDOverview):
        print('overview')
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
    for pad in pdMacroStrip:
        idx = pdMacroStrip.index(pad)
        color = colMacroStrip[idx]
        SetPadColor(pad, color, dimDefault)

def RefreshPresetNav():
    for pad in pdPresetNav :
        idx = pdPresetNav.index(pad)
        color = colPresetNav[idx]
        SetPadColor(pad, color, dimDefault)


def RefreshPage():
    for i in range(0, len(PageCtrls)):
        if(i == _CurrentPage):
            SendCC(PageCtrls[i], SingleColorFull)
        else:
            SendCC(PageCtrls[i], SingleColorOff)
    RefreshPatternPads()

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
            #print(fpcpadIdx, 'semitone', semitone , 'color', color)
            _PadMap[p].FPCColor = PadColorFromFLColor(color)
            _PadMap[p].MIDINote = semitone 
            SetPadColor(p, _PadMap[p].FPCColor, dim)
            fpcpadIdx += 1 # NOTE! will be 16 when we exit the for loop, the proper first value for the B Pads loop...
        # FPC B Pads
        for p in pdFPCB:
            color = plugins.getPadInfo(chanIdx, -1, PAD_Color, fpcpadIdx) 
            semitone = plugins.getPadInfo(chanIdx, -1, PAD_Semitone, fpcpadIdx) 
            _PadMap[p].FPCColor = PadColorFromFLColor(color)
            _PadMap[p].MIDINote = semitone 
            SetPadColor(p, _PadMap[p].FPCColor, dim)
            fpcpadIdx += 1 # continue 
    
        idx = 0;
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
    RefreshPresetNav()



def RefreshKnobMode():
    LEDVal = IDKnobModeLEDVals[_CurrentKnobMode] | 16
    #print('refreshmode. knob mode is', _CurrentKnobMode, 'led bit', IDKnobModeLEDVals[_CurrentKnobMode], 'val', LEDVal)
    SendCC(IDKnobModeLEDArray, LEDVal)

def RefreshPatternPadMap():
    print('Refresh PatternMap')
    global _PadMap
    global _PatternMap
    global _PatternCount

    _PatternCount = patterns.patternCount()
    
    if(len(_PatternMap) != _PatternCount):
        RefreshPatternMap(-1)
        _PatternCount = patterns.patternCount()


    if(PAD_MODE == MODE_PATTERNS): # Pattern mode, set the pattern buttons
        ClearPadMaps()
        pageLen = len(pdPatterns)
        pageOffs = _CurrentPage * pageLen 
        #print('RefreshPadMap', _CurrentPage, pageLen, pageOffs, _PatternCount)
        for patt in range(0, pageLen): # _PatternCount ):
            pattNum = patt + pageOffs
            if(pattNum < _PatternCount):
                FLPattNum = pattNum+1
                #print('PattNum', pattNum)
                padIdx = pdPatterns[patt] # 0 based
                padColor = PadColorFromFLColor(patterns.getPatternColor(FLPattNum)) # FL is 1-based
                _PatternMap[pattNum].Color = padColor
                pMap = TnfxPadMap(padIdx, FLPattNum, padColor, "")
                _PadMap[padIdx] = pMap
                # add the corresponding mute btn
                padIdx = pdMutes[patt]
        UpdatePatternPads() 

def RefreshPatternMap(pattNum):
    global _PatternMap
    #print('refresh patterns', pattNum, len(_PatternMap))

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
        #print('x', pattNum, _PatternCount)
        RefreshChannelStrip()      
        DisplayTextTop(patterns.getPatternName(pattNum))
        DisplayTimedText(channels.getChannelName(chanNum))


#misc functions 
def isFPCActive():
    chanIdx = channels.channelNumber()
    pluginName = plugins.getPluginName(chanIdx, -1, 0)      
    return (pluginName == 'FPC') 


def CopyPattern(FLPattern):
    print('copy pattern')
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
    print('---- copy pattern')

def UpdatePatternPads():
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
    global _CurrentKnobMode
    print('next knob mode. was', _CurrentKnobMode)

    _CurrentKnobMode += 1
    
    if(_CurrentKnobMode > 3):
        _CurrentKnobMode = 0    

    RefreshKnobMode()

def SetPage(page):
    global _CurrentPage
    _CurrentPage = page 
    RefreshPage()
       
    if(_CurrentKnobMode == MODE_PATTERNS):
        HandlePatternChanges()

def RefreshChannelStrip(): # was (patMap: TnfxPattern, nfxMixer):
    global _PatternMap
    global _CurrentPattern

    _CurrentPattern = patterns.patternNumber()
    print('updating channels for pattern', _CurrentPattern, len(_PatternMap))
    if(len(_PatternMap) == 0):
        return

    patMap = GetActivePatternMap() # _PatternMap[_CurrentPattern-1]
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
            if(idx < len(pdChanStripMutes)) and (channels.getTargetFxTrack(chan)  == mixerIdx): # do they share the same mixer num?
                SetPadColor(mutepadIdx, cDimWhite, dimDefault) 
            idx += 1

    RefreshPatternDisplay()
    RefreshPresetNav()

def ResetBeatIndicators():
    for i in range(0, len(BeatIndicators) ):
        SendCC(BeatIndicators[i], SingleColorOff)

def ShowPianoRoll(showVal, bSave):
    global _PatternMap 
    currVal = 0

    if(len(_PatternMap) > 0):
        selPat = GetActivePatternMap() # _PatternMap[_CurrentPattern-1]  # 0 based
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

    DisplayTimedText('Piano Roll: ' + _showText[showVal])


    #print('ShowPR: ', _Patterns[selPatIdx].ShowPianoRoll)

def ShowChannelSettings(showVal, bSave):
    global _PatternMap
    currVal = 0

    if(len(_PatternMap) > 0):
        selPat = GetActivePatternMap() # _PatternMap[_CurrentPattern-1]  # 0 based
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

    DisplayTimedText('Chan Sett: ' + _showText[showVal])

    if(bSave):
        if(len(_PatternMap) > 0):
            selPat.ShowChannelSettings = showVal
    #print('ShowCS: ', _Patterns[selPatIdx].ShowChannelSettings)

def ShowChannelEditor(showVal, bSave):
    global _PatternMap
    currVal = 0

    if(len(_PatternMap) > 0):
        selPat =  GetActivePatternMap() # _PatternMap[_CurrentPattern-1]  # 0 based
        currVal = selPat.ShowChannelEditor

    if(showVal == -1):  # toggle
        if(currVal == 0):
            showVal = 1
        else:
            showVal = 0

    ui.showWindow(widChannelRack)
    chanNum = channels.selectedChannel(0, 0, 1)
    channels.showEditor(chanNum, showVal)
    DisplayTimedText('Chan Editor: ' + _showText[showVal])

    if(showVal == 0): # make CR active
        ui.showWindow(widChannelRack)

    if(bSave):
        if(len(_PatternMap) > 0):
            selPat.ShowChannelEditor = showVal
    #print('ShowCE: ', _Patterns[selPatIdx].ShowChannelEditor)

def ShowPlaylist(showVal):
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
    DisplayTimedText('Playlist: ' + _showText[showVal])

def ShowMixer(showVal):
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
    DisplayTimedText('Mixer: ' + _showText[showVal])

def ShowChannelRack(showVal):
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
    DisplayTimedText('Chan Rack: ' + _showText[showVal])

def ShowBrowser(showVal):
    global _ShowBrowser

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
    DisplayTimedText('Browser: ' + _showText[showVal])






