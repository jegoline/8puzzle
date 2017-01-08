# Slide Puzzle
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import sys, random, time, os, psutil, pygame, re, astar, strips, dfs
import numpy as np
from pygame.locals import *
# from astar import astar
# import astar
# import strips

# Create the constants (go ahead and experiment with different values)
BOARDWIDTH = 3  # number of columns in the board
BOARDHEIGHT = 3 # number of rows in the board
TILESIZE = 80
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
FPS = 30
BLANK = 0
BOARD = []
GOAL_STATE = [[1, 4, 7], [2, 5, 8], [3, 6, 0]]

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
    # for x in range(BOARDWIDTH):
    #     column = []
    #     for y in range(BOARDHEIGHT):
    #         column.append(counter)
    #         counter += BOARDWIDTH
    #     board.append(column)
    #     counter -= BOARDWIDTH * (BOARDHEIGHT - 1) + BOARDWIDTH - 1
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
    number_runs = 4

    BOARD = []

    # generate random states
    for i in xrange(0, number_runs):
        BOARD.append(generateNewPuzzle(3))




    # TODO: calculate algorithms here

    # for i in xrange(0, number_runs):
    #    print BOARD[i]


    print 'starting with ' + str(number_runs) + ' runs'

    # starting_time = time.time()
    # steps = 0
    # length = 0
    # print 'start A* manhatten distance'
    # for i in xrange(0, number_runs):
    #     p,s = startAStarAlgorithmManhatten(BOARD[i])
    #     steps = steps + s.num_of_expanded
    #     length += len(p)
    # print 'solved in ' + str(time.time()-starting_time) + 's and expanded ' + str(steps/number_runs) + ' nodes on average and needed ' + str(length/number_runs) + ' steps'
    #
    # starting_time = time.time()
    # steps = 0
    # length = 0
    # print 'start A* missplaced tiles'
    # for i in xrange(0, number_runs):
    #     p,s = startAStarAlgorithmMissplacedTiles(BOARD[i])
    #     steps = steps + s.num_of_expanded
    #     length += len(p)
    # print 'solved in ' + str(time.time()-starting_time) + 's and expanded ' + str(steps/number_runs) + ' nodes on average and needed ' + str(length/number_runs) + ' steps'
    #
    # starting_time = time.time()
    # steps = 0
    # length = 0
    # print 'start Greedy manhatten distance'
    # for i in xrange(0, number_runs):
    #     p,s = startGreedyAlgorithmManhatten(BOARD[i])
    #     steps = steps + s.num_of_expanded
    #     length += len(p)
    # print 'solved in ' + str(time.time()-starting_time) + 's and expanded ' + str(steps/number_runs) + ' nodes on average and needed ' + str(length/number_runs) + ' steps'
    #
    # starting_time = time.time()
    # steps = 0
    # length = 0
    # print 'start Greedy misplaced tiles'
    # for i in xrange(0, number_runs):
    #     p,s = startGreedyAlgorithmMissplacedTiles(BOARD[i])
    #     steps = steps + s.num_of_expanded
    #     length += len(p)
    # print 'solved in ' + str(time.time()-starting_time) + 's and expanded ' + str(steps/number_runs) + ' nodes on average and needed ' + str(length/number_runs) + ' steps'

    # starting_time = time.time()
    # print 'start STRIPS'
    # for i in xrange(0, number_runs):
    #     stripsCreateFiles(i, BOARD[i])
    # # print 'files created'
    # steps = 0
    # length = 0
    # for i in xrange(0, number_runs):
    #     p,s = startStripsAlgorithm('puzzle' + str(i) + '.txt')
    #     steps += s
    #     length += p
    # print 'solved in ' + str(time.time()-starting_time) + 's and expanded ' + str(steps/number_runs) + ' nodes on average and needed ' + str(length/number_runs) + ' steps'

    # NICOLE: Starting Bfs

    starting_time = time.time()
    print 'start Bredth-First'
    steps = 0
    length = 0
    for i in xrange(0, number_runs):
        p,s = startAlgorithmBfs(BOARD[i]) # getting expanded nodes + steps
        steps += s
        length += p
    print 'solved in ' + str(time.time()-starting_time) + 's and expanded ' + str(steps/number_runs) + ' nodes on average and needed ' + str(length/number_runs) + ' steps'

    # NICOLE: Starting Dfs

    starting_time = time.time()
    print 'start Depth-First'
    steps = 0
    length = 0
    for i in xrange(0, number_runs):
        p,s = startAlgorithmDfs(BOARD[i]) # getting expanded nodes + steps
        steps += s
        length += p
    print 'solved in ' + str(time.time()-starting_time) + 's and expanded ' + str(steps/number_runs) + ' nodes on average and needed ' + str(length/number_runs) + ' steps'

    # dfs.main(BOARD)

    print 'finished'
    return

# NICOLE: Here I call your methods:

def startAlgorithmBfs(init_state):
    return dfs.run(init_state,'bfs', GOAL_STATE)

def startAlgorithmDfs(init_state):
    return dfs.run(init_state,'dfs', GOAL_STATE)

def startAStarAlgorithmMissplacedTiles(init_state):
    return astar.run(init_state, GOAL_STATE, astar.evaluate_a_star, astar.heuristic_misplaced_tiles)

def startAStarAlgorithmManhatten(init_state):
    return astar.run(init_state, GOAL_STATE, astar.evaluate_a_star, astar.heuristic_manhattan_distance)

