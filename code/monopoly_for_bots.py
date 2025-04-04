import random
import os


# methods for the game
from game_models import Property, PropertyStatus
from board import Board
from player import Player

from stats import display_statistics, display_game_statistics
from variables import bots_parameters, game_stats, colors, num_games


""" 
    Monopoly Game for Bot Players with less things #printed for speed
    """


# initiate risk tolerance for each bot



class MonopolyGame:
    def __init__(
        self, bot_count=2, neural_bot_count=2, bots_parameters=[], game_count=0
    ):

        if bot_count < 2:
            print(
                f"{colors['error']}Not enough players to start the game.{colors['reset']}"
            )
            self.game_over = True

        self.board = Board()
        self.players = self.create_bots(bot_count, neural_bot_count, bots_parameters)
        self.current_player_idx = 0
        self.doubles_count = 0
        self.game_count = game_count

        self.game_over = False
        self.winner = None

        # Initialize neural bots if there are any
        self.turn_count = 0
        """
        if neural_bot_count > 0:
            #print(f"{self.colors['title']}Initializing neural network models for bots...")
            for player in self.players:
                if player.is_bot and player.bot.__class__.__name__ == "NeuralBot":
                    #print(f"{self.colors['bot']}Initializing model for {player.name}")
                    player.bot.game = self  # Ensure the bot has a reference to the game
                    player.bot.initialise_model()  # Initialize the neural network model
                    #except Exception as e:
                        #print(f"{self.colors['error']}Error initializing model: {e}")
            #print(f"{self.colors['success']}All neural bot models initialized successfully!")
    """

    def create_bots(self, bot_count, neural_bot_count, bots_parameters=[]):
        players = []

        for i in range(bot_count):
            name = f"Bot {i + 1}"
            token = "🤖"
            if i < neural_bot_count:
                player = Player(
                    name,
                    token,
                    is_bot=True,
                    game=self,
                    bot_parameters=bots_parameters[i],
                    bot_type="neural",
                )
            else:
                player = Player(
                    name,
                    token,
                    is_bot=True,
                    game=self,
                    bot_parameters=bots_parameters[i],
                )
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
            if hasattr(prop, "houses") and prop.houses > 0:
                total_assets += (prop.house_price // 2) * prop.houses
            elif hasattr(prop, "hotel") and prop.hotel:
                total_assets += (prop.house_price // 2) * 5  # Hotel is worth 5 houses

        if total_assets < amount_due:
            # print(f"{colors['error']}\n{player.name} is bankrupt!{colors['reset']}")
            player.bankrupt = True
            if game_stats["bankrupt_count"]:
                game_stats["bankrupt_count"][player.name] += 1
            self.transfer_assets(player, recipient)
        else:
            if player.bot.decide_mortgage_property(
                amount_due
            ):  # Can the bot mortgage property?
                player.pay(amount_due)
                return True
            else:
                player.bankrupt = True
                if game_stats["bankrupt_count"]:
                    game_stats["bankrupt_count"][player.name] += 1
                self.transfer_assets(player, recipient)
        return False

    def transfer_assets(self, player, recipient):
        # Transfer remaining money and properties to recipient if any
        if recipient:
            recipient.receive(player.money)
            # print(f"{colors['info']}{player.name} transfers ${player.money} to {recipient.name}.{colors['reset']}")
            for prop in player.properties:
                prop.owner = recipient
                recipient.properties.append(prop)
        player.money = 0
        player.properties = []

        # Check if game is over (only one player left)
        active_players = [p for p in self.players if not p.bankrupt]
        # print(f"{colors['info']}{len(active_players)}, {active_players}{colors['reset']}")
        if len(active_players) == 1:
            self.game_over = True
            self.winner = active_players[0]
            print(
                f"{colors['success']}{self.winner.name} wins the game!{colors['reset']}"
            )
            if game_stats["wins_by_player"]:
                game_stats["wins_by_player"][active_players[0].name] += 1
                game_stats["turns"][self.winner.name] = self.turn_count

    def handle_property_landing(self, player, property, dice_sum=None):
        if property.status == PropertyStatus.UNOWNED:
            self.offer_property_purchase(player, property)
        elif property.status == PropertyStatus.OWNED and property.owner != player:
            # Pay rent
            rent = property.calculate_rent(dice_sum)
            # print(f"{colors['info']}\n{player.name} landed on {property.name}, owned by {property.owner.name}.{colors['reset']}")
            # print(f"{colors['prompt']}Rent due: ${rent}{colors['reset']}")

            if player.pay(rent):
                property.owner.receive(rent)
                # Track rent collection statistics
                if game_stats["total_rent_collected"]:
                    game_stats["total_rent_collected"][property.owner.name] += rent
                
                # Track property value statistics
                if game_stats["most_valuable_property"] and property.owner.name in game_stats["most_valuable_property"]:
                    if rent > game_stats["most_valuable_property"][property.owner.name]["rent"]:
                        game_stats["most_valuable_property"][property.owner.name] = {
                            "name": property.name,
                            "rent": rent
                        }
                
                # print(f"{colors['info']}{player.name} pays ${rent} to {property.owner.name}.{colors['reset']}")
            else:
                # print(f"{colors['error']}{player.name} doesn't have enough money to pay the rent!{colors['reset']}")
                self.check_bankruptcy(player, rent, property.owner)

    def offer_property_purchase(self, player, property):
        # print(f"{colors['info']}\n{player.name} landed on {property.name}.{colors['reset']}")
        # print(f"{colors['prompt']}Price: ${property.price}{colors['reset']}")

        # check if player is bot
        if player.is_bot:
            choice = "y" if player.bot.decide_buy_property(property) else "n"

        if choice != "n" and player.pay(property.price):
            player.own_property(property)
            property.owner = player
            property.status = PropertyStatus.OWNED
            
            # Track property acquisition statistics
            if game_stats["property_acquisitions"]:
                game_stats["property_acquisitions"][player.name] += 1
                
            # Track property types owned
            if game_stats["most_owned_property_type"] and player.name in game_stats["most_owned_property_type"]:
                property_color = property.color.value if hasattr(property, "color") else "Special"
                if property_color in game_stats["most_owned_property_type"][player.name]:
                    game_stats["most_owned_property_type"][player.name][property_color] += 1
                else:
                    game_stats["most_owned_property_type"][player.name][property_color] = 1
            
            # print(f"{colors['success']}{player.name} now owns {property.name}!{colors['reset']}")
        else:
            # print(f"{colors['info']}{player.name} property is put up on action {property.name}.{colors['reset']}")
            self.handel_auction(property)

    def handel_auction(self, property):

        # print(f"{colors['title']}\nAuction for {property.name} (Starting price: $1){colors['reset']}")

        # Players who can participate (not bankrupt and not the one who declined)
        eligible_bidders = [p for p in self.players if not p.bankrupt]

        current_bid = 1  # Start at half price
        highest_bidder = None

        # Continue auction until only one bidder remains
        active_bidders = eligible_bidders.copy()

        while len(active_bidders) > 0:
            for bidder in active_bidders.copy():
                # print(f"{colors['info']}\nCurrent bid: ${current_bid}{colors['reset']}")
                # print(f"{colors['prompt']}{bidder.name}'s turn (Money: ${bidder.money}){colors['reset']}")

                if bidder.is_bot:
                    choice = bidder.bot.decide_auction_bid(property, current_bid)

                try:
                    bid = int(choice)
                    if bid <= current_bid:
                        # print(f"{colors['error']}Bid must be higher than ${current_bid}!{colors['reset']}")
                        # print(f"{colors['info']}{bidder.name} passes.{colors['reset']}")
                        active_bidders.remove(bidder)
                    elif bid > bidder.money:
                        # print(f"{colors['error']}You don't have enough money for that bid!{colors['reset']}")
                        active_bidders.remove(bidder)
                    else:
                        current_bid = bid
                        highest_bidder = bidder
                        # print(f"{colors['success']}{bidder.name} bids ${current_bid}!{colors['reset']}")
                except ValueError:
                    # print(f"{colors['error']}Invalid input. You pass by default.{colors['reset']}")
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
                # print(f"{colors['success']}\n{highest_bidder.name} won the auction for {property.name} at ${current_bid}!{colors['reset']}")
            else:
                return
                # print(f"{colors['error']}{highest_bidder.name} couldn't pay for the property!{colors['reset']}")
        else:
            return
            # print(f"{colors['info']}No one bid on {property.name}. Property remains unowned.{colors['reset']}")

    def handle_card(self, player, card_type):
        if card_type == "Chans":
            card = self.board.draw_Chans_card()
            # print(f"{colors['info']}\nChans card: {card}{colors['reset']}")
        else:  # community chest
            card = self.board.draw_Almänning_card()
            # print(f"{colors['info']}\nCommunity Chest card: {card}{colors['reset']}")

        # Process card effects
        if "Advance to Go" in card:
            player.position = 0
            player.receive(200)
            # print(f"{colors['success']}{player.name} advances to Go and collects $200.{colors['reset']}")
        elif "Go to Jail" in card:
            player.go_to_jail()
            # print(f"{colors['info']}{player.name} goes to jail.{colors['reset']}")
        elif (
            "Collect" in card or "Receive" in card or "get" in card or "matures" in card
        ):
            # Extract amount
            amount = int("".join(filter(str.isdigit, card)))
            player.receive(amount)
            # print(f"{colors['success']}{player.name} receives ${amount}.{colors['reset']}")
        elif "Pay" in card or "fee" in card or "fine" in card:
            # Extract amount
            amount = int("".join(filter(str.isdigit, card)))
            if player.pay(amount):
                return
                # print(f"{colors['info']}{player.name} pays ${amount}.{colors['reset']}")
            else:
                # print(f"{colors['error']}{player.name} doesn't have enough money!{colors['reset']}")
                self.check_bankruptcy(player, amount)
        elif "Get Out of Jail Free" in card:
            player.jail_free_cards += 1
            # print(f"{colors['success']}{player.name} got a Get Out of Jail Free card.{colors['reset']}")
        # Additional card effects would be implemented here

    def handle_special_space(self, player, space_name):
        if space_name == "Go":
            # Already handled in move logic
            pass
        elif space_name == "Almänning":
            self.handle_card(player, "Almänning")
        elif space_name == "Inkomstskatt":
            tax = min(
                200, int(player.money * 0.1)
            )  # Pay $200 or 10%, whichever is less
            if player.pay(tax):
                # print(f"{colors['info']}{player.name} pays ${tax} in Income Tax.{colors['reset']}")
                return
            else:

                # print(f"{colors['error']}{player.name} doesn't have enough money to pay Income Tax!{colors['reset']}")
                self.check_bankruptcy(player, tax)
        elif space_name == "Chans":
            self.handle_card(player, "C")
        elif space_name == "Jail / Just Visiting":
            return
            # print(f"{colors['info']}{player.name} is just visiting jail.{colors['reset']}")
        elif space_name == "Fri Parkering":
            return
            # print(f"{colors['info']}{player.name} landed on Fri Parkering.{colors['reset']}")
        elif space_name == "Gå i fängelse":
            player.go_to_jail()
            # print(f"{colors['info']}{player.name} goes to jail.{colors['reset']}")
        elif space_name == "Lyxskatt":
            if player.pay(100):
                # print(f"{colors['info']}{player.name} pays $100 in Luxury Tax.{colors['reset']}")
                return
            else:
                # print(f"{colors['error']}{player.name} doesn't have enough money to pay Luxury Tax!{colors['reset']}")
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
                        # print(f"{colors['info']}{player.name} paid $50 after third turn in jail.{colors['reset']}")
                    return True  # Player's turn ends

        return False  # Not in jail

    def build_house_bot(self, player):
        """build house for bot"""
        property = player.bot.decide_house_purchases()
        if property and type:
            if property and type:
                cost = property.house_price
                if player.pay(cost):
                    # print(f"{colors['success']}Added a house/hotel to {property.name}!{colors['reset']}")
                    property.add_house_or_hotel()
                    
                    # Track house/hotel statistics
                    if hasattr(property, "houses") and property.houses > 0:
                        game_stats["avg_houses_per_player"][player.name] += 1
                    if hasattr(property, "hotel") and property.hotel:
                        game_stats["avg_hotels_per_player"][player.name] += 1
                        # Subtract houses when converting to hotel (typically 4 houses become 1 hotel)
                        game_stats["avg_houses_per_player"][player.name] -= 4
                # Check if property already has a hotel
                else:
                    # print(f"{colors['error']}Not enough money to buy a {type} (${cost}).{colors['reset']}")
                    return

    def play_turn(self):
        player = self.players[self.current_player_idx]
        # os.system('cls' if os.name == 'nt' else 'clear')

        if player.bankrupt:
            self.next_player()
            return
        # player.display_status(self.board)

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

        # Check for monopolies after property acquisition
        self.check_monopolies(player)

        # Check if game is over due to bankruptcy
        if self.game_over:
            return

        player.bot.make_move()
        self.turn_count += 1
        self.next_player()
        
    def check_monopolies(self, player):
        """Check if player has acquired any new monopolies and update statistics"""
        # Group properties by color
        color_groups = {}
        for prop in player.properties:
            if hasattr(prop, "color"):
                if prop.color not in color_groups:
                    color_groups[prop.color] = []
                color_groups[prop.color].append(prop)
        
        # Check each color group
        monopoly_count = 0
        for color, properties in color_groups.items():
            # Get total properties of this color on the board
            total_in_color = 0
            for space in self.board.spaces:
                if isinstance(space, Property) and hasattr(space, "color") and space.color == color:
                    total_in_color += 1
            
            # Check if player owns all properties of this color
            if len(properties) == total_in_color:
                monopoly_count += 1
        
        # Update monopoly statistics
        if monopoly_count > 0 and player.name in game_stats["monopolies_owned"]:
            # Track the maximum number of monopolies this player has had
            current_monopolies = game_stats["monopolies_owned"][player.name]
            if monopoly_count > current_monopolies:
                game_stats["monopolies_owned"][player.name] = monopoly_count

    def decide_winner(self):
        # print(f"{colors['title']}\n=== GAME REACHED 500 TURNS LIMIT ==={colors['reset']}")

        # Find the player with the most money
        active_players = [p for p in self.players if not p.bankrupt]
        if active_players:
            self.winner = max(active_players, key=lambda p: p.money)

            # Calculate total value (money + properties)
            player_values = {}
            for p in active_players:
                total_value = p.money
                for prop in p.properties:
                    total_value += prop.price
                    if hasattr(prop, "houses") and prop.houses > 0:
                        total_value += prop.house_price * prop.houses
                    if hasattr(prop, "hotel") and prop.hotel:
                        total_value += prop.house_price * 5
                player_values[p.name] = total_value

            """print(f"{colors['title']}\n=== FINAL STANDINGS ==={colors['reset']}")
            for name, value in sorted(player_values.items(), key=lambda x: x[1], reverse=True):
                print(f"{colors['info']}{name}: ${value}{colors['reset']}")"""

            print(
                f"{colors['title']}\n=== GAME REACHED TURN LIMIT ==={colors['reset']}"
            )
            print(
                f"{colors['success']}{self.winner.name} WINS THE GAME WITH ${self.winner.money}!{colors['reset']}"
            )
            if game_stats["wins_by_player"]:
                game_stats["wins_by_player"][self.winner.name] += 1
                game_stats["game_over_500_turns"] += 1
            self.game_over = True
            return

    def play_game(self):
        # print(f"{colors['info']}Welcome to Monopoly!{colors['reset']}")

        turns = 0

        while not self.game_over:
            # Clear the screen
            # os.system('cls' if os.name == 'nt' else 'clear')

            self.play_turn()

            if turns >= 500:
                if game_stats["game_over_500_turns"]:
                    game_stats["game_over_500_turns"] += 1
                self.decide_winner()

            if turns % 100 == 0 and turns != 0:
                """input(f"{colors['prompt']}Display statistics? (y/n): {colors['reset']}").lower()
                display_statistics(self) # Display statistics if player chooses to
                input(f"{colors['prompt']}Press enter to continue...{colors['reset']}")
                """
            turns += 1

        # Add at the end:
        result = {
            "turn_count": self.turn_count,
            "player_count": len(self.players),
            "winner": self.winner.name if self.winner else None,
        }

        return result


            property_count = len(player.properties)
            house_count = sum(
                p.houses for p in player.properties if hasattr(p, "houses")
            )
            hotel_count = sum(
                1 for p in player.properties if hasattr(p, "hotel") and p.hotel
            )
            mortgaged_count = sum(
                1 for p in player.properties if p.status == PropertyStatus.MORTGAGED
            )

            print(
                f"{colors['info']}{player.name}: {property_count} properties, {house_count} houses, {hotel_count} hotels, {mortgaged_count} mortgaged, ${player.money}{colors['reset']}"
            )

        # display all bankrupt players
        bankrupt_players = [p for p in self.players if p.bankrupt]
        if bankrupt_players:
            print(f"{colors['title']}\n=== BANKRUPT PLAYERS ==={colors['reset']}")
            for player in bankrupt_players:
                print(f"{colors['error']}{player.name} is bankrupt.{colors['reset']}")


def select_parameters(self):
    print(f"{self.colors['title']}=== SELECT BOT PARAMETERS ===")

    print(f"{self.colors['info']}Enter custom parameters:")
    for i, param in enumerate(bots_parameters):
        print(f"{self.colors['info']}Bot {i + 1}:")
        for key in param:
            value = input(
                f"{self.colors['prompt']}{key} (default {param[key]}): {self.colors['reset']}"
            )
            if value:
                bots_parameters[i][key] = float(value)
            else:
                print(f"{self.colors['info']}Using default value for {key}: {param[key]}")

def main():
    # Global variable to track game statistics
    global game_stats

    try:
        bot_count_input = input(f"{colors['prompt']}Enter number of bots (0-8): {colors['reset']}")
        bot_count = int(bot_count_input) if bot_count_input else 2
        if input(f"{colors['prompt']}Use custom parameters? (y/n): {colors['reset']}").lower() == "y":
            select_parameters()
        
        neural_bot_count_input = input(
                f"{colors['prompt']}how many should be neural bots? (0-{bot_count_input}): {colors['reset']}"
            )
        neural_bot_count = int(neural_bot_count_input) if neural_bot_count_input else 0
        
    except ValueError:
        print(f"{colors['error']}Invalid input. Please enter a number.{colors['reset']}")
        main()

    if bot_count < 2 or bot_count > 8:
        print(
            f"{colors['error']}Invalid number of bots. Please enter a number between 0 and 8.{colors['reset']}"
        )
        return

    # Initialize all statistics for each bot
    for i in range(bot_count):
        bot_name = f"Bot {i+1}"
        # Basic stats
        game_stats["wins_by_player"][bot_name] = 0
        game_stats["bankrupt_count"][bot_name] = 0
        game_stats["turns"][bot_name] = 0
        
        # Advanced stats
        game_stats["avg_houses_per_player"][bot_name] = 0
        game_stats["avg_hotels_per_player"][bot_name] = 0
        game_stats["monopolies_owned"][bot_name] = 0
        game_stats["avg_rent_collected"][bot_name] = 0
        game_stats["total_rent_collected"][bot_name] = 0
        game_stats["property_acquisitions"][bot_name] = 0
        game_stats["trades_made"][bot_name] = 0
        game_stats["trades_accepted"][bot_name] = 0
        game_stats["trades_rejected"][bot_name] = 0
        game_stats["most_valuable_property"][bot_name] = {"name": "None", "rent": 0}
        game_stats["most_owned_property_type"][bot_name] = {}

    for i in range(num_games):  # play 100 games
        print(f"{colors['info']}Game {i+1} of 100{colors['reset']}")
        game = MonopolyGame(
            bot_count=bot_count,
            neural_bot_count=neural_bot_count,
            bots_parameters=bots_parameters,
            game_count=i,
        )
        game.play_game()
        # Update statistics
        game_stats["games_played"] += 1

    # save_game_history()
    display_game_statistics(game_stats)

    print(f"{colors['title']}\nGame over!{colors['reset']}")


# Run the game
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        os.system("cls" if os.name == "nt" else "clear")
        print(f"{colors['error']}\nGame cancelled by user.{colors['reset']}")
        print(
            f"{colors['title']}Monopoly game ended. Thank you for playing!{colors['reset']}"
        )
        ##print the stats for everyone
