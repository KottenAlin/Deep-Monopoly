import random
import matplotlib.pyplot as plt

from monopoly_for_bots import MonopolyGame, bots_parameters
from Bot import Bot, parameters


class GeneticBot(Bot):
    def __init__(
        self, player, game, parameters=parameters, display=True, property=None
    ):
        super().__init__(player, game, parameters, display, property)
        self.player = player
        self.game = game
        self.display = display
        self.generation = 0
        self.fitness_score = 0
        self.parameters = parameters

    @staticmethod
    def generate_population(size=30):
        """Generate a population of parameter sets for genetic algorithm"""
        population = []
        for _ in range(size):
            params = {
                "risk_tolerance": random.random(),
                "property_focus": random.random(),
                "development_focus": random.random(),
                "cash_reserve_preference": random.random(),
                "trade_willingness": random.random(),
                "monopoly_focus": random.random(),
                "railroad_utility_interest": random.random(),
            }
            population.append(params)
        return population

    @staticmethod
    def select_parents(population, fitness_scores, num_parents=10):
        """Select parents using tournament selection"""
        parents = []
        # Normalize fitness scores
        total_fitness = sum(fitness_scores)
        if total_fitness == 0:
            # If all scores are 0, select randomly
            return random.sample(population, num_parents)

        probabilities = [score / total_fitness for score in fitness_scores]

        # Select parents based on probabilities
        for _ in range(num_parents):
            # Tournament selection
            tournament_size = min(5, len(population))
            tournament_indices = random.sample(range(len(population)), tournament_size)
            tournament_fitness = [fitness_scores[i] for i in tournament_indices]
            winner_idx = tournament_indices[
                tournament_fitness.index(max(tournament_fitness))
            ]
            parents.append(population[winner_idx])

        return parents

    @staticmethod
    def crossover(parents, population_size=30):
        """Perform crossover to create new generation"""
        offspring = []

        # Always keep some of the best parents
        elite_count = min(5, len(parents))
        offspring.extend(parents[:elite_count])

        # Create the rest through crossover
        while len(offspring) < population_size:
            parent1, parent2 = random.sample(parents, 2)
            child = {}

            # Uniform crossover - each parameter has 50% chance from each parent
            for param in parent1:
                if random.random() < 0.5:
                    child[param] = parent1[param]
                else:
                    child[param] = parent2[param]

            offspring.append(child)

        return offspring

    @staticmethod
    def mutate(population, mutation_rate=0.1, mutation_amount=0.2):
        """Apply random mutations to the population"""
        mutated_population = []

        for params in population:
            mutated_params = params.copy()

            for param in mutated_params:
                # Apply mutation with probability
                if random.random() < mutation_rate:
                    # Add or subtract a random amount
                    delta = (random.random() * 2 - 1) * mutation_amount
                    mutated_params[param] = max(
                        0, min(1, mutated_params[param] + delta)
                    )

            mutated_population.append(mutated_params)

        return mutated_population

    def calculate_fitness(self, game_result):
        """Calculate fitness based on game results"""
        # Base fitness on game outcome
        if self.player.bankrupt:
            # Penalize bankruptcy, but consider how long the bot survived
            turn_count = game_result.get("turn_count", 0)
            max_turns = game_result.get("max_turns", 100)
            survival_ratio = turn_count / max_turns
            return 10 * survival_ratio  # Max 10 points for surviving but going bankrupt

        # If not bankrupt, use asset value and ranking
        rank = game_result.get("rank", 0)
        player_count = game_result.get("player_count", 4)

        # Calculate asset value (money + property value)
        money = self.player.money
        property_value = sum(p.price for p in self.player.properties)

        # Factor in houses and hotels
        building_value = sum(
            (p.houses * p.house_price)
            for p in self.player.properties
            if hasattr(p, "houses") and p.houses > 0
        )
        building_value += sum(
            (5 * p.house_price)
            for p in self.player.properties
            if hasattr(p, "hotel") and p.hotel
        )

        # Calculate total assets
        total_assets = money + property_value + building_value

        # Normalize assets (assume 10000 is a good amount)
        asset_score = min(50, total_assets / 200)

        # Calculate rank score (winning is best)
        rank_score = 50 * (player_count - rank) / (player_count - 1)

        # Combine scores
        fitness = asset_score + rank_score

        # Add bonus for winning
        if rank == 1:
            fitness += 100

        return fitness

    @classmethod
    def evolve_population(cls, population, fitness_scores):
        """Evolve the population based on fitness scores"""
        # Select parents based on fitness
        parents = cls.select_parents(population, fitness_scores)

        # Create new offspring through crossover
        offspring = cls.crossover(parents)

        # Apply mutations
        mutated_offspring = cls.mutate(offspring)

        return mutated_offspring

    @staticmethod
    def run_genetic_algorithm(
        generations=20, population_size=30, games_per_individual=5
    ):
        """Run the complete genetic algorithm process"""
        # Generate initial population
        population = GeneticBot.generate_population(population_size)

        best_fitness_history = []
        avg_fitness_history = []
        best_parameters = None
        best_fitness = 0

        for gen in range(generations):
            print(f"Generation {gen+1}/{generations}")
            fitness_scores = []

            # Evaluate each individual in the population
            for i, params in enumerate(population):
                individual_fitness = 0

                # Run multiple games for more accurate evaluation
                for _ in range(games_per_individual):
                    # Set up a new game
                    game = MonopolyGame(
                        bot_count=4, neural_bot_count=0, bots_parameters=bots_parameters
                    )

                    # Replace player 0 with our genetic bot
                    player = game.players[0]
                    player.bot = GeneticBot(player, game, params, display=False)
                    player.is_bot = True

                    # Run the game
                    game_result = game.play_game()

                    # Calculate fitness
                    individual_fitness += player.bot.calculate_fitness(game_result)

                # Average fitness across games
                avg_fitness = individual_fitness / games_per_individual
                fitness_scores.append(avg_fitness)

                # Track best individual
                if avg_fitness > best_fitness:
                    best_fitness = avg_fitness
                    best_parameters = params.copy()

                print(
                    f"Individual {i+1}/{len(population)}: Fitness = {avg_fitness:.2f}"
                )

            # Record history
            best_fitness_history.append(max(fitness_scores))
            avg_fitness_history.append(sum(fitness_scores) / len(fitness_scores))

            # Evolve population
            population = GeneticBot.evolve_population(population, fitness_scores)

            print(
                f"Generation {gen+1} complete. Best fitness: {max(fitness_scores):.2f}, Avg fitness: {sum(fitness_scores)/len(fitness_scores):.2f}"
            )

        # Plot results
        plt.figure(figsize=(10, 6))
        plt.plot(range(1, generations + 1), best_fitness_history, label="Best Fitness")
        plt.plot(
            range(1, generations + 1), avg_fitness_history, label="Average Fitness"
        )
        plt.xlabel("Generation")
        plt.ylabel("Fitness")
        plt.title("Genetic Algorithm Progress")
        plt.legend()
        plt.savefig("genetic_algorithm_progress.png")
        plt.close()

        return best_parameters

    @staticmethod
    def save_best_parameters(parameters, filename="best_genetic_parameters.json"):
        """Save the best parameters to a file"""
        import json

        with open(filename, "w") as f:
            json.dump(parameters, f)
        print(f"Best parameters saved to {filename}")

    @staticmethod
    def load_parameters(filename="best_genetic_parameters.json"):
        """Load parameters from a file"""
        import json

        try:
            with open(filename, "r") as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"Parameter file {filename} not found. Using default parameters.")
            return parameters  # Use the global default

    @staticmethod
    def train(
        generations=20, population_size=30, games_per_individual=5, save_results=True
    ):
        """Train the genetic bot and optionally save the best parameters"""
        best_parameters = GeneticBot.run_genetic_algorithm(
            generations=generations,
            population_size=population_size,
            games_per_individual=games_per_individual,
        )

        if save_results and best_parameters:
            GeneticBot.save_best_parameters(best_parameters)

        return best_parameters

    @classmethod
    def create_trained_bot(cls, player, game, display=True):
        """Create a bot using the best trained parameters"""
        best_params = cls.load_parameters()
        return cls(player, game, best_params, display)

    def make_move(self):
        """Make all decisions for a turn."""
        # Start tracking state before move
        old_money = self.player.money
        old_properties = len(self.player.properties)
        old_buildings = sum(
            getattr(p, "houses", 0) for p in self.player.properties
        ) + sum(1 for p in self.player.properties if getattr(p, "hotel", False))

        # Use the parent class implementation for decision-making
        result = super().make_move()

        # Update fitness based on move results (optional during gameplay)
        money_change = self.player.money - old_money
        property_change = len(self.player.properties) - old_properties
        new_buildings = sum(
            getattr(p, "houses", 0) for p in self.player.properties
        ) + sum(1 for p in self.player.properties if getattr(p, "hotel", False))
        building_change = new_buildings - old_buildings

        # Simple heuristic fitness updates during gameplay
        if money_change > 0:
            self.fitness_score += money_change / 500
        if property_change > 0:
            self.fitness_score += 5 * property_change
        if building_change > 0:
            self.fitness_score += 3 * building_change

        return result

    def display_fitness(self):
        """Display the fitness score"""
        print(f"Fitness Score: {self.fitness_score:.2f}")
        plt.plot(self.fitness_score)
        plt.title("Fitness Score Over Time")
        plt.xlabel("Turn")
        plt.ylabel("Fitness Score")
        plt.show()
        # Save the plot
        plt.savefig("fitness_score_over_time.png")


def main():
    # Train the genetic bot
    best_parameters = GeneticBot.train(
        generations=20, population_size=30, games_per_individual=5, save_results=True
    )

    # Display the best parameters
    print("Best parameters found:")
    for param, value in best_parameters.items():
        print(f"{param}: {value:.4f}")
    input("Press Enter to continue...")
    # Create a game with a trained genetic bot
    game = MonopolyGame(
        bot_count=4, neural_bot_count=0, bots_parameters=best_parameters
    )

    # Set player 0 as a genetic bot with trained parameters
    player = game.players[0]
    player.is_bot = True
    player.bot = GeneticBot.create_trained_bot(player, game)

    # Start the game
    game.play_game()


if __name__ == "__main__":
    main()
