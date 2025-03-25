class player:
    
    def __init__(self):
        self.name = "Player1"
        self.bot = bot(self)
        

class bot:
    def __init__(self, player):
        self.player = player
        self.name = "Bot1"
        
    def get_player_name(self):
        return self.player.name


test = player()
print(test.bot.player.bot.player.bot)  # Output: Player1