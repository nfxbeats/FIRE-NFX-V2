#   PluginName:  Gross Beat
#   Created by:  NFX
# 
from fireNFX_Classes import TnfxParameter, TnfxChannelPlugin, cpChannelPlugin, cpMixerPlugin, TnfxParamPadMapping
from fireNFX_PluginDefs import USER_PLUGINS
from fireNFX_Colors import *
pluginGrossBeat = TnfxChannelPlugin('Gross Beat', '', cpMixerPlugin)
if(pluginGrossBeat.Name not in USER_PLUGINS.keys()):
    USER_PLUGINS[pluginGrossBeat.Name] = pluginGrossBeat
    print('Gross Beat parameter definitions loaded.')
 
pluginGrossBeat.addParamToGroup('ALL', TnfxParameter(0, 'Time slot', 0, 'Empty', False) )
pluginGrossBeat.addParamToGroup('ALL', TnfxParameter(1, 'Volume slot', 0, 'Empty', False) )
pluginGrossBeat.addParamToGroup('ALL', TnfxParameter(2, 'Time mix', 0, '100%', False) )
pluginGrossBeat.addParamToGroup('ALL', TnfxParameter(3, 'Volume mix', 0, '100%', False) )
pluginGrossBeat.addParamToGroup('ALL', TnfxParameter(4, 'Volume smoothing attack', 0, '2.00ms', False) )
pluginGrossBeat.addParamToGroup('ALL', TnfxParameter(5, 'Volume smoothing release', 0, '3.66ms', False) )
pluginGrossBeat.addParamToGroup('ALL', TnfxParameter(6, 'Volume envelope tension', 0, '0%', False) )
pluginGrossBeat.addParamToGroup('ALL', TnfxParameter(7, 'Hold delay (bar repeat)', 0, '', False) )
pluginGrossBeat.addParamToGroup('ALL', TnfxParameter(8, 'Time offset (scratching)', 0, '-000:00:000', False) )

pdTimeMap = [  0,  1,  2,  3,  4,  5,  6,  7,
            16, 17, 18, 19, 20, 21, 22, 23,
            32, 33, 34, 35, 36, 37, 38, 39,
            48, 49, 50, 51, 52, 53, 54, 55,
            -1, -1, -1, -1 ] # last four are to pad it to 36 total

pdVolMap = [  8,  9, 10, 11, 12, 13, 14, 15,
             24, 25, 26, 27, 28, 29, 30, 31,
             40, 41, 42, 43, 44, 45, 46, 47,
             56, 57, 58, 59, 60, 61, 62, 63,
             -1, -1, -1, -1 ] # last four are to pad it to 36 total

timeMap = TnfxParamPadMapping(0, cGreen, pdTimeMap)
volMap = TnfxParamPadMapping(1, cOrange, pdVolMap)

pluginGrossBeat.ParamPadMaps.append(timeMap)
pluginGrossBeat.ParamPadMaps.append(volMap)


# [PARAMETER OFFSETS] 
# Notice, the code lines above contains the text "TnfxParameter(" followed by a number
# That number represents the parameter offset for the parameter described on that line
# You can use the parameter offset number to program your own USER Knob mappings below
# 
# [HOW TO SET CUSTOM KNOB MAPPINGS]
# The assignKnobs() function takes a list of up to 8 parameter offsets.
# The list must be in brackets like this [ 21, 12, 3, 7]. Max 8 offsets in list.
# it assigns them in order from :
#   USER1, KNOBS 1-4 as the first 4 params
#   USER2, KNOBS 1-4 as the second 4 params

# [ENABLING THE CUSTOM MAPPING]
# Comment/Uncomment the next line to disable/enable the knob mappings. 
#pluginGrossBeat.assignKnobs([0, 1, 2, 3, 4, 5, 6, 7]) 
 
# [LAST STEP. DO NOT FORGET. NEEDED TO INCLUDE YOUR MAPPINGS] 
# Add the following line (without the #) to the end of fireNFX_CustomPlugins.py
#from pluginGrossBeat import pluginGrossBeat
