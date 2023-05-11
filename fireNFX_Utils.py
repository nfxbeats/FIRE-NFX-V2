import sys
import math
import transport
import time 
import device
from fireNFX_Classes import TnfxParameter, TnfxChannelPlugin, cpChannelPlugin, cpMixerPlugin #, _rd3d2PotParams 
import utils
import plugins
import mixer
import playlist
import ui
import channels 
import general 
from midi import *
from fireNFX_Colors import *
from fireNFX_Defs import *
from fireNFX_DefaultSettings import *
from fireNFX_FireUtils import *
import fireNFX_Anim as anim

# # enum code from https://stackoverflow.com/questions/36932/how-can-i-represent-an-enum-in-python
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
BeatLengthDivs  = [0, .5, 1, 1.5, 2, 4, 8, 16] #  or [0, .5, 1, 1.33333, 2, 4, 8, 16] ? 
BeatLengthSnap  = [Snap_Beat, Snap_Beat, Snap_Beat, Snap_ThirdBeat, Snap_FourthBeat, Snap_Step, Snap_HalfStep, Snap_FourthStep]
BeatLengthsDefaultOffs = 6 #  offset of above 

def SendCC(ID, Val):
    if (not device.isAssigned()):
        return
    device.midiOutNewMsg(MIDI_CONTROLCHANGE + (ID << 8) + (Val << 16), ID)

def getParamCaption(chanIdx, paramIdx, mixSlotIdx = -1):
    return plugins.getParamName(paramIdx, chanIdx, mixSlotIdx) # -1 denotes not mixer

def getPluginParam(chanIdx, paramIdx, prn = False, mixSlotIdx = -1): # -1 denotes not mixer
    hasCaption = (len(plugins.getParamName(paramIdx, chanIdx, mixSlotIdx)) > 0)
    caption = plugins.getParamName(paramIdx, chanIdx, mixSlotIdx) 
    value = plugins.getParamValue(paramIdx, chanIdx, mixSlotIdx) 
    valuestr = plugins.getParamValueString(paramIdx, chanIdx, mixSlotIdx)
    bipolar = False
    name, uname, varName = getPluginNames(chanIdx, mixSlotIdx)
    spclCnt = plugins.getPadInfo(chanIdx, mixSlotIdx, PAD_Count, paramIdx)
    if(hasCaption): # if(caption != ''):
        if prn:
            print(varName + ".addParamToGroup('ALL', TnfxParameter(" + str(paramIdx) +", '" + caption +"', 0, '" + valuestr + "', " + str(bipolar) + ") )")
            # if( spclCnt > 0 ):
            #     semitone = plugins.getPadInfo(chanIdx, mixSlotIdx, PAD_Semitone, paramIdx)
            #     padcolor = plugins.getPadInfo(chanIdx, mixSlotIdx, PAD_Color, paramIdx)
            #     for spclIdx in range(plugins.getPadInfo(chanIdx, mixSlotIdx, 0, paramIdx)):
            #         print('#    Semitone: ', semitone )
            #         print('#     Color:', hex(padcolor), padcolor )
            # print('#    ValStr', paramIdx, valuestr )
            # print('#    Color0', paramIdx, plugins.getColor(chanIdx, -1, 0, paramIdx) )
            # print('#    Color1', paramIdx, plugins.getColor(chanIdx, -1, 1, paramIdx) )
            # print('----------------------')
    return TnfxParameter(paramIdx, caption, value, valuestr, bipolar)

def getBeatLenInMS(div):
    #   0 = 1 bar whole not
    #   0.5 = half
    #   1 = Quarter
    #   1.33333 = dotted 8?
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
    return int(timeval)

def RemoveBadChars(badChars, textStr):
    res = textStr
    for badChar in badChars:
        res = res.replace(badChar, '')
    return res

def getAlphaNum(textStr, allowSpaces = False):
    res = textStr
    for idx, char in enumerate(textStr):
        if (allowSpaces) and (char == ' '):
            pass
        elif(not char.isalnum()):
            res = res.replace(char, '')
    return res

