# name=NFX Test

import device
from fireNFX_Classes import TnfxPadMap
import midi
import channels
import patterns
import utils
import time
import ui 
import transport 
import mixer 
import general


from fireNFX_Defs import * 
from fireNFX_PadDefs import *
from fireNFX_Utils import * 
from fireNFX_Display import *

_ShiftHeld = False
_AltHeld = False
_PatternCount = 0
_LastPattern = -1
_CurrentMode = 0
_CurrentPage = 0 
_Beat = 1
_PadMap = list()

def NextKnobMode():
    global _CurrentMode
    print('next knob mode. was', _CurrentMode)

    _CurrentMode += 1
    
    if(_CurrentMode > 3):
        _CurrentMode = 0    

    RefreshKnobMode()

def SetPage(page):
    global _CurrentPage
    _CurrentPage = page 
    RefreshPage()
    
    if(_CurrentMode == MODE_STEP):
        RefreshPadMap()


def RefreshPage():
    for i in range(0, len(PageCtrls)):
        if(i == _CurrentPage):
            SendCC(PageCtrls[i], SingleColorFull)
        else:
            SendCC(PageCtrls[i], SingleColorOff)


def RefreshKnobMode():
    LEDVal = IDKnobModeLEDVals[_CurrentMode] | 16
    print('refreshmode. knob mode is', _CurrentMode, 'led bit', IDKnobModeLEDVals[_CurrentMode], 'val', LEDVal)
    SendCC(IDKnobModeLEDArray, LEDVal)


def OnInit():
    print('OnInit')

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
        
    
    RefreshPadMode()
    RefreshTransport()
    RefreshShiftAlt()

    InitDisplay()
    DisplayText(Font6x16 , JustifyLeft, 0, "HELLO", True)
    

def ResetBeatIndicators():
    for i in range(0, len(BeatIndicators) ):
        SendCC(BeatIndicators[i], SingleColorOff)

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
#    print('refresh', flags)
    HW_Dirty_Patterns = 1024
    if(HW_Dirty_Patterns & flags):
        HandlePatternChanges()


def OnProjectLoad(status):
    print('OnProjectLoad', status)

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
        print('Pad Detected', padNum)

        # if STEP mode, treat as controls and not notes...
        if(PAD_MODE == MODE_STEP) and (pMap.FLPattern > 0):
            if(event.data2 > 0): # On Press only
                patterns.jumpToPattern(pMap.FLPattern)
                event.handled = True



        return 

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
        elif( ctrlID in PageCtrls):
            event.handled = HandlePage(event, ctrlID)  
        elif( ctrlID == KnobModeCtrlID):
            event.handled = HandleKnobMode()
        elif( ctrlID in KnobCtrls):
            event.handled = HandleKnob(event, ctrlID)

    else: # Released
        event.handled = True 


def HandlePatternChanges():
    global _PatternCount
    global _LastPattern
    
    currPattern = patterns.patternNumber()
    print('Refresh Patterns', patterns.patternCount(), currPattern)

    if(_PatternCount != patterns.patternCount()):
        print('pattern added/removed')
        _PatternCount = patterns.patternCount()
        RefreshPadMap()
    else:
        print('selected pattern changed', currPattern)
        if _LastPattern != currPattern:
            UpdatePatternPads()
    
    _LastPattern = currPattern

    if(patterns.patternCount() == 0) and (currPattern == 1): # empty project, set to 1
        _PatternCount = 1

def UpdatePatternPads():
    patternsPerPage = len(pdPatterns) 
    for i in range(0, patternsPerPage):
        padIdx = pdPatterns[i]
        pMap = _PadMap[padIdx] # 0-based
        if(patterns.patternNumber() == pMap.FLPattern): #current pattern
            SetPadColor(pMap.PadIndex, pMap.Color, pdDefaultBright)
        else:
            SetPadColor(pMap.PadIndex, pMap.Color, pdDefaultDim)

def InitPadMap():
    global _PadMap
    _PadMap.clear()
    for padIdx in range(0, 64):
        _PadMap.append(TnfxPadMap(padIdx, -1, 0x000000, ""))
    RefreshPads()

