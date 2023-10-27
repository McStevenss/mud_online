import random
import pygame
from tunneling import TunnelingAlgorithm
from item import Item, Equip_slots, get_loot_table


class Game_map():
    def __init__(self):
        self.walkable_tiles = [".","'"]
        self.unwalkable_tiles = ["#"]
        self.editable_tiles = ["+","$"]

        #Map
        self.map_width = 20
        self.map_height = 15
        
        #Create a full map
        self.map_data = [['#' for _ in range(self.map_width)] for _ in range(self.map_height)]

        self.min_room_width = 3
        self.max_room_width = 8
        self.min_room_height = 3
        self.max_room_height = 8
        self.max_attempts = 100
        
        self.tunneler = TunnelingAlgorithm()
        #self.game_map = [self.Generate_carve_map(10), self.Generate_carve_map(7),self.Generate_carve_map(7)]
        self.game_map = [self.Prune_Level(self.tunneler.generateLevel(50,50))]
        self.game_map_decoration = self.Decorate_rooms_for()
       # print(self.tunneler.rooms)#room cords

      
    def Edit_Map(self,x,y,floor,char):
        self.game_map[floor][y][x] = char

    def Get_Map(self):
        return self.game_map
    
    def Generate_Base_Map(self,W,H):
        """
        Generates a basemap, W-max = 20, H-max = 15
        """
        top_wall = ["#"]*W
        bottom_wall = ["#"]*W
        base_map = []   
        base_map.append(top_wall)    #Top wall
        for _ in range((H-2)):       #Middle walls
            base_map.append(["#" if i == 0 or i == W - 1 else "." for i in range(W)] )
        base_map.append(bottom_wall) #Bottom wall
        
        return base_map
    
    def Generate_Box_On_Map(self,x,y,w,h,map, char="#"):
        new_map = map
        for row in range(y,y+h):
            for i in range(x,x+w):
                new_map[row][i] = char
        return new_map  

    
    def is_valid_location(self,x, y, width, height, map):
        for i in range(x, x + width):
            for j in range(y, y + height):
                if map[j][i] != '#':
                    return False
        return True
    
    def Generate_carve_map(self,rooms):
        #Generate filled map
        base_map = [['#' for _ in range(self.map_width)] for _ in range(self.map_height)]
           
        room_locations = []
        #Create rooms
        for _ in range(rooms):
            
            # Randomly choose a dimension within the specified range for the room size
            random_width = random.randint(self.min_room_width, self.max_room_width)
            random_height = random.randint(self.min_room_height, self.max_room_height)
            
            for _ in range(self.max_attempts):
                x = random.randint(1, len(base_map[0]) - random_width - 1)
                y = random.randint(1, len(base_map) - random_height - 1)

                if self.is_valid_location(x, y, random_width, random_height,base_map):
                    # Place the room by updating the map
                    for i in range(x, x + random_width):
                        for j in range(y, y + random_height):
                            base_map[j][i] = '.'

                    room_locations.append([x,y,random_width,random_height])
                    break
        
        
        # Iterate through the map and place doors where there's only one wall between rooms
        #check horizontally
        door_candidates_hor = {}
        door_candidates_ver = {}
        
        #flood_start = None
        for y, row in enumerate(base_map):
            for x , block in enumerate(row):
                
                if (x != 0 and x != len(row)-1) and (y != 0 and y != len(base_map)-1):          
                    sorrounding_walls = 0
                    if base_map[y][x] == "#":
                        if base_map[y][x-1] == "#" or base_map[y][x-1] == " ": #LEFT
                            sorrounding_walls +=1                            
                        if base_map[y][x+1] == "#" or base_map[y][x+1] == " ": #RIGHT
                            sorrounding_walls +=1
                        if base_map[y-1][x] == "#" or base_map[y-1][x] == " ": #UP
                            sorrounding_walls +=1
                        if base_map[y+1][x] == "#" or base_map[y+1][x] == " ": #DOWN
                            sorrounding_walls +=1
                    
                    if sorrounding_walls == 4:
                        base_map[y][x] = " "
                        
                elif x == 0:
                    if base_map[y][x+1] == "#" or base_map[y][x+1] == " ": #RIGHT
                        base_map[y][x] = " "
                
                elif x == len(row)-1:
                    if base_map[y][x-1] == "#" or base_map[y][x-1] == " ": #LEFT
                            base_map[y][x] = " "
                
                elif y == 0:      
                    if base_map[y+1][x] == "#" or base_map[y+1][x] == " ": #DOWN
                            base_map[y][x] = " "
                
                elif y == len(base_map)-1:
                    if base_map[y-1][x] == "#" or base_map[y-1][x] == " ": #UP
                            base_map[y][x] = " "
                
                if x != 0 and x != len(row)-1:
                    if[row[x-1],block,row[x+1]] == [".","#","."]:
                        #Horizontally the door positions will always have the same X
                        if x not in door_candidates_ver.keys():
                            door_candidates_ver[x] = [y]
                        else:
                            door_candidates_ver[x].append(y)

                # if x != 0 and x < len(row)-2:        
                #     if [base_map[y][x-1],base_map[y][x],base_map[y][x+1],base_map[y][x+2]] == [".","#","#","."]:
                        
                #         if x not in door_candidates_ver.keys():
                #             door_candidates_ver[(x,x+1)] = [y]
                #         else:
                #             door_candidates_ver[(x,x+1)].append(y)
                #         print("Found horizontal double wall")
                        

                if y != 0 and y != len(base_map)-1:
                    if [base_map[y-1][x],base_map[y][x],base_map[y+1][x]] == [".","#","."]:
                        #Vertically the door positions will always have the same Y
                        if y not in door_candidates_ver.keys():
                            door_candidates_hor[y] = [x]
                        else:
                            door_candidates_hor[y].append(x)
                            
                # if y != 0 and y < len(base_map)-2:        
                #     if [base_map[y-1][x],base_map[y][x],base_map[y+1][x],base_map[y+2][x]] == [".","#","#","."]:
                #         #Vertically the door positions will always have the same Y                                  
                #         if x not in door_candidates_ver.keys():
                #             door_candidates_hor[(y,y+1)] = [x]
                #         else:
                #             door_candidates_hor[(y,y+1)].append(x)
                #         print("Found vertical double wall")
                        

                 
                # if (x != 0 and x != len(row)-1) and  (y != 0 and y != len(base_map)-1):
                #     if [base_map[y-1][x],base_map[y][x],base_map[y+1][x]] == ["#","#","#"]:
                #         if [row[x-1],block,row[x+1]] == ["#","#","#"]:
                #             flood_start = (x,y)
                            #base_map[y][x] = " "
        
        print("door_candidates_hor",door_candidates_hor)
        print("door_candidates_ver",door_candidates_ver)
        
        #Horizontal door random choice
        for r_x in door_candidates_ver:
            if type(r_x) != int:
                r_x_0 = r_x[0]
                r_x_1 = r_x[1]
                r_y = random.choice(door_candidates_ver[r_x])
                base_map[r_y][r_x_0] = "+"
                base_map[r_y][r_x_1] = "."
            else:
                r_y = random.choice(door_candidates_ver[r_x])
                base_map[r_y][r_x] = "+"
        
        for r_y in door_candidates_hor:        
            if type(r_y) != int: #double wall!
                r_y_0 = r_y[0]
                r_y_1 = r_y[1]
                r_x = random.choice(door_candidates_hor[r_y])
                base_map[r_y_0][r_x] = "+"
                base_map[r_y_1][r_x] = "."
            
            else: 
                r_x = random.choice(door_candidates_hor[r_y])
                base_map[r_y][r_x] = "+"
    

        #generate stairs down
        last_floor_tile = (0,0)
        for y, row in enumerate(base_map):
            for x , block in enumerate(row):
                if block == ".":
                    last_floor_tile = (x,y)
                    
        base_map[last_floor_tile[1]][last_floor_tile[0]] = ">"
        
        placed_stair_up = False
        for y, row in enumerate(base_map):
            for x, block in enumerate(row):
                if block == ".":
                    base_map[y][x] = "<"
                    placed_stair_up = True
                    break
                    
            if placed_stair_up == True:
                break
                    
                    
        
        print("Generated map!")
        for row in base_map:
            print(row)      
        return base_map
    
    def Prune_Level(self,base_map):
        widest_x = 0
        for y, row in enumerate(base_map):
            for x , block in enumerate(row):
                
                if (x != 0 and x != len(row)-1) and (y != 0 and y != len(base_map)-1):          
                    sorrounding_walls = 0
                    if base_map[y][x] == "#":
                        if base_map[y][x-1] == "#" or base_map[y][x-1] == " ": #LEFT
                            sorrounding_walls +=1                            
                        if base_map[y][x+1] == "#" or base_map[y][x+1] == " ": #RIGHT
                            sorrounding_walls +=1
                        if base_map[y-1][x] == "#" or base_map[y-1][x] == " ": #UP
                            sorrounding_walls +=1
                        if base_map[y+1][x] == "#" or base_map[y+1][x] == " ": #DOWN
                            sorrounding_walls +=1
                    
                    if sorrounding_walls == 4:
                        base_map[y][x] = " "
                        
                elif x == 0:
                    if base_map[y][x+1] == "#" or base_map[y][x+1] == " ": #RIGHT
                        base_map[y][x] = " "
                
                elif x == len(row)-1:
                    if base_map[y][x-1] == "#" or base_map[y][x-1] == " ": #LEFT
                            base_map[y][x] = " "
                
                elif y == 0:      
                    if base_map[y+1][x] == "#" or base_map[y+1][x] == " ": #DOWN
                            base_map[y][x] = " "
                
                elif y == len(base_map)-1:
                    if base_map[y-1][x] == "#" or base_map[y-1][x] == " ": #UP
                            base_map[y][x] = " "
                
                if block == "." and x > widest_x: widest_x = x
        #place stairs down faar away ">"
        furthest_y = 0
        for y,row in enumerate(base_map):
            if row[widest_x] == "." and y > furthest_y:
                furthest_y = y
        
        
        base_map[furthest_y][widest_x] = ">"
        print("far x,y", widest_x,furthest_y)
        return base_map
       
    def Get_spawn_point(self,current_floor):
        
        for y, row in enumerate(self.game_map[current_floor]):
            for x, block in enumerate(row):
                if block == ".":
                    return (x,y)
                
    def Get_stair_up_point(self,current_floor):
        last_floor_tile = (0,0)
        for y, row in enumerate(self.game_map[current_floor]):
            for x , block in enumerate(row):
                if block == ".":
                    last_floor_tile = (x,y)
                    
        return last_floor_tile
    
    def Decorate_rooms_for(self):
        #Right now only works for 1 map, not two
        decoration_list = []
        
        decoration_statues = [(12,12),(13,12),(14,12),(15,12),(16,12),(17,12),(18,12),(19,12),(34,12),(35,12)]
        decoration_misc = [(6,0),(7,0),(8,0),(9,0),(61,0)]

        items = get_loot_table()

        decoration_intensity = 6
        
        decorations = [
            {"tile": decoration_statues, "type": "decoration"},
            {"tile": decoration_misc,    "type": "decoration"},
            {"tile": items,              "type": "equippable"}
            ]
        
        for room in self.tunneler.rooms:
            #Everything is fucking flipped
            y0,y1,x0,x1 = room.x1,room.x2,room.y1,room.y2

            #Eventually change this to preset room decorations and fit them inside room instead if they fit
            for _ in range(decoration_intensity):
                
                decoration_category = random.choice(decorations)
                decoration_to_be_placed = random.choice(decoration_category["tile"])
                
                ranX = random.randint(x0+1,x1-1)
                ranY = random.randint(y0+1,y1-1)

                if decoration_category["type"] != "equippable":
                    decoration_list.append({"position": (ranX,ranY), "decoration_tile":(decoration_to_be_placed), "type":decoration_category["type"]})
                else:
                    decoration_list.append({"position": (ranX,ranY), "decoration_tile":(decoration_to_be_placed.loot_tile), "type":decoration_category["type"],"item":decoration_to_be_placed.serialize()})



        return decoration_list

                    
            
