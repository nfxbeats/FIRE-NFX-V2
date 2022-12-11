# name=harmonic scales
# url=
# this is a modified and expanded version of harmonicScales.py from the original Fire script.
#

HARMONICSCALE_LAST = 0      # retain compatibility
HarmonicScaleNamesT = []    # retain compatibility
HarmonicScaleList = []      # retain compatibility

HarmonicScaleGroups = {}
HarmonicScalesLoaded = []

def addScale(scaleName, noteList, groupName = 'UNSORTED'): 
    global HARMONICSCALE_LAST
    global HarmonicScaleNamesT
    global HarmonicScaleList
    HarmonicScaleList.append(noteList)
    HarmonicScalesLoaded.append(noteList)
    HarmonicScaleNamesT.append(scaleName)
    if(groupName in HarmonicScaleGroups.keys()):
        HarmonicScaleGroups[groupName].append(noteList)
    else:
        HarmonicScaleGroups[groupName] = [noteList]
    HARMONICSCALE_LAST = len(HarmonicScaleList)-1
    return HarmonicScaleNamesT[-1], HarmonicScaleList[-1], HARMONICSCALE_LAST

def GetScaleNoteCount(scale):
    Result = 0
    for n in range(0, 13):
        if HarmonicScaleList[scale][ n] != -1:
            Result += 1
    return Result

def IsNoteInScale(note, scale):
    c = GetScaleNoteCount(scale)
    for n in range(0, c + 1):
        if (note % 12) == HarmonicScaleList[scale][ n]:
            return True
    return False

def IsRootNote(note, scale, offset):
    return ((offset - note) % 12) == HarmonicScaleList[scale][ 0]

def IsBlackKey(note):
    return (note % 12) in [1, 3, 6, 8, 10]

def BuildNoteGrid(grid, sizeX, sizeY, baseNote, baseOctave, scale, rowNoteOffset = 3, bottomToTop = True):
    currentNote = 0
    octaveOffset = 0
    nextRowNote = 0
    for j in range(0, sizeY):
        for i in range(0, sizeX):
            if bottomToTop:
                y = sizeY - j - 1
            else:
                y = j
            grid[i][y] = baseNote + ((baseOctave + octaveOffset) * 12) + HarmonicScaleList[scale][ currentNote]
            currentNote += 1
            if HarmonicScaleList[scale][ currentNote] == -1:
                currentNote = 0;
                octaveOffset += 1

        octaveOffset = 0;
        nextRowNote += rowNoteOffset
        currentNote = nextRowNote
        if currentNote >= GetScaleNoteCount(scale):
            currentNote -= GetScaleNoteCount(scale)
            octaveOffset += 1

