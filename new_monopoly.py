import random
from enum import Enum
import time
import os
import numpy as np
from colorama import init, Fore, Back, Style
from game_models import Property, PropertyColor, PropertyStatus
from Bot import Bot, parameters
class Player:
    def __init__(self, name, token, is_bot=False, game=None):
        self.name = name
        self.token = token
        self.position = 0
        self.money = 1500
        self.properties = []
        self.jail_turns = 0
        self.jail_free_cards = 0
        self.bankrupt = False
        self.is_bot = is_bot
        self.bot = Bot(self, game=game, parameters=parameters)
    
    def move(self, steps, board_size=40):
        old_position = self.position
        self.position = (self.position + steps) % board_size
        # Check if player passed Go
        if self.position < old_position and steps > 0:
            return True  # Passed Go
        return False
    
    def go_to_jail(self):
        self.position = 10  # Jail position
        self.jail_turns = 3
    
    def pay(self, amount):
        if self.money >= amount:
            self.money -= amount
            return True
        return False
    
    def receive(self, amount):
        self.money += amount
        
    def own_property(self, property):
        self.properties.append(property)
        
    def display_status(self, board):
        colors = {
            'title': Fore.CYAN + Style.BRIGHT,
            'prompt': Fore.YELLOW,
            'info': Fore.WHITE,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'money': Fore.GREEN + Style.BRIGHT,
            'property': Fore.MAGENTA,
            'player': Fore.BLUE + Style.BRIGHT,
            'dice': Fore.CYAN,
            'rent': Fore.RED + Style.BRIGHT,
            'jail': Fore.WHITE + Back.BLACK,
            'reset': Style.RESET_ALL
        }
        
        print(f"\n{colors['player']}{self.name} ({self.token}):{colors['reset']}")
        
        # Display position with appropriate color based on space type
        space = board.spaces[self.position]
        if isinstance(space, Property):
            print(f"  {colors['info']}Position: {self.position} ({colors['property']}{space.name}{colors['reset']})")
        else:
            print(f"  {colors['info']}Position: {self.position} ({colors['info']}{space}{colors['reset']})")
        
        # Display money with money color
        print(f"  {colors['info']}Money: {colors['money']}${self.money}{colors['reset']}")
        
        # Display properties with appropriate formatting
        print(f"  {colors['info']}Properties: ", end="")
        if self.properties:
            property_list = []
            for p in self.properties:
                if p.status == PropertyStatus.MORTGAGED:
                    status = f" ({colors['warning']}Mortgaged{colors['reset']})"
                elif hasattr(p, 'houses') and p.houses > 0:
                    status = f" ({colors['success']}{p.houses} houses{colors['reset']})"
                elif hasattr(p, 'hotel') and p.hotel:
                    status = f" ({colors['success']}Hotel{colors['reset']})"
                else:
                    status = ""
                property_list.append(f"{colors['property']}{p.name}{status}")
            print(', '.join(property_list))
        else:
            print(f"{colors['info']}None")
        
        # Display jail status
        if self.jail_turns > 0:
            print(f"  {colors['jail']}In jail: {self.jail_turns} turns remaining{colors['reset']}")
