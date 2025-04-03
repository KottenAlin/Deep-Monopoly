# filepath: c:\Users\22sebali\Desktop\Important\Mer ai\Deep-Monopoly\deep-monopoly\code\mcts\__init__.py
from .state import State, Action, ActionType
from .node import MCTSNode
from .mcts import MCTS

# Example game initialization
from deep-monopoly.code.Bot import MCTSNeuralBot

# Initialize game and players
game = Game()
player1 = Player("MCTS Neural Bot")
player2 = Player("Regular Bot")

# Create bots
mcts_neural_bot = MCTSNeuralBot(player1, game)
regular_bot = Bot(player2, game)

# Run the game
game.run()