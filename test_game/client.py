from __future__ import print_function
import sys
from sys import stdin, exit
from time import sleep

from PodSixNet.Connection import connection, ConnectionListener
from game_shell import game_shell
from item import Item,Equip_slots,get_loot_table

class Client(ConnectionListener, game_shell):
    def __init__(self, host, port):
        self.Connect((host, port))

        self.Setup_character()

        self.players = {}
        game_shell.__init__(self) #Init game for client
        self.id = None
    
    def Loop(self): #Game loop
        self.Pump()
        connection.Pump()
        self.Events() #game_shell.events 
        self.Draw([p for p in self.players])
        
        if "connecting" in self.statusLabel:
            self.statusLabel = "connecting" + "".join(["." for s in range(int(self.frame / 30) % 4)])
    
    #######################    
    ### Event callbacks ###
    #######################

    #Game actions   
    def Move(self, pos):
        connection.Send({"action": "move", "position": pos, "current_floor": self.current_floor})
        
    def Use(self):
        connection.Send({"action": "use"})
    ###############################
    ### Network event callbacks ###
    ###############################
    
    def Network_initial(self, data): #This is reached by the server through:  player.Send({"action": "initial",....})
        self.players = data['players']
        self.current_floor = data['current_floor']
        self.game_map = data['game_map']
        self.id = data['player_id']
        self.game_map_decorations = data['game_map_decorations']
        self.Set_Window_Title(f"Player id: {self.id}")
        
        print(self.players)
        #Focus camera on player
        self.Set_Camera_Offset(offset_x=self.players[self.id]['position'][1],offset_y=self.players[self.id]['position'][1])
            
    def Network_move(self, data): #This is reached by the server through:  player.Send({"action": "initial",....})
        old_x, old_y = self.players[data['id']]['position']
        self.players[data['id']]['position'] = (old_x + data['position'][0], old_y + data['position'][1])
        
    def Network_use(self,data):     
        if 'move' in data.keys():
            if data['move'] == 'down':
                self.players[data['id']]['current_floor'] +=1
                self.players[data['id']]['position'] = data['position']
            
            if data['move'] == 'up':
                self.players[data['id']]['current_floor'] -=1
                self.players[data['id']]['position'] = data['position']

        elif 'equipped' in data.keys():
            slot = data["equipped"]["slot"]
            print(data["equipped"])
            equipped_tile = data["equipped"]["on_equipped_tile"]
            self.players[data['id']]['inventory'][slot] = equipped_tile
            self.game_map_decorations = data["updated_decorations"]

    
    def Network_editmap(self,data):
        print(f"player {data['id']} edited the map!")
        self.game_map[data['floor']] = data['edited_map'][data['floor']]
    
    def Network_nickname(self,data):
        print(f"{data['nickname']} ({data['id']}) has joined!")
        self.players[data['id']]["name"] = data["nickname"]
        self.players[data['id']]["base_character_tile"] = data["character"]

    def Setup_character(self):

        race_dict = {
            "human":{
                "male":(7,80),
                "female":(6,80)
                },
            "minotaur":{
                "male":(16,80),
                "female":(14,80)
                },
            "gargoyle":{
                "male":(63,80),
                "female":(62,80)
                },
            "lizardian":{
                "male":(3,81),
                "female":(2,81)
                }
            }
        print("Greetings adventurer")
        player_name   = input("Whats your name? >")
        player_race   = input("What race are you? (human, minotaur, gargoyle, lizardian) >")
        player_gender = input("What gender are you? male or female? >")

        connection.Send({"action": "nickname", "nickname": player_name, "character":race_dict[player_race][player_gender]})
    
    #Updates to players
    def Network_players(self, data): # self.SendToAll({"action": "players", "players": dict([(p.id, p.color) for p in self.players])})
        self.playersLabel = str(len(data['players'])) + " players"
        mark = []
        for i in data['players']:
            if not i in self.players: # New player
                self.players[i] = {
                    'position': data['players'][i]['position'],
                    'current_floor': data['players'][i]['current_floor'],
                    'inventory': data['players'][i]['inventory'],
                    'health': data['players'][i]['health'],
                    'base_character_tile': data['players'][i]['base_character_tile'],
                    'name': data['players'][i]['name']               
                    }
        
        for i in self.players: # Player is gone
            if not i in data['players'].keys():
                mark.append(i)
        
        for m in mark: #If there are players who are gone, remove them
            del self.players[m]
    
    def Network(self, data):
        #print('network:', data)
        pass
    
    def Network_connected(self, data):
        self.statusLabel = "connected"
    
    def Network_error(self, data):
        print(data)
        import traceback
        traceback.print_exc()
        self.statusLabel = data['error'][1]
        connection.Close()
    
    def Network_disconnected(self, data):
        self.statusLabel += " - disconnected"

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Usage:", sys.argv[0], "host:port")
        print("e.g.", sys.argv[0], "localhost:31425")
    else:
        host, port = sys.argv[1].split(":")
        c = Client(host, int(port))
        while 1:
            c.Loop()
            sleep(0.001)