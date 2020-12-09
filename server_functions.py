# Import sockets libraries
import socket

#Import display libraries
from datetime import datetime
import time

#Import cyphering key
from cyphering import *
key = "salut"

#Import files checking
import os

#! Commandes serveur
EXIT_SERVER = "#Exit" #Commande utilisée par le serveur pour shutdown
HELP_SERVER = "#Help" #Commande utilisée par le serveur pour obtenir de l'aide
KILL_SERVER = "#Kill" #Commande utilisée par le serveur pour kill le terminal d'un user
LISTU_SERVER = "#ListU" #Commande utilisée par le serveur pour afficher tous les utilisateurs connectés
ALERT_SERVER = "#Alert" #Commande utilisée par le serveur pour envoyer un message à tous les utilisateurs
PRIVATE_SERVER = "#Private" #Commande utilisée par le serveur pour envoyer un message à un utilisateur en particulier
LISTF_SERVER = "#ListF" #Commande utilisée par le serveur pour vérifier tous les fichiers existants dans le répertoire Files

#! Hints :
#? TOUJOURS mettre les 3 mêmes paramètres dans chaque fonction même si on ne se sert pas des 3
#? En effet les appels de fonctions sont définis par défaut avec ces paramètres dans la fonction Check_client_functions

'''
#* Fonction permettant de shutdown le server ce qui aura pour impact de shutdown tous les users connectés également

#? param input du server
#? la liste de tous les clients connectés
#? la connexion principale (la socket du server)
'''
def Server_Exit(input_server, clients_connectes,connexion_principale,clients_awaiting_connection):
        print("Server closing...")
        #On va fermer toutes les sockets des clients connectés et leur envoyer un message pour pouvoir sortir de la boucle while(true) dans client.py
        for client in clients_connectes:
            Send_Message("Server shutdown", key, client.socket)
            time.sleep(0.01)
            client.socket.close()

        #On va fermer toutes les sockets des clients en attente de connexion et leur envoyer un message pour pouvoir sortir de la boucle while(true) dans client.py
        for socket in clients_awaiting_connection:
            Send_Message("Server shutdown", key, socket)
            time.sleep(0.01)
            socket.close()

        #On ferme aussi la socket du server
        connexion_principale.close()
        return "exit"


'''
#* Fonction permettant de shutdown un terminal d'un user connecté 

#? param input du server
#? la liste de tous les clients connectés
#? la connexion principale (la socket du server)
'''
def Server_Kill(input_server, clients_connectes,connexion_principale,clients_awaiting_connection):
    client_connected_existed = False
    if(len(input_server.split(' ')) == 2): #on peut se permettre de verifier s'il n'y a que deux termes car le username ne peut pas contenir d'espace (regle qu'on a fixée)
        for client in clients_connectes: #on parcourt les clients connecté jusqu'à trouvé le client à kick
            if (client.username == input_server.split(' ')[1]):
                client_connected_existed = True
                Send_Message("You were kicked by server", key, client.socket) #Message pour pouvoir sortir de la boucle while(true) dans client.py
                client.socket.close() #on ferme la socket du client à kick
                clients_connectes.remove(client) #on le retir des clients connectés
                print("User '{}' was kicked by server at {} from @{}:{}".format(client.username, datetime.now(), client.IP, client.port))

                #on prévient tous les autres users connectés qu'un user a été kick
                for client_not_kicked in clients_connectes:
                    if (client_not_kicked != client):
                        msg = "User '{}' was kicked by server".format(input_server.split(' ')[1])
                        Send_Message(msg, key, client_not_kicked.socket)
    
    if (len(input_server.split(' ')) == 1):
        print("Please write a client name after the command")

    if (not client_connected_existed and len(input_server.split(' ')) != 1):
        print("Client not connected or not existing")


'''
#* Fonction affichant toutes les commandes possibles pour le server

#? param input du server
#? la liste de tous les clients connectés
#? la connexion principale (la socket du server)
'''
def Server_Help(input_server, clients_connectes,connexion_principale,clients_awaiting_connection):
    msg = "You can find a list of available commands below : \n \n \
    #Help (list command) \n \
    #Exit (server shutdown) \n \
    #Kill <user> (kick <user> from server) \n \
    #ListU (list of users in a server) \n \
    #ListF (list of files in a server) \n \
    #Private <user> <message> (private chat with another user) \n \
    #Alert <msg> (send msg to all users)"

    print(msg)


