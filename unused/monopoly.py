import random

class Player:
    """
    Represents a player in the Monopoly game.

    Attributes:
        name (str): The name of the player.
        money (int): The amount of money the player has.
        position (int): The current position of the player on the board (0-39).
        properties (list): A list of property names owned by the player.
        is_bankrupt (bool): Indicates if the player is bankrupt.
        in_jail (bool): Indicates if the player is in jail.
        jail_turns (int): Number of turns left in jail.
        get_out_of_jail_card (bool): Indicates if the player has a "Get Out of Jail Free" card.
    """
    def __init__(self, name, money=1500):
        """
        Initializes a Player object.

        Args:
            name (str): The name of the player.
            money (int, optional): The starting amount of money. Defaults to 1500.
        """
        self.name = name
        self.money = money
        self.position = 0
        self.properties = []
        self.is_bankrupt = False
        self.in_jail = False
        self.jail_turns = 0
        self.get_out_of_jail_card = False # Added for "Get Out of Jail Free" cards

    def move(self, spaces):
        """
        Moves the player's position on the board.  Handles passing Go.

        Args:
            spaces (int): The number of spaces to move.
        """
        old_position = self.position
        self.position = (self.position + spaces) % 40  # Wrap around the board
        if self.position < old_position and self.position != 0: # landed on go by going backwards.
            self.money += 200
            print(f"{self.name} passed Go and collected $200.")
        elif self.position == 0:
            self.money += 200
            print(f"{self.name} passed Go and collected $200.")

    def buy_property(self, property_name, price):
        """
        Buys a property if the player has enough money.

        Args:
            property_name (str): The name of the property to buy.
            price (int): The price of the property.

        Returns:
            bool: True if the property was bought, False otherwise.
        """
        if self.money >= price:
            self.money -= price
            self.properties.append(property_name)
            print(f"{self.name} bought {property_name} for ${price}.")
            return True
        else:
            print(f"{self.name} does not have enough money to buy {property_name}.")
            return False

    def pay_rent(self, amount, to_player=None):
        """
        Pays rent to another player or the bank.

        Args:
            amount (int): The amount of rent to pay.
            to_player (Player, optional): The player to pay rent to. Defaults to None (the bank).
        """
        if self.money >= amount:
            self.money -= amount
            if to_player:
                to_player.money += amount
                print(f"{self.name} paid ${amount} rent to {to_player.name} for {board[self.position]['name']}.")
            else:
                print(f"{self.name} paid ${amount} to the bank.")
        else:
            print(f"{self.name} does not have enough money to pay rent.")
            self.is_bankrupt = True
            print(f"{self.name} is bankrupt!")

    def receive_money(self, amount):
        """
        Receives money.

        Args:
            amount (int): The amount of money to receive.
        """
        self.money += amount
        print(f"{self.name} received ${amount}.")

    def go_to_jail(self):
        """
        Sends the player to jail.
        """
        self.in_jail = True
        self.jail_turns = 3
        self.position = 10  # Jail position
        print(f"{self.name} is sent to jail!")

    def get_out_of_jail(self, paid_bail=False):
        """
        Gets the player out of jail, either by paying bail or rolling doubles.

        Args:
            paid_bail (bool, optional): Indicates if the player paid bail. Defaults to False.
        """
        if self.in_jail:
            if self.get_out_of_jail_card: # Use the "Get Out of Jail Free" card
                self.in_jail = False
                self.jail_turns = 0
                self.get_out_of_jail_card = False
                print(f"{self.name} used a 'Get Out of Jail Free' card.")
                return

            if paid_bail:
                self.money -= 50
                self.in_jail = False
                self.jail_turns = 0
                print(f"{self.name} paid $50 bail and is out of jail.")
            else:
                roll1 = random.randint(1, 6)
                roll2 = random.randint(1, 6)
                print(f"{self.name} rolled {roll1} and {roll2} to get out of jail.")
                if roll1 == roll2:
                    self.in_jail = False
                    self.jail_turns = 0
                    print(f"{self.name} rolled doubles and is out of jail!")
                    self.move(roll1 + roll2)  # Move after getting out on doubles
                else:
                    self.jail_turns -= 1
                    if self.jail_turns == 0:
                        self.money -= 50
                        self.in_jail = False
                        self.jail_turns = 0
                        print(f"{self.name} paid $50 bail after 3 turns in jail.")
                        #move?
                    else:
                        print(f"{self.name} remains in jail for {self.jail_turns} more turns.")
        else:
            print(f"{self.name} is not in jail.")

    def morgade_property(self, property_name):
        """
        Morgade a property to the bank.

        Args:
            property_name (str): The name of the property to morgade.
        """
        if property_name in self.properties:
            self.properties.remove(property_name)
            print(f"{self.name} morgaded {property_name}.")
        else:
            print(f"{self.name} does not own {property_name}.")

    def __str__(self):
        """
        Returns a string representation of the player.
        """
        return f"{self.name} has ${self.money} and is on {board[self.position]['name']}."



