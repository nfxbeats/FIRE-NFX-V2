from fireNFX_Classes import TnfxChannelPlugin, TnfxParameter, cpGlobal
from fireNFX_Defs import FLEFFECTS

from pluginFLEX import plFLEX
from pluginFLKeys import plFLKeys
from pluginSTRUMGS2 import plStrumGS2
from pluginSlicex import plSlicex
from pluginFruityDance import plFruityDance
from pluginLoungeLizardEP4 import plLoungeLizardEP4
from midi import *

USER_PLUGINS = {}
KNOWN_PLUGINS = {plFLEX.Name:plFLEX, plFLKeys.Name:plFLKeys, plStrumGS2.Name:plStrumGS2, plSlicex.Name: plSlicex,
                  plFruityDance.Name:plFruityDance, plLoungeLizardEP4.Name: plLoungeLizardEP4}

try:
    from fireNFX_CustomPlugins import *
    KNOWN_PLUGINS.update(USER_PLUGINS)
    print('loaded custom plugins', USER_PLUGINS)
except e:
    print('except: {}'.format(e))


# for the FPC modes
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
plFLChanFX.addParamToGroup('LEVELS', TnfxParameter(REC_Chan_OfsPan, 'Pan', 0, '', True))
plFLChanFX.addParamToGroup('LEVELS', TnfxParameter(REC_Chan_OfsVol, 'Volume', 0, '', False))
# plFLChanFX.addParamToGroup('X', TnfxParameter(REC_Chan_OfsPitch, 'OfsPitch', 0, '', False)) # crash
plFLChanFX.addParamToGroup('LEVELS', TnfxParameter(REC_Chan_OfsFCut, 'Mod X', 0, '', False))
plFLChanFX.addParamToGroup('LEVELS', TnfxParameter(REC_Chan_OfsFRes, 'Mod Y', 0, '', False))


REC_Chan_MaxPoly = REC_Chan_Misc + 271
REC_Chan_MaxPoly2 = REC_Chan_Misc + 279
REC_Chan_PortaMono = REC_Chan_Misc + 289

plFLChanFX.addParamToGroup('POLYPHONY', TnfxParameter(REC_Chan_MaxPoly, 'Max Poly', 0, '', False)) 
plFLChanFX.addParamToGroup('POLYPHONY', TnfxParameter(REC_Chan_PortaMono, 'Porta/Mono', 0, '', False)) 
plFLChanFX.addParamToGroup('POLYPHONY', TnfxParameter(REC_Chan_PortaTime, 'Slide Time', 0, '', False)) # NO Value return

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
# plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_Pan_Setter, 'TRK Pan', 0, '', True))
# plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_ModX_Setter, 'TRK Mod X', 0, '', True))
# plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_ModY_Setter, 'TRK Mod Y', 0, '', True))

REC_Chan_Tracking_Vol_Pan  =  REC_Chan_Track_First
REC_Chan_Tracking_Vol_ModX =  REC_Chan_Track_First + 1
REC_Chan_Tracking_Vol_ModY =  REC_Chan_Track_First + 2
REC_Chan_Tracking_Vol_Mid  =  REC_Chan_Track_First + 3 # returns weird value from -2147483648 (0%) to -1082130432 (100%)
REC_Chan_Tracking_Key_Mid  =  REC_Chan_Track_First + 7 # MIDI note value. 60 decimal = note C5
REC_Chan_Tracking_Key_Pan  =  REC_Chan_Track_First + 16
REC_Chan_Tracking_Key_ModX =  REC_Chan_Track_First + 17
REC_Chan_Tracking_Key_ModY =  REC_Chan_Track_First + 18

plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_Vol_Pan, 'Vol Pan', 0, '', True))
plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_Vol_ModX, 'Vol Mod X', 0, '', True))
plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_Vol_ModY, 'Vol Mod Y', 0, '', True))
plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_Vol_Mid, 'Vol Middle', 0, '', True))
plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_Vol_Pan, 'Key Pan', 0, '', True))
plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_Vol_ModX, 'Key Mod X', 0, '', True))
plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_Vol_ModY, 'Key Mod Y', 0, '', True))
plFLChanFX.addParamToGroup('TRACKING', TnfxParameter( REC_Chan_Tracking_Vol_Mid, 'Key Middle', 0, '', True))



