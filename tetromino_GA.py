# Tetromino (a Tetris clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random, time, pygame, sys
from pygame.locals import *
import GA_BRAIN
import numpy as np
import copy

FPS = 60
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
BOXSIZE = 20
BOARDWIDTH = 10 # 10
BOARDHEIGHT = 20
BLANK = '.'

SHAPES = {'S' : 0, 'Z' : 1, 'I' : 2, 'J' : 3, 'L' : 4, 'T' : 5, 'O' : 6};
SHAPE_HEIGHT = {'S' : 3, 'Z': 3, 'I' : 4, 'O' : 2, 'J' : 3, 'L' : 3, 'T' : 3};
MOVESIDEWAYSFREQ = 0.02
MOVEDOWNFREQ = 0.02

XMARGIN = int((WINDOWWIDTH - BOARDWIDTH * BOXSIZE) / 2)
TOPMARGIN = WINDOWHEIGHT - (BOARDHEIGHT * BOXSIZE) - 5

#               R    G    B
WHITE       = (255, 255, 255)
GRAY        = (185, 185, 185)
BLACK       = (  0,   0,   0)
RED         = (155,   0,   0)
LIGHTRED    = (175,  20,  20)
GREEN       = (  0, 155,   0)
LIGHTGREEN  = ( 20, 175,  20)
BLUE        = (  0,   0, 155)
LIGHTBLUE   = ( 20,  20, 175)
YELLOW      = (155, 155,   0)
LIGHTYELLOW = (175, 175,  20)

BORDERCOLOR = BLUE
BGCOLOR = BLACK
TEXTCOLOR = WHITE
TEXTSHADOWCOLOR = GRAY
COLORS      = (     BLUE,      GREEN,      RED,      YELLOW)
LIGHTCOLORS = (LIGHTBLUE, LIGHTGREEN, LIGHTRED, LIGHTYELLOW)
assert len(COLORS) == len(LIGHTCOLORS) # each color must have light color

TEMPLATEWIDTH = 5
TEMPLATEHEIGHT = 5

S_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '..OO.',
                     '.OO..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '...O.',
                     '.....']]

Z_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '.O...',
                     '.....']]

I_SHAPE_TEMPLATE = [['..O..',
                     '..O..',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     'OOOO.',
                     '.....',
                     '.....']]

O_SHAPE_TEMPLATE = [['.....',
                     '.....',
                     '.OO..',
                     '.OO..',
                     '.....']]

J_SHAPE_TEMPLATE = [['.....',
                     '.O...',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..OO.',
                     '..O..',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '...O.',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '.OO..',
                     '.....']]

L_SHAPE_TEMPLATE = [['.....',
                     '...O.',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..O..',
                     '..OO.',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '.O...',
                     '.....'],
                    ['.....',
                     '.OO..',
                     '..O..',
                     '..O..',
                     '.....']]

T_SHAPE_TEMPLATE = [['.....',
                     '..O..',
                     '.OOO.',
                     '.....',
                     '.....'],
                    ['.....',
                     '..O..',
                     '..OO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '.....',
                     '.OOO.',
                     '..O..',
                     '.....'],
                    ['.....',
                     '..O..',
                     '.OO..',
                     '..O..',
                     '.....']]

PIECES = {'S': S_SHAPE_TEMPLATE,
          'Z': Z_SHAPE_TEMPLATE,
          'J': J_SHAPE_TEMPLATE,
          'L': L_SHAPE_TEMPLATE,
          'I': I_SHAPE_TEMPLATE,
          'O': O_SHAPE_TEMPLATE,
          'T': T_SHAPE_TEMPLATE}


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 100)
    pygame.display.set_caption('Tetromino')
    showTextScreen('Tetromino')
    while True: # game loop
        runGame()


