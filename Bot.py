import random
from game_models import Property, PropertyColor, PropertyStatus
import torch.nn as nn
import torch.optim as optim
from enum import Enum
import torch


global parameters
parameters = {
        "risk_tolerance": random.random(),
        "property_focus": random.random(),
        "development_focus": random.random(),
        "cash_reserve_preference": random.random(),
        "trade_willingness": random.random(),
        "monopoly_focus": random.random(),
        "railroad_utility_interest": random.random()
    } 


class Bot:
    def __init__(self, player, game, parameters=parameters, display=True, property=None):
        self.player = player
        self.game = game
        self.display = display
        
        self.risk_tolerance = parameters['risk_tolerance']
        self.property_focus = parameters['property_focus']
        self.development_focus = parameters['development_focus']
        self.cash_reserve_preference = parameters['cash_reserve_preference']
        self.trade_willingness = parameters['trade_willingness']
        self.monopoly_focus = parameters['monopoly_focus']
        self.railroad_utility_interest = parameters['railroad_utility_interest']

        # Generate a bot personality type based on parameters
        self.personality_type = self._determine_personality()
        
        
    def _determine_personality(self):
        """Set a personality type based on the randomized parameters"""
        if self.risk_tolerance > 0.7 and self.property_focus > 0.7:
            return "Aggressive Expander"
        elif self.development_focus > 0.7 and self.monopoly_focus > 0.7:
            return "Builder"
        elif self.cash_reserve_preference > 0.7:
            return "Conservative"
        elif self.trade_willingness > 0.7:
            return "Trader"
        elif self.railroad_utility_interest > 0.7:
            return "Utility Collector"
        else:
            return "Balanced Player"
        
    def decide_buy_property(self, property):
        """Decide whether to buy a property."""
        # Always buy if plenty of money, adjusted by cash reserve preference
        min_reserve = 500 * self.cash_reserve_preference
        if self.player.money > property.price + min_reserve:
            return True
        
        # More likely to buy railroads and utilities if interested in them
        if property.color in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
            return random.random() < 0.5 + (0.5 * self.railroad_utility_interest)
        
        # Check if we already own properties of this color, adjusted by monopoly focus
        same_color_count = sum(1 for p in self.player.properties if p.color == property.color)
        if same_color_count > 0:
            monopoly_chance = 0.5 + (0.3 * self.monopoly_focus) + (0.1 * same_color_count)
            return random.random() < monopoly_chance
        
        # Base decision on risk tolerance, property focus and money available
        purchase_chance = self.risk_tolerance * self.property_focus
        return random.random() < purchase_chance and self.player.money > property.price * (1.0 + self.cash_reserve_preference)

    def decide_auction_bid(self, property, current_bid):
        """Decide how much to bid in an auction."""
        # Maximum bid based on property focus and risk tolerance
        max_willing_to_pay = property.price * (0.7 + self.property_focus * 0.6)
        
        # Bid higher if we already own properties of this color
        same_color_count = sum(1 for p in self.player.properties if p.color == property.color)
        if same_color_count > 0:
            monopoly_bonus = self.monopoly_focus * 0.3 * same_color_count
            max_willing_to_pay *= (1 + monopoly_bonus)
        
        # Keep a reserve based on preference
        reserve_amount = 50 + (self.cash_reserve_preference * 200)
        
        # Don't bid more than we have minus reserve
        max_willing_to_pay = min(max_willing_to_pay, self.player.money - reserve_amount)
        
        if max_willing_to_pay <= current_bid:
            return 0  # Pass
        
        # Bid somewhere between current bid and max willing, based on risk tolerance
        bid_range = max_willing_to_pay - current_bid
        bid_percentage = 0.3 + (self.risk_tolerance * 0.5)  # More aggressive = higher bids
        new_bid = current_bid + max(1, int(bid_range * bid_percentage))
        return new_bid
 
    def decide_trade(self, my_property, their_property, cash_amount):
        """Decide whether to accept a trade offer."""
        # Low trade willingness means more likely to reject trades
        if random.random() > self.trade_willingness * 1.5:  # Scale up to make trades happen
            return False
            
        # Value of properties 
        my_prop_value = my_property.price * (0.5 if my_property.status == PropertyStatus.MORTGAGED else 1.0)
        their_prop_value = their_property.price * (0.5 if their_property.status == PropertyStatus.MORTGAGED else 1.0)
        
        # Check if we have almost a monopoly with their property
        gain_monopoly = False
        same_color_props = sum(1 for p in self.player.properties if p.color == their_property.color)
        total_in_color = sum(1 for p in self.game.board.spaces if hasattr(p, 'color') and p.color == their_property.color)
        if same_color_props + 1 == total_in_color:
            gain_monopoly = True
        
        # Check if we're giving away part of a monopoly
        lose_monopoly = False
        my_color_props = sum(1 for p in self.player.properties if p.color == my_property.color)
        total_in_my_color = sum(1 for p in self.game.board.spaces if hasattr(p, 'color') and p.color == my_property.color)
        if my_color_props == total_in_my_color:
            lose_monopoly = True
        
        # Adjust values based on strategic importance and monopoly focus
        if gain_monopoly:
            their_prop_value *= 1.0 + (self.monopoly_focus * 1.0)
        if lose_monopoly:
            my_prop_value *= 1.0 + (self.monopoly_focus * 1.0)
        
        # Consider the cash component
        total_value_for_me = their_prop_value - my_prop_value + cash_amount
        
        # Also consider if we have enough cash, based on cash reserve preference
        min_cash = 100 + (self.cash_reserve_preference * 300)
        if cash_amount < 0 and self.player.money < -cash_amount + min_cash:
            return False
        
        # Accept if it's a good deal or we're desperate for cash
        return total_value_for_me > 0 or (cash_amount > 0 and self.player.money < min_cash)

    def initiate_trade(self):
        """Initiate a trade with another player to complete color sets."""

        # Less willing traders initiate fewer trades
        if random.random() > self.trade_willingness:
            return None
            
        # Don't try to trade if we have very little money
        min_cash = 100 + (self.cash_reserve_preference * 200)
        if self.player.money < min_cash:
            return None
            
        # Find properties that would complete our color sets
        potential_monopolies = {}
        
        # Count how many properties we have of each color
        owned_by_color = {}
        for prop in self.player.properties:
            if prop.color not in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
                if prop.color not in owned_by_color:
                    owned_by_color[prop.color] = 0
                owned_by_color[prop.color] += 1
        
        # Find how many are in each complete set
        color_counts = {}
        for space in self.game.board.spaces:
            if hasattr(space, 'color') and space.color not in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
                if space.color not in color_counts:
                    color_counts[space.color] = 0
                color_counts[space.color] += 1
        
        # Find colors where we're one property away from a monopoly
        for color, count in owned_by_color.items():
            # Safely check if the color exists in color_counts before comparing
            if color in color_counts and count == color_counts[color] - 1:
                potential_monopolies[color] = color_counts[color]
        
        # If no near-monopolies but interested in railroads/utilities, try those
        if not potential_monopolies and self.railroad_utility_interest > 0.6:
            if any(p.color == PropertyColor.RAILROAD for p in self.player.properties):
                # Try to get more railroads
                potential_monopolies[PropertyColor.RAILROAD] = 4
            elif any(p.color == PropertyColor.UTILITY for p in self.player.properties):
                # Try to get more utilities
                potential_monopolies[PropertyColor.UTILITY] = 2
        
        if not potential_monopolies:
            return None  # No good trading opportunities
        
        # Find the missing properties and their owners
        targets = []
        for color in potential_monopolies:
            # Find properties of this color not owned by us
            for space in self.game.board.spaces:
                if hasattr(space, 'color') and space.color == color:
                    if space.owner and space.owner != self.player and not space.owner.bankrupt:
                        # Make sure this property isn't already in our properties list
                        if space not in self.player.properties:
                            targets.append((space, space.owner))
        
        if not targets:
            return None  # No targetable properties
        
        # Sort targets by value (higher is better)
        targets.sort(key=lambda x: x[0].price, reverse=True)
        
        # Try each target
        for target_prop, target_owner in targets:
            # Find what we could offer in exchange
            offer_props = []
            for prop in self.player.properties:
                # Don't offer properties from potential monopolies
                if prop.color not in potential_monopolies:
                    # Don't offer railroads or utilities unless we have extras or don't care about them
                    if prop.color == PropertyColor.RAILROAD:
                        railroad_count = sum(1 for p in self.player.properties if p.color == PropertyColor.RAILROAD)
                        if railroad_count <= 1 and self.railroad_utility_interest > 0.5:
                            continue
                    elif prop.color == PropertyColor.UTILITY:
                        utility_count = sum(1 for p in self.player.properties if p.color == PropertyColor.UTILITY)
                        if utility_count <= 1 and self.railroad_utility_interest > 0.5:
                            continue
                            
                    # Don't offer properties with houses/hotels
                    if (hasattr(prop, 'houses') and prop.houses > 0) or (hasattr(prop, 'hotel') and prop.hotel):
                        continue
                        
                    offer_props.append(prop)
            
            # No properties to offer
            if not offer_props:
                continue
                
            # Sort offer properties by how valuable they are to us (less valuable first)
            offer_props.sort(key=lambda p: p.price)
            
            # Try to find a fair trade
            for offer_prop in offer_props:
                # Calculate value difference
                value_diff = target_prop.price - offer_prop.price
                
                # Adjust for mortgaged properties
                if target_prop.status == PropertyStatus.MORTGAGED:
                    value_diff -= target_prop.mortgage_value * 0.1  # Unmortgaging cost
                if offer_prop.status == PropertyStatus.MORTGAGED:
                    value_diff += offer_prop.mortgage_value * 0.1  # They'd have to pay to unmortgage
                
                # Determine cash adjustment based on trade willingness
                cash_amount = 0
                max_cash_percentage = 0.3 + (self.trade_willingness * 0.5)  # More willing = more cash offered
                
                if value_diff > 0:  # We need to add cash
                    cash_amount = min(value_diff, self.player.money * max_cash_percentage)
                elif value_diff < 0:  # We should receive cash
                    cash_amount = max(value_diff, -target_owner.money * max_cash_percentage)
                
                # Use game's color system for the trade offer
                
                
                # Make the trade offer
                if self.display:
                    colors = self.game.colors
                    
                    print(f"\n{colors['bot']}BOT TRADE ({self.personality_type}): {colors['player']}{self.player.name} {colors['title']}offers {colors['player']}{target_owner.name} {colors['title']}a trade:{colors['reset']}")
                    print(f"{colors['info']}Offering: {colors['property']}{offer_prop.name}{colors['reset']}")
                    print(f"{colors['info']}Requesting: {colors['property']}{target_prop.name}{colors['reset']}")
                    
                    if cash_amount > 0:
                        print(f"{colors['info']}{self.player.name} offers {colors['money']}${int(cash_amount)}{colors['reset']} cash")
                    elif cash_amount < 0:
                        print(f"{colors['info']}{self.player.name} requests {colors['money']}${int(-cash_amount)}{colors['reset']} cash")
                    
                # For AI opponents, use their decide_trade method
                if target_owner.is_bot:
                    bot = target_owner.bot
                    accepted = bot.decide_trade(target_prop, offer_prop, -cash_amount)
                    print(f"{colors['bot']}Bot {target_owner.name} ({bot.personality_type}) is evaluating the trade...{colors['reset']}") if self.display else None
                else:
                    # For human players, ask for input
                    accepted = input(f"\n{colors['prompt']}{target_owner.name}, do you accept this trade? (y/n): {colors['reset']}").lower() == 'y' if self.display else False
                
                if accepted:
                    # Execute the trade
                    self.player.properties.remove(offer_prop)
                    target_owner.properties.remove(target_prop)
                    
                    self.player.properties.append(target_prop)
                    target_owner.properties.append(offer_prop)
                    
                    offer_prop.owner = target_owner
                    target_prop.owner = self.player
                    
                    if cash_amount > 0:
                        self.player.pay(int(cash_amount))
                        target_owner.receive(int(cash_amount))
                    elif cash_amount < 0:
                        target_owner.pay(int(-cash_amount))
                        self.player.receive(int(-cash_amount))
                    
                    print(f"\n{colors['success']}Trade completed! {colors['player']}{self.player.name} {colors['success']}traded {colors['property']}{offer_prop.name} {colors['success']}for {colors['property']}{target_prop.name}{colors['reset']}.") if self.display else None
                    if cash_amount != 0 and self.display:
                        who_paid = f"{colors['player']}{self.player.name}{colors['money']} paid" if cash_amount > 0 else f"{colors['player']}{target_owner.name}{colors['money']} paid"
                        print(f"{who_paid} ${int(abs(cash_amount))}{colors['reset']}.") if self.display else None
                    
                    return True  # Successfully made a trade
                else:
                    print(f"{colors['error']}Trade rejected by {colors['player']}{target_owner.name}{colors['reset']}.") if self.display else None
        
            return False  # No trades were accepted

        
    def decide_jail_strategy(self):
        """Decide how to handle being in jail."""
        # Use get out of jail card if available
        if self.player.jail_free_cards > 0:
            return "2"
        
        # Pay the fine if we have plenty of money or are impatient (low cash reserve preference)
        cash_threshold = 300 + (self.cash_reserve_preference * 500)
        if self.player.money > cash_threshold:
            return "3"
        
        # High risk tolerance players may pay to get out
        if random.random() < self.risk_tolerance * 0.5:
            return "3"
        
        # Otherwise, try to roll doubles
        return "1"

    def decide_house_purchases(self):
        """Decide whether and where to buy houses."""
        # Minimum cash reserve based on preference
        min_reserve = 200 + (self.cash_reserve_preference * 300)
        if self.player.money < min_reserve:
            return None
        
        # Group properties by color
        properties_by_color = {}
        for prop in self.player.properties:
            if prop.color not in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
                if prop.color not in properties_by_color:
                    properties_by_color[prop.color] = []
                properties_by_color[prop.color].append(prop)
        
        # Find complete sets
        complete_sets = {}
        for color, props in properties_by_color.items():
            color_count = sum(1 for p in self.game.board.spaces if hasattr(p, 'color') and p.color == color)
            if len(props) == color_count:
                complete_sets[color] = props
        
        if not complete_sets:
            return None
        
        # Prioritize based on position, current houses, and development focus
        best_set = None
        best_score = -1
        
        for color, props in complete_sets.items():
            avg_position = sum(p.position for p in props) / len(props)
            avg_houses = sum(p.houses for p in props) / len(props)
            
            # Score based on position, existing development, and affordability
            position_score = avg_position / 40  # Normalize to 0-1
            development_score = (3 - avg_houses) / 3  # Prefer less developed (more room to build)
            affordability = min(self.player.money / (props[0].house_price * len(props)), 1.0)
            
            # Adjust weight based on development focus
            position_weight = 0.3 + (self.risk_tolerance * 0.2)  # Risky players care more about position
            development_weight = 0.3
            affordability_weight = 0.2 + (self.cash_reserve_preference * 0.2)  # Conservative players care more about affordability
            
            score = (position_score * position_weight + 
                    development_score * development_weight + 
                    affordability * affordability_weight) * self.development_focus
            
            if score > best_score:
                best_score = score
                best_set = props
        
        if not best_set:
            return None
        
        # Find the property with the fewest houses
        best_set.sort(key=lambda p: p.houses)
        return best_set[0]

    def decide_mortgage_property(self, amount_needed):
        """Decide which property to mortgage to raise funds."""
        if not self.player.properties:
            return False

        # First, look for properties with houses/hotels to sell
        properties_with_buildings = [p for p in self.player.properties 
                      if (hasattr(p, 'houses') and p.houses > 0) or 
                         (hasattr(p, 'hotel') and p.hotel)]
        
        # Sort buildings by value (sell least valuable first)
        properties_with_buildings.sort(key=lambda p: p.house_price)
        
        # Try selling houses/hotels first
        properties_to_mortgage = []
        raised_amount = 0
        
        for prop in properties_with_buildings:
            if raised_amount >= amount_needed:
                return True
            if prop.hotel:
                # Selling a hotel yields half the house price * 5
                raised_amount += (prop.house_price // 2) * 5
                prop.remove_hotel()

            elif prop.houses > 0:
                # Calculate how many houses we need to sell
                houses_to_sell = min(prop.houses, 
                        ((amount_needed - raised_amount) + (prop.house_price // 2) - 1) // (prop.house_price // 2))
                raised_amount += (prop.house_price // 2) * houses_to_sell
                for _ in range(int(houses_to_sell)):
                    prop.remove_house()
        
        # If selling buildings wasn't enough, mortgage properties
        # Sort properties by how valuable they are to keep (mortgaging least valuable first)
        candidates = [p for p in self.player.properties 
                if p.status != PropertyStatus.MORTGAGED and p.houses == 0 and not p.hotel]
            
        # Calculate a score for each property based on bot parameters
        def property_value_score(prop):
            # Higher score = less likely to mortgage
            score = prop.price / 500.0  # Base value (0-1 range typically)
            
            # Bonus for properties in near-monopolies
            same_color_count = sum(1 for p in self.player.properties if p.color == prop.color)
            total_in_color = sum(1 for p in self.game.board.spaces if hasattr(p, 'color') and p.color == prop.color)
            monopoly_factor = same_color_count / total_in_color if total_in_color > 0 else 0
            score += monopoly_factor * self.monopoly_focus
            
            # Railroads and utilities get bonus if the bot values them
            if prop.color in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
                score += self.railroad_utility_interest * 0.5
            
            # Properties in developed areas are more valuable
            score += (prop.position / 40.0) * self.risk_tolerance * 0.5
            
            return score
            
        # Sort so lowest scored (least valuable) properties are mortgaged first
        candidates.sort(key=property_value_score)
        
        # Mortgage properties until we've raised enough money
        for prop in candidates:
            properties_to_mortgage.append(prop)
            raised_amount += prop.mortgage_value
            if raised_amount >= amount_needed:
                #print(f"\n{self.player.name} ({self.personality_type}) is mortgaging properties to pay off debts.") if self.display else None
                for p in properties_to_mortgage:
                    p.mortgage(self.player)
                return True
        
        # If we get here, we couldn't raise enough money
        return False

    def decide_unmortgage_property(self):
        """Decide which properties to unmortgage based on wealth and completing sets."""
        # Only unmortgage if we have plenty of money, modified by cash reserve preference
        min_reserve = 500 * (0.5 + self.cash_reserve_preference)
        if self.player.money < min_reserve:
            return None
        
        # Find all mortgaged properties
        mortgaged_props = [p for p in self.player.properties if p.status == PropertyStatus.MORTGAGED]
        
        if not mortgaged_props:
            return None
        
        # Count properties by color
        props_by_color = {}
        for prop in self.player.properties:
            if prop.color not in props_by_color:
                props_by_color[prop.color] = []
            props_by_color[prop.color].append(prop)
        
        # Find total properties in each color group
        color_counts = {}
        for space in self.game.board.spaces:
            if hasattr(space, 'color'):
                if space.color not in color_counts:
                    color_counts[space.color] = 0
                color_counts[space.color] += 1
        
        # Score each mortgaged property for unmortgaging priority
        def unmortgage_priority_score(prop):
            score = 0
            
            # Higher score for properties that would complete a monopoly
            if prop.color in props_by_color:
                mortgaged_in_color = sum(1 for p in props_by_color[prop.color] if p.status == PropertyStatus.MORTGAGED)
                owned_in_color = len(props_by_color[prop.color])
                total_in_color = color_counts.get(prop.color, 0)
                
                # If this would complete a monopoly
                if owned_in_color == total_in_color and mortgaged_in_color == 1:
                    score += 5.0 * self.monopoly_focus
                
                # Bonus for color groups we have a lot of
            if total_in_color > 0:
                monopoly_progress = owned_in_color / total_in_color
                score += monopoly_progress * self.monopoly_focus * 2.0
            
            # Railroads and utilities get bonus based on interest
            if prop.color in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
                count = sum(1 for p in self.player.properties 
                         if p.color == prop.color and p.status != PropertyStatus.MORTGAGED)
                score += count * self.railroad_utility_interest
            
            # Properties in developed areas get a bonus based on risk tolerance
            score += (prop.position / 40.0) * self.risk_tolerance
            
            return score
        
        # Sort mortgaged properties by priority score
        mortgaged_props.sort(key=unmortgage_priority_score, reverse=True)
        
        # Try to unmortgage the highest priority property if we can afford it
        for prop in mortgaged_props:
            unmortgage_cost = prop.unmortgage()
            affordable_reserve = self.player.money - unmortgage_cost - (300 * self.cash_reserve_preference)
            
            if affordable_reserve > 0:
                print(f"{self.player.name} ({self.personality_type}) unmortgages {prop.name} for ${unmortgage_cost}") if self.display else None
                self.player.pay(unmortgage_cost)
                return prop
        
        return None

    def make_move(self):
        """Make all decisions for a turn."""
        # If in jail, decide strategy
        if self.player.jail_turns > 0:
            return self.decide_jail_strategy()
        
        # Development is prioritized based on development focus
        if random.random() < self.development_focus:
            property = self.decide_house_purchases()
            if property:
                self.game.build_house_bot(self.player)
        
        # Trading frequency based on trade willingness
        if random.random() < self.trade_willingness:
            self.initiate_trade()
        
        # Unmortgage based on cash reserves and property focus
        if random.random() < self.property_focus:
            self.decide_unmortgage_property()
        
        # If low on money, consider mortgaging properties based on cash reserve preference
        min_cash = 50 + (self.cash_reserve_preference * 200)
        if self.player.money < min_cash:
            self.decide_mortgage_property(min_cash - self.player.money)
            
class NeuralNetwork(nn.Module):
    def __init__(self, input_dim=100, hidden_dim=64, output_dim=10):
        super(NeuralNetwork, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
    def forward(self, x):
        return self.model(x)

class NeuralBot(Bot):
    def __init__(self, player):
        super().__init__(player)
        self.model = NeuralNetwork()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
        self.memory = []  # For experience replay
        self.epsilon = 0.3  # For exploration vs exploitation
        
    def _get_state(self, board, players):
        """Create a state representation for the neural network"""
        state = []
        
        # Player information
        state.append(self.player.money / 2000.0)  # Normalized money
        state.append(self.player.position / 40.0)  # Normalized position
        state.append(1.0 if self.player.jail_turns > 0 else 0.0)  # In jail?
        
        # Property ownership (one-hot encoding for each property)
        for i in range(40):
            space = board.spaces[i]
            if isinstance(space, Property):
                # 1 if player owns it, 0 otherwise
                state.append(1.0 if space in self.player.properties else 0.0)
                # 1 if property is mortgaged, 0 otherwise
                state.append(1.0 if space in self.player.properties and space.status == PropertyStatus.MORTGAGED else 0.0)
                # Number of houses normalized
                if space in self.player.properties and hasattr(space, 'houses'):
                    state.append(space.houses / 5.0)
                else:
                    state.append(0.0)
            else:
                # Not a property, add zeros as placeholders
                state.append(0.0)
                state.append(0.0)
                state.append(0.0)
        
        # Add some opponent information
        other_players = [p for p in players if p != self.player and not p.bankrupt]
        avg_money = sum(p.money for p in other_players) / max(1, len(other_players))
        state.append(avg_money / 2000.0)  # Normalized average opponent money
        
        # Pad or truncate to match input_dim
        while len(state) < 100:
            state.append(0.0)
        
        return torch.tensor(state, dtype=torch.float32)
    
    def decide_buy_property(self, property):
        """Use neural network to decide whether to buy property"""
        if random.random() < self.epsilon:  # Exploration
            return super().decide_buy_property(property)
        
        # Get state and predict
        state = self._get_state(None, [])  # Need to implement proper state capture
        prediction = self.model(state)
        buy_score = prediction[0].item()  # First output neuron for buying property
        
        return buy_score > 0.5
    
    def decide_auction_bid(self, property, current_bid):
        """Use neural network to decide auction bid"""
        if random.random() < self.epsilon:  # Exploration
            return super().decide_auction_bid(property, current_bid)
        
        # Get state and predict
        state = self._get_state(None, [])
        prediction = self.model(state)
        bid_percentage = prediction[1].item()  # Second output for bid percentage
        
        # Bid between current_bid and property.price * bid_percentage
        max_bid = min(self.player.money * 0.8, property.price * 1.5)
        new_bid = current_bid + int((max_bid - current_bid) * bid_percentage)
        
        return max(current_bid + 1, new_bid) if new_bid > current_bid else 0
    
    def learn_from_experience(self, old_state, action, reward, new_state):
        """Store experience and learn from it"""
        self.memory.append((old_state, action, reward, new_state))
        
        # Only train after accumulating some experiences
        if len(self.memory) > 100:
            # Sample batch from memory
            batch = random.sample(self.memory, min(32, len(self.memory)))
            
            for old_s, act, rew, new_s in batch:
                # Simple Q-learning update
                target = rew
                if new_s is not None:  # Not a terminal state
                    target += 0.95 * torch.max(self.model(new_s)).item()
                
                # Get current prediction and update the action's value
                current = self.model(old_s)
                target_f = current.clone()
                target_f[0, act] = target
                
                # Train the model
                self.optimizer.zero_grad()
                loss = self.criterion(current, target_f)
                loss.backward()
                self.optimizer.step()
    
    def save_model(self, path="neural_bot_model.pth"):
        """Save the neural network model"""
        torch.save(self.model.state_dict(), path)
    
    def load_model(self, path="neural_bot_model.pth"):
        """Load a previously trained model"""
        self.model.load_state_dict(torch.load(path))
        self.model.eval()
