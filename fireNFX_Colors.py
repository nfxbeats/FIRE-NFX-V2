# name= 
#

from fireNFX_Utils import PadColorFromFLColor

cChannel = -1 #generic value to indicate to use the channel color

cOff        = 0x000000
cWhite      = 0xFFFFFF
cSilver     = 0X606060
cDimWhite   = 0x101010

cMagenta    = 0x7F0040
cMagentaLight = cMagenta | 0x040040 

cRed        = 0xFF0000
cRedLight   = 0x800000

cOrange     =  0xFFA500

cYellow     = 0xFFFF00

cPurple         = 0x1000FF
cPurpleLight    = PadColorFromFLColor(0xA020F0)

cBlue       = 0x0000FF
cBlueDark  = cBlue & 0x001010
cBlueMed   = 0x0020FF
cBlueLight = cBlue | 0x004040 

cCyan       = 0x00FFFF

cGreen      = 0x00FF00
cGreenDark  = 0x084000
cGreenMed   = 0x12B900
cGreenLight = PadColorFromFLColor(0x43D633)


cX1 = cPurple & 0x100010
cX2 = cPurple | 0x100010 
cX3 = cPurple | 0x7f007f

