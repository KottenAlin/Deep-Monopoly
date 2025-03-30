import random
import os
#import numpy as np
import matplotlib.pyplot as plt

# methods for the game
from game_models import Property, PropertyStatus
from board import Board
from player import Player


''' 
    Monopoly Game for Bot Players with less things #printed for speed
    '''
    
    
    
num_games = 100
game_stats = {
        "games_played": 0,
        "average_turns": 0,
        "wins_by_player": {},  # Will track number of wins per player
        "bankrupt_count": {},  # Will track number of bankruptcies per player
        "turns": {},
        "game_over_500_turns": 0,
    }
    
    #initiate risk tolerance for each bot
bots_parameters = [
        {
            "risk_tolerance": 1.0,
            "property_focus": 1.0,
            "development_focus": 1.0,
            "cash_reserve_preference": 1.0,
            "trade_willingness": 1.0,
            "monopoly_focus": 1.0,
            "railroad_utility_interest": 1.0
        },
        {
            "risk_tolerance": 1.0,
            "property_focus": 1.0,
            "development_focus": 1.0,
            "cash_reserve_preference": 0.5,
            "trade_willingness": 0.7,
            "monopoly_focus": 1.0,
            "railroad_utility_interest": 0
        },
        { 
            "risk_tolerance": 0,
            "property_focus": 0,
            "development_focus": 0,
            "cash_reserve_preference": 0,
            "trade_willingness": 1,
            "monopoly_focus": 0,
            "railroad_utility_interest": 0
        },
        {
            "risk_tolerance": 0.2,
            "property_focus": 0.5,
            "development_focus": 0.7,
            "cash_reserve_preference": 0.7,
            "trade_willingness": 0.5,
            "monopoly_focus": 1,
            "railroad_utility_interest": 0.3
        }
        
    ]

