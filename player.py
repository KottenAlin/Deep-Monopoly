from Bot import Bot, parameters
from game_models import PropertyStatus


class Player:
    def __init__(self, name, token, is_bot=True, game=None, bot_parameters=parameters):
        
        self.name = name
        self.token = token
        self.position = 0
        self.money = 1500
        self.properties = []
        self.jail_turns = 0
        self.jail_free_cards = 0
        self.bankrupt = False
        self.is_bot = is_bot
        self.bot = Bot(self, game=game, parameters=bot_parameters, display=False) if is_bot else None
    
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

        if self.properties:
            property_list = []
            for p in self.properties:
                status = " (Mortgaged)" if p.status == PropertyStatus.MORTGAGED else '(' + str(p.houses) + ')'
                property_list.append(f"{p.name}{status}")
