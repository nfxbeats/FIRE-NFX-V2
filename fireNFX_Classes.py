#
# Various class definitions
#
from fireNFX_Defs import *
import plugins
import channels

def clonePluginParams(srcPlugin, destPlugin):
    # enumerate the plugins list. no deepcopy :(  
    for param in srcPlugin.Parameters:
        newParam = TnfxParameter(param.Offset, param.Caption, param.Value, param.ValueStr, param.Bipolar, param.StepsAfterZero)
        if(newParam.Caption in ['?', ''] and newParam.Offset > -1):
            if(plugins.isValid(channels.selectedChannel())):
                newParam.Caption = plugins.getParamName(newParam.Offset, channels.selectedChannel(), -1) # -1 denotes not mixer

        destPlugin.addParamToGroup(param.GroupName, newParam)
    for knob in range(4):
        param1 = srcPlugin.User1Knobs[knob] 
        param2 = srcPlugin.User2Knobs[knob] 
        newParam1 = TnfxParameter(param1.Offset, param1.Caption, param1.Value, param1.ValueStr, param1.Bipolar, param1.StepsAfterZero)
        newParam2 = TnfxParameter(param2.Offset, param2.Caption, param2.Value, param2.ValueStr, param2.Bipolar, param2.StepsAfterZero)

        if(param1.Caption in ['?', ''] and param1.Offset > -1):
            if(plugins.isValid(channels.selectedChannel())):
                newParam1.Caption = plugins.getParamName(param1.Offset, channels.selectedChannel(), -1) # -1 denotes not mixer

        if(param2.Caption in ['?', ''] and param2.Offset > -1):
            if(plugins.isValid(channels.selectedChannel())):
                newParam2.Caption = plugins.getParamName(param2.Offset, channels.selectedChannel(), -1) # -1 denotes not mixer

        destPlugin.assignParameterToUserKnob(KM_USER1, knob, newParam1 )
        destPlugin.assignParameterToUserKnob(KM_USER2, knob, newParam2 )
    return destPlugin

cpGlobal = 0
cpChannel = 1
cpChannelPlugin = 2
cpMixer = 3
cpMixerPlugin = 4
class TnfxChannelPlugin:
    def __init__(self, name, username = "", type = cpChannelPlugin):
        self.Name = name
        self.PluginName = name
        self.UserName = username
        self.ParameterGroups = {} # { groupName: [TnfxParameters] }
        self.Parameters = []
        #self.GroupName = ''
        self.TweakableParam = None
        self.User1Knobs = []
        self.User2Knobs = []
        self.isNative = False
        self.AlwaysRescan = True
        self.FLChannelType = -1
        self.PresetGroups = {}
        self.Type = type
        for i in range(4): # pre-allocate these to have 4 each
            p = TnfxParameter(-1,'',i,'',False) # offset = -1 to identify it's unassigned
            self.User1Knobs.append(p)
            self.User2Knobs.append(p)
    def copy(self):
        newPlugin = TnfxChannelPlugin(self.PluginName)
        clonePluginParams(self, newPlugin)
        return newPlugin

    def getID(self):
        chanName= channels.getChannelName(channels.selectedChannel())
        presetName = "NONE"
        if(plugins.isValid(channels.selectedChannel())):
            presetName = plugins.getName(channels.selectedChannel(), -1, 6, -1)
        return "{}-{}-{}".format(self.PluginName, chanName, presetName)    

    def getParamNamesForGroup(self, groupName):
        params = []
        for p in self.ParameterGroups[groupName]:
            params.append(p.Caption)
        return params

    def getParamFromOffset(self, offset):
        for param in self.Parameters:
            if(param.Offset == offset):
                return param
        return None

    def getGroupNames(self):
        return list(self.ParameterGroups.keys())
        
    def addParamToGroup(self, groupName, nfxParameter):
        nfxParameter.GroupName = groupName 
        self.Parameters.append(nfxParameter)            # add to root level Param list
        if(groupName in self.ParameterGroups.keys()):   # add to group 
            self.ParameterGroups[groupName].append(nfxParameter)
        else:
            self.ParameterGroups[groupName] = [nfxParameter]

    def assignKnobsFromParamGroup(self, groupName):
        offslist = []
        for param in self.ParameterGroups[groupName]:
            offslist.append(param.Offset)
        if(len(offslist) > 0):
            self.assignKnobs(offslist)
            return True
        return False

    def getCurrentKnobParamOffsets(self):
        u1 = []
        u2 = []
        res = []
        for i in range(4): # pre-allocate these to have 4 each
            if(self.User1Knobs[i].Offset > -1):
                u1.append(self.User1Knobs[i].Offset)
            if(self.User2Knobs[i].Offset > -1):
                u2.append(self.User2Knobs[i].Offset)
        res.extend(u1)
        res.extend(u2)
        return res 
        
    def assignParameterToUserKnob(self, knobMode, knobIdx, nfxParameter):
        #print('ass', knobMode, knobIdx, nfxParameter.Offset )
        if(4 < knobIdx < 0):
            return 
        if(knobMode == KM_USER1):
            self.User1Knobs[knobIdx] = nfxParameter
        elif(knobMode == KM_USER2):
            self.User2Knobs[knobIdx] = nfxParameter

    def assignOffsetToUserKnob(self, usermode, knob, paramOffs):
        self.assignParameterToUserKnob(usermode, knob, self.getParamFromOffset(paramOffs) )

    def assignKnobsFromParamList(self, paramList):
        offsetList = []
        for param in paramList:
            offsetList.append(param.Offset)
            #print('appended offset', param.Offset)
        self.assignKnobs(offsetList)

    def assignKnobs(self, offsetList, PresetGroup = ''):
        #print('offsets', offsetList)
        res = 0
        for idx, offs in enumerate(offsetList):
            if idx > 7: 
                return idx
            km = KM_USER1
            ko = idx
            if idx > 3: 
                km = KM_USER2
                ko = idx - 4
            if(offs < 0) or (self.getParamFromOffset(offs) == None):
                self.assignParameterToUserKnob(km, ko, None)
            else:
                self.assignOffsetToUserKnob(km, ko, offs)
            res = idx + 1
        if(PresetGroup != ''):
            self.PresetGroups[PresetGroup] = res
        return res

