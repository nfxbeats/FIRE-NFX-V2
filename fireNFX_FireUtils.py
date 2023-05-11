# Fire device specific functions.

import device 
import midi
import utils 


# define and initialize A COLORMAP
class TnfxColorMap:
    def __init__(self, padIndex, color, dimFactor):
        self.PadIndex = padIndex
        self.PadColor = color
        self.DimFactor = dimFactor
        self.R = 0
        self.G = 0
        self.B = 0

_ColorMap = []

# init the color map
for p in range(64):
    _ColorMap.append(TnfxColorMap(p, 0, 0))

def getPadColor(padIdx):
    return _ColorMap[padIdx].PadColor


def SetPadColorBuffer(idx, col, dimFactor, flushBuffer = False, bSave = True):
    global _ColorMap
    if(col == -1):
        col = _ColorMap[idx].PadColor

    # r = (col & 0x7F0000) >> 16
    # g = (col & 0x007F00) >> 8
    # b = (col & 0x7F)

    newCol, r, g, b = AdjustedFirePadColor(FLColorToPadColor(col))

    # reduce brightness by half time dimFactor
    if(dimFactor > 0):
        for i in range(dimFactor):
            r = r >> 1
            g = g >> 1
            b = b >> 1

    if(bSave):
        _ColorMap[idx].PadColor = newCol 
        _ColorMap[idx].DimFactor = dimFactor
        _ColorMap[idx].R = r
        _ColorMap[idx].G = g
        _ColorMap[idx].B = b
    
    if(flushBuffer):
        FlushColorMap()

def FlushColorMap():
    MsgIDSetRGBPadLedState = 0x65
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

def SetPadColor(idx, col, dimFactor, bSaveColor = True, bUseBuffer = False, dimMult = 2.5):
    global _ColorMap
    if(bUseBuffer):
        SetPadColorBuffer(idx, col, dimFactor, False)
    else:
        SetPadColorDirect(idx, col, dimFactor, bSaveColor, dimMult)

def AdjustedFirePadColor(color):
    r, g, b = utils.ColorToRGB(color)
    reduceRed = 1
    reduceBlue = 1
    if(b > r) :
        reduceRed  = r / b
    if(g > b):
        reduceBlue = b / g
    if(g > r) and (reduceRed == 1):
        reduceRed  = r / g
    if reduceRed < 1:
        r = int(r * reduceRed)  # red adjust
    if(reduceBlue < 1):
        b = int(b * reduceBlue)  # blue adjust
    # reduce by half to support 0..127 range
    r = r//2
    g = g//2
    b = b//2
    return utils.RGBToColor(r, g, b), r, g, b    

def SetPadColorDirect(idx, col, dimFactor, bSaveColor = True, dimMult = 2.5):
    # if col is -1, it will remember the previously saved color for that idx.
    global _ColorMap

    if(idx < 0) or (idx > 63):
        return

    if(col == -1): # reads the stored color
        col = _ColorMap[idx].PadColor
        dimFactor = _ColorMap[idx].DimFactor

    col = FLColorToPadColor(col, 1)

    if(bSaveColor):
        _ColorMap[idx].PadColor = col 
        _ColorMap[idx].DimFactor = dimFactor
    
    newCol, r, g, b = AdjustedFirePadColor(col)

    # reduce brightness by half times dimFactor
    if(dimFactor > 0):
        for i in range(dimFactor):
            r = int(r / dimMult)
            g = int(g / dimMult)
            b = int(b / dimMult)

    SetPadRGB(idx, r, g, b)


def SetPadRGB(idx, r, g, b):  
    MsgIDSetRGBPadLedState = 0x65
    #print('Actual RGB To Pad', hex(r), hex(g), hex(b) )
    dataOut = bytearray(4)
    i = 0
    dataOut[i] = idx
    dataOut[i + 1] = r
    dataOut[i + 2] = g
    dataOut[i + 3] = b
    SendMessageToDevice(MsgIDSetRGBPadLedState, len(dataOut), dataOut)

def SendMessageToDevice(ID, l, data): # Fire specific
    ManufacturerIDConst = 0x47
    DeviceIDBroadCastConst = 0x7F
    ProductIDConst = 0x43

    if not device.isAssigned():
        return
    
    msg = bytearray(7 + l + 1)
    lsb = l & 0x7F
    msb = (l & (~ 0x7F)) >> 7

    msg[0] = midi.MIDI_BEGINSYSEX
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
    msg[len(msg) - 1] = midi.MIDI_ENDSYSEX
    device.midiOutSysex(bytes(msg))

import colorsys 
_FixChannelColors = True 

def FLColorToPadColor(FLColor, div = 2):
    
    padcolor = FLColor & 0xFFFFFF # take out any alpha channel
    # if(padcolor > 0x7F7F7F):
    #     div = 2

    r = (padcolor >> 16) & 0xFF
    g = (padcolor >> 8)  & 0xFF
    b = (padcolor) & 0xFF

    #print('------\nFLColor', hex(FLColor), '->', hex(utils.RGBToColor(r, g, b)), ' to padcolor', hex(padcolor), '\nrgb', hex(r),hex(g),hex(b) )

    # test this fix for channel colors
    if(_FixChannelColors):
        if (r == 20):
            r = 0
        if (g == 20):
            g = 0
        if (b == 20):
            b = 0
        # if (r == 0x80):
        #     r = 0x7f
        # if (g == 0x80):
        #     g = 0x7f
        # if (b == 0x80):
        #     b = 0x7f

        # r = r // div
        # g = g // div
        # b = b // div

        #print('adjusted color', hex(r),hex(g),hex(b) )

    # h,l,s = colorsys.rgb_to_hls(r, g, b)
    # print('hls', h,l,s)
    # l = 127.5
    # s = -1.007905138339921
    # r1, g1, b1 = colorsys.hls_to_rgb(h, l, s)
    # print('newrgb', r1, g1, b1 )

    return utils.RGBToColor(r, g, b)
