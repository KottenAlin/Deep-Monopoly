from colorama import init, Fore, Back, Style

init()

num_games = 100
game_stats = {
    "games_played": 0,
    "average_turns": 0,
    "wins_by_player": {},  # Will track number of wins per player
    "bankrupt_count": {},  # Will track number of bankruptcies per player
    "turns": {},
    "game_over_500_turns": 0,
    # New detailed statistics
    "avg_houses_per_player": {},  # Average houses owned by each player
    "avg_hotels_per_player": {},  # Average hotels owned by each player
    "monopolies_owned": {},       # Count of color monopolies owned by each player
    "avg_rent_collected": {},     # Average rent collected by each player
    "total_rent_collected": {},   # Total rent collected by each player
    "property_acquisitions": {},  # Number of properties acquired by each player
    "trades_made": {},            # Number of trades made by each player
    "trades_accepted": {},        # Number of trade offers accepted
    "trades_rejected": {},        # Number of trade offers rejected
    "most_valuable_property": {}, # Most valuable property (highest rent) for each player
    "most_owned_property_type": {}, # Most frequently owned property type/color
    # Winner statistics
    "winner_properties": {},      # Track properties owned by winners
    "winner_house_distribution": {}, # Track house distribution of winners
    "winner_property_colors": {}, # Track which color groups winners owned
}

def initialise_game_stats(bot_count):
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
    
    # Initialize winner statistics
    game_stats["winner_properties"] = {}  # Format: {property_name: count}
    game_stats["winner_house_distribution"] = {
        "0": 0,     # Properties with 0 houses
        "1": 0,     # Properties with 1 house
        "2": 0,     # Properties with 2 houses
        "3": 0,     # Properties with 3 houses
        "4": 0,     # Properties with 4 houses
        "hotel": 0  # Properties with hotels
    }
    game_stats["winner_property_colors"] = {}  # Format: {color: count}

colors = {
    "title": Fore.CYAN + Style.BRIGHT,
    "prompt": Fore.YELLOW,
    "info": Fore.WHITE,
    "success": Fore.GREEN,
    "warning": Fore.YELLOW,
    "error": Fore.RED,
    "money": Fore.GREEN + Style.BRIGHT,
    "property": Fore.MAGENTA,
    "player": Fore.BLUE + Style.BRIGHT,
    "dice": Fore.CYAN,
    "rent": Fore.RED + Style.BRIGHT,
    "jail": Fore.WHITE + Back.BLACK,
    "bot": Fore.YELLOW + Style.DIM,
    "reset": Style.RESET_ALL,
    "money": Fore.GREEN + Style.BRIGHT,
    "property": Fore.MAGENTA,
}


bots_parameters = [
    {
        "risk_tolerance": 1.0,
        "property_focus": 1.0,
        "development_focus": 1.0,
        "cash_reserve_preference": 1.0,
        "trade_willingness": 1.0,
        "monopoly_focus": 1.0,
        "railroad_utility_interest": 1.0,
    },
    {
        "risk_tolerance": 1.0,
        "property_focus": 1.0,
        "development_focus": 1.0,
        "cash_reserve_preference": 0.5,
        "trade_willingness": 0.7,
        "monopoly_focus": 1.0,
        "railroad_utility_interest": 0,
    },
    {
        "risk_tolerance": 0,
        "property_focus": 0,
        "development_focus": 0,
        "cash_reserve_preference": 0,
        "trade_willingness": 1,
        "monopoly_focus": 0,
        "railroad_utility_interest": 0,
    },
    {
        "risk_tolerance": 0.2,
        "property_focus": 0.5,
        "development_focus": 0.7,
        "cash_reserve_preference": 0.7,
        "trade_willingness": 0.5,
        "monopoly_focus": 1,
        "railroad_utility_interest": 0.3,
    },
    {
        "risk_tolerance": 0.5,
        "property_focus": 0.5,
        "development_focus": 0.5,
        "cash_reserve_preference": 0.5,
        "trade_willingness": 0.5,
        "monopoly_focus": 0.5,
        "railroad_utility_interest": 0.5,
    },
    {
        "risk_tolerance": 0.8,
        "property_focus": 1.0,
        "development_focus": 1.0,
        "cash_reserve_preference": 1.0,
        "trade_willingness": 1.0,
        "monopoly_focus": 1.0,
        "railroad_utility_interest": 1.0,
    },
    {
        "risk_tolerance": 0.3,
        "property_focus": 0.8,
        "development_focus": 0.6,
        "cash_reserve_preference": 0.4,
        "trade_willingness": 0.6,
        "monopoly_focus": 0.8,
        "railroad_utility_interest": 0.2,
    },
]
