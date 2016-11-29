import unittest
import astar
import slidepuzzle2


class MyTestCase(unittest.TestCase):

    def test_is_goal(self):
        root_state = [[1, 0],
                      [3, 2]]
        goal_state = [[1, 2],
                      [3, 0]]

        self.assertFalse(astar.is_goal(root_state, goal_state))

        root_state = [[7, 6, 5],
                      [8, 3, 2],
                      [1, 4, 0]]

        self.assertTrue(astar.is_goal(root_state, root_state))

    def test_heuristic_misplaced_tiles(self):
        state = [[7, 6, 5],
                 [8, 3, 2],
                 [1, 4, 0]]

        goal_state = [[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 0]]

        self.assertEquals(8, astar.heuristic_misplaced_tiles(state, goal_state))

    def test_heuristic_city_block(self):
        state = [[7, 2, 4],
                 [5, 0, 6],
                 [8, 3, 1]]

        goal_state = [[0, 1, 2],
                      [3, 4, 5],
                      [6, 7, 8]]

        self.assertEquals(18, astar.heuristic_manhattan_distance(state, goal_state))

    def test_get_moves(self):
        state = [[1, 2, 3],
                 [4, 5, 0],
                 [7, 8, 9]]
        open_list = astar.get_moves(state)

        self.assertTrue(len(open_list) == 3)
        self.assertTrue((0, 2) in open_list)
        self.assertTrue((1, 1) in open_list)
        self.assertTrue((2, 2) in open_list)

    def test_3(self):
        root_state = [[2, 3],
                      [1, 0]]

        goal_state = [[1, 2],
                      [3, 0]]

        path, evaluation = astar.run(root_state, goal_state, astar.evaluate_a_star, astar.heuristic_misplaced_tiles)
        self.assertEqual(len(path), 5)

        root_state = [[3, 2],
                      [1, 0]]
        goal_state = [[1, 2],
                      [3, 0]]

        path, evaluation = astar.run(root_state, goal_state, astar.evaluate_a_star, astar.heuristic_misplaced_tiles)
        self.assertEqual(path, None)

    def test_8(self):
        root_state = [[5, 2, 8],
                      [4, 1, 7],
                      [0, 3, 6]]

        goal_state = [[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 0]]

        path, evaluation = astar.run(root_state, goal_state, astar.evaluate_a_star, astar.heuristic_misplaced_tiles)
        self.assertEqual(len(path), 23)

    def test_8_with_city_block(self):
        root_state = [[5, 2, 8],
                      [4, 1, 7],
                      [0, 3, 6]]

        goal_state = [[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 0]]

        path, evaluation = astar.run(root_state, goal_state, astar.evaluate_a_star, astar.heuristic_manhattan_distance)
        self.assertEqual(len(path), 23)

    def test_if_city_block_performs_better(self):
        root_state = [[5, 2, 8],
                      [4, 1, 7],
                      [0, 3, 6]]

        goal_state = [[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 0]]

        path1, eval1 = astar.run(root_state, goal_state, astar.evaluate_a_star, astar.heuristic_misplaced_tiles)
        path2, eval2 = astar.run(root_state, goal_state, astar.evaluate_a_star, astar.heuristic_manhattan_distance)

        self.assertEqual(path1, path2)
        self.assertTrue(eval1.num_of_expanded > eval2.num_of_expanded)

    def test_greedy(self):
        root_state = [[5, 2, 8],
                      [4, 1, 7],
                      [0, 3, 6]]

        goal_state = [[1, 2, 3],
                      [4, 5, 6],
                      [7, 8, 0]]

        path1, eval1 = astar.run(root_state, goal_state, astar.evaluate_greedy, astar.heuristic_misplaced_tiles)
        path2, eval2 = astar.run(root_state, goal_state, astar.evaluate_greedy, astar.heuristic_manhattan_distance)

        self.assertNotEqual(len(path1), len(path2))

if __name__ == '__main__':
    unittest.main()
