import networkx as nx
import numpy as np
import sys


r = 3
c = 3

#board =np.array([[2, 8, 3], [1, 6, 4], [7, 0, 5]])

goalStateA = np.array([[1, 2, 3, ], [8, 0, 4], [7, 6, 5]])
goalStateB = np.array([[0, 1, 2, ], [3, 4, 5], [6, 7, 8]])


def getBlankPosition(board):

    for i in range(r):
        for j in range(c):
            if board[i][j] == 0:
                return (i, j)


def goalState(board, x, y):
    # type: (object, object, object) -> object
    r = len(board)
    c = len(board[0])

    count = 0

    for n in range(r):
        for m in range(c):

            br, bc = getBlankPosition(board)  # Avoiding the blank spot

            if x > n:
                continue
            elif x == n and y > m:
                continue

            elif board[br][bc] == board[n][m]:
                continue
            elif board[x][y] > board[n][m]:  # Avoiding to check the blank position
                count = count + 1
                # print('my legal moves are ', legal_moves(br,bc))
    return count


def createStateList(board):
    states = []

    for i in range(r):

        for j in range(c):
            # print('blank spot is ', br, bc)
            br, bc = getBlankPosition(board)
            if board[br][bc] == board[i][j]:
                continue

            states = states + [i, j]

    return states


def setStates(states,board):
    # making a list with states to check for the N which defined the goalstate
    #This  fuction decides which one the two goal states will be used based on the method described here http://www.8puzzle.com/8_puzzle_algorithm.html

   # ll = len(states)
    n = 0
  #  goalstate = []

    for i in xrange(0, 14, 2):  # hardcoded until a soltuion for  xrange(ll,lt,2) is found

        x = states[i]
        y = states[i + 1]

        count = goalState(board, x, y)
        n = n + count

    if n % 2 == 0:  # if N is odd then goalStateA if N even then goalStateB
        goalstate = goalStateB
    else:
        goalstate = goalStateA

    return goalstate


def legal_moves(board):                     # Setting a list of legal moves baased on the current position of the blank spot
    # temp=board
    moves = []
    row, col = getBlankPosition(board)

    if row > 0:  # up
        moves = moves + ['up']
        # temp[row][col], temp[row-1][col]= temp[row-1][col],temp[row][col]
    if col > 0:  # left
        moves = moves + ['left']
        # temp[row][col], temp[row][col-1]= temp[row][col-1],temp[row][col]
    if row < 2:  # down
        moves = moves + ['down']
        # temp[row][col], temp[row+1][col]= temp[row+1][col],temp[row][col]
    if col < 2:  # right
        moves = moves + ['right']
        # temp[row][col], temp[row][col+1]= temp[row][col+1],temp[row][col]

    return moves


def setMove(move, row, col,board):          #Setting the moves based on the list of legal moves i have retrieved
    temp = board

    if move == 'up':
        temp[row][col], temp[row - 1][col] = temp[row - 1][col], temp[row][col]
        # move.remove('up')
    elif move == 'left':
        temp[row][col], temp[row][col - 1] = temp[row][col - 1], temp[row][col]
        #  move.remove('left')
    elif move == 'down':
        temp[row][col], temp[row + 1][col] = temp[row + 1][col], temp[row][col]
        # move.remove('down')
    elif move == 'right':
        temp[row][col], temp[row][col + 1] = temp[row][col + 1], temp[row][col]
        #  move.remove('right')
    return temp

def create_node(board, parent,sibling, moves, depth,visited):
    return Node(board, parent, sibling, moves, depth,visited)

def cur_state(node,visited,goal,start):
    goalReached = False

    if node.parent==None and start==True:
        state = node.board.ravel()  # make temp flat
        state = int(''.join(map(str, state)))
        visited.add(state)
        start=False

    elif len(node.moves) != 0:
        temp = np.array(node.board)
        br, bc = getBlankPosition(temp)
        temp1 = setMove(node.moves[0], br, bc, temp)  # making my move
      #  print(node.moves[0])
        node.moves.pop(0)
        state = temp1.ravel()  # make temp flat
        print "1st state", state
        state = int(''.join(map(str, state)))
        print "2nd state", state
        v=False



    if state not in visited:

         visited.add(state)
         # node.visited = True
         new_moves= legal_moves(temp1)
         d = node.depth + 1
         print ("appending ", temp1)
         children = node.add_child(create_node(temp1, node, None, new_moves, d, False))
    else:
        v=True
    print goal
    if np.all(node.board == goal):  # Checking is the current board is winning
        print('I won!!')
        goalReached = True

    return start, goalReached, v