def runGame():
    # setup variables for the start of the game
    board = getBlankBoard()
    lastMoveDownTime = time.time()
    lastMoveSidewaysTime = time.time()
    lastFallTime = time.time()
    movingDown = False # note: there is no movingUp variable
    movingLeft = False
    movingRight = False
    score = 0;
    level, fallFreq = calculateLevelAndFallFreq(score)
    fallingPiece = None
    nextPiece = getNewPiece()
    index = 0;
    moves = []
    while True: # game loop
        if(fallingPiece == None):
            fallingPiece = nextPiece
            nextPiece = getNewPiece()
            ga_moves = GA_BRAIN.trainSolver(board,fallingPiece)
            moves = translateMoves(ga_moves);
            index = 0;
            if not isValidPosition(board, fallingPiece):
                return score

        checkForQuit()
        keyPress = 5 #do nothing
        if(index < len(moves)):
            keyPress = moves[index]
            index += 1
        if(keyPress == 0): #move up
            keyPress = 4
            fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
            if not isValidPosition(board, fallingPiece):
                fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']]);

        elif (keyPress == 1 and isValidPosition(board, fallingPiece, adjX=1)): # move right
                fallingPiece['x'] += 1
                lastMoveSidewaysTime = time.time()
        elif isValidPosition(board, fallingPiece, adjX=-1) and keyPress == 2 : #move left
                  fallingPiece['x'] -= 1
                  lastMoveSidewaysTime = time.time();
        elif keyPress == 3:
            while isValidPosition(board, fallingPiece, adjY=1):
                fallingPiece['y'] += 1

        if not isValidPosition(board, fallingPiece, adjY = 1):
            # falling piece has landed, set it on the board
            addToBoard(board, fallingPiece)
            score += removeCompleteLines(board)
            level, fallFreq = calculateLevelAndFallFreq(score)
            fallingPiece = None
        DISPLAYSURF.fill(BGCOLOR)
        drawBoard(board)
        drawStatus(score, level)
        drawNextPiece(nextPiece)
        if fallingPiece != None:
          drawPiece(fallingPiece)
        pygame.display.update()
        FPSCLOCK.tick(FPS)

    return score;


def processBoard(moves1, board, fallingPiece):
    score = 0;
    index = 0;
    notDown = 0;
    moves = translateMoves(moves1)
    oldRotation = fallingPiece['rotation'];
    heights = getInputs(board);
    heights.sort();
    done = False
    while not done and index < len(moves):
        keyPress = moves[index]
        index+=1
        if(keyPress == 0): #move up
            fallingPiece['rotation'] = (fallingPiece['rotation'] + 1) % len(PIECES[fallingPiece['shape']])
            if not isValidPosition(board, fallingPiece):
                fallingPiece['rotation'] = (fallingPiece['rotation'] - 1) % len(PIECES[fallingPiece['shape']]);

        elif (keyPress == 1 and isValidPosition(board, fallingPiece, adjX=1)): # move right
                fallingPiece['x'] += 1
        elif isValidPosition(board, fallingPiece, adjX=-1) and keyPress == 2 : #move left
                  fallingPiece['x'] -= 1
        else:
            while isValidPosition(board, fallingPiece, adjY=1):
                fallingPiece['y'] += 1


        if not isValidPosition(board, fallingPiece, adjY = 1):
            # falling piece has landed, set it on the board
            addToBoard(board, fallingPiece)
            score += removeCompleteLines2(board)
            done = True

    newHeight = getHeight(board);
    newWidth = getWidth(board);
    numGap = countGap(board);
    newHeights = getInputs(board);
    newHeights.sort();
    sumChanges = 0;
    for i in range(len(newHeights)):
        if newHeights[i] >  heights[i]:
            sumChanges += i;
    getOriginal(fallingPiece, board);
    fallingPiece['rotation'] = oldRotation;
    fallingPiece['x'] =  int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2)
    fallingPiece['y'] = -2
    return numGap,newHeight,newWidth,score,sumChanges;

def getOriginal(piece,board):
    for x in range(TEMPLATEWIDTH):
       for y in range(TEMPLATEHEIGHT):
           if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
                    board[min(len(board) - 1,x + piece['x'])][min(len(board[0]) - 1, y + piece['y'])] = '.'


def translateMoves(moves):
    res = []
    for i in range(moves[2]):
        res.append(0); #change rotation
    for i in range(moves[1]):
        res.append((moves[0]+1)); #num moves
    res.append(3)
    return res;

def countGap(board):
    count = 0
    for h in reversed(range(len(board[0]))):
        for w in range(len(board)):
            if(board[w][h] == '.' and board[w][max(0,h-1)] != '.'):
                count += 1
    return count;


def getHeight(board): # return the current height of the pieces
    maxHeight = 0;
    for w in range(len(board)): #width
        currentHeight = 0;
        for i in reversed(range(len(board[w]))): #height
            if board[w][i] != '.':
                currentHeight = len(board[w]) - i;
        if(maxHeight < currentHeight):
            maxHeight = currentHeight
    return maxHeight


def goodMove(board):
    #for h in reversed(range(len(board[0]))):
        # for w in range(len(board)):
        #     if(board[w][h] == '.' and board[w][h-1] != '.'):
        #         case1 = board[min(0 ,w-1)][h-1] != '.' or board[min(len(board) - 1 ,w+1)][h-1] != '.';
        #         if case1:
        #             return False;
    for h in reversed(range(len(board[0]))):
        for w in range(len(board)):
            if(board[w][h] == '.' and board[w][h-1] != '.'):
                case1 = ((board[max(0,w-1)][h] == '.' and board[max(0,w-1)][max(h-1,0)] != '.') or board[max(0,w-1)][h] != '.');
                case2 = ((board[min(len(board)-1 ,w+1)][h] == '.' and board[min(len(board)-1,w+1)][max(h-1,0)] != '.') or board[min(len(board)-1 ,w+1)][h] != '.');
                if((case1 and case2)):
                    return False;
    return True;