class MonopolyGame:
    def __init__(self, bot_count=None, bots_parameters=[]):
        
    
        
        if not bot_count:
            bot_count = int(input("Enter number of bots (0-8): "))
            neural_bot_count = int(input("how many should be neural bots? (0-8): "))
        
        if bot_count < 2:
            print("Not enough players to start the game.")
            self.game_over = True
        
        self.board = Board()
        self.players = self.create_bots(bot_count, neural_bot_count, bots_parameters)
        self.current_player_idx = 0
        self.doubles_count = 0
        self.game_over = False
    
    def create_bots(self, bot_count, neural_bot_count , bots_parameters=[]):
        players = []

        for i in range(bot_count):
            name = f"Bot {i + 1}"
            token = "🤖"
            if i < neural_bot_count:
                player = Player(name, token, is_bot=True, game=self, bot_parameters=bots_parameters[i], bot_type='neural')
            else:
                player = Player(name, token, is_bot=True, game=self, bot_parameters=bots_parameters[i])
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
            #rint(f"\n{player.name} is bankrupt!")
            player.bankrupt = True
            game_stats["bankrupt_count"][player.name] += 1
            self.transfer_assets(player, recipient)
        else:
            if player.bot.decide_mortgage_property(amount_due): # Can the bot mortgage property?
                player.pay(amount_due)
                return True
            else:
                player.bankrupt = True
                game_stats["bankrupt_count"][player.name] += 1
                #(f"\n{player.name} is bankrupt!")
                self.transfer_assets(player, recipient)
        return False
        
    def transfer_assets(self, player, recipient):
        # Transfer remaining money and properties to recipient if any
        if recipient:
            recipient.receive(player.money)
            #print(f"{player.name} transfers ${player.money} to {recipient.name}.")
            for prop in player.properties:
                prop.owner = recipient
                recipient.properties.append(prop)
        player.money = 0
        player.properties = []
        
        # Check if game is over (only one player left)
        active_players = [p for p in self.players if not p.bankrupt]
        #print(len(active_players), active_players)
        if len(active_players) == 1:
            self.game_over = True
            print(f"{active_players[0].name} wins the game!")
            game_stats["wins_by_player"][active_players[0].name] += 1
    
    def handle_property_landing(self, player, property, dice_sum=None):
        if property.status == PropertyStatus.UNOWNED:
            self.offer_property_purchase(player, property)
        elif property.status == PropertyStatus.OWNED and property.owner != player:
            # Pay rent
            rent = property.calculate_rent(dice_sum)
            #print(f"\n{player.name} landed on {property.name}, owned by {property.owner.name}.")
            #print(f"Rent due: ${rent}")
            
            if player.pay(rent):
                property.owner.receive(rent)
                #print(f"{player.name} pays ${rent} to {property.owner.name}.")
            else:
                #print(f"{player.name} doesn't have enough money to pay the rent!")
                
                self.check_bankruptcy(player, rent, property.owner)
                
    def offer_property_purchase(self, player, property):
        #print(f"\n{player.name} landed on {property.name}.")
        #print(f"Price: ${property.price}")
        
        # check if player is bot
        
        if player.is_bot:
            choice = 'y' if player.bot.decide_buy_property(property) else 'n'

        if choice != 'n' and player.pay(property.price):
            player.own_property(property)
            property.owner = player
            property.status = PropertyStatus.OWNED
            #print(f"{player.name} now owns {property.name}!")
        else:

            #print(f"{player.name} property is put up on action {property.name}.")
            self.handel_auction(property)
            
    def handel_auction(self, property):
    
        #print(f"\nAuction for {property.name} (Starting price: $1)")
        
        # Players who can participate (not bankrupt and not the one who declined)
        eligible_bidders = [p for p in self.players if not p.bankrupt]
        
        current_bid = 1  # Start at half price
        highest_bidder = None
        
        # Continue auction until only one bidder remains
        active_bidders = eligible_bidders.copy()
        
        while len(active_bidders) > 0:
            for bidder in active_bidders.copy():
                #print(f"\nCurrent bid: ${current_bid}")
                #print(f"{bidder.name}'s turn (Money: ${bidder.money})")
                
                if bidder.is_bot:
                    choice = bidder.bot.decide_auction_bid(property, current_bid)

                try:
                    bid = int(choice)
                    if bid <= current_bid:
                        #print(f"Bid must be higher than ${current_bid}!")
                        #print(f"{bidder.name} passes.")
                        active_bidders.remove(bidder)
                    elif bid > bidder.money:
                        #print(f"You don't have enough money for that bid!")
                        active_bidders.remove(bidder)
                    else:
                        current_bid = bid
                        highest_bidder = bidder
                        #print(f"{bidder.name} bids ${current_bid}!")
                except ValueError:
                    #print("Invalid input. You pass by default.")
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
                #print(f"\n{highest_bidder.name} won the auction for {property.name} at ${current_bid}!")
            else:
                return
                #print(f"{highest_bidder.name} couldn't pay for the property!")
        else:
            return
            #print(f"No one bid on {property.name}. Property remains unowned.")
    
    def handle_card(self, player, card_type):
        if card_type == "Chans":
            card = self.board.draw_Chans_card()
            #print(f"\nChans card: {card}")
        else:  # community chest
            card = self.board.draw_Almänning_card()
            #print(f"\nCommunity Chest card: {card}")
        
        # Process card effects
        if "Advance to Go" in card:
            player.position = 0
            player.receive(200)
            #print(f"{player.name} advances to Go and collects $200.")
        elif "Go to Jail" in card:
            player.go_to_jail()
            #print(f"{player.name} goes to jail.")
        elif "Collect" in card or "Receive" in card or "get" in card or "matures" in card:
            # Extract amount
            amount = int(''.join(filter(str.isdigit, card)))
            player.receive(amount)
            #print(f"{player.name} receives ${amount}.")
        elif "Pay" in card or "fee" in card or "fine" in card:
            # Extract amount
            amount = int(''.join(filter(str.isdigit, card)))
            if player.pay(amount):
                return
                #print(f"{player.name} pays ${amount}.")
            else:
                #print(f"{player.name} doesn't have enough money!")
                self.check_bankruptcy(player, amount)
        elif "Get Out of Jail Free" in card:
            player.jail_free_cards += 1
            #print(f"{player.name} got a Get Out of Jail Free card.")
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
                #print(f"{player.name} pays ${tax} in Income Tax.")
                return
            else:
                
                #print(f"{player.name} doesn't have enough money to pay Income Tax!")
                self.check_bankruptcy(player, tax)
        elif space_name == "Chans":
            self.handle_card(player, "C")
        elif space_name == "Jail / Just Visiting":
            return
            #print(f"{player.name} is just visiting jail.")
        elif space_name == "Fri Parkering":
            return
            #print(f"{player.name} landed on Fri Parkering.")
        elif space_name == "Gå i fängelse":
            player.go_to_jail()
            #print(f"{player.name} goes to jail.")
        elif space_name == "Lyxskatt":
            if player.pay(100):
                #print(f"{player.name} pays $100 in Luxury Tax.")
                return
            else:
                #print(f"{player.name} doesn't have enough money to pay Luxury Tax!")
                self.check_bankruptcy(player, 100)
    
    def handle_jail(self, player):
        if player.jail_turns > 0:
            
            # Options for getting out of jail
            
            if player.is_bot:
                choice = player.bot.decide_jail_strategy()

            if choice == "2" and player.jail_free_cards > 0:
                player.jail_free_cards -= 1
                player.jail_turns = 0
                return False  # Player can now roll and move
            elif choice == "3":
                if player.pay(50):
                    player.jail_turns = 0
                    
                    return False
            else:
                # Roll for doubles
                die1, die2 = self.roll_dice()
                
                if die1 == die2:
                    player.jail_turns = 0

                    return False  # Player can now move using this roll
                else:
                    player.jail_turns -= 1
                    if player.jail_turns == 0:
                        player.pay(50)  # Pay fine after third turn
                        #print(f"{player.name} paid $50 after third turn in jail.")
                    return True  # Player's turn ends
        
        return False  # Not in jail

    def build_house_bot(self, player):
        ''' build house for bot '''
        property = player.bot.decide_house_purchases()
        if property and type:
            if property and type:
                cost = property.house_price
                if player.pay(cost):
                        #print(f"Added a house/hotel to {property.name}!")
                        property.add_house_or_hotel()
                    # Check if property already has a hotel
                else:
                    #print(f"Not enough money to buy a {type} (${cost}).")
                    return
    
    def play_turn(self):
        player = self.players[self.current_player_idx]
        #os.system('cls' if os.name == 'nt' else 'clear')
        
        if player.bankrupt:
            self.next_player()
            return
        #player.display_status(self.board)
        
        # Check if player is in jail
        in_jail = self.handle_jail(player)
        if in_jail:
            self.next_player()
            return

        # Roll dice and move
        die1, die2 = self.roll_dice()
        dice_sum = die1 + die2
        
        
        # Move player
        passed_go = player.move(dice_sum)
        if passed_go:
            player.receive(200)
            
        
        # Handle landing on space
        space = self.board.get_property_at(player.position)
        
        if isinstance(space, Property):
            self.handle_property_landing(player, space, dice_sum)
        else:
            self.handle_special_space(player, space)
        
        # Check if game is over due to bankruptcy
        if self.game_over:
            return
        

        player.bot.make_move()
        self.next_player()
    
    def decide_winner(self):
        #print("\n=== GAME REACHED 500 TURNS LIMIT ===")
                
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
            
            '''print("\n=== FINAL STANDINGS ===")
            for name, value in sorted(player_values.items(), key=lambda x: x[1], reverse=True):
                print(f"{name}: ${value}")'''
            
            print(f"{winner.name} WINS THE GAME WITH ${winner.money}!")
            game_stats["wins_by_player"][winner.name] += 1
            self.game_over = True
            return
    
    def play_game(self):
        #print("\nWelcome to Monopoly!")
        
        turns = 0
    
        while not self.game_over:
            # Clear the screen
            #os.system('cls' if os.name == 'nt' else 'clear')
            
            self.play_turn()
            
            if turns >= 500:
                game_stats["game_over_500_turns"] += 1
                self.decide_winner()
            
            if turns % 100 == 0 and turns != 0:
                '''input("Display statistics? (y/n): ").lower()
                self.display_statistics() # Display statistics if player chooses to
                input("Press enter to continue...")'''
            turns += 1
            
        #input("display statistics... ")
        #self.display_statistics()
        
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

                # print properties by color group
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

                #print player property summaries
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