def getPluginNames(chanIdx = -1, mixSlotIdx = -1):
    if(mixSlotIdx > -1):
        if (chanIdx == -1):
            chanIdx = mixer.trackNumber()
    else:        
        if chanIdx == -1:
            chanIdx = channels.selectedChannel()
    name =  plugins.getPluginName(chanIdx, mixSlotIdx, 0)
    uname = plugins.getPluginName(chanIdx, mixSlotIdx, 1)
    vname = getAlphaNum("plugin{}".format(name))
    return name, uname, vname

def getPluginInfo(chanIdx, prn = False, inclBlanks = False, mixSlotIdx = -1):
    if(mixSlotIdx > -1):
        if (chanIdx == -1):
            chanIdx = mixer.trackNumber()
    else:        
        if chanIdx == -1:
            chanIdx = channels.selectedChannel()

    name, uname, vname = getPluginNames(chanIdx, mixSlotIdx)
    res = TnfxChannelPlugin(name, uname)
    res.Type = cpChannelPlugin
    type = 'cpChannelPlugin'
    if(mixSlotIdx > -1):
        res.Type = cpMixerPlugin
        type = 'cpMixerPlugin'

    res.Parameters.clear()
    pCnt = plugins.getParamCount(chanIdx, mixSlotIdx)
    knobsSamples = []
    varName =  vname
    fileName = vname + '.py'
    if(prn):
        print('# -----[ COPY AFTER THIS LINE, BUT DO NOT INCLUDE ]--------------------------------------------------------')   
        print('# Save this file as: "{}{}"'.format(sys.path[1],fileName))
        print('# ')
        print('#   PluginName: ', res.Name)
        print('#   Created by: ', '<your name here>')
        print('# ')
        print('from fireNFX_Classes import TnfxParameter, TnfxChannelPlugin, cpChannelPlugin, cpMixerPlugin')
        print('from fireNFX_PluginDefs import USER_PLUGINS')
        print(varName + " = TnfxChannelPlugin('" + name + "', '', " + type + ")")
        print("if({}.Name not in USER_PLUGINS.keys()):".format(varName))
        print("    USER_PLUGINS[{}.Name] = {}".format(varName, varName))
        print("    print('{} parameter definitions loaded.')".format(res.Name))
        print(" ")

    for paramIdx in range(0, pCnt):
        param = getPluginParam(chanIdx, paramIdx, prn, mixSlotIdx)
        if(param.Caption != "") or (inclBlanks):
            if(param.Caption == ""):
                param.Caption == "{}.Offset".format(paramIdx)

            if('MIDI CC' in param.Caption):
                param.Caption = param.Caption.replace('MIDI CC', '').replace('#', '').lstrip()
                res.addParamToGroup("MIDI CCs", param)
            else:    
                res.addParamToGroup("ALL", param)

            if(False): #(res.Name in _rd3d2PotParams.keys()):
                res.addParamToGroup("rd32d3 Ext", param)
                knobsSamples.append(param)
            elif(len(knobsSamples) < 8):
                knobsSamples.append(param)

            res.Parameters.append(param)

    if(prn):
        print('# [PARAMETER OFFSETS] ')
        print('# Notice, the code lines above contains the text "TnfxParameter(" followed by a number')
        print('# That number represents the parameter offset for the parameter described on that line')
        print('# You can use the parameter offset number to program your own USER Knob mappings below')
        print("# ")
        sampleCount = len(knobsSamples)
        if(sampleCount > 0 ):
            paramlist = []
            for idx, sample in enumerate(knobsSamples):
                if idx < 8:
                    paramlist.append(sample.Offset)
                else:
                    break
            print('# [HOW TO SET CUSTOM KNOB MAPPINGS]')
            print('# The assignKnobs() function takes a list of up to 8 parameter offsets.')
            print('# The list must be in brackets like this [ 21, 12, 3, 7]. Max 8 offsets in list.')
            print('# it assigns them in order from :')
            print('#   USER1, KNOBS 1-4 as the first 4 params')
            print('#   USER2, KNOBS 1-4 as the second 4 params')
            print('')
            print('# [ENABLING THE CUSTOM MAPPING]')
            print("# Comment/Uncomment the next line to disable/enable the knob mappings. ")
            print("#{}.assignKnobs({}) ".format(varName, str(paramlist)))
            print(" ")
            print("# [LAST STEP. DO NOT FORGET. NEEDED TO INCLUDE YOUR MAPPINGS] ")
            print("# Add the following line (without the #) to the end of fireNFX_CustomPlugins.py")
            print("#from {} import {}".format(varName, varName) )
            print(' ')   
            print('# -----[ COPY UP TO THIS LINE, BUT DO NOT INCLUDE ]---------------')   
        return ""
    return res 