'''
#* Fonction affichant tous les users connectés

#? input du server
#? la liste de tous les clients connectés
#? la connexion principale (la socket du server)
'''
def Server_ListU(input_server, clients_connectes,connexion_principale,clients_awaiting_connection):
    print("The following users are connected to the server :")
    for client in clients_connectes:
        print("   - User '{}' from @{}:{}".format(client.username, client.IP, client.port))


'''
#* Fonction permettant d'envoyer un message à tous les users

#? input du server
#? la liste de tous les clients connectés
#? la connexion principale (la socket du server)
'''
def Server_Alert(input_server, clients_connectes,connexion_principale,clients_awaiting_connection):
    if(len(input_server.split(' ')) != 1): #si l'input c'est pas seulement #Alert car dans ce cas il n'y a pas de message
        #On récupère l'input sous la forme d'un long string
        msg =""
        for word in input_server.split(' '):
            msg+= word + " "
        msg = msg.lstrip(input_server.split(' ')[0]) #On retire la #command
        msg = "MESSAGE FROM SERVER :" +msg

        for client in clients_connectes:
            Send_Message(msg, key, client.socket)

    else:
        print("There is nothing to send. If you want to send something, write a message after the command")


'''
#* Fonction permettant d'envoyer un message privé à un user 

#? input du server
#? la liste de tous les clients connectés
#? la connexion principale (la socket du server)
'''
def Server_Private(input_server, clients_connectes,connexion_principale,clients_awaiting_connection):
    client_connected_existed = False
    if(len(input_server.split(' ')) > 2): #on peut se permettre de verifier s'il n'y a que trois termes car le username ne peut pas contenir d'espace (regle qu'on a fixée)
        for client in clients_connectes: #On check si le client à qui veut s'adresser le serveur est bien connecté
            if (client.username == input_server.split(' ')[1]):
                client_connected_existed = True
                #On récupère le message que le server veut envoyer au client
                msg = input_server.split(' ')[2:len(input_server.split(' '))]
                msg = " ".join(msg)
                msg_a_envoyer = "PRIVATE MESSAGE FROM SERVER : " + msg
                Send_Message(msg_a_envoyer, key, client.socket)
    
    if (len(input_server.split(' ')) == 1):
        print("Please write a client name after the command")

    if (client_connected_existed == False and len(input_server.split(' ')) != 1):
        print("Client not connected or not existing")


'''
#* Fonction qui permet de lister tous les files présents sur le server

#? param input du server
#? la liste de tous les clients connectés
#? la connexion principale (la socket du server)
'''
def Server_ListF(input_server, clients_connectes,connexion_principale,clients_awaiting_connection):
    list_files = os.listdir("Files") # Folder où se trouve les files
    msg_a_print = "\n Liste des fichiers : \n "
    for fichier in list_files:
        msg_a_print+= "{} \n".format(fichier)
    print(msg_a_print)


#! Dictionnaire utilisé dans la fonction principale de ce fichier à savoir Check_server_functions (ci-dessous)
#! Il est utilisé comme un switch case
#! A gauche des ":" c'est la key (que l'on a défini tout en haut du fichier)
#! A droite des ":" c'est la value qui est ici la fonction qui sera executé en fonction de la key que l'on saisi
options = {
        EXIT_SERVER : Server_Exit,
        KILL_SERVER : Server_Kill,
        HELP_SERVER : Server_Help,
        LISTU_SERVER : Server_ListU,
        ALERT_SERVER : Server_Alert,
        PRIVATE_SERVER : Server_Private,
        LISTF_SERVER : Server_ListF
    }


'''
#* Fonction principale redirigeant vers la fonction adéquat de ce fichier par rapport à l'input server

#? param input du server
#? la liste de tous les clients connectés
#? la connexion principale (la socket du server)
'''
def Check_server_functions(input_server, clients_connectes,connexion_principale,clients_awaiting_connection):
    commande = input_server.split(' ')[0]

    try:
        return options[commande](input_server, clients_connectes,connexion_principale,clients_awaiting_connection)
    except :
        msg = "Command not found, try using #Help"
        print(msg)
