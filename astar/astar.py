import copy
import sortedcontainers.sorteddict
from heapq import heappush, heappop, heapify


class Node:
    def __init__(self, state, parent):
        self.state = state
        self.parent = parent
        self.path_cost = 0 if parent is None else parent.path_cost + 1


class Evaluation:
    def __init__(self, num_of_expanded):
        self.num_of_expanded = num_of_expanded


def find_number(state, number):
    tup = [x for x in state if number in x][0]
    raw = state.index(tup)
    col = tup.index(number)
    return raw, col


def get_moves(state):
    row, col = find_number(state, 0)
    successors = []
    if row > 0:
        successors.append((row - 1, col))
    if row < len(state) - 1:
        successors.append((row + 1, col))
    if col > 0:
        successors.append((row, col - 1))
    if col < len(state[0]) - 1:
        successors.append((row, col + 1))
    return successors


# expand possible successors
def expand(state):
    moves = get_moves(state.state)
    open_list = []
    for move in moves:
        next_state = copy.deepcopy(state.state)

        row, col = find_number(next_state, 0)
        next_state[row][col] = next_state[move[0]][move[1]]
        next_state[move[0]][move[1]] = 0

        open_list.append(Node(next_state, state))
    return open_list


def is_goal(state, goal_state):
    for index in range(len(state)):
        if state[index] != goal_state[index]:
            return False
    return True


def create_path(state):
    path = [state.state]
    while state.parent is not None:
        path.insert(0, state.parent.state)
        state = state.parent
    return path


def evaluate_a_star(node, goal_state, heuristic):
    return node.path_cost + heuristic(node.state, goal_state)


def evaluate_greedy(node, goal_state, heuristic):
    return heuristic(node.state, goal_state)


def heuristic_misplaced_tiles(state, goal_state):
    h = 0
    for i in range(len(state)):
        for j in range(len(state[i])):
            if state[i][j] != 0 and state[i][j] != goal_state[i][j]:
                h += 1
    return h


def heuristic_manhattan_distance(state, goal_state):
    h = 0
    for i in range(len(state)):
        for j in range(len(state[i])):
            if state[i][j] != 0:
                row, col = find_number(goal_state, state[i][j])
                h += abs(row - i) + abs(col - j)
    return h


def run(root_state, goal_state, evaluate, heuristic):
    assert len(root_state) == len(goal_state)
    assert len(root_state[0]) == len(goal_state[0])

    done = []
    frontier = []

    root = Node(root_state, None)
    heappush(frontier, (evaluate(root, goal_state, heuristic), root))
    done.append(root_state)

    while len(frontier) != 0:
        (f, state) = heappop(frontier)

        if is_goal(state.state, goal_state):
            return create_path(state), Evaluation(len(done))

        successors = expand(state)
        done.append(state.state)

        for successor in successors:
            if successor.state in done:
                continue
            duplicates = [(x, y) for (x, y) in frontier if y.state == successor.state]
            if len(duplicates) != 0 and duplicates[0][1].path_cost > successor.path_cost:
                frontier.remove(duplicates[0])
                heapify(frontier)
            heappush(frontier, (evaluate(successor, goal_state, heuristic), successor))

    return None, Evaluation(len(done))





