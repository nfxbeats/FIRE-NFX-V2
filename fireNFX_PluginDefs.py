from fireNFX_Classes import TnfxChannelPlugin, TnfxParameter
from fireNFX_Defs import FLEFFECTS
from pluginFLEX import plFLEX
from pluginFLKeys import plFLKeys
from pluginSTRUMGS2 import plStrumGS2
from pluginSlicex import plSlicex
from pluginFruityDance import plFruityDance
from pluginLoungeLizardEP4 import plLoungeLizardEP4
from midi import *

# for the FPC modes
#plFPC = TnfxChannelPlugin('FPC')
ppFPC_Volume = TnfxParameter(  0, 'PAD Volume', 0, '', False)
ppFPC_Pan    = TnfxParameter( 16, 'PAD Pan',    0, '', True)
ppFPC_Mute   = TnfxParameter( 32, 'PAD Mute',   0, '', True)
ppFPC_Solo   = TnfxParameter( 48, 'PAD Solo',   0, '', True)
ppFPC_Tune   = TnfxParameter( 256,'PAD Tune',   0, '', False)

# FL Channel FX 
plFLChanFX = TnfxChannelPlugin(FLEFFECTS)
plFLChanFX.addParamToGroup('CHANNEL', TnfxParameter(REC_Chan_Mute, 'CHAN Mute', 0, '', False, 1)) # NO Value return
plFLChanFX.addParamToGroup('CHANNEL', TnfxParameter(REC_Chan_Pan, 'CHAN Pan', 0, '', True))
plFLChanFX.addParamToGroup('CHANNEL', TnfxParameter(REC_Chan_Vol, 'CHAN Volume', 0, '', False))
plFLChanFX.addParamToGroup('CHANNEL', TnfxParameter(REC_Chan_Pitch, 'CHAN Pitch', 0, '', False, 128))
plFLChanFX.addParamToGroup('CHANNEL', TnfxParameter(REC_Chan_FXTrack, 'CHAN Mixer Trk', 0, '', False, 128))
REC_Chan_Arp_Mode = REC_Chan_Arp_First
REC_Chan_Arp_Range = REC_Chan_Arp_First + 1
plFLChanFX.addParamToGroup('ARPEGGIATOR', TnfxParameter( REC_Chan_Arp_Mode, 'ARP Mode', 0, '', False)) # NO Value return
plFLChanFX.addParamToGroup('ARPEGGIATOR', TnfxParameter( REC_Chan_Arp_Time, 'ARP Time', 0, '', False))
plFLChanFX.addParamToGroup('ARPEGGIATOR', TnfxParameter( REC_Chan_Arp_Gate, 'ARP Gate', 0, '', False))
plFLChanFX.addParamToGroup('ARPEGGIATOR', TnfxParameter( REC_Chan_Arp_Range, 'ARP Range', 0, '', False))
plFLChanFX.addParamToGroup('ARPEGGIATOR', TnfxParameter( REC_Chan_Arp_Repeat, 'ARP Repeat', 0, '', False))
plFLChanFX.addParamToGroup('ARPEGGIATOR', TnfxParameter( REC_Chan_Arp_Chord, 'ARP Chord', 0, '', False)) # NO Value return 
# delay
REC_Chan_Delay_Feed = REC_Chan_Delay_First
REC_Chan_Delay_Pan = REC_Chan_Delay_First + 1
REC_Chan_Delay_Pitch = REC_Chan_Delay_First + 2
REC_Chan_Delay_Echoes = REC_Chan_Delay_First + 3
REC_Chan_Delay_ModY = REC_Chan_Delay_First + 5
REC_Chan_Delay_ModX = REC_Chan_Delay_First + 6
plFLChanFX.addParamToGroup('DELAY', TnfxParameter( REC_Chan_Delay_Feed, 'DLY Feed', 0, '', False))
plFLChanFX.addParamToGroup('DELAY', TnfxParameter( REC_Chan_Delay_Pan, 'DLY Pan', 0, '', True))
plFLChanFX.addParamToGroup('DELAY', TnfxParameter( REC_Chan_Delay_ModX, 'DLY Mod X', 0, '', False))
plFLChanFX.addParamToGroup('DELAY', TnfxParameter( REC_Chan_Delay_ModY, 'DLY Mod Y', 0, '', False))
plFLChanFX.addParamToGroup('DELAY', TnfxParameter( REC_Chan_Delay_Pitch, 'DLY Pitch', 0, '', True))
plFLChanFX.addParamToGroup('DELAY', TnfxParameter( REC_Chan_Delay_Time, 'DLY Time', 0, '', False))
plFLChanFX.addParamToGroup('DELAY', TnfxParameter( REC_Chan_Delay_Echoes, 'DLY Echoes', 0, '', False))
#plFLChanFX.addParamToGroup('DELAY', TnfxParameter( REC_Chan_Delay_First+7, '7-DLY Feed', 0, '', False)) #crash
plFLChanFX.addParamToGroup('LEVELS', TnfxParameter(REC_Chan_OfsPan, 'LVL Pan', 0, '', True))
plFLChanFX.addParamToGroup('LEVELS', TnfxParameter(REC_Chan_OfsVol, 'LVL Volume', 0, '', False))
# plFLChanFX.addParamToGroup('X', TnfxParameter(REC_Chan_OfsPitch, 'OfsPitch', 0, '', False)) # crash
plFLChanFX.addParamToGroup('LEVELS', TnfxParameter(REC_Chan_OfsFCut, 'LVL Mod X', 0, '', False))
plFLChanFX.addParamToGroup('LEVELS', TnfxParameter(REC_Chan_OfsFRes, 'LVL Mod Y', 0, '', False))
plFLChanFX.addParamToGroup('POLYPHONY', TnfxParameter(REC_Chan_PortaTime, 'POLY Slide Time', 0, '', False)) # NO Value return
plFLChanFX.addParamToGroup('TIME', TnfxParameter(REC_Chan_GateTime, 'TIME Gate', 0, '', False)) # NO Value return
# plFLChanFX.addParamToGroup('X', TnfxParameter(REC_Chan_Crossfade, 'Crossfade', 0, '', False)) # does nothing, also no return value
plFLChanFX.addParamToGroup('TIME', TnfxParameter(REC_Chan_TimeOfs, 'TIME Shift', 0, '', False, 24))
plFLChanFX.addParamToGroup('TIME', TnfxParameter(REC_Chan_SwingMix, 'TIME Swing Mix', 0, '', False))
# mismatched get/set offsets
REC_Chan_Tracking_Pan_Setter = REC_Chan_Arp_First + 6 
REC_Chan_Tracking_Pan_Getter = REC_Chan_Track_First
REC_Chan_Tracking_ModX_Setter = REC_Chan_Arp_First + 7 
REC_Chan_Tracking_ModX_Getter = REC_Chan_Track_First
REC_Chan_Tracking_ModY_Setter = REC_Chan_Arp_First + 8 
REC_Chan_Tracking_ModY_Getter = REC_Chan_Track_First
plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_Pan_Setter, 'TRK Pan', 0, '', True))
plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_ModX_Setter, 'TRK Mod X', 0, '', True))
plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_ModY_Setter, 'TRK Mod Y', 0, '', True))

