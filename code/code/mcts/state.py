import copy
import random
from enum import Enum
from game_models import PropertyStatus, PropertyColor

class ActionType(Enum):
    BUY_PROPERTY = 0
    AUCTION_BID = 1
    BUILD_HOUSE = 2
    JAIL_STRATEGY = 3
    TRADE = 4
    INITIATE_TRADE = 5
    MORTGAGE = 6
    UNMORTGAGE = 7
    ROLL_DICE = 8
    END_TURN = 9

class Action:
    def __init__(self, action_type, data=None):
        self.action_type = action_type
        self.data = data  # Additional data relevant to the action
    
    def __str__(self):
        return f"{self.action_type.name}: {self.data}"

class State:
    ''' Class representing a state in the game of Monopoly for MCTS '''
    def __init__(self, game, player_index=None):
        self.game = copy.deepcopy(game)  # Deep copy to avoid modifying the original game
        self.current_player_index = player_index if player_index is not None else self.game.current_player_idx
        self.board = self.game.board
        self.players = self.game.players
        self.current_player = self.players[self.current_player_index]

    def get_possible_actions(self):
        """Return list of possible actions in this state"""
        actions = []
        player = self.current_player
        
        # Basic actions always available
        actions.append(Action(ActionType.END_TURN))
        
        # Add roll dice if not rolled yet
        '''if not self.game.dice_rolled:
            actions.append(Action(ActionType.ROLL_DICE))'''
        
        # If on unowned property and can afford it
        current_space = self.board.spaces[player.position]
        if (hasattr(current_space, 'owner') and 
            current_space.owner is None and 
            player.money >= current_space.price):
            actions.append(Action(ActionType.BUY_PROPERTY, current_space))
        
        # Check for properties to build houses on
        buildable_properties = self._get_buildable_properties()
        for prop in buildable_properties:
            actions.append(Action(ActionType.BUILD_HOUSE, prop))
        
        # Check for unmortgageable properties
        for prop in player.properties:
            if prop.status == PropertyStatus.MORTGAGED and player.money >= prop.unmortgage_cost:
                actions.append(Action(ActionType.UNMORTGAGE, prop))
        
        # Check for mortgageable properties
        for prop in player.properties:
            if prop.status != PropertyStatus.MORTGAGED and prop.houses == 0:
                actions.append(Action(ActionType.MORTGAGE, prop))
        
        # If in jail, add jail strategies
        if player.jail_turns > 0:
            actions.append(Action(ActionType.JAIL_STRATEGY, "1"))  # Pay to get out
            actions.append(Action(ActionType.JAIL_STRATEGY, "2"))  # Use get out of jail card
            actions.append(Action(ActionType.JAIL_STRATEGY, "3"))  # Roll for doubles
        
        # Check for trades
        for prop in player.properties:
            if prop.status != PropertyStatus.MORTGAGED:
                actions.append(Action(ActionType.INITIATE_TRADE, prop))
        
        return actions

    def _get_buildable_properties(self):
        """Helper to get properties where houses can be built"""
        buildable = []
        player = self.current_player
        
        # Group properties by color
        properties_by_color = {}
        for prop in player.properties:
            if hasattr(prop, 'color') and prop.color not in ['RAILROAD', 'UTILITY']:
                if prop.color not in properties_by_color:
                    properties_by_color[prop.color] = []
                properties_by_color[prop.color].append(prop)
        
        # Check which color groups are complete monopolies
        for color, props in properties_by_color.items():
            color_count = sum(1 for p in self.board.spaces if hasattr(p, 'color') and p.color == color)
            if len(props) == color_count:
                # Check if player can afford to build
                min_house_price = min(prop.house_price for prop in props)
                if player.money >= min_house_price:
                    # Add properties with fewest houses
                    min_houses = min(prop.houses for prop in props)
                    for prop in props:
                        if prop.houses == min_houses and prop.houses < 5:
                            buildable.append(prop)
        
        return buildable

    def apply_action(self, action):
        """Apply the given action to this state and return the resulting state"""
        new_state = self.clone()
        game = new_state.game
        player = new_state.current_player
        
        
        if action.action_type == ActionType.END_TURN:
            game.next_player()
        
        elif action.action_type == ActionType.ROLL_DICE:
            # Simulate dice roll
            game.roll_dice()
            
            # Handle landing on spaces
            space = game.board.spaces[player.position]
            if hasattr(space, 'owner') and space.owner and space.owner != player:
                # Pay rent
                rent = space.calculate_rent()
                player.money -= rent
                space.owner.money += rent
        
        elif action.action_type == ActionType.BUY_PROPERTY:
            property = action.data
            player.money -= property.price
            player.properties.append(property)
            property.owner = player
        
        elif action.action_type == ActionType.BUILD_HOUSE:
            property = action.data
            player.money -= property.house_price
            property.houses += 1
        
        elif action.action_type == ActionType.MORTGAGE:
            property = action.data
            player.money += property.mortgage_value
            property.is_mortgaged = True
        
        elif action.action_type == ActionType.UNMORTGAGE:
            property = action.data
            player.money -= property.unmortgage_cost
            property.is_mortgaged = False
        
        elif action.action_type == ActionType.JAIL_STRATEGY:
            strategy = action.data
            if strategy == "1":  # Pay to get out
                player.money -= 50
                player.jail_turns = 0
            elif strategy == "2":  # Use card
                if player.jail_free_cards > 0:
                    player.jail_free_cards -= 1
                    player.jail_turns = 0
            elif strategy == "3":  # Try rolling doubles
                # In simulation, assume 1/6 chance of getting out
                if random.random() < 1/6:
                    player.jail_turns = 0
                else:
                    player.jail_turns -= 1
                    if player.jail_turns == 0:
                        player.money -= 50  # Pay fine after 3rd turn
        
        # Check for bankruptcy
        if player.money < 0:
            self._handle_bankruptcy(new_state, player)
        
        return new_state
    
    def _handle_bankruptcy(self, state, player):
        """Handle player bankruptcy in simulation"""
        # Simple implementation - just mark player as bankrupt
        player.bankrupt = True
        
        # Transfer properties to bank/creditor
        for prop in player.properties:
            prop.owner = None
            prop.houses = 0
            prop.is_mortgaged = False

    def is_terminal(self):
        """Check if this is a terminal state (game over)"""
        # Game is over if only one player is not bankrupt
        active_players = [p for p in self.players if not p.bankrupt]
        return len(active_players) <= 1
    
    def get_reward(self, player_index):
        """Get reward for the specified player"""
        if self.is_terminal():
            active_players = [p for p in self.players if not p.bankrupt]
            if len(active_players) == 1 and active_players[0] == self.players[player_index]:
                return 1.0  # Win
            else:
                return -1.0  # Loss
        
        # Non-terminal state - use heuristic
        player = self.players[player_index]
        if player.bankrupt:
            return -1.0
        
        # Calculate net worth
        net_worth = player.money
        for prop in player.properties:
            if not prop.status == PropertyStatus.MORTGAGED:
                net_worth += prop.price
                if hasattr(prop, 'houses'):
                    net_worth += prop.houses * prop.house_price
        
        # Normalize to [0, 0.9] range (never as good as winning)
        max_possible_worth = 5000  # Arbitrary high value
        return 0.9 * min(net_worth / max_possible_worth, 1.0)

    def get_winner(self):
        """Return the winner if game is over, None otherwise"""
        if self.is_terminal():
            active_players = [p for p in self.players if not p.bankrupt]
            if len(active_players) == 1:
                return active_players[0]
        return None

    def clone(self):
        """Create a deep copy of this state"""
        new_state = State(self.game, self.current_player_index)
        return new_state