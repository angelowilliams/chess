import copy

class ChessPiece:
    horizontalSquareOrderList = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']

    def __init__(self, startPosition, gameBoard, playerColor, movementPatternLists):
        self.position = startPosition
        self.gameBoard = gameBoard
        self.playerColor = playerColor
        # Movement patterns are organized in a list of lists. The nested lists are a line of movement, like all of a Rook's
        # movement along one file in one direction. A rook would have 4 nested lists. A queen would have 8.
        self.movementPatternLists = movementPatternLists
        self.gameBoard.positionMap[self.position] = self
        self.positionsBeingAttackedByPiece = []

    def movePiece(self, positionToMoveTo, pieceCollidedWith=False):
        self.gameBoard.whiteInCheck = False
        self.gameBoard.blackInCheck = False
        if isinstance(self, PawnPiece):
            self.isAtStartingPosition = False
        if pieceCollidedWith:
            self.gameBoard.pieceList.remove(pieceCollidedWith)
        del(self.gameBoard.positionMap[self.position])
        self.gameBoard.positionMap[positionToMoveTo] = self
        self.position = positionToMoveTo

        for chessPiece in self.gameBoard.pieceList:
            chessPiece.positionsBeingAttackedByPiece = chessPiece.findPotentialMoves()

        oppositeKing = (self.gameBoard.blackKing if self.playerColor == "White" else self.gameBoard.whiteKing)
        if oppositeKing.checkIfInCheck():
           if self.playerColor == "White":
               self.gameBoard.blackInCheck = True
           else:
               self.gameBoard.whiteInCheck = True

        if self.gameBoard.whiteInCheck or self.gameBoard.blackInCheck:
            if self.playerColor == "White":
                if self.gameBoard.checkIfCheckmate("Black"):
                    self.gameBoard.isBlackInCheckmate = True
            else:
                if self.gameBoard.checkIfCheckmate("White"):
                    self.gameBoard.isWhiteInCheckmate = True
        else:
            if self.playerColor == "White":
                if self.gameBoard.checkIfStalemate("Black"):
                    self.gameBoard.isStalemate = True
            else:
                if self.gameBoard.checkIfStalemate("White"):
                    self.gameBoard.isStalemate = True

        return

    def checkCollisionWithOtherPiece(self, positionToCheck):
        for chessPiece in self.gameBoard.pieceList:
            if chessPiece.position == positionToCheck:
                return chessPiece
        return False

    def findNewPositionAfterMovement(self, horizontalAmountOfSquares, verticalAmountOfSquares, startPosition=None):
        if startPosition is None:
            startPosition = self.position
        xPosition = startPosition[0]
        xPositionIndex = ChessPiece.horizontalSquareOrderList.index(xPosition)
        xPositionIndex += horizontalAmountOfSquares
        if xPositionIndex > 7 or xPositionIndex < 0:
            return False
        xPosition = ChessPiece.horizontalSquareOrderList[xPositionIndex]

        yPosition = int(startPosition[1])
        yPosition += verticalAmountOfSquares
        if yPosition > 8 or yPosition < 1:
            return False

        return f"{xPosition}{yPosition}"

    def findPotentialMoves(self, startPosition=None, checkIfInCheck=True):
        if startPosition is None:
            startPosition = self.position
        potentialMoveList = []
        for movementPatternList in self.movementPatternLists:
            for movementPattern in movementPatternList:
                potentialMove = self.findNewPositionAfterMovement(movementPattern[0], movementPattern[1], startPosition=startPosition)
                if potentialMove:
                    collidedPiece = self.checkCollisionWithOtherPiece(potentialMove)
                    if collidedPiece:
                        if self.playerColor == collidedPiece.playerColor:
                            break
                        kingToCheck = (self.gameBoard.whiteKing if self.playerColor == "White" else self.gameBoard.blackKing)
                        if kingToCheck.checkIfInCheckAfterMove(self, (potentialMove, collidedPiece)):
                            break
                        else:
                            potentialMoveList.append((potentialMove, collidedPiece))
                    else:
                        kingToCheck = (self.gameBoard.whiteKing if self.playerColor == "White" else self.gameBoard.blackKing)
                        if kingToCheck.checkIfInCheckAfterMove(self, (potentialMove, collidedPiece)):
                            continue
                        else:
                            potentialMoveList.append((potentialMove, collidedPiece))
                else:
                    break
        return potentialMoveList


