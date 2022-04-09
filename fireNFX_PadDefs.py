from fireNFX_Colors import *

# defines the pads when used as a set from 0..63
pdPatterns = [ 0,  1,  2,  3,  4,  5,  6,  7,  8,  9, 10, 11]   # top row, first 12
pdMutes =  [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27]     # second row, first 12
pdChanStrip =  [ 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43  ] # third row, first 12
pdChanStripMutes = [ 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59 ] # fourth row, first 12
pdProgress = [12, 13, 14, 15, 31, 47, 63, 62, 61, 60, 44, 28]  


# these are defined in "FPC" order. Bottom Left is 0 index for pads
# so I define them bottom to top order for each set.
pdFPCA = [48, 49, 50, 51,
          32, 33, 34, 35, 
          16, 17, 18, 19,
           0,  1,  2,  3]

pdFPCB = [52, 53, 54, 55,
          36, 37, 38, 39,
          20, 21, 22, 23,
           4,  5,  6,  7]




#[ 12, 13, 14, 15, 28, 29, 30, 31]
pdMacroStrip = [30, 31, 
                14, 15,
                46, 47, 
                62, 63]
colMacroStrip = [ cBlueDark,  cBlueMed, cBlueLight, cRed, cDimWhite, cCyan, cGreen, cOrange]

pdPresetPrev = 44
pdPresetNext = 60
pdPresetNav = [pdPresetPrev, pdPresetNext]
colPresetNav = [cDimWhite, cWhite]

dimDefault = 3
dimBright = 1
dimFull = 0

