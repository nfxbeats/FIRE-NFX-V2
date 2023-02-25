# special
cOff        = 0x000000
cSilver     = 0X606060
cDimWhite   = 0x202020
cChannel    = -1   # value to indicate to use the previous channel color in specific cases.
cNotMuted   = cDimWhite
cMuted      = cOff


pallette1 = {   'Red': 0xA00000,
                'Orange': 0xE07F00, #0xFF7F00, 
                'Yellow': 0xFFFF00,
                'Lime': 0xAFFF00,
                'Green': 0x00FF00,
                'Teal': 0x00FFb0, 
                'Cyan': 0x00B0FF,
                'Blue': 0x0000FF,
                'Purple': 0x370093,
                'Magenta': 0xFF00FF,
                'White': 0xFFFFFF,
                'Black': 0x000000
            }

pallette2 = {   'Red': 0xA04B4B,
                'Orange': 0xDEAA5D,
                'Yellow': 0xDED008,
                'Lime': 0xA9F833,
                'Green': 0x23B100,
                'Teal': 0xC1CCC0, 
                'Cyan': 0x33DFE0,
                'Blue': 0x002AFF,
                'Purple': 0xA858FF,
                'Magenta': 0xDF78F1,
                'White': 0xFFFFFF,
                'Black': 0x000000
            }




# the base 12 distinct colors
cRed        = pallette1["Red"]
cOrange     = pallette1["Orange"]
cYellow     = pallette1["Yellow"]
cLime       = pallette1["Lime"]
cGreen      = pallette1["Green"]
cTeal       = pallette1["Teal"]
cCyan       = pallette1["Cyan"]
cBlue       = pallette1["Blue"]
cPurple     = pallette1["Purple"]
cMagenta    = pallette1["Magenta"]
cWhite      = pallette1["White"]
cBlack      = pallette1["Black"]

def SetPallette(p):
    global cWhite
    global cBlack
    global cRed 
    global cOrange
    global cYellow
    global cLime
    global cGreen
    global cTeal
    global cCyan
    global cBlue
    global cPurple
    global cMagenta

    cWhite      = p["White"]
    cBlack      = p["Black"]
    cRed        = p["Red"]
    cOrange     = p["Orange"]
    cYellow     = p["Yellow"]
    cLime       = p["Lime"]
    cGreen      = p["Green"]
    cTeal       = p["Teal"]
    cCyan       = p["Cyan"]
    cBlue       = p["Blue"]
    cPurple     = p["Purple"]
    cMagenta    = p["Magenta"]

