from enum import Enum
from game_models import Property, PropertyColor, PropertyStatus
import torch
import numpy as np
import torch.nn as nn
import torch.optim as optim
import pickle

from variables import colors, bots_parameters



game_history = [[]]

def display_statistics(game):
    # Display a comprehensive property and building report
    print(f"\n{colors['title']}=== PROPERTY AND BUILDING REPORT ===")
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

    print(f"{colors['info']}Total buildings on board: {colors['success']}{total_houses} houses, {total_hotels} hotels")

    # Display all properties grouped by color
    color_groups = {}
    for space in game.board.spaces:
        if isinstance(space, Property):
            if space.color not in color_groups:
                color_groups[space.color] = []
            color_groups[space.color].append(space)

    # Print properties by color group
    for color, properties in color_groups.items():
        print(f"\n{colors['title']}{color.value} Properties:")
        for prop in properties:
            owner_info = f"Owned by {colors['player']}{prop.owner.name}" if prop.owner else f"{colors['info']}Unowned"
            status_info = f" ({colors['warning']}Mortgaged{colors['reset']})" if prop.status == PropertyStatus.MORTGAGED else ""
            
            building_info = ""
            if hasattr(prop, 'houses') and prop.houses > 0:
                building_info = f", {prop.houses} houses"
            if hasattr(prop, 'hotel') and prop.hotel:
                building_info = f", {colors['success']}Hotel"
                
            rent_info = f", Current rent: {colors['rent']}${prop.calculate_rent()}" if prop.owner else ""
            print(f"{colors['property']}  {prop.name} - {colors['money']}${prop.price} - {owner_info}{status_info}{building_info}{rent_info}")

    # Print player property summaries
    print(f"\n{colors['title']}Player Property Summaries:")
    for player in active_players:
        property_count = len(player.properties)
        house_count = sum(p.houses for p in player.properties if hasattr(p, 'houses'))
        hotel_count = sum(1 for p in player.properties if hasattr(p, 'hotel') and p.hotel)
        mortgaged_count = sum(1 for p in player.properties if p.status == PropertyStatus.MORTGAGED)
        
        print(f"{colors['player']}{player.name}: {property_count} properties, {house_count} houses, {hotel_count} hotels, {mortgaged_count} mortgaged, {colors['money']}${player.money}")

    #display all bankrupt players
    bankrupt_players = [p for p in game.players if p.bankrupt]
    if bankrupt_players:
        print(f"\n{colors['title']}=== BANKRUPT PLAYERS ===")
        for player in bankrupt_players:
            print(f"{colors['error']}{player.name} is bankrupt.")
            
    if input(f"{colors['prompt']}Display extended statistics? (y/n): {colors['reset']}").lower() == 'y':
        display_extended_statistics(game)
        
