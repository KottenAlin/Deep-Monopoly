import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np
import random
import matplotlib.pyplot as plt
import time
from stats import calculate_win_probabilities
from monopoly_for_bots import MonopolyGame, bots_parameters
from Bot import Bot
import json
import os
from game_models import Property, PropertyColor, PropertyStatus
import types  # Add this import


# hyperparameters
LEARNING_RATE = 0.01
BATCH_SIZE = 32
MEMORY_SIZE = 1000
NUMBER_OF_GAMES = 50
NUMBER_OF_EPOCHS = 10
HIDDEN_SIZE = 64


class MonopolyNeuralModel(nn.Module):
    def __init__(self, input_size=124, hidden_size=64, output_size=10):
        super(MonopolyNeuralModel, self).__init__()

        # Define network architecture
        self.network = nn.Sequential(
            nn.Linear(input_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, hidden_size),
            nn.ReLU(),
            nn.Linear(hidden_size, output_size),
            nn.Sigmoid(),  # Output values between 0-1 for parameters
        )

    def forward(self, x):
        return self.network(x)


class NeuralAlgorithm:
    def __init__(
        self, learning_rate=1, memory_size=1000, batch_size=32, hidden_size=64
    ):
        self.input_size = 124  # Update to match the actual size of your state vectors
        self.hidden_size = hidden_size
        self.output_size = 10  # Number of bot parameters
        self.learning_rate = learning_rate
        self.memory_size = memory_size
        self.batch_size = batch_size  ## Size of experience replay batch

        # Initialize model, optimizer and loss function
        self.model = MonopolyNeuralModel(
            self.input_size, self.hidden_size, self.output_size
        )
        self.optimizer = optim.Adam(self.model.parameters(), lr=self.learning_rate)
        self.criterion = nn.MSELoss()

        # Experience replay memory
        self.memory = []

        # Tracking metrics
        self.win_rates = []
        self.rewards_history = []
        self.avg_game_length = []

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
        """Create a state representation of the current game"""
        state = []

        if player is None and len(game.players) > 0:
            player = game.players[0]

        if player:
            # Player money and position
            state.append(player.money / 2000.0)  # Normalize money
            state.append(player.position / 40.0)  # Normalize position
            state.append(1.0 if player.jail_turns > 0 else 0.0)  # In jail?
            state.append(len(player.properties) / 28.0)  # Property ownership percentage

            # Property details
            mortgaged_count = sum(
                1
                for p in player.properties
                if hasattr(p, "status") and p.status == PropertyStatus.MORTGAGED
            )
            state.append(mortgaged_count / max(1, len(player.properties)))

            # Development level
            total_houses = sum(getattr(p, "houses", 0) for p in player.properties)
            total_hotels = sum(
                1 for p in player.properties if getattr(p, "hotel", False)
            )
            state.append(total_houses / 32.0)  # Max 32 houses
            state.append(total_hotels / 12.0)  # Max 12 hotels

            # Monopoly sets
            color_counts = {}
            for prop in player.properties:
                if hasattr(prop, "color"):
                    if prop.color.name not in color_counts:
                        color_counts[prop.color.name] = 0
                    color_counts[prop.color.name] += 1

            monopoly_count = 0
            for color, count in color_counts.items():
                if (color == "BROWN" or color == "DARK_BLUE") and count == 2:
                    monopoly_count += 1
                elif count == 3:
                    monopoly_count += 1
                elif color == "RAILROAD" and count == 4:
                    monopoly_count += 1
                elif color == "UTILITY" and count == 2:
                    monopoly_count += 1

            state.append(monopoly_count / 8.0)  # 8 possible monopolies
        else:
            # Fill with zeros if no player provided
            state.extend([0.0] * 8)

        # Game state
        if game:
            # Number of active players
            active_players = sum(1 for p in game.players if not p.bankrupt)
            state.append(active_players / 4.0)

            # Game turns
            state.append(min(game.turn_count, 100) / 100.0)  # Cap at 100 turns

            # Property availability
            available_properties = sum(
                1 for s in game.board.spaces if hasattr(s, "owner") and s.owner is None
            )
            state.append(available_properties / 28.0)
        else:
            state.extend([0.0] * 3)

        # Opponent information (aggregate)
        if game and len(game.players) > 1:
            opponents = [p for p in game.players if p != player and not p.bankrupt]
            if opponents:
                avg_money = sum(p.money for p in opponents) / len(opponents)
                state.append(avg_money / 2000.0)

                avg_props = sum(len(p.properties) for p in opponents) / len(opponents)
                state.append(avg_props / 28.0)

                avg_development = sum(
                    sum(getattr(p, "houses", 0) for p in opp.properties)
                    for opp in opponents
                ) / max(1, len(opponents))
                state.append(avg_development / 32.0)
            else:
                state.extend([0.0] * 3)
        else:
            state.extend([0.0] * 3)

        # Property ownership detail (one-hot encoding for each property)
        for i in range(40):
            space = game.board.spaces[i] if i < len(game.board.spaces) else None
            if space and hasattr(space, "owner"):
                # 1 if player owns it, 0 otherwise
                state.append(1.0 if space.owner == player else 0.0)
                # 1 if property is mortgaged, 0 otherwise
                is_mortgaged = (
                    hasattr(space, "status")
                    and space.status == PropertyStatus.MORTGAGED
                )
                state.append(1.0 if space.owner == player and is_mortgaged else 0.0)
                # Number of houses normalized
                if space.owner == player and hasattr(space, "houses"):
                    state.append(space.houses / 5.0)
                else:
                    state.append(0.0)
            else:
                # Not a property, add zeros as placeholders
                state.append(0.0)
                state.append(0.0)
                state.append(0.0)

        # Pad state vector to ensure consistent size
        while len(state) < self.input_size:
            state.append(0.0)

        # Ensure state vector is the right size
        state = state[: self.input_size]

        return torch.tensor(state, dtype=torch.float32)

    def get_bot_parameters(self, state):
        """Generate bot parameters using the neural network"""
        with torch.no_grad():
            # Ensure state is the right size
            if state.size(0) != self.input_size:
                # Pad or truncate to match expected size
                padded_state = torch.zeros(self.input_size, dtype=torch.float32)
                min_size = min(state.size(0), self.input_size)
                padded_state[:min_size] = state[:min_size]
                state = padded_state

            parameters = self.model(state).tolist()

            # Convert to dictionary with parameter names
            return {
                name: value for name, value in zip(self.parameter_names, parameters)
            }

    def calculate_reward(self, game, player, starting_win_prob, ending_win_prob):
        # Make immediate actions more rewarding
        reward = (
            ending_win_prob - starting_win_prob
        ) * 2.0  # Stronger immediate signal

        # get the monopoly count and development level
        monopoly_count = 0

        # Calculate monopoly count
        color_counts = {}
        for prop in player.properties:
            if hasattr(prop, "color"):
                if prop.color not in color_counts:
                    color_counts[prop.color] = 0
            color_counts[prop.color] += 1

        monopoly_count = 0
        for color, count in color_counts.items():
            if color == PropertyColor.BROWN or color == PropertyColor.DARK_BLUE:
                if count == 2:
                    monopoly_count += 1
            elif color == PropertyColor.RAILROAD:
                if count == 4:
                    monopoly_count += 1

        money_factor = player.money / 2000.0  # Normalize money
        property_factor = len(player.properties) / 28.0

        house_count = sum(
            space.houses for space in player.properties if hasattr(space, "houses")
        )
        hotel_count = sum(1 for space in player.properties if hasattr(space, "hotels"))

        # Increase the importance of strategic achievements
        monopoly_factor = min(monopoly_count / 8.0, 1.0) * 0.5  # More weight (was 0.2)
        development_factor = (
            min((house_count + hotel_count * 4) / 32.0, 1.0) * 0.3
        )  # More weight (was 0.1)

        # Combine factors with better weighting
        return (
            reward
            + money_factor
            + property_factor
            + (development_factor * 3)
            + (monopoly_factor * 2)
        )

    def store_experience(self, state, parameters, reward, next_state):
        """Store experience in replay memory"""
        # Convert parameters dict to list
        param_list = [parameters[name] for name in self.parameter_names]

        self.memory.append((state, param_list, reward, next_state))

        # Limit memory size
        if len(self.memory) > self.memory_size:
            self.memory.pop(0)

    def train_from_memory(self):
        """Train neural network from experience replay memory with improved learning"""
        if len(self.memory) < self.batch_size:
            return 0

        # Sample batch with priority for high-reward experiences
        experiences = [
            (exp, abs(exp[2])) for exp in self.memory
        ]  # (experience, abs_reward)
        experiences.sort(key=lambda x: x[1], reverse=True)

        # Take 80% from high-reward experiences, 20% random for exploration
        high_reward_count = int(self.batch_size * 0.8)
        high_reward_batch = [exp[0] for exp in experiences[: high_reward_count * 2]]
        random_batch = random.sample(self.memory, self.batch_size - high_reward_count)

        # Combine samples, with extra importance to recent high-reward experiences
        batch = random.sample(high_reward_batch, high_reward_count) + random_batch

        # Prepare batch data
        states = torch.stack(
            [self._ensure_state_size(experience[0]) for experience in batch]
        )
        parameters = torch.tensor(
            [experience[1] for experience in batch], dtype=torch.float32
        )
        rewards = torch.tensor(
            [experience[2] for experience in batch], dtype=torch.float32
        ).view(-1, 1)
        next_states = torch.stack(
            [self._ensure_state_size(experience[3]) for experience in batch]
        )

        # REINFORCE-like algorithm: adjust parameters based on rewards
        predicted = self.model(states)

        # Create target using reward-weighted parameters
        target = parameters.clone()
        for i in range(len(batch)):
            reward_factor = rewards[i].item()
            # Use stronger updates for highly positive/negative rewards
            if abs(reward_factor) > 0.5:  # For significant rewards
                target[i] = (
                    parameters[i] if reward_factor > 0 else (1.0 - parameters[i])
                )
            else:
                # Your existing code for moderate rewards
                if reward_factor > 0:
                    target[i] = parameters[i]
                else:
                    adjustment = -reward_factor * 0.2  # Increased from 0.1
                    target[i] = torch.clamp(
                        predicted[i] + adjustment * (0.5 - parameters[i]), 0, 1
                    )

        # Calculate loss and update model
        self.optimizer.zero_grad()
        loss = self.criterion(predicted, target)
        loss.backward()
        self.optimizer.step()

        return loss.item()

    def _ensure_state_size(self, state):
        """Ensure state tensor is the correct size"""
        if state.size(0) != self.input_size:
            padded_state = torch.zeros(self.input_size, dtype=torch.float32)
            min_size = min(state.size(0), self.input_size)
            padded_state[:min_size] = state[:min_size]
            return padded_state
        return state

    def run_training_games(self, num_games=20, num_epochs=5, display_progress=True):
        """Run multiple games to train the neural network"""
        all_losses = []

        adaptive_epsilon = 0.3  # Start with high exploration

        for epoch in range(num_epochs):
            epoch_losses = []
            wins = 0
            total_reward = 0
            game_turn_counts = []

            print(f"Epoch {epoch+1}/{num_epochs}")
            start_time = time.time()

            for game_num in range(num_games):
                if display_progress and game_num % 5 == 0:
                    print(f"  Game {game_num+1}/{num_games}...")

                # Create parameters for neural bot
                initial_state = torch.zeros(self.input_size, dtype=torch.float32)
                parameters = self.get_bot_parameters(initial_state)

                # Play game with neural bot and opponents
                game = MonopolyGame(
                    bot_count=4,
                    neural_bot_count=1,  # First player is neural bot
                    bots_parameters=bots_parameters,
                )

                # Initialize neural bot with our model
                neural_bot = ActionNeuralBot(
                    player=game.players[0], game=game, display=False
                )
                neural_bot.new_initialise(self.model)
                neural_bot.epsilon = adaptive_epsilon * (
                    1 - epoch / num_epochs
                )  # Gradually decrease exploration
                game.players[0].bot = neural_bot

                # Play the game
                game_result = game.play_game()

                # Extract game and player data
                neural_bot_player = game.players[0]
                game_turn_counts.append(game.turn_count)

                # Calculate initial and final win probabilities for neural bot
                initial_win_prob = 0.25  # Equal chance at start

                # Get final win probability
                player_evaluations, _, _ = calculate_win_probabilities(game)
                final_win_prob = 0
                for player, data in player_evaluations.items():
                    if player == neural_bot_player:
                        final_win_prob = data.get("win_probability", 0)
                        break

                # Calculate reward
                reward = self.calculate_reward(
                    game, neural_bot_player, initial_win_prob, final_win_prob
                )
                total_reward += reward

                # Track wins
                if game.winner == neural_bot_player:
                    wins += 1

                # Create state representation for end of game
                final_state = self.create_game_state_vector(game, neural_bot_player)

                # Store experience
                self.store_experience(initial_state, parameters, reward, final_state)

                # Train from replay memory
                if len(self.memory) >= self.batch_size:
                    loss = self.train_from_memory()
                    epoch_losses.append(loss)

            # Calculate and store metrics
            win_rate = wins / num_games
            avg_reward = total_reward / num_games
            avg_turns = sum(game_turn_counts) / len(game_turn_counts)

            self.win_rates.append(win_rate)
            self.rewards_history.append(avg_reward)
            self.avg_game_length.append(avg_turns)

            all_losses.extend(epoch_losses)

            elapsed_time = time.time() - start_time
            print(f"  Epoch {epoch+1} completed in {elapsed_time:.2f}s")
            print(
                f"  Win rate: {win_rate:.2f}, Avg reward: {avg_reward:.4f}, Avg turns: {avg_turns:.1f}"
            )

            # Show current parameter values
            current_params = self.get_bot_parameters(
                torch.zeros(self.input_size, dtype=torch.float32)
            )
            print("  Current parameters:")
            for name, value in current_params.items():
                print(f"    {name}: {value:.4f}")

            # Save model after each epoch

            # self.save_model(f"models/neural_algorithm_model_epoch_{epoch+1}.pth")

            # At the end of each epoch in run_training_games
            if epoch < num_epochs - 1:  # Don't clear after final epoch
                # Keep the 20% highest-reward experiences, clear the rest
                self.memory.sort(key=lambda x: x[2], reverse=True)
                self.memory = self.memory[: int(len(self.memory) * 0.2)]

            # Update learning rate
            self.optimizer.param_groups[0]["lr"] = self.learning_rate * (
                0.9**epoch
            )  # Decrease learning rate gradually

        # Plot training results
        self.plot_training_results(all_losses)
        self.plot_model_parameters()

        results = {
            "win_rates": self.win_rates,
            "rewards": self.rewards_history,
            "rewards_history": self.rewards_history,
            "avg_game_length": self.avg_game_length,
        }
        return results

    def plot_training_results(self, losses):
        """Plot training metrics"""
        plt.figure(figsize=(15, 10))

        # Plot win rates
        plt.subplot(2, 2, 1)
        plt.plot(self.win_rates, "b-")
        plt.title("Win Rate")
        plt.xlabel("Epoch")
        plt.ylabel("Win Rate")

        # Plot rewards
        plt.subplot(2, 2, 2)
        plt.plot(self.rewards_history, "g-")
        plt.title("Average Reward")
        plt.xlabel("Epoch")
        plt.ylabel("Reward")

        # Plot game length
        plt.subplot(2, 2, 3)
        plt.plot(self.avg_game_length, "r-")
        plt.title("Average Game Length")
        plt.xlabel("Epoch")
        plt.ylabel("Turns")

        # Plot loss
        if losses:
            plt.subplot(2, 2, 4)
            plt.plot(losses, "k-")
            plt.title("Training Loss")
            plt.xlabel("Update")
            plt.ylabel("Loss")

        plt.tight_layout()
        plt.savefig("neural_algorithm_progress.png")
        plt.show()

    def plot_model_parameters(self):
        """Plot model parameters"""

        model = self.model.state_dict()
        # Get parameters from the model
        parameters = []
        layer_sizes = []

        # Collect weights from each layer
        for name, param in model.items():
            if "weight" in name:
                weights = param.detach().numpy()
                parameters.append(weights)
                layer_sizes.append(weights.shape)

        # Create the plot
        plt.figure(figsize=(15, 10))
        plt.suptitle("Neural Network Parameters Visualization", fontsize=16)

        # Calculate grid dimensions based on number of layers
        num_layers = len(parameters)
        if num_layers <= 3:
            grid_rows, grid_cols = 1, num_layers
        else:
            grid_rows = (num_layers + 1) // 2
            grid_cols = 2

        # Plot each layer's parameters
        for i, weights in enumerate(parameters):
            plt.subplot(grid_rows, grid_cols, i + 1)

            # Normalize the weights for better visualization
            weights_normalized = weights / (np.abs(weights).max() + 1e-10)

            # Create heatmap
            im = plt.imshow(weights_normalized, cmap="coolwarm", aspect="auto")

            # Add colorbar
            plt.colorbar(im, fraction=0.046, pad=0.04)

            # Add layer information
            plt.title(f"Layer {i+1} Weights\nShape: {weights.shape}")
            plt.xlabel("Input neurons")
            plt.ylabel("Output neurons")

        plt.tight_layout(rect=[0, 0, 1, 0.95])
        plt.savefig("neural_model_parameters.png")
        plt.show()

        # Additionally, plot parameter statistics
        plt.figure(figsize=(15, 6))

        # Collect statistics for each layer
        means = [p.mean() for p in parameters]
        stds = [p.std() for p in parameters]
        mins = [p.min() for p in parameters]
        maxs = [p.max() for p in parameters]

        # Plot statistics
        layers = [f"Layer {i+1}" for i in range(len(parameters))]
        x = np.arange(len(layers))
        width = 0.2

        plt.bar(x - 1.5 * width, means, width, label="Mean", color="green")
        plt.bar(x - 0.5 * width, stds, width, label="Std Dev", color="blue")
        plt.bar(x + 0.5 * width, mins, width, label="Min", color="red")
        plt.bar(x + 1.5 * width, maxs, width, label="Max", color="purple")

        plt.ylabel("Value")
        plt.title("Parameter Statistics by Layer")
        plt.xticks(x, layers)
        plt.legend()

        plt.tight_layout()
        plt.savefig("neural_model_statistics.png")
        plt.show()

    def save_model(self, filepath="models/neural_algorithm_model.pth"):
        """Save the trained model"""
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        torch.save(self.model.state_dict(), filepath)
        print(f"Model saved to {filepath}")

        # Also save current best parameters
        params = self.get_bot_parameters(
            torch.zeros(self.input_size, dtype=torch.float32)
        )
        with open("best_neural_parameters.json", "w") as f:
            json.dump(params, f, indent=4)
        print(f"Best parameters saved to best_neural_parameters.json")

    def load_model(self, filepath="models/neural_algorithm_model.pth"):
        """Load a trained model"""
        if os.path.exists(filepath):
            self.model.load_state_dict(torch.load(filepath))
            self.model.eval()
            print(f"Model loaded from {filepath}")
            return True
        else:
            print(f"No model found at {filepath}")
            return False