def display_statistics():
    #print overall statistics
    print("\n===== OVERALL GAME STATISTICS =====")
    print(f"Total games played: {game_stats['games_played']}")
    print("\nWins by player:")
    for player, wins in game_stats["wins_by_player"].items():
        player_index = int(player.split()[1]) - 1  # Extract the bot number from name and adjust to 0-based index
        print(f"{player}: {wins} wins ({(wins/game_stats['games_played'])*100:.1f}%)")

    print("\nBankruptcy rate:")
    for player, count in game_stats["bankrupt_count"].items():
        print(f"{player}: {count} bankruptcies ({(count/game_stats['games_played'])*100:.1f}%)")

    print(f"\nGames that reached 500 turns: {game_stats['game_over_500_turns']} (){(game_stats['game_over_500_turns']/game_stats['games_played'])*100:.1f}%)")

        # display bot parameters
    print("\nPLAYER PARAMETERS")
    print("===================================")
    for i, parameters in enumerate(bots_parameters):
        print(f"BOT {i+1} PARAMETERS:")
        for key, value in parameters.items():
            print(f"{key}: {value:.2f}")

def main():
    # Global variable to track game statistics
    global game_stats
    

    for i in range(bot_count):
        game_stats["wins_by_player"][f"Bot {i+1}"] = 0  # Initialize wins for each bot
        game_stats["bankrupt_count"][f"Bot {i+1}"] = 0  # Initialize bankrupt count for each bot
    
    for i in range(num_games):  # play 100 games
        print(f"Game {i+1} of 100")
        game = MonopolyGame(bot_count=bot_count, bots_parameters=bots_parameters)
        game.play_game()
        # Update statistics
        game_stats["games_played"] += 1

    display_statistics()
    
# Run the game
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\nGame cancelled by user.")
        print("Monopoly game ended. Thank you for playing!")
        ##print the stats for everyone
