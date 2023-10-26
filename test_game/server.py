from __future__ import print_function

import sys
from time import sleep, localtime
from random import randint
from weakref import WeakKeyDictionary

from PodSixNet.Server import Server
from PodSixNet.Channel import Channel

from game_map import Game_map
    
game_map = Game_map()
class ServerChannel(Channel):
    """
    This is the server representation of a single connected client (a player).
    """
    def __init__(self, *args, **kwargs):
        Channel.__init__(self, *args, **kwargs)
        self.id = str(self._server.NextId())
        intid = int(self.id)
        self.color = [(intid + 1) % 3 * 84, (intid + 2) % 3 * 84, (intid + 3) % 3 * 84] #tuple([randint(0, 127) for r in range(3)])
        self.game_map_class = game_map
        
        self.inventory = {"cloak": (16,84), "chest":(57,82), "legs":(38,93),"hands":(57,84) ,"head":(39,92),"feet":(60,83), "hand1":(42,90),"hand2":(48,85)}
        #self.inventory = {"cloak": None, "chest": None, "legs":None,"hands":None ,"head":None,"feet": None, "hand1": None,"hand2": None}
        
        self.current_floor = 0
        self.game_map = self.game_map_class.Get_Map()
        
        #Set initial position
        self.position = self.game_map_class.Get_spawn_point(current_floor=self.current_floor)
        
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
        new_position = (self.position[0] + data['position'][0], self.position[1] + data['position'][1])
        if self.Valid_move(new_position):
            self.position = (self.position[0] + data['position'][0], self.position[1] + data['position'][1])
            print(self.position)
            self.PassOn(data)
            
    def Network_use(self,data):
        x,y = self.position
        if self.game_map[self.current_floor][y][x] == ">": #Player is going down one level
            self.current_floor = self.current_floor + 1
            self.position = self.game_map_class.Get_spawn_point(current_floor=self.current_floor)
            data["move"] = "down"
            data["position"] = self.position
            self.PassOn(data)
        elif self.game_map[self.current_floor][y][x] == "<": #Player is going up one level
            self.current_floor = self.current_floor - 1
            self.position = self.game_map_class.Get_stair_up_point(current_floor=self.current_floor)
            data["move"] = "up"
            data["position"] = self.position
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
                     "players": dict([
                         (p.id,{
                           "color": p.color,
                           "position": p.position,
                           "current_floor": p.current_floor,
                           "inventory": player.inventory
                           }) for p in self.players])})
        self.SendPlayers()
    
    def DelPlayer(self, player):
        print("Deleting Player" + str(player.addr))
        del self.players[player]
        self.SendPlayers()
    
    def SendPlayers(self):
        self.SendToAll({"action": "players",
                        "players": dict([
                            (p.id,
                             {"color": p.color,
                              "position": p.position,
                              "current_floor": p.current_floor,
                              "inventory": p.inventory
                              }
                             ) for p in self.players])})
    
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