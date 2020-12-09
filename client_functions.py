# Import sockets libraries
import socket
import select

# Import display library
from datetime import datetime

from cyphering import *
from room_functions import *
key = "salut"

#Import files libraries
import os
import random
import string
import time

# Import threading libraries
import threading

# Import needed files
from RoomClass import *

#! Commandes clients
EXIT_CLIENT = "#Exit" #Commande utilisée par les clients pour quitter son terminal
HELP_CLIENT = "#Help" #Commande utilisée par les clients pour obtenir de l'aide
LISTU_CLIENT = "#ListU" #Commande utilisée par les clients pour obtenir la liste des autres utilisateurs connectés
PRIVATE_CLIENT = "#Private" #Commande utilisée par les clients pour discuter en privé les uns avec les autres
PUBLIC_CLIENT = "#Public" #Commande utilisée par les clients pour revenir au chat public après avoir utilisé le chat privé ou être entré dans une room
UPLOAD_CLIENT = "#TrfU" #Commande utilisée par les clients pour télécharger des fichiers
RING_USER = "#Ring" #Commande utilisée par les clients pour ring un utilisateur s'il est connecté
LISTF_CLIENT = "#ListF" #Commande utilisée par les clients pour voir tous les fichiers
DOWNLOAD_CLIENT = "#TrfD" #Commande utilisée par les clients pour télécharger des fichiers

CREATE_CHATROOM_CLIENT= "#CreateRoom" #Commande utilisée par les clients pour créer des discussions de groupe avec plusieurs utilisateurs
JOIN_CHATROOM_CLIENT="#JoinRoom" #Commande utilisée par les clients pour rejoindre une room à laquelle ils appartiennent
LIST_CHATROOM_CLIENT="#ListRoom" #Commande utilisée par les clients pour lister toutes les pièces auxquelles ils appartiennent
ADD_CLIENT_CHATROOM_CLIENT="#AddRoom" #Commande utilisée par les clients pour ajouter un utilisateur à une room
KICK_CLIENT_CHATROOM_CLIENT="#KickRoom" #Commande utilisée par les clients pour kick un utilisateur d'une room
LEAVE_CLIENT_CHATROOM_CLIENT="#LeaveRoom" #Commande utilisée par les clients pour quitter une room
LIST_CLIENT_CHATROOM_CLIENT="#ListClientRoom" #Commande utilisée par les clients pour lister les clients d'une room

#! Hints :
#TODO TOUJOURS mettre les 4 mêmes paramètres dans chaque fonction même si on ne se sert pas des 4
#TODO En effet les appels de fonctions sont définis par défaut avec ces paramètres dans la fonction Check_client_functions


'''
#* Fonction qui permet a un client de shutdown son terminal (de quitter l'application)

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Client_Exit (msg_recu,client, clients_connectes, Rooms):
    if(msg_recu == EXIT_CLIENT):
        # On notifie sur le serveur et tous les clients que le client a quitter le chat
        msg_client="'{}' left the chat".format(client.username)
        # Pour le serveur
        print("{} @{}:{} | '{}' has left the chat \n".format(datetime.now(), client.IP, client.port, client.username)) 
        # Pour les clients
        for element in clients_connectes:
            if (client != element):
                Send_Message(msg_client, key, element.socket)
        # On retire les clients de la liste des clients connectés et on ferme sa session
        clients_connectes.remove(client)
        client.socket.close()
    
    else :
        raise Exception


'''
#* Fonction qui permet a un client d'avoir accès a la liste des commandes qu'il peut effectuer

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Client_Help (msg_recu,client, clients_connectes, Rooms):
    # Message qui affiche la liste des commandes
    if(msg_recu == HELP_CLIENT):
        msg = "You can find a list of available commands below : \n \
        #Help (list command) \n \
        #Exit (exit chat) \n \
        #ListF (list of files in a server) \n \
        #ListU (list of users in a server) \n \
        #TrfU <filename if in current directory / absolute path> \n \
        #TrfD (transfer Download file to a server) \n \
        #Private <user> (private chat with another user) \n \
        #Public (back to the public chat) \n \
        #Ring <user> (notification if the user is logged in)\n \
        #CreateRoom <room_name> <user1> <user2> ... (create private chat room with multiple clients. Please note that your 'room_name' must not contain spaces) \n \
        #JoinRoom <room_name> (Join a room the client was added to)\n \
        #ListRoom (List all rooms the client was added to)\n \
        #AddRoom <room_name> <username>  (Add a client to room)\n \
        #KickRoom <room_name> <username>  (Kick a client from room)\n \
        #LeaveRoom <room_name> (Allow a client to leave a room)\n \
        #ListClientRoom <room_name> (Allow a client to see the members of the room)\n"

        # On envoie le message au client
        Send_Message(msg, key, client.socket, force=True)
    else:
        raise Exception


