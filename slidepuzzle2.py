# Slide Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import pygame, sys, random
from pygame.locals import *

# Create the constants (go ahead and experiment with different values)
BOARDWIDTH = 3  # number of columns in the board
BOARDHEIGHT = 3 # number of rows in the board
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = None
BOARD = []

#                 R    G    B
BLACK =         (  0,   0,   0)
WHITE =         (255, 255, 255)
BRIGHTBLUE =    (  0,  50, 255)
DARKTURQUOISE = (  3,  54,  73)
GREEN =         (  0, 204,   0)
RED =           (255,   0,   0)
BEIGE =         (255, 221, 153)
LIGHTRED =      (255,  50,  50)
LIGHTBLUE =     (150, 150, 255)
GREY =          (100, 100, 100)


BGCOLOR = BEIGE
TILECOLOR = GREEN
TEXTCOLOR = BLACK
TEXTBG = BGCOLOR
BORDERCOLOR = LIGHTBLUE
BASICFONTSIZE = 20

BUTTONCOLOR = WHITE
BUTTONTEXTCOLOR = BLACK
MESSAGECOLOR = DARKTURQUOISE

XMARGIN = int((WINDOWWIDTH - (TILESIZE * BOARDWIDTH + (BOARDWIDTH - 1))) - 10)
YMARGIN = int((WINDOWHEIGHT - (TILESIZE * BOARDHEIGHT + (BOARDHEIGHT - 1))) - 10)

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, MSG_SURF, MSG_RECT, ALG_SURF, ALG_RECT, ASTAR_SURF, ASTAR_RECT, \
        STRPS_SURF, STRPS_RECT, GO_SURF, GO_RECT, STEPS_SURF, STEPS_RECT, TIME_SURF, TIME_RECT, MEM_SURF, MEM_RECT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    pygame.display.set_caption('Solving 8-Puzzle')
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)

    # Store the option buttons and their rectangles in OPTIONS.
    MSG_SURF,   MSG_RECT   = makeText('Click GO! to start the algorithms', DARKTURQUOISE, TEXTBG, 5,     5)
    ALG_SURF,   ALG_RECT   = makeText('Algorithms',                        GREY,          TEXTBG, 10,  100)
    ASTAR_SURF, ASTAR_RECT = makeText('A-Star',                            GREY,          TEXTBG, 10,  130)
    STRPS_SURF, STRPS_RECT = makeText('STRIPS',                            GREY,          TEXTBG, 10,  160)
    STEPS_SURF, STEPS_RECT  = makeText('#steps',                           GREY,          TEXTBG, 140, 100)
    TIME_SURF,  TIME_RECT  = makeText('time',                              GREY,          TEXTBG, 220, 100)
    MEM_SURF,   MEM_RECT   = makeText('memory',                            GREY,          TEXTBG, 300, 100)
    GO_SURF,    GO_RECT    = makeText('GO!',                               TEXTCOLOR,     TEXTBG, 10, WINDOWHEIGHT-50)

    mainBoard = generateNewPuzzle(20)

    while True: # main game loop
        drawBoard(mainBoard)

        checkForQuit()
        for event in pygame.event.get(): # event handling loop
            if event.type == MOUSEBUTTONUP:
                if GO_RECT.collidepoint(event.pos):
                    calculateAlgorithms() # clicked on Solve button

        pygame.display.update()
        FPSCLOCK.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def getStartingBoard():
    # Return a board data structure with tiles in the solved state.
    # For example, if BOARDWIDTH and BOARDHEIGHT are both 3, this function
    # returns [[1, 4, 7], [2, 5, 8], [3, 6, BLANK]]
    counter = 1
    board = []
    for x in range(BOARDWIDTH):
        column = []
        for y in range(BOARDHEIGHT):
            column.append(counter)
            counter += BOARDWIDTH
        board.append(column)
        counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1

    board[BOARDWIDTH-1][BOARDHEIGHT-1] = BLANK
    return board


def getBlankPosition(board):
    # Return the x and y of board coordinates of the blank space.
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            if board[x][y] == BLANK:
                return (x, y)


def makeMove(board, move):
    # This function does not check if the move is valid.
    blankx, blanky = getBlankPosition(board)

    if move == UP:
        board[blankx][blanky], board[blankx][blanky + 1] = board[blankx][blanky + 1], board[blankx][blanky]
    elif move == DOWN:
        board[blankx][blanky], board[blankx][blanky - 1] = board[blankx][blanky - 1], board[blankx][blanky]
    elif move == LEFT:
        board[blankx][blanky], board[blankx + 1][blanky] = board[blankx + 1][blanky], board[blankx][blanky]
    elif move == RIGHT:
        board[blankx][blanky], board[blankx - 1][blanky] = board[blankx - 1][blanky], board[blankx][blanky]


def isValidMove(board, move):
    blankx, blanky = getBlankPosition(board)
    return (move == UP and blanky != len(board[0]) - 1) or \
           (move == DOWN and blanky != 0) or \
           (move == LEFT and blankx != len(board) - 1) or \
           (move == RIGHT and blankx != 0)


def getRandomMove(board, lastMove=None):
    # start with a full list of all four moves
    validMoves = [UP, DOWN, LEFT, RIGHT]

    # remove moves from the list as they are disqualified
    if lastMove == UP or not isValidMove(board, DOWN):
        validMoves.remove(DOWN)
    if lastMove == DOWN or not isValidMove(board, UP):
        validMoves.remove(UP)
    if lastMove == LEFT or not isValidMove(board, RIGHT):
        validMoves.remove(RIGHT)
    if lastMove == RIGHT or not isValidMove(board, LEFT):
        validMoves.remove(LEFT)

    # return a random move from the list of remaining moves
    return random.choice(validMoves)


def getLeftTopOfTile(tileX, tileY):
    left = XMARGIN + (tileX * TILESIZE) + (tileX - 1)
    top = YMARGIN + (tileY * TILESIZE) + (tileY - 1)
    return (left, top)


def makeText(text, color, bgcolor, top, left):
    # create the Surface and Rect objects for some text.
    textSurf = BASICFONT.render(text, True, color, bgcolor)
    textRect = textSurf.get_rect()
    textRect.topleft = (top, left)
    return (textSurf, textRect)


def drawBoard(board):
    DISPLAYSURF.fill(BGCOLOR)

    DISPLAYSURF.blit(MSG_SURF, MSG_RECT)
    DISPLAYSURF.blit(ALG_SURF, ALG_RECT)
    DISPLAYSURF.blit(ASTAR_SURF, ASTAR_RECT)
    DISPLAYSURF.blit(STRPS_SURF, STRPS_RECT)
    DISPLAYSURF.blit(STEPS_SURF, STEPS_RECT)
    DISPLAYSURF.blit(TIME_SURF, TIME_RECT)
    DISPLAYSURF.blit(MEM_SURF, MEM_RECT)
    DISPLAYSURF.blit(GO_SURF, GO_RECT)



def generateNewPuzzle(numSlides):
    # From a starting configuration, make numSlides number of moves
    board = getStartingBoard()
    lastMove = None
    for i in range(numSlides):
        move = getRandomMove(board, lastMove)
        makeMove(board, move)
        lastMove = move
    return (board)


def calculateAlgorithms():
    print 'not yet implemented'

    # generate random states
    for i in xrange(0, 300):
        print i
        BOARD.append(generateNewPuzzle(80))
        print BOARD[i]

    # TODO: calculate algorithms here
    return

if __name__ == '__main__':
    main()