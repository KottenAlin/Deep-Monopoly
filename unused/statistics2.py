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