def startGreedyAlgorithmMissplacedTiles(init_state):
    return astar.run(init_state, GOAL_STATE, astar.evaluate_greedy, astar.heuristic_misplaced_tiles)

def startGreedyAlgorithmManhatten(init_state):
    return astar.run(init_state, GOAL_STATE, astar.evaluate_greedy, astar.heuristic_manhattan_distance)

def startStripsAlgorithm(filename):
    return strips.run(filename)

def stripsCreateFiles(i, init_state):
    f = open('puzzle' + str(i) + '.txt', 'w')
    s = 'Initial state: Adj(A, B), Adj(B, C), Adj(D, E), Adj(E, F), Adj(G, H), Adj(H, I), Adj(A, D), Adj(B, E), Adj(C, F), Adj(D, G), Adj(E, H), Adj(F, I), Adj(B, A), Adj(C, B), Adj(E, D), Adj(F, E), Adj(H, G), Adj(I, H), Adj(D, A), Adj(E, B), Adj(F, C), Adj(G, D), Adj(H, E), Adj(I, F)'
    for i in xrange(0, 3):
        for j in xrange(0, 3):
            if init_state[i][j] == 0:
                s = s + ', BlankAt(' + str(numberToLiteral(i+j*3)) + ')'
            elif init_state[i][j]  == 1:
                s = s + ', OneAt(' + str(numberToLiteral(i+j*3)) + ')'
            elif init_state[i][j]  == 2:
                s = s + ', TwoAt(' + str(numberToLiteral(i+j*3)) + ')'
            elif init_state[i][j]  == 3:
                s = s + ', ThreeAt(' + str(numberToLiteral(i+j*3)) + ')'
            elif init_state[i][j]  == 4:
                s = s + ', FourAt(' + str(numberToLiteral(i+j*3)) + ')'
            elif init_state[i][j]  == 5:
                s = s + ', FiveAt(' + str(numberToLiteral(i+j*3)) + ')'
            elif init_state[i][j]  == 6:
                s = s + ', SixAt(' + str(numberToLiteral(i+j*3)) + ')'
            elif init_state[i][j]  == 7:
                s = s + ', SevenAt(' + str(numberToLiteral(i+j*3)) + ')'
            elif init_state[i][j]  == 8:
                s = s + ', EightAt(' + str(numberToLiteral(i+j*3)) + ')'
    s = s + '\n'
    s = s + 'Goal State: OneAt(A), TwoAt(B), ThreeAt(C), FourAt(D), FiveAt(E), SixAt(F), SevenAt(G), EightAt(H), BlankAt(I)\n'
    s = s + 'Actions:\n'
    s = s + 'MoveOne(X, Y)\n'
    s = s + 'Preconditions: OneAt(X), BlankAt(Y), Adj(X, Y)\n'
    s = s + 'Postconditions: !OneAt(X), !BlankAt(Y), BlankAt(X), OneAt(Y)\n'
    s = s + 'MoveTwo(X, Y)\n'
    s = s + 'Preconditions: TwoAt(X), BlankAt(Y), Adj(X, Y)\n'
    s = s + 'Postconditions: !TwoAt(X), !BlankAt(Y), BlankAt(X), TwoAt(Y)\n'
    s = s + 'MoveThree(X, Y)\n'
    s = s + 'Preconditions: ThreeAt(X), BlankAt(Y), Adj(X, Y)\n'
    s = s + 'Postconditions: !ThreeAt(X), !BlankAt(Y), BlankAt(X), ThreeAt(Y)\n'
    s = s + 'MoveFour(X, Y)\n'
    s = s + 'Preconditions: FourAt(X), BlankAt(Y), Adj(X, Y)\n'
    s = s + 'Postconditions: !FourAt(X), !BlankAt(Y), BlankAt(X), FourAt(Y)\n'
    s = s + 'MoveFive(X, Y)\n'
    s = s + 'Preconditions: FiveAt(X), BlankAt(Y), Adj(X, Y)\n'
    s = s + 'Postconditions: !FiveAt(X), !BlankAt(Y), BlankAt(X), FiveAt(Y)\n'
    s = s + 'MoveSix(X, Y)\n'
    s = s + 'Preconditions: SixAt(X), BlankAt(Y), Adj(X, Y)\n'
    s = s + 'Postconditions: !SixAt(X), !BlankAt(Y), BlankAt(X), SixAt(Y)\n'
    s = s + 'MoveSeven(X, Y)\n'
    s = s + 'Preconditions: SevenAt(X), BlankAt(Y), Adj(X, Y)\n'
    s = s + 'Postconditions: !SevenAt(X), !BlankAt(Y), BlankAt(X), SevenAt(Y)\n'
    s = s + 'MoveEight(X, Y)\n'
    s = s + 'Preconditions: EightAt(X), BlankAt(Y), Adj(X, Y)\n'
    s = s + 'Postconditions: !EightAt(X), !BlankAt(Y), BlankAt(X), EightAt(Y)\n'
    f.write(s)

def numberToLiteral(tileAt):
    if tileAt == 0:
        return 'A'
    elif tileAt == 1:
        return 'B'
    elif tileAt == 2:
        return 'C'
    elif tileAt == 3:
        return 'D'
    elif tileAt == 4:
        return 'E'
    elif tileAt == 5:
        return 'F'
    elif tileAt == 6:
        return 'G'
    elif tileAt == 7:
        return 'H'
    elif tileAt == 8:
        return 'I'

if __name__ == '__main__':
    main()