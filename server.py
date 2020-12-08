# Import threading libraries
import threading
import queue
import time

# Import sockets libraries
import socket
import select

#Import DB library
import sqlite3

# Import display library
from datetime import datetime

# Import Class and Manager files
from ClientClass import *
from RoomClass import *
import client_functions
import server_functions
from cyphering import *

# Global variables
clients_connectes = []
(returned_string, client_name_private) = ("","")
private_bool = False
end_private_message = "end"
Rooms=[]
key = "salut"



def read_kbd_input(inputQueue):
    print('Ready for keyboard input:')
    while (True):
        # Receive keyboard input from user.
        input_str = input()
        
        # Enqueue this input string.
        inputQueue.put(input_str)

def creation_database():
    conn = sqlite3.connect('database_chat.db',check_same_thread=False)
    print ("Opened database successfully")

    conn.execute('''CREATE TABLE IF NOT EXISTS user
            (USERNAME      TEXT    PRIMARY KEY     NOT NULL,
            PASSWORD        CHAR(50));''')
    print ("Table created successfully")
    return conn

def login_register(connexion_avec_client, infos_connexion,conn):
    global clients_connectes
    msg = b""
    response=""
    client_already_connected = True

    while(client_already_connected):
        while(response != "1" and response != "2"):
            msg = "Bienvenue, appuyez sur 1 pour vous connecter ou 2 pour creer un compte"
            Send_Message(msg, key, connexion_avec_client)
            response = Receive_Message(key, connexion_avec_client).decode()
        

        if(response == "1"):
            unconnected = True
            client_already_connected = False
            while(unconnected):
                msg = "Username :"
                Send_Message(msg, key, connexion_avec_client)
                username = Receive_Message(key, connexion_avec_client).decode()
                for client in clients_connectes:
                    if (client.username == username):
                        client_already_connected = True
                        msg = "User already connected, try another account if you have one or create a new one if you really want to be connected. You will now be redirected to the welcome message\n\n"
                        Send_Message(msg, key, connexion_avec_client)
                        break
                if (client_already_connected):
                    response = "" #on reinitialise la reponse sinon on ne re-rentrera pas dans le premier while verifiant la reponse du user
                    break
                msg = "Password :"
                Send_Message(msg, key, connexion_avec_client)
                password = Receive_Message(key, connexion_avec_client).decode()
                cursor = conn.execute("SELECT * FROM user WHERE USERNAME = '{}' AND PASSWORD = '{}'".format(username,password))
                conn.commit()
                if(cursor.fetchone() != None):
                    msg = "Connexion reussie, bienvenue dans le chat public"
                    Send_Message(msg, key, connexion_avec_client)
                    unconnected = False
                else:
                    msg = "Wrong credentials\n"
                    Send_Message(msg, key, connexion_avec_client)
                    unconnected = False #on laisse la possibilité de se créer un compte si jamais
                    response = ""
                    client_already_connected=True
                
                    
        if(response == "2"):
            unconnected = True
            client_already_connected = False
            while(unconnected):
                try:
                    username = " "
                    while(' ' in username):
                        msg = "Username :"
                        Send_Message(msg, key, connexion_avec_client)
                        username = Receive_Message(key, connexion_avec_client).decode()
                        if (' ' in username):
                            Send_Message("Username must not contain spaces\n", key, connexion_avec_client)
                    msg = "Password :"
                    Send_Message(msg, key, connexion_avec_client)
                    password = Receive_Message(key, connexion_avec_client).decode()
                    conn.execute("INSERT INTO user (USERNAME,PASSWORD) VALUES ('{}','{}')".format(username,password))
                    conn.commit()
                    unconnected = False
                    msg = "Creation de compte reussie, bienvenue dans le chat public"
                    Send_Message(msg, key, connexion_avec_client)
                except sqlite3.IntegrityError:
                    msg = "Username already existing"
                    Send_Message(msg, key, connexion_avec_client)
                    unconnected = False #on laisse la possibilité de se créer un compte si jamais
                    response = ""
                    client_already_connected=True
                 
    CurrentClient = Client(username,infos_connexion[0],infos_connexion[1],connexion_avec_client)
    clients_connectes.append(CurrentClient)
    print("\nUser '{}' connected at {} from @{}:{} \n".format(CurrentClient.username,datetime.now(),CurrentClient.IP,CurrentClient.port))

