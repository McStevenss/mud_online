from sys import exit
from os import environ
import os
import pygame
from pygame.locals import *
#SCREENSIZE = (640, 480)
SCREENSIZE = (1280, 960)



environ['SDL_VIDEO_CENTERED'] = '1'
pygame.init()
screen = pygame.display.set_mode(SCREENSIZE)

#test_screen = pygame.Surface((640,480))

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
                if event.key == pygame.K_UP:
                    self.Move(UP)
                if event.key == pygame.K_RIGHT:
                    self.Move(RIGHT)               
                if event.key == pygame.K_LEFT:
                    self.Move(LEFT)                 
                if event.key == pygame.K_DOWN:
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
        screen.fill(Color('black'))
        if self.game_map != None and self.current_floor != None and self.game_map_decorations != None:
            local_x = self.players[self.id]['position'][0]
            local_y = self.players[self.id]['position'][1]
            self.Set_Camera_Offset(offset_x=local_x*self.tileSize ,offset_y=local_y*self.tileSize)
            for y, row in enumerate(self.game_map[self.players[self.id]['current_floor']]):
                for x, char in enumerate(row):
                    
                    pos_x,pos_y = self.ConvertPos(x,y)
                    #Draw map
                    screen.blit(self.sprite_dict[char], (pos_x, pos_y))
            
            #{'position': (26, 20), 'decoration_tile': (32, 38)}
            for decoration in self.game_map_decorations:
                dec_x, dec_y = self.ConvertPos(decoration["position"][0],decoration["position"][1])
                screen.blit(self.image_at(decoration["decoration_tile"][0],decoration["decoration_tile"][1]), (dec_x, dec_y))
            #Draw players
            self.Draw_Players(players)
                    
        #scaled_win = pygame.transform.scale(screen, screen.get_size())
        #screen.blit(scaled_win, (0, 0))            
        pygame.display.flip()
        self.frame += 1
                    
        
    def Draw_Players(self,players):
        for color, position, id, inventory in players:
            if self.players[id]["current_floor"] == self.players[self.id]["current_floor"]: #Only draw players on the same floor as us
                
                pos_x,pos_y = self.ConvertPos(position[0],position[1])
                draw_order = ["cloak","player","legs","chest","feet","head","hand1","hand2"]
                
                for part in draw_order:           
                    if part == "player":
                        screen.blit(self.image_at(9,80), (pos_x, pos_y))
                    
                    elif inventory[part] == None:
                        continue
                    else:
                        screen.blit(self.image_at(inventory[part][0],inventory[part][1]), (pos_x, pos_y))   
