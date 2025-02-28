from threading import Thread
from time import sleep
import pygame as py
from network import connect_to_server, send_data, send_and_get_info, ReceiveThread
from game import Game

def analyse_packet_thread(packets, game: Game):
    while True:
        if len(packets) > 0:
            packet = packets.pop(0)
            head, body = packet
            
            match head:
                case "data":
                    game.update_other_player(body)

                case "new":
                    game.new_other_player(body)
                    
def send_thread(client_socket, player, sending_speed):
    while True:
        data = player.get_data()
        if send_data(client_socket, data): assert "Server down"
        sleep(sending_speed) # Fréquence d'envoi

def start_client(online=False):
    game = Game()
    if online: start_online(game, game.player)
    while True:
        for event in py.event.get():
            if event.type == py.QUIT:
                py.quit()
                return
            if event.type == py.KEYDOWN:
                if event.key==py.K_c:
                    print("Going online...")
                    start_online(game, game.player)

        game.update()
        game.dt = game.clock.tick(60)/1000

def start_online(game, player):
    client_socket = connect_to_server('6.tcp.eu.ngrok.io', 17181, with_ngrok=True)
    print("Connected") 
    all_player_info = send_and_get_info(client_socket, player.get_info())
    if all_player_info: game.initialize_other_players(all_player_info)

    receive_thread = ReceiveThread(client_socket)
    receive_thread.start()
    Thread(target=send_thread, args=(client_socket, player, 0.01)).start()

    Thread(target=analyse_packet_thread, args=(receive_thread.packet, game)).start()

start_client()