def private_server_client(clients_connectes,input_str):
    global returned_string, private_bool, client_name_private
    for client in clients_connectes:
        if(client.username == client_name_private):
            if (input_str == end_private_message):
                print("You ended the conversation with '{}' ".format(client_name_private))
                (returned_string, client_name_private) = ("","")
                private_bool = False
            else:
                msg = "PRIVATE MESSAGE FROM SERVER : " + input_str
                Send_Message(msg, key, client.socket)

def Create_Room_Server(client, room_name):
    global Rooms
    new_room=Room(room_name,client)
    clients_connectes.remove(client)
    while(True):
        choice=""
        while(choice!="1" and choice !="2"):
            msg="\nType 1 to add a new client or 2 to finish the creation: "
            Send_Message(msg, key, client.socket)
            choice= Receive_Message(key, client.socket).decode()
        if(choice=="1"):
            client_connected_existed=False
            client_functions.Check_client_functions("#ListU", client, clients_connectes,  Rooms)
            Send_Message("Please, write one of the name mentionned above: ", key, client.socket)
            #client.socket.send(b"Please, write one of the name mentionned above: ")
            client_typed= Receive_Message(key, client.socket).decode()
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
                choice= Receive_Message(key, client.socket).decode()
                if(choice=="exit"):
                    msg_exit="Your room wasn't created, you are now back in the chat.\n"
                    Send_Message(msg_exit, key, client.socket)
                    break
    clients_connectes.append(client)

def main():
    #Define global variables
    global clients_connectes, returned_string, private_bool, client_name_private


    #! Set up socket variables
    hote = ''
    port = 12800
    connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion_principale.bind((hote, port))
    connexion_principale.listen(50)
    

    #! DATABASE CREATION
    conn = creation_database()
    #Keyboard input queue to pass data from the thread reading the keyboard inputs to the main thread.
    inputQueue = queue.Queue()

    # Create & start a thread to read keyboard inputs.
    # Set daemon to True to auto-kill this thread when all other non-daemonic threads are exited. This is desired since
    # this thread has no cleanup to do, which would otherwise require a more graceful approach to clean up then exit.
    inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
    inputThread.start()


    #TODO Main loop
    while (True):                

        # On va vérifier que de nouveaux clients ne demandent pas à se connecter
        # Pour cela, on écoute la connexion_principale en lecture
        # On attend maximum 50ms
        try:
            connexions_demandees, wlist, xlist = select.select([connexion_principale], [], [], 0.05)
        
            for connexion in connexions_demandees:
                connexion_avec_client, infos_connexion = connexion.accept()
                # On lance un thread qui va demander au client ses identifiants ou de se créer un compte
                (threading.Thread(target=login_register, args=(connexion_avec_client,infos_connexion,conn,), daemon=True)).start()
        except :
            pass


        #! Read keyboard inputs
        if (inputQueue.qsize() > 0):
            input_str = inputQueue.get()

            #! Check if the server wants to talk to a client
            if (private_bool):
                private_server_client(clients_connectes,input_str)

            #TODO Insert your code here to do whatever you want with the input_str.
            try: #S'il n'y a pas de try except, le code va planter si on appuie juste sur entrée
                if (input_str[0] == "#"):
                    (returned_string, client_name_private) = server_functions.Check_server_functions(input_str,clients_connectes,connexion_principale,connexions_demandees)
                    if (returned_string == "exit"):              
                        break            
                    if (returned_string == "private_conv"):
                        private_bool = True
                        print("You are now speaking to '{}'\n".format(client_name_private))
                        print("Write 'end' to end the private conversation")
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
                # Empecher un crash si un client ferme sa fenetre avec la croix
                msg_recu="" #Définition de la variable
                try:
                    msg_recu = Receive_Message(key, client.socket)
                except ConnectionResetError: #Type d'erreur soulevé quand un client ferme de force sa fenêtre
                    print("User {} forcefully deconnected".format(client.username))
                    client.socket.close() #On ferme sa socket
                    clients_connectes.remove(client) #On le retire des clients connectés
                    continue #On passe au client suivant
                
                # Peut planter si le message contient des caractères spéciaux
                msg_recu = msg_recu.decode()
                
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
                            Send_Message(msg_a_envoyer, key, receveur_client.socket) #Envoi du msg reçu sur le channel public
                    print("{} @{}:{} | '{}' > {} \n".format(datetime.now(), client.IP, client.port, client.username, msg_recu)) #Affichage côté serveur
                

        # Sleep for a short time to prevent this thread from sucking up all of your CPU resources on your PC.
        time.sleep(0.01)

# If you run this Python file directly (ex: via `python3 this_filename.py`), do the following:
if (__name__ == '__main__'): 
    main()
