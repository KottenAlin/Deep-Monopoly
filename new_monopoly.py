import random
from enum import Enum
import time
import os
import torch
import numpy as np
import torch.nn as nn
import torch.optim as optim 

class PropertyColor(Enum):
    BROWN = "Brown"
    LIGHT_BLUE = "Light Blue"
    PINK = "Pink"
    ORANGE = "Orange"
    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"
    DARK_BLUE = "Dark Blue"
    RAILROAD = "Railroad"
    UTILITY = "Utility"
class PropertyStatus(Enum):
    UNOWNED = "Unowned"
    OWNED = "Owned"
    MORTGAGED = "Mortgaged"
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
        self.bot = Bot(self, game=game)
    
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
        print(f"\n{self.name} ({self.token}):")
        print(f"  Position: {self.position} ({board.spaces[self.position].name if isinstance(board.spaces[self.position], Property) else board.spaces[self.position]})")
        print(f"  Money: ${self.money}")
        print(f"  Properties: ", end="")
        if self.properties:
            property_list = []
            for p in self.properties:
                status = " (Mortgaged)" if p.status == PropertyStatus.MORTGAGED else '(' + str(p.houses) + ')'
                property_list.append(f"{p.name}{status}")
            print(', '.join(property_list))
        else:
            print("None")
        if self.jail_turns > 0:
            print(f"  In jail: {self.jail_turns} turns remaining")
class Property:
    def __init__(self, name, position, price, color, rents, mortgage_value, house_price=0):
        self.name = name
        self.position = position
        self.price = price
        self.color = color
        self.rents = rents  # List of rents [base, 1 house, 2 houses, 3 houses, 4 houses, hotel]
        self.mortgage_value = mortgage_value
        self.house_price = house_price
        self.owner = None
        self.status = PropertyStatus.UNOWNED
        self.houses = 0
        self.hotel = False
    
    def calculate_rent(self, dice_roll=None):
        if self.status == PropertyStatus.MORTGAGED:
            return 0
            
        if self.color == PropertyColor.UTILITY and dice_roll:
            # Utilities rent is based on dice roll
            multiplier = 4 if self.owner.properties.count(self) == 1 else 10
            return dice_roll * multiplier
            
        if self.color == PropertyColor.RAILROAD:
            # Railroads rent increases based on how many railroads the owner has
            railroad_count = sum(1 for prop in self.owner.properties if prop.color == PropertyColor.RAILROAD)
            return self.rents[railroad_count - 1]
            
        # Regular property
        if self.hotel:
            return self.rents[5]
        else:
            return self.rents[self.houses]
    
    def mortgage(self, player):
        if self.status == PropertyStatus.OWNED and self.houses == 0 and not self.hotel:
            self.status = PropertyStatus.MORTGAGED
            player.receive(self.mortgage_value)
            return self.mortgage_value
        return 0
    
    def unmortgage(self):
        if self.status == PropertyStatus.MORTGAGED:
            unmortgage_cost = int(self.mortgage_value)
            self.status = PropertyStatus.OWNED
            return unmortgage_cost
        return 0
    
    def add_house_or_hotel(self):
        #print(self.status, self.hotel, self.houses)
        if self.status == PropertyStatus.OWNED and not self.hotel:
            if  self.houses < 4 :
                self.houses += 1
                return True
            elif self.houses == 4:
                self.hotel = True
                self.houses = 0
                return True
            return False
    
    def remove_hotel(self):
        if self.hotel:
            self.hotel = False
            self.houses = 4
            return True
        return False
    
    def remove_house(self, house_count=1):
        if self.houses > 0:
            self.houses -= 1
            return True
        return False
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
        
        # Create a visual board
        board_size = 11
        board = [[" " for _ in range(board_size)] for _ in range(board_size)]
        
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
                if (i, j) in player_symbols:
                    # Show player tokens if present
                    tokens = "".join(player_symbols[(i, j)])
                    row += f"{tokens:4}|"
                else:
                    row += f"{cell:4}|"

            print(row)
            print("-" * (board_size * 5 + 1))