class ActionNeuralBot(Bot):
    """Neural bot that chooses actions directly using the neural network"""

    def __init__(self, player, game, parameters=None, display=True, property=None):
        # Set default parameters if none provided
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
        self.player = player
        self.game = game
        self.display = display

        # Neural network parameters
        self.input_dim = 124  # Match this with NeuralAlgorithm input_size
        self.hidden_dim = 64
        self.output_dim = 10  # Number of different bot actions

        # Initialize neural network
        self.model = self._create_model()
        self.model.eval()  # Set to evaluation mode

        # Action mapping
        self.actions = [
            "buy_property",
            "auction_bid",
            "buy_houses",
            "jail_strategy",
            "accept_trade",
            "initiate_trade",
            "mortgage_property",
            "unmortgage_property",
            "property_evaluation",
            "general_action",
        ]

        # Exploration-exploitation balance
        self.epsilon = 0.2  # Increase from 0.1 to encourage more exploration

        # Training parameters
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
        self.memory = []
        self.batch_size = 32

        # Try to load pre-trained model
        try:
            self.load_model()
            print("Pre-trained action neural bot model loaded")
        except:
            print("No pre-trained action neural bot model found, using new model")

    def _create_model(self):
        """Create neural network model"""
        model = nn.Sequential(
            nn.Linear(self.input_dim, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.hidden_dim),
            nn.ReLU(),
            nn.Linear(self.hidden_dim, self.output_dim),
            nn.Sigmoid(),  # Output probabilities between 0-1
        )
        return model

    def new_initialise(self, model):
        """Initialize the bot with an external model"""
        # Check input dimensions
        input_size = None
        output_size = None

        # Extract model dimensions
        for name, param in model.named_parameters():
            if "0.weight" in name:  # First layer weights
                input_size = param.size(1)
            elif "4.weight" in name:  # Last layer weights in the original model
                output_size = param.size(0)

        if input_size is None or output_size is None:
            print("Warning: Could not determine model dimensions, using defaults")
            input_size = self.input_dim
            output_size = 7  # NeuralAlgorithm default

        print(f"External model dimensions: input={input_size}, output={output_size}")
        print(
            f"Bot expected dimensions: input={self.input_dim}, output={self.output_dim}"
        )

        # We need a more complex adapter if the output dimensions don't match
        needs_adapter = (input_size != self.input_dim) or (
            output_size != self.output_dim
        )

        if needs_adapter:
            print("Creating adapter for model compatibility")

            # Store the external model
            self.external_model = model
            self.using_adapter = True

            # Create input adapter if needed
            if input_size != self.input_dim:
                self.input_adapter = nn.Sequential(
                    nn.Linear(self.input_dim, input_size), nn.ReLU()
                )
            else:
                self.input_adapter = None

            # Create output adapter if needed (map from output_size to our expected output_dim)
            if output_size != self.output_dim:
                self.output_adapter = nn.Sequential(
                    nn.Linear(output_size, self.output_dim),
                    nn.Sigmoid(),  # Keep outputs between 0-1
                )

                # Initialize the output adapter with reasonable weights
                # This ensures the default outputs are around 0.5 (neutral)
                for layer in self.output_adapter:
                    if isinstance(layer, nn.Linear):
                        nn.init.zeros_(layer.weight)
                        nn.init.ones_(layer.bias)
                        layer.bias.data.fill_(
                            0.0
                        )  # Initialize to produce ~0.5 outputs after sigmoid
            else:
                self.output_adapter = None

            # Override the _get_action_probabilities method to use adapters
            def adapted_get_action_probabilities(self_obj):
                state = self_obj._get_state()
                with torch.no_grad():
                    # Apply input adapter if needed
                    if self_obj.input_adapter is not None:
                        adapted_state = self_obj.input_adapter(state)
                    else:
                        adapted_state = state

                    # Pass through external model
                    intermediate_output = self_obj.external_model(adapted_state)

                    # Apply output adapter if needed
                    if self_obj.output_adapter is not None:
                        final_output = self_obj.output_adapter(intermediate_output)
                    else:
                        final_output = intermediate_output

                    return final_output

            self._get_action_probabilities = types.MethodType(
                adapted_get_action_probabilities, self
            )
        else:
            # If dimensions match, simply use the provided model
            self.model = model
            self.using_adapter = False

        print("Neural bot initialized with external model")

    def _get_state(self):
        """Create state representation of the game"""
        state = []

        # Player information
        state.append(self.player.money / 2000.0)  # Normalized money
        state.append(self.player.position / 40.0)  # Normalized position
        state.append(1.0 if self.player.jail_turns > 0 else 0.0)  # In jail?
        state.append(len(self.player.properties) / 28.0)  # Property percentage

        # Property details
        mortgaged_count = sum(
            1
            for p in self.player.properties
            if hasattr(p, "status") and p.status == PropertyStatus.MORTGAGED
        )
        state.append(mortgaged_count / max(1, len(self.player.properties)))

        # Development level
        total_houses = sum(
            getattr(p, "houses", 0)
            for p in self.player.properties
            if hasattr(p, "houses")
        )
        total_hotels = sum(
            1 for p in self.player.properties if hasattr(p, "hotel") and p.hotel
        )
        state.append(total_houses / 32.0)  # Max 32 houses
        state.append(total_hotels / 12.0)  # Max 12 hotels

        # Monopoly sets
        color_counts = {}
        for prop in self.player.properties:
            if hasattr(prop, "color"):
                if prop.color not in color_counts:
                    color_counts[prop.color] = 0
                color_counts[prop.color] += 1

        # Count property types on the board
        color_totals = {}
        for space in self.game.board.spaces:
            if hasattr(space, "color"):
                if space.color not in color_totals:
                    color_totals[space.color] = 0
                color_totals[space.color] += 1

        # Calculate monopoly count
        monopoly_count = 0
        for color, count in color_counts.items():
            if color in color_totals:
                if color == PropertyColor.BROWN or color == PropertyColor.DARK_BLUE:
                    if count == 2:
                        monopoly_count += 1
                elif color == PropertyColor.RAILROAD:
                    if count == 4:
                        monopoly_count += 1
                elif color == PropertyColor.UTILITY:
                    if count == 2:
                        monopoly_count += 1
                elif count == 3:
                    monopoly_count += 1
        state.append(monopoly_count / 8.0)  # 8 possible monopolies

        # Game state
        active_players = sum(1 for p in self.game.players if not p.bankrupt)
        state.append(active_players / 4.0)
        state.append(min(self.game.turn_count, 100) / 100.0)  # Cap at 100 turns

        # Property availability
        available_properties = sum(
            1 for s in self.game.board.spaces if hasattr(s, "owner") and s.owner is None
        )
        state.append(available_properties / 28.0)

        # Opponent information
        opponents = [
            p for p in self.game.players if p != self.player and not p.bankrupt
        ]
        if opponents:
            avg_money = sum(p.money for p in opponents) / len(opponents)
            state.append(avg_money / 2000.0)

            avg_props = sum(len(p.properties) for p in opponents) / len(opponents)
            state.append(avg_props / 28.0)

            # Calculate average opponent development
            total_opp_development = 0
            for opp in opponents:
                houses = sum(
                    getattr(p, "houses", 0)
                    for p in opp.properties
                    if hasattr(p, "houses")
                )
                hotels = sum(
                    1 for p in opp.properties if hasattr(p, "hotel") and p.hotel
                )
                total_opp_development += houses + (hotels * 5)
            avg_development = total_opp_development / max(1, len(opponents))
            state.append(avg_development / 32.0)
        else:
            state.extend([0.0, 0.0, 0.0])

        # Property ownership details (one-hot encoding)
        for i in range(40):
            if i < len(self.game.board.spaces):
                space = self.game.board.spaces[i]
                if hasattr(space, "owner"):
                    # Ownership: 1 if player owns, 0 otherwise
                    state.append(1.0 if space.owner == self.player else 0.0)

                    # Mortgage status: 1 if mortgaged and player-owned, 0 otherwise
                    mortgaged = (
                        hasattr(space, "status")
                        and space.status == PropertyStatus.MORTGAGED
                    )
                    state.append(
                        1.0 if space.owner == self.player and mortgaged else 0.0
                    )

                    # Development: houses/5 if player-owned, 0 otherwise
                    houses = (
                        getattr(space, "houses", 0) if space.owner == self.player else 0
                    )
                    state.append(houses / 5.0)
                else:
                    state.extend([0.0, 0.0, 0.0])
            else:
                state.extend([0.0, 0.0, 0.0])

        # Pad to ensure fixed length
        while len(state) < self.input_dim:
            state.append(0.0)

        # Truncate if too long
        state = state[: self.input_dim]

        return torch.tensor(state, dtype=torch.float32)

    def _get_action_probabilities(self):
        """Get action probabilities from the neural network"""
        state = self._get_state()
        with torch.no_grad():
            return self.model(state)

    def decide_buy_property(self, property):
        """Decide whether to buy a property using neural network"""
        # Exploration: sometimes use standard logic
        if random.random() < self.epsilon:
            return super().decide_buy_property(property)

        # Get action probabilities from network
        action_probs = self._get_action_probabilities()

        # Safety check
        if len(action_probs) < 1:
            return super().decide_buy_property(property)

        buy_prob = action_probs[0].item()  # First output is buy_property

        # Decision based on probability
        return buy_prob > 0.5

    def decide_auction_bid(self, property, current_bid):
        """Decide auction bid using neural network"""
        if random.random() < self.epsilon:
            return super().decide_auction_bid(property, current_bid)

        # Get action probabilities
        action_probs = self._get_action_probabilities()

        # Safety check
        if len(action_probs) < 2:
            return super().decide_auction_bid(property, current_bid)

        bid_percentage = action_probs[1].item()  # Second output is auction_bid

        # Calculate bid based on percentage
        max_affordable = min(self.player.money * 0.8, property.price * 2)
        bid_amount = current_bid + int((max_affordable - current_bid) * bid_percentage)

        # Ensure bid is higher than current bid
        if bid_amount <= current_bid:
            return 0  # Don't bid
        return bid_amount

    def decide_house_purchases(self):
        """Decide whether to buy houses using neural network"""
        if random.random() < self.epsilon:
            return super().decide_house_purchases()

        # Get action probabilities
        action_probs = self._get_action_probabilities()

        # Safety check
        if len(action_probs) < 3:
            return super().decide_house_purchases()

        build_prob = action_probs[2].item()  # Third output is buy_houses

        # If neural network decides not to build
        if build_prob < 0.5:
            return None

        # Otherwise, use standard logic to determine which property
        return super().decide_house_purchases()

    def decide_jail_strategy(self):
        """Decide jail strategy using neural network"""
        if random.random() < self.epsilon:
            return super().decide_jail_strategy()

        # Get action probabilities
        action_probs = self._get_action_probabilities()

        # Safety check
        if len(action_probs) < 4:
            return super().decide_jail_strategy()

        jail_strategy = action_probs[3].item()  # Fourth output is jail_strategy

        # Map probability to strategy
        if jail_strategy < 0.33:
            return "1"  # Try to roll doubles
        elif jail_strategy < 0.67:
            return "2"  # Use get out of jail card
        else:
            return "3"  # Pay fine

    def decide_trade(self, my_property, their_property, cash_amount):
        """Decide whether to accept a trade using neural network"""
        if random.random() < self.epsilon:
            return super().decide_trade(my_property, their_property, cash_amount)

        # Get action probabilities
        action_probs = self._get_action_probabilities()

        # Safety check
        if len(action_probs) < 5:
            return super().decide_trade(my_property, their_property, cash_amount)

        trade_acceptance = action_probs[4].item()  # Fifth output is accept_trade

        return trade_acceptance > 0.5

    def initiate_trade(self):
        """Decide whether to initiate a trade using neural network"""
        if random.random() < self.epsilon:
            return super().initiate_trade()

        # Get action probabilities
        action_probs = self._get_action_probabilities()

        # Safety check
        if len(action_probs) < 6:
            return super().initiate_trade()

        trade_initiation = action_probs[5].item()  # Sixth output is initiate_trade

        if trade_initiation <= 0.5:
            return False

        # Use standard logic to determine the trade
        return super().initiate_trade()

    def decide_mortgage_property(self, amount_needed):
        """Decide mortgage strategy using neural network"""
        if random.random() < self.epsilon:
            return super().decide_mortgage_property(amount_needed)

        # Get action probabilities
        action_probs = self._get_action_probabilities()

        # Safety check
        if len(action_probs) < 7:
            return super().decide_mortgage_property(amount_needed)

        mortgage_decision = action_probs[
            6
        ].item()  # Seventh output is mortgage_property

        # If we need money or the neural network says to mortgage
        if amount_needed > 0 or mortgage_decision > 0.5:
            return super().decide_mortgage_property(amount_needed)

        return False

    def decide_unmortgage_property(self):
        """Decide unmortgage strategy using neural network"""
        if random.random() < self.epsilon:
            return super().decide_unmortgage_property()

        # Get action probabilities
        action_probs = self._get_action_probabilities()

        # Safety check
        if len(action_probs) < 8:
            return super().decide_unmortgage_property()

        unmortgage_decision = action_probs[
            7
        ].item()  # Eighth output is unmortgage_property

        if unmortgage_decision <= 0.5:
            return False

        # Use standard logic to determine which property to unmortgage
        return super().decide_unmortgage_property()

    def make_move(self):
        """Make all decisions for a turn using neural network"""
        # Save initial state for learning
        initial_state = self._get_state()
        initial_money = self.player.money
        initial_properties = len(self.player.properties)

        # If in jail, handle jail strategy
        if self.player.jail_turns > 0:
            return self.decide_jail_strategy()

        # Get action probabilities from network
        action_probs = self._get_action_probabilities()

        # Safety check - ensure action_probs has enough dimensions
        if len(action_probs) < 7:
            print(
                f"Warning: Action probabilities has only {len(action_probs)} values, expected at least 7"
            )
            # Use default values if we don't have enough outputs
            house_purchase_prob = 0.5
            trade_initiation_prob = 0.3
            unmortgage_prob = 0.4
            mortgage_prob = 0.3
        else:
            # Extract specific action probabilities
            # Map the first few values to specific actions even if dimensions don't fully match
            house_purchase_prob = action_probs[min(2, len(action_probs) - 1)].item()
            trade_initiation_prob = (
                action_probs[min(5, len(action_probs) - 1)].item()
                if len(action_probs) > 5
                else 0.3
            )
            unmortgage_prob = (
                action_probs[min(7, len(action_probs) - 1)].item()
                if len(action_probs) > 7
                else 0.4
            )
            mortgage_prob = (
                action_probs[min(6, len(action_probs) - 1)].item()
                if len(action_probs) > 6
                else 0.3
            )

        # House purchases (based on probability)
        if house_purchase_prob > 0.5:
            property = self.decide_house_purchases()
            if property:
                try:
                    self.game.build_house_bot(self.player)
                except:
                    pass  # Ignore errors if house building fails

        # Trading (based on probability)
        if trade_initiation_prob > 0.5:
            self.initiate_trade()

        # Unmortgage properties (based on probability)
        if unmortgage_prob > 0.5:
            self.decide_unmortgage_property()

        # Mortgage properties if needed or if the network suggests it
        min_cash = 50 + (self.cash_reserve_preference * 200)
        if self.player.money < min_cash or mortgage_prob > 0.7:
            self.decide_mortgage_property(max(0, min_cash - self.player.money))

        # Get final state and calculate reward
        final_state = self._get_state()
        reward = self._calculate_reward(initial_state, final_state, initial_money)

        # Store experience for later training
        self.memory.append((initial_state, action_probs, reward, final_state))

    def _calculate_reward(self, initial_state, final_state, initial_money):
        """Calculate reward for the actions taken"""
        reward = 0.0

        # Reward for money increase
        money_change = self.player.money - initial_money
        reward += money_change / 500.0  # Normalize reward for money changes

        # Safe slicing to prevent index errors
        max_idx = min(
            self.input_dim - 3, 120
        )  # Ensure we don't go beyond tensor bounds

        # Reward for property acquisition - count properties owned (every 3rd element starting at index 14)
        initial_props = sum(initial_state[i].item() for i in range(14, max_idx, 3))
        final_props = sum(final_state[i].item() for i in range(14, max_idx, 3))
        if final_props > initial_props:
            reward += 0.3  # Reward for acquiring new properties

        # Reward for development - count house levels (every 3rd element + 2 starting at index 14)
        initial_houses = sum(
            initial_state[i + 2].item()
            for i in range(14, max_idx, 3)
            if i + 2 < self.input_dim
        )
        final_houses = sum(
            final_state[i + 2].item()
            for i in range(14, max_idx, 3)
            if i + 2 < self.input_dim
        )
        if final_houses > initial_houses:
            reward += 0.2 * (final_houses - initial_houses)  # Reward for development

        # Penalty for mortgaging properties (every 3rd element + 1 starting at index 14)
        initial_mortgaged = sum(
            initial_state[i + 1].item()
            for i in range(14, max_idx, 3)
            if i + 1 < self.input_dim
        )
        final_mortgaged = sum(
            final_state[i + 1].item()
            for i in range(14, max_idx, 3)
            if i + 1 < self.input_dim
        )
        if final_mortgaged > initial_mortgaged:
            reward -= 0.1 * (
                final_mortgaged - initial_mortgaged
            )  # Small penalty for mortgaging

        # Reward for unmortgaging
        if final_mortgaged < initial_mortgaged:
            reward += 0.15 * (
                initial_mortgaged - final_mortgaged
            )  # Reward for unmortgaging

        # Reward for winning and penalty for bankruptcy
        if hasattr(self.player, "winner") and self.player.winner:
            reward += 1.0  # Big reward for winning
        if hasattr(self.player, "bankrupt") and self.player.bankrupt:
            reward -= 1.0  # Big penalty for bankruptcy

        return reward

    def _train_from_memory(self):
        """Train neural network from experiences"""
        if len(self.memory) < self.batch_size:
            return

        # Sample batch
        batch = random.sample(self.memory, self.batch_size)

        # Prepare batch data
        states = torch.stack([exp[0] for exp in batch])
        actions = torch.stack([exp[1] for exp in batch])
        rewards = torch.tensor([exp[2] for exp in batch], dtype=torch.float32).view(
            -1, 1
        )

        # Policy gradient approach
        self.optimizer.zero_grad()

        # Forward pass
        predictions = self.model(states)

        # Calculate targets (modify probabilities based on rewards)
        targets = actions.clone()
        for i in range(len(batch)):
            # Scale rewards to keep in reasonable range
            scaled_reward = torch.clamp(rewards[i], -0.5, 0.5)

            # If positive reward, move toward the actions that worked
            if scaled_reward > 0:
                # Increase probability for successful actions
                targets[i] = actions[i] + scaled_reward * (1.0 - actions[i])
            else:
                # Decrease probability for unsuccessful actions
                targets[i] = actions[i] * (1.0 + scaled_reward)

            # Ensure values stay in [0,1] range
            targets[i] = torch.clamp(targets[i], 0.0, 1.0)

        # Calculate loss
        loss = self.criterion(predictions, targets)

        # Backward pass
        loss.backward()
        self.optimizer.step()

        # Occasionally save the model
        if random.random() < 0.05:  # 5% chance
            self.save_model()

    def save_model(self, path="models/action_neural_bot_model.pth"):
        """Save the neural network model"""
        os.makedirs(os.path.dirname(path), exist_ok=True)
        torch.save(self.model.state_dict(), path)

    def load_model(self, path="models/action_neural_bot_model.pth"):
        """Load a previously trained model"""
        if os.path.exists(path):
            self.model.load_state_dict(torch.load(path))
            self.model.eval()
        else:
            raise FileNotFoundError(f"No model found at {path}")


