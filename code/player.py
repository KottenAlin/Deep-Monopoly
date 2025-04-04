from Bot import Bot, parameters

from game_models import PropertyStatus, Property
from colorama import Fore, Style, Back
from variables import colors


class Player:
    def __init__(
        self,
        name,
        token,
        is_bot=False,
        game=None,
        bot_parameters=parameters,
        bot_type="default",
    ):
        """ """

        self.name = name
        self.token = token
        self.position = 0
        self.money = 1500
        self.properties = []
        self.jail_turns = 0
        self.jail_free_cards = 0
        self.bankrupt = False
        self.is_bot = is_bot

        if is_bot:
            if bot_type == "neural":
                # Import locally to avoid circular dependency
                from neural_algorithm import ActionNeuralBot

                self.bot = ActionNeuralBot(self, game=game, display=False)
            else:
                self.bot = Bot(
                    self, game=game, parameters=bot_parameters, display=False
                )
            self.bot_type = bot_type

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

        print(f"\n{colors['player']}{self.name} ({self.token}):{colors['reset']}")

        # Display position with appropriate color based on space type
        space = board.spaces[self.position]
        if isinstance(space, Property):
            print(
                f"  {colors['info']}Position: {self.position} ({colors['property']}{space.name}{colors['reset']})"
            )
        else:
            print(
                f"  {colors['info']}Position: {self.position} ({colors['info']}{space}{colors['reset']})"
            )

        # Display money with money color
        print(
            f"  {colors['info']}Money: {colors['money']}${self.money}{colors['reset']}"
        )

        # Display properties with appropriate formatting
        print(f"  {colors['info']}Properties: ", end="")
        if self.properties:
            property_list = []
            for p in self.properties:
                if p.status == PropertyStatus.MORTGAGED:
                    status = f" ({colors['warning']}Mortgaged{colors['reset']})"
                elif hasattr(p, "houses") and p.houses > 0:
                    status = f" ({colors['success']}{p.houses} houses{colors['reset']})"
                elif hasattr(p, "hotel") and p.hotel:
                    status = f" ({colors['success']}Hotel{colors['reset']})"
                else:
                    status = ""
                property_list.append(f"{colors['property']}{p.name}{status}")
            print(", ".join(property_list))
        else:
            print(f"{colors['info']}None")

        # Display jail status
        if self.jail_turns > 0:
            print(
                f"  {colors['jail']}In jail: {self.jail_turns} turns remaining{colors['reset']}"
            )
