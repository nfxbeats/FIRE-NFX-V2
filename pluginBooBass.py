# Save this file as: "D:\ImageLineData\FL Studio\Settings\Hardware\nfxTest\pluginBooBass.py"
# 
#   PluginName:  BooBass
#   Created by: <your name here>
# 
from fireNFX_Classes import TnfxParameter, TnfxChannelPlugin
from fireNFX_PluginDefs import KNOWN_PLUGINS
pluginBooBass = TnfxChannelPlugin('BooBass')
if(pluginBooBass.Name not in KNOWN_PLUGINS.keys()):
    KNOWN_PLUGINS[pluginBooBass.Name] = pluginBooBass
 
pluginBooBass.addParamToGroup('ALL', TnfxParameter(0, 'Bass', 0, '50%', False) )
pluginBooBass.addParamToGroup('ALL', TnfxParameter(1, 'Mid', 0, '50%', False) )
pluginBooBass.addParamToGroup('ALL', TnfxParameter(2, 'Treble', 0, '50%', False) )

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
#
# [ENABLING THE CUSTOM MAPPING]
# Comment/Uncomment the next line to disable/enable the knob mappings. 
#pluginBooBass.assignKnobs([0, 1, 2]) 
# 
# [LAST STEP. DO NOT FORGET. NEEDED TO INCLUDE YOUR MAPPINGS] 
# Add the following line (without the #) to the end of fireNFX_PluginDefs.py
#from pluginBooBass.py import pluginBooBass
 