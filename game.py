import pygame as py
from queue import Queue
from entity import Player, OtherPlayer
from physic import resolve_collision, bord_collision



class Game:
    def __init__(self, screen, name):
        # Initialisation du joystick
        self.joystick = None
        if py.joystick.get_count() > 0:
            self.joystick = py.joystick.Joystick(0)
            self.joystick.init()
            print(self.joystick.get_name(), " connected.")
        else:
            print("Aucun joystick détecté.")

        self.screen = screen

        # Charger l'image d'arrière-plan au format JPG
        self.background = py.Surface((1280,720))
        self.background.fill((0, 50, 70))  # Couleur par défaut pour visualiser l'objet

        self.default_font = py.font.Font(None, 20)


        self.update_queue = Queue()
        self.message_queue = Queue()

        self.other_players = {}

        self.player = Player(self.screen, self.joystick)

        self.name = name


    # Update du game engine
    def update(self, dt):
        self.player.update(dt)
        self.fluid_other_player()

        self.draw(dt)




    def draw(self, dt):
        self.screen.blit(self.background, (0, 0))  # Afficher l'arrière-plan

        self.screen.blit(self.player.image, self.player.rect)
        for player in self.other_players.values():
            self.screen.blit(player.image, player.rect)

        self.screen.blit(self.default_font.render(f"FPS : {round(1/dt,1)}", True, (0,0,0)), (0,0))
        
        py.display.flip()


    def fluid_other_player(self):
        for player in self.other_players.values():
            player.rect.center += player.velocity
            # Bord collide
            bord_collision(self.screen, player.rect, player.velocity)

    
    # Application des paquets
    def initialize_other_players(self, all_player_info):
        if all_player_info:
            print("Joueur présents dans la partie : ")
            for info in all_player_info:
                self.new_other_player(info, with_message=False)
                print(f"{info['name']} | ", end='')
            print('')
        else : print("Premier joueur du serveur !")


    def set_other_player_data(self, data):     # Recepteur final protocole "data" -> dict: list address ; list position ; list velocité
        player = self.other_players[tuple(data['address'])]
        player.rect.topleft =  data['position']
        player.velocity =      py.Vector2((data['velocity']))

    def set_other_player_info(self, data):      # Recepteur final protocole "update" -> dict: list address ; str attribut_name ; type_of_attribut attribut_value
        setattr(self.other_players[tuple(data['address'])], data['name'], data['value'])

    def message_from_other_player(self, data):  # Recepteur final protocole "msg" -> dict: list address ; str message
        print(f"{self.other_players[tuple(data['address'])].name} : {data['msg']}")
    
    def new_other_player(self, data, with_message=True):       # Recepteur final protocole "info" -> dict: list address ; str name ; list start_pos ; int masse
        if with_message: print(f"{data['name']} joined the party")
        self.other_players[tuple(data['address'])] = OtherPlayer(tuple(data['address']), data['name'], data['pos'], data['mass'])

    def del_other_player(self, data):       # Recepteur final protocole "del" -> list: address
        print(f"{self.other_players[tuple(data)].name} left the party")
        del self.other_players[tuple(data)]
    

    # Application protocole d'envoi paquets
    def get_data(self):
        data = {"position": self.player.rect.topleft, "velocity": (self.player.velocity.x, self.player.velocity.y)}       
        return data     # Emetteur initial protocole : "data" -> dict: list position ; list velocity
    
    def get_info(self):
        info = {"name":self.name, "pos": self.player.rect.topleft, "mass": self.player.mass}
        return info     # Emetteur initial protocole : "new" -> dict: string name ; list pos ; int mass
    
    
    def set_attribut(self, attribut_name, attribut_value):
        setattr(self.player, attribut_name, attribut_value)
        update = {"name":attribut_name, "value":attribut_value}
        self.update_queue.put(update)
                        # Emetteur initial protocole : "update" -> dict: str name (de l'attribut) ; type_of_attribut value
    
    def send_message(self, msg):                                                                  
        message = {"msg": msg}
        self.message_queue.put(message)
                        # Emetteur initial protocole "msg" -> dict: str msg
        
