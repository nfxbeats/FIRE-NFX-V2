#   PluginName:  Fruity Dance
#   ParamCount:  7
# -----------------------------------------------------------------
from fireNFX_Classes import TnfxParameter, TnfxChannelPlugin
from fireNFX_Defs import KM_USER1, KM_USER2
plFruityDance = TnfxChannelPlugin('Fruity Dance')
plFruityDance.addParamToGroup('DANCER', TnfxParameter(0, 'Move', 0, 'Stepping', False) )
plFruityDance.addParamToGroup('DANCER', TnfxParameter(5, 'X-coord', 0, '', False, 128) )
plFruityDance.addParamToGroup('DANCER', TnfxParameter(6, 'Y-coord', 0, '', False, 128) )
plFruityDance.addParamToGroup('DANCER', TnfxParameter(1, 'Mirror', 0, '', False, 1) )
plFruityDance.addParamToGroup('DANCER', TnfxParameter(3, 'Blend', 0, '', False) )
plFruityDance.addParamToGroup('DANCER', TnfxParameter(4, 'Speed', 0, '', False) )
plFruityDance.addParamToGroup('DANCER', TnfxParameter(2, 'Show', 0, '', False, 1) )

# -----------------------------------------------------------------
plFruityDance.assignParameterToUserKnob(KM_USER1, 0, TnfxParameter(0, 'Move', 0, 'Stepping', False))
plFruityDance.assignParameterToUserKnob(KM_USER1, 1, TnfxParameter(4, 'Speed', 0, '', False))
plFruityDance.assignParameterToUserKnob(KM_USER1, 2, TnfxParameter(5, 'X coord', 0, '', False, 128))
plFruityDance.assignParameterToUserKnob(KM_USER1, 3, TnfxParameter(6, 'Y coord', 0, '', False, 128))