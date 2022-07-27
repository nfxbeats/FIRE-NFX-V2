from fireNFX_Classes import *
#   PluginName:  FLEX
#   ParamCount:  45
#-----------------------------------------------------------------
plFLEX = TnfxChannelPlugin('FLEX')
plFLEX.AlwaysRescan = False

# Macros section. The name will change for these dependng on the preset
plFLEX.addParamToGroup('MACROS', TnfxParameter(10, '?', 0, '100%', False) )
plFLEX.addParamToGroup('MACROS', TnfxParameter(11, '?', 0, '0%', False) )
plFLEX.addParamToGroup('MACROS', TnfxParameter(12, '?', 0, '0%', False) )
plFLEX.addParamToGroup('MACROS', TnfxParameter(13, '?', 0, '100%', False) )
plFLEX.addParamToGroup('MACROS', TnfxParameter(14, '?', 0, '50%', False) )
plFLEX.addParamToGroup('MACROS', TnfxParameter(15, '?', 0, '0%', False) )
plFLEX.addParamToGroup('MACROS', TnfxParameter(16, '?', 0, '0%', False) )
plFLEX.addParamToGroup('MACROS', TnfxParameter(17, '?', 0, '0%', False) )

# First filter section
plFLEX.addParamToGroup('FILTER', TnfxParameter(18, 'Cutoff', 0, '50%', False) )
plFLEX.addParamToGroup('FILTER', TnfxParameter(19, 'Env Amt', 0, '50%', False) )
plFLEX.addParamToGroup('FILTER', TnfxParameter(20, 'Resonance', 0, '50%', False) )

# Enveleopes section
plFLEX.addParamToGroup('VOL ENV', TnfxParameter(0, 'Attack', 0, '50%', True) )
plFLEX.addParamToGroup('VOL ENV', TnfxParameter(1, 'Hold', 0, '50%', True) )
plFLEX.addParamToGroup('VOL ENV', TnfxParameter(2, 'Decay', 0, '50%', True) )
plFLEX.addParamToGroup('VOL ENV', TnfxParameter(3, 'Sustain', 0, '50%', True) )
plFLEX.addParamToGroup('VOL ENV', TnfxParameter(4, 'Release', 0, '50%', True) )

plFLEX.addParamToGroup('FILT ENV', TnfxParameter(5, 'Attack', 0, '50%', True) )
plFLEX.addParamToGroup('FILT ENV', TnfxParameter(6, 'Hold', 0, '50%', True) )
plFLEX.addParamToGroup('FILT ENV', TnfxParameter(7, 'Decay', 0, '50%', True) )
plFLEX.addParamToGroup('FILT ENV', TnfxParameter(8, 'Sustain', 0, '50%', True) )
plFLEX.addParamToGroup('FILT ENV', TnfxParameter(9, 'Release', 0, '50%', True) )

# Master Filter section
plFLEX.addParamToGroup('MASTER FILT', TnfxParameter(40, 'On/Off', 0, 'On', False, 1) )
plFLEX.addParamToGroup('MASTER FILT', TnfxParameter(21, 'Cutoff', 0, '98%', False) )
plFLEX.addParamToGroup('MASTER FILT', TnfxParameter(22, 'Resonance', 0, '0%', False) )
plFLEX.addParamToGroup('MASTER FILT', TnfxParameter(23, 'Type', 0, 'High pass 6', False) ) # was missing a name

# Delay section
plFLEX.addParamToGroup('DELAY', TnfxParameter(37, 'On/Off', 0, 'On', False) )
plFLEX.addParamToGroup('DELAY', TnfxParameter(24, 'Type', 0, 'Ping pong', False) ) # was missing a name
plFLEX.addParamToGroup('DELAY', TnfxParameter(25, 'Mix', 0, '20%', False) )
plFLEX.addParamToGroup('DELAY', TnfxParameter(26, 'Time', 0, '4:1', False) )
plFLEX.addParamToGroup('DELAY', TnfxParameter(27, 'Feedback', 0, '63%', False) )
plFLEX.addParamToGroup('DELAY', TnfxParameter(28, 'Mod', 0, '50%', False) )
plFLEX.addParamToGroup('DELAY', TnfxParameter(29, 'Color', 0, '50%', False) )

# Reverb Section
plFLEX.addParamToGroup('REVERB', TnfxParameter(38, 'On/Off', 0, 'Off', False) )
plFLEX.addParamToGroup('REVERB', TnfxParameter(31, 'Decay', 0, '50%', False) )
plFLEX.addParamToGroup('REVERB', TnfxParameter(32, 'Size', 0, '50%', False) )
plFLEX.addParamToGroup('REVERB', TnfxParameter(30, 'Mix', 0, '50%', False) )
plFLEX.addParamToGroup('REVERB', TnfxParameter(34, 'Color', 0, '16%', False) )
plFLEX.addParamToGroup('REVERB', TnfxParameter(33, 'Mod', 0, '0%', False) )
plFLEX.addParamToGroup('REVERB', TnfxParameter(44, 'Mod Spd', 0, '0%', False) )

# Limiter
plFLEX.addParamToGroup('LIMITER', TnfxParameter(41, 'On/Off', 0, 'On', False) )
plFLEX.addParamToGroup('LIMITER', TnfxParameter(35, 'PRE', 0, '50%', False) )
plFLEX.addParamToGroup('LIMITER', TnfxParameter(42, 'Mix', 0, '47%', False) )
plFLEX.addParamToGroup('LIMITER', TnfxParameter(43, 'Type', 0, 'Limiter', False) ) # was missing a name

# General
plFLEX.addParamToGroup('GENERAL', TnfxParameter(36, 'Output volume', 0, '57%', False) )
plFLEX.addParamToGroup('GENERAL', TnfxParameter(39, 'Pitch', 0, '+0 cent', True) )

# set up the predetermined USER1 and USER2 knob parameters to link to the 8 macros
for knobIdx in range(4):
    plFLEX.assignParameterToUserKnob(KM_USER1, knobIdx, TnfxParameter(10 + knobIdx, '?', 0, '', False) )
    plFLEX.assignParameterToUserKnob(KM_USER2, knobIdx, TnfxParameter(14 + knobIdx, '?', 0, '', False) )
#-----------------------------------------------------------------