def ShowPluginInfo(chanIdx):
    getPluginInfo(chanIdx, True)

def getBarFromAbsTicks(absticks):
    return ( absticks // general.getRecPPB() ) + 1

def getAbsTicksFromBar(bar):
    # thx to HDSQ from https://forum.image-line.com/viewtopic.php?p=1740588#p1740588
    return (bar - 1) * general.getRecPPB() 

#from the original AKAI script
def FadeColor(StartColor, EndColor, ColorSteps):
  rStart, gStart, bStart = ColorToRGB(StartColor)
  rEnd, gEnd, bEnd = ColorToRGB(EndColor)
  ratio = ColorSteps / 255
  rEnd = round(rStart * (1 - ratio) + (rEnd * ratio))
  gEnd = round(gStart * (1 - ratio) + (gEnd * ratio))
  bEnd = round(bStart * (1 - ratio) + (bEnd * ratio))
  return RGBToColor(rEnd, gEnd, bEnd)

mvUp = 0
mvUpRight = 1
mvRight = 2
mvDownRight = 3
mvDown = 4
mvDownLeft = 5
mvLeft = 6
mvUpLeft = 7
mvStay= 9

def MovePad(PadToMoveIdx, direction, StartColor = cGreen, EndColor = cWhite, colorStep = 0):
    padRow = PadToMoveIdx // 16
    padCol = PadToMoveIdx % 16
    addVal = 0
    if(direction != mvStay):
        #directions are indicated in a clock wise manner starting with the top
        if(direction in [mvUpLeft, mvUp, mvUpRight]): # up
            if(padRow > 0):
                addVal += -16
        if(direction in [mvUpRight, mvRight, mvDownRight]):
            if(padCol < 16):
                addVal += +1
        if(direction in [mvDownLeft, mvDown, mvDownRight]): # down
            if(padRow < 3):
                addVal += 16 
        if(direction in [mvUpLeft, mvLeft, mvDownLeft]):
            if(padCol > 0):
                addVal += -1
    newPadIdx = PadToMoveIdx + addVal
    stepSize = 255//4
    newColor = FadeColor(StartColor, EndColor, colorStep * stepSize)
    oldColor = newColor # FadeColor(StartColor, EndColor, (colorStep + 1) * stepSize)
    SetPadColor(newPadIdx, newColor, dimBright, False)
    SetPadColor(PadToMoveIdx, oldColor, dimDefault, False)
    return newPadIdx

_baseDelay = getBeatLenInMS(8)/1000
_testpath = [mvStay, mvLeft, mvUp, mvRight, mvRight, mvDown, mvDown, mvLeft, mvLeft, mvLeft, mvUp, mvUp, mvUp, mvRight, mvRight, mvRight, mvUp]
# ^ 34 start pad

#_testpath = [mvStay, mvDown, mvDown, mvDown, mvRight, mvUp, mvUp, mvUp, mvRight,
#    mvDown, mvDown, mvDown, mvRight, mvUp, mvUp, mvUp]

def BankMoves(startpad = 34, path = _testpath, color = cGreen, finishAtStart = True):
    delay = _baseDelay 
    pad = startpad
    pad2 = startpad + 4
    pad3 = startpad + 8
    pad4 = startpad + 12
    for step in _testpath:
        pad = MovePad(pad, step, color, cBlack, 0)
        pad2 = MovePad(pad2, step, color, cBlack, 0)
        pad3 = MovePad(pad3, step, color, cBlack, 0)
        pad4 = MovePad(pad4, step, color, cBlack, 0)
        time.sleep(delay) #getBeatLenInMS(4)/1000
    if(finishAtStart):
        pad = MovePad(startpad, step, color, cBlack, 0)
        pad2 = MovePad(startpad+4, step, color, cBlack, 0)
        pad3 = MovePad(startpad+8, step, color, cBlack, 0)
        pad4 = MovePad(startpad+12, step, color, cBlack, 0)

def LoopBankTest():
    BankMoves()
    BankMoves()
    BankMoves()
    BankMoves()

import _thread 

def TestThreadMove():
    delay = _baseDelay * 4
    startPad = 0 
    baseColor = cRed
    for goOffs in _gradientOffs:
        color = getGradientOffs(baseColor, goOffs)
        _thread.start_new_thread(BankMoves, (startPad, _testpath, color ) )
        time.sleep(delay)

# menu offsets, use a negatwe go negatiove because it is more reliable to move backwards 
MainMenu = {'File':'', 'Edit':'LLLL,LLL', 'Add':'LLLL,LL', 'Patterns':'LLL,LL', 'View':'LLL,L', 'Options':'LLL', 'Tools':'LL', 'Help':'L'}
PRToolsMenu = {'Tools', 'LL'}
PRTools = {}

def menuPause(seconds = Settings.MENU_DELAY):
    time.sleep(seconds)

def ProcessKeys(cmdStr):
    commands = {'U':ui.up, 'D':ui.down, 'L':ui.left, 'R':ui.right, 
                'E':ui.enter, 'S': ui.escape, 'N': ui.next, ',':menuPause }
    for cmd in cmdStr:
        commands.get(cmd.upper(), menuPause)()

def NavigateFLMenu(cmdString = '', altmenu = False):
    # this code was inspired by HDSQ's implementation: 
    # https://github.com/MiguelGuthridge/Universal-Controller-Script/blob/main/src/plugs/windows/piano_roll.py
    #
    if (ui.isInPopupMenu()):
        ui.closeActivePopupMenu()
    # open the File menu
    if(altmenu):
        transport.globalTransport(FPT_ItemMenu, 1)
    else:
        transport.globalTransport(FPT_Menu, 1)
        if(ui.getFocused(widPianoRoll) == 1): # auto move to the tools when the PR is active.
            ProcessKeys('LL')
    if(len(cmdString) > 0):
        ProcessKeys(cmdString)

def ShowScriptDebug():
    ui.showWindow(widChannelRack)       # make CR the active window so it pulls up the main menu
    NavigateFLMenu(',LLLLDDDDDDDDDDE')  # series of keys to pass

def ShowProject():
    ui.showWindow(widChannelRack)       # make CR the active window so it pulls up the main menu
    NavigateFLMenu(',LLL,LUUUUUELL')  # series of keys to pass

def ViewArrangeIntoWorkSpace():
    ui.showWindow(widChannelRack)       # make CR the active window so it pulls up the main menu
    NavigateFLMenu(',LLLLDDDDDDDDDDDDDDDDDDRDE')  # series of keys to pass

# VERSION Helpers
# Producer Edition v20.99.3000 [build 3209]
# # 
#  def getVersionNum():
#      return ui.getVersion()[ui.getVersion().index('v')+1:ui.getVersion().index('[')-1]
# def getVersionTuple(v = ''):
#     if v == '':
#         v = getVersionNum()
#     return tuple(map(int, (v.split("."))))

def checkFLVersionAtLeast(version):
    res = FLVersionAtLeast(version)
    if(not res):
        print('* FL Version is not supported at this time. *')
    return res   

def hidePLRect():
    showPLRect(-1,0,0,0)

def showPLRect(startBar, endBar, firstPLTrackIdx, numTracks):
    if(startBar>0): # 0-based
        startBar = startBar - 1 
    playlist.liveDisplayZone(startBar, firstPLTrackIdx, endBar, firstPLTrackIdx+numTracks)

def test():
    return

"""
Helper code for dealing with version checking.
Authors:
* NFX (main implementation)
* Miguel Guthridge (minor improvements)
"""
def getVersionStr() -> str:
    """
    Returns the version string with just the version number (eg '20.9.2')
    """
    return ui.getVersion()[ui.getVersion().index('v')+1:ui.getVersion().index('[')-1]

def getVersionTuple(v: str) -> tuple[int, int, int]:
    """
    Converts a version string into a tuple for easy comparison with other version strings
    """
    if v == '':
        v = getVersionStr()
    return tuple(map(int, (v.split("."))))

def FLVersionAtLeast(version: str) -> bool:
    """
    Expects a three part version string, ie. "20.99.0", return True when FL version is equal or greater than
    """
    return getVersionTuple(getVersionStr()) >= getVersionTuple(version)

# color funcs
def ColorToRGB(Color):
    return (Color >> 16) & 0xFF, (Color >> 8) & 0xFF, Color & 0xFF

def RGBToColor(R,G,B):
    return (R << 16) | (G << 8) | B

def GradientTest(stepsize = 8):
    #def Gradient(color1, color2, stepsize, padOffs=0):
    #stepsize = 4 # 255//5
    Gradient(cBlue, cOff, stepsize, 0)
    Gradient(cPurple, cOff, stepsize, 16)
    Gradient(cMagenta, cOff, stepsize, 32)
    Gradient(cRed, cOff, stepsize, 48)
    Gradient(cOrange, cOff, stepsize, 8)
    Gradient(cYellow, cOff, stepsize, 24)
    Gradient(cGreen, cOff, stepsize, 40)
    Gradient(cCyan, cOff, stepsize, 56)


def ShadeTest():
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

def ShowLayout(pads1, color1, pads2, color2):
    for pad in pads1:
        SetPadColor(pad, color1, dimDefault)
    for pad in pads2:
        SetPadColor(pad, color2, dimDefault)

def Dims(color, padOffs=0):
    SetPadColor(0+padOffs, color, dimDim)
    SetPadColor(1+padOffs, color, dimDefault)
    SetPadColor(2+padOffs, color, dimBright)
    SetPadColor(3+padOffs, color, dimFull)


def Shades(color, padOffs=0):
    SetPadColor(0+padOffs, getShade(color, shDim), 0)
    SetPadColor(1+padOffs, getShade(color, shDark), 0)
    SetPadColor(2+padOffs, getShade(color, shNorm), 0)
    SetPadColor(3+padOffs, getShade(color, shLight), 0)

def Grads(color, stepsize = 64):
    Gradient(cOff, color, stepsize, 0, 32)
    Gradient(color, cWhite, stepsize, 32, 32)


def Gradient(color1, color2, stepsize, padOffs=0, len=8):
    gradientList = []
    for pad in range(len):
        step = (127//stepsize) * pad
        col = FadeColor(color1, color2, step)
        if(padOffs > -1):
            SetPadColor(pad+padOffs, col, 0)
        gradientList.append(col)
    return gradientList


goDim = 0
goDark = 16
goNorm = 32
goLight = 48
_gradientOffs = [goLight, goNorm, goDark, goDim] # light to dark
def getGradientOffs(baseColor, goVal):
    gradientList = Gradient(cOff, baseColor, 64, -1, 32)
    gradientList.extend(Gradient(baseColor, cWhite, 64, -1, 32))
    return gradientList[goVal]  #, gradientList






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

from fireNFX_DefaultSettings import Settings

def TestPallette(dimMult = 4):
    for idx, color in enumerate(Settings.Pallette.values()):
        SetPadColor(idx+0, color, 0, False, False, dimMult)
        SetPadColor(idx+16, color, Settings.DIM_BRIGHT, False, False, dimMult)
        SetPadColor(idx+32, color, Settings.DIM_NORMAL, False, False, dimMult)
        SetPadColor(idx+48, color, Settings.DIM_DIM, False, False, dimMult)

def Pallette(jumpBy = 64):
    pad = 0
    offs = 0
    for r in range(0,128, jumpBy):
        for g in range(0,128, jumpBy):
            for b in range(0,128, jumpBy):
                print('pad', pad % 64, 'rgb', r,g,b, 'hex', hex(RGBToColor(r,g,b)) )
                SetPadColor(pad % 64, RGBToColor(r,g,b), 0)
                pad+= 1
                
def TestQuad(path = "DRULLDDRRRUUULLL", mirrMode = 0):
    TestTraveler(cPurple, 4, 4, path, mirrMode)

def SetColorPadColorMatrix(submatrices, padIdx, color, dimF, altMode = 0):
    #altMode 0 = None, 1 = X only, 2 = Y only, 3 = x,y, 4 = x y and xy
    for idx, matrix in enumerate(submatrices):
        if altMode > 0:
            if altMode == 1 and (idx % 2 != 0):
                matrix = anim.MirrorMatrix(matrix, True, False)
            if altMode == 2 and (idx %2 != 0):
                matrix = anim.MirrorMatrix(matrix, False, True)
            if altMode == 3 and (idx %2 != 0):
                matrix = anim.MirrorMatrix(matrix, True, True)
            if altMode == 4:
                matrixOffs = idx % 4
                if matrixOffs > 0:
                    if (matrixOffs == 1): # alternate
                        matrix = anim.MirrorMatrix(matrix, True, False)
                    if (matrixOffs == 2): # alternate
                        matrix = anim.MirrorMatrix(matrix, False, True)
                    if (matrixOffs == 3): # alternate
                        matrix = anim.MirrorMatrix(matrix, True, True)

        pads = anim.FlattenMatrix(matrix)
        padNum = pads[padIdx] 
        SetPadColor(padNum, color, dimF)


def DrawTraveler(submatrices, traveler, mirrorMode = 0):
    # modes 0 = none, 1 = X, 2 = y, 3 = x, y 
    dimF = 0 # no dim
    color = traveler.color
    SetColorPadColorMatrix(submatrices, traveler.getPadIndex(), color, dimF)
    if mirrorMode > 0:
        if mirrorMode in [1,3]:
            SetColorPadColorMatrix(submatrices, traveler.getPadIndex(True, False), color, dimF)
        if mirrorMode in [2,3]:
            SetColorPadColorMatrix(submatrices, traveler.getPadIndex(False, True), color, dimF)
        if mirrorMode in [3]:
            SetColorPadColorMatrix(submatrices, traveler.getPadIndex(True, True), color, dimF)

def DrawTail(submatrices, traveler, mirrorMode = 0):
    # modes 0 = none, 1 = X, 2 = y, 3 = x, y 
    dimF = 0
    print('tail', traveler.tail)
    
    sorted_tuples = sorted(traveler.tail.items(), key=lambda x: x[1], reverse=True)  # Sort the list of tuples by the values in descending order
    sorted_tail = dict(sorted_tuples)  # Create a new dictionary from the sorted list of tuples

    for padOffs, dimF in sorted_tail.items():
        color = traveler.color
        print('item', padOffs, dimF, traveler.color)
        # if(dimF == 0):
        #     color = cRed
        if(dimF >= traveler.tailSize):
            color = cOff

        # while we can use the traveler's color, we cannot rely upon it's position
        # to give us the mirrored locations of the tail
        SetColorPadColorMatrix(submatrices, padOffs, color, dimF, 0)
        if mirrorMode > 0:
            if mirrorMode in [1]:
                x, y = anim.PadIndexToXY(padOffs, traveler.width, traveler.height, 1)
                SetColorPadColorMatrix(submatrices, anim.XYToPadIndex(x, y, traveler.width), color, dimF, 1)
            if mirrorMode in [2]:
                x, y = anim.PadIndexToXY(padOffs, traveler.width, traveler.height, 2)
                SetColorPadColorMatrix(submatrices, anim.XYToPadIndex(x, y, traveler.width), color, dimF, 2)
            if mirrorMode in [3]:
                x, y = anim.PadIndexToXY(padOffs, traveler.width, traveler.height, 3)
                SetColorPadColorMatrix(submatrices, anim.XYToPadIndex(x, y, traveler.width), color, dimF, 3)

def TestTravelerLoop(color = cRed, width = 16, height = 4, path = 'LDLLUURRD', mirrMode = 0, centerStart = True, Looptimes = 4):
    newpath = ''
    for i in range(Looptimes):
        newpath += path
    TestTraveler(color, width, height, newpath, mirrMode, centerStart)

def TestTraveler(color = cRed, width = 16, height = 4, path = 'LDLLUURRD', mirrMode = 0, centerStart = True):
    delay = 0.1
    startX = 0 
    startY = 0 
    if(centerStart):
        startX = (width//2) - 1 
        startY = (height//2) - 1
    
    traveler = anim.Traveler(color, startX, startY, width, height) # init
    submatrices = anim.SubDivideMatrix(anim._PadMatrix, height, width) # h, w

    for step in path:
        time.sleep(delay)
        if step in ["Z", "0"]:
            traveler.stay()
        if step in ['L', '4']:
            traveler.move_left()
        if step in ['R', '6']:
            traveler.move_right()
        if step in ['U', '8']:
            traveler.move_up()
        if step in ['D', '2']:
            traveler.move_down()
        if step in ["7"]:
            traveler.move_up(False)
            traveler.move_left()
        if step in ["9"]:
            traveler.move_up(False)
            traveler.move_right()
        if step in ["1"]:
            traveler.move_down(False)
            traveler.move_left()
        if step in ["3"]:
            traveler.move_down(False)
            traveler.move_right()
    
        DrawTail(submatrices, traveler, mirrMode)


    # finish tail
    while len(traveler.tail.keys()) > 0:
        traveler.stay()
        time.sleep(delay)
        print('cu', traveler.tail)
        DrawTail(submatrices, traveler, mirrMode)

    return 


def get_note_time(note_length, tempo, dotted=False):
    """
    Calculates the time (in milliseconds) for a note of the given length
    at the given tempo (in beats per minute).
    If `dotted` is True, the note is dotted (lengthened by 50%).
    """
    # Define the number of milliseconds per minute
    ms_per_minute = 60000
    
    # Calculate the time for one beat at the given tempo
    beat_time = ms_per_minute / tempo
    
    # Calculate the time for the requested note length
    if note_length == 1:
        # Whole note
        note_time = 4 * beat_time
    elif note_length == 2:
        # Half note
        note_time = 2 * beat_time
    elif note_length == 4:
        # Quarter note
        note_time = beat_time
    elif note_length == 8:
        # Eighth note
        note_time = beat_time / 2
    elif note_length == 16:
        # Sixteenth note
        note_time = beat_time / 4
    elif note_length == 32:
        # Thirty-second note
        note_time = beat_time / 8
    elif note_length == 64:
        # Sixty-fourth note
        note_time = beat_time / 16
    else:
        # Invalid note length
        raise ValueError("Invalid note length")
    
    # Check if the note is dotted
    if dotted:
        note_time *= 1.5
    
    return note_time

last_time = None
def printts(text):
    global last_time
    
    # Get the current time in milliseconds
    current_time = time.time() * 1000
    
    # Calculate the time difference since the last call
    if last_time is not None:
        time_diff = current_time - last_time
    else:
        time_diff = 0
    
    # Print the text with the timestamp
    print(f"{text} ({time_diff:.2f} ms)")
    
    # Update the last_time variable
    last_time = current_time



# TestQuad("U", 1)
# TestTraveler(16, 4, 'UDDD9R-R-R-R-R-R-R-R-R-R-R-R-R-99DDD9R-R-R-R-R-R-R-R-R-R-R-R-R-9-9', 0)        
        
        


