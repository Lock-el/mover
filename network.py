import socket
import json
import threading
from queue import Queue
from time import sleep

# Partie serveur
def handle_client(client_socket, client_address, clients):
    # Reçu des informations d'initialisation (Au moins un nom)
    init_data = receive_one_packet(client_socket)
    if init_data: init_data = json.loads(init_data.decode())
    else: 
        print("Pas d'info")
        return None
    
    init_data['address'] = tuple(client_address)      # Protocole "data" : tuple adresse

    
    # Envoi les infos des autres joueurs au client, et client aux autres joueurs
    all_clients_init_data = []
    for client, info in clients:
        all_clients_init_data.append(info)
        client.sendall(json.dumps(("new", init_data)).encode() + b'\n')   # Client envoyé aux autres clients

    if clients: 
        client_socket.sendall(json.dumps(all_clients_init_data).encode() + b'\n')   # Autres clients envoyés au client
    else: 
        client_socket.sendall(json.dumps("no client").encode() + b'\n')

    # Ajout du client dans clients[]
    clients.append((client_socket, init_data))
    print(f"{init_data['name']} joined the party")

    # Boucle réception paquets (data) + Enoie à clients[]
    try:
        buffer=b''
        while True:
            try:
                data = client_socket.recv(1024)
            except ConnectionResetError: break
            if not data:
                break
            buffer += data
            while b'\n' in buffer:
                packet, buffer = buffer.split(b'\n', 1)

                head, body = json.loads(packet.decode())
                body['address'] = init_data['address']

                packet_to_send = json.dumps((head, body))

                if head=="msg": print(body['msg'])

                for client, data in clients:
                    if client != client_socket:
                        client.sendall(packet_to_send.encode() + b'\n')
                    else:
                        client.sendall(b'')

                
    finally:
        clients.remove((client_socket, init_data))
        client_socket.close()
        for client, info in clients:
            client.sendall(json.dumps(("del", init_data['address'])).encode() + b'\n')   # Protocole "del" : list adresse
        print(f"{init_data['name']} left the party")

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

class ClientConnexionThread(threading.Thread):
    """Thread qui gère la connexion du client.

    Initialisation : 
        Se connecte au serveur de l'adresse
        Envoie les données d'initialisation
        Reçois les données d'initialisation des autres clients (None si aucun autre client connecté)

    Boucle d'execution :
        Reçois les paquets du serveur et les stoque dans self.packets
    
    Fonction send_packet :
        Envoie un paquet au serveur et, donc, aux autres clients. Doit être un tuple contenant l'en-tête et le contenu du paquet
        
    """

    def __init__(self, client_address, client_init_data):
        threading.Thread.__init__(self)

        self.client_socket = connect_to_server(client_address)
        self.connected = self.client_socket is not None

        if self.connected: self.other_client_init_data = send_and_get_init_data(self.client_socket, client_init_data)


        self.clients_data = None
        self.packets = Queue()


    def run(self):
        self.buffer = b''  # Initialisation du buffer vide
        while self.connected:
            # Receive
            if self.client_socket:
                data = self.client_socket.recv(1024)  # Lire les données
                if not data:
                    print("Server down")
                    self.connected=False
                    break  # Si aucune donnée reçue, on sort de la boucle

                self.buffer += data  # Ajouter les données au buffer
                while b'\n' in self.buffer:
                    packet, self.buffer = self.buffer.split(b'\n', 1)
                    head, body = json.loads(packet.decode())
                    self.packets.put((head, body))
            else:
                print("Disconnected")
                break
        self.client_socket.close()

    def send_packet(self, data): # Envoi data aux autres joueurs (ce qu'on veut) - "data"
        try:
            self.client_socket.sendall(json.dumps(data).encode() + b'\n')
        
        except ConnectionAbortedError:
            print("Server down")
            self.connected = False

def connect_to_server(address):
    try:
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print("Connecting...")
        client_socket.connect(address)
        print("Connected")
        return client_socket
    except:
        print("Address invalid")
        return None
    
def send_and_get_init_data(client_socket: socket.socket, init_data): # Envoi informations d'initialisation au serveur et autres joueurs (au moins "name")
    client_socket.sendall(json.dumps(init_data).encode() + b'\n')
    msg = json.loads(receive_one_packet(client_socket).decode())
    if msg=='no client': return None
    else: return msg




# Client and Server
def receive_one_packet(client_socket, buffer_size=1024):
    buffer = b''

    while True:
        # Reçu des données du client (Ce qu'on veut)
        data = client_socket.recv(buffer_size)  # Lire les données

        if not data:
            return None
        buffer += data

        if b'\n' in buffer:
            packet, buffer = buffer.split(b'\n', 1)
            return packet