from enum import Enum


class PropertyColor(Enum):
    BROWN = "Brown"
    LIGHT_BLUE = "Light Blue"
    PINK = "Pink"
    ORANGE = "Orange"
    RED = "Red"
    YELLOW = "Yellow"
    GREEN = "Green"
    DARK_BLUE = "Dark Blue"
    RAILROAD = "Railroad"
    UTILITY = "Utility"
class PropertyStatus(Enum):
    UNOWNED = "Unowned"
    OWNED = "Owned"
    MORTGAGED = "Mortgaged"

class Property:
    def __init__(self, name, position, price, color, rents, mortgage_value, house_price=0):
        self.name = name
        self.position = position
        self.price = price
        self.color = color
        self.rents = rents  # List of rents [base, 1 house, 2 houses, 3 houses, 4 houses, hotel]
        self.mortgage_value = mortgage_value
        self.house_price = house_price
        self.owner = None
        self.status = PropertyStatus.UNOWNED
        self.houses = 0
        self.hotel = False
    
    def calculate_rent(self, dice_roll=None):
        if self.status == PropertyStatus.MORTGAGED:
            return 0
            
        if self.color == PropertyColor.UTILITY and dice_roll:
            # Utilities rent is based on dice roll
            multiplier = 4 if self.owner.properties.count(self) == 1 else 10
            return dice_roll * multiplier
            
        if self.color == PropertyColor.RAILROAD:
            # Railroads rent increases based on how many railroads the owner has
            railroad_count = sum(1 for prop in self.owner.properties if prop.color == PropertyColor.RAILROAD)
            return self.rents[railroad_count - 1]
            
        # Regular property
        if self.hotel:
            return self.rents[5]
        else:
            return self.rents[self.houses]
    
    def mortgage(self, player):
        if self.status == PropertyStatus.OWNED and self.houses == 0 and not self.hotel:
            self.status = PropertyStatus.MORTGAGED
            player.receive(self.mortgage_value)
            return self.mortgage_value
        return 0
    
    def unmortgage(self):
        if self.status == PropertyStatus.MORTGAGED:
            unmortgage_cost = int(self.mortgage_value)
            self.status = PropertyStatus.OWNED
            return unmortgage_cost
        return 0
    
    def add_house_or_hotel(self):
        #print(self.status, self.hotel, self.houses)
        if self.status == PropertyStatus.OWNED and not self.hotel:
            if  self.houses < 4 :
                self.houses += 1
                return True
            elif self.houses == 4:
                self.hotel = True
                self.houses = 0
                return True
            return False
    
    def remove_hotel(self):
        if self.hotel:
            self.hotel = False
            self.houses = 4
            return True
        return False
    
    def remove_house(self, house_count=1):
        if self.houses > 0:
            self.houses -= 1
            return True
        return False