def roll_dice():
    """
    Rolls two dice and returns the results.

    Returns:
        tuple: A tuple containing the results of the two dice rolls.
    """
    roll1 = random.randint(1, 6)
    roll2 = random.randint(1, 6)
    return roll1, roll2

def print_board(players, board):
    """Prints the current state of the game board and player positions.

       Args:
          players (list): A list of Player objects.
          board (list): A list of dictionaries representing the game board.
    """
    print("-" * 40)
    for space in board:
        print(f"{space['position']:2} - {space['name']:20}  ", end="")
        player_names = [p.name for p in players if p.position == space['position']]
        if player_names:
            print(f"Players: {', '.join(player_names)}")
        else:
            print()  # Just a newline
    print("-" * 40)
    for player in players:
        print(player)
    print("-" * 40)

def draw_card(deck, player, players):
    """
    Draws a card from the specified deck (Chance or Community Chest) and applies its effect.

    Args:
        deck (list): The deck to draw from (chance_deck or community_chest_deck).
        player (Player): The player drawing the card.
    """
    if not deck:
        print("The deck is empty.")
        return

    card = deck.pop(0)  # Draw the top card
    print(f"{player.name} drew: {card['text']}")

    if card['type'] == 'money':
        player.receive_money(card['amount'])
    elif card['type'] == 'move':
        if card['relative']:
            player.move(card['amount'])
        else:
            player.position = card['amount']
            print(f"{player.name} moved to {board[player.position]['name']}.")
    elif card['type'] == 'jail':
        player.go_to_jail()
    elif card['type'] == 'get_out_of_jail':
        player.get_out_of_jail_card = True # give the player the card.
    elif card['type'] == 'pay_each_player':
        for other_player in players:
            if other_player != player:
                if player.money >= card['amount']:
                    player.pay_rent(card['amount'], other_player)
                else:
                    print(f"{player.name} does not have enough money to pay each player.")
                    player.is_bankrupt = True
                    return
    elif card['type'] == 'receive_from_each_player':
        for other_player in players:
            if other_player != player:
                other_player.pay_rent(card['amount'], player) # force other players to pay.
    else:
        print(f"Unknown card type: {card['type']}")

def shuffle_deck(deck):
    """Shuffles the given deck of cards."""
    random.shuffle(deck)

