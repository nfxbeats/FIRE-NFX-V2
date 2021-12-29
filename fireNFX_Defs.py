# name = FireNFX Definitions
#
# most of this is copied from the Image-Line device_Fire code

MODE_STEP = 0
MODE_NOTE = 1
MODE_DRUM = 2
MODE_PERFORM = 3

PAD_MODE = MODE_STEP

UM_CHANNEL = 0
UM_MIXER = 1
UM_USER1 = 2
UM_USER2 = 3

USER_MODE = UM_CHANNEL 

# Message IDs (from PC to device)
MsgIDGetAllButtonStates = 0x40
MsgIDGetPowerOnButtonStates = 0x41
MsgIDSetRGBPadLedState = 0x65
MsgIDSetManufacturingData = 0x79
MsgIDDrawScreenText = 0x08
MsgIDDrawBarControl = 0x09
MsgIDFillOLEDDiplay = 0x0D
MsgIDSendPackedOLEDData = 0x0E
MsgIDSendUnpackedOLEDData = 0x0F


# Note/CC values for controls
IDKnob1 = 16 #0x10
IDKnob2 = 17 #0x11
IDKnob3 = 18 #0x12
IDKnob4 = 19 #0x13

IDJogWheel = 118 #0x76
IDSelect = IDJogWheel
IDJogWheelDown = 25 #0x19
IDSelectDown = IDJogWheelDown

IDKnobMode = 26 # 0x1B # shouldn't it be 0x1A ? (doc says 0x1B for outbound & 0x1A for inbound...)
IDKnobModeLEDArray = 27

IDPatternUp = 31 #0x1F
IDUp = IDPatternUp
IDPatternDown = 32 # 0x20
IDDown = IDPatternDown

IDBrowser = 33 #0x21

IDBankL = 34 #0x22
IDBankR = 35 #0x23

IDLeft = IDBankL
IDRight = IDBankR 

IDMute1 = 36 #0x24
IDMute2 = 37 #0x25
IDMute3 = 38 #0x26
IDMute4 = 39 #0x27

IDTrackSel1 = 40 #0x28
IDTrackSel2 = 41  #0x29
IDTrackSel3 =  42 #0x2A
IDTrackSel4 = 43  #0x2B

IDStepSeq = 44 #0x2C
IDAccent = 44
IDNote = 45 #0x2D
IDSnap = 45
IDDrum = 46 #0x2E
IDTap = 46
IDPerform = 47 #0x2F
IDOverview = 47

IDShift = 48 # 0x30
IDAlt = 49 #0x31

IDPatternSong = 50 #0x32
IDMetronome = 50 #
IDPlay = 51 #0x33
IDWait = 51 
IDStop = 52 #0x34
IDCount = 52
IDRec = 53 #0x35
IDLoop = 53 

# Pads
IDPadFirst = 54
IDPadLast = 117

TransportCtrls = [IDPatternSong, IDPlay, IDStop, IDRec]
ShiftAltCtrls = [IDShift, IDAlt]
PadModeCtrls = [IDStepSeq, IDNote, IDDrum, IDPerform]
NavCtrls = [IDUp, IDDown, IDLeft, IDRight]
KnobCtrls = [IDKnob1, IDKnob2, IDKnob3, IDKnob4]
SelectCtrls = [IDSelect, IDSelectDown]
PadCtrls = list()
for ctrlID in range(IDPadFirst, IDPadLast+1):
    PadCtrls.append(ctrlID)

# the operating knobs mode NOT Pad mode
KnobModeNames = ["Channel", "Mixer", "User1", "User2"]
KnobModeCtrlID = IDKnobMode
IDKnobModeLEDVals = [1,2,4,8]

PageCtrls = [IDMute1, IDMute2, IDMute3, IDMute4] #using these since I dont use the step mode

BeatIndicators = [IDTrackSel1, IDTrackSel2, IDTrackSel3, IDTrackSel4]



IdxStepSeq = 14
IdxNote = 15
IdxDrum = 16
IdxPerform = 17
IdxShift = 18
IdxAlt = 19
IdxPatternSong = 20
IdxPlay = 21
IdxStop = 22
IdxRec = 23
IdxButtonLast = 23

# Colors
DualColorOff = 0x00
DualColorHalfBright1 = 0x01
DualColorHalfBright2 = 0x02
DualColorFull1 = 0x03
DualColorFull2 = 0x04

SingleColorOff = 0x00
SingleColorHalfBright = 0x01
SingleColorFull = 0x02

IDColPattMode = DualColorHalfBright2
IDColSongMode = DualColorHalfBright1 

IDColPlayOff = DualColorOff
IDColPlayOn = DualColorHalfBright1
IDColPlayOnBar = DualColorFull2
IDColPlayOnBeat = DualColorFull1

IDColStopOff = DualColorOff
IDColStopOn = DualColorHalfBright2

IDColRecOff =  DualColorOff
IDColRecOn = DualColorFull1

IDColMetronome = DualColorFull2
IDColWait = DualColorFull2
IDColCount = DualColorFull2
IDColLoop = DualColorFull2

