from enum import Enum

#Easy access for valid equpmentslots
class Equip_slots(Enum):
    Cloak = "cloak"
    Chest = "chest"
    Legs = "legs"
    Hands = "hands"
    Head = "head"
    Feet = "feet"
    MainHand = "hand1"
    OffHand = "hand2"


#Class for items
class Item():
    def __init__(self,loot_tile, name, slot, on_equipped_tile):
        self.loot_tile = loot_tile
        self.name = name,
        self.slot = slot
        self.on_equipped_tile = on_equipped_tile

    def serialize(self):
        serialized_class = {
            "loot_tile": self.loot_tile,
            "name": f"{self.name}",
            "slot": self.slot.value,
            "on_equipped_tile": self.on_equipped_tile
        }
        return serialized_class

    @classmethod
    def from_dict(cls, data):
        loot_tile = data["loot_tile"]
        name = data["name"]
        slot = data["slot"]
        on_equipped_tile = data["on_equipped_tile"]
        return cls(loot_tile, name, slot, on_equipped_tile)

def get_loot_table():
    loot_table = []
    RoD = Item(loot_tile=(32,38), name="Robe of Dank",      slot=Equip_slots.Chest,    on_equipped_tile=(48,82))
    Coi = Item(loot_tile=(10,36), name="Cloak of Insight",  slot=Equip_slots.Cloak,    on_equipped_tile=(17,84))
    Sword = Item(loot_tile=(4,46), name="Sword",            slot=Equip_slots.MainHand, on_equipped_tile=(57,87))
    loot_table = loot_table + [RoD,Coi,Sword]


    #Armorset of Titan
    armorset_of_titan = []
    armorset_of_titan.append(Item(loot_tile=(14,38), name="Breastplate of Titan",slot=Equip_slots.Chest, on_equipped_tile=(53,82)))
    armorset_of_titan.append(Item(loot_tile=(62,36), name="Helmet of Titan",slot=Equip_slots.Head, on_equipped_tile=(30,92)))
    armorset_of_titan.append(Item(loot_tile=(7,36), name="Gloves of Titan",slot=Equip_slots.Hands, on_equipped_tile=(53,84)))
    armorset_of_titan.append(Item(loot_tile=(15,36), name="Legs of Titan",slot=Equip_slots.Legs, on_equipped_tile=(39,93)))
    armorset_of_titan.append(Item(loot_tile=(27,36), name="Sabatons of Titan",slot=Equip_slots.Feet, on_equipped_tile=(61,83)))
    loot_table = loot_table + armorset_of_titan


    return loot_table