class MonopolyGame:
    def __init__(self):
        # Get player count with default value handling
        player_count_input = input("Enter number of players (default 0): ").strip()
        player_count = int(player_count_input) if player_count_input else 0
        
        # Get bot count with default value handling
        bot_count_input = input("Enter number of bots (default 2): ").strip()
        bot_count = int(bot_count_input) if bot_count_input else 2
        
        if bot_count + player_count < 2:
            print("Not enough players to start the game.")
            self.game_over = True
        
        self.board = Board()
        self.players = self.create_players(player_count, bot_count)
        self.current_player_idx = 0
        self.doubles_count = 0
        self.game_over = False
    
    def create_players(self, player_count, bot_count):
        tokens = ["🎩", "🚗", "🚢", "🐕", "👞", "🎲", "🐎", "⛲"]
        players = []
        #bots = []
        for i in range(player_count):
            name = input(f"Enter name for player {i + 1}: ")
            token = tokens[i % len(tokens)] # Cycle through tokens if more than 8 players are playing
            players.append(Player(name, token))
        for i in range(bot_count):
            name = f"Bot {i + 1}"
            token = "🤖"
            player = Player(name, token, is_bot=True, game=self)
            #bots.append(Bot(player))
            players.append(player)
            
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
            print(f"\n{player.name} is bankrupt!")
            player.bankrupt = True
            self.transfer_assets(player, recipient)
        else:
            if player.bot.decide_mortgage_property(amount_due): # Can the bot mortgage property?
                player.pay(amount_due)
                return True
            else:
                player.bankrupt = True
                print(f"\n{player.name} is bankrupt!")
                self.transfer_assets(player, recipient)
        return False
        
    def transfer_assets(self, player, recipient):
        # Transfer remaining money and properties to recipient if any
        if recipient:
            recipient.receive(player.money)
            print(f"{player.name} transfers ${player.money} to {recipient.name}.")
            for prop in player.properties:
                prop.owner = recipient
                recipient.properties.append(prop)
        player.money = 0
        player.properties = []
        
        # Check if game is over (only one player left)
        active_players = [p for p in self.players if not p.bankrupt]
        print(len(active_players), active_players)
        if len(active_players) == 1:
            self.game_over = True
            print(f"\n{active_players[0].name} wins the game!")
    
    def handle_property_landing(self, player, property, dice_sum=None):
        if property.status == PropertyStatus.UNOWNED:
            self.offer_property_purchase(player, property)
        elif property.status == PropertyStatus.OWNED and property.owner != player:
            # Pay rent
            rent = property.calculate_rent(dice_sum)
            print(f"\n{player.name} landed on {property.name}, owned by {property.owner.name}.")
            print(f"Rent due: ${rent}")
            
            if player.pay(rent):
                property.owner.receive(rent)
                print(f"{player.name} pays ${rent} to {property.owner.name}.")
            else:
                print(f"{player.name} doesn't have enough money to pay the rent!")
                self.display_statistics()
                self.check_bankruptcy(player, rent, property.owner)
                
    def offer_property_purchase(self, player, property):
        print(f"\n{player.name} landed on {property.name}.")
        print(f"Price: ${property.price}")
        
        # check if player is bot
        
        if player.is_bot:
            choice = 'y' if player.bot.decide_buy_property(property) else 'n'
        else:
            choice = input(f"Would you like to buy {property.name} for ${property.price}? (y/n): ").lower()
        
        if choice == 'n' and player.pay(property.price):
            print(f"{player.name} property is put up on action {property.name}.")
            self.handel_auction(property)
        else:
            player.own_property(property)
            property.owner = player
            property.status = PropertyStatus.OWNED
            print(f"{player.name} now owns {property.name}!")
            
    def handel_auction(self, property):
    
        print(f"\nAuction for {property.name} (Starting price: $1)")
        
        # Players who can participate (not bankrupt and not the one who declined)
        eligible_bidders = [p for p in self.players if not p.bankrupt]
        
        current_bid = 1  # Start at half price
        highest_bidder = None
        
        # Continue auction until only one bidder remains
        active_bidders = eligible_bidders.copy()
        
        while len(active_bidders) > 0:
            for bidder in active_bidders.copy():
                print(f"\nCurrent bid: ${current_bid}")
                print(f"{bidder.name}'s turn (Money: ${bidder.money})")
                
                if bidder.is_bot:
                    choice = bidder.bot.decide_auction_bid(property, current_bid)
                else:
                    choice = input(f"{bidder.name}, bid higher than ${current_bid}? Enter amount (0 to pass): $")
                
                try:
                    bid = int(choice)
                    if bid <= current_bid:
                        print(f"Bid must be higher than ${current_bid}!")
                        print(f"{bidder.name} passes.")
                        active_bidders.remove(bidder)
                    elif bid > bidder.money:
                        print(f"You don't have enough money for that bid!")
                        active_bidders.remove(bidder)
                    else:
                        current_bid = bid
                        highest_bidder = bidder
                        print(f"{bidder.name} bids ${current_bid}!")
                except ValueError:
                    print("Invalid input. You pass by default.")
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
                print(f"\n{highest_bidder.name} won the auction for {property.name} at ${current_bid}!")
            else:
                print(f"{highest_bidder.name} couldn't pay for the property!")
        else:
            print(f"No one bid on {property.name}. Property remains unowned.")
    
    def handle_card(self, player, card_type):
        if card_type == "Chans":
            card = self.board.draw_Chans_card()
            print(f"\nChans card: {card}")
        else:  # community chest
            card = self.board.draw_Almänning_card()
            print(f"\nCommunity Chest card: {card}")
        
        # Process card effects
        if "Advance to Go" in card:
            player.position = 0
            player.receive(200)
            print(f"{player.name} advances to Go and collects $200.")
        elif "Go to Jail" in card:
            player.go_to_jail()
            print(f"{player.name} goes to jail.")
        elif "Collect" in card or "Receive" in card or "get" in card or "matures" in card:
            # Extract amount
            amount = int(''.join(filter(str.isdigit, card)))
            player.receive(amount)
            print(f"{player.name} receives ${amount}.")
        elif "Pay" in card or "fee" in card or "fine" in card:
            # Extract amount
            amount = int(''.join(filter(str.isdigit, card)))
            if player.pay(amount):
                print(f"{player.name} pays ${amount}.")
            else:
                print(f"{player.name} doesn't have enough money!")
                self.check_bankruptcy(player, amount)
        elif "Get Out of Jail Free" in card:
            player.jail_free_cards += 1
            print(f"{player.name} got a Get Out of Jail Free card.")
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
                print(f"{player.name} pays ${tax} in Income Tax.")
            else:
                print(f"{player.name} doesn't have enough money to pay Income Tax!")
                self.check_bankruptcy(player, tax)
        elif space_name == "Chans":
            self.handle_card(player, "C")
        elif space_name == "Jail / Just Visiting":
            print(f"{player.name} is just visiting jail.")
        elif space_name == "Fri Parkering":
            print(f"{player.name} landed on Fri Parkering.")
        elif space_name == "Gå i fängelse":
            player.go_to_jail()
            print(f"{player.name} goes to jail.")
        elif space_name == "Lyxskatt":
            if player.pay(100):
                print(f"{player.name} pays $100 in Luxury Tax.")
            else:
                print(f"{player.name} doesn't have enough money to pay Luxury Tax!")
                self.check_bankruptcy(player, 100)
    
    def handle_jail(self, player):
        if player.jail_turns > 0:
            print(f"\n{player.name} is in jail. {player.jail_turns} turns remaining.")
            
            # Options for getting out of jail
            
            if player.is_bot:
                choice = player.bot.decide_jail_strategy()
            else:
                choice = input("What would you like to do?\n1. Roll for doubles\n2. Use Get Out of Jail Free card\n3. Pay $50\nEnter choice: ")
            
            if choice == "2" and player.jail_free_cards > 0:
                player.jail_free_cards -= 1
                player.jail_turns = 0
                print(f"{player.name} used a Get Out of Jail Free card.")
                return False  # Player can now roll and move
            elif choice == "3":
                if player.pay(50):
                    player.jail_turns = 0
                    print(f"{player.name} paid $50 to get out of jail.")
                    return False
            else:
                # Roll for doubles
                print(f"{player.name} rolls to try for doubles...")
                die1, die2 = self.roll_dice()
                print(f"Rolled: {die1}, {die2}")
            
            if die1 == die2:
                player.jail_turns = 0
                print(f"{player.name} rolled doubles and gets out of jail!")
                return False  # Player can now move using this roll
            else:
                player.jail_turns -= 1
                if player.jail_turns == 0:
                    player.pay(50)  # Pay fine after third turn
                    print(f"{player.name} paid $50 after third turn in jail.")
                return True  # Player's turn ends
        
        return False  # Not in jail
    
    def property_management(self, player):
        
        if not player.properties:
            print("\nYou don't own any properties.")
            return
        
        print("\nYour properties:")
        for i, prop in enumerate(player.properties):
            status = "Mortgaged" if prop.status == PropertyStatus.MORTGAGED else "Owned"
            house_info = ""
            if hasattr(prop, 'houses') and prop.houses > 0:
                house_info = f", {prop.houses} houses"
            elif hasattr(prop, 'hotel') and prop.hotel:
                house_info = ", 1 hotel"
            print(f"{i+1}. {prop.name} ({status}{house_info}) - Value: ${prop.price}")
        
        choice = input("\nWhat would you like to do?\n1. Mortgage a property\n2. Unmortgage a property\n3. Buy houses/hotels\n4. Sell houses/hotels\n5. Trade Property\nEnter choice: ")
        
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
            print("No players available to trade with.")
            return
        
        # Select player to trade with
        print("\nSelect a player to trade with:")
        for i, p in enumerate(available_players):
            print(f"{i+1}. {p.name}")
        
        player_idx = int(input("Enter player number (or 0 to cancel): ")) - 1
        if player_idx < 0 or player_idx >= len(available_players):
            return
        
        trade_partner = available_players[player_idx]
        
        # Show your properties
        if not player.properties:
            print("You don't have any properties to offer.")
            return
        
        print("\nYour properties to offer:")
        for i, prop in enumerate(player.properties):
            status = "Mortgaged" if prop.status == PropertyStatus.MORTGAGED else "Owned"
            print(f"{i+1}. {prop.name} ({status}) - Value: ${prop.price}")
        
        # Select property to offer
        offer_idx = int(input("Select property to offer (or 0 to cancel): ")) - 1
        if offer_idx < 0 or offer_idx >= len(player.properties):
            return
        
        offer_property = player.properties[offer_idx]
        
        # Show partner's properties
        if not trade_partner.properties:
            print(f"{trade_partner.name} doesn't have any properties to trade.")
            return
        
        print(f"\n{trade_partner.name}'s properties:")
        for i, prop in enumerate(trade_partner.properties):
            status = "Mortgaged" if prop.status == PropertyStatus.MORTGAGED else "Owned"
            print(f"{i+1}. {prop.name} ({status}) - Value: ${prop.price}")
        
        # Select property to request
        request_idx = int(input("Select property to request (or 0 to cancel): ")) - 1
        if request_idx < 0 or request_idx >= len(trade_partner.properties):
            return
        
        request_property = trade_partner.properties[request_idx]
        
        # Ask for cash adjustment
        print("\nWould you like to include cash in the trade?")
        cash_option = input("1. You pay cash\n2. Request cash\n3. No cash involved\nEnter choice: ")
        
        cash_amount = 0
        if cash_option == "1":
            cash_amount = int(input(f"How much will you pay? (You have ${player.money}): $"))
            if cash_amount > player.money:
                print("You don't have that much money.")
                return
        elif cash_option == "2":
            cash_amount = -int(input(f"How much will you request? ({trade_partner.name} has ${trade_partner.money}): $"))
            if -cash_amount > trade_partner.money:
                print(f"{trade_partner.name} doesn't have that much money.")
                return
        
        # If bot, automatically decide
        if trade_partner.is_bot:
            # Simple bot logic for deciding trades
            accept = trade_partner.bot.decide_trade(request_property, offer_property, -cash_amount)
            
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
                
                print(f"\nTrade accepted! You traded {offer_property.name} for {request_property.name}.")
                if cash_amount != 0:
                    print(f"{'You paid' if cash_amount > 0 else 'You received'} ${abs(cash_amount)}.")
            else:
                print(f"\n{trade_partner.name} rejected your trade offer.")
        else:
            # Show trade summary to human player
            print(f"\nTrade Offer to {trade_partner.name}:")
            print(f"You offer: {offer_property.name}")
            print(f"You request: {request_property.name}")
            if cash_amount > 0:
                print(f"You will pay: ${cash_amount}")
            elif cash_amount < 0:
                print(f"You will receive: ${-cash_amount}")
            
            accept = input(f"\n{trade_partner.name}, do you accept this trade? (y/n): ").lower() == 'y'
            
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
                
                print("\nTrade completed successfully!")
            else:
                print("\nTrade rejected.")

    def mortage_property(self, player):
        prop_idx = int(input("Enter property number to mortgage: ")) - 1
        if 0 <= prop_idx < len(player.properties):
            prop = player.properties[prop_idx]
            if prop.status != PropertyStatus.MORTGAGED and prop.houses == 0 and not prop.hotel:
                mortgage_value = prop.mortgage()
                player.receive(mortgage_value)
                print(f"Mortgaged {prop.name} for ${mortgage_value}.")
            else:
                print("Cannot mortgage this property. Sell houses first or it's already mortgaged.")
        else:
            print("Invalid property number.")
    
    def unmortage_property(self, player):
        prop_idx = int(input("Enter property number to unmortgage: ")) - 1
        if 0 <= prop_idx < len(player.properties):
            prop = player.properties[prop_idx]
            if prop.status == PropertyStatus.MORTGAGED:
                unmortgage_cost = prop.unmortgage()
                if player.pay(unmortgage_cost):
                    print(f"Unmortgaged {prop.name} for ${unmortgage_cost}.")
                else:
                    print("Not enough money to unmortgage this property.")
                    prop.status = PropertyStatus.MORTGAGED  # Revert back if can't pay
            else:
                print("This property is not mortgaged.")
        else:
            print("Invalid property number.")
    
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
            print("You don't have any complete property sets to build on.")
            return
        
        print("\nYou can build on these property sets:")
        for i, (color, props) in enumerate(complete_sets.items()):
            print(f"{i+1}. {color.value}")
        
        set_idx = int(input("Choose a set to build on (or 0 to cancel): ")) - 1
        if set_idx == -1:
            return
        if 0 <= set_idx < len(complete_sets):
            chosen_color = list(complete_sets.keys())[set_idx]
            props = complete_sets[chosen_color]
            

            
            while True:
                #os.system('cls' if os.name == 'nt' else 'clear')
                # Display properties in the set
                print(f"\nProperties in {chosen_color.value} set:")
                for i, prop in enumerate(props):
                    house_info = f"{prop.houses} houses" if prop.houses > 0 else "no houses"
                    hotel_info = ", has hotel" if prop.hotel else ""
                    print(f"{i+1}. {prop.name} - {house_info}{hotel_info}, house cost: ${prop.house_price}")
                
                try:
                    prop_idx = int(input("Choose a property to build on (or 0 to cancel): ")) - 1
                except ValueError:
                    print("Invalid input. Please enter a number.")
                    continue
                
                if prop_idx == -1: # Cancel if 0
                    return
                if 0 <= prop_idx < len(props):
                    prop = props[prop_idx]
                    
                    # Check if player can build evenly (difference between houses should be at most 1)
                    min_houses = min(p.houses for p in props)
                    if prop.houses > min_houses and not all(p.houses == min_houses for p in props if p != prop):
                        print("You must build evenly. Build on properties with fewer houses first.")
                    
                    # Check if property already has a hotel
                    if prop.hotel:
                        print("This property already has a hotel. No more buildings possible.")
                    
                    # Determine if buying a house or hotel
                    if prop.houses == 4:
                        # Buy a hotel
                        if player.pay(prop.house_price):
                            if prop.add_house_or_hotel():
                                print(f"Added a hotel to {prop.name}!")
                            else:
                                player.receive(prop.house_price)  # Refund if hotel couldn't be added
                                print("Could not add a hotel to this property.")
                        else:
                            print(f"Not enough money to buy a hotel (${prop.house_price}).")
                    else:
                        # Buy a house
                        if player.pay(prop.house_price):
                            if prop.add_house_or_hotel():
                                print(f"Added a house to {prop.name}!")
                            else:
                                player.receive(prop.house_price)  # Refund if house couldn't be added
                                print("Could not add a house to this property.")
                        else:
                            print(f"Not enough money to buy a house (${prop.house_price}).")
                else:
                    print("Invalid property number.")
        else:
            print("Invalid set number.")
    
    def build_house_bot(self, player):
        ''' build house for bot '''
        property = player.bot.decide_house_purchases()
        if property and type:
            if property and type:
                cost = property.house_price
                if player.pay(cost):
                        print(f"Added a house/hotel to {property.name}!")
                        property.add_house_or_hotel()
                    # Check if property already has a hotel
                else:
                    print(f"Not enough money to buy a {type} (${cost}).")
    
    def sell_houses(self, player):
        # Find properties with houses or hotels
        props_with_buildings = [p for p in player.properties if p.houses > 0 or p.hotel]
        
        if not props_with_buildings:
            print("You don't have any properties with houses or hotels.")
            return
        
        print("\nYour properties with buildings:")
        for i, prop in enumerate(props_with_buildings):
            if prop.hotel:
                print(f"{i+1}. {prop.name} - Hotel (sell value: ${prop.house_price // 2})")
            else:
                print(f"{i+1}. {prop.name} - {prop.houses} houses (sell value: ${prop.house_price // 2} each)")
        
        prop_idx = int(input("Choose a property to sell buildings from (or 0 to cancel): ")) - 1
        if prop_idx == -1:
            return
        if 0 <= prop_idx < len(props_with_buildings):
            prop = props_with_buildings[prop_idx]
            
            # Find all properties in same color group
            same_color_props = [p for p in player.properties if p.color == prop.color]
            
            # Check if selling would create uneven distribution (difference > 1)
            if prop.hotel:
                sell_hotel = input("Sell hotel? (y/n): ").lower() == 'y'
                if sell_hotel:
                    if prop.remove_hotel():
                        player.receive(prop.house_price // 2)
                        print(f"Sold hotel from {prop.name} for ${prop.house_price // 2}.")
                    else:
                        print("Could not sell hotel.")
            else:
                num_to_sell = int(input(f"How many houses to sell (1-{prop.houses})? "))
                if 1 <= num_to_sell <= prop.houses:
                    # Check if selling would violate even build rule
                    max_houses = max(p.houses for p in same_color_props)
                    if prop.houses == max_houses or prop.houses - num_to_sell >= max_houses - 1:
                        for _ in range(num_to_sell):
                            if prop.remove_house():
                                player.receive(prop.house_price // 2)
                        print(f"Sold {num_to_sell} houses from {prop.name} for ${(prop.house_price // 2) * num_to_sell}.")
                    else:
                        print("Cannot create uneven building distribution. Sell houses from other properties first.")
                else:
                    print("Invalid number of houses.")
        else:
            print("Invalid property number.")
    
    def play_turn(self):
        player = self.players[self.current_player_idx]
        #os.system('cls' if os.name == 'nt' else 'clear')
        
        if player.bankrupt:
            self.next_player()
            return
        
        self.board.display_board(self.players)
        player.display_status(self.board)
        
        # Check if player is in jail
        in_jail = self.handle_jail(player)
        if in_jail:
            self.next_player()
            return
        
        # Player's turn menu
        while not player.is_bot:
            print("\nTurn Options:")
            print("1. Roll dice")
            print("2. Manage properties")
            print("3. Show all properties")
            choice = input("Enter choice (1-3): ")
            
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
        
        print(f"\n{player.name} rolls: {die1}, {die2} (Total: {dice_sum})")
        
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
            print(f"{player.name} passed GO and collected $200.")
        
        # Handle landing on space
        space = self.board.get_property_at(player.position)
        print(f"{player.name} landed on {space.name if isinstance(space, Property) else space}")
        
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
            input("Press Enter to continue...")
        else:
            player.bot.make_move()
        self.next_player()
    
    def display_all_properties(self):
        print("\nAll Properties on the Board:")
        for space in self.board.spaces:
            if isinstance(space, Property):
                if space.owner:
                    status = f"Owned by {space.owner.name}"
                    if space.status == PropertyStatus.MORTGAGED:
                        status += " (Mortgaged)"
                    elif hasattr(space, 'houses') and space.houses > 0:
                        status += f" ({space.houses} houses)"
                    elif hasattr(space, 'hotel') and space.hotel:
                        status += " (hotel)"
                else:
                    status = "Unowned"
                print(f"{space.name} - ${space.price} - {status}")
    
    def decide_winner(self):
        print("\n=== GAME REACHED 500 TURNS LIMIT ===")
                
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
            
            print("\n=== FINAL STANDINGS ===")
            for name, value in sorted(player_values.items(), key=lambda x: x[1], reverse=True):
                print(f"{name}: ${value}")
            
            print(f"\n{winner.name} WINS THE GAME WITH ${winner.money}!")
            self.game_over = True
            return
    
    def play_game(self):
        print("\nWelcome to Monopoly!")
        
        turns = 0
    
        while not self.game_over:
            # Clear the screen
            #os.system('cls' if os.name == 'nt' else 'clear')
            
            self.play_turn()
            
            if turns >= 500:
                self.decide_winner()
            
            if turns % 100 == 0 and turns != 0:
                if input("Display statistics? (y/n): ").lower() == 'y':
                    self.display_statistics() # Display statistics if player chooses to
            turns += 1
            #time.sleep(1)  # Small pause between turns
        if input("display statistics... ") == 'y':
            self.display_statistics()
        
    def display_statistics(self):
        # Display a comprehensive property and building report
        print("\n=== PROPERTY AND BUILDING REPORT ===")
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

        print(f"Total buildings on board: {total_houses} houses, {total_hotels} hotels")

        # Display all properties grouped by color
        color_groups = {}
        for space in self.board.spaces:
            if isinstance(space, Property):
                if space.color not in color_groups:
                    color_groups[space.color] = []
                color_groups[space.color].append(space)

        # Print properties by color group
        for color, properties in color_groups.items():
            print(f"\n{color.value} Properties:")
            for prop in properties:
                owner_info = f"Owned by {prop.owner.name}" if prop.owner else "Unowned"
                status_info = f" (Mortgaged)" if prop.status == PropertyStatus.MORTGAGED else ""
                
                building_info = ""
                if hasattr(prop, 'houses') and prop.houses > 0:
                    building_info = f", {prop.houses} houses"
                if hasattr(prop, 'hotel') and prop.hotel:
                    building_info = ", Hotel"
                    
                rent_info = f", Current rent: ${prop.calculate_rent()}" if prop.owner else ""
                print(f"  {prop.name} - ${prop.price} - {owner_info}{status_info}{building_info}{rent_info}")

        # Print player property summaries
        print("\nPlayer Property Summaries:")
        for player in active_players:
            property_count = len(player.properties)
            house_count = sum(p.houses for p in player.properties if hasattr(p, 'houses'))
            hotel_count = sum(1 for p in player.properties if hasattr(p, 'hotel') and p.hotel)
            mortgaged_count = sum(1 for p in player.properties if p.status == PropertyStatus.MORTGAGED)
            
            print(f"{player.name}: {property_count} properties, {house_count} houses, {hotel_count} hotels, {mortgaged_count} mortgaged", "$" + str(player.money))

        #display all bankrupt players
        bankrupt_players = [p for p in self.players if p.bankrupt]
        if bankrupt_players:
            print("\n=== BANKRUPT PLAYERS ===")
            for player in bankrupt_players:
                print(f"{player.name} is bankrupt.")
                
        if input("Display extended statistics? (y/n): ").lower() == 'y':
            self.display_extended_statistics()
                
    def display_extended_statistics(self):
        """Display more comprehensive game statistics."""
        active_players = [p for p in self.players if not p.bankrupt]
        bankrupt_players = [p for p in self.players if p.bankrupt]
        
        print("\n=== EXTENDED GAME STATISTICS ===\n")
        
        # Player Rankings by Net Worth
        print("PLAYER RANKINGS BY NET WORTH:")
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
            status = "ACTIVE" if next((p for p in active_players if p.name == name), None) else "BANKRUPT"
            print(f"{i+1}. {name}: ${value:.2f} ({status})")
        
        # Property Statistics
        print("\nPROPERTY STATISTICS:")
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
        
        print(f"Total Properties: {property_stats['total']}")
        print(f"Owned: {property_stats['owned']} ({property_stats['owned']/property_stats['total']*100:.1f}%)")
        print(f"Unowned: {property_stats['unowned']}")
        print(f"Mortgaged: {property_stats['mortgaged']} ({property_stats['mortgaged']/property_stats['owned']*100:.1f}% of owned)")
        print(f"Properties with Houses/Hotels: {property_stats['developed']}")
        print(f"Total Houses on Board: {property_stats['houses']}")
        print(f"Total Hotels on Board: {property_stats['hotels']}")
        
        if most_valuable_prop:
            owner_name = most_valuable_prop.owner.name if most_valuable_prop.owner else "None"
            print(f"\nMost Valuable Property: {most_valuable_prop.name} (Owned by: {owner_name})")
            print(f"Current Rent: ${highest_rent}")
        
        # Most developed color group
        if color_development:
            most_dev_color = max(color_development.items(), 
                                key=lambda x: x[1]["houses"] + x[1]["hotels"]*5)
            print(f"\nMost Developed Color Group: {most_dev_color[0].value}")
            print(f"Development: {most_dev_color[1]['houses']} houses, {most_dev_color[1]['hotels']} hotels")
        
        # Monopoly statistics
        print("\nMONOPOLY STATISTICS:")
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
                print(f"{player_name} has monopoly on: {', '.join(colors)}")
        else:
            print("No player has a monopoly on any color group.")
        
        # Special category ownership
        print("\nSPECIAL CATEGORY OWNERSHIP:")
        for category in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
            for player in active_players:
                count = sum(1 for p in player.properties if p.color == category)
                if count > 0:
                    print(f"{player.name} owns {count} {category.value}s")
        
        # Money distribution
        if active_players:
            print("\nMONEY DISTRIBUTION:")
            total_money = sum(p.money for p in self.players)
            for player in self.players:
                status = "Active" if not player.bankrupt else "Bankrupt"
                percentage = (player.money / total_money * 100) if total_money > 0 else 0
                print(f"{player.name}: ${player.money} ({percentage:.1f}% of total) - {status}")
        input("Press Enter to continue...")
class BotStatistics:
    def __init__(self):
        # Track property purchases
        self.properties_bought = 0
        self.properties_declined = 0
        self.money_spent_on_properties = 0
        
        # Track auction activity
        self.auctions_won = 0
        self.auctions_lost = 0
        self.money_spent_on_auctions = 0
        
        # Track trades
        self.trades_proposed = 0
        self.trades_accepted = 0
        self.trades_rejected = 0
        
        # Track building development
        self.houses_purchased = 0
        self.hotels_purchased = 0
        self.money_spent_on_buildings = 0
        
        # Track mortgage activity
        self.properties_mortgaged = 0
        self.properties_unmortgaged = 0
        
        # Track jail activity
        self.times_in_jail = 0
        self.jail_time_served = 0  # Total turns in jail
        self.paid_to_leave_jail = 0
        self.used_jail_card = 0
        
        # Track income and expenses
        self.rent_collected = 0
        self.rent_paid = 0
        self.tax_paid = 0
        self.money_from_cards = 0
        self.money_from_go = 0
        
        # Track movement
        self.total_moves = 0
        self.total_spaces_moved = 0
        self.doubles_rolled = 0
        
        # Decision making
        self.risky_decisions = 0  # Decisions where risk tolerance was the deciding factor
        self.conservative_decisions = 0  # Decisions to save money or avoid risk

class GameStatistics:
    def __init__(self, players):
        self.game_start_time = time.time()
        self.total_turns = 0
        self.total_dice_rolled = 0
        self.player_stats = {player.name: BotStatistics() for player in players}
        
        # Track property statistics
        self.property_landings = {i: 0 for i in range(40)}
        self.space_rents_collected = {i: 0 for i in range(40) if isinstance(players[0].game.board.spaces[i], Property)}
        
        # Game events
        self.bankruptcies = []  # List of (turn, player_name, creditor)
        self.monopolies_formed = []  # List of (turn, player_name, color)
        self.highest_rent_paid = (0, None, None, None)  # (amount, payer, owner, property)
        
    def record_property_purchase(self, player_name, property, price):
        stats = self.player_stats[player_name]
        stats.properties_bought += 1
        stats.money_spent_on_properties += price
        
    def record_property_declined(self, player_name):
        self.player_stats[player_name].properties_declined += 1
        
    def record_auction_result(self, player_name, property, price, won=True):
        stats = self.player_stats[player_name]
        if won:
            stats.auctions_won += 1
            stats.money_spent_on_auctions += price
        else:
            stats.auctions_lost += 1
            
    def record_trade(self, proposer, responder, accepted):
        self.player_stats[proposer].trades_proposed += 1
        if accepted:
            self.player_stats[proposer].trades_accepted += 1
            self.player_stats[responder].trades_accepted += 1
        else:
            self.player_stats[proposer].trades_rejected += 1
            
    def record_building_purchase(self, player_name, is_hotel, price):
        stats = self.player_stats[player_name]
        if is_hotel:
            stats.hotels_purchased += 1
        else:
            stats.houses_purchased += 1
        stats.money_spent_on_buildings += price
        
    def record_mortgage(self, player_name, is_mortgage):
        if is_mortgage:
            self.player_stats[player_name].properties_mortgaged += 1
        else:
            self.player_stats[player_name].properties_unmortgaged += 1
            
    def record_jail(self, player_name, action=None):
        stats = self.player_stats[player_name]
        if action is None:  # Just went to jail
            stats.times_in_jail += 1
        elif action == "serve":
            stats.jail_time_served += 1
        elif action == "pay":
            stats.paid_to_leave_jail += 1
        elif action == "card":
            stats.used_jail_card += 1
            
    def record_rent(self, payer, receiver, amount, property_position):
        self.player_stats[payer].rent_paid += amount
        self.player_stats[receiver].rent_collected += amount
        self.space_rents_collected[property_position] += amount
        
        # Check if this is the highest rent paid
        if amount > self.highest_rent_paid[0]:
            self.highest_rent_paid = (amount, payer, receiver, property_position)
            
    def record_tax(self, player_name, amount):
        self.player_stats[player_name].tax_paid += amount
        
    def record_card_money(self, player_name, amount):
        self.player_stats[player_name].money_from_cards += amount
        
    def record_go_money(self, player_name):
        self.player_stats[player_name].money_from_go += 200
        
    def record_move(self, player_name, spaces_moved, is_doubles=False):
        stats = self.player_stats[player_name]
        stats.total_moves += 1
        stats.total_spaces_moved += spaces_moved
        if is_doubles:
            stats.doubles_rolled += 1
        
        self.total_dice_rolled += 1
        
    def record_property_landing(self, position):
        self.property_landings[position] += 1
        
    def record_bankruptcy(self, turn, bankrupt_player, creditor=None):
        self.bankruptcies.append((turn, bankrupt_player, creditor))
        
    def record_monopoly(self, turn, player_name, color):
        self.monopolies_formed.append((turn, player_name, color))
        
    def record_decision(self, player_name, risky=True):
        if risky:
            self.player_stats[player_name].risky_decisions += 1
        else:
            self.player_stats[player_name].conservative_decisions += 1
            
    def display_statistics(self):
        """Display comprehensive statistics of the game."""
        game_duration = time.time() - self.game_start_time
        
        print("\n========== GAME STATISTICS ==========")
        print(f"Game Duration: {game_duration:.1f} seconds")
        print(f"Total Turns: {self.total_turns}")
        print(f"Total Dice Rolls: {self.total_dice_rolled}")
        
        print("\n---------- PLAYER ACTIVITY STATISTICS ----------")
        for player_name, stats in self.player_stats.items():
            print(f"\n{player_name}'s Statistics:")
            
            # Property statistics
            print(f"  Properties: Bought {stats.properties_bought}, Declined {stats.properties_declined}")
            print(f"  Money spent on properties: ${stats.money_spent_on_properties}")
            
            # Auction statistics
            print(f"  Auctions: Won {stats.auctions_won}, Lost {stats.auctions_lost}")
            print(f"  Money spent on auctions: ${stats.money_spent_on_auctions}")
            
            # Trading statistics
            if stats.trades_proposed > 0:
                acceptance_rate = (stats.trades_accepted / stats.trades_proposed) * 100
                print(f"  Trades: Proposed {stats.trades_proposed}, Accepted {stats.trades_accepted} ({acceptance_rate:.1f}%)")
            else:
                print(f"  Trades: None proposed")
            
            # Building statistics
            print(f"  Buildings: Houses {stats.houses_purchased}, Hotels {stats.hotels_purchased}")
            print(f"  Money spent on buildings: ${stats.money_spent_on_buildings}")
            
            # Mortgage statistics
            print(f"  Mortgages: Properties mortgaged {stats.properties_mortgaged}, unmortgaged {stats.properties_unmortgaged}")
            
            # Jail statistics
            print(f"  Jail: Times in jail {stats.times_in_jail}, turns served {stats.jail_time_served}")
            print(f"  Jail exits: Paid fine {stats.paid_to_leave_jail}, used get out of jail card {stats.used_jail_card}")
            
            # Money flow
            print(f"  Income: Rent collected ${stats.rent_collected}, GO passes ${stats.money_from_go}, Cards ${stats.money_from_cards}")
            print(f"  Expenses: Rent paid ${stats.rent_paid}, Tax paid ${stats.tax_paid}")
            
            # Movement
            avg_roll = stats.total_spaces_moved / max(1, stats.total_moves)
            print(f"  Movement: Total moves {stats.total_moves}, Average roll {avg_roll:.1f}, Doubles {stats.doubles_rolled}")
            
            # Decision making
            total_decisions = stats.risky_decisions + stats.conservative_decisions
            if total_decisions > 0:
                risk_percentage = (stats.risky_decisions / total_decisions) * 100
                print(f"  Decisions: Risky {stats.risky_decisions} ({risk_percentage:.1f}%), Conservative {stats.conservative_decisions}")
            else:
                print(f"  Decisions: No recorded decisions")
        
        # Most landed on properties
        print("\n---------- BOARD STATISTICS ----------")
        most_landed = sorted(self.property_landings.items(), key=lambda x: x[1], reverse=True)[:5]
        print("Most Landed On Spaces:")
        for position, count in most_landed:
            space = self.get_space_name(position)
            print(f"  {space} (position {position}): {count} times")
        
        # Most profitable properties
        if self.space_rents_collected:
            most_profitable = sorted(self.space_rents_collected.items(), key=lambda x: x[1], reverse=True)[:5]
            print("\nMost Profitable Properties:")
            for position, amount in most_profitable:
                if amount > 0:
                    space = self.get_space_name(position)
                    print(f"  {space} (position {position}): ${amount} collected")
        
        # Highest rent
        if self.highest_rent_paid[0] > 0:
            amount, payer, receiver, position = self.highest_rent_paid
            property_name = self.get_space_name(position)
            print(f"\nHighest Rent: ${amount} paid by {payer} to {receiver} for {property_name}")
        
        # Monopolies formed
        if self.monopolies_formed:
            print("\nMonopolies Formed:")
            for turn, player, color in self.monopolies_formed:
                print(f"  Turn {turn}: {player} completed {color} monopoly")
        
        # Bankruptcies
        if self.bankruptcies:
            print("\nBankruptcies:")
            for turn, player, creditor in self.bankruptcies:
                if creditor:
                    print(f"  Turn {turn}: {player} went bankrupt to {creditor}")
                else:
                    print(f"  Turn {turn}: {player} went bankrupt to the bank")
    
    def get_space_name(self, position):
        """Helper method to get the name of a space by position."""
        space = self.get_board().spaces[position]
        if isinstance(space, Property):
            return space.name
        return space
        
    def get_board(self):
        """Helper method to get the board from the game."""
        # This assumes the GameStatistics has access to the game object
        # You may need to adjust this based on your implementation
        return list(self.player_stats.values())[0].game.board if self.player_stats else None


class Bot:
    def __init__(self, player, game=None): # Bot class 
        self.player = player
        self.game = game
        self.risk_tolerance = random.random()  # 0.0 to 1.0, how risky the bot is in decisions
        
    def decide_buy_property(self, property):
        """Decide whether to buy a property."""
        # Always buy if plenty of money
        if self.player.money > property.price * 3:
            return True
        
        # More likely to buy railroads and utilities
        if property.color in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
            return random.random() < 0.8
        
        # Check if we already own properties of this color
        same_color_count = sum(1 for p in self.player.properties if p.color == property.color)
        if same_color_count > 0:
            return random.random() < 0.7 + (0.1 * same_color_count)  # More likely if we have others
        
        # Base decision on risk tolerance and money available
        return random.random() < self.risk_tolerance and self.player.money > property.price * 1.5

    def decide_auction_bid(self, property, current_bid):
        """Decide how much to bid in an auction."""
        max_willing_to_pay = property.price * (0.8 + self.risk_tolerance * 0.4)
        
        # Bid higher if we already own properties of this color
        same_color_count = sum(1 for p in self.player.properties if p.color == property.color)
        if same_color_count > 0:
            max_willing_to_pay *= (1 + same_color_count * 0.2)
        
        # Don't bid more than we have
        max_willing_to_pay = min(max_willing_to_pay, self.player.money - 50)  # Keep some reserve
        
        if max_willing_to_pay <= current_bid:
            return 0  # Pass
        
        # Bid somewhere between current bid and max willing
        bid_range = max_willing_to_pay - current_bid
        new_bid = current_bid + max(1, int(bid_range * random.random() * 0.5))
        return new_bid
 
    def decide_trade(self, my_property, their_property, cash_amount):
        """Decide whether to accept a trade offer."""
        # Value of properties 
        my_prop_value = my_property.price * (0.5 if my_property.status == PropertyStatus.MORTGAGED else 1.0)
        their_prop_value = their_property.price * (0.5 if their_property.status == PropertyStatus.MORTGAGED else 1.0)
        
        # Check if we have almost a monopoly with their property
        gain_monopoly = False
        for p in self.player.properties:
            if p.color == their_property.color:
                gain_monopoly = True
        
        # Check if we're giving away part of a monopoly
        lose_monopoly = False
        same_color_count = sum(1 for p in self.player.properties if p.color == my_property.color)
        color_total = sum(1 for p in self.player.properties if isinstance(p, Property) and p.color == my_property.color)
        if same_color_count > 1 and same_color_count == color_total:
            lose_monopoly = True
        
        # Adjust values based on strategic importance
        if gain_monopoly:
            their_prop_value *= 1.5
        if lose_monopoly:
            my_prop_value *= 1.5
        
        # Consider the cash component
        total_value_for_me = their_prop_value - my_prop_value + cash_amount
        
        # Also consider if we have enough cash
        if cash_amount < 0 and self.player.money < -cash_amount:
            return False
        
        # Accept if it's a good deal or we're desperate for cash
        return total_value_for_me > 0 or (cash_amount > 0 and self.player.money < 100)

    def initiate_trade(self):
        """Initiate a trade with another player to complete color sets."""
        # Don't try to trade if we have very little money
        if self.player.money < 100:
            return None
        # Find properties that would complete our color sets
        potential_monopolies = {}
        
        # Count how many properties we have of each color
        owned_by_color = {}
        for prop in self.player.properties:
            if prop.color not in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
                if prop.color not in owned_by_color:
                    owned_by_color[prop.color] = 0
                owned_by_color[prop.color] += 1
        
        # Find how many are in each complete set
        color_counts = {}
        for space in self.game.board.spaces:
            if isinstance(space, Property) and space.color not in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
                if space.color not in color_counts:
                    color_counts[space.color] = 0
                color_counts[space.color] += 1
        
        # Find colors where we're one property away from a monopoly
        for color, count in owned_by_color.items():
            if count == color_counts[color] - 1:
                potential_monopolies[color] = color_counts[color]
        
        if not potential_monopolies:
            # No near-monopolies, try to get more railroads or utilities instead
            if any(p.color == PropertyColor.RAILROAD for p in self.player.properties):
                # Try to get more railroads
                potential_monopolies[PropertyColor.RAILROAD] = 4
            elif any(p.color == PropertyColor.UTILITY for p in self.player.properties):
                # Try to get more utilities
                potential_monopolies[PropertyColor.UTILITY] = 2
        
        if not potential_monopolies:
            return None  # No good trading opportunities
        
        # Find the missing properties and their owners
        targets = []
        for color in potential_monopolies:
            # Find properties of this color not owned by us
            for space in self.game.board.spaces:
                if isinstance(space, Property) and space.color == color and space not in self.player.properties:
                    if space.owner and space.owner != self.player and not space.owner.bankrupt:
                        targets.append((space, space.owner))
        
        if not targets:
            return None  # No targetable properties
        
        # Sort targets by value (higher is better)
        targets.sort(key=lambda x: x[0].price, reverse=True)
        
        # Try each target
        for target_prop, target_owner in targets:
            # Find what we could offer in exchange
            offer_props = []
            for prop in self.player.properties:
                # Don't offer properties from potential monopolies
                if prop.color not in potential_monopolies:
                    # Don't offer railroads or utilities unless we have extras
                    if prop.color == PropertyColor.RAILROAD:
                        railroad_count = sum(1 for p in self.player.properties if p.color == PropertyColor.RAILROAD)
                        if railroad_count <= 1:  # Keep at least one
                            continue
                    elif prop.color == PropertyColor.UTILITY:
                        utility_count = sum(1 for p in self.player.properties if p.color == PropertyColor.UTILITY)
                        if utility_count <= 1:  # Keep at least one
                            continue
                            
                    # Don't offer properties with houses/hotels
                    if (hasattr(prop, 'houses') and prop.houses > 0) or (hasattr(prop, 'hotel') and prop.hotel):
                        continue
                        
                    offer_props.append(prop)
            
            # No properties to offer
            if not offer_props:
                continue
                
            # Sort offer properties by how valuable they are to us (less valuable first)
            offer_props.sort(key=lambda p: p.price)
            
            # Try to find a fair trade
            for offer_prop in offer_props:
                # Calculate value difference
                value_diff = target_prop.price - offer_prop.price
                
                # Adjust for mortgaged properties
                if target_prop.status == PropertyStatus.MORTGAGED:
                    value_diff -= target_prop.mortgage_value * 0.1  # Unmortgaging cost
                if offer_prop.status == PropertyStatus.MORTGAGED:
                    value_diff += offer_prop.mortgage_value * 0.1  # They'd have to pay to unmortgage
                
                # Determine cash adjustment
                cash_amount = 0
                if value_diff > 0:  # We need to add cash
                    cash_amount = min(value_diff, self.player.money * 0.7)  # Don't spend more than 70% of our money
                elif value_diff < 0:  # We should receive cash
                    cash_amount = max(value_diff, -target_owner.money * 0.7)  # Don't ask for more than 70% of their money
                
                # Make the trade offer
                print(f"\n{self.player.name} offers {target_owner.name} a trade:")
                print(f"Offering: {offer_prop.name}")
                print(f"Requesting: {target_prop.name}")
                
                if cash_amount > 0:
                    print(f"{self.player.name} offers ${int(cash_amount)} cash")
                elif cash_amount < 0:
                    print(f"{self.player.name} requests ${int(-cash_amount)} cash")
                
                # For AI opponents, use their decide_trade method
                if target_owner.is_bot:
                    bot = target_owner.bot
                    accepted = bot.decide_trade(target_prop, offer_prop, -cash_amount)
                else:
                    # For human players, ask for input
                    accepted = input(f"\n{target_owner.name}, do you accept this trade? (y/n): ").lower() == 'y'
                
                if accepted:
                    # Execute the trade
                    self.player.properties.remove(offer_prop)
                    target_owner.properties.remove(target_prop)
                    
                    self.player.properties.append(target_prop)
                    target_owner.properties.append(offer_prop)
                    
                    offer_prop.owner = target_owner
                    target_prop.owner = self.player
                    
                    if cash_amount > 0:
                        self.player.pay(int(cash_amount))
                        target_owner.receive(int(cash_amount))
                    elif cash_amount < 0:
                        target_owner.pay(int(-cash_amount))
                        self.player.receive(int(-cash_amount))
                    
                    print(f"\nTrade completed! {self.player.name} traded {offer_prop.name} for {target_prop.name}.")
                    if cash_amount != 0:
                        who_paid = f"{self.player.name} paid" if cash_amount > 0 else f"{target_owner.name} paid"
                        print(f"{who_paid} ${int(abs(cash_amount))}.")
                    
                    return True  # Successfully made a trade
        
            return False  # No trades were accepted

    def decide_jail_strategy(self):
        """Decide how to handle being in jail."""
        # Use get out of jail card if available
        if self.player.jail_free_cards > 0:
            return "2"
        
        # Pay the fine if we have plenty of money or in the late game
        if self.player.money > 500:
            return "3"
        
        # Otherwise, try to roll doubles
        return "1"

    def decide_house_purchases(self):
        """Decide whether and where to buy houses."""
        if self.player.money < 200:  # Keep some reserves
            return None
        
        # Group properties by color
        properties_by_color = {}
        for prop in self.player.properties:
            if prop.color not in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
                if prop.color not in properties_by_color:
                    properties_by_color[prop.color] = []
                properties_by_color[prop.color].append(prop)
        
        # Find complete sets
        complete_sets = {}
        for color, props in properties_by_color.items():
            color_count = sum(1 for p in self.game.board.spaces if isinstance(p, Property) and p.color == color)
            if len(props) == color_count:
                complete_sets[color] = props
        
        if not complete_sets:
            return None
        
        # Prioritize based on position (later in the board is better) and current houses
        best_set = None
        best_score = -1
        
        for color, props in complete_sets.items():
            avg_position = sum(p.position for p in props) / len(props)
            avg_houses = sum(p.houses for p in props) / len(props)
            
            # Score based on position (0.4), existing development (0.3), and affordability (0.3)
            position_score = avg_position / 40  # Normalize to 0-1
            development_score = (3 - avg_houses) / 3  # Prefer less developed (more room to build)
            affordability = min(self.player.money / (props[0].house_price * len(props)), 1.0)
            
            score = position_score * 0.4 + development_score * 0.3 + affordability * 0.3
            
            if score > best_score:
                best_score = score
                best_set = props
        
        if not best_set:
            return None
        
        # Find the property with the fewest houses
        best_set.sort(key=lambda p: p.houses)
        return best_set[0]

    def decide_mortgage_property(self, amount_needed):
        """Decide which property to mortgage to raise funds."""
        if not self.player.properties:
            return False

        # First, look for properties with houses/hotels to sell
        properties_with_buildings = [p for p in self.player.properties 
                      if (hasattr(p, 'houses') and p.houses > 0) or 
                         (hasattr(p, 'hotel') and p.hotel)]
        
        # Sort buildings by value (sell least valuable first)
        properties_with_buildings.sort(key=lambda p: p.house_price)
        
        # Try selling houses/hotels first
        properties_to_mortgage = []
        raised_amount = 0
        
        for prop in properties_with_buildings:
            if raised_amount >= amount_needed:
                return True
            if prop.hotel:
                # Selling a hotel yields half the house price * 5
                raised_amount += (prop.house_price // 2) * 5
                prop.remove_hotel()

            elif prop.houses > 0:
                # Calculate how many houses we need to sell
                houses_to_sell = min(prop.houses, 
                        ((amount_needed - raised_amount) + (prop.house_price // 2) - 1) // (prop.house_price // 2))
                raised_amount += (prop.house_price // 2) * houses_to_sell
                prop.remove_house(house_count = houses_to_sell)
        
        # If selling buildings wasn't enough, mortgage properties
        candidates = [p for p in self.player.properties 
                if p.status != PropertyStatus.MORTGAGED and p.houses == 0 and not p.hotel]
            
        # Sort candidates by the criteria defined above
        candidates.sort(key=lambda p: (
            sum(1 for op in self.player.properties if op.color == p.color),
            -p.position,
            -p.mortgage_value
        ))
        
        # Mortgage properties until we've raised enough money
        for prop in candidates:
            properties_to_mortgage.append(prop)
            raised_amount += prop.mortgage_value
            if raised_amount >= amount_needed:
                print(f"\n mortgaging properties to pay off debts.")
                for prop in properties_to_mortgage:
                    prop.mortgage(self.player)
                return True

    def decide_unmortgage_property(self):
        """Decide which properties to unmortgage based on wealth and completing sets."""
        # Only unmortgage if we have plenty of money (at least 500)
        if self.player.money < 500:
            return None
        
        # Find all mortgaged properties
        mortgaged_props = [p for p in self.player.properties if p.status == PropertyStatus.MORTGAGED]
        
        if not mortgaged_props:
            return None
        
        # Count properties by color
        props_by_color = {}
        for prop in self.player.properties:
            if prop.color not in props_by_color:
                props_by_color[prop.color] = []
            props_by_color[prop.color].append(prop)
        
        # Find total properties in each color group
        color_counts = {}
        for space in self.game.board.spaces:
            if isinstance(space, Property):
                if space.color not in color_counts:
                    color_counts[space.color] = 0
                color_counts[space.color] += 1
        
        # First priority: unmortgage properties that complete a set
        for prop in mortgaged_props:
            if prop.color in props_by_color:
                mortgaged_in_color = sum(1 for p in props_by_color[prop.color] if p.status == PropertyStatus.MORTGAGED)
                owned_in_color = len(props_by_color[prop.color])
                
                # If this is the only mortgaged property in a complete set
                if owned_in_color == color_counts.get(prop.color, 0) and mortgaged_in_color == 1:
                    unmortgage_cost = prop.unmortgage()
                    if unmortgage_cost <= self.player.money - 500:  # Keep some reserves
                        print(f"{self.player.name} unmortgages {prop.name} for ${unmortgage_cost} to complete a set")
                        self.player.pay(unmortgage_cost)
                        return prop
        
        # Second priority: unmortgage any property if we're wealthy
        if self.player.money > 1000:
            for prop in mortgaged_props:
                unmortgage_cost = prop.unmortgage()
                if unmortgage_cost <= self.player.money - 700:  # Keep larger reserves
                    print(f"{self.player.name} unmortgages {prop.name} for ${unmortgage_cost}")
                    self.player.pay(unmortgage_cost)
                    return prop
        
        return None

    def make_move(self):
        """Make all decisions for a turn."""
        # If in jail, decide strategy
        if self.player.jail_turns > 0:
            return self.decide_jail_strategy()
            
        property = self.decide_house_purchases()
        if property:
            print(property.name)
        self.game.build_house_bot(self.player)
        print(self.initiate_trade())
        self.decide_unmortgage_property()
        
        # If low on money, consider mortgaging properties
        if self.player.money < 100:
            self.decide_mortgage_property(100 - self.player.money)

class NeuralNetwork(nn.Module):
    def __init__(self, input_dim=100, hidden_dim=64, output_dim=10):
        super(NeuralNetwork, self).__init__()
        self.model = nn.Sequential(
            nn.Linear(input_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, hidden_dim),
            nn.ReLU(),
            nn.Linear(hidden_dim, output_dim)
        )
        
    def forward(self, x):
        return self.model(x)

class NeuralBot(Bot):
    def __init__(self, player):
        super().__init__(player)
        self.model = NeuralNetwork()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)
        self.criterion = nn.MSELoss()
        self.memory = []  # For experience replay
        self.epsilon = 0.3  # For exploration vs exploitation
        
    def _get_state(self, board, players):
        """Create a state representation for the neural network"""
        state = []
        
        # Player information
        state.append(self.player.money / 2000.0)  # Normalized money
        state.append(self.player.position / 40.0)  # Normalized position
        state.append(1.0 if self.player.jail_turns > 0 else 0.0)  # In jail?
        
        # Property ownership (one-hot encoding for each property)
        for i in range(40):
            space = board.spaces[i]
            if isinstance(space, Property):
                # 1 if player owns it, 0 otherwise
                state.append(1.0 if space in self.player.properties else 0.0)
                # 1 if property is mortgaged, 0 otherwise
                state.append(1.0 if space in self.player.properties and space.status == PropertyStatus.MORTGAGED else 0.0)
                # Number of houses normalized
                if space in self.player.properties and hasattr(space, 'houses'):
                    state.append(space.houses / 5.0)
                else:
                    state.append(0.0)
            else:
                # Not a property, add zeros as placeholders
                state.append(0.0)
                state.append(0.0)
                state.append(0.0)
        
        # Add some opponent information
        other_players = [p for p in players if p != self.player and not p.bankrupt]
        avg_money = sum(p.money for p in other_players) / max(1, len(other_players))
        state.append(avg_money / 2000.0)  # Normalized average opponent money
        
        # Pad or truncate to match input_dim
        while len(state) < 100:
            state.append(0.0)
        
        return torch.tensor(state, dtype=torch.float32)
    
    def decide_buy_property(self, property):
        """Use neural network to decide whether to buy property"""
        if random.random() < self.epsilon:  # Exploration
            return super().decide_buy_property(property)
        
        # Get state and predict
        state = self._get_state(None, [])  # Need to implement proper state capture
        prediction = self.model(state)
        buy_score = prediction[0].item()  # First output neuron for buying property
        
        return buy_score > 0.5
    
    def decide_auction_bid(self, property, current_bid):
        """Use neural network to decide auction bid"""
        if random.random() < self.epsilon:  # Exploration
            return super().decide_auction_bid(property, current_bid)
        
        # Get state and predict
        state = self._get_state(None, [])
        prediction = self.model(state)
        bid_percentage = prediction[1].item()  # Second output for bid percentage
        
        # Bid between current_bid and property.price * bid_percentage
        max_bid = min(self.player.money * 0.8, property.price * 1.5)
        new_bid = current_bid + int((max_bid - current_bid) * bid_percentage)
        
        return max(current_bid + 1, new_bid) if new_bid > current_bid else 0
    
    def learn_from_experience(self, old_state, action, reward, new_state):
        """Store experience and learn from it"""
        self.memory.append((old_state, action, reward, new_state))
        
        # Only train after accumulating some experiences
        if len(self.memory) > 100:
            # Sample batch from memory
            batch = random.sample(self.memory, min(32, len(self.memory)))
            
            for old_s, act, rew, new_s in batch:
                # Simple Q-learning update
                target = rew
                if new_s is not None:  # Not a terminal state
                    target += 0.95 * torch.max(self.model(new_s)).item()
                
                # Get current prediction and update the action's value
                current = self.model(old_s)
                target_f = current.clone()
                target_f[0, act] = target
                
                # Train the model
                self.optimizer.zero_grad()
                loss = self.criterion(current, target_f)
                loss.backward()
                self.optimizer.step()
    
    def save_model(self, path="neural_bot_model.pth"):
        """Save the neural network model"""
        torch.save(self.model.state_dict(), path)
    
    def load_model(self, path="neural_bot_model.pth"):
        """Load a previously trained model"""
        self.model.load_state_dict(torch.load(path))
        self.model.eval()

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
