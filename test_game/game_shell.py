from sys import exit
from os import environ
import os
import pygame
from pygame.locals import *
from item import Item,Equip_slots,get_loot_table

SCREENSIZE = (640, 480)
#SCREENSIZE = (1280, 960)



environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
screen = pygame.display.set_mode((1580, 960)) #Game screen will use (1280, 960), the other 300 pixels is gui

game_screen = pygame.Surface(SCREENSIZE)
gui_screen = pygame.Surface((300,960))


pygame.font.init()
fnt = pygame.font.SysFont("Arial", 14)
txtpos = (100, 90)

#MOVEMENT MACROS
UP = (0,-1)
RIGHT = (1,0)
LEFT = (-1,0)
DOWN = (0,1)
################

#SPRITES
spritesheet_path = os.path.join('textures', 'ProjectUtumno_full.png')
spritesheet = pygame.image.load(spritesheet_path).convert_alpha()

###########
floor_sprite = pygame.image.load(os.path.join('textures', 'floor.png')).convert_alpha()
p0_sprite = pygame.image.load(os.path.join('textures', 'p0.png'))
wall_sprite = pygame.image.load(os.path.join('textures', 'wall.png'))
door_sprite = pygame.image.load(os.path.join('textures', 'door.png'))
door_open_sprite = pygame.image.load(os.path.join('textures', 'door_open.png'))
money_sprite = pygame.image.load(os.path.join('textures', 'money.png'))
reaper_sprite = pygame.image.load(os.path.join('textures', 'reaper.png'))
ukn_sprite = pygame.image.load(os.path.join('textures', 'ukn.png'))

ladder_up_sprite = pygame.image.load(os.path.join('textures', 'ladder_up.png'))
ladder_down_sprite = pygame.image.load(os.path.join('textures', 'ladder_down.png'))





#Setup Window icon and title
pygame.display.set_caption("Connecting...")
pygame.display.set_icon(reaper_sprite)

#python pyinstaller.py --icon=icon.ico for icon when the game is built with pyinstaller :)


class game_shell:
    def __init__(self):
        self.statusLabel = "connecting"
        self.playersLabel = "0 players"
        self.frame = 0
        self.down = False
        
        self.current_floor = None #Set in initial
        self.game_map = None #Set in initial
        self.game_map_decorations = None #Set in initial
        self.tileSize = 32
  
        self.wall_color = (255,0,0)
        self.ground_color = (64,64,64)
        self.sprite_dict = {
               ".": self.image_at(9,4),
               "#": self.image_at(11,14),
               "+": self.image_at(56,1),
               "'": self.image_at(59,1),
               "$": money_sprite,
               " ": self.image_at(18,0),
               "<": self.image_at(54,11),
               ">": self.image_at(53,11)}
        
        self.font = pygame.font.Font('freesansbold.ttf', 32)
        self.small_font = pygame.font.Font('freesansbold.ttf', 12)



    def Set_Camera_Offset(self,offset_x,offset_y):
        self.camera_offset_x = (SCREENSIZE[0] // 2) - offset_x #((len(self.game_map[0]) * self.tileSize) // 2) 
        self.camera_offset_y = (SCREENSIZE[1] // 2) - offset_y #((len(self.game_map) * self.tileSize) // 2)
        #print("Set offset",self.camera_offset_x*self.tileSize,self.camera_offset_y*self.tileSize)
        
    def ConvertPos(self,x,y):
        screen_y = y * self.tileSize + self.camera_offset_y #(self.screen_height // 2) - ((len(self.map_data) * self.spritesheet.tilesize) // 2)
        screen_x = x * self.tileSize + self.camera_offset_x #(self.screen_width // 2) - ((len(self.map_data[0]) * self.spritesheet.tilesize) // 2)

        return screen_x,screen_y
    
    def Events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == 27):
                exit()
            
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    self.Move(UP)
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    self.Move(RIGHT)               
                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    self.Move(LEFT)                 
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    self.Move(DOWN) 
                    
                if event.key == pygame.K_RETURN:
                    self.Use()
                    
    def Set_Window_Title(self, text):
        pygame.display.set_caption(text)
    
        
    def image_at(self, x, y):
        """Load a specific image from a specific rectangle."""
        # Load image from x, y, x + offset, y + offset.
        rect = pygame.Rect(x * self.tileSize, y * self.tileSize, self.tileSize, self.tileSize)
        image = pygame.Surface(rect.size,pygame.SRCALPHA, 32)
        image.blit(spritesheet, (0, 0), rect)
        return image
    
            
    def Draw(self, players):
        game_screen.fill(Color('black'))
        if self.game_map != None and self.current_floor != None and self.game_map_decorations != None:
            local_x = self.players[self.id]['position'][0]
            local_y = self.players[self.id]['position'][1]
            self.Set_Camera_Offset(offset_x=local_x*self.tileSize ,offset_y=local_y*self.tileSize)
            for y, row in enumerate(self.game_map[self.players[self.id]['current_floor']]):
                for x, char in enumerate(row):        
                    pos_x,pos_y = self.ConvertPos(x,y)
                    #Draw map
                    game_screen.blit(self.sprite_dict[char], (pos_x, pos_y))

            self.Draw_Decorations()
            self.Draw_Players(players)
            self.Draw_Gui()
                    
        scaled_win = pygame.transform.scale(game_screen, (1280, 960))
        #scaled_win = pygame.transform.scale(game_screen, screen.get_size())
        screen.blit(scaled_win, (0, 0))    
        screen.blit(gui_screen,(1280, 0))        
        pygame.display.flip()
        self.frame += 1

    def Draw_Decorations(self):
        for decoration in self.game_map_decorations:
            dec_x, dec_y = self.ConvertPos(decoration["position"][0],decoration["position"][1])
            game_screen.blit(self.image_at(decoration["decoration_tile"][0],decoration["decoration_tile"][1]), (dec_x, dec_y))            
    
    def Draw_Players(self,players):
        for id in players:
            if self.players[id]["current_floor"] == self.players[self.id]["current_floor"]: #Only draw players on the same floor as us
                position = self.players[id]["position"]
                inventory = self.players[id]["inventory"]
                base_character_tile = self.players[id]["base_character_tile"]

                pos_x,pos_y = self.ConvertPos(position[0],position[1])
                draw_order = ["cloak","player","legs","chest","hands","feet","head","hand1","hand2"]
                
                for part in draw_order:           
                    if part == "player":
                        game_screen.blit(self.image_at(base_character_tile[0],base_character_tile[1]), (pos_x, pos_y))
                    
                    elif inventory[part] == None:
                        continue
                    else:
                        game_screen.blit(self.image_at(inventory[part][0],inventory[part][1]), (pos_x, pos_y))   


    def Draw_Gui(self):

        for players, attributes in self.players.items():
            pos_x,pos_y = self.ConvertPos(attributes["position"][0],attributes["position"][1])
            hp_text = self.small_font.render(f"{attributes['health']}", True, Color("green"), Color("blue"))

            game_screen.blit(hp_text, (pos_x+5,pos_y+32))

        
        name_text = self.font.render(f"Name:{self.players[self.id]['name']}", True, Color("green"))
        textRect = name_text.get_rect()
        textRect.topleft = (15,0)
        gui_screen.blit(name_text, textRect)

        health_text = self.font.render(f"Health:{self.players[self.id]['health']}", True, Color("green"))
        textRect = health_text.get_rect()
        textRect.topleft = (15,50)
        gui_screen.blit(health_text, textRect)

     



