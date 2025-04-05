import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import matplotlib.pyplot as plt
import time
from stats import calculate_win_probabilities
import monopoly_for_bots
from Bot import Bot
import json
import os
from game_models import Property, PropertyColor, PropertyStatus
import types
from colorama import Fore, Style
from variables import colors

# Simplified hyperparameters
LEARNING_RATE = 0.01
BATCH_SIZE = 32
MEMORY_SIZE = 500
NUMBER_OF_GAMES = 30
NUMBER_OF_EPOCHS = 5
HIDDEN_SIZE = 64

class MonopolyNeuralModel(nn.Module):
    """A neural network for Monopoly strategy"""
    def __init__(self, input_size=124, hidden_size=64, output_size=10):
        super(MonopolyNeuralModel, self).__init__()
        
        # Simpler architecture: just two layers
        self.input_layer = nn.Linear(input_size, hidden_size)
        self.hidden_layer = nn.Linear(hidden_size, hidden_size)
        self.output_layer = nn.Linear(hidden_size, output_size)
        
        # Simple dropout for regularization
        self.dropout = nn.Dropout(0.2)
        
    def forward(self, x):
        # Add batch dimension if needed
        if x.dim() == 1:
            x = x.unsqueeze(0)
        
        # Simple forward pass
        x = torch.relu(self.input_layer(x))
        x = self.dropout(x) if self.training else x
        x = torch.relu(self.hidden_layer(x))
        x = torch.sigmoid(self.output_layer(x))
        
        # Remove batch dimension if it was added
        if x.size(0) == 1:
            x = x.squeeze(0)
            
        return x

class ReplayBuffer:
    """An experience replay buffer"""
    def __init__(self, capacity):
        self.capacity = capacity
        self.buffer = []
        self.position = 0
        
    def __len__(self):
        return len(self.buffer)
        
    def add(self, experience):
        if len(self.buffer) < self.capacity:
            self.buffer.append(experience)
        else:
            self.buffer[self.position] = experience
        self.position = (self.position + 1) % self.capacity
        
    def sample(self, batch_size):
        if len(self.buffer) < batch_size:
            return self.buffer
        return random.sample(self.buffer, batch_size)

