import unittest
from unittest.mock import MagicMock, patch
import torch
import numpy as np
import pickle
import json


from code.stats import (
    display_statistics,
    display_extended_statistics,
    calculate_win_probabilities,
    display_win_probabilities,
    game_evaluation,
    WinPredictorNN,
    calculate_win_probabilities_nn,
    train_win_predictor,
    save_game_history,
    load_game_history
)

class MockProperty:
    def __init__(self, name, price, color, owner=None, houses=0, hotel=False, status=None, house_price=50):
        self.name = name
        self.price = price
        self.color = color
        self.owner = owner
        self.houses = houses
        self.hotel = hotel
        self.status = status
        self.house_price = house_price
    
    def calculate_rent(self):
        # Simple mock for rent calculation
        base_rent = self.price * 0.1
        if hasattr(self, 'houses') and self.houses > 0:
            return base_rent * (1 + self.houses * 0.5)
        if hasattr(self, 'hotel') and self.hotel:
            return base_rent * 4
        return base_rent

class MockPropertyStatus:
    MORTGAGED = "mortgaged"
    OWNED = "owned"

class MockPropertyColor:
    RAILROAD = "railroad"
    UTILITY = "utility"
    BROWN = "brown"
    BLUE = "blue"
    GREEN = "green"
    RED = "red"
    YELLOW = "yellow"
    ORANGE = "orange"
    PURPLE = "purple"
    LIGHTBLUE = "lightblue"
    
    def __init__(self, value):
        self.value = value

class MockPlayer:
    def __init__(self, name, money, properties=None, bankrupt=False):
        self.name = name
        self.money = money
        self.properties = properties or []
        self.bankrupt = bankrupt

class MockBoard:
    def __init__(self, spaces):
        self.spaces = spaces

class MockGame:
    def __init__(self, players, board):
        self.players = players
        self.board = board
        self.colors = {
            'title': '\033[95m',
            'info': '\033[94m',
            'success': '\033[92m',
            'warning': '\033[93m',
            'error': '\033[91m',
            'reset': '\033[0m',
            'player': '\033[96m',
            'money': '\033[92m',
            'property': '\033[94m',
            'rent': '\033[91m',
            'prompt': '\033[93m'
        }

