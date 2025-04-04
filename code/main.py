import sys
import os
import monopoly_game as monopoly_game
import monopoly_for_bots
import neural_algorithm
from colorama import init, Fore, Back, Style
import stats as stats


colors = {
    'title': Fore.CYAN + Style.BRIGHT,
    'prompt': Fore.YELLOW,
    'info': Fore.WHITE,
    'success': Fore.GREEN,
    'error': Fore.RED,
    'reset': Style.RESET_ALL,
}

def main():
    while True:
        print(f"{colors['title']}\n===== MONOPOLY MENU =====")
        print(f"{colors['info']}1. Play Monopoly")
        print(f"{colors['info']}2. Simulate Bot Games")
        print(f"{colors['info']}3. Train Neural bots")
        print(f"{colors['info']}4. View Statistics")
        print(f"{colors['info']}5. Exit")
        
        choice = input(f"\n{colors['prompt']}Enter your choice (1-4): {colors['reset']}")
        
        if choice == '1':
            
            monopoly_game.MonopolyGame().play_game()
            
        elif choice == '2':
            # Simulate games between bots
            monopoly_for_bots.MonopolyGame().play_game()
            
        elif choice == '3':
            # Train neural bots
            print(f"{colors['info']}Training neural bots...")
            neural_algorithm
        elif choice == '4':
            # Display game statistics
            print(f"{colors['title']}===== GAME STATISTICS =====")
            stats.display_statistics()
        
        elif choice == '5' or choice == 'exit':
            print(f"{colors['success']}Thank you for playing Monopoly!")
            sys.exit(0)
            
        else:
            print(f"{colors['error']}Invalid choice. Please try again.")
            
        os.system('cls' if os.name == 'nt' else 'clear')

if __name__ == "__main__":
    main()