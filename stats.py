from enum import Enum
from game_models import Property, PropertyColor, PropertyStatus

def display_statistics(game):
    # Display a comprehensive property and building report
    print(f"\n{game.colors['title']}=== PROPERTY AND BUILDING REPORT ===")
    active_players = [p for p in game.players if not p.bankrupt]

    # Count total houses and hotels on the board
    total_houses = 0
    total_hotels = 0
    for space in game.board.spaces:
        if isinstance(space, Property):
            if hasattr(space, 'houses') and space.houses > 0:
                total_houses += space.houses
            if hasattr(space, 'hotel') and space.hotel:
                total_hotels += 1

    print(f"{game.colors['info']}Total buildings on board: {game.colors['success']}{total_houses} houses, {total_hotels} hotels")

    # Display all properties grouped by color
    color_groups = {}
    for space in game.board.spaces:
        if isinstance(space, Property):
            if space.color not in color_groups:
                color_groups[space.color] = []
            color_groups[space.color].append(space)

    # Print properties by color group
    for color, properties in color_groups.items():
        print(f"\n{game.colors['title']}{color.value} Properties:")
        for prop in properties:
            owner_info = f"Owned by {game.colors['player']}{prop.owner.name}" if prop.owner else f"{game.colors['info']}Unowned"
            status_info = f" ({game.colors['warning']}Mortgaged{game.colors['reset']})" if prop.status == PropertyStatus.MORTGAGED else ""
            
            building_info = ""
            if hasattr(prop, 'houses') and prop.houses > 0:
                building_info = f", {prop.houses} houses"
            if hasattr(prop, 'hotel') and prop.hotel:
                building_info = f", {game.colors['success']}Hotel"
                
            rent_info = f", Current rent: {game.colors['rent']}${prop.calculate_rent()}" if prop.owner else ""
            print(f"{game.colors['property']}  {prop.name} - {game.colors['money']}${prop.price} - {owner_info}{status_info}{building_info}{rent_info}")

    # Print player property summaries
    print(f"\n{game.colors['title']}Player Property Summaries:")
    for player in active_players:
        property_count = len(player.properties)
        house_count = sum(p.houses for p in player.properties if hasattr(p, 'houses'))
        hotel_count = sum(1 for p in player.properties if hasattr(p, 'hotel') and p.hotel)
        mortgaged_count = sum(1 for p in player.properties if p.status == PropertyStatus.MORTGAGED)
        
        print(f"{game.colors['player']}{player.name}: {property_count} properties, {house_count} houses, {hotel_count} hotels, {mortgaged_count} mortgaged, {game.colors['money']}${player.money}")

    #display all bankrupt players
    bankrupt_players = [p for p in game.players if p.bankrupt]
    if bankrupt_players:
        print(f"\n{game.colors['title']}=== BANKRUPT PLAYERS ===")
        for player in bankrupt_players:
            print(f"{game.colors['error']}{player.name} is bankrupt.")
            
    if input(f"{game.colors['prompt']}Display extended statistics? (y/n): {game.colors['reset']}").lower() == 'y':
        display_extended_statistics(game)
        
