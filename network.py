import socket
import json
import threading
from time import sleep

# Partie serveur
def handle_client(client_socket, client_address, clients):
    # Reçu des informations d'initialisation (Au moins un nom)
    player_info = receive_packet(client_socket)
    player_info = json.loads(player_info.decode())
    player_info['address'] = tuple(client_address)      # Protocole "data" : tuple adresse

    
    # Envoi les infos des autres joueurs au client, et client aux autres joueurs
    all_clients_info = []
    for client, info in clients:
        all_clients_info.append(info)
        client.sendall(json.dumps(("new", player_info)).encode() + b'\n')   # Client envoyé aux autres clients
        print("Envoyé à ", info['name'], json.dumps(("new", player_info)))

    if clients: 
        client_socket.sendall(json.dumps(all_clients_info).encode() + b'\n')   # Autres clients envoyés au client
        print("Envoyé à ", player_info['name'], json.dumps(("new", all_clients_info)))
    else: 
        client_socket.sendall(json.dumps(None).encode() + b'\n')
        print("Envoyé à ", player_info['name'], json.dumps(None))

    # Ajout du client dans clients[]
    clients.append((client_socket, player_info))
    print(f"{player_info['name']} joined the party")

    # Boucle réception paquets (data) + Enoie à clients[]
    try:
        buffer=b''
        while True:
            data = client_socket.recv(1024)
            if not data:
                break
            buffer += data
            while b'\n' in buffer:
                packet, buffer = buffer.split(b'\n', 1)

                head, packet = json.loads(packet.decode())
                packet['address'] = player_info['address']

                match head:
                    case "data":
                        # Envoi des données aux autres joueurs (ajoute l'adresse) - "data"
                        for client, data in clients:
                            if client != client_socket:
                                client.sendall(json.dumps(("data", packet)).encode() + b'\n')
    finally:
        print(f"{player_info['name']} left the party")
        clients.remove((client_socket, player_info))
        client_socket.close()

def start_server(host='', port=65432):
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((host, port))
    server.listen(5)
    print(f"[Serveur] En attente de connexions sur {host}:{port}...")
    clients = []

    while True:
        client_socket, client_address = server.accept()
        threading.Thread(target=handle_client, args=(client_socket, client_address, clients)).start()

# Partie client
def send_data(client_socket, data): # Envoi data aux autres joueurs (ce qu'on veut) - "data"
    try:
        client_socket.sendall(json.dumps(("data", data)).encode() + b'\n')
        return False
    except ConnectionAbortedError:
        return True

def send_and_get_info(client_socket, info): # Envoi informations d'initialisation au serveur et autres joueurs (au moins "name")
    client_socket.sendall(json.dumps(info).encode() + b'\n')
    msg = json.loads(receive_packet(client_socket).decode())
    print(f"Server : {msg}")
    return msg

class ReceiveThread(threading.Thread): # Reçu des paquets serveur dans ReceiveThread.packets - "new" = info ; "data" = data
    def __init__(self, client_socket):
        threading.Thread.__init__(self)
        self.client_socket = client_socket
        self.buffer = b''  # Initialisation du buffer vide
        self.packet = []
    def run(self):
        while True:
            data = self.client_socket.recv(1024)  # Lire les données
            if not data:
                break  # Si aucune donnée reçue, on sort de la boucle

            self.buffer += data  # Ajouter les données au buffer
            while b'\n' in self.buffer:
                msg, self.buffer = self.buffer.split(b'\n', 1)
                self.packet.append(json.loads(msg.decode()))

def connect_to_server(host='127.0.0.1', port=65432, with_ngrok=True):
    if with_ngrok: #Pour l'utilisation de ngrok
        # Serveur ngrok tcp 65432
        print("Give the adress number + port in format \"x ppppp\"")
        a_p = input().split(' ')
        if a_p == ['']: a_p = ['0','14788']
        print(a_p)
        host, port = f"{a_p[0]}.tcp.eu.ngrok.io", int(a_p[1])
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((host, port))
    return client_socket



def receive_packet(client_socket, buffer=b'', buffer_size=1024, onepacket=True):
    buffer = buffer

    while True:
        # Reçu des données du client (Ce qu'on veut)
        data = client_socket.recv(buffer_size)
        if not data:
            if onepacket: return None
            else: return None, None
        buffer += data

        if b'\n' in buffer:
            packet, buffer = buffer.split(b'\n', 1)
            if onepacket: return packet
            else: return packet, buffer