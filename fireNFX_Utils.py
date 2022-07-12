import math
import time 
import device
from fireNFX_Classes import TnfxColorMap, TnfxParameter, TnfxPlugin
import utils
import plugins
import mixer
import playlist
import ui
import general 
from midi import *
from fireNFX_Colors import *
from fireNFX_Defs import *



# enum code from https://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
def enum(**enums):
    return type('Enum', (), enums)
 

# snap defs are in MIDI.py aka Snap_Cell, Snap_line, etc
SnapModes = enum(   Line = 0,
                    Cell = 1,
                    NoSnap = 3, #  "None" is a Python built-in constant so I use "NoSnap" instead
                    Step_6th = 4,
                    Step_4th = 5,
                    Step_3rd = 6,
                    Step_Half = 7,
                    Step = 8,
                    Beat_6th = 9,
                    Beat_4th = 10,
                    Beat_3rd = 11,
                    Beat_Half = 12,
                    Beat = 13,
                    Bar = 14
                )
class SnapModesOld:  # no enums :(
    Line = 0
    Cell = 1
    NoSnap = 3
    Step_6th = 4
    Step_4th = 5
    Step_3rd = 6
    Step_Half = 7
    Step = 8
    Beat_6th = 9
    Beat_4th = 10
    Beat_3rd = 11
    Beat_Half = 12
    Beat = 13
    Bar = 14

SnapModesText = ["Line", "Cell", "?", "None",
              "1/6 Step", "1/4 Step", "1/3 Step", "1/2 Step", "Step",
              "1/6 Beat", "1/4 Beat", "1/3 Beat", "1/2 Beat", "Beat",
              "Bar"]

#define your list of snap modes to cycle through.
SnapModesList = [0,1,2,3,4,5,6,7,8,9,10,11,12,13,14]
InitialSnapIndex = 0 #initial value - index of above - 0-based
RepeatSnapIdx = 7 # for repeat mode


BeatLengthNames = ['Bar/Whole', 'Half', 'Quarter', 'Dotted 8th', '8th', '16th', '32nd', '64th']
BeatLengthDivs  = [0, .5, 1, 1.33333, 2, 4, 8, 16]
BeatLengthSnap  = [Snap_Beat, Snap_Beat, Snap_Beat, Snap_ThirdBeat, Snap_FourthBeat, Snap_Step, Snap_HalfStep, Snap_FourthStep]
BeatLengthsDefaultOffs = 6 #  offset of above 

# init the color map
_ColorMap = list()
for p in range(64):
    colorMap = TnfxColorMap(p, 0, 0)
    _ColorMap.append(colorMap)

def getPadColor(padIdx):
    return _ColorMap[padIdx].PadColor

def TestColorMap():
    global _ColorMap

    for r in range(0, 127, 16):
        for g in range(0, 127, 16):
            for b in range(0, 127, 16):
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

def getColorMap():
    return _ColorMap

def SetPadColor(idx, col, dimFactor, bSaveColor = True):
    global _ColorMap
    SetPadColorDirect(idx, col, dimFactor, bSaveColor)
    #SetPadColorBuffer(idx, col, dimFactor, False)

def SetPadColorDirect(idx, col, dimFactor, bSaveColor = True):
    global _ColorMap
    global _PadMap 

    if(col == -1):
        col = _ColorMap[idx].PadColor
        dimFactor = _ColorMap[idx].DimFactor

    #print('SetLEDCol', idx, col)
    r = (col & 0x7F0000) >> 16
    g = (col & 0x007F00) >> 8
    b = (col & 0x7F)

    # reduce brightness by half times dimFactor
    if(dimFactor > 0):
        for i in range(dimFactor):
            r = r >> 1
            g = g >> 1
            b = b >> 1

    SetPadRGB(idx, r, g, b)

    _PadMap[idx].Color = col 
    
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
    andVal = 0xC7 # was 0xFF
    r = ((FLColor >> 16) & andVal) // 2
    g = ((FLColor >> 8) & andVal) // 2
    b = (FLColor & andVal) // 2
    return utils.RGBToColor(r, g, b)