'''
#* Fonction qui permet a un client d'avoir accès a la liste des clients connectés

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Client_ListU (msg_recu,client, clients_connectes, Rooms):
    if(msg_recu == LISTU_CLIENT):
        msg=("\nList of users (except you of course): \n") 
        count_user=1

        # On parcourt la liste des clients (excepté le client qui execute la commande) pour les stocker dans un string
        for element in clients_connectes:
            if (client != element):
                msg+=("User {}: '{}' @{}:{}\n".format(count_user, element.username, element.IP, element.port))
                count_user+=1
        msg+="\n"
        # On envoie le message au client
        Send_Message(msg, key, client.socket, force=True)
    else :
        raise Exception


'''
#* Fonction qui permet a un client d'envoyer un message privé à un autre client

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Client_Private(msg_recu,client, clients_connectes, Rooms):
    client_connected_existed = False
    #on peut se permettre de verifier s'il n'y a que deux termes car le username ne peut pas contenir d'espace (regle qu'on a fixée)
    if(len(msg_recu.split(' ')) == 2):
        # On parcourt la liste des clients connectés pour trouver le client à joindre en privé
        for other_client in clients_connectes:
            if (other_client.username == msg_recu.split(' ')[1]):
                # Si le client existe, indicateur passe a True
                client_connected_existed = True
                # L'attribut room de chacun des clients deviennent les usernames de l'autre
                other_client.room=client.username
                client.room=other_client.username
                msg = "\nYou entered a private chat with '{}'.\n".format(client.username) 
                msg+="If you want to get back in the public chat, type '#Public'."
                Send_Message(msg, key, other_client.socket)
                msg = "You entered a private chat with {}.\n".format(other_client.username) 
                msg+="If you want to get back in the public chat, type '#Public'."
                Send_Message(msg, key, client.socket)
    # Si la commande n'est pas correct
    if (len(msg_recu.split(' ')) == 1):
        Send_Message("Please write a user's name after the command", key, client.socket)
    # Si le client n'existe pas ou n'est pas connecté
    if (client_connected_existed == False and len(msg_recu.split(' ')) != 1):
        Send_Message("User not connected or not existing", key, client.socket)


'''
#* Fonction qui permet a un client qui était dans une room ou en chat privé de revenir dans le chat public

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Client_Public(msg_recu,client, clients_connectes, Rooms):
    if(msg_recu==PUBLIC_CLIENT):
        # On vérifie qu'il n'est pas déjà en public
        if(client.room != "public"):
            for other_client in clients_connectes:
                # Si dans la liste des clients connectés, le client à comme attribut room le username du client qui veut quitter 
                # la conversatino privé, on le previent du départ de celui-ci
                if(other_client.username==client.room):
                    msg="'{}' left the private chat.".format(client.username)
                    Send_Message(msg, key, other_client.socket)
            # On replace le client dans le chat public
            client.room="public"
    else:
        raise Exception


'''
#* Fonction qui fait appel a la fonction List_Room_RF
#* Permet a un client de voir la liste des rooms dont il fait parti

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def List_Room(msg_recu, client, clients_connectes, Rooms):
    List_Room_RF(msg_recu, client, clients_connectes, Rooms)


'''
#* Fonction qui fait appel a la fonction Create_Room_RF
#* Permet a un client de créer une room

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Create_Room(msg_recu, client, clients_connectes, Rooms):
    Create_Room_RF(msg_recu, client, clients_connectes, Rooms)



''' fonction non utilisé à ce jour mais aurait pu l'être avec Create_Room2_RF dans romm_functions.py si le tout avait été plus fonctionnel
def Create_Room2(msg_recu, client, clients_connectes, Rooms):
    Create_Room2_RF(msg_recu, client, clients_connectes, Rooms)                