def display_extended_statistics(game):
    """Display more comprehensive game statistics."""
    global colors
    
    active_players = [p for p in game.players if not p.bankrupt]
    bankrupt_players = [p for p in game.players if p.bankrupt]
    
    print(f"\n{colors['title']}=== EXTENDED GAME STATISTICS ===\n")
    
    # Player Rankings by Net Worth
    print(f"{colors['title']}PLAYER RANKINGS BY NET WORTH:")
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
        status = f"{colors['success']}ACTIVE" if next((p for p in active_players if p.name == name), None) else f"{colors['error']}BANKRUPT"
        print(f"{i+1}. {colors['player']}{name}: {colors['money']}${value:.2f} ({status}{colors['reset']})")
    
    # Property Statistics
    print(f"\n{colors['title']}PROPERTY STATISTICS:")
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
    
    print(f"{colors['info']}Total Properties: {property_stats['total']}")
    print(f"{colors['info']}Owned: {colors['success']}{property_stats['owned']} ({property_stats['owned']/property_stats['total']*100:.1f}%)")
    print(f"{colors['info']}Unowned: {colors['warning']}{property_stats['unowned']}")
    print(f"{colors['info']}Mortgaged: {colors['warning']}{property_stats['mortgaged']} ({property_stats['mortgaged']/property_stats['owned']*100:.1f}% of owned)")
    print(f"{colors['info']}Properties with Houses/Hotels: {colors['success']}{property_stats['developed']}")
    print(f"{colors['info']}Total Houses on Board: {colors['success']}{property_stats['houses']}")
    print(f"{colors['info']}Total Hotels on Board: {colors['success']}{property_stats['hotels']}")
    
    if most_valuable_prop:
        owner_name = most_valuable_prop.owner.name if most_valuable_prop.owner else "None"
        print(f"\n{colors['info']}Most Valuable Property: {colors['property']}{most_valuable_prop.name} (Owned by: {colors['player']}{owner_name})")
        print(f"{colors['info']}Current Rent: {colors['rent']}${highest_rent}")
    
    # Most developed color group
    if color_development:
        most_dev_color = max(color_development.items(), 
                            key=lambda x: x[1]["houses"] + x[1]["hotels"]*5)
        print(f"\n{colors['info']}Most Developed Color Group: {colors['property']}{most_dev_color[0].value}")
        print(f"{colors['info']}Development: {colors['success']}{most_dev_color[1]['houses']} houses, {most_dev_color[1]['hotels']} hotels")
    
    # Monopoly statistics
    print(f"\n{colors['title']}MONOPOLY STATISTICS:")
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
        for player_name, monopoly_colors in monopolies.items():
            print(f"{colors['player']}{player_name} has monopoly on: {colors['property']}{', '.join(monopoly_colors)}")
    else:
        print(f"{colors['info']}No player has a monopoly on any color group.")
    
    # Special category ownership
    print(f"\n{colors['title']}SPECIAL CATEGORY OWNERSHIP:")
    for category in [PropertyColor.RAILROAD, PropertyColor.UTILITY]:
        for player in active_players:
            count = sum(1 for p in player.properties if p.color == category)
            if count > 0:
                print(f"{colors['player']}{player.name} owns {colors['success']}{count} {colors['property']}{category.value}s")
    
    # Money distribution
    if active_players:
        print(f"\n{colors['title']}MONEY DISTRIBUTION:")
        total_money = sum(p.money for p in game.players)
        for player in game.players:
            status = f"{colors['success']}Active" if not player.bankrupt else f"{colors['error']}Bankrupt"
            percentage = (player.money / total_money * 100) if total_money > 0 else 0
            print(f"{colors['player']}{player.name}: {colors['money']}${player.money} ({percentage:.1f}% of total) - {status}")
    
    # game evaluation
    game_evaluation(game)
    
    input(f"{colors['prompt']}Press Enter to continue...{colors['reset']}")

def record_game_history(game, game_count=0):
    """Record game history for future analysis."""
    if game_count >= len(game_history):
        game_history.append([])
    game_history[game_count].append(game)

def save_game_history(filename="game_history.pkl"):
    """Save game history to a file using pickle."""

    with open(filename, 'wb') as f:
        pickle.dump(game_history, f)
        

def load_game_history(filename="game_history.pkl"):
    """Load game history from a file using pickle."""
    global game_history
    try:
        with open(filename, 'rb') as f:
            game_history = pickle.load(f)
        print(f"Successfully loaded game history with {sum(len(games) for games in game_history)} total game states.")
        return game_history
    except FileNotFoundError:
        print(f"File {filename} not found. Starting with empty game history.")
        game_history = [[]]
        return game_history
    '''except Exception as e:
        print(f"Error loading game history: {e}")
        game_history = [[]]
        return game_history'''

def game_evaluation(game):
    """Evaluate each player's chances of winning based on game state."""
    print(f"\n{colors['title']}=== GAME WINNING PROBABILITY ANALYSIS ===\n")
    
    active_players = [p for p in game.players if not p.bankrupt]
    if len(active_players) <= 1:
        if active_players:
            print(f"{colors['success']}{active_players[0].name} is the only player remaining and will win!")
        else:
            print(f"{colors['error']}No active players left in the game.")
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
        # Fewer monopolies increase bankruptcy risk
        if eval_data['monopoly_count'] == 0:
            bankruptcy_risk += 0.5  # No monopolies is a significant risk
        else:
            bankruptcy_risk += (1 / eval_data['monopoly_count']) * 0.2
        # Higher win rate decreases bankruptcy risk
        bankruptcy_risk -= eval_data['raw_probability'] * 0.1  # Reduce risk based on win probability
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