class Board:
    def __init__(self):
        self.spaces = self.create_board()
        self.Chans_cards = self.create_Chans_cards()
        self.Almänning_cards = self.create_Almänning_cards()
        random.shuffle(self.Chans_cards)
        random.shuffle(self.Almänning_cards)
    
    def create_board(self):
        spaces = [None] * 40
        
        # Create properties
        # Brown properties
        spaces[1] = Property("Västerlånggatan", 1, 60, PropertyColor.BROWN, [2, 10, 30, 90, 160, 250], 30, 50)
        spaces[3] = Property("Hornsgatan", 3, 60, PropertyColor.BROWN, [4, 20, 60, 180, 320, 450], 30, 50)
        
        # Light Blue properties
        spaces[6] = Property("Folkungagatan", 6, 100, PropertyColor.LIGHT_BLUE, [6, 30, 90, 270, 400, 550], 50, 50)
        spaces[8] = Property("Götgatan", 8, 100, PropertyColor.LIGHT_BLUE, [6, 30, 90, 270, 400, 550], 50, 50)
        spaces[9] = Property("Ringvägen", 9, 120, PropertyColor.LIGHT_BLUE, [8, 40, 100, 300, 450, 600], 60, 50)
        
        # Pink properties
        spaces[11] = Property("St. Eriksgatan", 11, 140, PropertyColor.PINK, [10, 50, 150, 450, 625, 750], 70, 100)
        spaces[13] = Property("Odengatan", 13, 140, PropertyColor.PINK, [10, 50, 150, 450, 625, 750], 70, 100)
        spaces[14] = Property("Valhallavägen", 14, 160, PropertyColor.PINK, [12, 60, 180, 500, 700, 900], 80, 100)
        
        # Orange properties
        spaces[16] = Property("Sturegatan", 16, 180, PropertyColor.ORANGE, [14, 70, 200, 550, 750, 950], 90, 100)
        spaces[18] = Property("Klaravägen", 18, 180, PropertyColor.ORANGE, [14, 70, 200, 550, 750, 950], 90, 100)
        spaces[19] = Property("Narvravägen", 19, 200, PropertyColor.ORANGE, [16, 80, 220, 600, 800, 1000], 100, 100)
        
        # Red properties
        spaces[21] = Property("Strandvägen", 21, 220, PropertyColor.RED, [18, 90, 250, 700, 875, 1050], 110, 150)
        spaces[23] = Property("Kungsträdgårdsgatan", 23, 220, PropertyColor.RED, [18, 90, 250, 700, 875, 1050], 110, 150)
        spaces[24] = Property("Hamngatan", 24, 240, PropertyColor.RED, [20, 100, 300, 750, 925, 1100], 120, 150)
        
        # Yellow properties
        spaces[26] = Property("Vasagatan", 26, 260, PropertyColor.YELLOW, [22, 110, 330, 800, 975, 1150], 130, 150)
        spaces[27] = Property("Kungsgatan", 27, 260, PropertyColor.YELLOW, [22, 110, 330, 800, 975, 1150], 130, 150)
        spaces[29] = Property("Stureplan", 29, 280, PropertyColor.YELLOW, [24, 120, 360, 850, 1025, 1200], 140, 150)
        
        # Green properties
        spaces[31] = Property("Gustav Adolfs Torg", 31, 300, PropertyColor.GREEN, [26, 130, 390, 900, 1100, 1275], 150, 200)
        spaces[32] = Property("Drottninggatan", 32, 300, PropertyColor.GREEN, [26, 130, 390, 900, 1100, 1275], 150, 200)
        spaces[34] = Property("Diplomatstaden", 34, 320, PropertyColor.GREEN, [28, 150, 450, 1000, 1200, 1400], 160, 200)
        
        # Dark Blue properties
        spaces[37] = Property("Centrum", 37, 350, PropertyColor.DARK_BLUE, [35, 175, 500, 1100, 1300, 1500], 175, 200)
        spaces[39] = Property("Normalmstorg", 39, 400, PropertyColor.DARK_BLUE, [50, 200, 600, 1400, 1700, 2000], 200, 200)
        
        # Railroads
        spaces[5] = Property("Södra Station", 5, 200, PropertyColor.RAILROAD, [25, 50, 100, 200], 100)
        spaces[15] = Property("Östra station", 15, 200, PropertyColor.RAILROAD, [25, 50, 100, 200], 100)
        spaces[25] = Property("Centralstationen", 25, 200, PropertyColor.RAILROAD, [25, 50, 100, 200], 100)
        spaces[35] = Property("Norra Station", 35, 200, PropertyColor.RAILROAD, [25, 50, 100, 200], 100)
        
        # Utilities
        spaces[12] = Property("Elvärket", 12, 150, PropertyColor.UTILITY, [0], 75)
        spaces[28] = Property("Vattenverket", 28, 150, PropertyColor.UTILITY, [0], 75)
        
        # Non-property spaces (represented by strings)
        spaces[0] = "Gå"
        spaces[2] = "Almänning"
        spaces[4] = "Inkomstskatt"
        spaces[7] = "Chans"
        spaces[10] = "Fängelse / På besök"
        spaces[17] = "Almänning"
        spaces[20] = "Fri Parkering"
        spaces[22] = "Chans"
        spaces[30] = "Gå i fängelse"
        spaces[33] = "Almänning"
        spaces[36] = "Chans"
        spaces[38] = "Lyxskatt"
        
        return spaces
    
    def create_Chans_cards(self):
        return [
            "Advance to Go. (Collect $200)",
            "Advance to Illinois Avenue. If you pass Go, collect $200.",
            "Advance to St. Charles Place. If you pass Go, collect $200.",
            "Advance to nearest Utility. If unowned, you may buy it from the Bank. If owned, throw dice and pay owner a total 10 times the amount thrown.",
            "Advance to the nearest Railroad. If unowned, you may buy it from the Bank. If owned, pay owner twice the rental to which they are otherwise entitled.",
            "Bank pays you dividend of $50.",
            "Get Out of Jail Free.",
            "Go Back 3 Spaces.",
            "Go to Jail. Go directly to Jail, do not pass Go, do not collect $200.",
            "Make general repairs on all your property. For each house pay $25. For each hotel pay $100.",
            "Speeding fine $15.",
            "Take a trip to Reading Railroad. If you pass Go, collect $200.",
            "Take a walk on the Boardwalk. Advance to Boardwalk.",
            "You have been elected Chairman of the Board. Pay each player $50.",
            "Your building loan matures. Collect $150.",
            "You have won a crossword competition. Collect $100."
        ]
    
    def create_Almänning_cards(self):
        return [
            "Advance to Go. (Collect $200)",
            "Bank error in your favor. Collect $200.",
            "Doctor's fee. Pay $50.",
            "From sale of stock you get $50.",
            "Get Out of Jail Free.",
            "Go to Jail. Go directly to jail, do not pass Go, do not collect $200.",
            "Holiday fund matures. Receive $100.",
            "Income tax refund. Collect $20.",
            "It is your birthday. Collect $10 from each player.",
            "Life insurance matures. Collect $100.",
            "Pay hospital fees of $100.",
            "Pay school fees of $50.",
            "Receive $25 consultancy fee.",
            "You are assessed for street repairs. $40 per house. $115 per hotel.",
            "You have won second prize in a beauty contest. Collect $10.",
            "You inherit $100."
        ]
    
    def draw_Chans_card(self):
        card = self.Chans_cards.pop(0)
        self.Chans_cards.append(card)  # Put the card at the bottom of the deck
        return card
    
    def draw_Almänning_card(self):
        card = self.Almänning_cards.pop(0)
        self.Almänning_cards.append(card)  # Put the card at the bottom of the deck
        return card
    
    def get_property_at(self, position):
        if position < 0 or position >= len(self.spaces):
            return None
        return self.spaces[position]
    
    def display_board(self, players):
        # Create a simple text-based board representation
        board_repr = [
            "GÅ", "VÄ", "AL", "HO", "IS", "SÖ", "FO", "CH", "GÖ", "RI", "FÄ",
            "SE", "EL", "OG", "VA", "ÖS", "SG", "AL", "KA", "NA", "FP",
            "ST", "CH", "KT", "HA", "CS", "VA", "KU", "VV", "SP", "GTF",
            "GUT", "DR", "AL", "DI", "NO", "CH", "CE", "LX", "NO"
        ]
        
        # Define colors for different types of properties
        colors = {
            PropertyColor.BROWN: Fore.RED + Back.BLACK,
            PropertyColor.LIGHT_BLUE: Fore.CYAN,
            PropertyColor.PINK: Fore.MAGENTA,
            PropertyColor.ORANGE: Fore.YELLOW,
            PropertyColor.RED: Fore.RED,
            PropertyColor.YELLOW: Fore.YELLOW + Style.BRIGHT,
            PropertyColor.GREEN: Fore.GREEN,
            PropertyColor.DARK_BLUE: Fore.BLUE,
            PropertyColor.RAILROAD: Fore.WHITE + Back.BLACK,
            PropertyColor.UTILITY: Fore.WHITE + Back.BLUE,
            "special": Fore.WHITE + Back.MAGENTA,  # For special spaces like Chance, Community Chest
            "corner": Fore.GREEN + Back.BLACK,     # For corner spaces
            "tax": Fore.RED + Back.WHITE,          # For tax spaces
            "default": Fore.WHITE                  # Default color
        }
        
        # Create a visual board
        board_size = 11
        board = [[" " for _ in range(board_size)] for _ in range(board_size)]
        # Color mapping for each position
        color_map = {}
        
        # Set colors for each space type
        for i in range(40):
            space = self.spaces[i]
            if isinstance(space, Property):
                color_map[i] = colors[space.color]
            elif i in [0, 10, 20, 30]:  # Corner spaces
                color_map[i] = colors["corner"]
            elif i in [2, 17, 33]:  # Community chest
                color_map[i] = colors["special"]
            elif i in [7, 22, 36]:  # Chance
                color_map[i] = colors["special"]
            elif i in [4, 38]:  # Tax spaces
                color_map[i] = colors["tax"]
            else:
                color_map[i] = colors["default"]
        
        # Fill in the board with property abbreviations
        # Top row (0-10)
        for i in range(board_size):
            board[0][i] = board_repr[i]
        
        # Right column (11-19)
        for i in range(1, board_size - 1):
            board[i][board_size - 1] = board_repr[10 + i]
        
        # Bottom row (20-30), reversed
        for i in range(board_size):
            board[board_size - 1][board_size - 1 - i] = board_repr[20 + i]
        
        # Left column (31-39), reversed
        for i in range(1, board_size - 1):
            board[board_size - 1 - i][0] = board_repr[30 + i]
        
        # Place players on the board
        player_symbols = {}
        for player in players:
            if not player.bankrupt:
                position = player.position
                x, y = 0, 0
                
                if position <= 10:  # Top row
                    x, y = 0, position
                elif position <= 20:  # Right column
                    x, y = position - 10, board_size - 1
                elif position <= 30:  # Bottom row
                    x, y = board_size - 1, board_size - 1 - (position - 20)
                else:  # Left column
                    x, y = board_size - 1 - (position - 30), 0
                
                # Store player token at this position
                if (x, y) in player_symbols:
                    player_symbols[(x, y)].append(player.token)
                else:
                    player_symbols[(x, y)] = [player.token]
        
        # Print the board
        print("\n" + "=" * (board_size * 5 + 1))
        for i in range(board_size): # Rows
            row = "|"
            for j in range(board_size):
                cell = board[i][j]
                if cell == " ":
                    row += "    |"
                    continue
                    
                # Determine the position on the board
                position = 0
                if i == 0:  # Top row
                    position = j
                elif j == board_size - 1:  # Right column
                    position = 10 + i
                elif i == board_size - 1:  # Bottom row
                    position = 20 + (board_size - 1 - j)
                elif j == 0:  # Left column
                    position = 30 + (board_size - 1 - i)
                
                # Get the color for this position
                color_code = color_map.get(position, colors["default"])
                
                if (i, j) in player_symbols:
                    # Show player tokens if present
                    tokens = "".join(player_symbols[(i, j)])
                    row += f"{color_code}{tokens:4}{Style.RESET_ALL}|"
                else:
                    row += f"{color_code}{cell:4}{Style.RESET_ALL}|"

            print(row)
            print("-" * (board_size * 5 + 1))