class TnfxParameter:
    def __init__(self, offset, caption, value=0, valuestr='', bipolar= False, stepsAfterZero = 0):
        self.Offset = offset 
        self.Caption = caption
        self.Value = value
        self.ValueStr = valuestr
        self.Bipolar = bipolar 
        self.StepsAfterZero = stepsAfterZero
        self.GroupName = ''
    def __str__(self):
        # 0, 'Chord Type',  0, 'Movable', False
        return "{}, '{}', {}, '{}'".format(self.Offset, self.Caption, self.Value, self.ValueStr)
    def getFullName(self):
        return self.GroupName + "-" + self.Caption 
    def updateCaption(self, caption):
        self.Caption = caption 

class TnfxPadMode:
    def __init__(self, name, mode, btnId = IDStepSeq,  isAlt = False):
        self.Name = name 
        self.Mode = mode
        self.ButtonID = btnId
        self.IsAlt = isAlt 
        self.NavSet = TnfxNavigationSet(nsDefault)
        self.AltNavSet = TnfxNavigationSet(nsDefault)
        self.AllowedNavSets = [nsDefault]
        self.AllowedNavSetIdx = 0
        self.LayoutIdx = 0

class TnfxProgressStep:
    def __init__(self, padIdx, color, songpos, abspos, barnum, selected = False):
        self.PadIndex = padIdx
        self.Color = color
        self.SongPos = songpos
        self.SongPosAbsTicks = abspos
        self.Selected = selected
        self.BarNumber = barnum 
        self.Markers = list()
    def __str__(self):
        return "ProgressStep PadIdx: {}, SongPos: {}%, {} ticks, Bar #{}".format(self.PadIndex, self.SongPos, self.SongPosAbsTicks, self.BarNumber)

class TnfxMarker:
    def __init__(self, number, name, ticks):
        self.Number = number
        self.Name = name
        self.SongPosAbsTicks = ticks
    def __str__(self):
        return "Marker #{}, {}, SongPos: {}".format(self.Number, self.Name, self.SongPosAbsTicks)

class TnfxMixer:
    def __init__(self, flIdx, name):
        self.Name = name 
        self.FLIndex = flIdx
        self.Muted = 0

class TnfxChannel:
    def __init__(self, flIdx, name):
        self.Name = name 
        self.FLIndex = flIdx 
        self.ItemIndex = flIdx
        self.Mixer = TnfxMixer(-1, "")
        self.LoopSize = 0
        self.Muted = 0
        self.PadAColor = 0
        self.DimA = 3
        self.PadBColor = 0
        self.DimB = 3 
        self.ChannelType = -1
        self.GlobalIndex = -1
        self.ShowChannelEditor = -1
        self.ShowCSForm = -1
        self.ShowPianoRoll = -1
        self.Selected = False 
    def __str__(self):
        return "Channel #{} - {} - Selected: {}".format(self.FLIndex, self.Name, self.Selected)        

nsNone = 0
nsDefault = 1
nsScale = 2
nsUDLR = 3
nsDefaultDrum = 4
nsDefaultDrumAlt = 5
nsChannel = 6
nsPlaylist = 7
nsMixer = 8
nsPianoRoll = 9