class PawnPiece(ChessPiece):
    def __init__(self, startPosition, gameBoard, playerColor):
        super(PawnPiece, self).__init__(startPosition, gameBoard, playerColor, None)
        self.isAtStartingPosition = True

    def findPotentialMoves(self, startPosition=None, checkIfInCheck=True):
        if startPosition is None:
            startPosition = self.position

        potentialMoveList = []
        if self.playerColor == "White":
            forwardDirection = 1
        else:
            forwardDirection = -1
        potentialMove = self.findNewPositionAfterMovement(0, 1 * forwardDirection, startPosition=startPosition)
        if potentialMove:
            isCollision = self.checkCollisionWithOtherPiece(potentialMove)
            if not isCollision:
                kingToCheck = (self.gameBoard.whiteKing if self.playerColor == "White" else self.gameBoard.blackKing)
                if kingToCheck.checkIfInCheckAfterMove(self, (potentialMove, isCollision)):
                    pass
                else:
                    potentialMoveList.append((potentialMove, isCollision))

                if self.isAtStartingPosition:
                    potentialMove = self.findNewPositionAfterMovement(0, 2 * forwardDirection, startPosition=startPosition)
                    if potentialMove:
                        isCollision = self.checkCollisionWithOtherPiece(potentialMove)
                        if not isCollision:
                            kingToCheck = (self.gameBoard.whiteKing if self.playerColor == "White" else self.gameBoard.blackKing)
                            if kingToCheck.checkIfInCheckAfterMove(self, (potentialMove, isCollision)):
                                pass
                            else:
                                potentialMoveList.append((potentialMove, isCollision))

        for horizontalSquaresAwayFromPosition in [-1, 1]:
            potentialMove = self.findNewPositionAfterMovement(horizontalSquaresAwayFromPosition, 1 * forwardDirection, startPosition=startPosition)
            if potentialMove:
                isCollision = self.checkCollisionWithOtherPiece(potentialMove)
                if isCollision:
                    if self.playerColor == isCollision.playerColor:
                        continue
                    kingToCheck = (self.gameBoard.whiteKing if self.playerColor == "White" else self.gameBoard.blackKing)
                    if kingToCheck.checkIfInCheckAfterMove(self, (potentialMove, isCollision)):
                        continue
                    else:
                        potentialMoveList.append((potentialMove, isCollision))

        return potentialMoveList


class KingPiece(ChessPiece):
    movementPattern = [[(0, 1)], [(1, 1)], [(1, 0)], [(1, -1)],
                        [(0, -1)], [(-1, -1)], [(-1, 0)], [(-1, 1)]]

    def __init__(self, startPosition, gameBoard, playerColor):
        super(KingPiece, self).__init__(startPosition, gameBoard, playerColor, KingPiece.movementPattern)

    def checkIfInCheck(self):
        for movementPattern in QueenPiece.movementPattern:
            collidedPiece = self.checkIfCollisionAlongMovementPattern(self.position, movementPattern)
            if isinstance(collidedPiece, QueenPiece):
                return True
        for movementPattern in RookPiece.movementPattern:
            collidedPiece = self.checkIfCollisionAlongMovementPattern(self.position, movementPattern)
            if isinstance(collidedPiece, RookPiece):
                return True
        for movementPattern in BishopPiece.movementPattern:
            collidedPiece = self.checkIfCollisionAlongMovementPattern(self.position, movementPattern)
            if isinstance(collidedPiece, BishopPiece):
                return True
        for movementPattern in KnightPiece.movementPattern:
            collidedPiece = self.checkIfCollisionAlongMovementPattern(self.position, movementPattern)
            if isinstance(collidedPiece, KnightPiece):
                return True
        for movementPattern in KingPiece.movementPattern:
            collidedPiece = self.checkIfCollisionAlongMovementPattern(self.position, movementPattern)
            if isinstance(collidedPiece, KingPiece):
                return True
        if self.playerColor == "White":
            for movementPattern in [[(-1, 1)], [(1, 1)]]:
                collidedPiece = self.checkIfCollisionAlongMovementPattern(self.position, movementPattern)
                if isinstance(collidedPiece, PawnPiece):
                    return True
        else:
            for movementPattern in [[(-1, -1)], [(1, -1)]]:
                collidedPiece = self.checkIfCollisionAlongMovementPattern(self.position, movementPattern)
                if isinstance(collidedPiece, PawnPiece):
                    return True

    def checkIfCollisionAlongMovementPattern(self, startPosition, movementPattern):
        horizontalPosition = ChessPiece.horizontalSquareOrderList.index(startPosition[0])
        verticalPosition = int(startPosition[1])

        for move in movementPattern:
            horizontalPositionToCheck = horizontalPosition + move[0]
            verticalPositionToCheck = verticalPosition + move[1]
            if horizontalPositionToCheck < 0 or \
                horizontalPositionToCheck > 7 or \
                verticalPositionToCheck < 1 or \
                verticalPositionToCheck > 8:
                break
            positionToCheck = f"{ChessPiece.horizontalSquareOrderList[horizontalPositionToCheck]}{verticalPositionToCheck}"
            for piece in self.gameBoard.pieceList:
                if piece.position == positionToCheck:
                    if piece.playerColor != self.playerColor:
                        return piece
                    return False

        return False

    def checkIfInCheckAfterMove(self, pieceToMove, potentialMove):
        gameBoard = copy.deepcopy(self.gameBoard)
        pieceList = gameBoard.pieceList
        collidedPiece = False
        for chessPiece in pieceList:
            if chessPiece.position == pieceToMove.position:
                pieceToMove = chessPiece
            if potentialMove[1]:
                if chessPiece.position == potentialMove[1].position:
                    collidedPiece = chessPiece

        if collidedPiece:
            pieceList.remove(collidedPiece)
        pieceToMove.position = potentialMove[0]

        if self.playerColor == "White":
            kingPiece = gameBoard.whiteKing
        else:
            kingPiece = gameBoard.blackKing

        result = kingPiece.checkIfInCheck()

        return result


