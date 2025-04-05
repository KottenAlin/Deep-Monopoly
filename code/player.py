from Bot import Bot, parameters

from game_models import PropertyStatus, Property

from variables import colors
import os
from pathlib import Path

class Player:
    def __init__(
        self,
        name,
        token,
        is_bot=False,
        game=None,
        bot_parameters=parameters,
        bot_type="default",
        run_with_input=False,
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
                if run_with_input:
                    self.show_loading_models()
            else:
                self.bot = Bot(
                    self, game=game, parameters=bot_parameters, display=False
                )
            self.bot_type = bot_type


    def show_loading_models(self):
        
        # Find models directory relative to the current file
        if input("load models from folder? (y/n): ").lower() != 'y':
            return None
        
        models_dir = Path('models/')

        # Get all model files
        model_files = [f for f in os.listdir(models_dir)]
        
        if not model_files:
            print(f"{colors['warning']}No models found in {models_dir}{colors['reset']}")
            return None
        
        # Display available models
        print(f"{colors['info']}Available models:{colors['reset']}")
        for i, model_file in enumerate(model_files):
            print(f"{i+1}. {model_file}")
        
        # Let the user choose a model
        while True:
            choice = input(f"{colors['prompt']}Select a model number to load (or 'q' to quit): {colors['reset']}")
            if choice.lower() == 'q':
                return None
            
            try:
                index = int(choice) - 1
                if 0 <= index < len(model_files):
                    model_path = str(models_dir / model_files[index])
                    print(f"{colors['success']}Loading model: {model_files[index]}{colors['reset']}")
                    
                    # Import locally to avoid circular dependency
                    self.bot.load_model(model_path)
                    print(f"{colors['success']}Model loaded successfully!{colors['reset']}")
                    return model_files[index]
                else:
                    print(f"{colors['error']}Invalid selection. Please choose a number between 1 and {len(model_files)}{colors['reset']}")
            except ValueError:
                print(f"{colors['error']}Please enter a valid number or 'q'{colors['reset']}")

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
