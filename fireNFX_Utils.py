import device
import utils
from midi import *
from fireNFX_Defs import *

def SetPadColor(idx, col, dimFactor):
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

def PadColorFromFLColor(FLColor):
    r = ((FLColor >> 16) & 0xFF) // 2
    b = (FLColor & 0xFF) // 2
    g = ((FLColor >> 8) & 0xFF) // 2
    return utils.RGBToColor(r, g, b)

    

