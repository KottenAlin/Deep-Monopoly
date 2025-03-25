import random
from colorama import Fore, Back, Style
from game_models import Property, PropertyColor, 


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