def getWidth(board): # return the current height of the pieces
    width = 0;
    for w in range(len(board)): #width
            if board[w][19] != '.':
                width += 1;
    return width;


def getInputs(board):
    inputs = [];
    for w in range(len(board)):
        top = len(board);
        for i in reversed(range(len(board[w]))):
            if board[w][i] != '.':
                top = i
        inputs.append(len(board) - top);
    return inputs
         

'''

0 up, 1 down, 2 left, 3 

'''
def getMaxIndex(outputs):
    
    # output = outputs[0];
    # val = int(round((output * 0.4) * 10));
    # return int((output * 0.5) * 10);
    index = 0;
    max = outputs[index];
    for i in range(len(outputs)):
        if(outputs[i] > max):
            max = outputs[i];
            index = i;
    return index;

def makeTextObjs(text, font, color):
    surf = font.render(text, True, color)
    return surf, surf.get_rect()


def terminate():
    pygame.quit()
    sys.exit()


def checkForKeyPress():
    # Go through event queue looking for a KEYUP event.
    # Grab KEYDOWN events to remove them from the event queue.
    checkForQuit()

    for event in pygame.event.get([KEYDOWN, KEYUP]):
        if event.type == KEYDOWN:
            continue
        return event.key
    return None


def showTextScreen(text):
    # This function displays large text in the
    # center of the screen until a key is pressed.
    # Draw the text drop shadow
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTSHADOWCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2))
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the text
    titleSurf, titleRect = makeTextObjs(text, BIGFONT, TEXTCOLOR)
    titleRect.center = (int(WINDOWWIDTH / 2) - 3, int(WINDOWHEIGHT / 2) - 3)
    DISPLAYSURF.blit(titleSurf, titleRect)

    # Draw the additional "Press a key to play." text.
    pressKeySurf, pressKeyRect = makeTextObjs('Press a key to play.', BASICFONT, TEXTCOLOR)
    pressKeyRect.center = (int(WINDOWWIDTH / 2), int(WINDOWHEIGHT / 2) + 100)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)

    while checkForKeyPress() == None:
        pygame.display.update()
        FPSCLOCK.tick()


def checkForQuit():
    for event in pygame.event.get(QUIT): # get all the QUIT events
        terminate() # terminate if any QUIT events are present
    for event in pygame.event.get(KEYUP): # get all the KEYUP events
        if event.key == K_ESCAPE:
            terminate() # terminate if the KEYUP event was for the Esc key
        pygame.event.post(event) # put the other KEYUP event objects back


def calculateLevelAndFallFreq(score):
    # Based on the score, return the level the player is on and
    # how many seconds pass until a falling piece falls one space.
    level = int(score / 10) + 1
    fallFreq = 0.27 - (level * 0.02)
    return level, fallFreq

def getNewPiece():
    # return a random new piece in a random rotation and color
    shape = random.choice(list(PIECES.keys()))
    newPiece = {'shape': shape,
                'rotation': random.randint(0, len(PIECES[shape]) - 1),
                'x': int(BOARDWIDTH / 2) - int(TEMPLATEWIDTH / 2),
                'y': -2, # start it above the board (i.e. less than 0)
                'color': random.randint(0, len(COLORS)-1)}
    return newPiece


def addToBoard(board, piece):
    # fill in the board based on piece's location, shape, and rotation
    for x in range(TEMPLATEWIDTH):
	   for y in range(TEMPLATEHEIGHT):
	       if PIECES[piece['shape']][piece['rotation']][y][x] != BLANK:
	                board[max(0,min(len(board) - 1,x + piece['x']))][max(0,min(len(board[0]) - 1, y + piece['y']))] = piece['color']


def getBlankBoard():
    # create and return a new blank board data structure
    board = []
    for i in range(BOARDWIDTH):
        board.append([BLANK] * BOARDHEIGHT)
    return board


def isOnBoard(x, y):
    return x >= 0 and x < BOARDWIDTH and y < BOARDHEIGHT


def isValidPosition(board, piece, adjX=0, adjY=0):
    # Return True if the piece is within the board and not colliding
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            isAboveBoard = y + piece['y'] + adjY < 0
            if isAboveBoard or PIECES[piece['shape']][piece['rotation']][y][x] == BLANK:
                continue
            if not isOnBoard(x + piece['x'] + adjX, y + piece['y'] + adjY):
                return False
            if board[x + piece['x'] + adjX][y + piece['y'] + adjY] != BLANK:
                return False
    return True

