import general
from midi import *
import channels
import mixer
from older.OBS_midi import REC_SetChanged

def getCurrChanIdx(): # backwards compatibility
    return channels.selectedChannel()

def SetNativeParam(offset, value):
    return general.processRECEvent(offset, value, REC_SetAll)  # REC_SetAll forces the refresh...

def GetNativeParam(offset):
    return general.processRECEvent(offset, 0, REC_GetValue)

def SetChannelFXParam(offset, value, chanNum = -1):
    if(chanNum == -1):
        chanNum = channels.selectedChannel()
    recEventID = channels.getRecEventId(chanNum)    
    return general.processRECEvent(recEventID + offset, value, REC_SetAll) # REC_SetAll forces the refresh...

def GetChannelFXParam(offset, chanNum = -1):
    if(chanNum == -1):
        chanNum = channels.selectedChannel()
    recEventID = channels.getRecEventId(chanNum)    
    return general.processRECEvent(recEventID + offset, 0, REC_GetValue)

def SetMixerParam(offset, value, trkNum = -1):
    if(trkNum == -1):
        trkNum = mixer.trackNumber() 
    recEventID = channels.getRecEventId(trkNum)    
    return general.processRECEvent(recEventID + offset, value, REC_SetAll) # REC_SetAll forces the refresh...

def GetMixerParam(offset, trkNum = -1):
    if(trkNum == -1):
        trkNum = getCurrChanIdx()
    recEventID = channels.getRecEventId(trkNum)    
    return general.processRECEvent(recEventID + offset, 0, REC_GetValue)