class TestStats(unittest.TestCase):
    
    def setUp(self):
        # Create sample properties
        self.property_colors = {
            "brown": MockPropertyColor("Brown"),
            "blue": MockPropertyColor("Blue"),
            "railroad": MockPropertyColor("Railroad"),
            "utility": MockPropertyColor("Utility"),
        }
        
        # Create sample players
        self.player1 = MockPlayer("Player1", 1000)
        self.player2 = MockPlayer("Player2", 800)
        self.bankrupt_player = MockPlayer("Bankrupt", 0, bankrupt=True)
        
        # Create sample properties
        self.prop1 = MockProperty("Baltic Avenue", 60, self.property_colors["brown"], self.player1, houses=1)
        self.prop2 = MockProperty("Boardwalk", 400, self.property_colors["blue"], self.player2)
        self.prop3 = MockProperty("Reading Railroad", 200, self.property_colors["railroad"], self.player1)
        self.prop4 = MockProperty("Electric Company", 150, self.property_colors["utility"], self.player2)
        self.prop5 = MockProperty("Mediterranean Avenue", 60, self.property_colors["brown"], self.player1)
        self.prop6 = MockProperty("Unowned Property", 100, self.property_colors["blue"], None)
        
        # Assign properties to players
        self.player1.properties = [self.prop1, self.prop3, self.prop5]
        self.player2.properties = [self.prop2, self.prop4]
        
        # Create board with spaces
        self.spaces = [self.prop1, self.prop2, self.prop3, self.prop4, self.prop5, self.prop6]
        self.board = MockBoard(self.spaces)
        
        # Create game with players and board
        self.game = MockGame([self.player1, self.player2, self.bankrupt_player], self.board)
    
    @patch('builtins.print')
    @patch('builtins.input', return_value='n')  # Mock input to avoid extended statistics
    def test_display_statistics(self, mock_input, mock_print):
        # Test that display_statistics runs without errors
        display_statistics(self.game)
        # Check that print was called
        self.assertTrue(mock_print.called)
    
    @patch('builtins.print')
    @patch('builtins.input', return_value='')  # Mock input for "Press Enter to continue"
    def test_display_extended_statistics(self, mock_input, mock_print):
        # Test that display_extended_statistics runs without errors
        with patch('stats.game_evaluation') as mock_game_eval:
            display_extended_statistics(self.game)
            # Check that game_evaluation was called
            mock_game_eval.assert_called_once_with(self.game)
        self.assertTrue(mock_print.called)
    
    def test_calculate_win_probabilities(self):
        # Test that calculate_win_probabilities returns properly structured data
        player_evaluations, game_progress, game_phase = calculate_win_probabilities(self.game)
        
        # Check that we have evaluations for each player
        self.assertEqual(len(player_evaluations) - 1, 2)  # -1 for total_net_worth key
        
        # Check that we have the expected keys in the evaluation
        for player in [self.player1, self.player2]:
            self.assertIn(player, player_evaluations)
            player_data = player_evaluations[player]
            expected_keys = ['net_worth', 'monopoly_count', 'railroad_count', 
                            'utility_count', 'cash_ratio', 'raw_probability', 
                            'bankruptcy_risk', 'win_probability', 'bankruptcy_probability']
            for key in expected_keys:
                self.assertIn(key, player_data)
        
        # Check that game_progress is between 0 and 1
        self.assertGreaterEqual(game_progress, 0)
        self.assertLessEqual(game_progress, 1)
        
        # Check that game_phase is one of the expected values
        self.assertIn(game_phase, ["Early", "Mid", "Late"])
    
    @patch('builtins.print')
    def test_display_win_probabilities(self, mock_print):
        # Test that display_win_probabilities runs without errors
        player_evaluations = {
            self.player1: {
                'net_worth': 1500,
                'win_probability': 70,
                'bankruptcy_probability': 20,
                'monopoly_count': 1,
                'railroad_count': 1,
                'cash_ratio': 0.4
            },
            self.player2: {
                'net_worth': 1200,
                'win_probability': 30,
                'bankruptcy_probability': 80,
                'monopoly_count': 0,
                'railroad_count': 0,
                'cash_ratio': 0.1
            },
            'total_net_worth': 2700
        }
        
        display_win_probabilities(self.game, player_evaluations, 0.5, "Mid")
        self.assertTrue(mock_print.called)
    
    @patch('stats.calculate_win_probabilities')
    @patch('stats.display_win_probabilities')
    @patch('builtins.print')
    def test_game_evaluation(self, mock_print, mock_display, mock_calculate):
        # Setup mock return values
        mock_calculate.return_value = ({}, 0.5, "Mid")
        
        # Test game evaluation with multiple active players
        game_evaluation(self.game)
        
        # Verify that the functions were called
        mock_calculate.assert_called_once_with(self.game)
        mock_display.assert_called_once()
        
        # Test with only one active player
        self.player2.bankrupt = True
        game_evaluation(self.game)
        
        # Verify that print is called with winning message
        mock_print.assert_any_call(f"{self.game.colors['success']}{self.player1.name} is the only player remaining and will win!")
    
    def test_win_predictor_nn_model(self):
        # Test that WinPredictorNN model can be created and forward pass works
        model = WinPredictorNN()
        
        # Create a sample input tensor
        batch_size = 2
        features = 6  # net_worth, monopoly_count, railroad_count, utility_count, cash_ratio, game_progress
        x = torch.rand(batch_size, features)
        
        # Forward pass
        output = model(x)
        
        # Check output shape and values
        self.assertEqual(output.shape, (batch_size, 2))  # win_probability, bankruptcy_probability
        self.assertTrue(torch.all(output >= 0) and torch.all(output <= 1))  # Output should be between 0 and 1

    @patch('torch.load')
    @patch('stats.calculate_win_probabilities')
    def test_calculate_win_probabilities_nn(self, mock_calculate, mock_torch_load):
        # Mock torch.load to return a model
        mock_model = MagicMock()
        mock_model.return_value = torch.tensor([[0.7, 0.3], [0.4, 0.6]])
        mock_torch_load.return_value = mock_model
        mock_calculate.return_value = ({self.player1: {'win_probability': 60, 'bankruptcy_probability': 40},
                                       self.player2: {'win_probability': 40, 'bankruptcy_probability': 60},
                                       'total_net_worth': 2700}, 0.5, "Mid")
        
        # Test function
        with patch('torch.FloatTensor', return_value=torch.rand(1, 6)):
            player_evaluations, game_progress, game_phase = calculate_win_probabilities_nn(self.game)
        
        # Check results
        self.assertIn('total_net_worth', player_evaluations)
        self.assertEqual(game_phase, "Mid")
        self.assertEqual(game_progress, 0.5)

    @patch('pickle.dump')
    def test_save_game_history(self, mock_dump):
        # Test save_game_history
        with patch('builtins.open') as mock_open:
            save_game_history("test.pkl")
            mock_open.assert_called_once_with("test.pkl", 'wb')
            mock_dump.assert_called_once()

    @patch('pickle.load')
    @patch('builtins.print')
    def test_load_game_history(self, mock_print, mock_load):
        # Test successful load
        mock_load.return_value = [[self.game, self.game]]
        
        with patch('builtins.open'):
            result = load_game_history("test.pkl")
            self.assertEqual(result, [[self.game, self.game]])
        
        # Test file not found
        mock_load.side_effect = FileNotFoundError()
        
        with patch('builtins.open'):
            result = load_game_history("nonexistent.pkl")
            self.assertEqual(result, [[]])
        
        # Test other exception
        mock_load.side_effect = Exception("Test error")
        
        with patch('builtins.open'):
            result = load_game_history("error.pkl")
            self.assertEqual(result, [[]])

    @patch('torch.save')
    @patch('torch.FloatTensor')
    @patch('stats.calculate_win_probabilities')
    @patch('builtins.print')
    def test_train_win_predictor(self, mock_print, mock_calculate, mock_float_tensor, mock_torch_save):
        # Mock torch.FloatTensor to return valid tensors
        mock_float_tensor.side_effect = [
            torch.rand(5, 6),  # inputs
            torch.rand(5, 2)   # targets
        ]
        
        # Mock calculate_win_probabilities to return valid data
        player_data = {
            'net_worth': 1000,
            'monopoly_count': 1,
            'railroad_count': 1,
            'utility_count': 0,
            'cash_ratio': 0.5,
            'win_probability': 60,
            'bankruptcy_probability': 30
        }
        
        mock_calculate.return_value = (
            {self.player1: player_data, self.player2: player_data, 'total_net_worth': 2000},
            0.5,
            "Mid"
        )
        
        # Test with fewer epochs for speed
        with patch('torch.optim.Adam'):
            train_win_predictor([self.game], epochs=2)
        
        # Verify model was saved
        mock_torch_save.assert_called_once()

if __name__ == '__main__':
    unittest.main()