def display_extended_statistics(game):
    """Display more comprehensive game statistics."""
    active_players = [p for p in game.players if not p.bankrupt]
    bankrupt_players = [p for p in game.players if p.bankrupt]
    
    print(f"\n{game.colors['title']}=== EXTENDED GAME STATISTICS ===\n")
    
    # Player Rankings by Net Worth
    print(f"{game.colors['title']}PLAYER RANKINGS BY NET WORTH:")
    player_values = {}
    for p in game.players:
        total_value = p.money
        for prop in p.properties:
            # Don't add mortgaged properties to net worth
            if prop.status != PropertyStatus.MORTGAGED:
                total_value += prop.price
                if hasattr(prop, 'houses') and prop.houses > 0:
                    total_value += prop.house_price * prop.houses
                if hasattr(prop, 'hotel') and prop.hotel:
                    total_value += prop.house_price * 5
            else:
                # For mortgaged properties, add the mortgage value they could recover
                total_value += 0 #prop.price / 2  # Mortgage value is typically half of property price
        player_values[p.name] = total_value
    
    # Sort players by net worth and display ranking
    for i, (name, value) in enumerate(sorted(player_values.items(), key=lambda x: x[1], reverse=True)):
        status = f"{game.colors['success']}ACTIVE" if next((p for p in active_players if p.name == name), None) else f"{game.colors['error']}BANKRUPT"
        print(f"{i+1}. {game.colors['player']}{name}: {game.colors['money']}${value:.2f} ({status}{game.colors['reset']})")
    
    # Property Statistics
    print(f"\n{game.colors['title']}PROPERTY STATISTICS:")
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
    
    for space in game.board.spaces:
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
    
    print(f"{game.colors['info']}Total Properties: {property_stats['total']}")
    print(f"{game.colors['info']}Owned: {game.colors['success']}{property_stats['owned']} ({property_stats['owned']/property_stats['total']*100:.1f}%)")
    print(f"{game.colors['info']}Unowned: {game.colors['warning']}{property_stats['unowned']}")
    print(f"{game.colors['info']}Mortgaged: {game.colors['warning']}{property_stats['mortgaged']} ({property_stats['mortgaged']/property_stats['owned']*100:.1f}% of owned)")
    print(f"{game.colors['info']}Properties with Houses/Hotels: {game.colors['success']}{property_stats['developed']}")
    print(f"{game.colors['info']}Total Houses on Board: {game.colors['success']}{property_stats['houses']}")
    print(f"{game.colors['info']}Total Hotels on Board: {game.colors['success']}{property_stats['hotels']}")
    
    if most_valuable_prop:
        owner_name = most_valuable_prop.owner.name if most_valuable_prop.owner else "None"
        print(f"\n{game.colors['info']}Most Valuable Property: {game.colors['property']}{most_valuable_prop.name} (Owned by: {game.colors['player']}{owner_name})")
        print(f"{game.colors['info']}Current Rent: {game.colors['rent']}${highest_rent}")
    
    # Most developed color group
    if color_development:
        most_dev_color = max(color_development.items(), 
                            key=lambda x: x[1]["houses"] + x[1]["hotels"]*5)
        print(f"\n{game.colors['info']}Most Developed Color Group: {game.colors['property']}{most_dev_color[0].value}")
        print(f"{game.colors['info']}Development: {game.colors['success']}{most_dev_color[1]['houses']} houses, {most_dev_color[1]['hotels']} hotels")
    
    # Monopoly statistics
    print(f"\n{game.colors['title']}MONOPOLY STATISTICS:")
    monopolies = {}
    for player in active_players:
        player_monopolies = []
        for color in set(p.color for p in player.properties if p.color not in [PropertyColor.RAILROAD, PropertyColor.UTILITY]):
            owned_props = [p for p in player.properties if p.color == color]
            total_in_color = sum(1 for p in game.board.spaces if isinstance(p, Property) and p.color == color)
            if len(owned_props) == total_in_color:
                player_monopolies.append(color.value)
        
        if player_monopolies:
            monopolies[player.name] = player_monopolies
    
    if monopolies:
        for player_name, colors in monopolies.items():
            print(f"{game.colors['player']}{player_name} has monopoly on: {game.colors['property']}{', '.join(colors)}")
    else:
        print(f"{game.colors['info']}No player has a monopoly on any color group.")
    
    # Special category ownership
    print(f"\n{game.colors['title']}SPECIAL CATEGORY OWNERSHIP:")
    for category in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
        for player in active_players:
            count = sum(1 for p in player.properties if p.color == category)
            if count > 0:
                print(f"{game.colors['player']}{player.name} owns {game.colors['success']}{count} {game.colors['property']}{category.value}s")
    
    # Money distribution
    if active_players:
        print(f"\n{game.colors['title']}MONEY DISTRIBUTION:")
        total_money = sum(p.money for p in game.players)
        for player in game.players:
            status = f"{game.colors['success']}Active" if not player.bankrupt else f"{game.colors['error']}Bankrupt"
            percentage = (player.money / total_money * 100) if total_money > 0 else 0
            print(f"{game.colors['player']}{player.name}: {game.colors['money']}${player.money} ({percentage:.1f}% of total) - {status}")
    
    # game evaluation
    game_evaluation(game)
    
    input(f"{game.colors['prompt']}Press Enter to continue...{game.colors['reset']}")

