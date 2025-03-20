import random
from enum import Enum
import time
import os

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
    def __init__(self, name, token, is_bot=False, bot = None):
        self.name = name
        self.token = token
        self.position = 0
        self.money = 1500
        self.properties = []
        self.jail_turns = 0
        self.jail_free_cards = 0
        self.bankrupt = False
        self.is_bot = is_bot
        self.bot = bot
    
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
        
    def display_status(self):
        print(f"\n{self.name} ({self.token}):")
        print(f"  Position: {self.position}")
        print(f"  Money: ${self.money}")
        print(f"  Properties: {', '.join([p.name for p in self.properties]) if self.properties else 'None'}")
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
    
    def mortgage(self):
        if self.status == PropertyStatus.OWNED and self.houses == 0 and not self.hotel:
            self.status = PropertyStatus.MORTGAGED
            return self.mortgage_value
        return 0
    
    def unmortgage(self):
        if self.status == PropertyStatus.MORTGAGED:
            unmortgage_cost = int(self.mortgage_value * 1.1)  # 10% interest
            self.status = PropertyStatus.OWNED
            return unmortgage_cost
        return 0
    
    def add_house(self):
        if self.status == PropertyStatus.OWNED and self.houses < 4 and not self.hotel:
            self.houses += 1
            return True
        return False
    
    def add_hotel(self):
        if self.status == PropertyStatus.OWNED and self.houses == 4:
            self.houses = 0
            self.hotel = True
            return True
        return False
    
    def remove_hotel(self):
        if self.hotel:
            self.hotel = False
            self.houses = 4
            return True
        return False
    
    def remove_house(self):
        if self.houses > 0:
            self.houses -= 1
            return True
        return False

