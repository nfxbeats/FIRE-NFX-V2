print("Loading...")
# name=harmonic scales
# url=

HARMONICSCALE_MAJOR = 0
HARMONICSCALE_HARMONICMINOR = 1
HARMONICSCALE_MELODICMINOR = 2
HARMONICSCALE_WHOLETONE = 3
HARMONICSCALE_DIMINISHED = 4
HARMONICSCALE_MAJORPENTATONIC = 5
HARMONICSCALE_MINORPENTATONIC = 6
HARMONICSCALE_JAPINSEN = 7
HARMONICSCALE_MAJORBEBOP = 8
HARMONICSCALE_DOMINANTBEBOP = 9
HARMONICSCALE_BLUES = 10
HARMONICSCALE_ARABIC = 11
HARMONICSCALE_ENIGMATIC = 12
HARMONICSCALE_NEAPOLITAN = 13
HARMONICSCALE_NEAPOLITANMINOR = 14
HARMONICSCALE_HUNGARIANMINOR = 15
HARMONICSCALE_DORIAN = 16
HARMONICSCALE_PHRYGIAN = 17
HARMONICSCALE_LYDIAN = 18
HARMONICSCALE_MIXOLYDIAN = 19
HARMONICSCALE_AEOLIAN = 20
HARMONICSCALE_LOCRIAN = 21
HARMONICSCALE_CHROMATIC = 22

HARMONICSCALE_LAST = 22

HarmonicScaleNamesT = ['Ionian/Major', 'Harmonic minor', 'Melodic minor', 'Whole tone', 'Diminished', 'Major penta', 'Minor penta', 'Jap in sen', 'Major bebop', 'Dominant bebop', 'Blues', 'Arabic', 'Enigmatic', 'Neapolitan', 'Neap. minor', 'Hungarian minor', 'Dorian', 'Phrygian', 'Lydian', 'Mixolydian', 'Aeolian/Minor', 'Locrian', 'Chromatic']

HarmonicScaleList = [[0 for x in range(13)] for y in range(23)]


