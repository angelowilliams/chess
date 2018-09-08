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

    def movePiece(self, positionToMoveTo, pieceCollidedWith=False, castlingMove=False):
        self.gameBoard.whiteInCheck = False
        self.gameBoard.blackInCheck = False
        self.isAtStartingPosition = False
        self.gameBoard.pawnMovedDoubleLastTurn = False
        originalPosition = self.position if isinstance(self, PawnPiece) and pieceCollidedWith else False

        if isinstance(self, PawnPiece):
            if abs(int(self.position[1]) - int(positionToMoveTo[1])) == 2:
                self.gameBoard.pawnMovedDoubleLastTurn = self

        if castlingMove:
            self.gameBoard.positionMap[castlingMove] = pieceCollidedWith
            pieceCollidedWith.position = castlingMove
        elif pieceCollidedWith:
            self.gameBoard.pieceList.remove(pieceCollidedWith)
            self.gameBoard.updatePieceCounters(pieceCollidedWith)
        del(self.gameBoard.positionMap[self.position])
        self.gameBoard.positionMap[positionToMoveTo] = self
        self.position = positionToMoveTo

        if isinstance(self, PawnPiece):
            promotionRank = "8" if self.playerColor == "White" else "1"
            if self.position[1] == promotionRank:
                self.promotePawn()
                if self.playerColor == "White":
                    self.gameBoard.whiteQueenCount += 1
                else:
                    self.gameBoard.blackQueenCount += 1

        oppositeKing = (self.gameBoard.blackKing if self.playerColor == "White" else self.gameBoard.whiteKing)
        if oppositeKing.checkIfInCheck():
           if self.playerColor == "White":
               self.gameBoard.blackInCheck = True
           else:
               self.gameBoard.whiteInCheck = True

        for chessPiece in self.gameBoard.pieceList:
            chessPiece.positionsBeingAttackedByPiece = chessPiece.findPotentialMoves()

        if self.gameBoard.checkIfDraw():
            self.gameBoard.isDraw = True

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
                    self.gameBoard.isDraw = True
            else:
                if self.gameBoard.checkIfStalemate("White"):
                    self.gameBoard.isDraw = True

        self.gameBoard.addMoveToMoveList(self, (positionToMoveTo, pieceCollidedWith, castlingMove), originalPosition=originalPosition)
        print(self.gameBoard.moveList)

        if pieceCollidedWith or isinstance(self, PawnPiece):
            self.gameBoard.movesSinceLastCaptureOrPawnMove = 0
        else:
            self.gameBoard.movesSinceLastCaptureOrPawnMove += 1
        if self.gameBoard.movesSinceLastCaptureOrPawnMove >= 100:
            self.gameBoard.isDraw = True

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
                            potentialMoveList.append((potentialMove, collidedPiece, False))
                            break
                    else:
                        kingToCheck = (self.gameBoard.whiteKing if self.playerColor == "White" else self.gameBoard.blackKing)
                        if kingToCheck.checkIfInCheckAfterMove(self, (potentialMove, collidedPiece)):
                            continue
                        else:
                            potentialMoveList.append((potentialMove, collidedPiece, False))
                else:
                    break

        # Check if castling is a potential move
        if isinstance(self, KingPiece) and \
                self.isAtStartingPosition and \
                not (self.gameBoard.whiteInCheck if self.playerColor == "White" else self.gameBoard.blackInCheck):
            for chessPiece in self.gameBoard.pieceList:
                if isinstance(chessPiece, RookPiece) and \
                        chessPiece.playerColor == self.playerColor and \
                        chessPiece.isAtStartingPosition:

                    canCastle = True
                    castleRank = "1" if self.playerColor == "White" else "8"
                    if chessPiece.position[0] == 'a':
                        positionsToCheck = [f"c{castleRank}", f"d{castleRank}"]
                        # For queen-side castling, the b-file must be checked for a piece, but not for attacking pieces
                        positionToCheckForCollision = [f"b{castleRank}"]
                        kingPositionAfterCastle = f"c{castleRank}"
                        rookPositionAfterCastle = f"d{castleRank}"
                    elif chessPiece.position[0] == 'h':
                        positionsToCheck = [f"f{castleRank}", f"g{castleRank}"]
                        positionToCheckForCollision = []
                        kingPositionAfterCastle = f"g{castleRank}"
                        rookPositionAfterCastle = f"f{castleRank}"

                    for position in positionsToCheck:
                        for piece in self.gameBoard.pieceList:
                            if piece.position == position:
                                canCastle = False
                            if position in piece.positionsBeingAttackedByPiece:
                                canCastle = False
                    for position in positionToCheckForCollision:
                        if piece.position == position:
                            canCastle = False

                    if canCastle:
                        potentialMoveList.append((kingPositionAfterCastle, chessPiece, rookPositionAfterCastle))


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
                    potentialMoveList.append((potentialMove, isCollision, False))

                if self.isAtStartingPosition:
                    potentialMove = self.findNewPositionAfterMovement(0, 2 * forwardDirection, startPosition=startPosition)
                    if potentialMove:
                        isCollision = self.checkCollisionWithOtherPiece(potentialMove)
                        if not isCollision:
                            kingToCheck = (self.gameBoard.whiteKing if self.playerColor == "White" else self.gameBoard.blackKing)
                            if kingToCheck.checkIfInCheckAfterMove(self, (potentialMove, isCollision)):
                                pass
                            else:
                                potentialMoveList.append((potentialMove, isCollision, False))

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
                        potentialMoveList.append((potentialMove, isCollision, False))

        if self.gameBoard.pawnMovedDoubleLastTurn:
            positionOfDoubleMovedPawn = self.gameBoard.pawnMovedDoubleLastTurn.position
            indexOfFile = ChessPiece.horizontalSquareOrderList.index(positionOfDoubleMovedPawn[0])
            for horizontalSquaresAwayFromPosition in [-1, 1]:
                if f"{ChessPiece.horizontalSquareOrderList[indexOfFile - horizontalSquaresAwayFromPosition]}{positionOfDoubleMovedPawn[1]}" == self.position:
                    potentialMove = self.findNewPositionAfterMovement(horizontalSquaresAwayFromPosition,
                                                                  1 * forwardDirection, startPosition=startPosition)
                    potentialMoveList.append((potentialMove, self.gameBoard.pawnMovedDoubleLastTurn, False))

        return potentialMoveList

    def promotePawn(self):
        self.gameBoard.pieceList.remove(self)
        self.gameBoard.pieceList.append(QueenPiece(self.position, self.gameBoard, self.playerColor))

        return


