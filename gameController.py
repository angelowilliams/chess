import gameClasses
import pygame

class ChessGame():

    positionToCoordinateMultipleDict = {'a': 0,
                                        'b': 1,
                                        'c': 2,
                                        'd': 3,
                                        'e': 4,
                                        'f': 5,
                                        'g': 6,
                                        'h': 7,
                                        '8': 0,
                                        '7': 1,
                                        '6': 2,
                                        '5': 3,
                                        '4': 4,
                                        '3': 5,
                                        '2': 6,
                                        '1': 7}

    def __init__(self, screenSize):
        self.screenSize = screenSize
        self.blockSize = int(self.screenSize / 8)
        self.spriteSize = self.blockSize - int(self.blockSize * 0.2)
        self.bufferDistance = (self.blockSize - self.spriteSize) / 2
        self.dotSpriteSize = int(self.blockSize / 2)
        self.dotBufferDistance = int(self.blockSize / 4)

        pygame.init()
        self.gameBoard = gameClasses.GameBoard()
        self.gameSurface = pygame.display.set_mode((screenSize, screenSize))
        pygame.display.set_caption("Chess")
        self.gameOver = False

        self.backgroundChessBoard = pygame.transform.scale(pygame.image.load("assets/chessBoard.png"), (self.screenSize, self.screenSize))
        self.whitePawnSprite = pygame.transform.scale(pygame.image.load("assets/whitePawn.png"), (self.spriteSize, self.spriteSize))
        self.whiteRookSprite = pygame.transform.scale(pygame.image.load("assets/whiteRook.png"), (self.spriteSize, self.spriteSize))
        self.whiteKnightSprite = pygame.transform.scale(pygame.image.load("assets/whiteKnight.png"), (self.spriteSize, self.spriteSize))
        self.whiteBishopSprite = pygame.transform.scale(pygame.image.load("assets/whiteBishop.png"), (self.spriteSize, self.spriteSize))
        self.whiteQueenSprite = pygame.transform.scale(pygame.image.load("assets/whiteQueen.png"), (self.spriteSize, self.spriteSize))
        self.whiteKingSprite = pygame.transform.scale(pygame.image.load("assets/whiteKing.png"), (self.spriteSize, self.spriteSize))
        self.blackPawnSprite = pygame.transform.scale(pygame.image.load("assets/blackPawn.png"), (self.spriteSize, self.spriteSize))
        self.blackRookSprite = pygame.transform.scale(pygame.image.load("assets/blackRook.png"), (self.spriteSize, self.spriteSize))
        self.blackKnightSprite = pygame.transform.scale(pygame.image.load("assets/blackKnight.png"), (self.spriteSize, self.spriteSize))
        self.blackBishopSprite = pygame.transform.scale(pygame.image.load("assets/blackBishop.png"), (self.spriteSize, self.spriteSize))
        self.blackQueenSprite = pygame.transform.scale(pygame.image.load("assets/blackQueen.png"), (self.spriteSize, self.spriteSize))
        self.blackKingSprite = pygame.transform.scale(pygame.image.load("assets/blackKing.png"), (self.spriteSize, self.spriteSize))
        self.greenDotSprite = pygame.transform.scale(pygame.image.load("assets/greenDot.png"), (self.dotSpriteSize, self.dotSpriteSize))
        self.redBorderSprite = pygame.transform.scale(pygame.image.load("assets/redBorder.png"), (self.blockSize, self.blockSize))
        self.greenSquareSprite = pygame.transform.scale(pygame.image.load("assets/greenSquare.png"), (self.blockSize, self.blockSize))

        self.gameLoop()

        return


    def gameLoop(self):
        turnMap = {True: "White", False: "Black"}
        playerTurn = True
        lastClickedPiece = None
        kingInCheck = False

        while not self.gameOver:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.gameOver = True

                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouseClickPosition = pygame.mouse.get_pos()
                    clickedBoardPosition = self.convertScreenCoordinatesToBoardPosition(mouseClickPosition)

                    if lastClickedPiece:
                        for potentialMove in lastClickedPiece.positionsBeingAttackedByPiece:
                            if clickedBoardPosition in potentialMove:
                                lastClickedPiece.movePiece(clickedBoardPosition, pieceCollidedWith=potentialMove[1])
                                playerTurn = not playerTurn
                                if playerTurn:
                                    self.gameBoard.whiteInCheck = self.gameBoard.whiteKing.checkIfInCheck()
                                else:
                                    self.gameBoard.blackInCheck = self.gameBoard.blackKing.checkIfInCheck()
                                lastClickedPiece = None
                    if lastClickedPiece == self.gameBoard.positionMap.get(clickedBoardPosition, None):
                        lastClickedPiece = None
                        continue
                    else:
                        lastClickedPiece = self.gameBoard.positionMap.get(clickedBoardPosition, None)
                        if lastClickedPiece:
                            if lastClickedPiece.playerColor != turnMap[playerTurn]:
                                lastClickedPiece = None
                                continue

            self.gameSurface.blit(self.backgroundChessBoard, (0, 0))

            if self.gameBoard.whiteInCheck:
                kingInCheck = self.gameBoard.whiteKing
            elif self.gameBoard.blackInCheck:
                kingInCheck = self.gameBoard.blackKing

            if kingInCheck:
                borderCoordinates = self.convertBoardPositionToScreenCoordinates(kingInCheck.position, 0)
                transparentSurface = pygame.Surface((self.blockSize, self.blockSize)).convert()
                transparentSurface.blit(self.gameSurface, (-borderCoordinates[0], -borderCoordinates[1]))
                transparentSurface.blit(self.redBorderSprite, (0, 0))
                transparentSurface.set_alpha(200)

                self.gameSurface.blit(transparentSurface, borderCoordinates)
            kingInCheck = False

            if lastClickedPiece:
                pieceCoordinates = self.convertBoardPositionToScreenCoordinates(lastClickedPiece.position, 0)
                transparentSurface = pygame.Surface((self.blockSize, self.blockSize)).convert()
                transparentSurface.blit(self.gameSurface, (-pieceCoordinates[0], -pieceCoordinates[1]))
                transparentSurface.blit(self.greenSquareSprite, (0, 0))
                transparentSurface.set_alpha(90)

                self.gameSurface.blit(transparentSurface, pieceCoordinates)

            for chessPiece in self.gameBoard.pieceList:
                pieceCoordinates = self.convertBoardPositionToScreenCoordinates(chessPiece.position, self.bufferDistance)
                playerColor = chessPiece.playerColor
                if isinstance(chessPiece, gameClasses.PawnPiece):
                    pieceSprite = (self.whitePawnSprite if playerColor == "White" else self.blackPawnSprite)
                elif isinstance(chessPiece, gameClasses.RookPiece):
                    pieceSprite = (self.whiteRookSprite if playerColor == "White" else self.blackRookSprite)
                elif isinstance(chessPiece, gameClasses.KnightPiece):
                    pieceSprite = (self.whiteKnightSprite if playerColor == "White" else self.blackKnightSprite)
                elif isinstance(chessPiece, gameClasses.BishopPiece):
                    pieceSprite = (self.whiteBishopSprite if playerColor == "White" else self.blackBishopSprite)
                elif isinstance(chessPiece, gameClasses.QueenPiece):
                    pieceSprite = (self.whiteQueenSprite if playerColor == "White" else self.blackQueenSprite)
                elif isinstance(chessPiece, gameClasses.KingPiece):
                    pieceSprite = (self.whiteKingSprite if playerColor == "White" else self.blackKingSprite)

                self.gameSurface.blit(pieceSprite, pieceCoordinates)

            if lastClickedPiece:
                for potentialMove in lastClickedPiece.positionsBeingAttackedByPiece:
                    dotSprite = self.greenDotSprite if potentialMove[1] is False else self.redBorderSprite
                    bufferDistance = self.dotBufferDistance if potentialMove[1] is False else 0
                    dotCoordinates = self.convertBoardPositionToScreenCoordinates(potentialMove[0], bufferDistance)

                    transparentSurface = pygame.Surface((dotSprite.get_width(), dotSprite.get_height())).convert()
                    transparentSurface.blit(self.gameSurface, (-dotCoordinates[0], -dotCoordinates[1]))
                    transparentSurface.blit(dotSprite, (0, 0))
                    transparentSurface.set_alpha(150)

                    self.gameSurface.blit(transparentSurface, dotCoordinates)

            if self.gameBoard.isWhiteInCheckmate:
                print("Black wins!")
                #return
            elif self.gameBoard.isBlackInCheckmate:
                print("White wins!")
                #return
            elif self.gameBoard.isStalemate:
                print("Draw")
                #return

            pygame.display.update()
        return

    def convertBoardPositionToScreenCoordinates(self, positionToConvert, bufferDistance):
        horizontalPosition = positionToConvert[0]
        horizontalCoordinate = int(self.blockSize * ChessGame.positionToCoordinateMultipleDict[horizontalPosition] + bufferDistance)

        verticalPosition = positionToConvert[1]
        verticalCoordinate = int(self.blockSize * ChessGame.positionToCoordinateMultipleDict[verticalPosition] + bufferDistance)

        return (horizontalCoordinate, verticalCoordinate)

    def convertScreenCoordinatesToBoardPosition(self, positionToConvert):
        horizontalCoordinate = positionToConvert[0]
        if horizontalCoordinate in range(0, self.screenSize // 8):
            horizontalPosition = 'a'
        elif horizontalCoordinate in range(self.screenSize // 8, 2 * self.screenSize // 8):
            horizontalPosition = 'b'
        elif horizontalCoordinate in range(2 * self.screenSize // 8, 3 * self.screenSize // 8):
            horizontalPosition = 'c'
        elif horizontalCoordinate in range(3 * self.screenSize // 8, 4 * self.screenSize // 8):
            horizontalPosition = 'd'
        elif horizontalCoordinate in range(4 * self.screenSize // 8, 5 * self.screenSize // 8):
            horizontalPosition = 'e'
        elif horizontalCoordinate in range(5 * self.screenSize // 8, 6 * self.screenSize // 8):
            horizontalPosition = 'f'
        elif horizontalCoordinate in range(6 * self.screenSize // 8, 7 * self.screenSize // 8):
            horizontalPosition = 'g'
        elif horizontalCoordinate in range(7 * self.screenSize // 8, self.screenSize):
            horizontalPosition = 'h'

        verticalCoordinate = positionToConvert[1]
        if verticalCoordinate in range(0, self.screenSize // 8):
            verticalPosition = '8'
        elif verticalCoordinate in range(self.screenSize // 8, 2 * self.screenSize // 8):
            verticalPosition = '7'
        elif verticalCoordinate in range(2 * self.screenSize // 8, 3 * self.screenSize // 8):
            verticalPosition = '6'
        elif verticalCoordinate in range(3 * self.screenSize // 8, 4 * self.screenSize // 8):
            verticalPosition = '5'
        elif verticalCoordinate in range(4 * self.screenSize // 8, 5 * self.screenSize // 8):
            verticalPosition = '4'
        elif verticalCoordinate in range(5 * self.screenSize // 8, 6 * self.screenSize // 8):
            verticalPosition = '3'
        elif verticalCoordinate in range(6 * self.screenSize // 8, 7 * self.screenSize // 8):
            verticalPosition = '2'
        elif verticalCoordinate in range(7 * self.screenSize // 8, self.screenSize):
            verticalPosition = '1'

        return f"{horizontalPosition}{verticalPosition}"


ChessGame(640)