# Initialize the game board
board = [
    {"position": 0, "name": "Go", "type": "go"},
    {"position": 1, "name": "Mediterranean Avenue", "type": "property", "price": 60, "rent": [2, 10, 30, 90, 160, 250], "owner": None},
    {"position": 2, "name": "Community Chest", "type": "community_chest"},
    {"position": 3, "name": "Baltic Avenue", "type": "property", "price": 60, "rent": [4, 20, 60, 180, 320, 450], "owner": None},
    {"position": 4, "name": "Income Tax", "type": "tax"},
    {"position": 5, "name": "Reading Railroad", "type": "property", "price": 200, "rent": [25, 50, 100, 200], "owner": None},
    {"position": 6, "name": "Oriental Avenue", "type": "property", "price": 100, "rent": [6, 30, 90, 270, 400, 550], "owner": None},
    {"position": 7, "name": "Chance", "type": "chance"},
    {"position": 8, "name": "Vermont Avenue", "type": "property", "price": 100, "rent": [6, 30, 90, 270, 400, 550], "owner": None},
    {"position": 9, "name": "Connecticut Avenue", "type": "property", "price": 120, "rent": [8, 40, 100, 300, 450, 600], "owner": None},
    {"position": 10, "name": "Jail", "type": "jail"},
    {"position": 11, "name": "St. Charles Place", "type": "property", "price": 140, "rent": [10, 50, 150, 450, 625, 750], "owner": None},
    {"position": 12, "name": "Electric Company", "type": "property", "price": 150, "rent": [4, 10], "owner": None},
    {"position": 13, "name": "States Avenue", "type": "property", "price": 140, "rent": [10, 50, 150, 450, 625, 750], "owner": None},
    {"position": 14, "name": "Virginia Avenue", "type": "property", "price": 160, "rent": [12, 60, 180, 500, 700, 900], "owner": None},
    {"position": 15, "name": "Pennsylvania Railroad", "type": "property", "price": 200, "rent": [25, 50, 100, 200], "owner": None},
    {"position": 16, "name": "St. James Place", "type": "property", "price": 180, "rent": [14, 70, 200, 550, 750, 950], "owner": None},
    {"position": 17, "name": "Community Chest", "type": "community_chest"},
    {"position": 18, "name": "Tennessee Avenue", "type": "property", "price": 180, "rent": [14, 70, 200, 550, 750, 950], "owner": None},
    {"position": 19, "name": "New York Avenue", "type": "property", "price": 200, "rent": [16, 80, 220, 600, 800, 1000], "owner": None},
    {"position": 20, "name": "Free Parking", "type": "free_parking"},
    {"position": 21, "name": "Kentucky Avenue", "type": "property", "price": 220, "rent": [18, 90, 250, 700, 875, 1050], "owner": None},
    {"position": 22, "name": "Chance", "type": "chance"},
    {"position": 23, "name": "Indiana Avenue", "type": "property", "price": 220, "rent": [18, 90, 250, 700, 875, 1050], "owner": None},
    {"position": 24, "name": "Illinois Avenue", "type": "property", "price": 240, "rent": [20, 100, 300, 750, 925, 1100], "owner": None},
    {"position": 25, "name": "B&O Railroad", "type": "property", "price": 200, "rent": [25, 50, 100, 200], "owner": None},
    {"position": 26, "name": "Atlantic Avenue", "type": "property", "price": 260, "rent": [22, 110, 330, 800, 975, 1150], "owner": None},
    {"position": 27, "name": "Ventnor Avenue", "type": "property", "price": 260, "rent": [22, 110, 330, 800, 975, 1150], "owner": None},
    {"position": 28, "name": "Water Works", "type": "property", "price": 150, "rent": [4, 10], "owner": None},
    {"position": 29, "name": "Marvin Gardens", "type": "property", "price": 280, "rent": [24, 120, 360, 850, 1025, 1200], "owner": None},
    {"position": 30, "name": "Go to Jail", "type": "go_to_jail"},
    {"position": 31, "name": "Pacific Avenue", "type": "property", "price": 300, "rent": [26, 130, 390, 900, 1100, 1275], "owner": None},
    {"position": 32, "name": "North Carolina Avenue", "type": "property", "price": 300, "rent": [26, 130, 390, 900, 1100, 1275], "owner": None},
    {"position": 33, "name": "Community Chest", "type": "community_chest"},
    {"position": 34, "name": "Pennsylvania Avenue", "type": "property", "price": 320, "rent": [28, 150, 450, 1000, 1200, 1400], "owner": None},
    {"position": 35, "name": "Short Line", "type": "property", "price": 200, "rent": [25, 50, 100, 200], "owner": None},
    {"position": 36, "name": "Chance", "type": "chance"},
    {"position": 37, "name": "Park Place", "type": "property", "price": 350, "rent": [35, 175, 500, 1100, 1300, 1500], "owner": None},
    {"position": 38, "name": "Luxury Tax", "type": "tax"},
    {"position": 39, "name": "Boardwalk", "type": "property", "price": 400, "rent": [50, 200, 600, 1400, 1700, 2000], "owner": None},
]

# Initialize the decks
community_chest_deck = [
    {"type": "move", "amount": 0, "relative": False, "text": "Advance to Go (Collect $200)"},
    {"type": "money", "amount": 200, "text": "Bank error in your favor. Collect $200"},
    {"type": "money", "amount": -50, "text": "Doctor's fee. Pay $50"},
    {"type": "money", "amount": 50, "text": "From sale of stock you get $50"},
    {"type": "get_out_of_jail", "text": "Get Out of Jail Free"},
    {"type": "jail", "text": "Go to Jail. Go directly to Jail. Do not pass Go, do not collect $200"},
    {"type": "money", "amount": 50, "text": "Holiday fund matures. Receive $50"},
    {"type": "money", "amount": 100, "text": "Income tax refund. Collect $100"},
    {"type": "money", "amount": 20, "text": "It's your birthday. Collect $20 from each player"},
    {"type": "money", "amount": 100, "text": "Life insurance matures. Collect $100"},
    {"type": "money", "amount": -50, "text": "Hospital fees. Pay $50"},
    {"type": "money", "amount": -50, "text": "School fees. Pay $50"},
    {"type": "money", "amount": 25, "text": "Receive $25 consultancy fee"},
    {"type": "money", "amount": 10, "text": "You have won second prize in a beauty contest. Collect $10"},
    {"type": "money", "amount": 100, "text": "You inherit $100"},
    {"type": "receive_from_each_player", "amount": 10, "text": "It's your birthday. Collect $10 from every player"}
]

