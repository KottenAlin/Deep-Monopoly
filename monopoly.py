import random
from enum import Enum
import time

# Define player class
class Player:
    def __init__(self, name):
        self.name = name
        self.position = 0
        self.money = 1500
        self.properties = []
        self.in_jail = False
        self.jail_turns = 0
        self.get_out_of_jail_cards = 0

    def move(self, steps):
        self.position = (self.position + steps) % 40
        return self.position

# Define property class
class Property:
    def __init__(self, name, position, price, rent, color_group=None):
        self.name = name
        self.position = position
        self.price = price
        self.rent = rent
        self.owner = None
        self.color_group = color_group
        self.houses = 0
        self.hotel = False

# Define card types
class CardType(Enum):
    CHANCE = 1
    COMMUNITY_CHEST = 2

# Define the board
def create_board():
    board = [
        {"name": "GO", "type": "go"},
        {"name": "Mediterranean Avenue", "type": "property", "price": 60, "rent": 2, "color": "brown"},
        {"name": "Community Chest", "type": "card", "card_type": CardType.COMMUNITY_CHEST},
        {"name": "Baltic Avenue", "type": "property", "price": 60, "rent": 4, "color": "brown"},
        {"name": "Income Tax", "type": "tax", "amount": 200},
        {"name": "Reading Railroad", "type": "railroad", "price": 200, "rent": 25},
        {"name": "Oriental Avenue", "type": "property", "price": 100, "rent": 6, "color": "light blue"},
        {"name": "Chance", "type": "card", "card_type": CardType.CHANCE},
        {"name": "Vermont Avenue", "type": "property", "price": 100, "rent": 6, "color": "light blue"},
        {"name": "Connecticut Avenue", "type": "property", "price": 120, "rent": 8, "color": "light blue"},
        {"name": "Jail / Just Visiting", "type": "jail"},
        {"name": "St. Charles Place", "type": "property", "price": 140, "rent": 10, "color": "pink"},
        {"name": "Electric Company", "type": "utility", "price": 150},
        {"name": "States Avenue", "type": "property", "price": 140, "rent": 10, "color": "pink"},
        {"name": "Virginia Avenue", "type": "property", "price": 160, "rent": 12, "color": "pink"},
        {"name": "Pennsylvania Railroad", "type": "railroad", "price": 200, "rent": 25},
        {"name": "St. James Place", "type": "property", "price": 180, "rent": 14, "color": "orange"},
        {"name": "Community Chest", "type": "card", "card_type": CardType.COMMUNITY_CHEST},
        {"name": "Tennessee Avenue", "type": "property", "price": 180, "rent": 14, "color": "orange"},
        {"name": "New York Avenue", "type": "property", "price": 200, "rent": 16, "color": "orange"},
        {"name": "Free Parking", "type": "free_parking"},
        {"name": "Kentucky Avenue", "type": "property", "price": 220, "rent": 18, "color": "red"},
        {"name": "Chance", "type": "card", "card_type": CardType.CHANCE},
        {"name": "Indiana Avenue", "type": "property", "price": 220, "rent": 18, "color": "red"},
        {"name": "Illinois Avenue", "type": "property", "price": 240, "rent": 20, "color": "red"},
        {"name": "B&O Railroad", "type": "railroad", "price": 200, "rent": 25},
        {"name": "Atlantic Avenue", "type": "property", "price": 260, "rent": 22, "color": "yellow"},
        {"name": "Ventnor Avenue", "type": "property", "price": 260, "rent": 22, "color": "yellow"},
        {"name": "Water Works", "type": "utility", "price": 150},
        {"name": "Marvin Gardens", "type": "property", "price": 280, "rent": 24, "color": "yellow"},
        {"name": "Go To Jail", "type": "go_to_jail"},
        {"name": "Pacific Avenue", "type": "property", "price": 300, "rent": 26, "color": "green"},
        {"name": "North Carolina Avenue", "type": "property", "price": 300, "rent": 26, "color": "green"},
        {"name": "Community Chest", "type": "card", "card_type": CardType.COMMUNITY_CHEST},
        {"name": "Pennsylvania Avenue", "type": "property", "price": 320, "rent": 28, "color": "green"},
        {"name": "Short Line Railroad", "type": "railroad", "price": 200, "rent": 25},
        {"name": "Chance", "type": "card", "card_type": CardType.CHANCE},
        {"name": "Park Place", "type": "property", "price": 350, "rent": 35, "color": "blue"},
        {"name": "Luxury Tax", "type": "tax", "amount": 100},
        {"name": "Boardwalk", "type": "property", "price": 400, "rent": 50, "color": "blue"}
    ]
    return board

