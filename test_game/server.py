from __future__ import print_function

import sys
from time import sleep, localtime
from random import randint
from weakref import WeakKeyDictionary

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

from game_map import Game_map
import command_utils

from item import Item, Equip_slots, get_loot_table
from player import Player

game_map = Game_map()
class ServerChannel(Channel):
    """
    This is the server representation of a single connected client (a player).
    """
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.id = str(self._server.NextId())
        intid = int(self.id)
        self.game_map_class = game_map
        
        #self.inventory = {"cloak": (16,84), "chest":(57,82), "legs":(38,93),"hands":(57,84) ,"head":(39,92),"feet":(60,83), "hand1":(42,90),"hand2":(48,85)}
        self.inventory = {"cloak": None, "chest": None, "legs":None,"hands":None ,"head":None,"feet": None, "hand1": None,"hand2": None} 
        self.current_floor = 0
        self.game_map = self.game_map_class.Get_Map()
        
        #Set initial position
        self.position = self.game_map_class.Get_spawn_point(current_floor=self.current_floor)
        self.health = 100
    
        #Here evey player object is setup.
        self.player_object = Player(self.id,self.position,self.inventory,self.current_floor,self.health)




    def PassOn(self, data): # pass on what we received to all connected clients
        data.update({"id": self.id})
        self._server.SendToAll(data)
    
    def Close(self):
        self._server.DelPlayer(self)
    
    def Valid_move(self, position):    
        #Check if map allows it

        if self.game_map[self.current_floor][position[1]][position[0]] in self.game_map_class.editable_tiles:
            is_edited = False
            if self.game_map[self.current_floor][position[1]][position[0]] == "+":
                self.game_map_class.Edit_Map(x=position[0],y=position[1],floor=self.current_floor,char="'")
                is_edited = True
                
            elif self.game_map[self.current_floor][position[1]][position[0]] == "$":
                self.game_map_class.Edit_Map(x=position[0],y=position[1],floor=self.current_floor,char=".")
                is_edited = True
            
            if is_edited:
                self.PassOn({"action": "editmap", "edited_map":self.game_map, "floor":self.current_floor})
            
                
        elif self.game_map != None and self.game_map[self.current_floor][position[1]][position[0]] in self.game_map_class.unwalkable_tiles:
            return False    
        return True
    
    
    ##################################
    ### Network specific callbacks ###
    ##################################

    def Network_move(self, data):
        new_position = (self.player_object.position[0] + data['position'][0], self.player_object.position[1] + data['position'][1])
        if self.Valid_move(new_position):
            self.player_object.position = (self.player_object.position[0] + data['position'][0], self.player_object.position[1] + data['position'][1])
            #print(self.position)
            self.PassOn(data)
            
    def Network_use(self,data):
        #command_utils.parse_action(self,data)
        x,y = self.player_object.position
        if self.game_map[self.player_object.current_floor][y][x] == ">": #Player is going down one level
            self.player_object.current_floor = self.player_object.current_floor + 1
            self.player_object.position = self.game_map_class.Get_spawn_point(current_floor=self.player_object.current_floor)
            data["move"] = "down"
            data["position"] = self.player_object.position
            self.PassOn(data)
        
        elif self.game_map[self.player_object.current_floor][y][x] == "<": #Player is going up one level
            self.player_object.current_floor = self.player_object.current_floor - 1
            self.player_object.position = self.game_map_class.Get_stair_up_point(current_floor=self.player_object.current_floor)
            data["move"] = "up"
            data["position"] = self.player_object.position
            self.PassOn(data)

        else:
            #Check if its an item or decoration player is trying to use
            for decoration in self.game_map_class.game_map_decoration:
                if decoration["position"] == (x,y):
                    #We have found the correct decoration, depending on type we do different things
                    if decoration["type"] == "equippable":
                        de_serialized_item = Item.from_dict(decoration["item"])
                        self.player_object.inventory[de_serialized_item.slot]=de_serialized_item.on_equipped_tile
                        data["equipped"] = {"slot":de_serialized_item.slot, "on_equipped_tile":de_serialized_item.on_equipped_tile}

                        self.game_map_class.game_map_decoration.remove(decoration)
                        data["updated_decorations"] = self.game_map_class.game_map_decoration
                        self.PassOn(data)

    def Network_nickname(self, data):
        self.player_object.name = data['nickname']
        self.player_object.base_character_tile = data['character']
        self.PassOn(data)


class GameServer(Server):
    '''
    This is the game server
    '''
    channelClass = ServerChannel
    
    def __init__(self, *args, **kwargs):
        self.id = 0
        Server.__init__(self, *args, **kwargs)
        self.players = WeakKeyDictionary()
        self.game_map_class = game_map
        self.game_map = self.game_map_class.Get_Map()
        self.ticks = 1000
        print('Server launched')
    
    def NextId(self):
        self.id += 1
        return self.id
    
    def Connected(self, channel, addr):
        self.AddPlayer(channel)
    
    def AddPlayer(self, player):
        print("New Player" + str(player.addr), player.id)
        self.players[player] = True
        
        #Sent to player on connecting
        player.Send({"action": "initial",
                     "player_id": player.id,
                     "game_map":self.game_map,
                     "game_map_decorations":self.game_map_class.game_map_decoration,
                     "current_floor": player.current_floor,
                     "health": player.health,
                     "players": dict([
                         (p.id, p.player_object.serialize()) for p in self.players])})
        self.SendPlayers()
    
    def DelPlayer(self, player):
        print("Deleting Player" + str(player.addr))
        del self.players[player]
        self.SendPlayers()
    
    def SendPlayers(self):
        self.SendToAll({"action": "players",
                        "players": dict([
                            (p.id,p.player_object.serialize()) for p in self.players])})
  
    
    def SendToAll(self, data):
        [p.Send(data) for p in self.players]
    
    def Launch(self):
        while True:
            self.Pump()

            sleep(0.0001)

# get command line argument of server, port
if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "host:port")
        print("e.g.", sys.argv[0], "localhost:31425")
    else:
        host, port = sys.argv[1].split(":")
        s = GameServer(localaddr=(host, int(port)))
        s.Launch()