class KingPiece(ChessPiece):
    movementPattern = [[(0, 1)], [(1, 1)], [(1, 0)], [(1, -1)],
                        [(0, -1)], [(-1, -1)], [(-1, 0)], [(-1, 1)]]

    def __init__(self, startPosition, gameBoard, playerColor):
        super(KingPiece, self).__init__(startPosition, gameBoard, playerColor, KingPiece.movementPattern)
        self.isAtStartingPosition = True

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
        self.isAtStartingPosition = True


class BishopPiece(ChessPiece):
    movementPattern = [[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
                     [(1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7)],
                     [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)],
                     [(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7)]]
    def __init__(self, startPosition, gameBoard, playerColor):
        super(BishopPiece, self).__init__(startPosition, gameBoard, playerColor, BishopPiece.movementPattern)
        self.isAtStartingPosition = True


class RookPiece(ChessPiece):
    movementPattern = [[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)],
                     [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                     [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)],
                     [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)]]
    def __init__(self, startPosition, gameBoard, playerColor):
        super(RookPiece, self).__init__(startPosition, gameBoard, playerColor, RookPiece.movementPattern)
        self.isAtStartingPosition = True


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
        self.isAtStartingPosition = True


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
        self.isDraw = False
        self.movesSinceLastCaptureOrPawnMove = 0
        self.pawnMovedDoubleLastTurn = False

        self.whitePawnCount = 8
        self.whiteRookCount = 2
        self.whiteKnightCount = 2
        self.whiteBishopCount = 2
        self.whiteQueenCount = 1
        self.blackPawnCount = 8
        self.blackRookCount = 2
        self.blackKnightCount = 2
        self.blackBishopCount = 2
        self.blackQueenCount = 1

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

    def updatePieceCounters(self, pieceBeingRemoved):
        if pieceBeingRemoved.playerColor == "White":
            if isinstance(pieceBeingRemoved, PawnPiece):
                self.whitePawnCount -= 1
            if isinstance(pieceBeingRemoved, RookPiece):
                self.whiteRookCount -= 1
            if isinstance(pieceBeingRemoved, KnightPiece):
                self.whiteKnightCount -= 1
            if isinstance(pieceBeingRemoved, BishopPiece):
                self.whiteBishopCount -= 1
            if isinstance(pieceBeingRemoved, QueenPiece):
                self.whiteQueenCount -= 1
        elif pieceBeingRemoved.playerColor == "Black":
            if isinstance(pieceBeingRemoved, PawnPiece):
                self.blackPawnCount -= 1
            if isinstance(pieceBeingRemoved, RookPiece):
                self.blackRookCount -= 1
            if isinstance(pieceBeingRemoved, KnightPiece):
                self.blackKnightCount -= 1
            if isinstance(pieceBeingRemoved, BishopPiece):
                self.blackBishopCount -= 1
            if isinstance(pieceBeingRemoved, QueenPiece):
                self.blackQueenCount -= 1

        return

    def checkIfDraw(self):
        isDraw = False
        # Check for insufficient material
        if self.whitePawnCount == 0 and self.whiteQueenCount == 0 and self.whiteRookCount == 0 and \
                self.blackPawnCount == 0 and self.blackQueenCount == 0 and self.blackRookCount == 0:
            # King | King
            if self.whiteBishopCount == 0 and self.whiteKnightCount == 0 and \
                    self.blackBishopCount == 0 and self.blackKnightCount == 0:
                isDraw = True
            # King + Bishop | King
            elif self.whiteKnightCount == 0 and self.blackKnightCount == 0 and \
                    self.blackBishopCount == 0:
                isDraw = True
            # King | King + Bishop
            elif self.blackKnightCount == 0 and self.whiteKnightCount == 0 and \
                    self.whiteBishopCount == 0:
                isDraw = True
            # King + Knight | King
            elif self.whiteBishopCount == 0 and self.blackKnightCount == 0 and \
                    self.blackBishopCount == 0:
                isDraw = True
            # King | King + Knight
            elif self.blackBishopCount == 0 and self.whiteKnightCount == 0 and \
                    self.whiteBishopCount == 0:
                isDraw = True

        # Check for threefold repetition
        if len(self.moveList) >= 12:
            if self.moveList[-2] + self.moveList[-1] == self.moveList[-6] + self.moveList[-5] == self.moveList[-10] + self.moveList[-9]:
                isDraw = True

        return isDraw

    def addMoveToMoveList(self, pieceBeingMoved, moveToAdd, originalPosition=False):
        moveNotation = ""
        if moveToAdd[2]:
            if moveToAdd[2][0] == 'd':
                moveNotation = "0-0-0"
            else:
                moveNotation = "0-0"
            self.moveList.append(moveNotation)
            return

        if isinstance(pieceBeingMoved, PawnPiece):
            if moveToAdd[1]:
                moveNotation += originalPosition[0]
        elif isinstance(pieceBeingMoved, RookPiece):
            moveNotation += "R"
        elif isinstance(pieceBeingMoved, KnightPiece):
            moveNotation += "N"
        elif isinstance(pieceBeingMoved, BishopPiece):
            moveNotation += "B"
        elif isinstance(pieceBeingMoved, QueenPiece):
            moveNotation += "Q"
        elif isinstance(pieceBeingMoved, KingPiece):
            moveNotation += "K"

        if moveToAdd[1]:
            moveNotation += "x"

        moveNotation += moveToAdd[0]

        if self.isWhiteInCheckmate or self.isBlackInCheckmate:
            moveNotation += "#"
        elif self.whiteInCheck or self.blackInCheck:
            moveNotation += "+"

        self.moveList.append(moveNotation)

        return

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