def getPluginParam(chanIdx, paramIdx):
    m = chanIdx 
    caption = plugins.getParamName(paramIdx, chanIdx, -1) # -1 denotes not mixer
    value = plugins.getParamValue(paramIdx, chanIdx, -1) 
    valuestr = plugins.getParamValueString(paramIdx, chanIdx, -1)
    if(value == .5):
        bipolar = True 
    else:
        bipolar = False

    name = plugins.getPluginName(chanIdx)
    varName =  "pl" + name 
    print("\t" + varName + ".Parameters.append( TnfxParameter(" + str(paramIdx) +", '" + caption +"', 0, '" + valuestr + "', " + str(bipolar) + ") )")



    #print('TnfxParameter')
    #print('     Param', paramIdx, caption )
    #print('     Value', paramIdx, value )
    #print('    ValStr', paramIdx, valuestr )
    #print('    Color0', paramIdx, plugins.getColor(chanIdx, -1, 0, paramIdx) )
    #print('    Color1', paramIdx, plugins.getColor(chanIdx, -1, 1, paramIdx) )
    #print('----------------------')
    return TnfxParameter(paramIdx, caption, value, valuestr, bipolar)


            
        
def getBeatLenInMS(div):
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
    #print('tempo', tempo, 'div', div, 'beatlen', beatlen, 'output', timeval, 'Barlen', barlen) 
    return int(timeval)

def getPluginInfo(chanIdx):
    res = TnfxPlugin(plugins.getPluginName(chanIdx, -1, 0))
    res.Parameters.clear()

    print('   PluginName: ', res.Name)
    pCnt = plugins.getParamCount(chanIdx, -1)
    print('   ParamCount: ', pCnt)
    name = plugins.getPluginName(chanIdx)
    varName =  "pl" + name 
    print('-----------------------------------------------------------------')
    print(varName + " = TnfxPlugin('" + name + "')")
    for paramIdx in range(0, pCnt):
        #if(plugins.getParamName(paramIdx, chanIdx, -1) != ''):
        if(True):
            param = getPluginParam(chanIdx, paramIdx)
            res.Parameters.append(param)
    print('-----------------------------------------------------------------')            
    return res 

def ShowPluginInfo(chanIdx):
    print('   PluginName: ', plugins.getPluginName(chanIdx, -1, 0))
    pCnt = plugins.getParamCount(chanIdx, -1)
    print('   ParamCount: ', pCnt)
    for param in range(0, pCnt):
        if(plugins.getParamName(param, chanIdx, -1) != ''):
            getPluginParam(chanIdx, param)



def ColorToRGB(Color):
    return (Color >> 16) & 0xFF, (Color >> 8) & 0xFF, Color & 0xFF

def RGBToColor(R,G,B):
    return (R << 16) | (G << 8) | B

def GradTest():
    #def Gradient(color1, color2, stepsize, padOffs=0):
    stepsize = 5 # 255//5
    Gradient(cBlue, cOff, stepsize, 0)
    Gradient(cPurple, cOff, stepsize, 16)
    Gradient(cMagenta, cOff, stepsize, 32)
    Gradient(cRed, cOff, stepsize, 48)
    Gradient(cOrange, cOff, stepsize, 4)
    Gradient(cYellow, cOff, stepsize, 20)
    Gradient(cGreen, cOff, stepsize, 36)
    Gradient(cCyan, cOff, stepsize, 52)


def ColorTest(arg1):
    Shades(cBlue,0)
    Shades(cPurple, 16)
    Shades(cMagenta, 32)
    Shades(cRed, 48)
    Shades(cOrange, 4)
    Shades(cYellow, 20)
    Shades(cGreen, 36)
    Shades(cCyan, 52)


shDim = 0
shDark = 1
shNorm = 2
shLight = 3


def getShade(baseColor, shadeOffs):
    multLighten = 1.33
    multDarken = .23
    if(shadeOffs == shDim):
        return Shade(baseColor, multDarken, 2)    # dim
    elif(shadeOffs == shDark):
        return Shade(baseColor, multDarken, 1)    # dark
    elif(shadeOffs == shNorm):
        return baseColor                           # norm
    elif(shadeOffs == shLight):
        return Shade(baseColor, multLighten, 1)   # light
    else: 
        return baseColor


def Shades(color, padOffs=0):
    SetPadColor(0+padOffs, getShade(color, shDim), 0)
    SetPadColor(1+padOffs, getShade(color, shDark), 0)
    SetPadColor(2+padOffs, getShade(color, shNorm), 0)
    SetPadColor(3+padOffs, getShade(color, shLight), 0)