# Create chance cards
def create_chance_cards():
    cards = [
        "Advance to Go. Collect $200.",
        "Advance to Illinois Avenue. If you pass Go, collect $200.",
        "Advance to St. Charles Place. If you pass Go, collect $200.",
        "Advance to the nearest Railroad. If unowned, you may buy it from the Bank.",
        "Advance to the nearest Utility. If unowned, you may buy it from the Bank.",
        "Bank pays you dividend of $50.",
        "Get Out of Jail Free.",
        "Go Back 3 Spaces.",
        "Go to Jail. Go directly to Jail, do not pass Go, do not collect $200.",
        "Make general repairs on all your property. For each house pay $25, for each hotel pay $100.",
        "Speeding fine $15.",
        "Take a trip to Reading Railroad. If you pass Go, collect $200.",
        "You have been elected Chairman of the Board. Pay each player $50.",
        "Your building loan matures. Collect $150."
    ]
    random.shuffle(cards)
    return cards

# Create community chest cards
def create_community_chest_cards():
    cards = [
        "Advance to Go. Collect $200.",
        "Bank error in your favor. Collect $200.",
        "Doctor's fee. Pay $50.",
        "From sale of stock you get $50.",
        "Get Out of Jail Free.",
        "Go to Jail. Go directly to jail, do not pass Go, do not collect $200.",
        "Holiday fund matures. Receive $100.",
        "Income tax refund. Collect $20.",
        "It is your birthday. Collect $10 from every player.",
        "Life insurance matures. Collect $100.",
        "Pay hospital fees of $100.",
        "Pay school fees of $50.",
        "Receive $25 consultancy fee.",
        "You are assessed for street repair. $40 per house, $115 per hotel.",
        "You have won second prize in a beauty contest. Collect $10.",
        "You inherit $100."
    ]
    random.shuffle(cards)
    return cards

# Roll dice
def roll_dice():
    die1 = random.randint(1, 6)
    die2 = random.randint(1, 6)
    return die1, die2

# Display the board (simplified)
def display_board(board, players):
    print("\n=== MONOPOLY BOARD ===")
    for i, space in enumerate(board):
        players_here = [p.name for p in players if p.position == i]
        players_str = ", ".join(players_here) if players_here else ""
        print(f"{i:2d}. {space['name']} {players_str}")
    print("=====================\n")