class MonopolyGame:
    def __init__(self):
        #clear screan
        os.system('cls' if os.name == 'nt' else 'clear')
        
        # Initialize colorama for cross-platform color support
        init(autoreset=True)  # Automatically reset colors after each print
        
        self.colors = {
            'title': Fore.CYAN + Style.BRIGHT,
            'prompt': Fore.YELLOW,
            'info': Fore.WHITE,
            'success': Fore.GREEN,
            'warning': Fore.YELLOW,
            'error': Fore.RED,
            'money': Fore.GREEN + Style.BRIGHT,
            'property': Fore.MAGENTA,
            'player': Fore.BLUE + Style.BRIGHT,
            'dice': Fore.CYAN,
            'rent': Fore.RED + Style.BRIGHT,
            'jail': Fore.WHITE + Back.BLACK,
            'bot': Fore.YELLOW + Style.DIM,
            'reset': Style.RESET_ALL,
            'money': Fore.GREEN + Style.BRIGHT,
            'property': Fore.MAGENTA,
        }
        
        # Get player count with default value handling
        print(f"{self.colors['title']}=== MONOPOLY GAME SETUP ===")
        try:
            player_count_input = input(f"{self.colors['prompt']}Enter number of players (default 0): {self.colors['reset']}").strip()
            player_count = int(player_count_input) if player_count_input else 0
            
            # Get bot count with default value handling
            bot_count_input = input(f"{self.colors['prompt']}Enter number of bots (default 2): {self.colors['reset']}").strip()
            bot_count = int(bot_count_input) if bot_count_input else 2
        except ValueError:
            time.sleep(2)
            MonopolyGame()
        
        if bot_count + player_count < 2:
            print(f"{self.colors['error']}Not enough players to start the game.")
            time.sleep(2)
            MonopolyGame()
        
        self.board = Board()
        self.players = self.create_players(player_count, bot_count)
        self.current_player_idx = 0
        self.doubles_count = 0
        self.game_over = False
        
    def create_players(self, player_count, bot_count):
        tokens = ["🎩", "🚗", "🚢", "🐕", "👞", "🎲", "🐎", "⛲"]
        players = []
        for i in range(player_count):
            name = input(f"{self.colors['prompt']}Enter name for player {i + 1}: {self.colors['reset']}")
            token = tokens[i % len(tokens)] # Cycle through tokens if more than 8 players are playing
            players.append(Player(name, token))
        for i in range(bot_count):
            name = f"Bot {i + 1}"
            token = "🤖"
            player = Player(name, token, is_bot=True, game=self)
            players.append(player)
            print(f"{self.colors['bot']}Added AI player: {name} {token}")
            
        return players
    
    def roll_dice(self):
        return random.randint(1, 6), random.randint(1, 6)
    
    def next_player(self):
        # Find next non-bankrupt player
        self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        while self.players[self.current_player_idx].bankrupt:
            self.current_player_idx = (self.current_player_idx + 1) % len(self.players)
        
        # Reset doubles count
        self.doubles_count = 0
    
    def check_bankruptcy(self, player, amount_due, recipient=None):
        total_assets = player.money
        
        # Calculate total assets including property values
        for prop in player.properties:
            if prop.status != PropertyStatus.MORTGAGED:
                total_assets += prop.mortgage_value
            # Add value of houses and hotels (half of purchase price)
            if hasattr(prop, 'houses') and prop.houses > 0:
                total_assets += (prop.house_price // 2) * prop.houses
            elif hasattr(prop, 'hotel') and prop.hotel:
                total_assets += (prop.house_price // 2) * 5  # Hotel is worth 5 houses
        
        if total_assets < amount_due:
            print(f"\n{self.colors['error']}{player.name} is bankrupt!")
            player.bankrupt = True
            if input("display statistics? (y/n): ").lower() == 'y':
                    self.display_statistics()
            self.transfer_assets(player, recipient)
        else:
            if player.bot.decide_mortgage_property(amount_due): # Can the bot mortgage property?
                player.pay(amount_due)
                return True
            else:
                player.bankrupt = True
                print(f"\n{self.colors['error']}{player.name} is bankrupt!")
                if input("display statistics? (y/n): ").lower() == 'y':
                    self.display_statistics()
                self.transfer_assets(player, recipient)
        return False
        
    def transfer_assets(self, player, recipient):
        # Transfer remaining money and properties to recipient if any
        if recipient:
            recipient.receive(player.money)
            print(f"{self.colors['warning']}{player.name} transfers {self.colors['money']}${player.money} to {self.colors['player']}{recipient.name}.")
            for prop in player.properties:
                prop.owner = recipient
                recipient.properties.append(prop)
                print(f"{self.colors['property']}Property transferred: {prop.name}")
        player.money = 0
        player.properties = []
        
        # Check if game is over (only one player left)
        active_players = [p for p in self.players if not p.bankrupt]
        print(f"{self.colors['info']}Active players: {len(active_players)}")
        if len(active_players) == 1:
            self.game_over = True
            print(f"\n{self.colors['success']}{active_players[0].name} wins the game!")
    
    def handle_property_landing(self, player, property, dice_sum=None):
        if property.status == PropertyStatus.UNOWNED:
            self.offer_property_purchase(player, property)
        elif property.status == PropertyStatus.OWNED and property.owner != player:
            # Pay rent
            rent = property.calculate_rent(dice_sum)
            print(f"\n{self.colors['player']}{player.name} landed on {self.colors['property']}{property.name}, owned by {self.colors['player']}{property.owner.name}.")
            print(f"{self.colors['rent']}Rent due: ${rent}")
            
            if player.pay(rent):
                property.owner.receive(rent)
                print(f"{self.colors['player']}{player.name} pays {self.colors['rent']}${rent} to {self.colors['player']}{property.owner.name}.")
            else:
                print(f"{self.colors['error']}{player.name} doesn't have enough money to pay the rent!")
                
                self.check_bankruptcy(player, rent, property.owner)
                
    def offer_property_purchase(self, player, property):
        print(f"\n{self.colors['player']}{player.name} landed on {self.colors['property']}{property.name}.")
        print(f"{self.colors['money']}Price: ${property.price}")
        
        # check if player is bot
        
        if player.is_bot:
            choice = 'y' if player.bot.decide_buy_property(property) else 'n'
            print(f"{self.colors['bot']}Bot decision: {'Buy' if choice == 'y' else 'Auction'}")
        else:
            choice = input(f"{self.colors['prompt']}Would you like to buy {property.name} for ${property.price}? (y/n): {self.colors['reset']}").lower()
        
        if choice != 'n' and player.pay(property.price): # Player declined to buy the property 
            player.own_property(property)
            property.owner = player
            property.status = PropertyStatus.OWNED
            print(f"{self.colors['success']}{player.name} now owns {self.colors['property']}{property.name}!")
            
        else:
            print(f"{self.colors['warning']}{player.name} declined to buy the property.")
            # Start auction
            self.handel_auction(property)
    def handel_auction(self, property):
    
        print(f"\n{self.colors['title']}AUCTION for {self.colors['property']}{property.name} (Starting price: {self.colors['money']}$1)")
        
        # Players who can participate (not bankrupt and not the one who declined)
        eligible_bidders = [p for p in self.players if not p.bankrupt]
        
        current_bid = 1  # Start at half price
        highest_bidder = None
        
        # Continue auction until only one bidder remains
        active_bidders = eligible_bidders.copy()
        
        while len(active_bidders) > 0:
            for bidder in active_bidders.copy():
                print(f"\n{self.colors['info']}Current bid: {self.colors['money']}${current_bid}")
                print(f"{self.colors['player']}{bidder.name}'s turn (Money: {self.colors['money']}${bidder.money})")
                
                if bidder.is_bot:
                    choice = bidder.bot.decide_auction_bid(property, current_bid)
                    print(f"{self.colors['bot']}Bot bids: ${choice if choice > current_bid else 'PASS'}")
                else:
                    choice = input(f"{self.colors['prompt']}{bidder.name}, bid higher than ${current_bid}? Enter amount (0 to pass): ${self.colors['reset']}")
                
                try:
                    bid = int(choice)
                    if bid <= current_bid:
                        print(f"{self.colors['warning']}Bid must be higher than ${current_bid}!")
                        print(f"{self.colors['player']}{bidder.name} passes.")
                        active_bidders.remove(bidder)
                    elif bid > bidder.money:
                        print(f"{self.colors['error']}You don't have enough money for that bid!")
                        active_bidders.remove(bidder)
                    else:
                        current_bid = bid
                        highest_bidder = bidder
                        print(f"{self.colors['success']}{bidder.name} bids ${current_bid}!")
                except ValueError:
                    print(f"{self.colors['error']}Invalid input. You pass by default.")
                    active_bidders.remove(bidder)
            
            # If only one bidder left, they win
            if len(active_bidders) == 1:
                break
            
            # If no bidders left but someone bid before, the last bidder wins
            if len(active_bidders) == 0 and highest_bidder:
                break
        
        # Conclude the auction
        if highest_bidder:
            if highest_bidder.pay(current_bid):
                highest_bidder.own_property(property)
                property.owner = highest_bidder
                property.status = PropertyStatus.OWNED
                print(f"\n{self.colors['success']}{highest_bidder.name} won the auction for {self.colors['property']}{property.name} at {self.colors['money']}${current_bid}!")
            else:
                print(f"{self.colors['error']}{highest_bidder.name} couldn't pay for the property!")
        else:
            print(f"{self.colors['info']}No one bid on {self.colors['property']}{property.name}. Property remains unowned.")
    
    def handle_card(self, player, card_type):
        if card_type == "Chans":
            card = self.board.draw_Chans_card()
            print(f"\n{self.colors['title']}Chans card: {self.colors['info']}{card}")
        else:  # community chest
            card = self.board.draw_Almänning_card()
            print(f"\n{self.colors['title']}Community Chest card: {self.colors['info']}{card}")
        
        # Process card effects
        if "Advance to Go" in card:
            player.position = 0
            player.receive(200)
            print(f"{self.colors['success']}{player.name} advances to Go and collects {self.colors['money']}$200.")
        elif "Go to Jail" in card:
            player.go_to_jail()
            print(f"{self.colors['jail']}{player.name} goes to jail.")
        elif "Collect" in card or "Receive" in card or "get" in card or "matures" in card:
            # Extract amount
            amount = int(''.join(filter(str.isdigit, card)))
            player.receive(amount)
            print(f"{self.colors['success']}{player.name} receives {self.colors['money']}${amount}.")
        elif "Pay" in card or "fee" in card or "fine" in card:
            # Extract amount
            amount = int(''.join(filter(str.isdigit, card)))
            if player.pay(amount):
                print(f"{self.colors['warning']}{player.name} pays {self.colors['money']}${amount}.")
            else:
                print(f"{self.colors['error']}{player.name} doesn't have enough money!")
                self.check_bankruptcy(player, amount)
        elif "Get Out of Jail Free" in card:
            player.jail_free_cards += 1
            print(f"{self.colors['success']}{player.name} got a Get Out of Jail Free card.")
        # Additional card effects would be implemented here
    
    def handle_special_space(self, player, space_name):
        if space_name == "Go":
            # Already handled in move logic
            pass
        elif space_name == "Almänning":
            self.handle_card(player, "Almänning")
        elif space_name == "Inkomstskatt":
            tax = min(200, int(player.money * 0.1))  # Pay $200 or 10%, whichever is less
            if player.pay(tax):
                print(f"{self.colors['warning']}{player.name} pays {self.colors['money']}${tax} in Income Tax.")
            else:
                print(f"{self.colors['error']}{player.name} doesn't have enough money to pay Income Tax!")
                self.check_bankruptcy(player, tax)
        elif space_name == "Chans":
            self.handle_card(player, "C")
        elif space_name == "Jail / Just Visiting":
            print(f"{self.colors['info']}{player.name} is just visiting jail.")
        elif space_name == "Fri Parkering":
            print(f"{self.colors['info']}{player.name} landed on Fri Parkering.")
        elif space_name == "Gå i fängelse":
            player.go_to_jail()
            print(f"{self.colors['jail']}{player.name} goes to jail.")
        elif space_name == "Lyxskatt":
            if player.pay(100):
                print(f"{self.colors['warning']}{player.name} pays {self.colors['money']}$100 in Luxury Tax.")
            else:
                print(f"{self.colors['error']}{player.name} doesn't have enough money to pay Luxury Tax!")
                self.check_bankruptcy(player, 100)
    
    def handle_jail(self, player):
        if player.jail_turns > 0:
            print(f"\n{self.colors['jail']}{player.name} is in jail. {player.jail_turns} turns remaining.")
            
            # Options for getting out of jail
            
            if player.is_bot:
                choice = player.bot.decide_jail_strategy()
                print(f"{self.colors['bot']}Bot jail strategy: {choice}")
            else:
                choice = input(f"{self.colors['prompt']}What would you like to do?\n1. Roll for doubles\n2. Use Get Out of Jail Free card\n3. Pay $50\nEnter choice: {self.colors['reset']}")
            
            if choice == "2" and player.jail_free_cards > 0:
                player.jail_free_cards -= 1
                player.jail_turns = 0
                print(f"{self.colors['success']}{player.name} used a Get Out of Jail Free card.")
                return False  # Player can now roll and move
            elif choice == "3":
                if player.pay(50):
                    player.jail_turns = 0
                    print(f"{self.colors['success']}{player.name} paid {self.colors['money']}$50 to get out of jail.")
                    return False
            else:
                # Roll for doubles
                print(f"{self.colors['info']}{player.name} rolls to try for doubles...")
                die1, die2 = self.roll_dice()
                print(f"{self.colors['dice']}Rolled: {die1}, {die2}")
            
            if die1 == die2:
                player.jail_turns = 0
                print(f"{self.colors['success']}{player.name} rolled doubles and gets out of jail!")
                return False  # Player can now move using this roll
            else:
                player.jail_turns -= 1
                if player.jail_turns == 0:
                    player.pay(50)  # Pay fine after third turn
                    print(f"{self.colors['warning']}{player.name} paid {self.colors['money']}$50 after third turn in jail.")
                return True  # Player's turn ends
        
        return False  # Not in jail
    
    def property_management(self, player):
        
        if not player.properties:
            print(f"\n{self.colors['info']}You don't own any properties.")
            return
        
        print(f"\n{self.colors['title']}YOUR PROPERTIES:")
        for i, prop in enumerate(player.properties):
            status = "Mortgaged" if prop.status == PropertyStatus.MORTGAGED else "Owned"
            house_info = ""
            if hasattr(prop, 'houses') and prop.houses > 0:
                house_info = f", {prop.houses} houses"
            elif hasattr(prop, 'hotel') and prop.hotel:
                house_info = ", 1 hotel"
            print(f"{self.colors['property']}{i+1}. {prop.name} ({status}{house_info}) - Value: {self.colors['money']}${prop.price}")
        
        choice = input(f"\n{self.colors['prompt']}What would you like to do?\n1. Mortgage a property\n2. Unmortgage a property\n3. Buy houses/hotels\n4. Sell houses/hotels\n5. Trade Property\nEnter choice: {self.colors['reset']}")
        
        # Using a dictionary as a switch case
        actions = {
            "1": lambda: self.mortage_property(player),
            "2": lambda: self.unmortage_property(player),
            "3": lambda: self.buy_houses(player),
            "4": lambda: self.sell_houses(player),
            "5": lambda: self.trade_property(player) 
        }
        
        # Execute the selected action if it exists
        if choice in actions:
            actions[choice]()
    
    def trade_property(self, player):
    
        # Show all other non-bankrupt players
        available_players = [p for p in self.players if p != player and not p.bankrupt]
        
        if not available_players:
            print(f"{self.colors['info']}No players available to trade with.")
            return
        
        # Select player to trade with
        print(f"\n{self.colors['title']}SELECT A PLAYER TO TRADE WITH:")
        for i, p in enumerate(available_players):
            print(f"{self.colors['player']}{i+1}. {p.name}")
        
        player_idx = int(input(f"{self.colors['prompt']}Enter player number (or 0 to cancel): {self.colors['reset']}")) - 1
        if player_idx < 0 or player_idx >= len(available_players):
            return
        
        trade_partner = available_players[player_idx]
        
        # Show your properties
        if not player.properties:
            print(f"{self.colors['error']}You don't have any properties to offer.")
            return
        
        print(f"\n{self.colors['title']}YOUR PROPERTIES TO OFFER:")
        for i, prop in enumerate(player.properties):
            status = "Mortgaged" if prop.status == PropertyStatus.MORTGAGED else "Owned"
            print(f"{self.colors['property']}{i+1}. {prop.name} ({status}) - Value: {self.colors['money']}${prop.price}")
        
        # Select property to offer
        offer_idx = int(input(f"{self.colors['prompt']}Select property to offer (or 0 to cancel): {self.colors['reset']}")) - 1
        if offer_idx < 0 or offer_idx >= len(player.properties):
            return
        
        offer_property = player.properties[offer_idx]
        
        # Show partner's properties
        if not trade_partner.properties:
            print(f"{self.colors['error']}{trade_partner.name} doesn't have any properties to trade.")
            return
        
        print(f"\n{self.colors['title']}{trade_partner.name}'S PROPERTIES:")
        for i, prop in enumerate(trade_partner.properties):
            status = "Mortgaged" if prop.status == PropertyStatus.MORTGAGED else "Owned"
            print(f"{self.colors['property']}{i+1}. {prop.name} ({status}) - Value: {self.colors['money']}${prop.price}")
        
        # Select property to request
        request_idx = int(input(f"{self.colors['prompt']}Select property to request (or 0 to cancel): {self.colors['reset']}")) - 1
        if request_idx < 0 or request_idx >= len(trade_partner.properties):
            return
        
        request_property = trade_partner.properties[request_idx]
        
        # Ask for cash adjustment
        print(f"\n{self.colors['title']}CASH ADJUSTMENT:")
        cash_option = input(f"{self.colors['prompt']}1. You pay cash\n2. Request cash\n3. No cash involved\nEnter choice: {self.colors['reset']}")
        
        cash_amount = 0
        if cash_option == "1":
            cash_amount = int(input(f"{self.colors['prompt']}How much will you pay? (You have {self.colors['money']}${player.money}): ${self.colors['reset']}"))
            if cash_amount > player.money:
                print(f"{self.colors['error']}You don't have that much money.")
                return
        elif cash_option == "2":
            cash_amount = -int(input(f"{self.colors['prompt']}How much will you request? ({trade_partner.name} has {self.colors['money']}${trade_partner.money}): ${self.colors['reset']}"))
            if -cash_amount > trade_partner.money:
                print(f"{self.colors['error']}{trade_partner.name} doesn't have that much money.")
                return
        
        # If bot, automatically decide
        if trade_partner.is_bot:
            # Simple bot logic for deciding trades
            accept = trade_partner.bot.decide_trade(request_property, offer_property, -cash_amount)
            print(f"{self.colors['bot']}Bot evaluating trade offer...")
            
            if accept:
                # Execute the trade
                player.properties.remove(offer_property)
                trade_partner.properties.remove(request_property)
                
                player.properties.append(request_property)
                trade_partner.properties.append(offer_property)
                
                offer_property.owner = trade_partner
                request_property.owner = player
                
                if cash_amount > 0:
                    player.pay(cash_amount)
                    trade_partner.receive(cash_amount)
                elif cash_amount < 0:
                    trade_partner.pay(-cash_amount)
                    player.receive(-cash_amount)
                
                print(f"\n{self.colors['success']}Trade accepted! You traded {self.colors['property']}{offer_property.name} for {self.colors['property']}{request_property.name}.")
                if cash_amount != 0:
                    print(f"{self.colors['money']}{'You paid' if cash_amount > 0 else 'You received'} ${abs(cash_amount)}.")
            else:
                print(f"\n{self.colors['error']}{trade_partner.name} rejected your trade offer.")
        else:
            # Show trade summary to human player
            print(f"\n{self.colors['title']}TRADE OFFER TO {trade_partner.name}:")
            print(f"{self.colors['info']}You offer: {self.colors['property']}{offer_property.name}")
            print(f"{self.colors['info']}You request: {self.colors['property']}{request_property.name}")
            if cash_amount > 0:
                print(f"{self.colors['money']}You will pay: ${cash_amount}")
            elif cash_amount < 0:
                print(f"{self.colors['money']}You will receive: ${-cash_amount}")
            
            accept = input(f"\n{self.colors['prompt']}{trade_partner.name}, do you accept this trade? (y/n): {self.colors['reset']}").lower() == 'y'
            
            if accept:
                # Execute the trade
                player.properties.remove(offer_property)
                trade_partner.properties.remove(request_property)
                
                player.properties.append(request_property)
                trade_partner.properties.append(offer_property)
                
                offer_property.owner = trade_partner
                request_property.owner = player
                
                if cash_amount > 0:
                    player.pay(cash_amount)
                    trade_partner.receive(cash_amount)
                elif cash_amount < 0:
                    trade_partner.pay(-cash_amount)
                    player.receive(-cash_amount)
                
                print(f"\n{self.colors['success']}Trade completed successfully!")
            else:
                print(f"\n{self.colors['error']}Trade rejected.")

    def mortage_property(self, player):
        prop_idx = int(input(f"{self.colors['prompt']}Enter property number to mortgage: {self.colors['reset']}")) - 1
        if 0 <= prop_idx < len(player.properties):
            prop = player.properties[prop_idx]
            if prop.status != PropertyStatus.MORTGAGED and prop.houses == 0 and not prop.hotel:
                mortgage_value = prop.mortgage(player)
                player.receive(mortgage_value)
                print(f"{self.colors['success']}Mortgaged {self.colors['property']}{prop.name} for {self.colors['money']}${mortgage_value}.")
            else:
                print(f"{self.colors['error']}Cannot mortgage this property. Sell houses first or it's already mortgaged.")
        else:
            print(f"{self.colors['error']}Invalid property number.")
    
    def unmortage_property(self, player):
        prop_idx = int(input(f"{self.colors['prompt']}Enter property number to unmortgage: {self.colors['reset']}")) - 1
        if 0 <= prop_idx < len(player.properties):
            prop = player.properties[prop_idx]
            if prop.status == PropertyStatus.MORTGAGED:
                unmortgage_cost = prop.unmortgage()
                if player.pay(unmortgage_cost):
                    print(f"{self.colors['success']}Unmortgaged {self.colors['property']}{prop.name} for {self.colors['money']}${unmortgage_cost}.")
                else:
                    print(f"{self.colors['error']}Not enough money to unmortgage this property.")
                    prop.status = PropertyStatus.MORTGAGED  # Revert back if can't pay
            else:
                print(f"{self.colors['error']}This property is not mortgaged.")
        else:
            print(f"{self.colors['error']}Invalid property number.")
    
    def buy_houses(self, player):
        # Group properties by color
        properties_by_color = {}
        for prop in player.properties:
            if prop.color not in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
                if prop.color not in properties_by_color:
                    properties_by_color[prop.color] = []
                properties_by_color[prop.color].append(prop)
        
        # Find color groups where player owns all properties
        complete_sets = {}
        for color, props in properties_by_color.items():
            color_count = sum(1 for p in self.board.spaces if isinstance(p, Property) and p.color == color)
            if len(props) == color_count:
                complete_sets[color] = props
        
        if not complete_sets:
            print(f"{self.colors['error']}You don't have any complete property sets to build on.")
            return
        
        print(f"\n{self.colors['title']}YOU CAN BUILD ON THESE PROPERTY SETS:")
        for i, (color, props) in enumerate(complete_sets.items()):
            print(f"{self.colors['property']}{i+1}. {color.value}")
        
        set_idx = int(input(f"{self.colors['prompt']}Choose a set to build on (or 0 to cancel): {self.colors['reset']}")) - 1
        if set_idx == -1:
            return
        if 0 <= set_idx < len(complete_sets):
            chosen_color = list(complete_sets.keys())[set_idx]
            props = complete_sets[chosen_color]
            

            
            while True:
                
                # Display properties in the set
                print(f"\n{self.colors['title']}PROPERTIES IN {chosen_color.value} SET:")
                for i, prop in enumerate(props):
                    house_info = f"{prop.houses} houses" if prop.houses > 0 else "no houses"
                    hotel_info = ", has hotel" if prop.hotel else ""
                    print(f"{self.colors['property']}{i+1}. {prop.name} - {house_info}{hotel_info}, house cost: {self.colors['money']}${prop.house_price}")
                
                try:
                    prop_idx = int(input(f"{self.colors['prompt']}Choose a property to build on (or 0 to cancel): {self.colors['reset']}")) - 1
                except ValueError:
                    print(f"{self.colors['error']}Invalid input. Please enter a number.")
                    continue
                
                if prop_idx == -1: # Cancel if 0
                    return
                if 0 <= prop_idx < len(props):
                    prop = props[prop_idx]
                    
                    # Check if player can build evenly (difference between houses should be at most 1)
                    min_houses = min(p.houses for p in props)
                    if prop.houses > min_houses and not all(p.houses == min_houses for p in props if p != prop):
                        print(f"{self.colors['error']}You must build evenly. Build on properties with fewer houses first.")
                    
                    # Check if property already has a hotel
                    if prop.hotel:
                        print(f"{self.colors['error']}This property already has a hotel. No more buildings possible.")
                    
                    # Determine if buying a house or hotel
                    if prop.houses == 4:
                        # Buy a hotel
                        if player.pay(prop.house_price):
                            if prop.add_house_or_hotel():
                                print(f"{self.colors['success']}Added a hotel to {self.colors['property']}{prop.name}!")
                            else:
                                player.receive(prop.house_price)  # Refund if hotel couldn't be added
                                print(f"{self.colors['error']}Could not add a hotel to this property.")
                        else:
                            print(f"{self.colors['error']}Not enough money to buy a hotel ({self.colors['money']}${prop.house_price}).")
                    else:
                        # Buy a house
                        if player.pay(prop.house_price):
                            if prop.add_house_or_hotel():
                                print(f"{self.colors['success']}Added a house to {self.colors['property']}{prop.name}!")
                            else:
                                player.receive(prop.house_price)  # Refund if house couldn't be added
                                print(f"{self.colors['error']}Could not add a house to this property.")
                        else:
                            print(f"{self.colors['error']}Not enough money to buy a house ({self.colors['money']}${prop.house_price}).")
                else:
                    print(f"{self.colors['error']}Invalid property number.")
        else:
            print(f"{self.colors['error']}Invalid set number.")
    
    def build_house_bot(self, player):
        ''' build house for bot '''
        property = player.bot.decide_house_purchases()
        if property and type:
            if property and type:
                cost = property.house_price
                if player.pay(cost):
                        print(f"{self.colors['success']}Bot added a house/hotel to {self.colors['property']}{property.name}!")
                        property.add_house_or_hotel()
                    # Check if property already has a hotel
                else:
                    print(f"{self.colors['bot']}Not enough money to buy a {type} ({self.colors['money']}${cost}).")
    
    def sell_houses(self, player):
        # Find properties with houses or hotels
        props_with_buildings = [p for p in player.properties if p.houses > 0 or p.hotel]
        
        if not props_with_buildings:
            print(f"{self.colors['info']}You don't have any properties with houses or hotels.")
            return
        
        print(f"\n{self.colors['title']}YOUR PROPERTIES WITH BUILDINGS:")
        for i, prop in enumerate(props_with_buildings):
            if prop.hotel:
                print(f"{self.colors['property']}{i+1}. {prop.name} - Hotel (sell value: {self.colors['money']}${prop.house_price // 2})")
            else:
                print(f"{self.colors['property']}{i+1}. {prop.name} - {prop.houses} houses (sell value: {self.colors['money']}${prop.house_price // 2} each)")
        
        prop_idx = int(input(f"{self.colors['prompt']}Choose a property to sell buildings from (or 0 to cancel): {self.colors['reset']}")) - 1
        if prop_idx == -1:
            return
        if 0 <= prop_idx < len(props_with_buildings):
            prop = props_with_buildings[prop_idx]
            
            # Find all properties in same color group
            same_color_props = [p for p in player.properties if p.color == prop.color]
            
            # Check if selling would create uneven distribution (difference > 1)
            if prop.hotel:
                sell_hotel = input(f"{self.colors['prompt']}Sell hotel? (y/n): {self.colors['reset']}").lower() == 'y'
                if sell_hotel:
                    if prop.remove_hotel():
                        player.receive(prop.house_price // 2)
                        print(f"{self.colors['success']}Sold hotel from {self.colors['property']}{prop.name} for {self.colors['money']}${prop.house_price // 2}.")
                    else:
                        print(f"{self.colors['error']}Could not sell hotel.")
            else:
                num_to_sell = int(input(f"{self.colors['prompt']}How many houses to sell (1-{prop.houses})? {self.colors['reset']}"))
                if 1 <= num_to_sell <= prop.houses:
                    # Check if selling would violate even build rule
                    max_houses = max(p.houses for p in same_color_props)
                    if prop.houses == max_houses or prop.houses - num_to_sell >= max_houses - 1:
                        for _ in range(num_to_sell):
                            if prop.remove_house():
                                player.receive(prop.house_price // 2)
                        print(f"{self.colors['success']}Sold {num_to_sell} houses from {self.colors['property']}{prop.name} for {self.colors['money']}${(prop.house_price // 2) * num_to_sell}.")
                    else:
                        print(f"{self.colors['error']}Cannot create uneven building distribution. Sell houses from other properties first.")
                else:
                    print(f"{self.colors['error']}Invalid number of houses.")
        else:
            print(f"{self.colors['error']}Invalid property number.")
    
    def play_turn(self):
        player = self.players[self.current_player_idx]
        os.system('cls' if os.name == 'nt' else 'clear')
        
        if player.bankrupt:
            self.next_player()
            return
        
        print(f"\n{self.colors['title']}===== {player.name}'S TURN =====")
        self.board.display_board(self.players)
        player.display_status(self.board)
        
        # Check if player is in jail
        in_jail = self.handle_jail(player)
        if in_jail:
            self.next_player()
            return
        
        # Player's turn menu
        while not player.is_bot:
            print(f"\n{self.colors['title']}TURN OPTIONS:")
            print(f"{self.colors['prompt']}1. Roll dice")
            print(f"{self.colors['prompt']}2. Manage properties")
            print(f"{self.colors['prompt']}3. Show all properties")
            choice = input(f"{self.colors['prompt']}Enter choice (1-3): {self.colors['reset']}")
            
            if choice == "2":
                self.property_management(player)
            elif choice == "3":
                self.display_all_properties()
                continue
            else:
                break

        # Roll dice and move
        die1, die2 = self.roll_dice()
        dice_sum = die1 + die2
        
        print(f"\n{self.colors['player']}{player.name} rolls: {self.colors['dice']}{die1}, {die2} (Total: {dice_sum})")
        
        '''is_doubles = die1 == die2
        
        if is_doubles:
            self.doubles_count += 1
            print("Doubles!")
            
            if self.doubles_count == 3:
                print("Third doubles in a row! Going to jail.")
                player.go_to_jail()
                self.doubles_count = 0
                self.next_player()
                return
        '''
        
        # Move player
        passed_go = player.move(dice_sum)
        if passed_go:
            player.receive(200)
            print(f"{self.colors['success']}{player.name} passed GO and collected {self.colors['money']}$200.")
        
        # Handle landing on space
        space = self.board.get_property_at(player.position)
        print(f"{self.colors['player']}{player.name} landed on {self.colors['property' if isinstance(space, Property) else 'info']}{space.name if isinstance(space, Property) else space}")
        
        if isinstance(space, Property):
            self.handle_property_landing(player, space, dice_sum)
        else:
            self.handle_special_space(player, space)
        
        # Check if game is over due to bankruptcy
        if self.game_over:
            return
        
        # If doubles, player goes again unless they went to jail
        '''if is_doubles and player.jail_turns == 0:
            print(f"{player.name} rolled doubles and goes again!")
        else:
            self.next_player() '''
        
        if not player.is_bot:
            input(f"{self.colors['prompt']}Press Enter to continue...{self.colors['reset']}")
        else:
            print(f"{self.colors['bot']}{player.name} is thinking about their next move...")
            player.bot.make_move()
        self.next_player()
    
    def display_all_properties(self):
        print(f"\n{self.colors['title']}ALL PROPERTIES ON THE BOARD:")
        for space in self.board.spaces:
            if isinstance(space, Property):
                if space.owner:
                    status = f"Owned by {self.colors['player']}{space.owner.name}"
                    if space.status == PropertyStatus.MORTGAGED:
                        status += f" ({self.colors['warning']}Mortgaged{self.colors['reset']})"
                    elif hasattr(space, 'houses') and space.houses > 0:
                        status += f" ({space.houses} houses)"
                    elif hasattr(space, 'hotel') and space.hotel:
                        status += f" ({self.colors['success']}hotel{self.colors['reset']})"
                else:
                    status = f"{self.colors['info']}Unowned"
                print(f"{self.colors['property']}{space.name} - {self.colors['money']}${space.price} - {status}")
   
    def decide_winner(self):
        print(f"\n{self.colors['warning']}=== GAME REACHED 500 TURNS LIMIT ===")
                
        # Find the player with the most money
        active_players = [p for p in self.players if not p.bankrupt]
        if active_players:
            winner = max(active_players, key=lambda p: p.money)
            
            # Calculate total value (money + properties)
            player_values = {}
            for p in active_players:
                total_value = p.money
                for prop in p.properties:
                    total_value += prop.price
                    if hasattr(prop, 'houses') and prop.houses > 0:
                        total_value += prop.house_price * prop.houses
                    if hasattr(prop, 'hotel') and prop.hotel:
                        total_value += prop.house_price * 5
                player_values[p.name] = total_value
            
            print(f"\n{self.colors['title']}=== FINAL STANDINGS ===")
            for name, value in sorted(player_values.items(), key=lambda x: x[1], reverse=True):
                print(f"{self.colors['player']}{name}: {self.colors['money']}${value}")
            
            print(f"\n{self.colors['success']}{winner.name} WINS THE GAME WITH {self.colors['money']}${winner.money}!")
            self.game_over = True
            return
    
    def play_game(self):
        print(f"\n{self.colors['title']}Welcome to Monopoly!")
        
        turns = 0
    
        while not self.game_over:
            
            self.play_turn()
            
            if turns >= 500:
                self.decide_winner()
            
            if turns % 100 == 0 and turns != 0:
                if input(f"{self.colors['prompt']}Display statistics? (y/n): {self.colors['reset']}").lower() == 'y':
                    self.display_statistics() # Display statistics if player chooses to
            turns += 1
            #time.sleep(1)  # Small pause between turns
        if input(f"{self.colors['prompt']}Display statistics? (y/n): {self.colors['reset']}").lower() == 'y':
            self.display_statistics()
        
    def display_statistics(self):
        # Display a comprehensive property and building report
        print(f"\n{self.colors['title']}=== PROPERTY AND BUILDING REPORT ===")
        active_players = [p for p in self.players if not p.bankrupt]

        # Count total houses and hotels on the board
        total_houses = 0
        total_hotels = 0
        for space in self.board.spaces:
            if isinstance(space, Property):
                if hasattr(space, 'houses') and space.houses > 0:
                    total_houses += space.houses
                if hasattr(space, 'hotel') and space.hotel:
                    total_hotels += 1

        print(f"{self.colors['info']}Total buildings on board: {self.colors['success']}{total_houses} houses, {total_hotels} hotels")

        # Display all properties grouped by color
        color_groups = {}
        for space in self.board.spaces:
            if isinstance(space, Property):
                if space.color not in color_groups:
                    color_groups[space.color] = []
                color_groups[space.color].append(space)

        # Print properties by color group
        for color, properties in color_groups.items():
            print(f"\n{self.colors['title']}{color.value} Properties:")
            for prop in properties:
                owner_info = f"Owned by {self.colors['player']}{prop.owner.name}" if prop.owner else f"{self.colors['info']}Unowned"
                status_info = f" ({self.colors['warning']}Mortgaged{self.colors['reset']})" if prop.status == PropertyStatus.MORTGAGED else ""
                
                building_info = ""
                if hasattr(prop, 'houses') and prop.houses > 0:
                    building_info = f", {prop.houses} houses"
                if hasattr(prop, 'hotel') and prop.hotel:
                    building_info = f", {self.colors['success']}Hotel"
                    
                rent_info = f", Current rent: {self.colors['rent']}${prop.calculate_rent()}" if prop.owner else ""
                print(f"{self.colors['property']}  {prop.name} - {self.colors['money']}${prop.price} - {owner_info}{status_info}{building_info}{rent_info}")

        # Print player property summaries
        print(f"\n{self.colors['title']}Player Property Summaries:")
        for player in active_players:
            property_count = len(player.properties)
            house_count = sum(p.houses for p in player.properties if hasattr(p, 'houses'))
            hotel_count = sum(1 for p in player.properties if hasattr(p, 'hotel') and p.hotel)
            mortgaged_count = sum(1 for p in player.properties if p.status == PropertyStatus.MORTGAGED)
            
            print(f"{self.colors['player']}{player.name}: {property_count} properties, {house_count} houses, {hotel_count} hotels, {mortgaged_count} mortgaged, {self.colors['money']}${player.money}")

        #display all bankrupt players
        bankrupt_players = [p for p in self.players if p.bankrupt]
        if bankrupt_players:
            print(f"\n{self.colors['title']}=== BANKRUPT PLAYERS ===")
            for player in bankrupt_players:
                print(f"{self.colors['error']}{player.name} is bankrupt.")
                
        if input(f"{self.colors['prompt']}Display extended statistics? (y/n): {self.colors['reset']}").lower() == 'y':
            self.display_extended_statistics()
                
    def display_extended_statistics(self):
        """Display more comprehensive game statistics."""
        active_players = [p for p in self.players if not p.bankrupt]
        bankrupt_players = [p for p in self.players if p.bankrupt]
        
        print(f"\n{self.colors['title']}=== EXTENDED GAME STATISTICS ===\n")
        
        # Player Rankings by Net Worth
        print(f"{self.colors['title']}PLAYER RANKINGS BY NET WORTH:")
        player_values = {}
        for p in self.players:
            total_value = p.money
            for prop in p.properties:
                total_value += prop.price
                if hasattr(prop, 'houses') and prop.houses > 0:
                    total_value += prop.house_price * prop.houses
                if hasattr(prop, 'hotel') and prop.hotel:
                    total_value += prop.house_price * 5
                if prop.status == PropertyStatus.MORTGAGED:
                    total_value -= prop.mortgage_value * 0.1  # Unmortgaging cost
            player_values[p.name] = total_value
        
        # Sort players by net worth and display ranking
        for i, (name, value) in enumerate(sorted(player_values.items(), key=lambda x: x[1], reverse=True)):
            status = f"{self.colors['success']}ACTIVE" if next((p for p in active_players if p.name == name), None) else f"{self.colors['error']}BANKRUPT"
            print(f"{i+1}. {self.colors['player']}{name}: {self.colors['money']}${value:.2f} ({status}{self.colors['reset']})")
        
        # Property Statistics
        print(f"\n{self.colors['title']}PROPERTY STATISTICS:")
        property_stats = {
            "total": 0,
            "owned": 0,
            "unowned": 0,
            "mortgaged": 0,
            "developed": 0,
            "houses": 0,
            "hotels": 0
        }
        
        # Most valuable property
        most_valuable_prop = None
        highest_rent = 0
        
        # Most developed color group
        color_development = {}
        
        for space in self.board.spaces:
            if isinstance(space, Property):
                property_stats["total"] += 1
                
                if space.owner:
                    property_stats["owned"] += 1
                    if space.status == PropertyStatus.MORTGAGED:
                        property_stats["mortgaged"] += 1
                    
                    # Track houses/hotels
                    if hasattr(space, 'houses') and space.houses > 0:
                        property_stats["developed"] += 1
                        property_stats["houses"] += space.houses
                    if hasattr(space, 'hotel') and space.hotel:
                        property_stats["developed"] += 1
                        property_stats["hotels"] += 1
                    
                    # Track rent values
                    current_rent = space.calculate_rent()
                    if current_rent > highest_rent:
                        highest_rent = current_rent
                        most_valuable_prop = space
                    
                    # Track color group development
                    if space.color not in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
                        if space.color not in color_development:
                            color_development[space.color] = {"houses": 0, "hotels": 0, "properties": 0}
                        color_development[space.color]["properties"] += 1
                        if hasattr(space, 'houses'):
                            color_development[space.color]["houses"] += space.houses
                        if hasattr(space, 'hotel') and space.hotel:
                            color_development[space.color]["hotels"] += 1
                else:
                    property_stats["unowned"] += 1
        
        print(f"{self.colors['info']}Total Properties: {property_stats['total']}")
        print(f"{self.colors['info']}Owned: {self.colors['success']}{property_stats['owned']} ({property_stats['owned']/property_stats['total']*100:.1f}%)")
        print(f"{self.colors['info']}Unowned: {self.colors['warning']}{property_stats['unowned']}")
        print(f"{self.colors['info']}Mortgaged: {self.colors['warning']}{property_stats['mortgaged']} ({property_stats['mortgaged']/property_stats['owned']*100:.1f}% of owned)")
        print(f"{self.colors['info']}Properties with Houses/Hotels: {self.colors['success']}{property_stats['developed']}")
        print(f"{self.colors['info']}Total Houses on Board: {self.colors['success']}{property_stats['houses']}")
        print(f"{self.colors['info']}Total Hotels on Board: {self.colors['success']}{property_stats['hotels']}")
        
        if most_valuable_prop:
            owner_name = most_valuable_prop.owner.name if most_valuable_prop.owner else "None"
            print(f"\n{self.colors['info']}Most Valuable Property: {self.colors['property']}{most_valuable_prop.name} (Owned by: {self.colors['player']}{owner_name})")
            print(f"{self.colors['info']}Current Rent: {self.colors['rent']}${highest_rent}")
        
        # Most developed color group
        if color_development:
            most_dev_color = max(color_development.items(), 
                                key=lambda x: x[1]["houses"] + x[1]["hotels"]*5)
            print(f"\n{self.colors['info']}Most Developed Color Group: {self.colors['property']}{most_dev_color[0].value}")
            print(f"{self.colors['info']}Development: {self.colors['success']}{most_dev_color[1]['houses']} houses, {most_dev_color[1]['hotels']} hotels")
        
        # Monopoly statistics
        print(f"\n{self.colors['title']}MONOPOLY STATISTICS:")
        monopolies = {}
        for player in active_players:
            player_monopolies = []
            for color in set(p.color for p in player.properties if p.color not in [PropertyColor.RAILROAD, PropertyColor.UTILITY]):
                owned_props = [p for p in player.properties if p.color == color]
                total_in_color = sum(1 for p in self.board.spaces if isinstance(p, Property) and p.color == color)
                if len(owned_props) == total_in_color:
                    player_monopolies.append(color.value)
            
            if player_monopolies:
                monopolies[player.name] = player_monopolies
        
        if monopolies:
            for player_name, colors in monopolies.items():
                print(f"{self.colors['player']}{player_name} has monopoly on: {self.colors['property']}{', '.join(colors)}")
        else:
            print(f"{self.colors['info']}No player has a monopoly on any color group.")
        
        # Special category ownership
        print(f"\n{self.colors['title']}SPECIAL CATEGORY OWNERSHIP:")
        for category in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
            for player in active_players:
                count = sum(1 for p in player.properties if p.color == category)
                if count > 0:
                    print(f"{self.colors['player']}{player.name} owns {self.colors['success']}{count} {self.colors['property']}{category.value}s")
        
        # Money distribution
        if active_players:
            print(f"\n{self.colors['title']}MONEY DISTRIBUTION:")
            total_money = sum(p.money for p in self.players)
            for player in self.players:
                status = f"{self.colors['success']}Active" if not player.bankrupt else f"{self.colors['error']}Bankrupt"
                percentage = (player.money / total_money * 100) if total_money > 0 else 0
                print(f"{self.colors['player']}{player.name}: {self.colors['money']}${player.money} ({percentage:.1f}% of total) - {status}")
        input(f"{self.colors['prompt']}Press Enter to continue...{self.colors['reset']}")



# Run the game
if __name__ == "__main__":
    try:
        game = MonopolyGame()
        game.play_game()
    except KeyboardInterrupt:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\nGame cancelled by user.")
        print("Monopoly game ended. Thank you for playing!")
        #print the stats for everyone
