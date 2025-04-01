def run_simulation(bot, game, num_simulations=100):
    results = []
    
    for _ in range(num_simulations):
        # Clone the game state for simulation
        game_copy = game.clone()
        bot_copy = bot.clone()
        
        while not game_copy.is_over():
            move = bot_copy.make_move()
            game_copy.apply_move(move)
        
        results.append(game_copy.get_winner())
    
    return results

def evaluate_bot(bot, game, num_simulations=100):
    results = run_simulation(bot, game, num_simulations)
    win_count = results.count(bot.player)
    return win_count / num_simulations

def simulate_turn(bot, game):
    # Simulate a single turn for the bot
    move = bot.make_move()
    game.apply_move(move)
    return game.get_state()  # Return the new state after the move

def simulate_full_game(bot, game):
    # Simulate a full game until completion
    while not game.is_over():
        simulate_turn(bot, game)
    return game.get_winner()  # Return the winner at the end of the game
