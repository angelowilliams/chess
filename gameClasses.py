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

        # if not (self.gameBoard.whiteInCheck or self.gameBoard.blackInCheck):
        #     oppositeKing = (self.gameBoard.blackKing if self.playerColor == "White" else self.gameBoard.whiteKing)
        #     if oppositeKing.checkIfInCheck():
        #        if self.playerColor == "White":
        #            self.gameBoard.blackInCheck = True
        #        else:
        #            self.gameBoard.whiteInCheck = True

        # if self.gameBoard.boardDepth == 1:
        #     if self.gameBoard.whiteInCheck or self.gameBoard.blackInCheck:
        #         if self.playerColor == "White":
        #             if self.gameBoard.checkIfCheckmate("Black"):
        #                 self.gameBoard.isBlackInCheckmate = True
        #         else:
        #             if self.gameBoard.checkIfCheckmate("White"):
        #                 self.gameBoard.isWhiteInCheckmate = True
        #     else:
        #         if self.playerColor == "White":
        #             if self.gameBoard.checkIfStalemate("Black"):
        #                 self.gameBoard.isStalemate = True
        #         else:
        #             if self.gameBoard.checkIfStalemate("White"):
        #                 self.gameBoard.isStalemate = True

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

    def findPotentialMoves(self, startPosition=None):
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
                        else:
                            kingInCheck = (self.gameBoard.whiteKing if self.playerColor == "White" else self.gameBoard.blackKing)
                            if kingInCheck.checkIfInCheckAfterMove(self, (potentialMove, collidedPiece)):
                                break
                            else:
                                potentialMoveList.append((potentialMove, collidedPiece))
                                break
                    else:
                        kingInCheck = (self.gameBoard.whiteKing if self.playerColor == "White" else self.gameBoard.blackKing)
                        if kingInCheck.checkIfInCheckAfterMove(self, (potentialMove, collidedPiece)):
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

    def findPotentialMoves(self, startPosition=None):
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
                if (self.gameBoard.whiteInCheck if self.playerColor == "White" else self.gameBoard.blackInCheck):
                    kingInCheck = (self.gameBoard.whiteKing if self.playerColor == "White" else self.gameBoard.blackKing)
                    if kingInCheck.checkIfInCheckAfterMove(self, (potentialMove, isCollision)):
                        pass
                    else:
                        potentialMoveList.append((potentialMove, isCollision))
                else:
                    potentialMoveList.append((potentialMove, isCollision))
                if self.isAtStartingPosition:
                    potentialMove = self.findNewPositionAfterMovement(0, 2 * forwardDirection, startPosition=startPosition)
                    if potentialMove:
                        isCollision = self.checkCollisionWithOtherPiece(potentialMove)
                        if not isCollision:
                            if (self.gameBoard.whiteInCheck if self.playerColor == "White" else self.gameBoard.blackInCheck):
                                kingInCheck = (self.gameBoard.whiteKing if self.playerColor == "White" else self.gameBoard.blackKing)
                                if kingInCheck.checkIfInCheckAfterMove(self, (potentialMove, isCollision)):
                                    pass
                                else:
                                    potentialMoveList.append((potentialMove, isCollision))
                            else:
                                potentialMoveList.append((potentialMove, isCollision))

        for horizontalSquaresAwayFromPosition in [-1, 1]:
            potentialMove = self.findNewPositionAfterMovement(horizontalSquaresAwayFromPosition, 1 * forwardDirection, startPosition=startPosition)
            if potentialMove:
                isCollision = self.checkCollisionWithOtherPiece(potentialMove)
                if isCollision:
                    if self.playerColor == isCollision.playerColor:
                        continue
                    if (self.gameBoard.whiteInCheck if self.playerColor == "White" else self.gameBoard.blackInCheck):
                        kingInCheck = (self.gameBoard.whiteKing if self.playerColor == "White" else self.gameBoard.blackKing)
                        if kingInCheck.checkIfInCheckAfterMove(self, (potentialMove, isCollision)):
                            continue
                        else:
                            potentialMoveList.append((potentialMove, isCollision))
                    else:
                        potentialMoveList.append((potentialMove, isCollision))

        return potentialMoveList