def isCompleteLine(board, y):
    # Return True if the line filled with boxes with no gaps.
    for x in range(BOARDWIDTH):
        if board[x][y] == BLANK:
            return False
    return True



def removeCompleteLines(board):
    # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1 # start y at the bottom of the board
    while y >= 0:
        if isCompleteLine(board, y):
            # Remove the line and pull boxes down by one line.
            for pullDownY in range(y, 0, -1):
                for x in range(BOARDWIDTH):
                    board[x][max(0,pullDownY)] = board[x][max(0,pullDownY-1)]
            # Set very top line to blank.
            for x in range(BOARDWIDTH):
                board[x][0] = BLANK
            numLinesRemoved += 1
            # Note on the next iteration of the loop, y is the same.
            # This is so that if the line that was pulled down is also
            # complete, it will be removed.
        y -= 1 # move on to check next row up
    return numLinesRemoved

def removeCompleteLines2(board):
    # Remove any completed lines on the board, move everything above them down, and return the number of complete lines.
    numLinesRemoved = 0
    y = BOARDHEIGHT - 1 # start y at the bottom of the board
    while y >= 0:
        if isCompleteLine(board, y):
            # Remove the line and pull boxes down by one line.
            numLinesRemoved += 1
        y-=1;
     
    return numLinesRemoved


def convertToPixelCoords(boxx, boxy):
    # Convert the given xy coordinates of the board to xy
    # coordinates of the location on the screen.
    return (XMARGIN + (boxx * BOXSIZE)), (TOPMARGIN + (boxy * BOXSIZE))


def drawBox(boxx, boxy, color, pixelx=None, pixely=None):
    # draw a single box (each tetromino piece has four boxes)
    # at xy coordinates on the board. Or, if pixelx & pixely
    # are specified, draw to the pixel coordinates stored in
    # pixelx & pixely (this is used for the "Next" piece).
    if color == BLANK:
        return
    if pixelx == None and pixely == None:
        pixelx, pixely = convertToPixelCoords(boxx, boxy)
    pygame.draw.rect(DISPLAYSURF, COLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 1, BOXSIZE - 1))
    pygame.draw.rect(DISPLAYSURF, LIGHTCOLORS[color], (pixelx + 1, pixely + 1, BOXSIZE - 4, BOXSIZE - 4))


def drawBoard(board):
    # draw the border around the board
    pygame.draw.rect(DISPLAYSURF, BORDERCOLOR, (XMARGIN - 3, TOPMARGIN - 7, (BOARDWIDTH * BOXSIZE) + 8, (BOARDHEIGHT * BOXSIZE) + 8), 5)

    # fill the background of the board
    pygame.draw.rect(DISPLAYSURF, BGCOLOR, (XMARGIN, TOPMARGIN, BOXSIZE * BOARDWIDTH, BOXSIZE * BOARDHEIGHT))
    # draw the individual boxes on the board
    for x in range(BOARDWIDTH):
        for y in range(BOARDHEIGHT):
            drawBox(x, y, board[x][y])


def drawStatus(score, level):
    # draw the score text
    scoreSurf = BASICFONT.render('Score: %s' % score, True, TEXTCOLOR)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 150, 20)
    DISPLAYSURF.blit(scoreSurf, scoreRect)

    # draw the level text
    levelSurf = BASICFONT.render('Level: %s' % level, True, TEXTCOLOR)
    levelRect = levelSurf.get_rect()
    levelRect.topleft = (WINDOWWIDTH - 150, 50)
    DISPLAYSURF.blit(levelSurf, levelRect)


def drawPiece(piece, pixelx=None, pixely=None):
    shapeToDraw = PIECES[piece['shape']][piece['rotation']]
    if pixelx == None and pixely == None:
        # if pixelx & pixely hasn't been specified, use the location stored in the piece data structure
        pixelx, pixely = convertToPixelCoords(piece['x'], piece['y'])

    # draw each of the boxes that make up the piece
    for x in range(TEMPLATEWIDTH):
        for y in range(TEMPLATEHEIGHT):
            if shapeToDraw[y][x] != BLANK:
                drawBox(None, None, piece['color'], pixelx + (x * BOXSIZE), pixely + (y * BOXSIZE))


def drawNextPiece(piece):
    # draw the "next" text
    nextSurf = BASICFONT.render('Next:', True, TEXTCOLOR)
    nextRect = nextSurf.get_rect()
    nextRect.topleft = (WINDOWWIDTH - 120, 80)
    DISPLAYSURF.blit(nextSurf, nextRect)
    # draw the "next" piece
    drawPiece(piece, pixelx=WINDOWWIDTH-120, pixely=100)


if __name__ == '__main__':

    main()