# Sampler / Audio
plSampler = TnfxChannelPlugin("Sampler")
plSampler.isNative = True
plSampler.addParamToGroup('MAIN', TnfxParameter(REC_Chan_Mute, 'MAIN Mute', 0, '', False, 1)) # NO Value return
plSampler.addParamToGroup('MAIN', TnfxParameter(REC_Chan_Pan, 'MAIN Pan', 0, '', True))
plSampler.addParamToGroup('MAIN', TnfxParameter(REC_Chan_Vol, 'MAIN Volume', 0, '', False))
plSampler.addParamToGroup('MAIN', TnfxParameter(REC_Chan_Pitch, 'MAIN Pitch', 0, '', False, 128))
plSampler.addParamToGroup('MAIN', TnfxParameter(REC_Chan_FXTrack, 'MAIN Mixer Trk', 0, '', False, 128))

REC_Chan_Env_Panning_PreDelay  = REC_Chan_Env_First + 9
REC_Chan_Env_Panning_Attack  = REC_Chan_Env_First + 10
REC_Chan_Env_Panning_Amount  = REC_Chan_Env_First + 11
REC_Chan_Env_Panning_LFO_Speed = REC_Chan_Env_First + 12


plSampler.addParamToGroup('FILTER', TnfxParameter(REC_Chan_FCut, 'FLT Cut/Mod X', 0, '', False))
plSampler.addParamToGroup('FILTER', TnfxParameter(REC_Chan_FRes, 'FLT Res/Mod Y', 0, '', False))
plSampler.addParamToGroup('FILTER', TnfxParameter(REC_Chan_FType, 'FLT Type', 0, '', False))
# plSampler.addParamToGroup('X', TnfxParameter(REC_Chan_Crossfade, 'Crossfade', 0, '', False)) # does nothing, also no return value
plSampler.addParamToGroup('PLAYBACK', TnfxParameter(REC_Chan_SmpOfs, 'PLAY Sample Offset', 0, '', False))
plSampler.addParamToGroup('TIME STRETCHING', TnfxParameter(REC_Chan_StretchTime, 'STRETCH Time', 0, '', False)) # NO Value return
# plSampler.addParamToGroup('X', TnfxParameter(REC_Chan_OfsPitch, 'OfsPitch', 0, '', False)) # crash


# global
plGlobal = TnfxChannelPlugin('Global')
plGlobal.isNative = True
plGlobalType = cpGlobal
plGlobal.addParamToGroup('FL Main', TnfxParameter(REC_MainVol, 'Volume', 0, '', False))
plGlobal.addParamToGroup('FL Main', TnfxParameter(REC_MainShuffle, 'Shuffle', 0, '', False))
plGlobal.addParamToGroup('FL Main', TnfxParameter(REC_MainPitch, 'Pitch', 0, '', False))
plGlobal.addParamToGroup('FL Main', TnfxParameter(REC_Tempo, 'Tempo', 0, '', False))

# mixer
plMixer = TnfxChannelPlugin('Mixer')
plMixer.isNative = True
plMixer.addParamToGroup('Main', TnfxParameter(REC_Mixer_Vol, 'Volume'))
plMixer.addParamToGroup('Main', TnfxParameter(REC_Mixer_Pan, 'Pan'))
plMixer.addParamToGroup('Main', TnfxParameter(REC_Mixer_SS, 'Stereo Sep'))
plMixer.addParamToGroup('EQ', TnfxParameter(REC_Mixer_EQ_Gain, 'Lo Gain'))
plMixer.addParamToGroup('EQ', TnfxParameter(REC_Mixer_EQ_Freq, 'Lo Freq'))
plMixer.addParamToGroup('EQ', TnfxParameter(REC_Mixer_EQ_Q, 'Lo Q'))
plMixer.addParamToGroup('EQ', TnfxParameter(REC_Mixer_EQ_Gain+1, 'Mid Gain'))
plMixer.addParamToGroup('EQ', TnfxParameter(REC_Mixer_EQ_Freq+1, 'Mid Freq'))
plMixer.addParamToGroup('EQ', TnfxParameter(REC_Mixer_EQ_Q+1, 'Mid Q'))
plMixer.addParamToGroup('EQ', TnfxParameter(REC_Mixer_EQ_Gain+2, 'Hi Gain'))
plMixer.addParamToGroup('EQ', TnfxParameter(REC_Mixer_EQ_Freq+2, 'Hi Freq'))
plMixer.addParamToGroup('EQ', TnfxParameter(REC_Mixer_EQ_Q+2, 'Hi Q'))







  