'''


'''
#* Fonction qui fait appel a la fonction Join_Room_RF
#* Permet a un client de rejoindre une room

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Join_Room(msg_recu, client, clients_connectes, Rooms):
    Join_Room_RF(msg_recu, client, clients_connectes, Rooms)


'''
#* Fonction qui fait appel a la fonction Add_Room_RF
#* Permet a un client admin d'ajouter un autre client à sa room

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Add_Room(msg_recu, client, clients_connectes, Rooms):
    Add_Room_RF(msg_recu, client, clients_connectes, Rooms)


'''
#* Fonction qui fait appel a la fonction Kick_Room_RF
#* Permet a un client admin de retirer un autre client de sa room

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Kick_Room(msg_recu, client, clients_connectes, Rooms):
    Kick_Room_RF(msg_recu, client, clients_connectes, Rooms)


'''
#* Fonction qui fait appel a la fonction Leave_Room_RF
#* Permet a un client de se retirer de sa room

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Leave_Room(msg_recu, client, clients_connectes, Rooms):
    Leave_Room_RF(msg_recu, client, clients_connectes, Rooms)


'''
#* Fonction qui fait appel a la fonction List_Client_Room_RF
#* Permet a un client de voir la liste des clients present dans une room

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def List_Client_Room(msg_recu, client, clients_connectes, Rooms):
    List_Client_Room_RF(msg_recu, client, clients_connectes, Rooms)


'''
#* Fonction qui permet à un client d'upload un fichier

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Client_Upload(msg_recu,client, clients_connectes, Rooms):
    filename, filesize = msg_recu.split("<>")
    filename = filename.split(" ",1)[1]
    filename = os.path.basename(filename)
    filesize = int(filesize)
    # On retire le client de la liste des clients connectés pour éviter qu'on ne lise ses messages comme du texte standard
    clients_connectes.remove(client)
    # On prévient le client que le serveur est prêt à recevoir la data du fichier
    Send_Message("OK UPLOAD", key, client.socket)
    
    filename_sans_extension, extension = filename.split(".")

    try: # On crée un dossier pour sauvegarder les fichiers uploadés
        os.makedirs("Files_Uploaded")
    except:
        pass

    filename_for_save = "Files_Uploaded/{}_{}.{}".format(filename_sans_extension,''.join(random.choices(string.ascii_letters + string.digits, k=10)), extension)
    #Ajouter un code à la fin du nom de base du fichier afin d'éviter des remplacements de fichier si plusieurs ont le même nom
    sum_bytes=0
    percent=0
    with open(filename_for_save, "wb") as f:
        while(True):
            
            try:
                percent = (int) (sum_bytes/filesize)*100
                print("", end=f"\r {filename} envoyé par {client.username} reçu: {percent} %")
                client.socket.settimeout(0.5)
                bytes_read = client.socket.recv(1024)
                sum_bytes+= len(bytes_read)
                client.socket.settimeout(None) 
                # On retire le timeout, il ne sert que pour le transfert de fichiers
            except :
                client.socket.settimeout(None)
                break  
            # On sauvegarde le fichier
            
            
            f.write(bytes_read)
        print()
    clients_connectes.append(client)


'''
#* Fonction qui permet à un client de notifier un autre client

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Client_Ring(msg_recu,client, clients_connectes, Rooms):
    client_target_existed = False
    #on peut se permettre de verifier s'il n'y a que deux termes car le username ne peut pas contenir d'espace (regle qu'on a fixée)
    if(len(msg_recu.split(' ')) == 2):
        # On verifie que le client est dans la liste des clients connectés
        for other_client in clients_connectes:
            # Si le client exite et est connecté on lui envoie le ping
            if (other_client.username == msg_recu.split(' ')[1]):
                client_target_existed = True
                msg = "\nThe user : '{}' try to reach you.\n".format(client.username) 
                Send_Message(msg, key, other_client.socket)
    # Si la commande est mal rentrée
    if (len(msg_recu.split(' ')) == 1):
        Send_Message("Please write a user's name after the command", key, client.socket)
    
    # Si le client n'est pas connecté ou n'existe pas
    if (client_target_existed == False and len(msg_recu.split(' ')) != 1):
        Send_Message("User you tried to ring is not connected or not existing", key, client.socket)


