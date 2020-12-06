'''
• Client function (command line):
#! 1) #Help (list command)
#! 2) #Exit (client exit)
#! 3) #ListU (list of users in a server)
#! Rémi 4) #ListF (list of files in a server)
#! Rémi 5) #TrfU (Upload file transfer to a server)
#TODO Rémi 6) #TrfD (transfer Download file to a server)
#TODO VALOT • # Private <user> (private chat with another user)
#TODO VALOT • #Public (back to the public)
#TODO MUTEZ 1) #Ring <user> (notification if the user is logged in)
#TODO MUTEZ Limit size of messages (280 characters)
2) Your original orders

'''

# Import sockets libraries
import socket
import select

# Import display library
from datetime import datetime

from cyphering import *
key = "salut"
#Import files libraries
import os
import random
import string
import time

# Import threading libraries
import threading

#! Commandes clients
EXIT_CLIENT = "#Exit" #Command used by clients to leave
HELP_CLIENT = "#Help" #Command used by clients to get help
LISTU_CLIENT = "#ListU" #Command used by clients to get the list of other connected users
PRIVATE_CLIENT = "#Private" #Command used by clients to chat privately with one another
PUBLIC_CLIENT = "#Public" #Command used by clients to get back to public chat after using private chat
CREATE_CHATROOM_CLIENT= "#CreateRoom" #Command used by clients to create group chats with multiple users
JOIN_CHATROOM_CLIENT="#JoinRoom"
LIST_CHATROOM_CLIENT="#ListRoom"
UPLOAD_CLIENT = "#TrfU" #Command used by clients to upload files
RING_USER = "#Ring" #Command used by clients to ring a user if he's logged in
LISTF_CLIENT = "#ListF" #Command used by clients to see all files
#TODO TOUJOURS mettre les 3 mêmes paramètres dans chaque fonction même si on ne se sert pas des 3
#TODO En effet les appels de fonctions sont définis par défaut avec ces paramètres dans la fonction Check_client_functions

def Client_Exit (msg_recu,client, clients_connectes,client_en_envoi_fichier, Rooms):
    if(msg_recu == EXIT_CLIENT):
        msg_client="'{}' left the chat".format(client.username)
        print("{} @{}:{} | '{}' has left the chat \n".format(datetime.now(), client.IP, client.port, client.username)) 

        for element in clients_connectes:
            if (client != element):
                Send_Message(msg_client.encode(), key, element.socket)
                #element.socket.send(msg_client.encode())
        clients_connectes.remove(client)
        client.socket.close()
    
    else :
        raise Exception
        
def Client_Help (msg_recu,client, clients_connectes,client_en_envoi_fichier, Rooms):
    if(msg_recu == HELP_CLIENT):
        msg = "You can find a list of available commands below : \n \n \
        #Help (list command) \n \
        #Exit (exit chat) \n \
        #ListF (list of files in a server) \n \
        #ListU (list of users in a server) \n \
        #TrfU <filename if in current directory / absolute path> \n \
        #TrfD (transfer Download file to a server) \n \
        #Private <user> (private chat with another user) \n \
        #Public (back to the public chat) \n \
        #Ring <user> (notification if the user is logged in)\n \
        #CreateRoom <room name> (create private chat room with multiple clients) \n \
        #JoinRoom <room name> (Join a room the client was added to)\n \
        #ListRoom (List all rooms the client was added to)\n"

        Send_Message(msg.encode(), key, client.socket, force=True)
        #client.socket.send(msg.encode())
    else:
        raise Exception

def Client_ListU (msg_recu,client, clients_connectes,client_en_envoi_fichier, Rooms):
    if(msg_recu == LISTU_CLIENT):
        msg=("\nList of users (except you of course): \n") 
        count_user=1

        for element in clients_connectes:
            if (client != element):
                msg+=("User {}: {} @{}:{}\n".format(count_user, element.username, element.IP, element.port))
                count_user+=1
        msg+="\n"
        Send_Message(msg.encode(), key, client.socket)
        #client.socket.send(msg.encode())
    else :
        raise Exception

