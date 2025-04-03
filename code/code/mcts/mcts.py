import time
import random
from .node import MCTSNode

class MCTS:
    def __init__(self, state, max_iterations=100, max_time=1.0, exploration_weight=1.41):
        self.root = MCTSNode(state)
        self.max_iterations = max_iterations
        self.max_time = max_time  # Maximum time in seconds
        self.exploration_weight = exploration_weight
    
    def search(self):
        """Run the MCTS algorithm to find the best action"""
        start_time = time.time()
        iteration = 0
        
        # Run until time or iteration limit
        while (iteration < self.max_iterations and 
               time.time() - start_time < self.max_time):
            # Selection and expansion
            node = self.select_and_expand()
            
            # Simulation
            result = self.simulate(node.state)
            
            # Backpropagation
            self.backpropagate(node, result)
            
            iteration += 1
        
        # Return best child based on visits (more robust than value)
        return self.best_action()
    
    def select_and_expand(self):
        """Select a node to expand using UCB1, then expand it"""
        node = self.root
        
        # Selection: traverse tree until we find a node that isn't fully expanded
        # or is terminal
        while not node.is_terminal() and node.is_fully_expanded():
            node = node.select_child(self.exploration_weight)
        
        # Expansion: if node is not terminal, expand it by adding a child
        if not node.is_terminal():
            node = node.expand()
        
        return node
    
    def simulate(self, state):
        """Run a random simulation from the given state to a terminal state"""
        # For performance, use a cut-off depth rather than simulating to terminal state
        depth = 0
        max_depth = 20  # Adjust based on game complexity
        
        current_state = state.clone()
        
        # Rollout until terminal state or max depth
        while not current_state.is_terminal() and depth < max_depth:
            # Get possible actions and select one randomly
            actions = current_state.get_possible_actions()
            if not actions:
                break
                
            action = random.choice(actions)
            current_state = current_state.apply_action(action)
            depth += 1
        
        # Return the reward for the player who started the simulation
        player_index = self.root.player_index
        return current_state.get_reward(player_index)
    
    def backpropagate(self, node, result):
        """Backpropagate the simulation result up the tree"""
        while node is not None:
            node.update(result)
            node = node.parent
    
    def best_action(self):
        """Return the best action based on the most visited child"""
        if not self.root.children:
            return None
            
        # Use visits rather than UCB for final selection (more robust)
        best_child = max(self.root.children, key=lambda c: c.visits)
        return best_child.action