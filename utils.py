# name=Basic functions
# url=

import math

class TRect:
    def __init__(self, left, top, right, bottom):
        self.Top = top
        self.Left = left
        self.Bottom = bottom
        self.Right = right

    def Width(self):
        return self.Right - self.Left

    def Height(self):
        return self.Bottom - self.Top

class TClipLauncherLastClip:
    def __init__(self, trackNum, subNum, flags):
        self.TrackNum = trackNum
        self.SubNum = subNum
        self.Flags = flags

def RectOverlapEqual(R1, R2):
  return (R1.Left <= R2.Right) & (R1.Right >= R2.Left) & (R1.Top <= R2.Bottom) & (R1.Bottom >= R2.Top)

def RectOverlap(R1, R2):
  return  (R1.Left < R2.Right) & (R1.Right > R2.Left) & (R1.Top < R2.Bottom) & (R1.Bottom > R2.Top)

def Limited(Value, Min, Max):
    if Value <= Min:
        res = Min
    else:
        res = Value
    if res > Max:
        res = Max
    return res

def InterNoSwap(X, A, B):
    return (X >= A) & (X <= B)

def DivModU(A, B):
    C = A % B
    return (A // B), C

def SwapInt(A, B):
    return B, A

def Zeros(value, nChars, c = '0'):
    if value < 0:
        Result = str(-value)
        Result = '-' + c * (nChars - len(Result)) + Result
    else:
        Result = str(value)
        Result = c * (nChars - len(Result)) + Result
    return Result

def Zeros_Strict(value, nChars, c ='0'):
    if value < 0:
        Result = str(-value)
        Result = '-' +  c * (nChars - len(Result) - 1) + Result
    else:
        Result = str(value)
        Result = c * (nChars - len(Result)) + Result
    if len(Result) > nChars:
        Result = Result[len(Result) - nChars]
    return Result

def Sign(value):
    if value < 0: 
        return -1
    elif value == 0:
        return 0
    else:   
        return 1

SignBitPos_64 = 63
SignBit_64 = 1 << SignBitPos_64
SignBitPos_Nat = SignBitPos_64

def SignOf(value):
    if value == 0:
        return 0
    elif value < 0:
        return -1
    else:   
        return 1

def KnobAccelToRes2(Value):
    n = abs(Value)
    if n > 1:
        res = n ** 0.75
    else:
        res = 1
    return res

def OffsetRect(R, dx, dy):
  R.Left = R.Left + dx
  R.Top = R.Top + dy
  R.Right = R.Right + dx
  R.Bottom = R.Bottom + dy

def RGBToHSV(R, G, B):
    Min = min(min(R, G), B)
    V = max(max(R, G), B)

    Delta = V - Min

    if V == 0:
        S = 0
    else:
        S = Delta / V

    if S == 0.0:
        H = 0.0 
    else:
        if R == V:
            H = 60.0 * (G - B) / Delta
        elif G == V:
            H = 120.0 + 60.0 * (B - R) / Delta
        elif B == V:
            H = 240.0 + 60.0 * (R - G) / Delta

        if H < 0.0:
            H = H + 360.0

    return H, S, V

def RGBToHSVColor(Color):
    r = ((Color & 0xFF0000) >> 16) / 255
    g = ((Color & 0x00FF00) >> 8) / 255
    b = ((Color & 0x0000FF) >> 0) / 255
    H, S, V = RGBToHSV(r, g, b)
    return H, S, V

def HSVtoRGB(H, S, V):
    hTemp = 0
    if S == 0.0:
        R = V
        G = V
        B = V
    else:
        if H == 360.0:
            hTemp = 0.0
        else:
            hTemp = H

        hTemp = hTemp / 60
        i = math.trunc(hTemp)
        f = hTemp - i

        p = V * (1.0 - S)
        q = V * (1.0 - (S * f))
        t = V * (1.0 - (S * (1.0 - f)))

        if i == 0:
            R = V
            G = t
            B = p
        elif i == 1:
            R = q
            G = V
            B = p
        elif i == 2:
            R = p
            G = V
            B = t
        elif i == 3:
            R = p
            G = q
            B = V
        elif i == 4:
            R = t
            G = p
            B = V
        elif i == 5:
            R = V
            G = p
            B = q
    return R, G, B

NoteNameT = ('C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B')

def GetNoteName(NoteNum):
    NoteNum += 1200
    return NoteNameT[NoteNum % 12] + str((NoteNum // 12) - 100)

def ColorToRGB(Color):
    return (Color >> 16) & 0xFF, (Color >> 8) & 0xFF, Color & 0xFF

def RGBToColor(R,G,B):
    return (R << 16) | (G << 8) | B

def FadeColor(StartColor, EndColor, Value):
  rStart, gStart, bStart = ColorToRGB(StartColor)
  rEnd, gEnd, bEnd = ColorToRGB(EndColor)
  ratio = Value / 255
  rEnd = round(rStart * (1 - ratio) + (rEnd * ratio))
  gEnd = round(gStart * (1 - ratio) + (gEnd * ratio))
  bEnd = round(gStart * (1 - ratio) + (bEnd * ratio))
  return RGBToColor(rEnd, gEnd, bEnd)

def LightenColor(Color, Value):
    r, g, b = ColorToRGB(Color)
    ratio = Value / 255
    return RGBToColor(round(r + (1.0 - r) * ratio), round(g + (1.0 - g) * ratio) , round(b + (1.0 - b) * ratio))

def VolTodB(Value):
    Value = (math.exp(Value * math.log(11)) - 1) * 0.1
    if Value == 0:
        return 0
    return round(math.log10(Value) * 20, 1)

