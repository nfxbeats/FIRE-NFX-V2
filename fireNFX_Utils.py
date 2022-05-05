import device
from fireNFX_Classes import TnfxColorMap, TnfxParameter
import utils
import plugins
import mixer
import playlist
import ui
from midi import *
from fireNFX_Defs import *

# init the color map
_ColorMap = list()
for p in range(64):
    colorMap = TnfxColorMap(p, 0, 0)
    _ColorMap.append(colorMap)

def getPadColor(padIdx):
    return _ColorMap[padIdx].PadColor

def TestColorMap():
    global _ColorMap

    for r in range(127):
        for g in range(127):
            for b in range(127):
                for cMap in _ColorMap:
                    cMap.R = r
                    cMap.G = g
                    cMap.B = b 
                FlushColorMap()  
                
def SetPadColorBuffer(idx, col, dimFactor, flushBuffer = False):
    global _ColorMap
    
    if(col == -1):
        col = _ColorMap[idx].PadColor

    #print('SetLEDCol', idx, col)
    r = (col & 0x7F0000) >> 16
    g = (col & 0x007F00) >> 8
    b = (col & 0x7F)

    # reduce brightness by half time dimFactor
    if(dimFactor > 0):
        for i in range(dimFactor):
            r = r >> 1
            g = g >> 1
            b = b >> 1

    _ColorMap[idx].PadColor = col 
    _ColorMap[idx].DimFactor = dimFactor
    _ColorMap[idx].R = r
    _ColorMap[idx].G = g
    _ColorMap[idx].B = b
    
    if(flushBuffer):
        FlushColorMap()

def FlushColorMap():
    dataOut = bytearray(4 * 64)
    bufOffs = 0
    for cMap in _ColorMap:
        dataOut[bufOffs] = cMap.PadIndex
        dataOut[bufOffs + 1] = cMap.R
        dataOut[bufOffs + 2] = cMap.G
        dataOut[bufOffs + 3] = cMap.B
        bufOffs += 4
    SendMessageToDevice(MsgIDSetRGBPadLedState, len(dataOut), dataOut)


def SetPadColor(idx, col, dimFactor, bSaveColor = True):
    global _ColorMap
    SetPadColorDirect(idx, col, dimFactor, bSaveColor)
    #SetPadColorBuffer(idx, col, dimFactor, False)

def SetPadColorDirect(idx, col, dimFactor, bSaveColor = True):
    global _ColorMap

    if(col == -1):
        col = _ColorMap[idx].PadColor
        dimFactor = _ColorMap[idx].DimFactor

    #print('SetLEDCol', idx, col)
    r = (col & 0x7F0000) >> 16
    g = (col & 0x007F00) >> 8
    b = (col & 0x7F)

    # reduce brightness by half time dimFactor
    if(dimFactor > 0):
        for i in range(dimFactor):
            r = r >> 1
            g = g >> 1
            b = b >> 1

    SetPadRGB(idx, r, g, b)

    if(bSaveColor):
        _ColorMap[idx].PadColor = col 
        _ColorMap[idx].DimFactor = dimFactor

def SetPadRGB(idx, r, g, b):  
    #print('SetLED', idx, r, g, b)
    dataOut = bytearray(4)
    i = 0
    dataOut[i] = idx
    dataOut[i + 1] = r
    dataOut[i + 2] = g
    dataOut[i + 3] = b

    SendMessageToDevice(MsgIDSetRGBPadLedState, len(dataOut), dataOut)



def SendCC(ID, Val):

    if (not device.isAssigned()):
        return
    device.midiOutNewMsg(MIDI_CONTROLCHANGE + (ID << 8) + (Val << 16), ID)