def InitScales():
    # Chromatic ALWAYS needs to be first and always needs to be in the list for fireNFX to function properly.
    addScale('Chromatic', [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, -1], '')

    # Define the scales chromatic offsets
    # you can comment or uncomment to remove or add scales.
    #
    #addScale('Ionian', [0, 2, 4, 5, 7, 9, 11, -1, -1, -1, -1, -1, -1])
    addScale('Major-ION', [0, 2, 4, 5, 7, 9, 11, -1, -1, -1, -1, -1, -1], 'Faves')
    addScale('Maj-Penta', [0, 2, 4, 7, 9, -1, -1, -1, -1, -1, -1, -1, -1], 'Faves')
    addScale('Minor-AEO', [0, 2, 3, 5, 7, 8, 10, -1, -1, -1, -1, -1, -1], 'Faves')
    addScale('Min-Penta', [0, 3, 5, 7, 10, -1, -1, -1, -1, -1, -1, -1, -1], 'Faves')
    # addScale('Min-Harmonic',  [0, 2, 3, 5, 7, 8, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Min-Melodic',   [0, 2, 3, 5, 7, 9, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Whole Tone', [0, 2, 4, 6, 8, 10, -1, -1, -1, -1, -1, -1, -1])
    # addScale('Diminished', [0, 2, 3, 5, 6, 8, 9, 11, -1, -1, -1, -1, -1])
    # addScale('Japinsen', [0,1, 5, 7, 10, -1, -1, -1, -1, -1, -1, -1, -1])
    # addScale('Major BeBop', [0, 2, 4, 5, 7, 8, 9, 11, -1, -1, -1, -1, -1])
    # addScale('Dominant BeBop', [0,2,4,5,7,9,10,11,-1,-1,-1,-1,-1])
    addScale('Blues', [0, 3, 5, 6, 7, 10, -1, -1, -1, -1, -1, -1, -1])
    # addScale('Arabian', [0, 2, 4, 5, 6, 8, 10, -1, -1, -1, -1, -1, -1])
    # addScale('ArabicOrig', [0, 1, 4, 5, 7, 8, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Enigmatic', [0, 1, 4, 6, 8, 10, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Neopolitan', [0, 1, 3, 5, 7, 8, 11, -1, -1, -1, -1, -1, -1])
    # addScale('NeopolitanOrig', [0, 1, 3, 5, 7, 9, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Neap. Minor', [0, 1, 3, 5, 7, 8, 10, -1, -1, -1, -1, -1, -1])
    # addScale('Neap. Minor Orig', [0, 1, 3, 5, 7, 8, 11, -1, -1, -1, -1, -1, -1])
    addScale('Gypsy', [0, 2, 3, 6, 7, 8, 11, -1, -1, -1, -1, -1, -1], 'Ethnic')
    # addScale('DORIAN', [0, 2, 3, 5, 7, 9, 10, -1, -1, -1, -1, -1, -1])
    # addScale('DOR #4', [0, 2, 3, 6, 7, 9, 10, -1, -1, -1, -1, -1, -1])
    # addScale('DOR B2', [0, 1, 3, 5, 6, 8, 9, -1, -1, -1, -1, -1, -1])
    addScale('PHRYGIAN', [0, 1, 3, 5, 7, 8, 10, -1, -1, -1, -1, -1, -1], 'MODES')
    addScale('FLAM PHRYGIAN', [0, 1, 3, 4, 5, 7, 8, 10, -1, -1, -1, -1, -1], 'MODES')
    # addScale('LYDIAN', [0, 2, 4, 6, 7, 9, 11, -1, -1, -1, -1, -1, -1])
    # addScale('LYD #9', [0, 3, 4, 6, 7, 9, 11, -1, -1, -1, -1, -1, -1])
    # addScale('LYD B7', [0, 2, 4, 6, 7, 9, 10, -1, -1, -1, -1, -1, -1])
    # addScale('MIXO', [0, 2, 4, 5, 7, 9, 10, -1, -1, -1, -1, -1, -1])
    # addScale('MIXO B6', [0, 2, 4, 5, 7, 8, 10, -1, -1, -1, -1, -1, -1])
    # addScale('LOCRIAN', [0, 1, 3, 5, 6, 8, 10, -1, -1, -1, -1, -1, -1])
    # addScale('LOC 2', [0, 2, 3, 5, 6, 8, 10, -1, -1, -1, -1, -1, -1])
    # addScale('LOC 6', [0, 1, 3, 5, 6, 9, 10, -1, -1, -1, -1, -1, -1])

    # addScale('6-Tone Symmetrical', [0, 1, 4, 5, 8, 9, -1, -1, -1, -1, -1, -1, -1])
    # addScale('8-Tone Spanish', [0, 1, 3, 4, 5, 6, 8, 10, -1, -1, -1, -1, -1])
    # addScale('Altered', [0, 1, 3, 4, 6, 8, 10, -1, -1, -1, -1, -1, -1])
    # addScale('Altered Bb7', [0, 1, 3, 4, 6, 8, 9, -1, -1, -1, -1, -1, -1])
    # addScale('Augm. Ionian', [0, 2, 4, 5, 8, 9, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Augm. Lydian', [0, 2, 4, 6, 8, 9, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Augmented', [0, 3, 4, 7, 8, 11, -1, -1, -1, -1, -1, -1, -1])
    # addScale('Balinese', [0, 1, 3, 6, 8, -1, -1, -1, -1, -1, -1, -1, -1])
    # addScale('Byzantine', [0, 1, 4, 5, 7, 8, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Chinese', [0, 4, 6, 7, 11, -1, -1, -1, -1, -1, -1, -1, -1])
    # addScale('Dim. Half-Wholetone', [0, 1, 3, 4, 6, 7, 9, 10, -1, -1, -1, -1, -1])
    # addScale('Dim. Lydian', [0, 2, 3, 6, 7, 9, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Dim. Whole-Halftone', [0, 2, 3, 5, 6, 8, 9, 11, -1, -1, -1, -1, -1])
    # addScale('Double Harmonic', [0, 1, 4, 5, 7, 8, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Egyptian', [0, 2, 5, 7, 10, -1, -1, -1, -1, -1, -1, -1, -1])
    # addScale('Hindu', [0, 2, 4, 5, 7, 8, 10, -1, -1, -1, -1, -1, -1])
    # addScale('Hirajoshi', [0, 2, 3, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1])
    # addScale('Hungarian Major', [0, 3, 4, 6, 7, 9, 10, -1, -1, -1, -1, -1, -1])
    # addScale('Ichikosucho', [0, 2, 4, 5, 6, 7, 9, 11, -1, -1, -1, -1, -1])
    # addScale('Kumoi', [0, 2, 3, 7, 9, -1, -1, -1, -1, -1, -1, -1, -1])
    # addScale('Leading Whole Tone', [0, 2, 4, 6, 8, 10, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Major Phrygian', [0, 1, 4, 5, 7, 8, 10, -1, -1, -1, -1, -1, -1])
    # addScale('Minor Lydian', [0, 2, 4, 6, 7, 8, 10, -1, -1, -1, -1, -1, -1])

    # addScale('Mohammedan', [0, 2, 3, 5, 7, 8, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Mongolian', [0, 2, 4, 7, 9, -1, -1, -1, -1, -1, -1, -1, -1])
    # addScale('Natural Minor', [0, 2, 3, 5, 7, 8, 10, -1, -1, -1, -1, -1, -1])
    # addScale('Neap. Major', [0, 1, 3, 5, 7, 9, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Overtone', [0, 2, 4, 6, 7, 9, 10, -1, -1, -1, -1, -1, -1])
    # addScale('Pelog', [0, 1, 3, 7, 8, -1, -1, -1, -1, -1, -1, -1, -1])
    # addScale('Persian', [0, 1, 4, 5, 6, 8, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Prometheus', [0, 2, 4, 6, 9, 10, -1, -1, -1, -1, -1, -1, -1])
    # addScale('Prometheus Neap.', [0, 1, 4, 6, 9, 10, -1, -1, -1, -1, -1, -1, -1])
    # addScale('Purvi Theta', [0, 1, 4, 6, 7, 8, 11, -1, -1, -1, -1, -1, -1])
    # addScale('Todi Theta', [0, 1, 3, 6, 7, 8, 11, -1, -1, -1, -1, -1, -1])
    

InitScales()
print('{} scales loaded.'.format(len(HarmonicScaleList)))

