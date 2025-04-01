import unittest
from code.mcts.mcts import MCTS
from code.mcts.node import Node
from code.mcts.state import State

class TestMCTS(unittest.TestCase):
    
    def setUp(self):
        self.initial_state = State()  # Initialize with a default state
        self.mcts = MCTS(self.initial_state)

    def test_node_initialization(self):
        node = Node(state=self.initial_state)
        self.assertEqual(node.state, self.initial_state)
        self.assertIsNone(node.parent)
        self.assertEqual(len(node.children), 0)
        self.assertEqual(node.visit_count, 0)
        self.assertEqual(node.win_score, 0)

    def test_mcts_selection(self):
        node = Node(state=self.initial_state)
        self.mcts.root = node
        selected_node = self.mcts.select(node)
        self.assertIsInstance(selected_node, Node)

    def test_mcts_expansion(self):
        node = Node(state=self.initial_state)
        self.mcts.root = node
        self.mcts.expand(node)
        self.assertGreater(len(node.children), 0)

    def test_mcts_simulation(self):
        node = Node(state=self.initial_state)
        self.mcts.root = node
        result = self.mcts.simulate(node)
        self.assertIn(result, [True, False])  # Assuming simulation returns a boolean

    def test_mcts_backpropagation(self):
        node = Node(state=self.initial_state)
        self.mcts.root = node
        self.mcts.backpropagate(node, 1)  # Assuming a win score of 1
        self.assertEqual(node.visit_count, 1)
        self.assertEqual(node.win_score, 1)

if __name__ == '__main__':
    unittest.main()