def Client_Private(msg_recu,client, clients_connectes,client_en_envoi_fichier, Rooms):
    client_connected_existed = False
    if(len(msg_recu.split(' ')) == 2): #on peut se permettre de verifier s'il n'y a que deux termes car le username ne peut pas contenir d'espace (regle qu'on a fixée)
        for other_client in clients_connectes:
            if (other_client.username == msg_recu.split(' ')[1]):
                client_connected_existed = True
                other_client.room=client.username
                client.room=other_client.username
                msg = "\nYou entered a private chat with '{}'.\n".format(client.username) 
                msg+="If you want to get back in the public chat, type '#Public'."
                Send_Message(msg.encode(), key, other_client.socket)
                msg = "You entered a private chat with {}.\n".format(other_client.username) 
                msg+="If you want to get back in the public chat, type '#Public'."
                Send_Message(msg.encode(), key, client.socket)
    
    if (len(msg_recu.split(' ')) == 1):
        Send_Message(b"Please write a user's name after the command", key, client.socket)
        #client.socket.send(b"Please write a user's name after the command")

    if (client_connected_existed == False and len(msg_recu.split(' ')) != 1):
        Send_Message(b"User not connected or not existing", key, client.socket)
        #client.socket.send(b"User not connected or not existing")


def Client_Public(msg_recu,client, clients_connectes,client_en_envoi_fichier, Rooms):
    if(msg_recu==PUBLIC_CLIENT):
        if(client.room != "public"):
            for other_client in clients_connectes:
                if(other_client.username==client.room):
                    msg="'{}' left the private chat.".format(client.username)
                    Send_Message(msg.encode(), key, other_client.socket)
                    #other_client.socket.send(msg.encode())
            client.room="public"
    else:
        raise Exception

def List_Room(client,msg_recu, clients_connectes, client_en_envoi_fichier, Rooms):
    
    no_client=[]
    client_room=msg_recu.split(' ')[1:len(msg_recu.split(' '))]
    if(len(client_room) > 1): #on peut se permettre de verifier s'il n'y a que deux termes car le username ne peut pas contenir d'espace (regle qu'on a fixée)
        for i in range (len(client_room))
            client_connected_existed = False
            for other_client in clients_connectes:
                
                if (other_client.username == client_room[i]):
                    client_connected_existed = True
                    

            if(client_connected_existed==False):
                no_client.append(client_room[i])

    
    elif (len(client_room) == 0):
        Send_Message(b"Please write a user's name after the command",key,client.socket)
        
    
    elif (len(msg_recu.split(' ')) == 1):
        Send_Message(b"Please write more than one user's name after the command, or use command #Private",key,client.socket)
                       
def Create_Room(client,msg_recu, clients_connectes, client_en_envoi_fichier, Rooms):
    exist=False
    if(len(msg_recu.split(' '))>1):
        room_name = msg_recu.lstrip(msg_recu.split(' ')[0])
        room_name = room_name[1:len(room_name)]
        if(len(Rooms)!=0):
            for room in Rooms:
                if(room_name==room.name):
                    exist=True
                    break
        if(not exist):
            return client, room_name
    elif(len(msg_recu.split(' '))==1):
        Send_Message(b"Please precise a room name after the #CreateRoom command.",key,client.socket)                   
    


                            