def Gradient(color1, color2, stepsize, padOffs=0):
    for pad in range(4):
        step = (255//stepsize) * pad
        col = FadeColor(color1, color2, step)
        SetPadColor(pad+padOffs, col, 0)



def Shade(color, mul = 1.1, offs = 0):
    color1 = color
    for i in range(3):
        if(i > 0):
            color = ColorMult(color, mul)
            color1 = ColorMult2(color, mul)
        if(i == offs):
            return color1

def AnimOff(padIdx, color, steps = 16, wait = 0.1):
    OrigColor = _ColorMap[padIdx].PadColor 
    Color1 = cWhite # getShade(color, shLight)
    Color2 = cOff # getShade(color, shDim)
    for step in range(steps):
        stepSize = 255//steps
        col = FadeColor(OrigColor, Color2, step * stepSize)
        SetPadColor(padIdx, col, 0)    
        time.sleep(wait)

def AnimOn(padIdx, color, steps = 16, wait = 0.1):
    OrigColor = _ColorMap[padIdx].PadColor 
    Color1 = cWhite # getShade(color, shLight)
    Color2 = cOff # getShade(color, shDim)
    for step in range(steps):
        stepSize = 255//steps
        col = FadeColor(Color2, OrigColor, step * stepSize)
        SetPadColor(padIdx, col, 0)    
        time.sleep(wait)


def CycleColors(len = 64, steps = 8, freq = 0.5):
    center = 128
    amplitude = 127
    for inc in range(len):
        # value = Math.sin(frequency*increment)*amplitude + center;
        rPhase =  0 
        gPhase =  2 * math.pi/2
        bPhase =  4 * math.pi/steps
        rFreq = 2 * math.pi/steps
        gFreq = 2 * math.pi/steps
        bFreq = 2 * math.pi/steps
        red = int( math.sin(rFreq * inc + rPhase) * amplitude + center )
        green = int( math.sin(gFreq * inc + gPhase) * amplitude + center )
        blue = int( math.sin(bFreq * inc + bPhase) * amplitude + center )
        col = RGBToColor(red, green, blue)
        print(inc % 64, "color =",hex(col), '#', col,  'rgb', red, green, blue)
        #if(inc < 64):
        SetPadColor(inc % 64, col, 0)
        #time.sleep(0.001)

def ColorMult(color, mul):
    r, g, b = ColorToRGB(color)
    r *= mul
    g *= mul
    b *= mul
    r2, g2, b2 = redistribute_rgb(r, g, b)
    return RGBToColor(r2, g2, b2)

def ColorMult2(color, mul):
    r, g, b = ColorToRGB(color)
    r *= mul
    g *= mul
    b *= mul
    r2, g2, b2 = clamp_rgb(r, g, b)
    return RGBToColor(r2, g2, b2)


def clamp_rgb(r, g, b):
    # from https://stackoverflow.com/questions/141855/programmatically-lighten-a-color
    return min(127, int(r)), min(127, int(g)), min(127, int(b))

def redistribute_rgb(r, g, b):
    # from https://stackoverflow.com/questions/141855/programmatically-lighten-a-color
    threshold = 255.999
    m = max(r, g, b)
    if m <= threshold:
        return int(r), int(g), int(b)
    total = r + g + b
    if total >= 3 * threshold:
        return int(threshold), int(threshold), int(threshold)
    x = (3 * threshold - total) / (3 * m - total)
    gray = threshold - x * m
    return int(gray + x * r), int(gray + x * g), int(gray + x * b)

def getBarFromAbsTicks(absticks):
    return ( absticks // general.getRecPPB() ) + 1

def getAbsTicksFromBar(bar):
    # thx to HDSQ from https://forum.image-line.com/viewtopic.php?p=1740588#p1740588
    return (bar - 1) * general.getRecPPB() 

#from the original AKAI script
def FadeColor(StartColor, EndColor, Value):
  rStart, gStart, bStart = ColorToRGB(StartColor)
  rEnd, gEnd, bEnd = ColorToRGB(EndColor)
  ratio = Value / 255
  rEnd = round(rStart * (1 - ratio) + (rEnd * ratio))
  gEnd = round(gStart * (1 - ratio) + (gEnd * ratio))
  bEnd = round(bStart * (1 - ratio) + (bEnd * ratio))
  return RGBToColor(rEnd, gEnd, bEnd)