def game_evaluation(game):
    """Evaluate each player's chances of winning based on game state."""
    print(f"\n{game.colors['title']}=== GAME WINNING PROBABILITY ANALYSIS ===\n")
    
    active_players = [p for p in game.players if not p.bankrupt]
    if len(active_players) <= 1:
        if active_players:
            print(f"{game.colors['success']}{active_players[0].name} is the only player remaining and will win!")
        else:
            print(f"{game.colors['error']}No active players left in the game.")
        return
    
    # Calculate win probabilities
    player_evaluations, game_progress, game_phase = calculate_win_probabilities(game)
    
    # Display results
    display_win_probabilities(game, player_evaluations, game_progress, game_phase)

def calculate_win_probabilities(game):
    """Calculate win and bankruptcy probabilities for all active players."""
    player_evaluations = {}
    active_players = [p for p in game.players if not p.bankrupt]
    
    # Calculate game progress based on total properties owned and developed
    total_properties = sum(1 for space in game.board.spaces if isinstance(space, Property))
    owned_properties = sum(1 for space in game.board.spaces 
                            if isinstance(space, Property) and space.owner is not None)
    developed_properties = sum(1 for space in game.board.spaces
                                if isinstance(space, Property) and hasattr(space, 'houses') 
                                and (space.houses > 0 or (hasattr(space, 'hotel') and space.hotel)))
    
    game_progress = (owned_properties / total_properties) * 0.6 + (developed_properties / total_properties) * 0.4
    game_phase = "Early" if game_progress < 0.3 else "Mid" if game_progress < 0.7 else "Late"
    
    total_net_worth = 0
    
    for player in active_players:
        net_worth = player.money
        monopoly_count = 0
        
        # Count monopolies
        color_counts = {}
        for prop in player.properties:
            if prop.color not in color_counts:
                color_counts[prop.color] = 0
            color_counts[prop.color] += 1
            
            # Add property value only if not mortgaged
            if prop.status != PropertyStatus.MORTGAGED:
                net_worth += prop.price
                if hasattr(prop, 'houses') and prop.houses > 0:
                    net_worth += prop.houses * prop.house_price
                if hasattr(prop, 'hotel') and prop.hotel:
                    net_worth += 5 * prop.house_price
            else:
                # For mortgaged properties, add the mortgage value
                net_worth += prop.price / 2
        
        # Check for monopolies
        for color, count in color_counts.items():
            total_in_color = sum(1 for p in game.board.spaces 
                                if isinstance(p, Property) and p.color == color)
            if count == total_in_color and color not in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
                monopoly_count += 1
        
        # Store player evaluation data
        player_evaluations[player] = {
            'net_worth': net_worth,
            'monopoly_count': monopoly_count,
            'railroad_count': sum(1 for p in player.properties if p.color == PropertyColor.RAILROAD),
            'utility_count': sum(1 for p in player.properties if p.color == PropertyColor.UTILITY),
            'cash_ratio': player.money / net_worth if net_worth > 0 else 0
        }
        total_net_worth += net_worth
    
    # Calculate win probability based on different factors and game phase
    for player, eval_data in player_evaluations.items():
        # Base probability on net worth
        net_worth_factor = eval_data['net_worth'] / total_net_worth if total_net_worth > 0 else 1/len(active_players)
        
        # Adjust for monopolies - more important in mid to late game
        monopoly_factor = 1 + (eval_data['monopoly_count'] * 0.25 * min(game_progress * 2, 1))
        
        # Cash ratio - important in early game, less so later
        cash_factor = 1 + (eval_data['cash_ratio'] * 0.1 * (1 - game_progress))
        
        # Railroad and utility factor - more important in early to mid game
        special_factor = 1 + (eval_data['railroad_count'] * 0.05 + eval_data['utility_count'] * 0.03) * (1 - game_progress)
        
        # Calculate final win probability
        win_probability = (net_worth_factor * monopoly_factor * cash_factor * special_factor)**2
        
        # Store for normalization
        player_evaluations[player]['raw_probability'] = win_probability
        
        # Calculate bankruptcy risk factors
        bankruptcy_risk = 0
        # Low cash is a major risk factor
        if eval_data['cash_ratio'] < 0.2:
            bankruptcy_risk += (0.2 - eval_data['cash_ratio']) * 5
        # Few properties means fewer options to mortgage
        if len(player.properties) < 3:
            bankruptcy_risk += (3 - len(player.properties)) * 0.1
        # Already mortgaged properties indicate financial trouble
        mortgaged_count = sum(1 for p in player.properties if p.status == PropertyStatus.MORTGAGED)
        if mortgaged_count > 0:
            bankruptcy_risk += mortgaged_count * 0.15
        # Lower net worth relative to others increases bankruptcy risk
        if net_worth_factor < 0.25:  # Below 25% of average
            bankruptcy_risk += (0.25 - net_worth_factor) * 2
            
        # Store bankruptcy risk
        player_evaluations[player]['bankruptcy_risk'] = min(bankruptcy_risk, 1.0)  # Cap at 100%
    
    # Normalize probabilities to sum to 100%
    total_raw_prob = sum(data['raw_probability'] for data in player_evaluations.values())
    total_bankruptcy_risk = sum(data['bankruptcy_risk'] for data in player_evaluations.values())
    
    if total_raw_prob > 0:
        for player, data in player_evaluations.items():
            data['win_probability'] = (data['raw_probability'] / total_raw_prob) * 100
    else:
        # Equal probability if calculation resulted in 0
        for player, data in player_evaluations.items():
            data['win_probability'] = 100 / len(player_evaluations)
    
    # Normalize bankruptcy risk
    if total_bankruptcy_risk > 0:
        for player, data in player_evaluations.items():
            data['bankruptcy_probability'] = (data['bankruptcy_risk'] / total_bankruptcy_risk) * 100
    else:
        for player, data in player_evaluations.items():
            data['bankruptcy_probability'] = 100 / len(player_evaluations)
            
    # Add total net worth to evaluations dictionary for later use
    player_evaluations['total_net_worth'] = total_net_worth
    
    return player_evaluations, game_progress, game_phase

