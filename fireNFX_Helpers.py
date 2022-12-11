# 
# Helper for FL Global and PLugin Parameter handling.
#
import general
import device 
import midi
import channels
import mixer
import plugins 


# Global
def SetNativeParam(offset, value):
    return general.processRECEvent(offset, value, midi.REC_SetAll)  # REC_SetAll forces the refresh...

def GetNativeParam(offset):
    return general.processRECEvent(offset, 0, midi.REC_GetValue)

# Channel
def getCurrChanIdx(): # backwards compatibility
    return channels.selectedChannel()

def SetChannelFXParam(offset, value, chanNum = -1):
    if(chanNum == -1):
        chanNum = channels.selectedChannel()
    recEventID = channels.getRecEventId(chanNum)    
    return general.processRECEvent(recEventID + offset, value, midi.REC_SetAll) # REC_SetAll forces the refresh...

def GetChannelFXParam(offset, chanNum = -1):
    if(chanNum == -1):
        chanNum = channels.selectedChannel()
    recEventID = channels.getRecEventId(chanNum)    
    return general.processRECEvent(recEventID + offset, 0, midi.REC_GetValue)

# MIXER
def SetMixerGenParamVal(offset, value, trkNum = -1):
    # usage: SetMixerGenParamVal(midi.REC_Mixer_Vol, 11400, 1) to set the volume of mixer channel # 1 to 11400
    if(trkNum == -1):
        trkNum = mixer.trackNumber() 
    recEventID = mixer.getTrackPluginId(trkNum, 0)
    return general.processRECEvent(recEventID + offset, value, midi.REC_SetAll) # REC_SetAll forces the refresh...

def GetMixerGenParamVal(offset, trkNum = -1):
    # usage: GetMixerGenParamVal(midi.REC_Mixer_Vol, 1) to get the volume of mixer channel #1
    if(trkNum == -1):
        trkNum = mixer.trackNumber()
    recEventID = mixer.getTrackPluginId(trkNum, 0)
    return general.processRECEvent(recEventID + offset, 0, midi.REC_GetValue)

def SetMixerPluginParamVal(offset, value, trkNum = 0, slotIdx = 0):
    if(trkNum == -1):
        trkNum = mixer.trackNumber() 
    res = plugins.setParamValue(value, offset, trkNum, slotIdx)
    return res

def GetMixerPluginParamVal(offset, trkNum = 0, slotIdx = 0):
    if(trkNum == -1):
        trkNum = mixer.trackNumber()
    val = plugins.getParamValue(offset, trkNum, slotIdx)
    return val

def GetMixerSlotPluginName(trkNum = -1, slotIdx = 0):
    if(trkNum == -1):
        trkNum = mixer.trackNumber()
    if(plugins.isValid(trkNum, slotIdx)):
        return plugins.getPluginName(trkNum, slotIdx, 0), plugins.getPluginName(trkNum, slotIdx, 1)
    else:
        return 'INVALID', 'INVALID'

def GetMixerSlotEffects(trkNum = -1):
    # return a dict of  slotNum:'Plguin Name'
    res = {}
    for fx in range(10): # 0-9
        name, uname = GetMixerSlotPluginName(trkNum, fx)
        if(name != 'INVALID'):
            res[fx+1] = name
    return res

# Utility
def ScanParams(offsetStart, scanLength = 10, includeBlank = False):  
    # usage: ScanParams(midi.REC_Mixer_First, 127) 
    for offset in range(scanLength):
        try:
            offs = offset + offsetStart
            val = GetNativeParam(offs)
            if val == midi.REC_InvalidID:
                val = 'Invalid'
            linked = device.getLinkedParamName(offs)
            strval = device.getLinkedValueString(offs)
            if includeBlank or (len(strval) != 0): # (str(val) != '0'):
                print('offset {} + {}, value "{}", link {}, strval "{}"'.format(offsetStart, offset, val, linked, strval))
        except Exception as e:
            print('Offset +{}, Scan Exception: {}'.format(offset, e))

# classes
class GlobalSettingControl:
    def setTempo(self, val):
        return SetNativeParam(midi.REC_Tempo, val)
    def getTempo(self, ):
        return GetNativeParam(midi.REC_Tempo)
    def setVolume(self, val):
        return SetNativeParam(midi.REC_MainVol, val)
    def getVolume(self):
        return GetNativeParam(midi.REC_MainVol)
    def setPitch(self, val):
        return SetNativeParam(midi.REC_MainPitch, val)
    def getPitch(self):
        return GetNativeParam(midi.REC_MainPitch)
    def setSwing(self, val):
        return SetNativeParam(midi.REC_MainShuffle, val)
    def getSwing(self):
        return GetNativeParam(midi.REC_MainShuffle)
flmain = GlobalSettingControl()