'''
#* Fonction qui permet à un client de voir tous les fichiers

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Client_ListF(msg_recu,client, clients_connectes, Rooms):
    list_files = os.listdir("Files")
    msg_a_envoyer = "Liste des fichier : \n"
    for fichier in list_files:
        msg_a_envoyer+= "{} \n".format(fichier)
    msg_a_envoyer = msg_a_envoyer
    Send_Message(msg_a_envoyer,key,client.socket, force=True)


'''
#* Fonction qui permet à un client de download un fichier

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Client_Download(msg_recu,client, clients_connectes, Rooms):
    filename=""
    filesize = ""
    try:
        # On cherche si le fichier que veut DL le client existe bien, et si oui on lui renvoie les informations sur ce fichier
        filename = msg_recu.split(' ',1)[1]
        filesize = os.path.getsize("Files/"+filename)
        msg_a_envoyer = "#TrfD {}<>{}".format(filename,filesize)
        msg_a_envoyer = msg_a_envoyer
    except:
        # Sinon on lui dit qu'il a choisi un mauvais fichier
        msg_a_envoyer = "#TrfD Error with file"
    Send_Message(msg_a_envoyer,key,client.socket)


    if(filesize != ""): #Si le file a bien été trouvé
        
        clients_connectes.remove(client) 
        # On ne veut rien lui envoyer d'autre que le fichier
        client_ready = False
        recu = ""
        while(not client_ready):
            # On attend que le client soit prêt à recevoir le fichier
            try:
                recu = Receive_Message(key, client.socket).decode()
            except:
                pass
            if(recu == "OK DOWNLOAD"): client_ready=True
        # On lance le thread d'émission de fichier
        threading.Thread(target=Thread_File_Sender, args=(filename,filesize,client,clients_connectes,)).start()


'''
#* Fonction permettant 

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Thread_File_Sender (filename,filesize,client, client_connectes):
    
    #start sending file
    sum_bytes=0
    percent=0
    with open("Files/"+filename, "rb") as f:
        while(True):
			# On lit le fichier
            bytes_read = f.read(1024)
            if not bytes_read:
				# Transmission finie
                break
			
            sum_bytes+= len(bytes_read)
            percent = (int) (sum_bytes/filesize)*100
            print("", end=f"\r {filename} envoyé à '{client.username}' : {percent} %")
            client.socket.sendall(bytes_read)
            
			
    print()
    client_connectes.append(client)


#! Dictionnaire utilisé dans la fonction principale de ce fichier à savoir Check_client_functions (ci-dessous)
#! Il est utilisé comme un switch case
#! A gauche des ":" c'est la key (que l'on a défini tout en haut du fichier)
#! A droite des ":" c'est la value qui est ici la fonction qui sera executé en fonction de la key que l'on saisi
options = {
        EXIT_CLIENT : Client_Exit,
        HELP_CLIENT : Client_Help,
        LISTU_CLIENT : Client_ListU,
        PRIVATE_CLIENT : Client_Private,
        PUBLIC_CLIENT : Client_Public,
        CREATE_CHATROOM_CLIENT : Create_Room,
        JOIN_CHATROOM_CLIENT: Join_Room,
        LIST_CHATROOM_CLIENT: List_Room,
        ADD_CLIENT_CHATROOM_CLIENT: Add_Room,
        KICK_CLIENT_CHATROOM_CLIENT: Kick_Room,
        LEAVE_CLIENT_CHATROOM_CLIENT: Leave_Room,
        LIST_CLIENT_CHATROOM_CLIENT: List_Client_Room,
        UPLOAD_CLIENT : Client_Upload,
        RING_USER : Client_Ring,
        LISTF_CLIENT : Client_ListF,
        DOWNLOAD_CLIENT : Client_Download
    }


'''
#* Fonction principale redirigeant vers la fonction adéquat de ce fichier par rapport à l'input client

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Check_client_functions(msg_recu, client, clients_connectes,  Rooms):
    commande = msg_recu.split(' ')[0]

    try:
        return options[commande](msg_recu,client, clients_connectes,  Rooms)
    except :
        Send_Message("Command not found, try using #Help",key,client.socket)
    

