import pygame as py

class Player(py.sprite.Sprite):
    def __init__(self, name, start_pos=(50,20), mass=1, speed=5):
        super().__init__()
        self.image = py.image.load("assets/player.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = start_pos

        # Constantes
        self.client_socket = None
        self.name = name

        self.mass = mass
        self.speed = speed

        # Variables
        self.velocity = py.Vector2(1,1)
        

    def get_data(self):
        data = {"position": self.rect.topleft, "velocity": (self.velocity.x, self.velocity.y)}       # Emetteur initial protocole : "data" : list position ; list velocité
        return data
    
    def get_info(self):
        info = {"name":self.name, "pos": self.rect.topleft, "mass": self.mass}                       # Emetteur initial protocole : "new" : string name ; list position ; int masse
        return info

class OtherPlayer(py.sprite.Sprite):
    def __init__(self, adress, name, start_pos, mass):
        super().__init__()
        self.image = py.image.load("assets/player.png")
        self.rect = self.image.get_rect()
        self.rect.topleft = start_pos


        # Constantes
        self.adress = adress
        self.name = name
        self.mass = mass

        # Variables
        self.velocity = py.Vector2(1,1)