def bfs(node, goal, depth):
    depth_limit = depth
    goalReached=False   #Goal Reached boolean
    nodes = []
    visited = set()
    visitedB=False   #Visited Boolean
    OFM=False       #Out Of Moves Boolean
    start=True
    d=0
    goalStateB=False

    while goalReached==False:


        if len(nodes)==0 and start==True:       #Appending the root node

            start,goalReached, v = cur_state(node,visited,goal,start)
            nodes.append(node)

        elif len(node.moves)!=0 and node.depth<depth_limit:

            start, goalReached, v = cur_state(node, visited, goal,start)
            if node.has_children():
                child = node.children.pop(0)
                nodes.append(child)
            elif goalReached:
                break
           # elif v:
             #   m = list(node.moves)
               # m.pop(0)
        elif len(node.moves)== 0 and node.depth < depth_limit:
            if len(nodes) > 1:
                nodes.pop(0)
                node = nodes[0]
            else:
                print "I explored the tree to the given maximum depth"
                break
        elif len(node.moves)==0 and node.parent!=None:
            node=node.parent
        elif node.depth == depth_limit:
            if len(nodes) > 1:
                nodes.pop(0)
                node=nodes[0]
            else:
                print "I explored the tree to the given maximum depth"
                break


def dfs(node, goal, depth):
    depth_limit = depth
    goalReached=False   #Goal Reached boolean
    nodes = []
    visited = set()
    visitedB=False   #Visited Boolean
    OFM=False       #Out Of Moves Boolean
    start=True
    d=0
    goalStateB=False

    while goalReached==False:


        if len(nodes)==0 and start==True:       #Appending the root node

            start,goalReached, v = cur_state(node,visited,goal,start)
            nodes.append(node)

        elif len(node.moves)!=0 and node.depth<depth_limit:
            start, goalReached, v = cur_state(node, visited, goal,start)
            if node.has_children():
                node = node.children.pop(0)
                nodes.append(node)
           # elif v:
             #   m = list(node.moves)
               # m.pop(0)

        elif len(node.moves)==0 and node.parent!=None:
            node=node.parent
        elif node.depth == depth_limit:
            node=node.parent
        elif len(node.moves)==0 and node.parent==None :
            print "explored the tree to its depth limit and i am out of moves"
            break




# Node data structure
class Node:
    def __init__(self, board, parent, sibling, moves, depth,visited):
        self.parent = parent
        self.depth = depth
        self.board = board
        self.moves = moves
        self.sibling=sibling
        self.children=[]
        self.visited=visited

    def add_child(self, node):
        self.children.append(node)

    def get_children(self):
        return self.children

    def get_rev_children(self):
        children = self.children[:]
        children.reverse()
        return children

    def get_board(self):
        return self.board

    def has_children(self):
        if len(self.children)!=0:
            return self.children

    def get_children(self):

            i=len(self.children)-1
            return self.children[i]

    def get_i_child(self,i):
        return self.children[i]

    def get_parent(self):
        if self.parent:
            return self.parent


def main():
    states = []

    board = np.array([[1, 4, 0], [3, 2, 5], [8, 6, 7]])
    #board =np.array([[2, 8, 3], [1, 6, 4], [7, 0, 5]])
    #board = np.array([[1, 2, 3, ], [4, 0, 5], [6, 7, 8]])
    #board = np.array([[2, 8,3], [1, 6, 4], [7, 0, 5]])
    #board = np.array([[3, 1,2], [0, 4, 5], [6, 7 , 8]])
    #board = np.array([[1, 0, 3, ], [4, 2, 5], [6, 7, 8]])


    moves = legal_moves(board)


    root = Node(board, None, None, moves, 0,False)

    states = createStateList(board)

    s = setStates(states,board)
    print s
    #dfs(root, s, 20)


    bfs(root, s, 50)

if __name__ == '__main__':
    main()
