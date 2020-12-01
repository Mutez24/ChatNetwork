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
import client_functions
import server_functions

# Global variables
clients_connectes = []
(returned_string, client_name_private) = ("","")
private_bool = False
end_private_message = "end"



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
            msg = b"Bienvenue, appuyez sur 1 pour vous connecter ou 2 pour creer un compte"
            connexion_avec_client.send(msg)
            msg = connexion_avec_client.recv(1024)
            response = msg.decode()
        

        if(response == "1"):
            unconnected = True
            client_already_connected = False
            while(unconnected):
                msg = b"Username :"
                connexion_avec_client.send(msg)
                username = connexion_avec_client.recv(1024)
                username = username.decode()
                for client in clients_connectes:
                    if (client.username == username):
                        client_already_connected = True
                        msg = b"User already connected, try another account if you have one or create a new one if you really want to be connected. You will now be redirected to the welcome message\n\n"
                        connexion_avec_client.send(msg)
                        break
                if (client_already_connected):
                    response = "" #on reinitialise la reponse sinon on ne re-rentrera pas dans le premier while verifiant la reponse du user
                    break
                msg = b"Password :"
                connexion_avec_client.send(msg)
                password = connexion_avec_client.recv(1024)
                password = password.decode()
                cursor = conn.execute("SELECT * FROM user WHERE USERNAME = '{}' AND PASSWORD = '{}'".format(username,password))
                conn.commit()
                if(cursor.fetchone() != None):
                    msg = b"Connexion reussie, bienvenue dans le chat public"
                    connexion_avec_client.send(msg)
                    unconnected = False
                else:
                    msg = b"Wrong credentials "
                    connexion_avec_client.send(msg)
                
                    
        if(response == "2"):
            unconnected = True
            while(unconnected):
                try:
                    username = " "
                    while(' ' in username):
                        msg = b"Username :"
                        connexion_avec_client.send(msg)
                        username = connexion_avec_client.recv(1024)
                        username = username.decode()
                        if (' ' in username):
                            connexion_avec_client.send(b"Username must not contain spaces\n")
                    msg = b"Password :"
                    connexion_avec_client.send(msg)
                    password = connexion_avec_client.recv(1024)
                    password = password.decode()
                    conn.execute("INSERT INTO user (USERNAME,PASSWORD) VALUES ('{}','{}')".format(username,password))
                    conn.commit()
                    unconnected = False
                    msg = b"Creation de compte reussie, bienvenue dans le chat public"
                    connexion_avec_client.send(msg)
                except sqlite3.IntegrityError:
                    msg = b"Username already existing"
                    connexion_avec_client.send(msg)
                
        
        
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
                client.socket.send(msg.encode())
                    

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
                        print("You are now speaking to '{}' ".format(client_name_private))
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
                msg_recu = client.socket.recv(1024)
                # Peut planter si le message contient des caractères spéciaux
                msg_recu = msg_recu.decode()
                
                #! Check client functions
                if(msg_recu[0] == "#"):
                    client_functions.Check_client_functions(msg_recu, client, clients_connectes)
                else:                                               
                    for receveur_client in clients_connectes:
                        if(client != receveur_client):
                            msg_a_envoyer = "{} > {}".format(client.username,msg_recu)
                            receveur_client.socket.send(msg_a_envoyer.encode()) #Envoi du msg reçu sur le channel public
                        else:
                            print("{} @{}:{} | {} > {} \n".format(datetime.now(), client.IP, client.port, client.username, msg_recu)) #Affichage côté serveur
                   
        # Sleep for a short time to prevent this thread from sucking up all of your CPU resources on your PC.
        time.sleep(0.01)

# If you run this Python file directly (ex: via `python3 this_filename.py`), do the following:
if (__name__ == '__main__'): 
    main()
