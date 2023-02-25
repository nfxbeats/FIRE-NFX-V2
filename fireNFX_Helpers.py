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

def SetChannelPluginParam(offset, value, chanNum = -1):
    if(chanNum == -1):
        chanNum = channels.selectedChannel()
    recEventID = channels.getRecEventId(chanNum) + midi.REC_Chan_Plugin_First
    return general.processRECEvent(recEventID + offset, value, midi.REC_SetAll) # REC_SetAll forces the refresh...

def GetChannelPluginParam(offset, chanNum = -1):
    if(chanNum == -1):
        chanNum = channels.selectedChannel()
    recEventID = channels.getRecEventId(chanNum) + midi.REC_Chan_Plugin_First
    return general.processRECEvent(recEventID + offset, 0, midi.REC_GetValue)

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
def SetMixerGenParamVal(offset, value, trkNum = -1, slotIndex = 0):
    # usage: SetMixerGenParamVal(midi.REC_Mixer_Vol, 11400, 1) to set the volume of mixer channel # 1 to 11400
    if(trkNum == -1):
        trkNum = mixer.trackNumber() 
    recEventID = mixer.getTrackPluginId(trkNum, slotIndex)
    return general.processRECEvent(recEventID + offset, value, midi.REC_SetAll) # REC_SetAll forces the refresh...

def GetMixerGenParamVal(offset, trkNum = -1, slotIndex = 0):
    # usage: GetMixerGenParamVal(midi.REC_Mixer_Vol, 1) to get the volume of mixer channel #1
    if(trkNum == -1):
        trkNum = mixer.trackNumber()
    recEventID = mixer.getTrackPluginId(trkNum, slotIndex)
    return general.processRECEvent(recEventID + offset, 0, midi.REC_GetValue)


# GetMixerGenParamVal((REC_Plug_General_First, 0, 0)
#ScanParams(REC_Plug_General_First + (REC_ItemRange*2), 2, True)

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

def GetMixerSlotPluginNames(trkNum = -1, slotIdx = 0):
    if(trkNum == -1):
        trkNum = mixer.trackNumber()
    if(plugins.isValid(trkNum, slotIdx)):
        name = plugins.getPluginName(trkNum, slotIdx, 0)
        uname = plugins.getPluginName(trkNum, slotIdx, 1)
        uname = uname.partition(" (")[0].strip()
        return name, uname
    else:
        return 'INVALID', 'INVALID'

# Utility
def ScanParams(offsetStart, scanLength = 10, includeBlank = False):  
    # usage: ScanParams(midi.REC_Mixer_First, 127) 
    # may crash FL when attempting to scan certain ranges. 
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