class KnightPiece(ChessPiece):
    movementPattern = [[(1, 2)],
                         [(2, 1)],
                         [(2, -1)],
                         [(1, -2)],
                         [(-1, -2)],
                         [(-2, -1)],
                         [(-2, 1)],
                         [(-1, 2)]]
    def __init__(self, startPosition, gameBoard, playerColor):
        super(KnightPiece, self).__init__(startPosition, gameBoard, playerColor, KnightPiece.movementPattern)


class BishopPiece(ChessPiece):
    movementPattern = [[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
                     [(1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7)],
                     [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)],
                     [(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7)]]
    def __init__(self, startPosition, gameBoard, playerColor):
        super(BishopPiece, self).__init__(startPosition, gameBoard, playerColor, BishopPiece.movementPattern)


class RookPiece(ChessPiece):
    movementPattern = [[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)],
                     [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                     [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)],
                     [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)]]
    def __init__(self, startPosition, gameBoard, playerColor):
        super(RookPiece, self).__init__(startPosition, gameBoard, playerColor, RookPiece.movementPattern)


class QueenPiece(ChessPiece):
    movementPattern = [[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)],
                     [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                     [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)],
                     [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)],
                     [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
                     [(1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7)],
                     [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)],
                     [(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6),  (-7, 7)]]
    def __init__(self, startPosition, gameBoard, playerColor):
        super(QueenPiece, self).__init__(startPosition, gameBoard, playerColor, QueenPiece.movementPattern)


class GameBoard:
    def __init__(self):
        self.boardDepth = 1
        self.moveList = []
        self.pieceList = []
        self.playerToMoveNext = "White"
        self.positionMap = {}
        self.whiteInCheck = False
        self.blackInCheck = False
        self.isWhiteInCheckmate = False
        self.isBlackInCheckmate = False
        self.isStalemate = False

        self.initializePieces()

        for chessPiece in self.pieceList:
            if isinstance(chessPiece, KingPiece):
                if chessPiece.playerColor == "White":
                    self.whiteKing = chessPiece
                else:
                    self.blackKing = chessPiece

        for chessPiece in self.pieceList:
            chessPiece.positionsBeingAttackedByPiece = chessPiece.findPotentialMoves()

    def checkIfPlayerHasNoPotentialMoves(self, playerColor):
        for chessPiece in self.pieceList:
            if chessPiece.playerColor == playerColor:
                if len(chessPiece.positionsBeingAttackedByPiece) > 0:
                    return False
        return True

    def checkIfCheckmate(self, playerColor):
        if playerColor == "White":
            inCheck = self.whiteInCheck
        else:
            inCheck = self.blackInCheck
        if inCheck:
            if self.checkIfPlayerHasNoPotentialMoves(playerColor):
                return True
        return False

    def checkIfStalemate(self, playerColor):
        if playerColor == "White":
            inCheck = self.whiteInCheck
        else:
            inCheck = self.blackInCheck
        if not inCheck:
            if self.checkIfPlayerHasNoPotentialMoves(playerColor):
                return True
        return False

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
                          KingPiece("e1", self, "White"),
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
                          KingPiece("e8", self, "Black"),
                          BishopPiece("f8", self, "Black"),
                          KnightPiece("g8", self, "Black"),
                          RookPiece("h8", self, "Black")]