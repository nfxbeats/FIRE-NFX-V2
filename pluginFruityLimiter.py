# Save this file as: "D:\ImageLineData\FL Studio\Settings\Hardware\nfxTest\pluginFruityLimiter.py"
# 
#   PluginName:  Fruity Limiter
#   Created by:  NFX
# 
from fireNFX_Classes import TnfxParameter, TnfxChannelPlugin, cpChannelPlugin, cpMixerPlugin
from fireNFX_PluginDefs import USER_PLUGINS
pluginFruityLimiter = TnfxChannelPlugin('Fruity Limiter', '', cpMixerPlugin)
if(pluginFruityLimiter.Name not in USER_PLUGINS.keys()):
    USER_PLUGINS[pluginFruityLimiter.Name] = pluginFruityLimiter
    print('Fruity Limiter parameter definitions loaded.')
 
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(0, 'Gain', 0, '0.0dB  1.00', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(1, 'Soft saturation threshold', 0, '0.0dB  1.00', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(2, 'Limiter ceiling', 0, '0.0dB  1.00', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(3, 'Limiter attack time', 0, '2.00ms', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(4, 'Limiter attack curve', 0, '3', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(5, 'Limiter release time', 0, '85.53ms', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(6, 'Limiter release curve', 0, '3', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(7, 'Limiter peak window', 0, '10.00ms', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(8, 'Comp threshold', 0, '0.0dB  1.00', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(9, 'Comp ratio', 0, '1:1.0', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(10, 'Comp knee', 0, '0%', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(11, 'Comp attack time', 0, '0.00ms', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(12, 'Comp release time', 0, '248.22ms', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(13, 'Comp curve', 0, '', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(14, 'Comp RMS window', 0, '1.00ms', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(15, 'Noise gain', 0, '0.0dB  1.00', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(16, 'Noise threshold', 0, '-INFdB  0.00', False) )
pluginFruityLimiter.addParamToGroup('ALL', TnfxParameter(17, 'Noise release time', 0, '50.01ms', False) )
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
#pluginFruityLimiter.assignKnobs([0, 1, 2, 3, 4, 5, 6, 7]) 
 
# [LAST STEP. DO NOT FORGET. NEEDED TO INCLUDE YOUR MAPPINGS] 
# Add the following line (without the #) to the end of fireNFX_PluginDefs.py
#from pluginFruityLimiter import pluginFruityLimiter
 
# -----[ COPY UP TO THIS LINE, BUT DO NOT INCLUDE ]---------------
