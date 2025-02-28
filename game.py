import pygame as py
from entity import Player, OtherPlayer
from physic import resolve_collision

# Dimensions de la fenêtre
WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
PLAYER_SIZE = 30

class Game:
    def __init__(self):
        py.init()
        print("Enter name : ", end='')
        name = input()
        self.player = Player(name)
        self.other_players = {}
        self.screen = py.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        py.display.set_caption("Mover")
        self.clock = py.time.Clock()
        self.dt = 0

    # Pour le jeu en ligne
    def update_other_player(self, data):     # Recepteur final protocole "data" : list adress ; list position ; list velocité
        try:
            address = tuple(data['address'])
            self.other_players[address].rect.topleft =  data['position']
            self.other_players[address].velocity =      py.Vector2((data['velocity']))
        except KeyError:
            print("Demande d'update de player sans paquet de création player")
    
    def new_other_player(self, data):       # Recepteur final protocole "info" : list adress ; str name ; list start_pos ; int masse
        self.other_players[tuple(data['address'])] = OtherPlayer(tuple(data['address']), data['name'], data['pos'], data['mass'])
    
    def initialize_other_players(self, all_player_info):
        for info in all_player_info:
            self.new_other_player(info)

    # Update du game engine
    def update(self):
        self.handle_input()
        self.update_player()
        self.fluid_other_player()
        self.draw()

    def fluid_other_player(self):
        for player in self.other_players.values():
            r=player.rect
            v=player.velocity
            r.center += v
            # Bord collide
            if r.top<0: 
                r.top=0
                v.y=0
            elif r.bottom>self.screen.get_height(): 
                r.bottom=self.screen.get_height()
                v.y=0
            if r.left<0: 
                r.left=0
                v.x=0
            elif r.right>self.screen.get_width(): 
                r.right=self.screen.get_width()
                v.x=0

    # Fonctions pour l'update du game engine
    def update_player(self):
        r=self.player.rect
        v=self.player.velocity

        r.center += v

        # Bord collide
        if r.top<0: 
            r.top=0
            v.y=0
        elif r.bottom>self.screen.get_height(): 
            r.bottom=self.screen.get_height()
            v.y=0
        if r.left<0: 
            r.left=0
            v.x=0
        elif r.right>self.screen.get_width(): 
            r.right=self.screen.get_width()
            v.x=0

        #for player in self.other_players.values():
        #    if self.player.rect.colliderect(player.rect):
        #        self.player.velocity, player.velocity = resolve_collision(self.player, player)


    def draw(self):
        self.screen.fill((0,60,60))
        self.screen.blit(self.player.image, self.player.rect)
        for player in self.other_players.values():
            self.screen.blit(player.image, player.rect)
        py.display.flip()

    def handle_input(self):
        keys = py.key.get_pressed()
        if keys[py.K_z]:
            self.player.velocity.y -= self.player.speed * self.dt
        if keys[py.K_s]:
            self.player.velocity.y += self.player.speed * self.dt
        if keys[py.K_q]:
            self.player.velocity.x -= self.player.speed * self.dt
        if keys[py.K_d]:
            self.player.velocity.x += self.player.speed * self.dt