def RefreshPadMap():
    global _PadMap
    if(PAD_MODE == MODE_STEP): # Pattern mode, set the pattern buttons
        InitPadMap()
        pageLen = len(pdPatterns)
        pageOffs = _CurrentPage * pageLen 
        print('RefreshPadMap', _CurrentPage, pageLen, pageOffs, _PatternCount)
        for patt in range(0, pageLen): # _PatternCount ):
            pattNum = patt + pageOffs
            if(pattNum <= _PatternCount):
                FLPattNum = pattNum+1
                print('PattNum', pattNum, _PatternCount)
                padIdx = pdPatterns[patt]
                padColor = PadColorFromFLColor(patterns.getPatternColor(FLPattNum)) # FL is 1-based
                pMap = TnfxPadMap(padIdx, FLPattNum, padColor, "")
                _PadMap[padIdx] = pMap
                # add the corresponding mute btn
                padIdx = pdMutes[patt]
        UpdatePatternPads() 

def RefreshPads():
    for pad in range(0,64):
        SetPadColor(pad, _PadMap[pad].Color, pdDefaultDim)    


def HandleKnobMode():
    print('handle mode')
    NextKnobMode()
    return True

def HandleKnob(event, ctrlID):
    event.inEv = event.data2
    if event.inEv >= 0x40:
        event.outEv = event.inEv - 0x80
    else:
        event.outEv = event.inEv
    event.isIncrement = 1

    #print('handle knob', event.data1, event.data2, ctrlID, channels.channelNumber())
    if USER_MODE == UM_CHANNEL :
        chanNum = channels.channelNumber()
        recEventID = channels.getRecEventId(chanNum)
        value = event.outEv
        if chanNum > -1: # -1 is none selected
            if ctrlID == IDKnob1:
                return HandleKnobReal(recEventID + REC_Chan_Vol,  value, 'Channel Volume', False)
            elif ctrlID == IDKnob2:
                return HandleKnobReal(recEventID + REC_Chan_Pan, value, 'Channel Pan', True)
            elif ctrlID == IDKnob3:
                return HandleKnobReal(recEventID + REC_Chan_FCut, value, 'Channel Filter', False)
            elif ctrlID == IDKnob4:
                return HandleKnobReal(recEventID + REC_Chan_FRes, value, 'Channel Resonance', False)
        
    

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
    print('handlepage', _CurrentPage)
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

def RefreshShiftAlt():
    if(_AltHeld):
        SendCC(IDAlt, SingleColorHalfBright)
    else:
        SendCC(IDAlt, SingleColorOff)

    if(_ShiftHeld):
        RefreshShifted()
    else:  
        SendCC(IDShift, DualColorOff)
        RefreshPadMode()
        RefreshTransport()

def HandlePadMode(event):
    print('padmode')
    global PAD_MODE
    oldPadMode = PAD_MODE
    ctrlID = event.data1 
    if(ctrlID == IDStepSeq):
        PAD_MODE = MODE_STEP
    elif(ctrlID == IDNote):
        PAD_MODE = MODE_NOTE
    elif(ctrlID == IDDrum):
        PAD_MODE = MODE_DRUM
    elif(ctrlID == IDPerform):
        PAD_MODE = MODE_PERFORM
    
    if(oldPadMode != PAD_MODE):
        InitPadMap()
    
    RefreshPadMode()

    return True

def RefreshPadMode():
    SendCC(IDStepSeq, DualColorOff)
    SendCC(IDNote, DualColorOff)
    SendCC(IDDrum, DualColorOff)
    SendCC(IDPerform, DualColorOff)
    if(PAD_MODE == MODE_STEP):
        SendCC(IDStepSeq, DualColorFull2)
    elif(PAD_MODE == MODE_NOTE):
        SendCC(IDNote, DualColorFull2)
    elif(PAD_MODE == MODE_DRUM):
        SendCC(IDDrum, DualColorFull2)
    elif(PAD_MODE == MODE_PERFORM):
        SendCC(IDPerform, DualColorFull2)



def HandleTransport(event):
    print('.....Transport OnPress', event.data1)
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


def OnNoteOn(event):
    print ('Note On', utils.GetNoteName(event.data1),event.data1,event.data2)
           
def OnNoteOff(event):
    print ('Note Off', utils.GetNoteName(event.data1),event.data1,event.data2)