def update_game_probabilities_with_winner(game, winner):
    """Update win probabilities after the game has ended with a known winner."""
    print(f"\n{game.colors['title']}=== FINAL GAME ANALYSIS ===\n")
    
    # Get the regular probability calculation
    player_evaluations, game_progress, game_phase = calculate_win_probabilities(game)
    
    # Store the original probabilities for comparison
    for player in player_evaluations:
        if player != 'total_net_worth':  # Skip the non-player entry
            player_evaluations[player]['original_win_probability'] = player_evaluations[player]['win_probability']
    
    # Set actual probabilities (100% for winner, 0% for others)
    for player in player_evaluations:
        if player != 'total_net_worth':  # Skip the non-player entry
            if player == winner:
                player_evaluations[player]['win_probability'] = 100.0
            else:
                player_evaluations[player]['win_probability'] = 0.0
    
    # Display results
    print(f"{game.colors['success']}The winner is: {game.colors['player']}{winner.name}!")
    print(f"\n{game.colors['title']}Comparing Predictions vs. Reality:\n")
    
    # Display players sorted by original probability
    sorted_players = sorted(
        [(p, data) for p, data in player_evaluations.items() if p != 'total_net_worth'],
        key=lambda x: x[1]['original_win_probability'], 
        reverse=True
    )
    
    for i, (player, data) in enumerate(sorted_players):
        actual = "Winner" if player == winner else "Lost"
        accuracy = "Correct" if (player == winner and data['original_win_probability'] > 50) or \
                              (player != winner and data['original_win_probability'] < 50) else "Incorrect"
        
        accuracy_color = game.colors['success'] if accuracy == "Correct" else game.colors['error']
        actual_color = game.colors['success'] if actual == "Winner" else game.colors['warning']
        
        print(f"{i+1}. {game.colors['player']}{player.name}:")
        print(f"   Predicted: {game.colors['info']}{data['original_win_probability']:.1f}% chance to win")
        print(f"   Actual: {actual_color}{actual}")
        print(f"   Prediction was: {accuracy_color}{accuracy}\n")
    
    # Calculate overall prediction accuracy
    correct_predictions = sum(1 for p, data in sorted_players if 
                            (p == winner and data['original_win_probability'] > 50) or 
                            (p != winner and data['original_win_probability'] < 50))
    
    accuracy_percentage = (correct_predictions / len(sorted_players)) * 100 if sorted_players else 0
    
    print(f"{game.colors['title']}Overall Prediction Accuracy: {game.colors['info']}{accuracy_percentage:.1f}%")
    
    # If winner was not the highest probability player, explain why
    if sorted_players and sorted_players[0][0] != winner:
        print(f"\n{game.colors['warning']}The model predicted {sorted_players[0][0].name} " + 
              f"to win with {sorted_players[0][1]['original_win_probability']:.1f}% probability.")
        print(f"{game.colors['info']}Possible factors for the unexpected outcome:")
        print(f" - Luck in dice rolls or card draws")
        print(f" - Strategic decisions not captured by the model")
        print(f" - Late-game property or cash exchanges")
    
    return player_evaluations



