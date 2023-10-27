

class Room_decorations():
    def __init__(self):

        self.rooms = []
    

#Current structure
#{"position": (ranX,ranY), "decoration_tile":(decoration_to_be_placed), "type":decoration_category["type"]}
#{"position": (ranX,ranY), "decoration_tile":(decoration_to_be_placed.loot_tile), "type":decoration_category["type"],"item":decoration_to_be_placed.serialize()}

# 13,12
#4x4
room1 = [
    [(13,12),None,None,(13,12)],
    [None   ,None,None,   None],
    [None   ,None,None,   None],
    [(13,12),None,None,(13,12)],

    ]