class NeuralAlgorithm:
    """A neural algorithm for Monopoly"""
    def __init__(self, learning_rate=0.01, memory_size=500, batch_size=32, hidden_size=64):
        self.input_size = 124
        self.hidden_size = hidden_size
        self.output_size = 10
        self.learning_rate = learning_rate
        
        # Create model and optimizer
        self.model = MonopolyNeuralModel(self.input_size, self.hidden_size, self.output_size)
        self.model.eval()  # Start in evaluation mode
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()
        
        # Simple replay buffer
        self.memory = ReplayBuffer(memory_size)
        self.batch_size = batch_size
        
        # Tracking metrics
        self.win_rates = []
        self.rewards_history = []
        
        # Parameter names for reference
        self.parameter_names = [
            "risk_tolerance",
            "property_focus",
            "development_focus",
            "cash_reserve_preference",
            "trade_willingness",
            "monopoly_focus",
            "railroad_utility_interest",
            "property_management_focus",
            "trade_acceptance_threshold",
            "property_value_assessment",
        ]
    
    def create_game_state_vector(self, game, player=None):
        """Create a simplified state representation of the current game"""
        if player is None and len(game.players) > 0:
            player = game.players[0]
            
        state = torch.zeros(self.input_size, dtype=torch.float32)
        
        if not player:
            return state
            
        # Basic player info (money, position, jail)
        state[0] = player.money / 2000.0
        state[1] = player.position / 40.0
        state[2] = 1.0 if player.jail_turns > 0 else 0.0
        state[3] = len(player.properties) / 28.0
        
        # Property ownership and development
        property_index = 14
        for space_idx, space in enumerate(game.board.spaces):
            if hasattr(space, "owner"):
                # First value: ownership
                state[property_index] = 1.0 if space.owner == player else 0.0
                
                # Second value: mortgaged
                is_mortgaged = (hasattr(space, "status") and 
                               space.status == PropertyStatus.MORTGAGED)
                state[property_index + 1] = 1.0 if space.owner == player and is_mortgaged else 0.0
                
                # Third value: development
                houses = getattr(space, "houses", 0) if space.owner == player else 0
                state[property_index + 2] = houses / 5.0
                
                property_index += 3
                if property_index >= self.input_size:
                    break
        
        return state

    def get_bot_parameters(self, state):
        """Generate bot parameters using the model"""
        self.model.eval()
        with torch.no_grad():
            output = self.model(state)
            
            if isinstance(output, torch.Tensor):
                parameters = output.tolist() if output.dim() == 1 else output.squeeze(0).tolist()
            else:
                parameters = output
                
            return {name: value for name, value in zip(self.parameter_names, parameters)}
    
    def calculate_reward(self, game, player, win_prob_before, win_prob_after):
        """Calculate a simplified reward"""
        # Base reward on win probability change
        reward = (win_prob_after - win_prob_before) * 2.0
        
        # Additional reward components
        money_factor = player.money / 2000.0
        property_factor = len(player.properties) / 28.0
        
        # Calculate monopoly count
        monopoly_count = 0
        color_counts = {}
        for prop in player.properties:
            if hasattr(prop, "color"):
                if prop.color not in color_counts:
                    color_counts[prop.color] = 0
                color_counts[prop.color] += 1
                
        for color, count in color_counts.items():
            if color == PropertyColor.BROWN or color == PropertyColor.DARK_BLUE:
                if count == 2:
                    monopoly_count += 1
            elif color == PropertyColor.RAILROAD:
                if count == 4:
                    monopoly_count += 1
            elif count == 3:
                monopoly_count += 1
                
        monopoly_factor = min(monopoly_count / 8.0, 1.0) * 0.5
        
        # Combine all factors
        reward += money_factor + property_factor + monopoly_factor
        
        return reward
    
    def train_from_memory(self):
        """Train model from replay buffer - simplified version"""
        if len(self.memory) < self.batch_size:
            return 0
            
        # Sample batch
        batch = self.memory.sample(self.batch_size)
        
        # Prepare batch data
        states = torch.stack([exp[0] for exp in batch])
        parameters = torch.tensor([exp[1] for exp in batch], dtype=torch.float32)
        rewards = torch.tensor([exp[2] for exp in batch], dtype=torch.float32).view(-1, 1)
        
        # Set to training mode
        self.model.train()
        
        # Forward pass
        predictions = self.model(states)
        
        # Create simple reward-weighted targets
        targets = parameters.clone()
        for i in range(len(batch)):
            # If positive reward, reinforce those actions
            if rewards[i] > 0:
                targets[i] = parameters[i]
            else:
                # For negative rewards, move toward neutral
                targets[i] = 0.5 * torch.ones_like(parameters[i])
        
        # Calculate loss and update
        self.optimizer.zero_grad()
        loss = self.criterion(predictions, targets)
        loss.backward()
        self.optimizer.step()
        
        # Back to eval mode
        self.model.eval()
        
        return loss.item()
    
    def plot_training_progress(self, losses=None):
        """Plot detailed training progress metrics"""
        plt.figure(figsize=(15, 12))
        plt.suptitle("Monopoly Neural Training Results", fontsize=16)
        
        # Create a grid of subplots
        plt.subplot(2, 2, 1)
        plt.plot(self.win_rates, 'b-o', linewidth=2)
        plt.title('Win Rate Progress')
        plt.xlabel('Epoch')
        plt.ylabel('Win Rate')
        plt.grid(True, alpha=0.3)
        
        # Plot rewards over time
        plt.subplot(2, 2, 2)
        plt.plot(self.rewards_history, 'g-o', linewidth=2)
        plt.title('Average Reward Progress')
        plt.xlabel('Epoch')
        plt.ylabel('Reward')
        plt.grid(True, alpha=0.3)
        
        # If we have loss data, plot that too
        if losses:
            plt.subplot(2, 2, 3)
            plt.plot(losses, 'r-', linewidth=1.5, alpha=0.7)
            plt.title('Training Loss')
            plt.xlabel('Update Step')
            plt.ylabel('Loss')
            plt.grid(True, alpha=0.3)
        
        # Plot final parameters as a bar chart
        plt.subplot(2, 2, 4)
        current_params = self.get_bot_parameters(torch.zeros(self.input_size, dtype=torch.float32))
        param_names = list(current_params.keys())
        param_values = list(current_params.values())
        
        # Create a colorful bar chart
        bars = plt.bar(range(len(param_names)), param_values, 
                       color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
                              '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', 
                              '#bcbd22', '#17becf'])
        
        plt.title('Bot Parameters')
        plt.xlabel('Parameter')
        plt.xticks(range(len(param_names)), param_names, rotation=45, ha='right')
        plt.ylim(0, 1.0)
        plt.grid(True, axis='y', alpha=0.3)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width()/2., height + 0.02,
                    f'{height:.2f}', ha='center', va='bottom', fontsize=8)
        
        plt.tight_layout(rect=[0, 0, 1, 0.95])  # Adjust for the suptitle
        
        # Save the figure
        plt.savefig("training_progress.png", dpi=150)
        print(f"Training progress plot saved to training_progress.png")
        plt.show()
    
    def run_training_games(self, num_games=20, num_epochs=3):
        """Run training games with simplified approach"""
        losses = []  # Track losses for plotting
        
        for epoch in range(num_epochs):
            print(f"Epoch {epoch+1}/{num_epochs}")
            
            wins = 0
            total_reward = 0
            
            epoch_losses = []  # Track losses for this epoch
            
            for game_num in range(num_games):
                if game_num % 5 == 0:
                    print(f"  Game {game_num+1}/{num_games}...")
                
                # Create initial state and get parameters
                initial_state = torch.zeros(self.input_size, dtype=torch.float32)
                parameters = self.get_bot_parameters(initial_state)
                param_list = [parameters[name] for name in self.parameter_names]
                
                # Play game
                game = monopoly_for_bots.MonopolyGame(
                    bot_count=4,
                    neural_bot_count=1,
                )
                
                # Initialize neural bot
                neural_bot = ActionNeuralBot(
                    player=game.players[0], 
                    game=game, 
                    display=False
                )
                neural_bot.initialize_with_model(self.model)
                game.players[0].bot = neural_bot
                
                # Play the game
                game_result = game.play_game()
                
                # Get results
                neural_player = game.players[0]
                if game.winner == neural_player:
                    wins += 1
                
                # Calculate reward (simplified)
                reward = 1.0 if game.winner == neural_player else -0.2
                reward += neural_player.money / 5000.0  # Small reward for money
                reward += len(neural_player.properties) / 28.0  # Small reward for properties
                
                total_reward += reward
                
                # Create final state
                final_state = self.create_game_state_vector(game, neural_player)
                
                # Store experience
                self.memory.add((initial_state, param_list, reward, final_state))
                
                # Train periodically
                if len(self.memory) >= self.batch_size and game_num % 5 == 0:
                    loss = self.train_from_memory()
                    epoch_losses.append(loss)
            
            # Add epoch losses to overall losses
            losses.extend(epoch_losses)
            
            # Calculate metrics
            win_rate = wins / num_games
            avg_reward = total_reward / num_games
            
            self.win_rates.append(win_rate)
            self.rewards_history.append(avg_reward)
            
            print(f"  Win rate: {win_rate:.2f}, Avg reward: {avg_reward:.2f}")
            
            # Show current parameters
            current_params = self.get_bot_parameters(torch.zeros(self.input_size, dtype=torch.float32))
            print("  Current parameters:")
            for name, value in current_params.items():
                print(f"    {name}: {value:.4f}")
        
        # Plot training progress at the end
        self.plot_training_progress(losses=losses)
        
        return {
            "win_rates": self.win_rates,
            "rewards": self.rewards_history,
            "final_parameters": current_params,
            "losses": losses
        }
    
    def run_self_play_tournament(self, generations=3, matches_per_generation=10):
        """Run a simplified self-play tournament"""
        # Start with a few models
        model_pool = []
        for _ in range(3):
            new_model = MonopolyNeuralModel(self.input_size, self.hidden_size, self.output_size)
            model_pool.append(new_model)
        
        # Add our current model to the pool
        model_pool.append(self.model)
        
        for gen in range(generations):
            print(f"Generation {gen+1}/{generations}")
            
            # Tournament results
            results = {}
            for i, model in enumerate(model_pool):
                results[i] = 0
            
            # Play round-robin matches
            for i in range(len(model_pool)):
                for j in range(i+1, len(model_pool)):
                    # Play matches between models i and j
                    for _ in range(matches_per_generation // 10):
                        # Create game
                        game = monopoly_for_bots.MonopolyGame(
                            bot_count=4,
                            neural_bot_count=2
                        )
                        
                        # Setup bots
                        bot_a = ActionNeuralBot(player=game.players[0], game=game, display=False)
                        bot_a.initialize_with_model(model_pool[i])
                        game.players[0].bot = bot_a
                        
                        bot_b = ActionNeuralBot(player=game.players[1], game=game, display=False)
                        bot_b.initialize_with_model(model_pool[j])
                        game.players[1].bot = bot_b
                        
                        # Play game
                        game_result = game.play_game()
                        
                        # Update results
                        if game.winner == game.players[0]:
                            results[i] += 1
                        elif game.winner == game.players[1]:
                            results[j] += 1
            
            # Rank models
            ranked_models = sorted(results.items(), key=lambda x: x[1], reverse=True)
            print(f"  Model rankings: {ranked_models}")
            
            # Select best model
            best_idx = ranked_models[0][0]
            best_model = model_pool[best_idx]
            
            # Create new variants from best model
            new_pool = [best_model]
            
            # Add some variations
            for _ in range(3):
                new_model = MonopolyNeuralModel(self.input_size, self.hidden_size, self.output_size)
                # Copy parameters from best model
                new_model.load_state_dict(best_model.state_dict())
                
                # Add some random variations
                with torch.no_grad():
                    for param in new_model.parameters():
                        noise = torch.randn_like(param) * 0.1
                        param.add_(noise)
                
                new_pool.append(new_model)
            
            # Update model pool
            model_pool = new_pool
            
            # Update main model with best performer
            self.model = best_model
            
        print(f"Self-play tournament complete. Best model selected.")
        
        # Save the final model
        name = input("Enter a name for the final model: ")
        self.save_model(f"models/{name}.pth")
        
        # At the end, after saving the model:
        self.plot_training_progress()
    
    def save_model(self, filepath):
        """Save the model to a file"""
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        torch.save(self.model.state_dict(), filepath)
        print(f"Model saved to {filepath}")
    
    def load_model(self, filepath):
        """Load a model from a file"""
        if os.path.exists(filepath):
            self.model.load_state_dict(torch.load(filepath))
            self.model.eval()
            print(f"Model loaded from {filepath}")
            return True
        else:
            print(f"No model found at {filepath}")
            return False

class ActionNeuralBot(Bot):
    """A neural bot for Monopoly"""
    def __init__(self, player, game, parameters=None, display=True, property=None):
        # Default parameters
        if parameters is None:
            parameters = {
                "risk_tolerance": 0.5,
                "property_focus": 0.5,
                "development_focus": 0.5,
                "cash_reserve_preference": 0.5,
                "trade_willingness": 0.5,
                "monopoly_focus": 0.5,
                "railroad_utility_interest": 0.5,
            }
            
        super().__init__(player, game, parameters, display, property)
        
        # Simple model architecture
        self.input_dim = 124
        self.hidden_dim = 64
        self.output_dim = 10
        
        # Create the model
        self.model = nn.Sequential(
            nn.Linear(self.input_dim, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.output_dim),
            nn.Sigmoid()
        )
        
        # Exploration parameter
        self.epsilon = 0.2
    
    def initialize_with_model(self, model):
        """Initialize bot with a given model"""
        self.model = model
    
    def _get_state(self):
        """Get current game state as tensor"""
        state = []
        
        # Player info
        state.append(self.player.money / 2000.0)
        state.append(self.player.position / 40.0)
        state.append(1.0 if self.player.jail_turns > 0 else 0.0)
        state.append(len(self.player.properties) / 28.0)
        
        # Pad to full size
        while len(state) < self.input_dim:
            state.append(0.0)
        
        return torch.tensor(state[:self.input_dim], dtype=torch.float32)
    
    def _get_action_probabilities(self):
        """Get action probabilities from the model"""
        state = self._get_state()
        with torch.no_grad():
            return self.model(state)
    
    def decide_buy_property(self, property):
        """Decide whether to buy property"""
        # Occasionally use random strategy
        if random.random() < self.epsilon:
            return super().decide_buy_property(property)
        
        # Get action probabilities
        probs = self._get_action_probabilities()
        
        # Use first output for buy decision
        return probs[0].item() > 0.5
    
    def decide_auction_bid(self, property, current_bid):
        """Decide auction bid"""
        if random.random() < self.epsilon:
            return super().decide_auction_bid(property, current_bid)
        
        probs = self._get_action_probabilities()
        
        # Scale bid based on second output
        bid_factor = probs[1].item()
        max_bid = min(self.player.money * 0.8, property.price * 1.5)
        bid = current_bid + int((max_bid - current_bid) * bid_factor)
        
        if bid <= current_bid:
            return 0
        return bid
    
    def decide_house_purchases(self):
        """Decide whether to buy houses"""
        if random.random() < self.epsilon:
            return super().decide_house_purchases()
        
        probs = self._get_action_probabilities()
        
        if probs[2].item() > 0.5:
            return super().decide_house_purchases()
        return None
    
    def make_move(self):
        """Make all decisions for a turn"""
        # Get action probabilities
        probs = self._get_action_probabilities()
        
        # House purchases
        if probs[2].item() > 0.5:
            property = self.decide_house_purchases()
            if property:
                try:
                    self.game.build_house_bot(self.player)
                except:
                    pass
        
        # Mortgage if low on cash
        min_cash = 50 + (self.cash_reserve_preference * 200)
        if self.player.money < min_cash or probs[6].item() > 0.7:
            self.decide_mortgage_property(max(0, min_cash - self.player.money))
            
        # Attempt to make trade offers
        if random.random() < probs[4].item():  # Use trade_willingness parameter
            self.attempt_trading()
    
    def attempt_trading(self):
        """Attempt to make trades with other players"""
        # Only try trading if we have properties
        if not self.player.properties:
            return
            
        # Get action probabilities
        probs = self._get_action_probabilities()
        
        # Select a random opponent to trade with
        potential_traders = [p for p in self.game.players if p != self.player and not p.bankrupt]
        if not potential_traders:
            return
            
        trade_partner = random.choice(potential_traders)
        
        # Create a trade offer
        trade_offer = self.decide_trade_offer(trade_partner, probs)
        if trade_offer:
            # Present the trade to the partner
            accepted = self.present_trade(trade_partner, trade_offer)
            if self.display and accepted:
                print(f"{Fore.GREEN}Trade accepted between {self.player.name} and {trade_partner.name}!{Style.RESET_ALL}")
    
    def decide_trade_offer(self, trade_partner, probs=None):
        """Generate a trade offer based on neural model outputs"""
        if probs is None:
            probs = self._get_action_probabilities()
            
        # If partner has no properties, can't make a meaningful trade
        if not trade_partner.properties:
            return None
            
        # Initialize trade properties and money
        properties_to_give = []
        properties_to_receive = []
        money_to_give = 0
        money_to_receive = 0
        
        # Determine which properties to give based on neural output
        trade_willingness = probs[4].item()  # Trade willingness parameter
        monopoly_focus = probs[5].item()     # Monopoly focus parameter
        
        # Select properties to offer
        our_nonmonopoly_props = [p for p in self.player.properties 
                                if hasattr(p, "color") and not self.is_monopoly(p.color)]
        
        # Only offer properties if we're willing to trade
        if our_nonmonopoly_props and trade_willingness > 0.4:
            # Number of properties to offer
            num_to_give = max(1, int(len(our_nonmonopoly_props) * trade_willingness * 0.5))
            properties_to_give = random.sample(our_nonmonopoly_props, min(num_to_give, len(our_nonmonopoly_props)))
        
        # Determine which properties to request
        # Focus on properties that would complete monopolies
        desired_colors = self.get_near_monopoly_colors()
        partner_props_of_interest = [p for p in trade_partner.properties 
                                     if hasattr(p, "color") and 
                                     (p.color in desired_colors or random.random() < 0.3)]
        
        if partner_props_of_interest:
            # Number of properties to request based on monopoly focus
            num_to_request = max(1, int(len(partner_props_of_interest) * monopoly_focus * 0.5))
            properties_to_receive = random.sample(partner_props_of_interest, 
                                                 min(num_to_request, len(partner_props_of_interest)))
        
        # If no properties selected, no trade
        if not properties_to_give and not properties_to_receive:
            return None
            
        # Add money to balance the trade based on property_value_assessment
        property_value_multiplier = 0.8 + (probs[9].item() * 0.4)  # 0.8 to 1.2 range
        
        our_offer_value = sum(p.price for p in properties_to_give)
        their_offer_value = sum(p.price for p in properties_to_receive)
        
        value_difference = their_offer_value - our_offer_value
        
        # If we're getting more value, offer money
        if value_difference > 0:
            money_to_give = int(value_difference * property_value_multiplier)
            # Ensure we have enough money and keep a reserve
            max_money_to_offer = max(0, self.player.money - 100)
            money_to_give = min(money_to_give, max_money_to_offer)
        else:
            # If we're giving more value, request money
            money_to_receive = int(abs(value_difference) * property_value_multiplier)
            # Make sure it's reasonable for them to pay
            max_money_to_request = max(0, trade_partner.money - 100)
            money_to_receive = min(money_to_receive, max_money_to_request)
        
        # Create the trade offer
        trade_offer = {
            "give_properties": properties_to_give,
            "receive_properties": properties_to_receive,
            "give_money": money_to_give,
            "receive_money": money_to_receive
        }
        
        # Only proceed if there's a meaningful exchange
        if (properties_to_give or money_to_give > 0) and (properties_to_receive or money_to_receive > 0):
            return trade_offer
        return None
    
    def is_monopoly(self, color):
        """Check if player has monopoly in a color group"""
        # Count how many properties in this color group
        color_count = sum(1 for p in self.player.properties if hasattr(p, "color") and p.color == color)
        
        # Determine the total count in the color group
        if color == PropertyColor.BROWN or color == PropertyColor.DARK_BLUE:
            return color_count == 2
        elif color == PropertyColor.RAILROAD or color == PropertyColor.UTILITY:
            return color_count == 4 if color == PropertyColor.RAILROAD else color_count == 2
        else:
            return color_count == 3
    
    def get_near_monopoly_colors(self):
        """Find color groups where player is one property away from monopoly"""
        color_counts = {}
        for prop in self.player.properties:
            if hasattr(prop, "color"):
                if prop.color not in color_counts:
                    color_counts[prop.color] = 0
                color_counts[prop.color] += 1
        
        near_monopolies = []
        for color, count in color_counts.items():
            if color == PropertyColor.BROWN or color == PropertyColor.DARK_BLUE:
                if count == 1:
                    near_monopolies.append(color)
            elif color == PropertyColor.RAILROAD:
                if count >= 2:
                    near_monopolies.append(color)
            elif color == PropertyColor.UTILITY:
                if count == 1:
                    near_monopolies.append(color)
            elif count == 2:
                near_monopolies.append(color)
                
        return near_monopolies
    
    def present_trade(self, trade_partner, trade_offer):
        """Present a trade offer to another player"""
        # If the trade partner is a bot, use their bot to evaluate
        if hasattr(trade_partner, 'bot'):
            # For standard bots, we need to adapt our trade format to match Bot.decide_trade() expectations
            # Bot.decide_trade() expects single properties and a cash amount, while our neural bot uses lists
            
            # Convert to the format expected by Bot.decide_trade()
            # We'll simplify by offering the first property in each list and adjusting the cash amount
            receive_props = trade_offer["receive_properties"]
            give_props = trade_offer["give_properties"]
            
            if self.display:
                properties_to_give = ", ".join([p.name for p in give_props])
                properties_to_receive = ", ".join([p.name for p in receive_props])
                print(f"\n{Fore.CYAN}Trade proposed: {self.player.name} offers {properties_to_give}")
                if trade_offer["give_money"] > 0:
                    print(f"and ${trade_offer['give_money']}")
                print(f"in exchange for {properties_to_receive}")
                if trade_offer["receive_money"] > 0:
                    print(f"and ${trade_offer['receive_money']}{Style.RESET_ALL}")
            
            # If we have no properties to give or receive, can't make a trade
            if not give_props or not receive_props:
                return False
                
            # Calculate net cash transfer (positive means we're giving cash)
            net_cash = trade_offer["give_money"] - trade_offer["receive_money"]
            
            # Call the standard bot's decide_trade method with the first property from each list
            # and the net cash amount
            accepted = trade_partner.bot.decide_trade(receive_props[0], give_props[0], net_cash)
            
            if accepted:
                self.execute_trade(trade_partner, trade_offer)
            return accepted
        
        # If not a bot, default to False (human would need UI)
        return False
    
    def evaluate_trade_offer(self, trade_partner, trade_offer):
        """Evaluate an incoming trade offer"""
        # Get action probabilities for decision making
        probs = self._get_action_probabilities()
        
        # Extract trade acceptance threshold
        acceptance_threshold = probs[8].item()  # Range 0-1
        
        # Calculate value of properties offered to us
        receive_value = sum(p.price for p in trade_offer["receive_properties"])
        receive_value += trade_offer["receive_money"]
        
        # Calculate value of what we're giving
        give_value = sum(p.price for p in trade_offer["give_properties"])
        give_value += trade_offer["give_money"]
        
        # Base value ratio
        value_ratio = receive_value / max(1, give_value)
        
        # Check if any properties being received would complete a monopoly
        near_monopoly_colors = self.get_near_monopoly_colors()
        monopoly_bonus = 0
        for prop in trade_offer["receive_properties"]:
            if hasattr(prop, "color") and prop.color in near_monopoly_colors:
                monopoly_bonus += 0.3  # Significant bonus for monopoly completion
        
        # Check if we're giving away properties that would help opponent form monopolies
        opponent_bonus = 0
        opponent_property_colors = [p.color for p in trade_partner.properties if hasattr(p, "color")]
        for prop in trade_offer["give_properties"]:
            if hasattr(prop, "color") and prop.color in opponent_property_colors:
                opponent_bonus -= 0.2  # Penalty for helping opponent
        
        # Final score - more likely to accept if good value or completes monopolies
        final_score = value_ratio + monopoly_bonus + opponent_bonus
        
        # Adjust by neural model parameters
        trade_willingness = probs[4].item()
        final_score += (trade_willingness - 0.5) * 0.4  # More willing traders accept more
        
        # Compare against acceptance threshold
        adjusted_threshold = max(0.8, acceptance_threshold)  # Minimum 0.8 to prevent terrible trades
        
        if self.display and final_score >= adjusted_threshold:
            print(f"{Fore.GREEN}{self.player.name} accepts the trade (score: {final_score:.2f}){Style.RESET_ALL}")
        elif self.display:
            print(f"{Fore.RED}{self.player.name} rejects the trade (score: {final_score:.2f}){Style.RESET_ALL}")
            
        return final_score >= adjusted_threshold
    
    def execute_trade(self, trade_partner, trade_offer):
        """Execute an accepted trade between players"""
        # Transfer properties from player to partner
        for prop in trade_offer["give_properties"]:
            self.player.properties.remove(prop)
            trade_partner.properties.append(prop)
            prop.owner = trade_partner
            
        # Transfer properties from partner to player
        for prop in trade_offer["receive_properties"]:
            trade_partner.properties.remove(prop)
            self.player.properties.append(prop)
            prop.owner = self.player
            
        # Transfer money
        self.player.money -= trade_offer["give_money"]
        trade_partner.money += trade_offer["give_money"]
        
        self.player.money += trade_offer["receive_money"]
        trade_partner.money -= trade_offer["receive_money"]
        
        if self.display:
            print(f"{Fore.YELLOW}Trade completed between {self.player.name} and {trade_partner.name}{Style.RESET_ALL}")

def main():
    """Main function to run the neural algorithm"""
    print(f"{colors['title']}Starting Neural Algorithm for Monopoly{colors['reset']}")
    
    # Initialize algorithm
    algorithm = NeuralAlgorithm(
        learning_rate=LEARNING_RATE,
        memory_size=MEMORY_SIZE,
        batch_size=BATCH_SIZE,
        hidden_size=HIDDEN_SIZE
    )
    
    # Try to load existing model
    model_loaded = algorithm.load_model("models/simple_model.pth")
    if not model_loaded:
        print(f"{colors['warning']}Starting with a new model{colors['reset']}")
    
    # Ask whether to run self-play or direct training
    choice = input(f"{colors['prompt']}1. Run self-play tournament\n2. Train against standard bots\nChoose an option: {colors['reset']}")
    
    if choice == "1":
        print(f"{colors['title']}Running self-play tournament...{colors['reset']}")
        algorithm.run_self_play_tournament(generations=3, matches_per_generation=10)
    else:
        print(f"{colors['title']}Running training against standard bots...{colors['reset']}")
        results = algorithm.run_training_games(num_games=NUMBER_OF_GAMES, num_epochs=NUMBER_OF_EPOCHS)
        
        # Save trained model
        algorithm.save_model("models/simple_trained_model.pth")
        
        # Display results
        print(f"\n{colors['success']}Training completed!{colors['reset']}")
        print(f"Final win rate: {results['win_rates'][-1]:.2f}")
    
    # Run test games
    test_wins = 0
    num_test_games = 5
    
    print(f"\n{colors['title']}Running test games...{colors['reset']}")
    
    test_results = {
        "games": [],
        "wins": [],
        "neural_money": [],
        "neural_properties": []
    }
    
    for i in range(num_test_games):
        print(f"Test game {i+1}/{num_test_games}...")
        
        # Create game with neural bot
        game = monopoly_for_bots.MonopolyGame(
            bot_count=4,
            neural_bot_count=1,
        )
        
        # Initialize neural bot with our model
        neural_bot = ActionNeuralBot(player=game.players[0], game=game, display=False)
        neural_bot.initialize_with_model(algorithm.model)
        game.players[0].bot = neural_bot
        
        # Play the game
        game_result = game.play_game()
        
        if game_result["winner"] == game.players[0]:
            print(f"{colors['success']}Neural bot wins!{colors['reset']}")
            test_wins += 1
        
        # Record detailed results from each game
        test_results["games"].append(i+1)
        test_results["wins"].append(1 if game_result["winner"] == game.players[0] else 0)
        test_results["neural_money"].append(game.players[0].money)
        test_results["neural_properties"].append(len(game.players[0].properties))
    
    # Plot test results
    plt.figure(figsize=(12, 5))
    plt.subplot(1, 2, 1)
    plt.bar(test_results["games"], test_results["wins"], color='green')
    plt.title("Test Game Results")
    plt.xlabel("Game Number")
    plt.ylabel("Win (1) or Loss (0)")
    plt.ylim(0, 1.2)
    
    plt.subplot(1, 2, 2)
    plt.bar(test_results["games"], test_results["neural_money"], color='blue', alpha=0.7, label="Money")
    ax2 = plt.twinx()
    ax2.plot(test_results["games"], test_results["neural_properties"], 'ro-', label="Properties")
    plt.title("Game Performance")
    plt.xlabel("Game Number")
    plt.ylabel("Money ($)")
    ax2.set_ylabel("Properties", color='red')
    
    plt.tight_layout()
    plt.savefig("test_results.png")
    
    print(f"\n{colors['title']}Test win rate: {colors['success']}{test_wins/num_test_games:.2f}{colors['reset']}")
    print(f"{colors['success']}Neural algorithm training complete!{colors['reset']}")

if __name__ == "__main__":
    main()