def addScale(scaleName, noteList): # addScale('nfx', [9,8,7,6,5,4,3,2,1,0,9,8,7])
    global HARMONICSCALE_LAST
    global HarmonicScaleNamesT
    global HarmonicScaleList
    HarmonicScaleList.append(noteList)
    HarmonicScaleNamesT.append(scaleName)
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

    # Define the scales chromatic offsets
    HarmonicScaleList[HARMONICSCALE_MAJOR][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_MAJOR][ 1] = 2
    HarmonicScaleList[HARMONICSCALE_MAJOR][ 2] = 4
    HarmonicScaleList[HARMONICSCALE_MAJOR][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_MAJOR][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_MAJOR][ 5] = 9
    HarmonicScaleList[HARMONICSCALE_MAJOR][ 6] = 11
    HarmonicScaleList[HARMONICSCALE_MAJOR][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_MAJOR][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_MAJOR][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_MAJOR][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_MAJOR][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_MAJOR][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_HARMONICMINOR][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_HARMONICMINOR][ 1] = 2
    HarmonicScaleList[HARMONICSCALE_HARMONICMINOR][ 2] = 3
    HarmonicScaleList[HARMONICSCALE_HARMONICMINOR][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_HARMONICMINOR][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_HARMONICMINOR][ 5] = 8
    HarmonicScaleList[HARMONICSCALE_HARMONICMINOR][ 6] = 11
    HarmonicScaleList[HARMONICSCALE_HARMONICMINOR][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_HARMONICMINOR][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_HARMONICMINOR][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_HARMONICMINOR][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_HARMONICMINOR][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_HARMONICMINOR][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_MELODICMINOR][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_MELODICMINOR][ 1] = 2
    HarmonicScaleList[HARMONICSCALE_MELODICMINOR][ 2] = 3
    HarmonicScaleList[HARMONICSCALE_MELODICMINOR][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_MELODICMINOR][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_MELODICMINOR][ 5] = 9
    HarmonicScaleList[HARMONICSCALE_MELODICMINOR][ 6] = 11
    HarmonicScaleList[HARMONICSCALE_MELODICMINOR][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_MELODICMINOR][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_MELODICMINOR][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_MELODICMINOR][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_MELODICMINOR][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_MELODICMINOR][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_WHOLETONE][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_WHOLETONE][ 1] = 2
    HarmonicScaleList[HARMONICSCALE_WHOLETONE][ 2] = 4
    HarmonicScaleList[HARMONICSCALE_WHOLETONE][ 3] = 6
    HarmonicScaleList[HARMONICSCALE_WHOLETONE][ 4] = 8
    HarmonicScaleList[HARMONICSCALE_WHOLETONE][ 5] = 10
    HarmonicScaleList[HARMONICSCALE_WHOLETONE][ 6] = -1
    HarmonicScaleList[HARMONICSCALE_WHOLETONE][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_WHOLETONE][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_WHOLETONE][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_WHOLETONE][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_WHOLETONE][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_WHOLETONE][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_DIMINISHED][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_DIMINISHED][ 1] = 2
    HarmonicScaleList[HARMONICSCALE_DIMINISHED][ 2] = 3
    HarmonicScaleList[HARMONICSCALE_DIMINISHED][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_DIMINISHED][ 4] = 6
    HarmonicScaleList[HARMONICSCALE_DIMINISHED][ 5] = 8
    HarmonicScaleList[HARMONICSCALE_DIMINISHED][ 6] = 9
    HarmonicScaleList[HARMONICSCALE_DIMINISHED][ 7] = 11
    HarmonicScaleList[HARMONICSCALE_DIMINISHED][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_DIMINISHED][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_DIMINISHED][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_DIMINISHED][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_DIMINISHED][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_MAJORPENTATONIC][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_MAJORPENTATONIC][ 1] = 2
    HarmonicScaleList[HARMONICSCALE_MAJORPENTATONIC][ 2] = 4
    HarmonicScaleList[HARMONICSCALE_MAJORPENTATONIC][ 3] = 7
    HarmonicScaleList[HARMONICSCALE_MAJORPENTATONIC][ 4] = 9
    HarmonicScaleList[HARMONICSCALE_MAJORPENTATONIC][ 5] = -1
    HarmonicScaleList[HARMONICSCALE_MAJORPENTATONIC][ 6] = -1
    HarmonicScaleList[HARMONICSCALE_MAJORPENTATONIC][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_MAJORPENTATONIC][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_MAJORPENTATONIC][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_MAJORPENTATONIC][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_MAJORPENTATONIC][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_MAJORPENTATONIC][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_MINORPENTATONIC][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_MINORPENTATONIC][ 1] = 3
    HarmonicScaleList[HARMONICSCALE_MINORPENTATONIC][ 2] = 5
    HarmonicScaleList[HARMONICSCALE_MINORPENTATONIC][ 3] = 7
    HarmonicScaleList[HARMONICSCALE_MINORPENTATONIC][ 4] = 10
    HarmonicScaleList[HARMONICSCALE_MINORPENTATONIC][ 5] = -1
    HarmonicScaleList[HARMONICSCALE_MINORPENTATONIC][ 6] = -1
    HarmonicScaleList[HARMONICSCALE_MINORPENTATONIC][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_MINORPENTATONIC][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_MINORPENTATONIC][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_MINORPENTATONIC][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_MINORPENTATONIC][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_MINORPENTATONIC][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_JAPINSEN][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_JAPINSEN][ 1] = 1
    HarmonicScaleList[HARMONICSCALE_JAPINSEN][ 2] = 5
    HarmonicScaleList[HARMONICSCALE_JAPINSEN][ 3] = 7
    HarmonicScaleList[HARMONICSCALE_JAPINSEN][ 4] = 10
    HarmonicScaleList[HARMONICSCALE_JAPINSEN][ 5] = -1
    HarmonicScaleList[HARMONICSCALE_JAPINSEN][ 6] = -1
    HarmonicScaleList[HARMONICSCALE_JAPINSEN][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_JAPINSEN][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_JAPINSEN][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_JAPINSEN][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_JAPINSEN][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_JAPINSEN][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_MAJORBEBOP][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_MAJORBEBOP][ 1] = 2
    HarmonicScaleList[HARMONICSCALE_MAJORBEBOP][ 2] = 4
    HarmonicScaleList[HARMONICSCALE_MAJORBEBOP][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_MAJORBEBOP][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_MAJORBEBOP][ 5] = 8
    HarmonicScaleList[HARMONICSCALE_MAJORBEBOP][ 6] = 9
    HarmonicScaleList[HARMONICSCALE_MAJORBEBOP][ 7] = 11
    HarmonicScaleList[HARMONICSCALE_MAJORBEBOP][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_MAJORBEBOP][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_MAJORBEBOP][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_MAJORBEBOP][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_MAJORBEBOP][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_DOMINANTBEBOP][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_DOMINANTBEBOP][ 1] = 2
    HarmonicScaleList[HARMONICSCALE_DOMINANTBEBOP][ 2] = 4
    HarmonicScaleList[HARMONICSCALE_DOMINANTBEBOP][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_DOMINANTBEBOP][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_DOMINANTBEBOP][ 5] = 9
    HarmonicScaleList[HARMONICSCALE_DOMINANTBEBOP][ 6] = 10
    HarmonicScaleList[HARMONICSCALE_DOMINANTBEBOP][ 7] = 11
    HarmonicScaleList[HARMONICSCALE_DOMINANTBEBOP][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_DOMINANTBEBOP][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_DOMINANTBEBOP][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_DOMINANTBEBOP][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_DOMINANTBEBOP][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_BLUES][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_BLUES][ 1] = 3
    HarmonicScaleList[HARMONICSCALE_BLUES][ 2] = 5
    HarmonicScaleList[HARMONICSCALE_BLUES][ 3] = 6
    HarmonicScaleList[HARMONICSCALE_BLUES][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_BLUES][ 5] = 10
    HarmonicScaleList[HARMONICSCALE_BLUES][ 6] = -1
    HarmonicScaleList[HARMONICSCALE_BLUES][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_BLUES][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_BLUES][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_BLUES][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_BLUES][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_BLUES][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_ARABIC][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_ARABIC][ 1] = 1
    HarmonicScaleList[HARMONICSCALE_ARABIC][ 2] = 4
    HarmonicScaleList[HARMONICSCALE_ARABIC][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_ARABIC][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_ARABIC][ 5] = 8
    HarmonicScaleList[HARMONICSCALE_ARABIC][ 6] = 11
    HarmonicScaleList[HARMONICSCALE_ARABIC][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_ARABIC][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_ARABIC][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_ARABIC][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_ARABIC][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_ARABIC][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_ENIGMATIC][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_ENIGMATIC][ 1] = 1
    HarmonicScaleList[HARMONICSCALE_ENIGMATIC][ 2] = 4
    HarmonicScaleList[HARMONICSCALE_ENIGMATIC][ 3] = 6
    HarmonicScaleList[HARMONICSCALE_ENIGMATIC][ 4] = 8
    HarmonicScaleList[HARMONICSCALE_ENIGMATIC][ 5] = 10
    HarmonicScaleList[HARMONICSCALE_ENIGMATIC][ 6] = 11
    HarmonicScaleList[HARMONICSCALE_ENIGMATIC][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_ENIGMATIC][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_ENIGMATIC][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_ENIGMATIC][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_ENIGMATIC][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_ENIGMATIC][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_NEAPOLITAN][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_NEAPOLITAN][ 1] = 1
    HarmonicScaleList[HARMONICSCALE_NEAPOLITAN][ 2] = 3
    HarmonicScaleList[HARMONICSCALE_NEAPOLITAN][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_NEAPOLITAN][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_NEAPOLITAN][ 5] = 9
    HarmonicScaleList[HARMONICSCALE_NEAPOLITAN][ 6] = 11
    HarmonicScaleList[HARMONICSCALE_NEAPOLITAN][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_NEAPOLITAN][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_NEAPOLITAN][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_NEAPOLITAN][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_NEAPOLITAN][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_NEAPOLITAN][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_NEAPOLITANMINOR][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_NEAPOLITANMINOR][ 1] = 1
    HarmonicScaleList[HARMONICSCALE_NEAPOLITANMINOR][ 2] = 3
    HarmonicScaleList[HARMONICSCALE_NEAPOLITANMINOR][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_NEAPOLITANMINOR][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_NEAPOLITANMINOR][ 5] = 8
    HarmonicScaleList[HARMONICSCALE_NEAPOLITANMINOR][ 6] = 11
    HarmonicScaleList[HARMONICSCALE_NEAPOLITANMINOR][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_NEAPOLITANMINOR][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_NEAPOLITANMINOR][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_NEAPOLITANMINOR][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_NEAPOLITANMINOR][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_NEAPOLITANMINOR][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_HUNGARIANMINOR][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_HUNGARIANMINOR][ 1] = 2
    HarmonicScaleList[HARMONICSCALE_HUNGARIANMINOR][ 2] = 3
    HarmonicScaleList[HARMONICSCALE_HUNGARIANMINOR][ 3] = 6
    HarmonicScaleList[HARMONICSCALE_HUNGARIANMINOR][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_HUNGARIANMINOR][ 5] = 8
    HarmonicScaleList[HARMONICSCALE_HUNGARIANMINOR][ 6] = 11
    HarmonicScaleList[HARMONICSCALE_HUNGARIANMINOR][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_HUNGARIANMINOR][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_HUNGARIANMINOR][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_HUNGARIANMINOR][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_HUNGARIANMINOR][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_HUNGARIANMINOR][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_DORIAN][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_DORIAN][ 1] = 2
    HarmonicScaleList[HARMONICSCALE_DORIAN][ 2] = 3
    HarmonicScaleList[HARMONICSCALE_DORIAN][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_DORIAN][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_DORIAN][ 5] = 9
    HarmonicScaleList[HARMONICSCALE_DORIAN][ 6] = 10
    HarmonicScaleList[HARMONICSCALE_DORIAN][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_DORIAN][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_DORIAN][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_DORIAN][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_DORIAN][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_DORIAN][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_PHRYGIAN][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_PHRYGIAN][ 1] = 1
    HarmonicScaleList[HARMONICSCALE_PHRYGIAN][ 2] = 3
    HarmonicScaleList[HARMONICSCALE_PHRYGIAN][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_PHRYGIAN][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_PHRYGIAN][ 5] = 8
    HarmonicScaleList[HARMONICSCALE_PHRYGIAN][ 6] = 10
    HarmonicScaleList[HARMONICSCALE_PHRYGIAN][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_PHRYGIAN][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_PHRYGIAN][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_PHRYGIAN][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_PHRYGIAN][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_PHRYGIAN][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_LYDIAN][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_LYDIAN][ 1] = 2
    HarmonicScaleList[HARMONICSCALE_LYDIAN][ 2] = 4
    HarmonicScaleList[HARMONICSCALE_LYDIAN][ 3] = 6
    HarmonicScaleList[HARMONICSCALE_LYDIAN][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_LYDIAN][ 5] = 9
    HarmonicScaleList[HARMONICSCALE_LYDIAN][ 6] = 11
    HarmonicScaleList[HARMONICSCALE_LYDIAN][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_LYDIAN][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_LYDIAN][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_LYDIAN][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_LYDIAN][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_LYDIAN][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_MIXOLYDIAN][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_MIXOLYDIAN][ 1] = 2
    HarmonicScaleList[HARMONICSCALE_MIXOLYDIAN][ 2] = 4
    HarmonicScaleList[HARMONICSCALE_MIXOLYDIAN][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_MIXOLYDIAN][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_MIXOLYDIAN][ 5] = 9
    HarmonicScaleList[HARMONICSCALE_MIXOLYDIAN][ 6] = 10
    HarmonicScaleList[HARMONICSCALE_MIXOLYDIAN][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_MIXOLYDIAN][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_MIXOLYDIAN][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_MIXOLYDIAN][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_MIXOLYDIAN][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_MIXOLYDIAN][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_AEOLIAN][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_AEOLIAN][ 1] = 2
    HarmonicScaleList[HARMONICSCALE_AEOLIAN][ 2] = 3
    HarmonicScaleList[HARMONICSCALE_AEOLIAN][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_AEOLIAN][ 4] = 7
    HarmonicScaleList[HARMONICSCALE_AEOLIAN][ 5] = 8
    HarmonicScaleList[HARMONICSCALE_AEOLIAN][ 6] = 10
    HarmonicScaleList[HARMONICSCALE_AEOLIAN][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_AEOLIAN][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_AEOLIAN][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_AEOLIAN][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_AEOLIAN][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_AEOLIAN][ 12] = -1

    HarmonicScaleList[HARMONICSCALE_LOCRIAN][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_LOCRIAN][ 1] = 1
    HarmonicScaleList[HARMONICSCALE_LOCRIAN][ 2] = 3
    HarmonicScaleList[HARMONICSCALE_LOCRIAN][ 3] = 5
    HarmonicScaleList[HARMONICSCALE_LOCRIAN][ 4] = 6
    HarmonicScaleList[HARMONICSCALE_LOCRIAN][ 5] = 8
    HarmonicScaleList[HARMONICSCALE_LOCRIAN][ 6] = 10
    HarmonicScaleList[HARMONICSCALE_LOCRIAN][ 7] = -1
    HarmonicScaleList[HARMONICSCALE_LOCRIAN][ 8] = -1
    HarmonicScaleList[HARMONICSCALE_LOCRIAN][ 9] = -1
    HarmonicScaleList[HARMONICSCALE_LOCRIAN][ 10] = -1
    HarmonicScaleList[HARMONICSCALE_LOCRIAN][ 11] = -1
    HarmonicScaleList[HARMONICSCALE_LOCRIAN][ 12] = -1

    # used internally for chromatic mode
    HarmonicScaleList[HARMONICSCALE_CHROMATIC][ 0] = 0
    HarmonicScaleList[HARMONICSCALE_CHROMATIC][ 1] = 1
    HarmonicScaleList[HARMONICSCALE_CHROMATIC][ 2] = 2
    HarmonicScaleList[HARMONICSCALE_CHROMATIC][ 3] = 3
    HarmonicScaleList[HARMONICSCALE_CHROMATIC][ 4] = 4
    HarmonicScaleList[HARMONICSCALE_CHROMATIC][ 5] = 5
    HarmonicScaleList[HARMONICSCALE_CHROMATIC][ 6] = 6
    HarmonicScaleList[HARMONICSCALE_CHROMATIC][ 7] = 7
    HarmonicScaleList[HARMONICSCALE_CHROMATIC][ 8] = 8
    HarmonicScaleList[HARMONICSCALE_CHROMATIC][ 9] = 9
    HarmonicScaleList[HARMONICSCALE_CHROMATIC][ 10] = 10
    HarmonicScaleList[HARMONICSCALE_CHROMATIC][ 11] = 11
    HarmonicScaleList[HARMONICSCALE_CHROMATIC][ 12] = -1

InitScales()