def Client_Upload(msg_recu,client, clients_connectes,client_en_envoi_fichier, Rooms):
    filename, filesize = msg_recu.split("<>")
    filename = filename.split(" ",1)[1]
    filename = os.path.basename(filename)
    filesize = int(filesize)
    #Start File-receiver Thread 
    client_en_envoi_fichier.append(client)
    Send_Message(b"OK", key, client.socket)
    #client.socket.send(b"OK")
  

    filename_sans_extension, extension = filename.split(".")
    filename_for_save = "Files/{}_{}.{}".format(filename_sans_extension,''.join(random.choices(string.ascii_letters + string.digits, k=10)), extension)
    #Ajouter un code à la fin du nom de base du fichier afin d'éviter des remplacements de fichier si plusieurs ont le même nom
    #threading.Thread(target=Thread_File_Receiver, args=(filename,filesize,client,client_en_envoi_fichier,)).start()
    sum_bytes=0
    percent=0
    with open(filename_for_save, "wb") as f:
        while(True):
            # read 1024 bytes from the socket (receive)
            try:
                percent = (int) (sum_bytes/filesize)*100
                print("", end=f"\r {filename} envoyé par {client.username} reçu: {percent} %")
                client.socket.settimeout(0.5)
                bytes_read = client.socket.recv(1024)
                sum_bytes+= len(bytes_read)
                client.socket.settimeout(None) # On retire le timeout, il ne sert que pour le transfert de fichiers
            except :
                client.socket.settimeout(None)
                break  
            # write to the file the bytes we just received
            
            
            f.write(bytes_read)
        print()
    client_en_envoi_fichier.remove(client)

''' #! Inutilisé
def Thread_File_Receiver(filename,filesize,client,client_en_envoi_fichier):
    # start receiving the file from the socket
    # and writing to the file stream
    progress = tqdm.tqdm(range(filesize), f"Receiving {filename}", unit="B", unit_scale=True, unit_divisor=1024)
    with open(filename, "wb") as f:
        for _ in progress:
            # read 1024 bytes from the socket (receive)
            bytes_read = client.socket.recv(1024)
            if not bytes_read:    
                # nothing is received
                # file transmitting is done
                break
            # write to the file the bytes we just received
            f.write(bytes_read)
            # update the progress bar
            progress.update(len(bytes_read))
    client_en_envoi_fichier.remove(client)
'''
def Client_Ring(msg_recu,client, clients_connectes,client_en_envoi_fichier, Rooms):
    client_target_existed = False
    if(len(msg_recu.split(' ')) == 2): #on peut se permettre de verifier s'il n'y a que deux termes car le username ne peut pas contenir d'espace (regle qu'on a fixée)
        for other_client in clients_connectes:
            if (other_client.username == msg_recu.split(' ')[1]):
                client_target_existed = True
                msg = "\nThe user : '{}' try to reach you.\n".format(client.username) 
                Send_Message(msg.encode(), key, other_client.socket)
                #other_client.socket.send(msg.encode())
    
    if (len(msg_recu.split(' ')) == 1):
        Send_Message(b"Please write a user's name after the command", key, client.socket)
        #client.socket.send(b"Please write a user's name after the command")

    if (client_target_existed == False and len(msg_recu.split(' ')) != 1):
        Send_Message(b"User you tried to ring is not connected or not existing", key, client.socket)
        #client.socket.send(b"User you tried to ring is not connected or not existing")

def Client_ListF(msg_recu,client, clients_connectes,client_en_envoi_fichier, Rooms):
    list_files = os.listdir("Files")
    msg_a_envoyer = "Liste des fichier : \n"
    for fichier in list_files:
        msg_a_envoyer+= "{} \n".format(fichier)
    msg_a_envoyer = msg_a_envoyer.encode()
    Send_Message(msg_a_envoyer,key,client.socket)

options = {
        EXIT_CLIENT : Client_Exit,
        HELP_CLIENT : Client_Help,
        LISTU_CLIENT : Client_ListU,
        PRIVATE_CLIENT : Client_Private,
        PUBLIC_CLIENT : Client_Public,
        CREATE_CHATROOM_CLIENT : Create_Room,
        LIST_CHATROOM_CLIENT : List_Room,
        UPLOAD_CLIENT : Client_Upload,
        RING_USER : Client_Ring,
        LISTF_CLIENT : Client_ListF
    }

def Check_client_functions(msg_recu, client, clients_connectes, client_en_envoi_fichier, Rooms):
    commande = msg_recu.split(' ')[0]

    try:
        return options[commande](client,msg_recu, clients_connectes, client_en_envoi_fichier, Rooms)
    except :
        Send_Message(b"Command not found, try using #Help",key,client.socket)
    