class Board:
    def __init__(self):
        self.spaces = self.create_board()
        self.chance_cards = self.create_chance_cards()
        self.community_chest_cards = self.create_community_chest_cards()
        random.shuffle(self.chance_cards)
        random.shuffle(self.community_chest_cards)
    
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
        spaces[24] = Property("Hangatan", 24, 240, PropertyColor.RED, [20, 100, 300, 750, 925, 1100], 120, 150)
        
        # Yellow properties
        spaces[26] = Property("Vasagatan", 26, 260, PropertyColor.YELLOW, [22, 110, 330, 800, 975, 1150], 130, 150)
        spaces[27] = Property("Kungsgatan", 27, 260, PropertyColor.YELLOW, [22, 110, 330, 800, 975, 1150], 130, 150)
        spaces[29] = Property("Stureplan", 29, 280, PropertyColor.YELLOW, [24, 120, 360, 850, 1025, 1200], 140, 150)
        
        # Green properties
        spaces[31] = Property("Gustav Adolfs Torg", 31, 300, PropertyColor.GREEN, [26, 130, 390, 900, 1100, 1275], 150, 200)
        spaces[32] = Property("Drottninggatan", 32, 300, PropertyColor.GREEN, [26, 130, 390, 900, 1100, 1275], 150, 200)
        spaces[34] = Property("Diplomatstaden", 34, 320, PropertyColor.GREEN, [28, 150, 450, 1000, 1200, 1400], 160, 200)
        
        # Dark Blue properties
        spaces[37] = Property("Park Place", 37, 350, PropertyColor.DARK_BLUE, [35, 175, 500, 1100, 1300, 1500], 175, 200)
        spaces[39] = Property("Boardwalk", 39, 400, PropertyColor.DARK_BLUE, [50, 200, 600, 1400, 1700, 2000], 200, 200)
        
        # Railroads
        spaces[5] = Property("Reading Railroad", 5, 200, PropertyColor.RAILROAD, [25, 50, 100, 200], 100)
        spaces[15] = Property("Pennsylvania Railroad", 15, 200, PropertyColor.RAILROAD, [25, 50, 100, 200], 100)
        spaces[25] = Property("B&O Railroad", 25, 200, PropertyColor.RAILROAD, [25, 50, 100, 200], 100)
        spaces[35] = Property("Short Line", 35, 200, PropertyColor.RAILROAD, [25, 50, 100, 200], 100)
        
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
    
    def create_chance_cards(self):
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
    
    def create_community_chest_cards(self):
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
    
    def draw_chance_card(self):
        card = self.chance_cards.pop(0)
        self.chance_cards.append(card)  # Put the card at the bottom of the deck
        return card
    
    def draw_community_chest_card(self):
        card = self.community_chest_cards.pop(0)
        self.community_chest_cards.append(card)  # Put the card at the bottom of the deck
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
        player_count = int(input("Enter number of players: "))
        bot_count = int(input("Enter number of bots"))
        self.board = Board()
        self.players = self.create_players(player_count, bot_count)
        self.current_player_idx = 0
        self.doubles_count = 0
        self.game_over = False
    
    def create_players(self, player_count, bot_count):
        tokens = ["🎩", "🚗", "🚢", "🐕", "👞", "🎲", "🐎", "⛲"]
        players = []
        for i in range(player_count):
            name = input(f"Enter name for player {i + 1}: ")
            token = tokens[i % len(tokens)] # Cycle through tokens if more than 8 players are playing
            players.append(Player(name, token))
        for i in range(bot_count):
            name = f"Bot {i + 1}"
            
            token = tokens[(i + player_count) % len(tokens)]
            players.append(Player(name, token, is_bot=True, bot=Bot()))
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
        
        if total_assets < amount_due:
            print(f"\n{player.name} is bankrupt!")
            player.bankrupt = True
            
            # Transfer remaining money and properties to recipient if any
            if recipient:
                recipient.receive(player.money)
                for prop in player.properties:
                    prop.owner = recipient
                    recipient.properties.append(prop)
            
            # Check if game is over (only one player left)
            active_players = [p for p in self.players if not p.bankrupt]
            if len(active_players) == 1:
                self.game_over = True
                print(f"\n{active_players[0].name} wins the game!")
            
            return True
        return False
        
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
                self.check_bankruptcy(player, rent, property.owner)
    
    def offer_property_purchase(self, player, property):
        print(f"\n{player.name} landed on {property.name}.")
        print(f"Price: ${property.price}")
        
        choice = input(f"Would you like to buy {property.name} for ${property.price}? (y/n): ").lower()
        if choice == 'y' and player.pay(property.price):
            player.own_property(property)
            property.owner = player
            property.status = PropertyStatus.OWNED
            print(f"{player.name} now owns {property.name}!")
        else:
            print(f"{player.name} property is put up on action {property.name}.")
            self.handel_auction(player, property)
            
    
    def handel_auction(self, player, property):
    
        print(f"\nAuction for {property.name} (Starting price: ${1})")
        
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
        if card_type == "chance":
            card = self.board.draw_chance_card()
            print(f"\nChance card: {card}")
        else:  # community chest
            card = self.board.draw_community_chest_card()
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
        elif space_name == "Community Chest":
            self.handle_card(player, "community_chest")
        elif space_name == "Income Tax":
            tax = min(200, int(player.money * 0.1))  # Pay $200 or 10%, whichever is less
            if player.pay(tax):
                print(f"{player.name} pays ${tax} in Income Tax.")
            else:
                print(f"{player.name} doesn't have enough money to pay Income Tax!")
                self.check_bankruptcy(player, tax)
        elif space_name == "Chance":
            self.handle_card(player, "chance")
        elif space_name == "Jail / Just Visiting":
            print(f"{player.name} is just visiting jail.")
        elif space_name == "Free Parking":
            print(f"{player.name} landed on Free Parking.")
        elif space_name == "Go To Jail":
            player.go_to_jail()
            print(f"{player.name} goes to jail.")
        elif space_name == "Luxury Tax":
            if player.pay(75):
                print(f"{player.name} pays $75 in Luxury Tax.")
            else:
                print(f"{player.name} doesn't have enough money to pay Luxury Tax!")
                self.check_bankruptcy(player, 75)
    
    def handle_jail(self, player):
        if player.jail_turns > 0:
            print(f"\n{player.name} is in jail. {player.jail_turns} turns remaining.")
            
            # Options for getting out of jail
            if player.jail_free_cards > 0:
                use_card = input("Use a Get Out of Jail Free card? (y/n): ").lower() == 'y'
                if use_card:
                    player.jail_free_cards -= 1
                    player.jail_turns = 0
                    print(f"{player.name} used a Get Out of Jail Free card.")
                    return False  # Player can now roll and move
            
            pay_fine = input("Pay $50 to get out of jail? (y/n): ").lower() == 'y'
            if pay_fine and player.pay(50):
                player.jail_turns = 0
                print(f"{player.name} paid $50 to get out of jail.")
                return False  # Player can now roll and move
            
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
        
        choice = input("\nWhat would you like to do?\n1. Mortgage a property\n2. Unmortgage a property\n3. Buy houses/hotels\n4. Sell houses/hotels\n5. Back to turn menu\nEnter choice: ")
        
        if choice == "1":
            # Mortgage a property
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
        
        elif choice == "2":
            # Unmortgage a property
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
        
        elif choice == "3":
            # Buy houses/hotels
            self.buy_houses(player)
        
        elif choice == "4":
            # Sell houses/hotels
            self.sell_houses(player)
    
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
            
            # Display properties in the set
            print(f"\nProperties in {chosen_color.value} set:")
            for i, prop in enumerate(props):
                house_info = f"{prop.houses} houses" if prop.houses > 0 else "no houses"
                hotel_info = ", has hotel" if prop.hotel else ""
                print(f"{i+1}. {prop.name} - {house_info}{hotel_info}, house cost: ${prop.house_price}")
            
            prop_idx = int(input("Choose a property to build on (or 0 to cancel): ")) - 1
            if prop_idx == -1:
                return
            if 0 <= prop_idx < len(props):
                prop = props[prop_idx]
                
                # Check if player can build evenly (difference between houses should be at most 1)
                min_houses = min(p.houses for p in props)
                if prop.houses > min_houses and not all(p.houses == min_houses for p in props if p != prop):
                    print("You must build evenly. Build on properties with fewer houses first.")
                    return
                
                # Check if property already has a hotel
                if prop.hotel:
                    print("This property already has a hotel. No more buildings possible.")
                    return
                
                # Determine if buying a house or hotel
                if prop.houses == 4:
                    # Buy a hotel
                    if player.pay(prop.house_price):
                        if prop.add_hotel():
                            print(f"Added a hotel to {prop.name}!")
                        else:
                            player.receive(prop.house_price)  # Refund if hotel couldn't be added
                            print("Could not add a hotel to this property.")
                    else:
                        print(f"Not enough money to buy a hotel (${prop.house_price}).")
                else:
                    # Buy a house
                    if player.pay(prop.house_price):
                        if prop.add_house():
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
        
        if player.bankrupt:
            self.next_player()
            return
        
        self.board.display_board(self.players)
        player.display_status()
        
        # Check if player is in jail
        in_jail = self.handle_jail(player)
        if in_jail:
            self.next_player()
            return
        
        # Player's turn menu
        while True:
            print("\nTurn Options:")
            print("1. Roll dice")
            print("2. Manage properties")
            print("3. Show all properties")
            choice = input("Enter choice (1-3): ")
            
            if choice == "1":
                break  # Continue with dice roll
            elif choice == "2":
                self.property_management(player)
            elif choice == "3":
                self.display_all_properties()
        
        # Roll dice and move
        die1, die2 = self.roll_dice()
        dice_sum = die1 + die2
        is_doubles = die1 == die2
        
        print(f"\n{player.name} rolls: {die1}, {die2} (Total: {dice_sum})")
        
        if is_doubles:
            self.doubles_count += 1
            print("Doubles!")
            
            if self.doubles_count == 3:
                print("Third doubles in a row! Going to jail.")
                player.go_to_jail()
                self.doubles_count = 0
                self.next_player()
                return
        
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
        if is_doubles and player.jail_turns == 0:
            print(f"{player.name} rolled doubles and goes again!")
        else:
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
    
    def play_game(self):
        print("\nWelcome to Monopoly!")
        try:
            while not self.game_over:
                self.play_turn()
                #time.sleep(1)  # Small pause between turns
        except KeyboardInterrupt:
            print("\nGame cancelled by user.")
            # Clear the screen
            os.system('cls' if os.name == 'nt' else 'clear')
            print("Monopoly game ended. Thank you for playing!")



