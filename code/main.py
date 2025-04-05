import sys
import os

import genetic_algorithem
import monopoly_game as monopoly_game
import monopoly_for_bots
import neural_algorithm
import stats as stats

from variables import colors, game_stats

def display_statistics():
    """Display the current game statistics if available."""
    if not game_stats or game_stats["games_played"] == 0:
        print(f"{colors['error']}No statistics available yet. Play some games first!")
    else:
        try:
            stats.display_game_statistics(game_stats)
        except Exception as e:
            print(f"{colors['error']}Error displaying statistics: {e}")
    
    input(f"{colors['prompt']}Press Enter to return to the menu...{colors['reset']}")

def main():
    while True:
        try:
            print(f"{colors['title']}\n===== MONOPOLY MENU =====")
            print(f"{colors['info']}1. Play Monopoly")
            print(f"{colors['info']}2. Simulate Bot Games")
            print(f"{colors['info']}3. Train Neural bots")
            print(f"{colors['info']}4. Train Genetic Algorithm")
            print(f"{colors['info']}5. View Statistics")
            print(f"{colors['info']}6. Exit")
            
            choice = input(f"\n{colors['prompt']}Enter your choice (1-6): {colors['reset']}")
            
            if choice == '1':
                try:
                    monopoly_game.MonopolyGame().play_game()
                except Exception as e:
                    print(f"{colors['error']}Error during game: {e}")
                    input(f"{colors['prompt']}Press Enter to continue...{colors['reset']}")
                
            elif choice == '2':
                # Simulate games between bots
                try:
                    monopoly_for_bots.main()
                except Exception as e:
                    print(f"{colors['error']}Error during bot simulation: {e}")
                    input(f"{colors['prompt']}Press Enter to continue...{colors['reset']}")
                
            elif choice == '3':
                # Train neural bots
                try:
                    print(f"{colors['info']}Training neural bots...")
                    neural_algorithm.main()
                except Exception as e:
                    print(f"{colors['error']}Error training neural bots: {e}")
                    input(f"{colors['prompt']}Press Enter to continue...{colors['reset']}")
                    
            elif choice == '4':
                # Train genetic algorithm
                try:
                    print(f"{colors['info']}Training genetic algorithm...")
                    genetic_algorithem.main()
                except Exception as e:
                    print(f"{colors['error']}Error training genetic algorithm: {e}")
                    input(f"{colors['prompt']}Press Enter to continue...{colors['reset']}")
                    
            elif choice == '5':
                # Display game statistics
                display_statistics()
            
            elif choice == '6' or choice.lower() == 'exit':
                print(f"{colors['success']}Thank you for playing Monopoly!")
                sys.exit(0)
                
            else:
                print(f"{colors['error']}Invalid choice. Please enter a number between 1 and 6.")
                input(f"{colors['prompt']}Press Enter to continue...{colors['reset']}")
                
        except KeyboardInterrupt:
            print(f"{colors['error']}\nOperation interrupted. Returning to menu...")
            input(f"{colors['prompt']}Press Enter to continue...{colors['reset']}")
        except Exception as e:
            print(f"{colors['error']}An unexpected error occurred: {e}")
            input(f"{colors['prompt']}Press Enter to continue...{colors['reset']}")
            
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{colors['error']}Game interrupted. Exiting...")
        os.system('cls' if os.name == 'nt' else 'clear')