def SendMessageToDevice(ID, l, data):

    ManufacturerIDConst = 0x47
    DeviceIDBroadCastConst = 0x7F
    ProductIDConst = 0x43

    if not device.isAssigned():
        return
    
    msg = bytearray(7 + l + 1)
    lsb = l & 0x7F
    msb = (l & (~ 0x7F)) >> 7

    msg[0] = MIDI_BEGINSYSEX
    msg[1] = ManufacturerIDConst
    msg[2] = DeviceIDBroadCastConst
    msg[3] = ProductIDConst
    msg[4] = ID
    msg[5] = msb
    msg[6] = lsb
    if (l > 63):
        for n in range(0, len(data)):
            msg[7 + n] = data[n]
    else:
        for n in range(0, l):
            msg[7 + n] = data[n]
    msg[len(msg) - 1] = MIDI_ENDSYSEX
    device.midiOutSysex(bytes(msg))

def FLColorToPadColor(FLColor):
    r = ((FLColor >> 16) & 0xFF) // 2
    b = (FLColor & 0xFF) // 2
    g = ((FLColor >> 8) & 0xFF) // 2
    return utils.RGBToColor(r, g, b)

def getPluginParam(chanIdx, paramIdx):
    m = chanIdx 
    caption = plugins.getParamName(paramIdx, chanIdx, -1) # -1 denotes not mixer
    value = plugins.getParamValue(paramIdx, chanIdx, -1) 
    valuestr = plugins.getParamValueString(paramIdx, chanIdx, -1)
    bipolar = False
    print('     Param', paramIdx, caption )
    print('     Value', paramIdx, value )
    print('    ValStr', paramIdx, valuestr )
    print('    Color0', paramIdx, plugins.getColor(chanIdx, -1, 0, paramIdx) )
    print('    Color1', paramIdx, plugins.getColor(chanIdx, -1, 1, paramIdx) )
    print('----------------------')
    return TnfxParameter(caption, paramIdx, value, valuestr, bipolar)

def setSnapMode(newmode):
    mode = ui.getSnapMode()
    while(mode < newmode):
        ui.snapMode(1)  # inc by 1
        mode = ui.getSnapMode()
    while(mode > newmode):
        ui.snapMode(-1)  # inc by 1
        mode = ui.getSnapMode()
        
# snap defs are in MIDI.py aka Snap_Cell, Snap_line, etc
SnapModes = ["Default", "Line", "?", "Cell", "None",
              "1/6 Step", "1/4 Step", "1/3 Step", "1/2 Step", "Step",
              "1/6 Beat", "1/4 Beat", "1/3 Beat", "1/2 Beat", "Beat",
              "Bar"]

#define your list of snap modes to cycle through.
SnapModesList = [Snap_Beat, Snap_HalfBeat, Snap_ThirdBeat, Snap_Step, Snap_HalfStep, Snap_ThirdStep, Snap_None]
InitialSnapIndex = 1 #initial value - index of above - 0-based
RepeatSnapIdx = 4 # for repeat mode


BeatLengthNames = ['Bar/Whole', 'Half', 'Quarter', 'Dotted 8th', '8th', '16th', '32nd', '64th']
BeatLengthDivs  = [0, .5, 1, 1.33333, 2, 4, 8, 16]
BeatLengthsDefaultOffs = 6 #  offset of above 
def GetBeatLenInMS(div):
    #   0 = 1 bar whole not
    #   0.5 = half
    #   1 = Quarter
    #   1.33333 = dotted 8 
    #   2 = Eighth
    #   4 = sixteenth
    #   8 = 32nd
    #  16 = 64th

    tempo = mixer.getCurrentTempo(0)
    beatlen = (60000/tempo)
    if(div > 0 ):
        timeval = (beatlen/div) * 1000 #
    else: #when div = 0...
        timeval = beatlen * 4000 # one bar aka whole note.
    barlen = playlist.getVisTimeTick()
    print('tempo', tempo, 'div', div, 'beatlen', beatlen, 'output', timeval, 'Barlen', barlen) 
    return int(timeval)



def ShowPluginInfo(chanIdx):
    print('   PluginName: ', plugins.getPluginName(chanIdx, -1, 0))
    pCnt = plugins.getParamCount(chanIdx, -1)
    print('   ParamCount: ', pCnt)
    for param in range(0, pCnt):
        if(plugins.getParamName(param, chanIdx, -1) != ''):
            getPluginParam(chanIdx, param)

