from fireNFX_Classes import TnfxChannelPlugin, TnfxParameter
from fireNFX_Defs import KM_USER1, KM_USER2
#   PluginName:  FL Keys
#   ParamCount:  15
# -----------------------------------------------------------------
plFLKeys = TnfxChannelPlugin('FL Keys')
plFLKeys.AlwaysRescan = False
plFLKeys.addParamToGroup('ENVIRONMENT', TnfxParameter(0, 'Decay', 0, '-32%', True) )
plFLKeys.addParamToGroup('ENVIRONMENT', TnfxParameter(1, 'Release', 0, '25%', True) )
plFLKeys.addParamToGroup('ENVIRONMENT', TnfxParameter(12, 'Pan/Tremolo', 0, 'Off', True) )
plFLKeys.addParamToGroup('ENVIRONMENT', TnfxParameter(7, 'Stereo', 0, '0%', False) )

plFLKeys.addParamToGroup('MISC', TnfxParameter(14, 'Overdrive', 0, '55.8%', False) )
plFLKeys.addParamToGroup('MISC', TnfxParameter(13, 'LFO Rate', 0, '0.01 Hz', False) )
plFLKeys.addParamToGroup('MISC', TnfxParameter(11, 'Treble', 0, '0%', True) )
plFLKeys.addParamToGroup('MISC', TnfxParameter(10, 'Stretch', 0, '0.0 cents', True) )

plFLKeys.addParamToGroup('VELOCITY', TnfxParameter(5, 'Vel->Muffle', 0, '100%', False) )
plFLKeys.addParamToGroup('VELOCITY', TnfxParameter(4, 'Muffle', 0, '100000%', False) )
plFLKeys.addParamToGroup('VELOCITY', TnfxParameter(3, 'Vel->Hardness', 0, '-100%', True) )
plFLKeys.addParamToGroup('VELOCITY', TnfxParameter(2, 'Hardness', 0, '12%', True) )
plFLKeys.addParamToGroup('VELOCITY', TnfxParameter(6, 'Vel Sensitivity', 0, '-50%', True) )

plFLKeys.addParamToGroup('TUNING', TnfxParameter(8, 'Tune', 0, '0 cents', True) )
plFLKeys.addParamToGroup('TUNING', TnfxParameter(9, 'Detune', 0, '3.0', False) )

for knob in range(4):
    plFLKeys.assignParameterToUserKnob(KM_USER1, knob, plFLKeys.ParameterGroups['ENVIRONMENT'][knob])

# -----------------------------------------------------------------
#    Non Blank Params Count: 15
