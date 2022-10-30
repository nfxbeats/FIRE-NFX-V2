from fireNFX_Classes import TnfxParameter, TnfxChannelPlugin
from fireNFX_PluginDefs import USER_PLUGINS
pluginSoundFontPlayer = TnfxChannelPlugin('SoundFont Player')
if(pluginSoundFontPlayer.Name not in USER_PLUGINS.keys()):
    print('sfp loaded')
    USER_PLUGINS[pluginSoundFontPlayer.Name] = pluginSoundFontPlayer
pluginSoundFontPlayer.addParamToGroup('MISC', TnfxParameter(4, 'Modulation', 0, '0', False) )
pluginSoundFontPlayer.addParamToGroup('MISC', TnfxParameter(12, 'Initial filter cutoff', 0, 'Disabled', False) )
pluginSoundFontPlayer.addParamToGroup('Env 2 ', TnfxParameter(5, 'attack time', 0, 'Disabled', False) )
pluginSoundFontPlayer.addParamToGroup('Env 2 ', TnfxParameter(6, 'decay time', 0, 'Disabled', False) )
pluginSoundFontPlayer.addParamToGroup('Env 2 ', TnfxParameter(7, 'sustain level', 0, 'Disabled', False) )
pluginSoundFontPlayer.addParamToGroup('Env 2 ', TnfxParameter(8, 'release time', 0, 'Disabled', False) )
pluginSoundFontPlayer.addParamToGroup('LFO 2', TnfxParameter(9, 'predelay', 0, 'Disabled', False) )
pluginSoundFontPlayer.addParamToGroup('LFO 2', TnfxParameter(10, 'amount', 0, 'Disabled', False) )
pluginSoundFontPlayer.addParamToGroup('LFO 2', TnfxParameter(11, 'speed', 0, 'Disabled', False) )
pluginSoundFontPlayer.addParamToGroup('RevCho', TnfxParameter(2, 'Reverb send level (multiplier)', 0, '100%', False) )
pluginSoundFontPlayer.addParamToGroup('RevCho', TnfxParameter(3, 'Chorus send level (multiplier)', 0, '100%', False) )
pluginSoundFontPlayer.assignKnobs([5,6,7,8,2,3,4,12]) 
