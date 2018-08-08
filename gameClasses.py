class ChessPiece():
    horizontalSquareOrderList = ['a', 'b', 'c', 'd', 'e', 'f', 'g', ' h']

    def __init__(self, startPosition, gameBoard, playerColor, movementPatternLists):
        position = startPosition
        gameBoard = gameBoard
        playerColor = playerColor
        # Movement patterns are organized in a list of lists. The nested lists are a line of movement, like all of a Rook's
        # movement along one file in one direction. A rook would have 4 nested lists. A queen would have 8.
        movementPatternLists = None

    def movePiece(self, positionToMoveTo, pieceCollidedWith=False):
        if pieceCollidedWith:
            del(self.gameBoard[pieceCollidedWith])
        self.gameBoard[self] = positionToMoveTo
        self.position = positionToMoveTo

    def checkCollisionWithOtherPiece(self, positionToCheck):
        for chessPiece in self.gameBoard:
            if chessPiece.position == positionToCheck:
                return chessPiece
            else:
                return False

    def findNewPositionAfterMovement(self, horizontalAmountOfSquares, verticalAmountOfSquares):
        xPosition = self.position[0]
        xPositionIndex = ChessPiece.horizontalSquareOrderList.index(xPosition)
        xPositionIndex += horizontalAmountOfSquares
        if xPositionIndex > 7 or xPositionIndex < 0:
            return False
        xPosition = ChessPiece.horizontalSquareOrderList[xPositionIndex]

        yPosition = self.position[1]
        yPosition += verticalAmountOfSquares
        if yPosition > 8 or yPosition < 1:
            return False

        return (xPosition, yPosition)

    def findPotentialMoves(self):
        potentialMoveList = []
        for movementPatternList in self.movementPatternLists:
            for movementPattern in movementPatternList:
                potentialMove = self.findNewPositionAfterMovement(movementPattern[0], movementPattern[1])
                if potentialMove:
                    isCollision = self.checkCollisionWithOtherPieces(potentialMove)
                    potentialMoveList.append((potentialMove, isCollision))
                    if isCollision:
                        break
                else:
                    break
        return potentialMoveList


class PawnPiece(ChessPiece):
    def __init__(self, startPosition, gameBoard, playerColor):
        super().__init__(startPosition, gameBoard, playerColor)
        isAtStartingPosition = True

    def findPotentialMoves(self):
        potentialMoveList = []
        if self.playerColor == "White":
            forwardDirection = 1
        else:
            forwardDirection = -1
        potentialMove = self.findNewPositionAfterMovement(0, 1 * forwardDirection)
        if potentialMove:
            isCollision = self.checkCollisionWithOtherPieces(potentialMove)
            if not isCollision:
                potentialMoveList.append(potentialMove, isCollision)
                if self.isAtStartingPosition:
                    potentialMove = self.findNewPositionAfterMovement(0, 2 * forwardDirection)
                    if potentialMove:
                        if not isCollision:
                            potentialMoveList.append(potentialMove, isCollision)

        for horizontalSquaresAwayFromPosition in [-1, 1]:
            potentialMove = self.findNewPositionAfterMovement(horizontalSquaresAwayFromPosition, 1 * forwardDirection)
            if potentialMove:
                isCollision = self.checkCollisionWithOtherPieces(potentialMove)
                if isCollision:
                    potentialMoveList.append(potentialMove, isCollision)

        return potentialMoveList


class KnightPiece(ChessPiece):
    def __init__(self, startPosition, gameBoard, playerColor):
        super().__init__(startPosition, gameBoard, playerColor, [[(1, 3)],
                                                                 [(3, 1)],
                                                                 [(3, -1)],
                                                                 [(1, -3)],
                                                                 [(-1, -3)],
                                                                 [(-3, -1)],
                                                                 [(-3, 1)],
                                                                 [(-1, 3)]])

class BishopPiece(ChessPiece):
    def __init__(self, startPosition, gameBoard, playerColor):
        super().__init__(startPosition, gameBoard, playerColor, [[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
                                                                 [(1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7)],
                                                                 [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)],
                                                                 [(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7)]])

class RookPiece(ChessPiece):
    def __init__(self, startPosition, gameBoard, playerColor):
        super().__init__(startPosition, gameBoard, playerColor, [[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)],
                                                                 [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                                                                 [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)],
                                                                 [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)]])
class QueenPiece(ChessPiece):
    def __init__(self, startPosition, gameBoard, playerColor):
        super().__init__(startPosition, gameBoard, playerColor, [[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)],
                                                                 [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                                                                 [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)],
                                                                 [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)],
                                                                 [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
                                                                 [(1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7)],
                                                                 [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)],
                                                                 [(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6),  (-7, 7)]])

class GameBoard():
    def __init__(self):
        moveList = []
        pieceList = []
        playerToMoveNext = "White"
        self.initializePieces()

    def initializePieces(self):
        self.pieceList = [PawnPiece("a2", self, "White"),
                          PawnPiece("b2", self, "White"),
                          PawnPiece("c2", self, "White"),
                          PawnPiece("d2", self, "White"),
                          PawnPiece("e2", self, "White"),
                          PawnPiece("f2", self, "White"),
                          PawnPiece("g2", self, "White"),
                          PawnPiece("h2", self, "White"),
                          RookPiece("a1", self, "White"),
                          KnightPiece("b1", self, "White"),
                          BishopPiece("c1", self, "White"),
                          QueenPiece("d1", self, "White"),
                          PawnPiece("e1", self, "White"),
                          BishopPiece("f1", self, "White"),
                          KnightPiece("g1", self, "White"),
                          RookPiece("h1", self, "White"),
                          PawnPiece("a7", self, "Black"),
                          PawnPiece("b7", self, "Black"),
                          PawnPiece("c7", self, "Black"),
                          PawnPiece("d7", self, "Black"),
                          PawnPiece("e7", self, "Black"),
                          PawnPiece("f7", self, "Black"),
                          PawnPiece("g7", self, "Black"),
                          PawnPiece("h7", self, "Black"),
                          RookPiece("a8", self, "Black"),
                          KnightPiece("b8", self, "Black"),
                          BishopPiece("c8", self, "Black"),
                          QueenPiece("d8", self, "Black"),
                          PawnPiece("e8", self, "Black"),
                          BishopPiece("f8", self, "Black"),
                          KnightPiece("g8", self, "Black"),
                          RookPiece("h8", self, "Black")]