chance_deck = [
    {"type": "move", "amount": 0, "relative": False, "text": "Advance to Go (Collect $200)"},
    {"type": "move", "amount": 24, "relative": False, "text": "Advance to Illinois Avenue. If you pass Go, collect $200"},
    {"type": "move", "amount": 11, "relative": False, "text": "Advance to St. Charles Place. If you pass Go, collect $200"},
    {"type": "move", "amount": 5, "relative": False, "text": "Advance to nearest Railroad. If unowned, you may buy it from the Bank"},
    {"type": "move", "amount": 39, "relative": False, "text": "Take a walk on the Boardwalk. Advance to Boardwalk"},
    {"type": "money", "amount": 50, "text": "Bank pays you dividend of $50"},
    {"type": "get_out_of_jail", "text": "Get Out of Jail Free"},
    {"type": "move", "amount": -3, "relative": True, "text": "Go back three spaces"},
    {"type": "jail", "text": "Go to Jail. Go directly to Jail. Do not pass Go, do not collect $200"},
    {"type": "money", "amount": -15, "text": "Pay poor tax of $15"},
    {"type": "move", "amount": 5, "relative": False, "text": "Take a trip to Reading Railroad. If you pass Go, collect $200"},
    {"type": "money", "amount": -50, "text": "You have been elected Chairman of the Board. Pay each player $50"},
    {"type": "money", "amount": 150, "text": "Your building loan matures. Collect $150"},
    {"type": "money", "amount": 100, "text": "You have won a crossword competition. Collect $100"},
    {"type": "money", "amount": -100, "text": "Pay hospital $100"},
    {"type": "money", "amount": -150, "text": "Pay school tax of $150"},
    {"type": "money", "amount": 50, "text": "Holiday fund matures. Receive $50"},
]

def init_players():
        # Initialize players
    num_players = int(input("Enter the number of players (2-4): "))
    while num_players < 2 or num_players > 8:
        print("Invalid number of players. Please enter a number between 2 and 8.")
        num_players = int(input("Enter the number of players (2-4): "))
    players = []
    for i in range(num_players):
        name = input(f"Enter the name for Player {i+1}: ")
        players.append(Player(name))
    return players, num_players


    
# Game loop
def handle_property_landing(player, space):
    if space["owner"] is None:
        if player.money >= space["price"]:
            action = input(f"Do you want to buy {space['name']} for ${space['price']}? (yes/no): ").lower()
            if action == "yes" or action == "y":
                player.buy_property(space["name"], space["price"])
                space["owner"] = player
            else:
                print(f"{player.name} chose not to buy {space['name']}.")
        else:
            print(f"{player.name} does not have enough money to buy {space['name']}.")
    elif space["owner"] != player:
        # Pay rent
        rent = space["rent"][0]  # Base rent. In a real game, this would vary.
        player.pay_rent(rent, space["owner"])

def handle_player_turn(player, board, players):
    if player.in_jail:
        print(f"{player.name} is in jail.")
        action = input(f"{player.name}, pay $50 bail or roll doubles? (pay/roll): ").lower()
        if action == "pay":
            player.get_out_of_jail(paid_bail=True)
        elif action == "roll":
            player.get_out_of_jail(paid_bail=False)
        else:
            print("Invalid action. You lose your turn.")
        return player.in_jail  # Return True if still in jail

    roll1, roll2 = roll_dice() 
    print(f"{player.name} rolled {roll1} and {roll2}.")
    player.move(roll1 + roll2)
    print(player)  # show player status
    
    # Handle landing on different types of spaces
    space = board[player.position]
    if space["type"] == "property":
        handle_property_landing(player, space)
    elif space["type"] == "tax":
        if space["name"] == "Income Tax":
            amount = min(200, int(0.1 * player.money))
            player.pay_rent(amount)
        elif space["name"] == "Luxury Tax":
            player.pay_rent(75)
    elif space["type"] == "go_to_jail":
        player.go_to_jail()
    elif space["type"] == "go":
        player.receive_money(200)
    elif space["type"] == "free_parking":
        print(f"{player.name} landed on Free Parking. Nothing happens.")
    elif space["type"] == "chance":
        draw_card(chance_deck, player, players)
    elif space["type"] == "community_chest":
        draw_card(community_chest_deck, player, players)
    elif space["type"] == "jail":
        print(f"{player.name} is visiting jail.")
    else:
        print(f"Landed on {space['name']}. Nothing happens.")
    
    return False  # Not in jail after turn

def main():
    # Shuffle the decks
    shuffle_deck(chance_deck)
    shuffle_deck(community_chest_deck)

    players, num_players = init_players()

    # Game loop
    turn = 0
    while True:
        print_board(players, board)
        
        # Check if only one player remains
        active_players = [p for p in players if not p.is_bankrupt]
        if len(active_players) == 1:
            print(f"{active_players[0].name} wins!")
            break
            
        current_player_index = turn % len(players)
        player = players[current_player_index]

        if player.is_bankrupt:
            players.pop(current_player_index)
            if len(players) == 1:
                print(f"{players[0].name} wins!")
                break
            continue  # Skip to next player without incrementing turn
        
        still_in_jail = handle_player_turn(player, board, players)
        if not still_in_jail:
            turn += 1

if __name__ == "__main__":
    main()
