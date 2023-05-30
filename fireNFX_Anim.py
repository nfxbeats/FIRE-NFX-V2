class PadColor:
    def __init__(self, color, dim):
        self.color = color
        self.dim = dim 

    def __repr__(self):
        return f'(Color: {hex(self.color)}, dim: {self.dim})'        

class Traveler:
    def __init__(self, color, x=0, y=0, width=4, height=4):
        self.color = color 
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.tail = {}
        self.tailSize = 3

    def __repr__(self):
        return f'({self.x}, {self.y})'
    
    def stay(self):
        self.addToTail(False)

    def move_up(self, updateTail = True):
        self.y = (self.y - 1) % self.height
        if updateTail:
            self.addToTail()

    def move_down(self, updateTail = True):
        self.y = (self.y + 1) % self.height
        if updateTail:
            self.addToTail()

    def move_left(self, updateTail = True):
        self.x = (self.x - 1) % self.width
        if updateTail:
            self.addToTail()

    def move_right(self, updateTail = True):
        self.x = (self.x + 1) % self.width
        if updateTail:
            self.addToTail()
    
    def addToTail(self, addPosition = True):
        # todo process the tail.
        localTail = self.tail.copy()
        for padOffs, gen in localTail.items():
            if self.tail[padOffs] <= self.tailSize:
                self.tail[padOffs] = gen + 1
            else:
                del self.tail[padOffs]
        #add new 
        if addPosition:
            self.tail[self.getPadIndex()] = 0 # gen 0

    def getValueMatrix(self):
        mtx = CreateMatrix(self.height, self.width, 0)
        mtx[self.y][self.x] = 1
        return mtx 
        
    def getPadMatrix(self):
        mtx = CreateMatrix(self.height, self.width)
        return mtx 
        
    def getPadIndex(self, mirrorX = False, mirrorY = False):
        x = self.x
        y = self.y
        if mirrorX:
            x = self.get_mirrored_x()
        if mirrorY:
            y = self.get_mirrored_y()
        return y * self.width + x    
    
    def getPadIndexes(self):
        return self.getPadIndex(False, False),  self.getPadIndex(True, False), self.getPadIndex(False, True), self.getPadIndex(True, True)
        
    def get_mirrored_x(self):
        return self.width - self.x - 1

    def get_mirrored_y(self):
        return self.height - self.y - 1

def MirroredMatrices(matrix):
    # Mirror in x direction
    mirrored_x = [row[::-1] for row in matrix]
    
    # Mirror in y direction
    mirrored_y = matrix[::-1]
    
    # Mirror in x/y direction
    mirrored_xy = [row[::-1] for row in matrix[::-1]]
    
    # Return all four versions of the matrix
    return matrix, mirrored_x, mirrored_y, mirrored_xy

def PadIndexToXY(padIndex, width, height, mirrMode = 0):
    x = padIndex % width
    y = padIndex // width

    if(mirrMode in [1,3]):
        x = width - x - 1

    if(mirrMode in [2,3]):
        y = height - y - 1

    return x, y

def XYToPadIndex(x, y, width):
    return y * width + x    

def GetBankNumber(matrix, offset):
    submatrix = []
    if offset >= 0 and offset < len(matrix[0]):
        start = offset * 4
        for row in matrix:
            submatrix.append(row[start:start+4])
    return submatrix

def Get2x2(matrix, row_offset, col_offset):
    submatrix = []
    if row_offset >= 0 and row_offset < len(matrix) and col_offset >= 0 and col_offset < len(matrix[0]):
        for i in range(row_offset, min(row_offset+2, len(matrix))):
            submatrix.append(matrix[i][col_offset:min(col_offset+2, len(matrix[0]))])
    return submatrix

def SubDivideMatrix(matrix, num_rows, num_cols):
    # return a list of all the matrix sets starting at pad 0, ie 2x2, 4x4, 8x2, etc
    divided_matrices = []
    for row in range(0, len(matrix), num_rows):
        for col in range(0, len(matrix[0]), num_cols):
            divided_matrix = [row[col:col+num_cols] for row in matrix[row:row+num_rows]]
            if( len(divided_matrix[0]) == num_cols ): # only add segments of the requested size, ignore the remainders
                divided_matrices.append(divided_matrix)
    return divided_matrices

def CreateMatrix(rows, cols, initval = None):
    matrix = []
    for i in range(rows):
        row = []
        for j in range(cols):
            if initval == None:
                row.append(i * cols + j)
            else:
                row.append(initval)
        matrix.append(row)
    return matrix

def MirrorMatrix(matrix, mirror_horizontally=True, mirror_vertically=True):
    mirrored_matrix = []
    for row in matrix:
        mirrored_row = row[::-1] if mirror_horizontally else row
        mirrored_matrix.append(mirrored_row)
    mirrored_matrix = mirrored_matrix[::-1] if mirror_vertically else mirrored_matrix
    return mirrored_matrix

def FlattenMatrix(matrix):
    flat_matrix = [element for sublist in matrix for element in sublist]
    return flat_matrix

def FlattenMatrix1(matrices):
    flattened_matrix = []
    for i in range(len(matrices[0])):
        row = []
        for matrix in matrices:
            row.extend(matrix[i])
        flattened_matrix.append(row)
    return flattened_matrix

def QuadrantToBank(matrixA, mirrX, mirrY):
    # matrixA = [ [0,1], [0,0] ]
    if mirrX:
        matrixB = MirrorMatrix(matrixA, True, False)
    else:
        matrixB = matrixA 
    
    if not mirrY:
        matrixC = MirrorMatrix(matrixA, False, True)
    else:
        matrixC = matrixA 
    
    if not mirrX and not mirrY:
        matrixD = MirrorMatrix(matrixA, True, True)
    else:
        matrixD = matrixA 
        
    return FlattenMatrix([matrixA, matrixB, matrixC, matrixD])


_PadMatrix = CreateMatrix(4, 16) # can also be 4, 12 to allow work while macro/nav remains
_BankAMatrix = GetBankNumber(_PadMatrix, 0) # 0-based
_BankBMatrix = GetBankNumber(_PadMatrix, 1) # 0-based
_BankCMatrix = GetBankNumber(_PadMatrix, 2) # 0-based
_BankDMatrix = GetBankNumber(_PadMatrix, 3) # 0-based
_BankList = []
_BankList.append(_BankAMatrix)
_BankList.append(_BankBMatrix)
_BankList.append(_BankCMatrix)
_BankList.append(_BankDMatrix)




    