def main():
    """Main function to run the neural algorithm"""
    print("Starting Neural Algorithm for Monopoly")

    # Initialize neural algorithm
    algorithm = NeuralAlgorithm(LEARNING_RATE, MEMORY_SIZE, BATCH_SIZE, HIDDEN_SIZE)

    # Try to load existing model
    model_loaded = algorithm.load_model()
    if not model_loaded:
        print("Starting with a new model")

    # Run training games
    results = algorithm.run_training_games(
        num_games=NUMBER_OF_GAMES, num_epochs=NUMBER_OF_EPOCHS
    )

    # Save trained model
    algorithm.save_model()

    # Display final results
    print("\nTraining completed!")
    print(f"Final win rate: {results['win_rates'][-1]:.2f}")
    print(f"Final average reward: {results['rewards'][-1]:.4f}")
    print("\nOptimal parameters found:")
    for name, value in results["final_parameters"].items():
        print(f"  {name}: {value:.4f}")

    print("\nEvaluating final model in test games...")

    # Run some test games with the final model
    final_params = results["final_parameters"]
    test_wins = 0
    num_test_games = 5

    for i in range(num_test_games):
        print(f"Test game {i+1}/{num_test_games}...")

        # Create a game with neural bot
        game = MonopolyGame(
            bot_count=4,
            neural_bot_count=1,
            bots_parameters=bots_parameters,
        )

        # Initialize neural bot with our model
        neural_bot = ActionNeuralBot(player=game.players[0], game=game, display=False)
        neural_bot.new_initialise(algorithm.model)
        game.players[0].bot = neural_bot

        # Play the game
        game_result = game.play_game()

        if game_result["winner"] == game.players[0]:
            print("Neural bot wins!")
            test_wins += 1

    print(f"\nTest win rate: {test_wins/num_test_games:.2f}")
    print("Neural algorithm training complete!")


if __name__ == "__main__":
    main()