def display_win_probabilities(game, player_evaluations, game_progress, game_phase):
    """Display the calculated win and bankruptcy probabilities."""
    total_net_worth = player_evaluations.pop('total_net_worth', 0)
    
    print(f"{game.colors['info']}Game Progress: {game.colors['success']}{game_progress*100:.1f}% ({game_phase} game)\n")
    
    # Display results sorted by win probability
    sorted_players = sorted(player_evaluations.items(), key=lambda x: x[1]['win_probability'], reverse=True)
    
    for i, (player, data) in enumerate(sorted_players):
        # Calculate color for probability
        if data['win_probability'] > 50:
            prob_color = game.colors['success']
        elif data['win_probability'] > 25:
            prob_color = game.colors['warning']
        else:
            prob_color = game.colors['error']
            
        print(f"{i+1}. {game.colors['player']}{player.name}: {prob_color}{data['win_probability']:.1f}% chance to win")
        print(f"   Net Worth: {game.colors['money']}${data['net_worth']:.0f} " + 
                f"({data['net_worth']/total_net_worth*100:.1f}% of total)")
        
        # Display bankruptcy probability
        bankruptcy_color = game.colors['success'] if data['bankruptcy_probability'] < 25 else (
                            game.colors['warning'] if data['bankruptcy_probability'] < 50 else game.colors['error'])
        print(f"   Bankruptcy Risk: {bankruptcy_color}{data['bankruptcy_probability']:.1f}%")
        
        # Show key factors
        factors = []
        if data['monopoly_count'] > 0:
            factors.append(f"{data['monopoly_count']} monopolies")
        if data['railroad_count'] > 0:
            factors.append(f"{data['railroad_count']} railroads")
        if data['cash_ratio'] > 0.3:
            factors.append(f"good cash reserves ({data['cash_ratio']*100:.0f}%)")
        elif data['cash_ratio'] < 0.1:
            factors.append(f"low cash ({data['cash_ratio']*100:.0f}%)")
        
        if factors:
            print(f"   Key factors: {game.colors['info']}{', '.join(factors)}")
        print()
    
    # Display players sorted by bankruptcy risk
    print(f"\n{game.colors['title']}=== BANKRUPTCY RISK ANALYSIS ===\n")
    bankruptcy_sorted = sorted(player_evaluations.items(), key=lambda x: x[1]['bankruptcy_probability'], reverse=True)
    
    print(f"{game.colors['info']}Players most likely to go bankrupt next:")
    for i, (player, data) in enumerate(bankruptcy_sorted[:3]):  # Show top 3 at risk
        bankruptcy_color = game.colors['success'] if data['bankruptcy_probability'] < 25 else (
                            game.colors['warning'] if data['bankruptcy_probability'] < 50 else game.colors['error'])
        print(f"{i+1}. {game.colors['player']}{player.name}: {bankruptcy_color}{data['bankruptcy_probability']:.1f}% risk")
        print(f"   Cash: {game.colors['money']}${player.money} ({data['cash_ratio']*100:.0f}% of assets)")
        
        # Additional risk factors
        mortgaged = sum(1 for p in player.properties if p.status == PropertyStatus.MORTGAGED)
        if mortgaged > 0:
            print(f"   {game.colors['warning']}Has {mortgaged} mortgaged properties")