# Sampler / Audio
plSampler = TnfxChannelPlugin("Sampler")
plSampler.isNative = True
plSampler.addParamToGroup('MAIN', TnfxParameter(REC_Chan_Mute, 'MAIN Mute', 0, '', False, 1)) # NO Value return
plSampler.addParamToGroup('MAIN', TnfxParameter(REC_Chan_Pan, 'MAIN Pan', 0, '', True))
plSampler.addParamToGroup('MAIN', TnfxParameter(REC_Chan_Vol, 'MAIN Volume', 0, '', False))
plSampler.addParamToGroup('MAIN', TnfxParameter(REC_Chan_Pitch, 'MAIN Pitch', 0, '', False, 128))
plSampler.addParamToGroup('MAIN', TnfxParameter(REC_Chan_FXTrack, 'MAIN Mixer Trk', 0, '', False, 128))
plSampler.addParamToGroup('FILTER', TnfxParameter(REC_Chan_FCut, 'FLT Cut/Mod X', 0, '', False))
plSampler.addParamToGroup('FILTER', TnfxParameter(REC_Chan_FRes, 'FLT Res/Mod Y', 0, '', False))
plSampler.addParamToGroup('FILTER', TnfxParameter(REC_Chan_FType, 'FLT Type', 0, '', False))
# plSampler.addParamToGroup('X', TnfxParameter(REC_Chan_Crossfade, 'Crossfade', 0, '', False)) # does nothing, also no return value
plSampler.addParamToGroup('PLAYBACK', TnfxParameter(REC_Chan_SmpOfs, 'PLAY Sample Offset', 0, '', False))
plSampler.addParamToGroup('TIME STRETCHING', TnfxParameter(REC_Chan_StretchTime, 'STRETCH Time', 0, '', False)) # NO Value return
# plSampler.addParamToGroup('X', TnfxParameter(REC_Chan_OfsPitch, 'OfsPitch', 0, '', False)) # crash

# # envelope
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_First, '0-EnvFirst', 0, '', False)) 
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_First + 1, '1-EnvFirst', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_First + 2, '2-EnvFirst', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_First + 3, '3-EnvFirst', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_First + 4, '4-EnvFirst', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_First + 5, '5-EnvFirst', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_First + 6, '6-EnvFirst', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_First + 7, '7-EnvFirst', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_First + 8, '8-EnvFirst', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_MA, '8-MA', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_LFO_First, '9-LFO1st', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_LFO_First+1, '10-LFO1st', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_LFOA, '11-LFOA', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_LFOA+1, '12-LFOA', 0, '', False))
# #plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_Hole, '13-Hole', 0, '', False)) # crash
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_Hole+1, '14-Hole', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_Hole+1, '15-Hole', 0, '', False))
# plSampler.addParamToGroup('ENV', TnfxParameter(REC_Chan_Env_PLast, '16-PLast', 0, '', False))

#plFLChanFX


CUSTOM_PLUGINS = {plFLEX.Name:plFLEX, plFLKeys.Name:plFLKeys, plStrumGS2.Name:plStrumGS2, plSlicex.Name: plSlicex,
                  plFruityDance.Name:plFruityDance, plLoungeLizardEP4.Name: plLoungeLizardEP4}





  








