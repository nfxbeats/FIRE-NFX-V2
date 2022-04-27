
from fireNFX_Classes import *

ppFPC_Volume = TnfxParameter(  0, 'PAD Volume', 0, '', False)
ppFPC_Pan    = TnfxParameter( 16, 'PAD Pan',    0, '', True)
ppFPC_Mute   = TnfxParameter( 32, 'PAD Mute',   0, '', True)
ppFPC_Solo   = TnfxParameter( 48, 'PAD Solo',   0, '', True)
ppFPC_Tune   = TnfxParameter( 256,'PAD Tune',   0, '', False)


plStrumGS2 = TnfxPlugin('Strum GS-2')
plStrumGS2.Parameters.append( TnfxParameter(0, 'Play Mode', 0, 'Guitar', False)  )
plStrumGS2.Parameters.append( TnfxParameter(0, 'Play Mode', 0, 'Guitar', False)  )



