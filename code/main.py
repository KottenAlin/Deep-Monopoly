import sys
import os

import genetic_algorithem
import monopoly_game as monopoly_game
import monopoly_for_bots
import neural_algorithm
import stats as stats

from variables import colors



def main():
    while True:
        print(f"{colors['title']}\n===== MONOPOLY MENU =====")
        print(f"{colors['info']}1. Play Monopoly")
        print(f"{colors['info']}2. Simulate Bot Games")
        print(f"{colors['info']}3. Train Neural bots")
        print(f"{colors['info']}4. Train Genetic Algorithm")
        print(f"{colors['info']}5. View Statistics")
        print(f"{colors['info']}6. Exit")
        
        choice = input(f"\n{colors['prompt']}Enter your choice (1-4): {colors['reset']}")
        
        if choice == '1':
            
            monopoly_game.MonopolyGame().play_game()
            
        elif choice == '2':
            # Simulate games between bots
            monopoly_for_bots.main()
            
        elif choice == '3':
            # Train neural bots
            print(f"{colors['info']}Training neural bots...")
            neural_algorithm.main()
        elif choice == '4':
            # Train genetic algorithm
            print(f"{colors['info']}Training genetic algorithm...")
            genetic_algorithem.main()
        elif choice == '5':
            # Display game statistics
            print(f"{colors['title']}===== GAME STATISTICS =====")
            print(f"{colors['error']} Statistics are not available yet.")
            input(f"{colors['prompt']}Press Enter to return to the menu...{colors['reset']}")
        
        elif choice == '6' or choice == 'exit':
            print(f"{colors['success']}Thank you for playing Monopoly!")
            sys.exit(0)
            
        else:
            print(f"{colors['error']}Invalid choice. Please try again.")
            
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"{colors['error']}Game interrupted. Exiting...")
        os.system('cls' if os.name == 'nt' else 'clear')

        