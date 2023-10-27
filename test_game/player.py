

#Class players
class Player():
    def __init__(self, id, position, inventory,current_floor,health=100,base_character_tile = (7,80), name=""):
        self.id = id
        self.position = position
        self.inventory = inventory
        self.current_floor = current_floor
        self.health = health
        self.name = name


        self.base_character_tile = base_character_tile

    def serialize(self):
        serialized_class = {
            "id": self.id,
            "position": self.position,
            "inventory": self.inventory,
            "current_floor": self.current_floor,
            "health":self.health,
            "base_character_tile": self.base_character_tile,
            "name": self.name
        }
        return serialized_class

    @classmethod
    def from_dict(cls, data):
        id = data["id"]
        position = data["position"]
        inventory = data["inventory"]
        current_floor = data["current_floor"]
        health = data["health"]
        base_character_tile = data["base_character_tile"]
        name = data["name"]
        return cls(id, position, inventory, current_floor,health,base_character_tile,name)