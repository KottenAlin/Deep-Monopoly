# Deep Monopoly

Deep Monopoly is a strategic implementation of the classic board game Monopoly, enhanced with artificial intelligence techniques. This project utilizes a neural network-based bot and a Monte Carlo Tree Search (MCTS) algorithm to make intelligent decisions during gameplay.

## Features

- **NeuralBot**: A bot that uses a neural network to make decisions regarding property purchases, trades, and house developments.
- **Monte Carlo Tree Search (MCTS)**: An algorithm that simulates potential future game states to make optimal decisions.
- **Simulation Utilities**: Functions to simulate game turns and evaluate game states for testing and training purposes.

## Project Structure

```
deep-monopoly
├── code
│   ├── Bot.py                # Implementation of the NeuralBot class
│   ├── mcts                  # Monte Carlo Tree Search module
│   │   ├── __init__.py
│   │   ├── node.py           # Node class for MCTS
│   │   ├── mcts.py           # MCTS algorithm implementation
│   │   └── state.py          # Game state representation for MCTS
│   ├── utils                 # Utility functions for simulations
│   │   ├── __init__.py
│   │   └── simulation.py
│   └── neural_models         # Neural network models
│       ├── __init__.py
│       └── models.py
├── models
│   └── neural_bot_model.pth   # Pre-trained model for the neural bot
├── tests
│   └── test_mcts.py          # Unit tests for MCTS implementation
└── README.md                 # Project documentation
```

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/deep-monopoly.git
   cd deep-monopoly
   ```

2. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

## Usage

To run the game with the NeuralBot, execute the following command:

```
python code/Bot.py
```

You can also run tests for the MCTS implementation using:

```
python -m unittest tests/test_mcts.py
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request or open an issue for any suggestions or improvements.

## License

This project is licensed under the MIT License. See the LICENSE file for more details.