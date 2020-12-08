'''
• Client function (command line):
#! 1) #Help (list command)
#! 2) #Exit (client exit)
#! 3) #ListU (list of users in a server)
#! Rémi 4) #ListF (list of files in a server)
#! Rémi 5) #TrfU (Upload file transfer to a server)
#! Rémi 6) #TrfD (transfer Download file to a server)
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

from RoomClass import *

#! Commandes clients
EXIT_CLIENT = "#Exit" #Command used by clients to leave
HELP_CLIENT = "#Help" #Command used by clients to get help
LISTU_CLIENT = "#ListU" #Command used by clients to get the list of other connected users
PRIVATE_CLIENT = "#Private" #Command used by clients to chat privately with one another
PUBLIC_CLIENT = "#Public" #Command used by clients to get back to public chat after using private chat
CREATE_CHATROOM_CLIENT= "#CreateRoom" #Command used by clients to create group chats with multiple users
JOIN_CHATROOM_CLIENT="#JoinRoom" #Join one room which the client belongs to
LIST_CHATROOM_CLIENT="#ListRoom" #List all rooms the client belongs to
ADD_CLIENT_CHATROOM_CLIENT="#AddRoom" #Add a client to a room
KICK_CLIENT_CHATROOM_CLIENT="#KickRoom" #Kick a client to a room
LEAVE_CLIENT_CHATROOM_CLIENT="#LeaveRoom" #Client wants to leave the room
LIST_CLIENT_CHATROOM_CLIENT="#ListClientRoom" #List of client in a room
UPLOAD_CLIENT = "#TrfU" #Command used by clients to upload files
RING_USER = "#Ring" #Command used by clients to ring a user if he's logged in
LISTF_CLIENT = "#ListF" #Command used by clients to see all files
DOWNLOAD_CLIENT = "#TrfD" #Command used by clients to upload files
#TODO TOUJOURS mettre les 3 mêmes paramètres dans chaque fonction même si on ne se sert pas des 3
#TODO En effet les appels de fonctions sont définis par défaut avec ces paramètres dans la fonction Check_client_functions

def Client_Exit (msg_recu,client, clients_connectes, Rooms):
    if(msg_recu == EXIT_CLIENT):
        msg_client="'{}' left the chat".format(client.username)
        print("{} @{}:{} | '{}' has left the chat \n".format(datetime.now(), client.IP, client.port, client.username)) 

        for element in clients_connectes:
            if (client != element):
                Send_Message(msg_client, key, element.socket)
        clients_connectes.remove(client)
        client.socket.close()
    
    else :
        raise Exception
        
def Client_Help (msg_recu,client, clients_connectes, Rooms):
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
        #CreateRoom <room name> <user1> <user2> ... (create private chat room with multiple clients) \n \
        #JoinRoom <room name> (Join a room the client was added to)\n \
        #ListRoom (List all rooms the client was added to)\n \
        #AddRoom <username> <room name> (Add a client to room)\n \
        #KickRoom <username> <room name> (Kick a client from room)\n \
        #LeaveRoom <room name> (Allow a client to leave a room)\n \
        #ListClientRoom <room name> (Allow a client to see the members of the room)\n"

        Send_Message(msg, key, client.socket, force=True)
    else:
        raise Exception

def Client_ListU (msg_recu,client, clients_connectes, Rooms):
    if(msg_recu == LISTU_CLIENT):
        msg=("\nList of users (except you of course): \n") 
        count_user=1

        for element in clients_connectes:
            if (client != element):
                msg+=("User {}: '{}' @{}:{}\n".format(count_user, element.username, element.IP, element.port))
                count_user+=1
        msg+="\n"
        Send_Message(msg, key, client.socket, force=True)
    else :
        raise Exception

def Client_Private(msg_recu,client, clients_connectes, Rooms):
    client_connected_existed = False
    if(len(msg_recu.split(' ')) == 2): #on peut se permettre de verifier s'il n'y a que deux termes car le username ne peut pas contenir d'espace (regle qu'on a fixée)
        for other_client in clients_connectes:
            if (other_client.username == msg_recu.split(' ')[1]):
                client_connected_existed = True
                other_client.room=client.username
                client.room=other_client.username
                msg = "\nYou entered a private chat with '{}'.\n".format(client.username) 
                msg+="If you want to get back in the public chat, type '#Public'."
                Send_Message(msg, key, other_client.socket)
                msg = "You entered a private chat with {}.\n".format(other_client.username) 
                msg+="If you want to get back in the public chat, type '#Public'."
                Send_Message(msg, key, client.socket)
    
    if (len(msg_recu.split(' ')) == 1):
        Send_Message("Please write a user's name after the command", key, client.socket)

    if (client_connected_existed == False and len(msg_recu.split(' ')) != 1):
        Send_Message("User not connected or not existing", key, client.socket)


def Client_Public(msg_recu,client, clients_connectes, Rooms):
    if(msg_recu==PUBLIC_CLIENT):
        if(client.room != "public"):
            for other_client in clients_connectes:
                if(other_client.username==client.room):
                    msg="'{}' left the private chat.".format(client.username)
                    Send_Message(msg, key, other_client.socket)
            client.room="public"
    else:
        raise Exception

def List_Room(msg_recu, client, clients_connectes,  Rooms):
    list_rooms="Here is the list of private Chat room you belong to:\n   "
    for room in Rooms:
        for room_client in room.clients:
            if client.username==room_client.username:
                list_rooms+=room.name+"\n   "
                break
    Send_Message(list_rooms,key,client.socket, force=True)

def Create_Room(msg_recu, client, clients_connectes,  Rooms):
    if(len(msg_recu.split(' '))>3):
        exist=False
        creation_success = False
        clients_to_add_to_room = []
        error_msg=""

        msg_recu = msg_recu.split(' ')
        room_name = msg_recu[1]
        name_clients_typed = msg_recu[2:len(msg_recu)]

        name_clients_connected=[]
        for cli in clients_connectes:
            name_clients_connected.append(cli.username)

        if(room_name in name_clients_connected):
            error_msg="The name of the room is already taken by a user, please try again and change the name.\n"
            exist=True
        for room in Rooms:
            if(room_name==room.name):
                error_msg="The name of the room is already taken by another room, please try again and change the name.\n"
                exist=True
                break
        
        if (not exist):
            for name_cli_typed in name_clients_typed:
                if (name_cli_typed in name_clients_connected and (name_cli_typed not in clients_to_add_to_room)):
                    clients_to_add_to_room.append(name_cli_typed)
                else:
                    msg = "User '{}' is not connected or does not exist. In both case, he can't be added to the room. It's also possible that you already added him to the room (you might have written his name twice or more).".format(name_cli_typed)
                    Send_Message(msg, key, client.socket)
            
            if (len(clients_to_add_to_room) > 1):
                new_room=Room(room_name,client)
                for cli in clients_connectes: #on refait cette boucle pour prendre toutes les infos concernant le client et pas que son nom
                    if (cli.username in clients_to_add_to_room and cli.username != client.username):
                        new_room.clients.append(cli)
                Rooms.append(new_room)
                print("The room '{}' was created successfully at {} by '{}' from @{}:{}\n".format(new_room.name,datetime.now(),client.username,client.IP,client.port))
                msg_success="Room '{}' created successfully!".format(room_name) 
                Send_Message(msg_success, key, client.socket)  
                for added_client in new_room.clients:
                    if(added_client.username!=client.username):
                        msg_to_added_client="You were added to the room '{}' by '{}'".format(new_room.name, client.username)
                        Send_Message(msg_to_added_client, key, added_client.socket)
            else:
                msg_exit="You don't have enough clients in your room (3).\n"
                msg_exit+="Your room wasn't created, you are now back in the chat.\n"
                Send_Message(msg_exit, key, client.socket) 
        else:
            Send_Message(error_msg, key, client.socket)
    else:
        Send_Message("Please write the correct attributes after the command. Please not that to create a room, you need at least 3 users including you", key, client.socket)




def Create_Room2(msg_recu, client, clients_connectes,  Rooms):
    name_clients=[]
    error_msg=""
    for cli in clients_connectes:
        name_clients.append(cli.username)
    exist=False
    if(len(msg_recu.split(' '))>1):
        room_name = msg_recu.lstrip(msg_recu.split(' ')[0])
        room_name = room_name[1:len(room_name)]
        
        if(room_name in name_clients):
            error_msg="The name of the room is already taken by a user, please try again and change the name.\n"
            exist=True
        for room in Rooms:
            if(room_name==room.name):
                error_msg="The name of the room is already taken by another room, please try again and change the name.\n"
                exist=True
                break
        if(not exist):
            return client, room_name
        else:
            Send_Message(error_msg,key,client.socket) 
    elif(len(msg_recu.split(' '))==1):
        Send_Message("Please precise a room name after the #CreateRoom command.",key,client.socket)                   
    
def Join_Room(msg_recu, client, clients_connectes,  Rooms):
    found=False
    if(len(msg_recu.split(' ')) > 1):
        room_name = msg_recu.lstrip(msg_recu.split(' ')[0])
        room_name = room_name[1:len(room_name)]
        for room in Rooms:
            if room.name==room_name:
                for client_in_room in room.clients:
                    if client.username==client_in_room.username:
                        client.room=room.name
                        found=True
                        break
                if(found): 
                    break
        if(found):
            msg="You are now in the room {}. \n".format(room_name)
            msg+="Every message you send can only be seen by members of this room.\n"
            Send_Message(msg,key,client.socket, force=True)
        else:
            msg="The room name you provided is either wrong or you don't belong to this room.\n"
            Send_Message(msg,key,client.socket, force=True)
    elif (len(msg_recu.split(' ')) == 1):
        Send_Message("Please write a user's name after the command", key, client.socket)
    else:
        raise Exception

def Add_Room(msg_recu, client, clients_connectes,  Rooms):
    check_room = False
    check_added_client = False

    if(len(msg_recu.split(' ')) > 2):
        msg_recu = msg_recu.split(' ')
        client_to_add = msg_recu[1]
        room_name = msg_recu[2:len(msg_recu)]
        room_name = " ".join(room_name)

        name_clients_connected=[]
        for cli in clients_connectes:
            name_clients_connected.append(cli.username)

        name_clients_room=[]
        for room in Rooms:
            if (room.name == room_name):
                for cli in room.clients:
                    name_clients_room.append(cli.username)

        for room in Rooms:
            if (room_name == room.name):
                check_room = True
                if (client.username == room.admin.username):
                    for cli in clients_connectes:
                        if (cli.username == client_to_add and (client_to_add in name_clients_connected) and (client_to_add not in name_clients_room)):
                            check_added_client = True
                            room.clients.append(cli)
                            msg_to_added_client="You were added to the room '{}' by '{}'".format(room_name, client.username)
                            Send_Message(msg_to_added_client.encode(), key, cli.socket)
                            break
                else:
                    Send_Message("You can't do this action because you are not the admin of the room", key, client.socket)
                break

        if (not check_room):
            Send_Message("The room name you wrote doesn't exist", key, client.socket)

        if (not check_added_client and check_room):
            Send_Message("The user is either not connected or already in the room", key, client.socket)
    else:
        Send_Message("Please write the correct attributes after the command", key, client.socket)

def Kick_Room(msg_recu, client, clients_connectes,  Rooms):
    check_room = False
    check_kicked_client = False

    if(len(msg_recu.split(' ')) > 2):
        msg_recu = msg_recu.split(' ')
        client_to_kick = msg_recu[1]
        room_name = msg_recu[2:len(msg_recu)]
        room_name = " ".join(room_name)

        name_clients_connected=[]
        for cli in clients_connectes:
            name_clients_connected.append(cli.username)

        name_clients_room=[]
        for room in Rooms:
            if (room.name == room_name):
                for cli in room.clients:
                    name_clients_room.append(cli.username)

        for room in Rooms:
            if (room_name == room.name):
                check_room = True
                if (client.username == room.admin.username):
                    for cli in clients_connectes:
                        if (cli.username == client_to_kick and (client_to_kick in name_clients_connected) and (client_to_kick in name_clients_room)):
                            check_kicked_client = True
                            room.clients.remove(cli)
                            cli.room = "public"
                            msg_to_kicked_client="You were kicked from the room '{}' by '{}'.\n".format(room_name, client.username)
                            msg_to_kicked_client+="You are now back at the public chat."
                            Send_Message(msg_to_kicked_client.encode(), key, cli.socket)
                            break
                else:
                    Send_Message("You can't do this action because you are not the admin of the room", key, client.socket)
                break

        if (not check_room):
            Send_Message("The room name you wrote doesn't exist", key, client.socket)

        if (not check_kicked_client and check_room):
            Send_Message("The user is either not connected or not in the room", key, client.socket)
    else:
        Send_Message("Please write the correct attributes after the command", key, client.socket)

def Leave_Room(msg_recu, client, clients_connectes,  Rooms):
    found=False
    if(len(msg_recu.split(' ')) > 1):
        room_name = msg_recu.lstrip(msg_recu.split(' ')[0])
        room_name = room_name[1:len(room_name)]
        index_removing_room=-1
        for room in Rooms:
            index_removing_room+=1
            if room.name==room_name:
                index_removing_client=-1
                for client_in_room in room.clients:
                    index_removing_client+=1
                    if client.username==client_in_room.username:
                        room.clients.pop(index_removing_client)
                        msg="'{}' Left the Chat Room '{}'.\n".format(client.username, room.name)
                        if(len(room.clients)<2):
                            msg+="Chat room was dissolved because too few people were remaining.\n"
                            for member in room.clients:
                                Send_Message(msg,key, member.socket)
                            Rooms.pop(index_removing_room)
                        elif(client.username==room.admin.username):
                            room.admin=room.clients[0]
                            msg="You are now the admin of the chat room '{}'.\n".format(room.name)
                            Send_Message(msg,key, room.admin.socket)
                        else:
                            for member in room.clients:
                                Send_Message(msg,key, member.socket)
                        found=True
                        break
                if(found): 
                    break
        if(found): 
            Send_Message("You left the chat room.\n", key, client.socket)
        else:
            Send_Message("You either typed a wrong room name or don't belong to this room.\n", key, client.socket)
    else:
        raise Exception 


def List_Client_Room(msg_recu, client, clients_connectes,  Rooms):
    exist=False
    if(len(msg_recu.split(' ')) > 1):
        room_name = msg_recu.lstrip(msg_recu.split(' ')[0])
        room_name = room_name[1:len(room_name)]
        list_clients="Here is the list of clients belonging to Chat room '{}':".format(room_name)
        for room in Rooms:
            if room_name==room.name:
                for cli in room.clients:
                    if cli.username==client.username: #If client doesn't belong to the room, he can't see its members
                        exist=True
                    if cli.username==room.admin.username:
                        list_clients+="\n   "+cli.username+" (admin)"
                    else:
                        list_clients+="\n   "+cli.username
                break
        if(exist):
            Send_Message(list_clients,key,client.socket, force=True)
        else:
            Send_Message("The room name you provided is either wrong or you don't belong to this room.\n",key,client.socket, force=True)
    else:
        raise Exception
            

    
                            
def Client_Upload(msg_recu,client, clients_connectes, Rooms):
    filename, filesize = msg_recu.split("<>")
    filename = filename.split(" ",1)[1]
    filename = os.path.basename(filename)
    filesize = int(filesize)
    #Start File-receiver Thread 
    clients_connectes.remove(client) #client connectés remove plutot
    Send_Message("OK UPLOAD", key, client.socket)
    #client.socket.send(b"OK UPLOAD")
  

    filename_sans_extension, extension = filename.split(".")

    try: #Create directory to save files downloaded from server
        os.makedirs("Files_Uploaded")
    except:
        pass

    filename_for_save = "Files_Uploaded/{}_{}.{}".format(filename_sans_extension,''.join(random.choices(string.ascii_letters + string.digits, k=10)), extension)
    #Ajouter un code à la fin du nom de base du fichier afin d'éviter des remplacements de fichier si plusieurs ont le même nom
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
    clients_connectes.append(client)


def Client_Ring(msg_recu,client, clients_connectes, Rooms):
    client_target_existed = False
    if(len(msg_recu.split(' ')) == 2): #on peut se permettre de verifier s'il n'y a que deux termes car le username ne peut pas contenir d'espace (regle qu'on a fixée)
        for other_client in clients_connectes:
            if (other_client.username == msg_recu.split(' ')[1]):
                client_target_existed = True
                msg = "\nThe user : '{}' try to reach you.\n".format(client.username) 
                Send_Message(msg.encode(), key, other_client.socket)
    
    if (len(msg_recu.split(' ')) == 1):
        Send_Message("Please write a user's name after the command", key, client.socket)

    if (client_target_existed == False and len(msg_recu.split(' ')) != 1):
        Send_Message("User you tried to ring is not connected or not existing", key, client.socket)

def Client_ListF(msg_recu,client, clients_connectes, Rooms):
    list_files = os.listdir("Files")
    msg_a_envoyer = "Liste des fichier : \n"
    for fichier in list_files:
        msg_a_envoyer+= "{} \n".format(fichier)
    msg_a_envoyer = msg_a_envoyer
    Send_Message(msg_a_envoyer,key,client.socket, force=True)

def Client_Download(msg_recu,client, clients_connectes, Rooms):
    filename=""
    filesize = ""
    try:
        filename = msg_recu.split(' ',1)[1]
        filesize = os.path.getsize("Files/"+filename)
        msg_a_envoyer = "#TrfD {}<>{}".format(filename,filesize)
        msg_a_envoyer = msg_a_envoyer
    except:
        msg_a_envoyer = "#TrfD Error with file"
    Send_Message(msg_a_envoyer,key,client.socket)


    if(filesize != ""): #Si le file a bien été trouvé
        #connexion_avec_serveur.send(msg_a_envoyer)
        clients_connectes.remove(client) # On ne veut rien lui envoyer d'autre que le fichier
        client_ready = False
        recu = ""
        while(not client_ready):
            try:
                recu = Receive_Message(key, client.socket).decode()
            except:
                pass
            if(recu == "OK DOWNLOAD"): client_ready=True
        threading.Thread(target=Thread_File_Sender, args=(filename,filesize,client,clients_connectes,)).start()

def Thread_File_Sender (filename,filesize,client, client_connectes):
    
    #start sending file
    sum_bytes=0
    percent=0
    with open("Files/"+filename, "rb") as f:
        while(True):
			# read the bytes from the file
            bytes_read = f.read(1024)
            if not bytes_read:
				# file transmitting is done
                break
			# we use sendall to assure transimission in 
			# busy networks
            sum_bytes+= len(bytes_read)
            percent = (int) (sum_bytes/filesize)*100
            print("", end=f"\r {filename} envoyé à '{client.username}' : {percent} %")
            client.socket.sendall(bytes_read)
            
			# update the progress bar
    print()
    client_connectes.append(client)
    

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

def Check_client_functions(msg_recu, client, clients_connectes,  Rooms):
    commande = msg_recu.split(' ')[0]

    try:
        return options[commande](msg_recu,client, clients_connectes,  Rooms)
    except :
        Send_Message("Command not found, try using #Help",key,client.socket)
    

