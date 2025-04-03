import math
import random

class MCTSNode:
    ''' Node in the MCTS tree representing a game state '''
    def __init__(self, state, parent=None, action=None):
        self.state = state
        self.parent = parent
        self.action = action  # Action that led to this state
        self.children = []
        self.visits = 0
        self.value = 0.0
        self.untried_actions = state.get_possible_actions()
        self.player_index = state.current_player_index
    
    def select_child(self, exploration_weight=1.0):
        """Select a child node using UCB1 formula"""
        # UCB1 formula: v_i + C * sqrt(ln(N) / n_i)
        # where v_i is the value of the child, N is parent visits,
        # n_i is child visits, and C is the exploration weight
        
        log_visits = math.log(self.visits) if self.visits > 0 else 0
        
        def ucb_score(child):
            if child.visits == 0:
                return float('inf')  # Ensure unvisited nodes are selected first
            
            exploitation = child.value / child.visits
            exploration = exploration_weight * math.sqrt(log_visits / child.visits)
            return exploitation + exploration
        
        return max(self.children, key=ucb_score)
    
    def expand(self):
        """Expand the node by adding a child node for an untried action"""
        if not self.untried_actions:
            return None
            
        action = self.untried_actions.pop(random.randrange(len(self.untried_actions)))
        next_state = self.state.apply_action(action)
        child = MCTSNode(next_state, parent=self, action=action)
        self.children.append(child)
        return child
    
    def update(self, result):
        """Update node statistics with the simulation result"""
        self.visits += 1
        self.value += result
        
    def is_fully_expanded(self):
        """Check if all possible actions have been tried"""
        return len(self.untried_actions) == 0
    
    def is_terminal(self):
        """Check if this node represents a terminal state"""
        return self.state.is_terminal()