class KingPiece(ChessPiece):
    def __init__(self, startPosition, gameBoard, playerColor):
        super(KingPiece, self).__init__(startPosition, gameBoard, playerColor, [[(0, 1)], [(1, 1)], [(1, 0)], [(1, -1)],
                                                                                [(0, -1)], [(-1, -1)], [(-1, 0)], [(-1, 1)]])

    def checkIfInCheck(self):
        for chessPiece in self.gameBoard.pieceList:
            if chessPiece.playerColor != self.playerColor:
                potentialMoves = chessPiece.findPotentialMoves()
                for potentialMove in potentialMoves:
                    if potentialMove[0] == self.position:
                        return True
        return False

    def checkIfInCheckAfterMove(self, pieceToMove, potentialMove):
        copiedGameBoard = copy.deepcopy(self.gameBoard)
        copiedGameBoard.boardDepth += 1
        copiedPieceToMove = copiedGameBoard.positionMap[pieceToMove.position]
        if potentialMove[1]:
            potentialMove = (potentialMove[0], copiedGameBoard.positionMap[potentialMove[1].position])
        copiedPieceToMove.movePiece(potentialMove[0], pieceCollidedWith=potentialMove[1])
        if self.playerColor == "White":
            kingPiece = copiedGameBoard.whiteKing
        else:
            kingPiece = copiedGameBoard.blackKing
        return kingPiece.checkIfInCheck()


class KnightPiece(ChessPiece):
    def __init__(self, startPosition, gameBoard, playerColor):
        super(KnightPiece, self).__init__(startPosition, gameBoard, playerColor, [[(1, 2)],
                                                                 [(2, 1)],
                                                                 [(2, -1)],
                                                                 [(1, -2)],
                                                                 [(-1, -2)],
                                                                 [(-2, -1)],
                                                                 [(-2, 1)],
                                                                 [(-1, 2)]])

class BishopPiece(ChessPiece):
    def __init__(self, startPosition, gameBoard, playerColor):
        super(BishopPiece, self).__init__(startPosition, gameBoard, playerColor, [[(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
                                                                 [(1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7)],
                                                                 [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)],
                                                                 [(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6), (-7, 7)]])

class RookPiece(ChessPiece):
    def __init__(self, startPosition, gameBoard, playerColor):
        super(RookPiece, self).__init__(startPosition, gameBoard, playerColor, [[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)],
                                                                 [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                                                                 [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)],
                                                                 [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)]])
class QueenPiece(ChessPiece):
    def __init__(self, startPosition, gameBoard, playerColor):
        super(QueenPiece, self).__init__(startPosition, gameBoard, playerColor, [[(0, 1), (0, 2), (0, 3), (0, 4), (0, 5), (0, 6), (0, 7)],
                                                                 [(1, 0), (2, 0), (3, 0), (4, 0), (5, 0), (6, 0), (7, 0)],
                                                                 [(0, -1), (0, -2), (0, -3), (0, -4), (0, -5), (0, -6), (0, -7)],
                                                                 [(-1, 0), (-2, 0), (-3, 0), (-4, 0), (-5, 0), (-6, 0), (-7, 0)],
                                                                 [(1, 1), (2, 2), (3, 3), (4, 4), (5, 5), (6, 6), (7, 7)],
                                                                 [(1, -1), (2, -2), (3, -3), (4, -4), (5, -5), (6, -6), (7, -7)],
                                                                 [(-1, -1), (-2, -2), (-3, -3), (-4, -4), (-5, -5), (-6, -6), (-7, -7)],
                                                                 [(-1, 1), (-2, 2), (-3, 3), (-4, 4), (-5, 5), (-6, 6),  (-7, 7)]])


class GameBoard():
    def __init__(self):
        self.boardDepth = 1
        self.moveList = []
        self.pieceList = []
        self.playerToMoveNext = "White"
        self.positionMap = {}
        self.initializePieces()
        for chessPiece in self.pieceList:
            if isinstance(chessPiece, KingPiece):
                if chessPiece.playerColor == "White":
                    self.whiteKing = chessPiece
                else:
                    self.blackKing = chessPiece
        self.whiteInCheck = False
        self.blackInCheck = False
        self.isWhiteInCheckmate = False
        self.isBlackInCheckmate = False
        self.isStalemate = False

    def checkIfPlayerHasNoPotentialMoves(self, playerColor):
        for chessPiece in self.pieceList:
            if chessPiece.playerColor == playerColor:
                potentialMoves = chessPiece.findPotentialMoves()
                for potentialMove in potentialMoves:
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
