import pygame as py
from network import ClientConnexionThread
from game import Game
from threading import Thread
from time import sleep

def start_client(online=False):
    #Flag
    running = True

    # Constantes
    WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
    FPS = 60

    NAME = "Lockel"
    if NAME == "":
        print("Enter name : ", end="")
        NAME = input()

    # Pygame
    py.init()
    screen = py.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    py.display.set_caption("Mover")

    clock = py.time.Clock()
    game = Game(screen, NAME)

    connexion_thread = None
    if online: connexion_thread = start_online(game)

    while running:
        # Event
        for event in py.event.get():
            if event.type == py.QUIT:
                running=False
                break
            
            if event.type == py.KEYDOWN:

                if event.key==py.K_c and online==False:
                    if connexion_thread is not None:
                        connexion_thread = None
                        print("Déconnecter")
                    connexion_thread = start_online(game)


                if event.key == py.K_SPACE:
                        game.player.jump()  # Appelle la fonction de saut

            if game.joystick and event.type == py.JOYBUTTONDOWN:
                if event.button == 0:
                    game.player.jump()
                elif event.button == 1:
                    game.player.rect.topleft = (50, 0)
        

        dt = clock.tick(FPS) / 1000.0
        if connexion_thread is not None: 
            if connexion_thread.connected: send_and_apply_data(game, connexion_thread)
            else: connexion_thread = None

        game.update(dt)
    print("Quitt")
    if connexion_thread is not None:
        connexion_thread.connected=False
        sleep(2)
    py.quit

def start_online(game: Game):
    address = ('7.tcp.eu.ngrok.io', 19294)
    with_ngrok=False
    if with_ngrok: #Pour l'utilisation de ngrok
            # Serveur ngrok tcp 65432
            print("Give the adress number + port in format \"x ppppp\"")
            a_p = input().split(' ')
            if a_p == ['']: a_p = ['0','14788']
            address = (f"{a_p[0]}.tcp.eu.ngrok.io", int(a_p[1]))

    connexion_thread = ClientConnexionThread(address, game.get_info())
    if connexion_thread.connected: 
        game.initialize_other_players(connexion_thread.other_client_init_data)
        connexion_thread.start()

    return connexion_thread

def send_and_apply_data(game: Game, connexion: ClientConnexionThread):
    # Send data
    if not game.update_queue.empty():                   
        connexion.send_packet(("update", game.update_queue.get()))    # paquet "update"

    elif not game.message_queue.empty():                
        connexion.send_packet(("msg", game.message_queue.get()))      # paquet "msg"

    else: 
        connexion.send_packet(("data", game.get_data()))              # paquet "data"
    
    # Analyze data
    while not connexion.packets.empty():
        packet = connexion.packets.get()
        head, body = packet
        
        match head:
            case "update":
                game.set_other_player_info(body)
            case "msg":
                game.message_from_other_player(body)
            case "data":
                game.set_other_player_data(body)

            case "new":
                game.new_other_player(body)
            case "del":
                game.del_other_player(body)

start_client()