def display_win_probabilities(game, player_evaluations, game_progress, game_phase):
    """Display the calculated win and bankruptcy probabilities."""
    total_net_worth = player_evaluations.pop('total_net_worth', 0)
    
    print(f"{colors['info']}Game Progress: {colors['success']}{game_progress*100:.1f}% ({game_phase} game)\n")
    
    # Display results sorted by win probability
    sorted_players = sorted(player_evaluations.items(), key=lambda x: x[1]['win_probability'], reverse=True)
    
    for i, (player, data) in enumerate(sorted_players):
        # Calculate color for probability
        if data['win_probability'] > 50:
            prob_color = colors['success']
        elif data['win_probability'] > 25:
            prob_color = colors['warning']
        else:
            prob_color = colors['error']
            
        print(f"{i+1}. {colors['player']}{player.name}: {prob_color}{data['win_probability']:.1f}% chance to win")
        print(f"   Net Worth: {colors['money']}${data['net_worth']:.0f} " + 
                f"({data['net_worth']/total_net_worth*100:.1f}% of total)")
        
        # Display bankruptcy probability
        bankruptcy_color = colors['success'] if data['bankruptcy_probability'] < 25 else (
                            colors['warning'] if data['bankruptcy_probability'] < 50 else colors['error'])
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
            print(f"   Key factors: {colors['info']}{', '.join(factors)}")
        print()
    
    # Display players sorted by bankruptcy risk
    print(f"\n{colors['title']}=== BANKRUPTCY RISK ANALYSIS ===\n")
    bankruptcy_sorted = sorted(player_evaluations.items(), key=lambda x: x[1]['bankruptcy_probability'], reverse=True)
    
    print(f"{colors['info']}Players most likely to go bankrupt next:")
    for i, (player, data) in enumerate(bankruptcy_sorted[:3]):  # Show top 3 at risk
        bankruptcy_color = colors['success'] if data['bankruptcy_probability'] < 25 else (
                            colors['warning'] if data['bankruptcy_probability'] < 50 else colors['error'])
        print(f"{i+1}. {colors['player']}{player.name}: {bankruptcy_color}{data['bankruptcy_probability']:.1f}% risk")
        print(f"   Cash: {colors['money']}${player.money} ({data['cash_ratio']*100:.0f}% of assets)")
        
        # Additional risk factors
        mortgaged = sum(1 for p in player.properties if p.status == PropertyStatus.MORTGAGED)
        if mortgaged > 0:
            print(f"   {colors['warning']}Has {mortgaged} mortgaged properties")


