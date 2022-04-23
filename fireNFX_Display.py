import screen # this is for the FIRE display and is undocumented
from midi import *
from fireNFX_Defs import *


DisplayWidth = 128
DisplayHeight = 64
# Text settings
Font6x8 = 0
Font6x16 = 1
Font10x16 = 2
Font12x32 = 3
JustifyLeft = 0
JustifyCenter = 1
JustifyRight = 2
ScreenDisplayDelay = 2 # delay (in ms) required to access the screen (seems slow)

TextScrollPause = 5
TextScrollSpeed = 2
TextDisplayTime = 4000

TimedTextRow = 1
FPSRow = 3
FireFontSize = 15 # was 16
TextOffset = -4
TextRowHeight = 18 #was 20

Idle_Interval = 100
Idle_Interval_Max = 8

ScreenActiveTimeout = 10 # seconds to keep screen active (screen has its own timeout which will kick in after this)
ScreenAutoTimeout = 5

tlNone = 1
tlText = 1 << 1
tlBar = 1 << 2
tlMeter = 1 << 3

ROWTOP = 0
ROWMID = 1
ROWBOT = 2


def ClearDisplay():
    screen.fillRect(0, 0, DisplayWidth, DisplayHeight, 0x000000)
    screen.update()

def DisplayText(Font, Justification, PageTop, Text, CheckIfSame, DisplayTime = 0):
    try:
        screen.displayText(Font, Justification, PageTop, Text, CheckIfSame, DisplayTime)
        screen.update()
    except:
        return 
    
def DisplayBar(Text, Value, Bipolar):
    screen.displayBar(0, TextRowHeight * TimedTextRow, Text, Value, Bipolar)


def DisplayTimedText2(Text1, Text2, Text3):
    screen.displayTimedText(Text1, ROWTOP)
    screen.displayTimedText(Text2, ROWMID)
    screen.displayTimedText(Text3, ROWBOT)
    screen.update()


def DisplayTimedText(Text):
    screen.displayTimedText(Text, TimedTextRow)
    screen.update()

def InitDisplay():
    screen.init(DisplayWidth, DisplayHeight, TextRowHeight, FireFontSize, 0xFFFFFF, 0)
    sysexHeader = int.from_bytes(bytes([MIDI_BEGINSYSEX, ManufacturerIDConst, DeviceIDBroadCastConst ,ProductIDConst, MsgIDSendPackedOLEDData]), byteorder='little')
    screen.setup(sysexHeader, ScreenActiveTimeout, ScreenAutoTimeout, TextScrollPause, TextScrollSpeed, TextDisplayTime)
    screen.fillRect(0, 0, DisplayWidth, DisplayHeight, 0)

def DeInitDisplay():
    screen.deInit()

# Helpers

def DisplayTextAll(textTop, textMid, textBot):
    DisplayTextTop(textTop)
    DisplayTextMiddle(textMid)
    DisplayTextBottom(textBot)
    screen.update

def DisplayTextTop(text):
    DisplayText(Font6x16 , JustifyLeft, ROWTOP, text, True)

def DisplayTextMiddle(text):
    DisplayText(Font6x16 , JustifyLeft, ROWMID, text, True)

def DisplayTextBottom(text):
    DisplayText(Font6x16 , JustifyLeft, ROWBOT, text, True)





#snippets

#i = screen.findTextLine(0, 20, 128, 20 + 44)
#if (general.getVersion() > 8):
#  if (i >= 0):
#    screen.removeTextLine(i, 1)
#  if mode in [ScreenModePeak, ScreenModeScope]:
#    screen.addMeter(mode, 0, 20, 128, 20 + 44)

#screen.init(self.DisplayWidth, self.DisplayHeight, TextRowHeight, FireFontSize, 0xFFFFFF, 0)
#sysexHeader = int.from_bytes(bytes([MIDI_BEGINSYSEX, ManufacturerIDConst, DeviceIDBroadCastConst ,ProductIDConst, MsgIDSendPackedOLEDData]), byteorder='little')
#screen.setup(sysexHeader, ScreenActiveTimeout, ScreenAutoTimeout, TextScrollPause, TextScrollSpeed, TextDisplayTime)
#self.BgCol = 0x000000
#self.FgCol = 0xFFFFFF
#self.DiCol = 0xFFFFFF
#screen.fillRect(0, 0, self.DisplayWidth, self.DisplayHeight, 0)
