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

def cur_state(board):
    moves = legal_moves(board)
    return moves

def bfs(node, goal, depth):
    depth_limit = depth
    goalReached=False   #Goal Reached boolean
    nodes = []
    visited = set()
    visitedB=False   #Visited Boolean
    OFM=False       #Out Of Moves Boolean
    start=True
    d=0

    while goalReached==False or OFM:

        if len(nodes)==0 and start==True:
           start=False
           nodes.append(node)

        if node.depth <= depth_limit:

            if len(node.moves)==0 and node.has_children():

                if (node.parent==None and len(node.children)!=0) or (node.parent==None and len(node.parent.children)==0):           #for the root
                    node = node.children.pop(0)
                    nodes.append(node)
                elif node.parent!=None and len(node.parent.children)==0:
                    nodes.pop(0)
                    node=nodes[0]
                    node= node.children[0]
                elif node.parent!=None and (node.parent.has_children() and len(node.parent.moves) == 0):
                    node = node.parent.children.pop(0)  # take the next sibling
                    nodes.append(node)
            elif len(nodes)!=0:
                if node.moves==0 and node.children==0:
                    node=nodes.pop(0)
            elif len(nodes)==1:
                if node.moves==0 and node.children==0:
                    print "out of moves and i am ending the game here"
                    OFM=True
                break
        elif node.depth > depth_limit:
            print "I've reached the maximum depth"
            break



        if np.all(node.board == goal):                  #Checking is the current board is winning
            print('I won!!')
            goalReached=True

        if len(nodes) == 0: return None
        tmp = np.array(node.board)

        br, bc = getBlankPosition(tmp)  # getting current position
        node.moves=cur_state(tmp)
       # temp = setMove(node.moves[0], br, bc, temp)  # making my move
        moves_size=len(node.moves)


        for i in range(moves_size):
            temp = np.array(node.board)
            temp_move = setMove(node.moves[0], br, bc, temp)
            node.moves.pop(0)
            state = temp_move.ravel()  # make temp flat
            state = int(''.join(map(str, state)))
            if state not in visited:
                if np.all(state==goal):
                    print "win win"
                    break
                else:
                    visited.add(state)
                    print "state is in the bucket", state
                    #node.visited = True
                    new_moves = cur_state(temp_move)
                    d = node.depth + 1
                    children = node.add_child(create_node(temp_move, node, None, new_moves, d, False))
            else:
                print "This state was visited already, skipping to the next move"

        node.visited = True


def dfs(node, goal, depth):
    depth_limit = depth
    goalReached=False   #Goal Reached boolean
    nodes = []
    visited = set()
    visitedB=False   #Visited Boolean
    OFM=False       #Out Of Moves Boolean
    start=True
    d=0

    while goalReached==False:

        if len(nodes)==0 and start==True:       #Appending the root node
            start=False
            nodes.append(node)
        elif node.has_children() and node.visited==False:       #If the currently focused node has children, then append the first child . The node focuses on the parent which is in position node_lendth-1
            node.visited=True
            node=node.get_children()
            nodes.append(node)
        elif node.has_children() and node.parent==None:       #If the currently focused node has children, then append the first child . The node focuses on the parent which is in position node_lendth-1
            node.visited=True
            node=node.get_children()
            nodes.append(node)
        elif node.visited and OFM:  # If the state of the node has been visited and there are no available moves, remove the node to iterate backwards into the tree
            node = nodes.pop()
            node = node.get_parent()
            node.visited=False
            OFM=False
        elif node.visited and OFM==False:                                  #If the state was visited continue with the same node and the rest of it's available moves
           # node=node.get_parent()
            node.visited=False
            print('Still have moves')
        elif len(nodes)==0:
            print('I am out of moves')
            break



        print('my board', node.board)

        if np.all(node.board == goal):                  #Checking is the current board is winning
            print('I won!!')
            goalReached=True

        if len(nodes) == 0: return None
        temp = np.array(node.board)

        if node.depth <= depth_limit:

            if len(node.moves)!= 0:
                temp1=temp
                br,bc=getBlankPosition(temp1)    #getting current position
                temp1=setMove(node.moves[0],br,bc,temp)   #making my move
                node.moves.pop(0)
                state = temp1.ravel()     #make temp flat
                state = int(''.join(map(str, state)))
            if state not in visited:

                if np.all(state == goal):                  #Checking is the current board is winning
                    print('I won!!')
                    goalReached=True
                    break
                else:
                    visited.add(state)
                    #node.visited = True
                    new_moves = cur_state(temp1)
                    d = node.depth +1
                    children=node.add_child(create_node(temp1, node, None, new_moves, d,False))

            elif len(node.moves)!=0:
                OFM=False
                node.visited = True
                continue
            elif len(node.moves)==0:
                OFM=True
                node.visited=True
             #   node = nodes.pop()
                continue
        elif node.depth==depth_limit:                       #TB fixed
            print('Checking the depth', node.depth)
            node=nodes.pop()
            node=node.get_parent()
         #   node.visited=True

            continue
        elif node.depth>depth_limit:
            print('I am out of moves. My goal is' , goal ,' These are the states visited ', visited)






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

    #board = np.array([[1, 4, 0], [3, 2, 5], [8, 6, 7]])
    #board =np.array([[2, 8, 3], [1, 6, 4], [7, 0, 5]])
    board = np.array([[1, 2, 3, ], [4, 0, 5], [6, 7, 8]])
    #board = np.array([[2, 8,3], [1, 6, 4], [7, 0, 5]])

    moves = legal_moves(board)

    root = Node(board, None, None, moves, 0,False)

    states = createStateList(board)

    s = setStates(states,board)

    #dfs(root, s, 3)


    bfs(root, s, 1)

if __name__ == '__main__':
    main()