class TnfxNavigationSet:
    def __init__(self, navSet):
        self.NavSetID = navSet
        self.Index = -1
        self.ChanNav = False
        self.ScaleNav = False
        self.SnapNav = False
        self.NoteRepeat = False
        self.OctaveNav = False
        self.LayoutNav = False
        self.PresetNav = False
        self.UDLRNav = False 
        self.MacroNav = True 
        self.NoNav = False
        if navSet == nsDefault:
            self.ChanNav = True
            self.SnapNav = True
            self.PresetNav = True
        elif navSet == nsDefaultDrum:
            self.ChanNav = True
            self.SnapNav = True
            self.NoteRepeat = True
            self.PresetNav = True
        elif navSet == nsDefaultDrumAlt:
            self.ChanNav = True
            self.LayoutNav = True 
            self.OctaveNav = True
            self.PresetNav = True
        elif(navSet == nsScale):
            self.ChanNav = True
            self.ScaleNav = True
        elif(navSet == nsUDLR):
            self.UDLRNav = True
        elif(navSet == nsNone):
            self.MacroNav = False
            self.NoNav = True 


class TnfxPattern:
    def __init__(self, flIdx, name):
        self.Name = name 
        self.FLIndex = flIdx 
        self.ItemIndex = flIdx - 1
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
        self.Selected = False 
    def __str__(self):
        return "Pattern #{} - {} - Selected: {}".format(self.FLIndex, self.Name, self.Selected)

class TnfxPlaylistTrack:
    def __init__(self, flIdx, name, color):
        self.FLIndex = flIdx
        self.Name = name
        self.Color = color
        self.Muted = -1
        self.Selected = False 
        self.ChanIdx = -1
        self.MixerIdx = -1
        
class TnfxNoteInfo:
    def __init__(self):
        self.MIDINote = -1          # the midi Note for this pad
        self.ChordNum = -1          # the chord . ie 1 = I, 2 = ii, etc
        self.IsRootNote = False     #
        self.Highlight = False      #


#pad types
ptUndefined = -1
ptPattern = 0
ptChannel = 1
ptPlaylistTrack = 2
ptNote = 3
ptDrum = 4
ptMacro = 5
ptNav = 6
ptProgress = 7

class TnfxPadMap:
    def __init__(self, padIndex, flIndex, color, tag):
        self.PadIndex = padIndex    # the pad num 0..63
        self.FLIndex = flIndex
        self.Color = color          # the color 
        self.Pressed = -1 
#        self.MIDINote = -1
        self.Tag = tag
        self.ItemType = ptUndefined 
        self.ItemObject = object()
        self.ItemIndex = -1
        self.NoteInfo = TnfxNoteInfo()

class TnfxMacro:
    def __init__(self, name, color, command = None):
        self.Name = name
        self.PadIndex = -1
        self.PadColor = color 
        self.Execute = command

class TnfxColorMap:
    def __init__(self, padIndex, color, dimFactor):
        self.PadIndex = padIndex
        self.PadColor = color
        self.DimFactor = dimFactor
        self.R = 0
        self.G = 0
        self.B = 0
        self.Anim = ''
        self.AnimStep = -1

class TnfxMenuItems:
    def __init__(self, text, object = None) -> None:
        self.Level = 0
        self.Parent = None
        self.Text = text
        self.Value = 0
        self.Selected = False
        self.Object = object
        self.SubItems = []
    def __str__(self):
        return "TnfxMenuItem( {}, {}, {} ) - {} subitem(s) - parent: {}".format(self.Level, self.Text, self.Value, len(self.SubItems), self.Parent )
    def addSubItem(self, item):
        exists = False
        item.Level = self.Level + 1
        item.Parent = self 
        item.Value = len(self.SubItems)
        for idx, mi in enumerate(self.SubItems):
            #if(item.Text == mi.Text) and (idx == mi.Value): 
            if (id(item) == id(mi)):
                exists = True
                break
        if(not exists):
            self.SubItems.append(item)

_rd3d2PotParams = {} # 'PluginName':[param1, .., paramX]
_rd3d2PotParamOffsets = {} 
try:
   # from native_pot_parameters import PluginParameter, native_plugin_parameters as npp 
   # until rd3d2 approves my submitted code I will use the local file.
    from rd3d2_pot_params import PluginParameter, native_plugin_parameters as npp
    if(len(npp) < 1): # no error, but no list either
        print('rd3d2 Pot Parameters found, but the dictionary did not load.')    
    else:
        print('rd3d2 Pot Parameters found. {} plugins available in the dictionary.'.format(len(npp)))
        for plugin in npp.keys():
            _rd3d2PotParams[plugin] = []
            # for param in npp[plugin]:
            #     if param != None:
            #         bipolar = param.deadzone_centre != None
            #         name = param.name
            #         if name == '':
            #             name = '?' 
            #         nfxParam = TnfxParameter(param.index, name, 0, '', bipolar)
            #         _rd3d2PotParams[plugin].append(nfxParam)
            #         _rd3d2PotParamOffsets[plugin].append(param.index)
        print('rd3d2 Pot Parameters conversion. {} plugins converted.'.format(len(_rd3d2PotParams)))
except ImportError:
    print('rd3d2 Pot Parameters NOT found.')# Failed to import - assume they don't have custom settings


