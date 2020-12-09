# Import librairies nécessaires au threading
import threading
import queue
import time

# Import librairies nécessaires aux sockets
import socket
import select

# Import librairies DB
import sqlite3

# Import librairie pour affichage
from datetime import datetime

# Import nedded files
from ClientClass import *
from RoomClass import *
import client_functions
import server_functions
from cyphering import *

# Variables globales
clients_connectes = []
clients_awaiting_connection = []
(returned_string, client_name_private) = ("","")
private_bool = False
end_private_message = "end"
Rooms=[]
key = "salut"


'''
#* Fonction permettant d'enregistrer dans une queue les caractères tapés par le client dans la console
#* On l'utilise dans un thread pour permettre au client d'écrire à tout moment

#? inputQueue : Queue utilisée pour sauvegarder les inputs du client 
'''
def read_kbd_input(inputQueue):
    print('Ready for keyboard input:')
    while (True):
        # Receive keyboard input from user.
        input_str = input()
        
        # Enqueue this input string.
        inputQueue.put(input_str)


'''
#* Fonction permettant de se connecter à la database et la créer si elle n'existe pas encore avec les tables nécessaires
'''
def creation_database():
    conn = sqlite3.connect('database_chat.db',check_same_thread=False)
    print ("Opened database successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS user
            (USERNAME      TEXT    PRIMARY KEY     NOT NULL,
            PASSWORD        CHAR(50));''')
    print ("Table created successfully")
    return conn


'''
#* Fonction permettant de gérer le login et le register
#* Impossible de se connecter sur un utilisateur déjà logged

#? connexion_avec_client : socket du client essayant de se connecter
#? infos_connexion : informations de connexion du client
#? conn : connexion avec la database 
'''
def login_register(connexion_avec_client, infos_connexion,conn):
    global clients_connectes
    msg = b""
    response=""
    client_already_connected = True

    try:
        # On met un try car si un client est en cours de connexion alors que le server se ferme, sa socket va être fermée
        # Dès lors, toutes les fonctions Receive_Message et Send_Message vont crasher
        while(client_already_connected):
            while(response != "1" and response != "2"):

                # Empêche de répondre autre chose que 1 et 2
                msg = "Bienvenue, appuyez sur 1 pour vous connecter ou 2 pour creer un compte"
                Send_Message(msg, key, connexion_avec_client)
                response = Receive_Message(key, connexion_avec_client)
            

            if(response == "1"):
                # Si le client veut se connecter avec un compte déjà existant
                unconnected = True
                client_already_connected = False
                while(unconnected):
                    msg = "Username :"
                    # Demande de username
                    Send_Message(msg, key, connexion_avec_client)
                    username = Receive_Message(key, connexion_avec_client)
                    # Check si le client est déjà connecté
                    for client in clients_connectes:
                        if (client.username == username):
                            client_already_connected = True
                            msg = "User already connected, try another account if you have one or create a new one if you really want to be connected. You will now be redirected to the welcome message\n\n"
                            Send_Message(msg, key, connexion_avec_client)
                            break
                    if (client_already_connected):
                        response = "" 
                        # On réinitialise la réponse pour que le choix 1 ou 2 soit de nouveau proposé au client
                        break
                    msg = "Password :"
                    Send_Message(msg, key, connexion_avec_client)
                    password = Receive_Message(key, connexion_avec_client)
                    # Check du password
                    cursor = conn.execute("SELECT * FROM user WHERE USERNAME = '{}' AND PASSWORD = '{}'".format(username,password))
                    conn.commit()
                    if(cursor.fetchone() != None):
                        msg = "Connexion reussie, bienvenue dans le chat public"
                        Send_Message(msg, key, connexion_avec_client)
                        unconnected = False
                    else:
                        msg = "Wrong credentials\n"
                        Send_Message(msg, key, connexion_avec_client)
                        unconnected = False 
                        # On laisse la possibilité de se créer un compte si jamais
                        response = ""
                        client_already_connected=True
                    
            # Création de compte
            if(response == "2"):
                unconnected = True
                client_already_connected = False
                while(unconnected):
                    try:
                        username = " "
                        while(' ' in username or Room.Check_Username_Client(username,Rooms)):
                            msg = "Username :"
                            Send_Message(msg, key, connexion_avec_client)
                            username = Receive_Message(key, connexion_avec_client)
                            if (' ' in username):
                                Send_Message("Username must not contain spaces\n", key, connexion_avec_client)
                            if (Room.Check_Username_Client(username,Rooms)):
                                Send_Message("Username is the same as an existed room on the server so you have to choose another one\n", key, connexion_avec_client)
                        msg = "Password :"
                        Send_Message(msg, key, connexion_avec_client)
                        password = Receive_Message(key, connexion_avec_client)
                        conn.execute("INSERT INTO user (USERNAME,PASSWORD) VALUES ('{}','{}')".format(username,password))
                        conn.commit()
                        unconnected = False
                        msg = "Creation de compte reussie, bienvenue dans le chat public"
                        Send_Message(msg, key, connexion_avec_client)

                    except sqlite3.IntegrityError:
                        msg = "Username already existing"
                        Send_Message(msg, key, connexion_avec_client)
                        unconnected = False 
                        #On laisse la possibilité de se créer un compte si jamais
                        response = ""
                        client_already_connected=True

        # Création d'une entité client et ajout à la liste des clients connectés
        CurrentClient = Client(username,infos_connexion[0],infos_connexion[1],connexion_avec_client)
        clients_connectes.append(CurrentClient)

        # On supprime le client, dont la connexion vient d'être accepté, de la liste des clients en attente
        clients_awaiting_connection.remove(connexion_avec_client)
        # Log server
        print("\nUser '{}' connected at {} from @{}:{} \n".format(CurrentClient.username,datetime.now(),CurrentClient.IP,CurrentClient.port))


    except:
        pass
        
    
''' fonction non utilisé à ce jour mais aurait pu l'être avec Create_Room2_RF dans romm_functions.py si le tout avait été plus fonctionnel
def Create_Room_Server(client, room_name):
    global Rooms
    new_room=Room(room_name,client)
    clients_connectes.remove(client)
    while(True):
        choice=""
        while(choice!="1" and choice !="2"):
            msg="\nType 1 to add a new client or 2 to finish the creation: "
            Send_Message(msg, key, client.socket)
            choice= Receive_Message(key, client.socket)
        if(choice=="1"):
            client_connected_existed=False
            client_functions.Check_client_functions("#ListU", client, clients_connectes,  Rooms)
            Send_Message("Please, write one of the name mentionned above: ", key, client.socket)
            #client.socket.send(b"Please, write one of the name mentionned above: ")
            client_typed= Receive_Message(key, client.socket)
            for other_client in clients_connectes:
                if (other_client.username == client_typed and (other_client not in new_room.clients)):
                    new_room.clients.append(other_client)
                    client_connected_existed = True
            if(not client_connected_existed):
                msg_error="\nclient '{}' doesn't exist or is unconnected or is already in your room.\n".format(client_typed)
                Send_Message(msg_error, key, client.socket)
        else:
            if(len(new_room.clients)>=3):
                Rooms.append(new_room)
                print("The room '{}' was created successfully at {} by '{}' from @{}:{}\n".format(new_room.name,datetime.now(),client.username,client.IP,client.port))
                msg_success="Room '{}' created successfully!".format(room_name) 
                Send_Message(msg_success, key, client.socket)
                for added_client in new_room.clients:
                    if(added_client.username!=client.username):
                        msg_to_added_client="You were added to the room '{}' by '{}'".format(new_room.name, client.username)
                        Send_Message(msg_to_added_client, key, added_client.socket)     
                
                break
            else:
                msg_exit="You don't have enough clients in your room (3).\n"
                msg_exit+="If you want to exit this process, type : 'exit'.\n"
                msg_exit+="Otherwise, press any other key and then enter.\n"
                Send_Message(msg_exit, key, client.socket)
                choice= Receive_Message(key, client.socket)
                if(choice=="exit"):
                    msg_exit="Your room wasn't created, you are now back in the chat.\n"
                    Send_Message(msg_exit, key, client.socket)
                    break
    clients_connectes.append(client)
'''


def main():
    #Definition des variables globales afin de pouvoir les modifier
    global clients_connectes, returned_string, private_bool, client_name_private, clients_awaiting_connection


    #! Set up socket variables
    hote = ''
    port = 12800
    connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion_principale.bind((hote, port))
    connexion_principale.listen(50)
    

    #! DATABASE CREATION
    conn = creation_database()
    inputQueue = queue.Queue()

    # Création du thread pour récupérer les input du server
    inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
    inputThread.start()


    #* Main loop
    while (True):                

        # On va vérifier que de nouveaux clients ne demandent pas à se connecter
        # Pour cela, on écoute la connexion_principale en lecture
        # On attend maximum 50ms
        try:
            connexions_demandees, wlist, xlist = select.select([connexion_principale], [], [], 0.05)
        
            for connexion in connexions_demandees:
                connexion_avec_client, infos_connexion = connexion.accept()
                clients_awaiting_connection.append(connexion_avec_client)
                # On lance un thread qui va demander au client ses identifiants ou de se créer un compte
                (threading.Thread(target=login_register, args=(connexion_avec_client,infos_connexion,conn,), daemon=True)).start()
        except :
            pass


        #! Lecture des inputs
        if (inputQueue.qsize() > 0):
            input_str = inputQueue.get()

            try: 
                #S'il n'y a pas de try except et qu'on appuie sur entrée, le code plante
                if (input_str[0] == "#"):
                    #Vérification des commandes server
                    if (server_functions.Check_server_functions(input_str,clients_connectes,connexion_principale,clients_awaiting_connection) == "exit"):              
                        break
            except:
                pass

        # Maintenant, on écoute la liste des clients connectés
        # Les clients renvoyés par select sont ceux devant être lus (recv)
        # On attend là encore 50ms maximum
        # On enferme l'appel à select.select dans un bloc try
        # En effet, si la liste de clients connectés est vide, une exception
        # Peut être levée
        
        try:
            sockets_a_lire, wlist, xlist = select.select(Client.Liste_Sockets(clients_connectes),[], [], 0.05)
            clients_a_lire = Client.Liste_Sockets_Avec_Info(sockets_a_lire,clients_connectes)
        except:
            pass
        else:
            # On parcourt la liste des clients à lire
            for client in clients_a_lire:
                # Client est de type Client
                msg_recu="" #Définition de la variable
                # Empecher un crash si un client ferme sa fenetre avec la croix
                try:
                    msg_recu = Receive_Message(key, client.socket)
                except ConnectionResetError: #Type d'erreur soulevé quand un client ferme de force sa fenêtre
                    print("User {} forcefully deconnected".format(client.username))
                    client.socket.close() #On ferme sa socket
                    clients_connectes.remove(client) #On le retire des clients connectés
                    continue #On passe au client suivant
                
                
                #! Check client functions
                if(msg_recu[0] == "#"):
                    '''
                    if(msg_recu[1:11]=="CreateRoom"):
                        try:
                            room_creator, room_name=client_functions.Check_client_functions(msg_recu, client, clients_connectes,  Rooms)
                            (threading.Thread(target=Create_Room_Server, args=(room_creator, room_name,), daemon=True)).start()
                            #Create_Room_Server(room_creator, room_name)
                        except:
                            pass
                    else:
                    '''
                    client_functions.Check_client_functions(msg_recu, client, clients_connectes,  Rooms)
                #Si l'attribut room du client n'est pas sur public, alors on doit envoyer son message à un client en particulier
                elif(client.room!="public"):
                    for other_client in clients_connectes:
                        if(other_client.username==client.room):
                            msg_a_envoyer = "Private: '{}' > {}".format(client.username,msg_recu)
                            Send_Message(msg_a_envoyer, key, other_client.socket)
                            print("{} @{}:{} to @{}:{} | '{}' to '{}' > {} \n".format(datetime.now(), client.IP, client.port, other_client.IP, other_client.port, client.username, other_client.username, msg_recu)) #Affichage côté serveur
                    for room in Rooms:
                        if(room.name==client.room):
                            for receveur_client in room.clients:
                                if(client != receveur_client):
                                    msg_a_envoyer = "Room '{}': '{}' > {}".format(room.name,client.username,msg_recu)
                                    Send_Message(msg_a_envoyer, key, receveur_client.socket)
                            
                else:                                               
                    for receveur_client in clients_connectes:
                        if(client != receveur_client):
                            msg_a_envoyer = "Public: '{}' > {}".format(client.username,msg_recu)
                            Send_Message(msg_a_envoyer, key, receveur_client.socket) 
                            #Envoi du msg reçu sur le channel public
                    # Affichage des logs
                    print("{} @{}:{} | '{}' > {} \n".format(datetime.now(), client.IP, client.port, client.username, msg_recu)) #Affichage côté serveur
                

        # Sleep for a short time to prevent this thread from sucking up all of your CPU resources on your PC.
        time.sleep(0.01)

# If you run this Python file directly (ex: via `python3 this_filename.py`), do the following:
if (__name__ == '__main__'): 
    main()