class Bot:
    def __init__(self, player, game): # Bot class 
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

    def decide_jail_strategy(self):
        """Decide how to handle being in jail."""
        # Use get out of jail card if available
        if self.player.jail_free_cards > 0:
            return "card"
        
        # Pay the fine if we have plenty of money or in the late game
        if self.player.money > 500:
            return "pay"
        
        # Otherwise, try to roll doubles
        return "roll"

    def decide_house_purchases(self):
        """Decide whether and where to buy houses."""
        if self.player.money < 200:  # Keep some reserves
            return None, None
        
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
            return None, None
        
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
            return None, None
        
        # Find the property with the fewest houses
        best_set.sort(key=lambda p: p.houses)
        return best_set[0], "house" if best_set[0].houses < 4 else "hotel"

    def decide_mortgage_property(self, amount_needed):
        """Decide which property to mortgage to raise funds."""
        if not self.player.properties:
            return None
        
        # Candidate properties that can be mortgaged
        candidates = [p for p in self.player.properties 
                      if p.status != PropertyStatus.MORTGAGED and p.houses == 0 and not p.hotel]
        
        if not candidates:
            return None
        
        # Sort by importance (least to most)
        candidates.sort(key=lambda p: (
            # Sort by whether it's part of a complete set (preserve complete sets)
            sum(1 for op in self.player.properties if op.color == p.color),
            # Sort by position value (mortgage less valuable properties first)
            -p.position,
            # Sort by mortgage value (mortgage lower value properties first)
            -p.mortgage_value
        ))
        
        return candidates[0]

    def make_move(self):
        """Make all decisions for a turn."""
        # If in jail, decide strategy
        if self.player.jail_turns > 0:
            return self.decide_jail_strategy()
        
        # Check if we should buy houses
        property_to_build, building_type = self.decide_house_purchases()
        if property_to_build and self.player.money > property_to_build.house_price * 2:
            return {
                "action": "build",
                "property": property_to_build,
                "type": building_type
            }
        
        # If low on money, consider mortgaging properties
        if self.player.money < 100:
            property_to_mortgage = self.decide_mortgage_property(100 - self.player.money)
            if property_to_mortgage:
                return {
                    "action": "mortgage",
                    "property": property_to_mortgage
                }
        
        # Otherwise, just roll the dice
        return {
            "action": "roll"
        }


# Run the game
if __name__ == "__main__":
    game = MonopolyGame()
    game.play_game()