# Main game function
def play_monopoly():
    # Setup
    board = create_board()
    chance_cards = create_chance_cards()
    community_chest_cards = create_community_chest_cards()
    
    # Get number of players
    num_players = int(input("Enter number of players (2-8): "))
    while num_players < 2 or num_players > 8:
        num_players = int(input("Please enter a number between 2 and 8: "))
    
    # Create players
    players = []
    for i in range(num_players):
        name = input(f"Enter name for Player {i+1}: ")
        players.append(Player(name))
    
    # Game loop
    current_player_idx = 0
    game_over = False
    round_num = 1
    
    while not game_over:
        current_player = players[current_player_idx]
        
        print(f"\n=== Round {round_num}: {current_player.name}'s Turn ===")
        print(f"Money: ${current_player.money}")
        print(f"Current Position: {board[current_player.position]['name']}")
        
        # Handle jail
        if current_player.in_jail:
            print(f"{current_player.name} is in jail (Turn {current_player.jail_turns + 1}/3)")
            jail_choice = input("Options: (1) Pay $50, (2) Use Get Out of Jail Free card, (3) Roll for doubles: ")
            
            if jail_choice == "1" and current_player.money >= 50:
                current_player.money -= 50
                current_player.in_jail = False
                print(f"{current_player.name} paid $50 and is out of jail.")
            elif jail_choice == "2" and current_player.get_out_of_jail_cards > 0:
                current_player.get_out_of_jail_cards -= 1
                current_player.in_jail = False
                print(f"{current_player.name} used a Get Out of Jail Free card.")
            else:
                die1, die2 = roll_dice()
                print(f"{current_player.name} rolled {die1} and {die2}")
                
                if die1 == die2:
                    current_player.in_jail = False
                    print(f"{current_player.name} rolled doubles and is out of jail!")
                    current_player.move(die1 + die2)
                else:
                    current_player.jail_turns += 1
                    if current_player.jail_turns >= 3:
                        current_player.money -= 50
                        current_player.in_jail = False
                        current_player.jail_turns = 0
                        print(f"{current_player.name} paid $50 after 3 turns and is out of jail.")
                        current_player.move(die1 + die2)
                    else:
                        current_player_idx = (current_player_idx + 1) % num_players
                        continue
        else:
            # Roll dice and move
            input("Press Enter to roll dice...")
            die1, die2 = roll_dice()
            doubles = die1 == die2
            total = die1 + die2
            
            print(f"{current_player.name} rolled {die1} and {die2} (total: {total})")
            
            # Move player
            old_position = current_player.position
            new_position = current_player.move(total)
            
            # Check if passed GO
            if new_position < old_position and not (new_position == 30):  # Not Go To Jail
                current_player.money += 200
                print(f"{current_player.name} passed GO and collected $200!")
            
            # Handle landing on different spaces
            space = board[new_position]
            print(f"{current_player.name} landed on {space['name']}")
            
            if space["type"] == "property" or space["type"] == "railroad" or space["type"] == "utility":
                # Check if property is owned
                owner = next((p for p in players if any(prop.get("name") == space["name"] for prop in p.properties)), None)
                
                if owner is None:
                    # Property is available to buy
                    if current_player.money >= space["price"]:
                        buy_choice = input(f"Would you like to buy {space['name']} for ${space['price']}? (y/n): ")
                        if buy_choice.lower() == 'y':
                            current_player.money -= space["price"]
                            current_player.properties.append(space)
                            print(f"{current_player.name} bought {space['name']} for ${space['price']}")
                    else:
                        print(f"{current_player.name} doesn't have enough money to buy {space['name']}")
                elif owner != current_player:
                    # Pay rent
                    rent = space["rent"]
                    current_player.money -= rent
                    owner.money += rent
                    print(f"{current_player.name} paid ${rent} rent to {owner.name}")
            
            elif space["type"] == "tax":
                current_player.money -= space["amount"]
                print(f"{current_player.name} paid ${space['amount']} in taxes")
            
            elif space["type"] == "go_to_jail":
                current_player.position = 10  # Jail position
                current_player.in_jail = True
                print(f"{current_player.name} was sent to jail!")
            
            elif space["type"] == "card":
                card_type = space["card_type"]
                if card_type == CardType.CHANCE:
                    card = chance_cards.pop(0)
                    chance_cards.append(card)  # Put card at the bottom of the deck
                    print(f"Chance card: {card}")
                    # Handle card effects here
                elif card_type == CardType.COMMUNITY_CHEST:
                    card = community_chest_cards.pop(0)
                    community_chest_cards.append(card)  # Put card at the bottom of the deck
                    print(f"Community Chest card: {card}")
                    # Handle card effects here
        
        # Check if game should end
        if current_player.money < 0:
            print(f"{current_player.name} is bankrupt!")
            players.remove(current_player)
            
            if len(players) == 1:
                print(f"\n{players[0].name} wins the game!")
                game_over = True
                break
        
        # Next player's turn
        if not doubles or current_player.in_jail:
            current_player_idx = (current_player_idx + 1) % len(players)
            if current_player_idx == 0:
                round_num += 1
        else:
            print(f"{current_player.name} rolled doubles and gets another turn!")
        
        # Display the board after the move
        display_board(board, players)
        
        # Wait a bit before the next turn for readability
        time.sleep(1)

# Start the game
if __name__ == "__main__":
    print("Welcome to Monopoly!")
    play_monopoly()