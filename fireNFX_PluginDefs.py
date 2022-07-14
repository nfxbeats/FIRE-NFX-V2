
from fireNFX_Classes import *


plFPC = TnfxPlugin('FPC')
ppFPC_Volume = TnfxParameter(  0, 'PAD Volume', 0, '', False)
ppFPC_Pan    = TnfxParameter( 16, 'PAD Pan',    0, '', True)
ppFPC_Mute   = TnfxParameter( 32, 'PAD Mute',   0, '', True)
ppFPC_Solo   = TnfxParameter( 48, 'PAD Solo',   0, '', True)
ppFPC_Tune   = TnfxParameter( 256,'PAD Tune',   0, '', False)

def getFPCPlugin():
    plFPC = TnfxPlugin('FPC')
    plFPC.Parameters.append(TnfxParameter(  0, 'PAD Volume', 0, '', False))
    plFPC.Parameters.append(TnfxParameter( 16, 'PAD Pan',    0, '', True))
    #plFPC.Parameters.append(TnfxParameter( 32, 'PAD Mute',   0, '', True))
    #plFPC.Parameters.append(TnfxParameter( 48, 'PAD Solo',   0, '', True))
    plFPC.Parameters.append(TnfxParameter( 256,'PAD Tune',   0, '', False))
    return plFPC

def getStrumGS2Plugin():
    plStrumGS2 = TnfxPlugin('Strum GS-2')
    plStrumGS2.Parameters.append( TnfxParameter(0, 'Play Mode',   0, 'Guitar',  False, 2)  )
    plStrumGS2.Parameters.append( TnfxParameter(4, 'Auto Strum',  0, 'Off',     False, 1)  )
    plStrumGS2.Parameters.append( TnfxParameter(7, 'Chord Type',  0, 'Movable', False)  )
    plStrumGS2.Parameters.append( TnfxParameter(8, 'Voicing Pos', 0, 'Fret 1',  False)  )
    return plStrumGS2

def getPlugin(pluginName):
    if(pluginName == 'Strum GS-2'):
        return getStrumGS2Plugin()
    else:
        return TnfxPlugin('Not Found')






