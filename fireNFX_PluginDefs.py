from fireNFX_Classes import TnfxChannelPlugin, TnfxParameter
from pluginFLEX import plFLEX
from pluginFLKeys import plFLKeys
from pluginSTRUMGS2 import plStrumGS2

# for the FPC modes
plFPC = TnfxChannelPlugin('FPC')
ppFPC_Volume = TnfxParameter(  0, 'PAD Volume', 0, '', False)
ppFPC_Pan    = TnfxParameter( 16, 'PAD Pan',    0, '', True)
ppFPC_Mute   = TnfxParameter( 32, 'PAD Mute',   0, '', True)
ppFPC_Solo   = TnfxParameter( 48, 'PAD Solo',   0, '', True)
ppFPC_Tune   = TnfxParameter( 256,'PAD Tune',   0, '', False)

CUSTOM_PLUGINS = {plFLEX.Name:plFLEX, plFLKeys.Name:plFLKeys, plStrumGS2.Name:plStrumGS2}





  