def display_game_statistics(game_stats):
    # Print overall statistics with improved color and layout
    print(f"{colors['title']}\n===== OVERALL GAME STATISTICS ====={colors['reset']}")
    print(f"{colors['info']}Total games played: {colors['success']}{game_stats['games_played']}{colors['reset']}")
    
    # Calculate average number of turns across all games
    total_turns = sum(game_stats["turns"].values())
    avg_turns = total_turns / max(1, game_stats["games_played"])
    print(f"{colors['info']}Average game length: {colors['success']}{avg_turns:.1f} turns{colors['reset']}")
    
    # Wins section with percentage bar visualization
    print(f"\n{colors['title']}===== PLAYER PERFORMANCE ====={colors['reset']}")
    print(f"{colors['info']}Wins by player:{colors['reset']}")
    
    # Find max wins for scaling
    max_wins = max(game_stats["wins_by_player"].values()) if game_stats["wins_by_player"] else 1
    
    for player, wins in game_stats["wins_by_player"].items():
        win_percentage = (wins/game_stats['games_played'])*100
        # Create a visual bar based on win percentage
        bar_length = int(win_percentage / 5)  # Scale to make bars reasonable length
        visual_bar = "█" * bar_length
        
        print(
            f"{colors['success']}{player}: {wins} wins ({win_percentage:.1f}%) {colors['prompt']}{visual_bar}{colors['reset']}"
        )

    # Bankruptcy section with visualization
    print(f"\n{colors['info']}Bankruptcy rate:{colors['reset']}")
    for player, count in game_stats["bankrupt_count"].items():
        bankruptcy_percentage = (count/game_stats['games_played'])*100
        bar_length = int(bankruptcy_percentage / 5)
        visual_bar = "█" * bar_length
        
        print(
            f"{colors['error']}{player}: {count} bankruptcies ({bankruptcy_percentage:.1f}%) {colors['prompt']}{visual_bar}{colors['reset']}"
        )

    print(
        f"\n{colors['info']}Games that reached 500 turns: {colors['success']}{game_stats['game_over_500_turns']} ({(game_stats['game_over_500_turns']/game_stats['games_played'])*100:.1f}%){colors['reset']}"
    )
    
    # Display new detailed statistics with improved visuals
    print(f"\n{colors['title']}===== DETAILED PLAYER STATISTICS ====={colors['reset']}")
    
    # Property acquisition stats with comparative analysis
    print(f"\n{colors['title']}PROPERTY OWNERSHIP ANALYSIS{colors['reset']}")
    if game_stats["property_acquisitions"]:
        max_properties = max(game_stats["property_acquisitions"].values())
        
        print(f"{colors['info']}Property Acquisitions (average per game):{colors['reset']}")
        for player, count in game_stats["property_acquisitions"].items():
            if game_stats["games_played"] > 0:
                avg_per_game = count / game_stats["games_played"]
                bar_length = int((count / max_properties) * 20)  # Scale to max 20 chars
                visual_bar = "■" * bar_length
                
                print(f"{colors['info']}{player}: {count} total ({avg_per_game:.1f} per game) {colors['success']}{visual_bar}{colors['reset']}")
    
    # Monopoly stats with visualization
    print(f"\n{colors['title']}MONOPOLY CONTROL{colors['reset']}")
    if game_stats["monopolies_owned"]:
        max_monopolies = max(game_stats["monopolies_owned"].values())
        
        for player in game_stats["monopolies_owned"]:
            monopoly_count = game_stats["monopolies_owned"][player]
            if max_monopolies > 0:
                bar_length = int((monopoly_count / max_monopolies) * 15)
                visual_bar = "■" * bar_length
                
                print(f"{colors['success']}{player}: {monopoly_count} monopolies {colors['prompt']}{visual_bar}{colors['reset']}")
    
    # House and Hotel stats with combined visualization
    print(f"\n{colors['title']}PROPERTY DEVELOPMENT{colors['reset']}")
    print(f"{colors['info']}House and Hotel Development:{colors['reset']}")
    for player in game_stats["avg_houses_per_player"]:
        avg_houses = game_stats["avg_houses_per_player"][player] / max(1, game_stats["games_played"])
        avg_hotels = game_stats["avg_hotels_per_player"][player] / max(1, game_stats["games_played"])
        
        # House visual
        house_bar = "🏠" * min(10, int(avg_houses))
        if avg_houses > 10:
            house_bar += f"+{int(avg_houses)-10}"
            
        # Hotel visual    
        hotel_bar = "🏨" * min(5, int(avg_hotels))
        if avg_hotels > 5:
            hotel_bar += f"+{int(avg_hotels)-5}"
            
        print(f"{colors['info']}{player}:{colors['reset']}")
        print(f"{colors['success']}  Houses: {avg_houses:.1f}/game {house_bar}{colors['reset']}")
        print(f"{colors['prompt']}  Hotels: {avg_hotels:.1f}/game {hotel_bar}{colors['reset']}")
    
    # Rent collection stats with financial performance indicator
    print(f"\n{colors['title']}FINANCIAL PERFORMANCE{colors['reset']}")
    print(f"{colors['info']}Rent Collection:{colors['reset']}")
    
    if game_stats["total_rent_collected"]:
        max_rent = max(game_stats["total_rent_collected"].values())
        
        for player in game_stats["total_rent_collected"]:
            total_rent = game_stats["total_rent_collected"][player]
            if game_stats["games_played"] > 0:
                avg_rent = total_rent / game_stats["games_played"]
                
                # Create a visual financial indicator
                rent_ratio = total_rent / max(1, max_rent)
                if rent_ratio > 0.7:
                    financial_indicator = f"{colors['success']}★★★{colors['reset']}"  # High performer
                elif rent_ratio > 0.4:
                    financial_indicator = f"{colors['prompt']}★★{colors['reset']}"     # Medium performer
                else:
                    financial_indicator = f"{colors['error']}★{colors['reset']}"       # Low performer
                
                print(f"{colors['info']}{player}: ${total_rent} total (${avg_rent:.1f} per game) {financial_indicator}{colors['reset']}")
    
    # Most valuable properties with better visualization
    print(f"\n{colors['title']}HIGH-VALUE PROPERTIES{colors['reset']}")
    print(f"{colors['info']}Most Valuable Properties (highest rent):{colors['reset']}")
    for player in game_stats["most_valuable_property"]:
        prop_data = game_stats["most_valuable_property"][player]
        if prop_data["name"] != "None":
            # Add value indicator based on rent amount
            if prop_data["rent"] > 200:
                value_indicator = f"{colors['success']}[PREMIUM]{colors['reset']}"
            elif prop_data["rent"] > 100:
                value_indicator = f"{colors['prompt']}[HIGH]{colors['reset']}"
            else:
                value_indicator = f"{colors['info']}[STANDARD]{colors['reset']}"
                
            print(f"{colors['info']}{player}: {prop_data['name']} (${prop_data['rent']} rent) {value_indicator}{colors['reset']}")
    
    # Trading activity with detailed stats
    print(f"\n{colors['title']}TRADING BEHAVIOR{colors['reset']}")
    print(f"{colors['info']}Trading Activity:{colors['reset']}")
    for player in game_stats["trades_made"]:
        trades = game_stats["trades_made"][player]
        accepted = game_stats["trades_accepted"][player]
        rejected = game_stats["trades_rejected"][player]
        
        if trades > 0:
            acceptance_rate = (accepted / trades) * 100
            # Trading style indicator
            if trades > (game_stats["games_played"] * 2):
                style = f"{colors['prompt']}[AGGRESSIVE TRADER]{colors['reset']}"
            elif trades > game_stats["games_played"]:
                style = f"{colors['success']}[ACTIVE TRADER]{colors['reset']}"
            else:
                style = f"{colors['info']}[CAUTIOUS TRADER]{colors['reset']}"
                
            print(f"{colors['info']}{player}: {trades} trades offered, {accepted} accepted ({acceptance_rate:.1f}%) {style}{colors['reset']}")
    
    # Property type preferences with visual representation
    print(f"\n{colors['title']}PROPERTY TYPE PREFERENCES{colors['reset']}")
    for player in game_stats["most_owned_property_type"]:
        if game_stats["most_owned_property_type"][player]:
            # Sort property types by frequency
            sorted_types = sorted(
                game_stats["most_owned_property_type"][player].items(), 
                key=lambda x: x[1], 
                reverse=True
            )
            
            # Get top 3 property types
            top_types = sorted_types[:3]
            
            print(f"{colors['info']}{player} prefers:{colors['reset']}")
            for i, (prop_type, count) in enumerate(top_types):
                # Use different colors for different rankings
                if i == 0:
                    rank_color = colors['success']
                elif i == 1:
                    rank_color = colors['prompt']
                else:
                    rank_color = colors['info']
                    
                print(f"  {rank_color}{i+1}. {prop_type} properties ({count} owned){colors['reset']}")
    
    # Display bot parameters with improved formatting
    if input(f"{colors['prompt']}Display bot parameters? (y/n): {colors['reset']}").lower() == 'y':
        pass
    else:
        return
    
    print(f"\n{colors['title']}===== PLAYER PARAMETERS ====={colors['reset']}")
    print(f"{colors['title']}==================================={colors['reset']}")
    
    for i, parameters in enumerate(bots_parameters):
        print(f"{colors['prompt']}BOT {i+1} PARAMETERS:{colors['reset']}")
        
        for key, value in parameters.items():
            # Color-code parameter values based on their magnitude
            if value > 0.7:
                param_color = colors['success']  # High values in green
            elif value > 0.3:
                param_color = colors['prompt']   # Medium values in yellow
            else:
                param_color = colors['error']    # Low values in red
                
            print(f"  {colors['info']}{key}: {param_color}{value:.2f}{colors['reset']}")

    print(f"\n{colors['title']}=== WINNER PROPERTY STATISTICS ==={colors['reset']}")
    
    # Display most commonly owned properties by winners
    print(f"\n{colors['info']}Most Common Properties Owned by Winners:{colors['reset']}")
    if game_stats["winner_properties"]:
        sorted_props = sorted(game_stats["winner_properties"].items(), key=lambda x: x[1], reverse=True)
        for prop, count in sorted_props[:5]:  # Show top 5
            win_percentage = (count / game_stats["games_played"]) * 100
            print(f"{colors['property']}{prop}: {count} wins ({win_percentage:.1f}%){colors['reset']}")
    
    # Display property color groups most commonly owned by winners
    print(f"\n{colors['info']}Most Common Color Groups Owned by Winners:{colors['reset']}")
    if game_stats["winner_property_colors"]:
        sorted_colors = sorted(game_stats["winner_property_colors"].items(), key=lambda x: x[1], reverse=True)
        for color, count in sorted_colors:
            win_percentage = (count / (game_stats["games_played"] * 3)) * 100  # Assuming average 3 properties per color
            print(f"{colors['property']}{color}: {count} properties ({win_percentage:.1f}%){colors['reset']}")
    
    # Display house distribution of winners
    print(f"\n{colors['info']}House Distribution of Winners:{colors['reset']}")
    if game_stats["winner_house_distribution"]:
        total_properties = sum(game_stats["winner_house_distribution"].values())
        if total_properties > 0:
            for houses, count in game_stats["winner_house_distribution"].items():
                percentage = (count / total_properties) * 100 if total_properties > 0 else 0
                house_label = "Hotel" if houses == "hotel" else f"{houses} House(s)"
                print(f"{colors['property']}{house_label}: {count} properties ({percentage:.1f}%){colors['reset']}")
    
def main():
    print("Training completed for all game histories.")

if __name__ == "__main__":
    main()
