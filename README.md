# Deep-Monopoly

An AI approach to mastering the game of Monopoly using deep learning techniques.

For further reading in Swedish, visit [Dokumentation](./Dokumentation.md)

## Overview

Deep-Monopoly is a project that applies deep reinforcement learning algorithms to develop an AI agent capable of playing Monopoly. By modeling the game's complex decision space and economic principles, our agent learns optimal strategies for property acquisition, development, and negotiation.

## Features

- ~~Game state representation using neural networks~~
- ~~Reinforcement learning models for decision making~~
- ~~Strategy evaluation in various game scenarios~~
- ~~Performance metrics and visualization tools~~

## Getting Started

### Prerequisites

```
python >= 3.8
pytorch

numpy
matplotlib
colorama

```

### Installation

```bash
git clone https://github.com/yourusername/Deep-Monopoly.git
cd Deep-Monopoly
pip install -r requirements.txt
```

## Usage

```python

```python
# Run the main game
python code/main.py

# Train a neural network agent
python code/neural_algorithm.py --train

# Run a genetic algorithm experiment
python code/genetic_algorithem.py


## Methodology

### Game Development
1. **Foundation**: Built a text-based Monopoly game with solid architecture
2. **Features**: Implemented property purchases, auctions, house building, and mortgaging
3. **Rule-based Agents**: Created bots with predefined strategies for baseline comparison
4. **Analytics**: Added statistics tracking for wins and various game metrics

### AI Implementation
1. **Neural Agent**: Developed an AI agent using PyTorch
2. **State Representation**: Created neural network inputs with game state information
3. **Action Representation**: Designed output layers for decision-making processes
4. **Training Methods**: Applied self-play tournaments and experience replay
5. **Reward Function**: Created rewards based on money, properties, monopolies, and win probability

## Results

Our implementation successfully created a fully functional Monopoly environment with an AI agent capable of playing against both rule-based bots and other AI agents. Key findings:

- The technical framework works correctly, but training results are suboptimal
- AI agents can compete against rule-based opponents but show limited strategic depth
- The reward function struggles to connect early decisions with final outcomes
- Loss function decreases during training, but gameplay improvement is difficult to measure

We discovered several effective Monopoly strategies:

1. **House Strategy**: Rapid development of three houses on properties
2. **Economic Strategy**: Maintaining cash reserves over single properties
3. **Trading Strategy**: Strategic exchanges to secure monopolies
4. **Tactical Approaches**: Station valuation, utility considerations, and jail tactics
5. **Endgame Strategy**: Focus on cash flow and property development to maximize winning chances





## Contributing

Sebastian Alin: Sebastian200 and KottenAlin

## License

This project is licensed under the MIT License - see the LICENSE file for details.
