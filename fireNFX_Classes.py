from fireNFX_Defs import *

class TnfxPlugin:
    def __init__(self, name):
        self.Name = name
        self.Parameters = list() #

class TnfxParameter:
    def __init__(self, offset, caption, value, valuestr, bipolar, stepsize = 0, maxvalue = 0):
        self.Offset = offset 
        self.Caption = caption
        self.Value = value
        self.ValueStr = valuestr
        self.Bipolar = bipolar 
        self.StepSize = stepsize
        self.MaxValue = maxvalue

class TnfxMixer:
    def __init__(self, flIdx, name):
        self.Name = name 
        self.FLIndex = flIdx
        self.SelectPad = -1
        self.MutePad = -1
        self.Muted = 0

class TnfxChannel:
    def __init__(self, flIdx, name):
        self.Name = name 
        self.FLIndex = flIdx 
        self.Mixer = TnfxMixer(-1, "")
        self.LoopSize = 0
        self.Muted = 0
        self.Color = 0 
        self.ChannelType = -1
        self.GlobalIndex = -1
        self.ShowChannelEditor = -1
        self.ShowCSForm = -1
        self.ShowPianoRoll = -1

class TnfxPattern:
    def __init__(self, flIdx, name):
        self.Name = name 
        self.FLIndex = flIdx 
        self.Channels = list()
        self.Mixer = TnfxMixer(-1, "")
        self.Muted = 0
        self.ShowChannelEditor = 0
        self.ShowPianoRoll = 0
        self.ShowChannelSettings = 0
        self.Color = 0x000000
        self.MutePreset1 = 0
        self.MutePreset2 = 1
        self.FilterParam = -1
        self.ResParam = -1
        self.PluginName = ''
        self.Parameters = list() 
        self.ParamPages = []
        self.ParamPageIdx = -1

class TnfxPlaylistTrack:
    def __init__(self, flIdx, name, color):
        self.FLIndex = flIdx
        self.Name = name
        self.Color = color
        self.Muted = -1
        self.Selected = False 
        


class TnfxColorMap:
    def __init__(self, padIndex, color, dimFactor):
        self.PadIndex = padIndex
        self.PadColor = color
        self.DimFactor = dimFactor
        self.R = 0
        self.G = 0
        self.B = 0

class TnfxNoteInfo:
    def __init__(self):
        self.MIDINote = -1          # the midi Note for this pad
        self.ChordNum = -1             # the chord . ie 1 = I, 2 = ii, etc
        self.IsRootNote = False     #
        self.Highlight = False      #

class TnfxPadMap:
    def __init__(self, padIndex, flIndex, color, tag):
        self.PadIndex = padIndex          # the pad num 0..63
        self.FLIndex = flIndex
        self.Color = color        # the color 
        self.Pressed = -1 
#        self.MIDINote = -1
        self.Tag = tag
        self.ItemIndex = -1
        self.NoteInfo = TnfxNoteInfo()

class TnfxMacro:
    def __init__(self, name, color):
        self.Name = name
        self.PadIndex = -1
        self.Color = color 


    