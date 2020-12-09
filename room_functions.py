# Import display library
from datetime import datetime

# Import nedded files
from cyphering import *
from RoomClass import *
from ClientClass import *
key = "salut"

'''
#* Fonction permettant de créer une room à partir d'un nom de room et de au moins 2 noms de clients.

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Create_Room_RF(msg_recu, client, clients_connectes, Rooms):
    #On vérifie d'abord que le msg_recu comporte bien au moins 4 arguments.
    #Dans le cas contraire, la fonction ne peut pas fonctionner étant donné qu'elle
    #nécessite 1 nom de room et 2 noms de users minimum (sans espace dans les noms)
    if(len(msg_recu.split(' '))>3):
        success=False
        msg_recu = msg_recu.split(' ')
        room_name = msg_recu[1]
        name_clients_typed = msg_recu[2:len(msg_recu)]

        #On vérifie que le créateur de la room ne rentre pas son propre nom dans la liste des clients à ajouter
        if(not client.username in name_clients_typed):
            #On vérifie que le nom de la room n'est pas déjà emprunté par un client.
            if(Room.Check_Name_With_Clients(room_name, clients_connectes)):
                #On vérifie que le nom de la room n'est pas déjà emprunté par une autre room.
                if(not Room.Check_Name(room_name,Rooms)):
                    #On récupère les objets clients à partir de leur username.
                    clients_typed=Client.List_Clients(name_clients_typed, clients_connectes)
                    #Si le nombre de clients récupérés est inférieur au nombre de noms,
                    #cela signifie que un ou plusieurs noms de client ne correspondait 
                    #à aucun client existant ou connecté
                    if(len(clients_typed)!=len(name_clients_typed)):
                        Send_Message("One or more client's name you typed don't match any connected client.\n", key, client.socket)
                    #On vérifie qu'on a au moins 2 clients valides pour créer la room.
                    if(len(clients_typed)>=2):
                        new_room=Room(room_name,client) #On crée l'objet room
                        for member in clients_typed: #On ajoute chaque client en les notifiant d'un message
                            new_room.clients.append(member)
                            msg_to_added_client="You were added to the room '{}' by '{}'.\n".format(new_room.name, client.username)
                            Send_Message(msg_to_added_client, key, member.socket)
                        Rooms.append(new_room) #On rend l'objet room consistant en l'ajoutant à Rooms
                        success=True
                        msg_to_admin= "The room '{}' was created successfully\n".format(new_room.name)
                        Send_Message(msg_to_admin,key,client.socket)
                        print("The room '{}' was created successfully at {} by '{}' from @{}:{}\n".format(new_room.name,datetime.now(),client.username,client.IP,client.port))                       
                    else:
                        Send_Message("You don't have enough clients to add to your group.\n", key, client.socket)
                else:
                    Send_Message("The room name is already taken by another room, please try again and change the name.\n", key, client.socket)
            else:
                Send_Message("The room name is invalid because a client has the same name.\n", key, client.socket)
            if(not success):
                Send_Message("Your room wasn't created, you are now back in the chat.\n", key, client.socket)    
        else:
            Send_Message("You can't write your own name in the list of users to add, you will be added automatically as admin.\n", key, client.socket)
    else:
        Send_Message("Please write the correct attributes after the command. \nPlease note that to create a room, you need at least 3 users including you.\n", key, client.socket)


''' fonction non utilisé à ce jour mais aurait pu l'être avec Create_Room_Server dans server.py si le tout avait été plus fonctionnel
def Create_Room2_RF(msg_recu, client, clients_connectes, Rooms):
    name_clients=[]
    error_msg=""
    for cli in clients_connectes:
        name_clients.append(cli.username)
    exist=False
    if(len(msg_recu.split(' '))>1):
        room_name = msg_recu.lstrip(msg_recu.split(' ')[0])
        room_name = room_name[1:len(room_name)]
        
        if(room_name in name_clients):
            error_msg=b"The name of the room is already taken by a user, please try again and change the name.\n"
            exist=True
        for room in Rooms:
            if(room_name==room.name):
                error_msg=b"The name of the room is already taken by another room, please try again and change the name.\n"
                exist=True
                break
        if(not exist):
            return client, room_name
        else:
            Send_Message(error_msg,key,client.socket) 
    elif(len(msg_recu.split(' '))==1):
        Send_Message(b"Please precise a room name after the #CreateRoom command.",key,client.socket)                   
'''  


'''
#* Fonction permettant à un membre d'une room de rejoindre une room à laquelle il appartient.

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Join_Room_RF(msg_recu, client, clients_connectes, Rooms):
    if(len(msg_recu.split(' ')) > 1):
        msg_recu = msg_recu.split(' ')
        room_name = msg_recu[1]
        #On vérifie que le nom de la room est valide cad existant.
        if Room.Check_Name(room_name, Rooms):
            room=Room.Get_Room(room_name, Rooms) #On peut ainsi récupérer l'objet room à partir de son nom
            #On vérifie que le client qui demande à rejoindre appartient bien à la room
            if room.Check_Client(client.username):
                #On modifie l'attribut room de Client pour que désormais chaque message qu'il envoie
                #soit reçu par chaque membre du groupe
                client.room=room.name    
                msg="You are now in the room {}.\n".format(room_name)
                msg+="Every message you send can only be seen by members of this room.\n"
                Send_Message(msg, key, client.socket, force=True)
            else:
                Send_Message("You don't belong to this room.\n", key, client.socket)
        else:
            Send_Message("You typed a wrong room name. \n", key, client.socket)

    elif (len(msg_recu.split(' ')) == 1):
        Send_Message("Please write a room name after the command.\n", key, client.socket)
    else:
        raise Exception


'''
#* Fonction permettant à l'admin du groupe d'ajouter un client à la room.

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Add_Room_RF(msg_recu, client, clients_connectes, Rooms):
    if(len(msg_recu.split(' ')) > 2):
        msg_recu = msg_recu.split(' ')
        room_name = msg_recu[1]
        name_client_to_add = msg_recu[2]

        #On vérifie que le nom de la room est valide cad existant.
        if Room.Check_Name(room_name, Rooms):
            room=Room.Get_Room(room_name, Rooms)
            #On vérifie que le client appartient bien à la room.
            if room.Check_Client(client.username):
                #On vérifie que le client est bien l'admin de la room.
                if (client == room.admin):
                    #on regarde si le client à ajouter est connecté.
                    if Client.Check_Client_Connected(name_client_to_add, clients_connectes):
                        client_to_add=Client.Get_Client(name_client_to_add, clients_connectes)
                        room.clients.append(client_to_add)
                        msg_to_added_client="You were added to the room '{}' by '{}'.\n".format(room_name, client.username)
                        Send_Message(msg_to_added_client, key, client_to_add.socket)
                        #On notifie tous les autres membres de l'ajout.
                        msg_to_other="'{}' was added to the room '{}' by '{}'.\n".format(name_client_to_add, room_name, client.username)
                        for other_client in room.clients:
                            if other_client!=client_to_add:
                                Send_Message(msg_to_other, key, other_client.socket)
                    else:
                        Send_Message("The client you want to add doesn't exist or isn't connected.\n", key, client.socket)
                else: 
                    Send_Message("You aren't the admin of this room.\n", key, client.socket)        
            else:
                Send_Message("You don't belong to this room.\n", key, client.socket)
        else:
            Send_Message("You typed a wrong room name. \n", key, client.socket)
    else:
        Send_Message("Please write the correct attributes after the command.\n", key, client.socket)


'''
#* Fonction permettant à l'admin du groupe d'enlever un client de la room.

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Kick_Room_RF(msg_recu, client, clients_connectes, Rooms):
    if(len(msg_recu.split(' ')) > 2):
        msg_recu = msg_recu.split(' ')
        room_name = msg_recu[1]
        name_client_to_kick = msg_recu[2]
        #On vérifie que le nom de la room est valide cad existant.
        if Room.Check_Name(room_name, Rooms):
            room=Room.Get_Room(room_name, Rooms)
            #On vérifie que le client appartient bien à la room.
            if room.Check_Client(client.username):
                #On vérifie que le client est bien l'admin de la room.
                if (client == room.admin):
                    #On vérifie que le client à kick est bien dans la room.
                    if room.Check_Client(name_client_to_kick):
                        client_to_kick=room.Get_Client(name_client_to_kick)
                        room.clients.remove(client_to_kick)
                        client_to_kick.room = "public"
                        msg_to_kicked_client="You were kicked from the room '{}' by '{}'.\n".format(room_name, client.username)
                        msg_to_kicked_client+="You are now back at the public chat.\n"
                        Send_Message(msg_to_kicked_client, key, client_to_kick.socket)

                        #On notifie tous les autres membres de la suppression.
                        msg_to_other="'{}' was kicked from the room '{}' by '{}'.\n".format(name_client_to_kick,room_name, client.username)
                        for other_client in room.clients:
                            if other_client!=client_to_kick:
                                Send_Message(msg_to_other, key, other_client.socket)

                        #Si le nombre de clients appartenant à la room descend en dessous de 2,
                        #alors la room n'a plus de raison d'exister et on la supprime.
                        if(len(room.clients)<2):
                            msg="Chat room was dissolved because too few people were remaining (< 2).\n"
                            for member in room.clients:
                                Send_Message(msg,key, member.socket)
                            Rooms.remove(room)
                    else:
                        Send_Message("The client you want to kick doesn't belong to this room.\n", key, client.socket)
                else: 
                    Send_Message("You aren't the admin of this room.\n", key, client.socket)        
            else:
                Send_Message("You don't belong to this room.\n", key, client.socket)
        else:
            Send_Message("You typed a wrong room name. \n", key, client.socket)
    else:
        Send_Message("Please write the correct attributes after the command.\n", key, client.socket)


'''
#* Fonction permettant de supprimer le client de la room mentionnée.

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def Leave_Room_RF(msg_recu, client, clients_connectes, Rooms):
    if(len(msg_recu.split(' ')) > 1):
        msg_recu = msg_recu.split(' ')
        room_name = msg_recu[1]

        #On vérifie que le nom de la room est valide cad existant.
        if Room.Check_Name(room_name, Rooms):
            room=Room.Get_Room(room_name, Rooms)
            #On vérifie que le client appartient bien à la room.
            if room.Check_Client(client.username):
                room.clients.remove(client)
                msg_leaver="You left the chat room '{}'.\n".format(room.name)
                Send_Message(msg_leaver, key, client.socket)

                msg="'{}' Left the Chat Room '{}'.\n".format(client.username, room.name)
                #Si le nombre de clients appartenant à la room descend en dessous de 2,
                #alors la room n'a plus de raison d'exister et on la supprime.
                if(len(room.clients)<2):
                    msg+="Chat room was dissolved because too few people were remaining.\n"
                    for member in room.clients:
                        Send_Message(msg,key, member.socket)
                    Rooms.remove(room)
                #Si le client qui quitte la room est admin, il faut en élire un nouveau.
                elif(client==room.admin):
                    room.admin=room.clients[0]
                    msg="You are now the admin of the chat room '{}'.\n".format(room.name)
                    Send_Message(msg,key, room.admin.socket)
                else:
                    for member in room.clients:
                        Send_Message(msg,key, member.socket)
            else:
                Send_Message("You don't belong to this room.\n", key, client.socket)
        else:
            Send_Message("You typed a wrong room name. \n", key, client.socket)
    else:
        raise Exception 


'''
#* Fonction permettant de lister tous les clients d'une room à un client appartenant à cette room.

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def List_Client_Room_RF(msg_recu, client, clients_connectes, Rooms):
    exist=False
    if(len(msg_recu.split(' ')) > 1):
        msg_recu = msg_recu.split(' ')
        room_name = msg_recu[1]
        
        #On vérifie que le nom de la room est valide cad existant.
        if Room.Check_Name(room_name,Rooms):
            list_clients="Here is the list of clients belonging to Chat room '{}':".format(room_name)
            room=Room.Get_Room(room_name, Rooms)
            #On vérifie que le client appartient bien à la room.
            if room.Check_Client(client.username):
                for cli in room.clients:
                    if cli==room.admin:
                        list_clients+="\n   "+cli.username+" (admin)"
                    else:
                        list_clients+="\n   "+cli.username
                    if cli==client:
                        list_clients+=" (you)"

                Send_Message(list_clients,key,client.socket, force=True)
            else:
                Send_Message("You don't belong to this room.\n",key,client.socket, force=True)
        else:
            Send_Message("The room name you provided is wrong or the room doesn't exist.\n",key,client.socket, force=True)
    else:
        raise Exception


'''
#* Fonction permettant d'afficher toutes les rooms à laquelle le client appartient.

#? msg_recu : input ecrit par un client
#? client : client qui a ecrit le message
#? clients_connectés : liste qui contient les clients connectés
#? Rooms : liste de toutes les room
'''
def List_Room_RF(msg_recu, client, clients_connectes, Rooms):
    msg=""
    #On récupère les rooms auxquelles le client appartient.
    list_rooms=client.List_Rooms(Rooms)
    if(len(list_rooms)!=0):
        msg="Here is the list of private Chat room you belong to:\n   "
        for room in list_rooms:
            msg+=room.name+"\n   "
    else:
        msg="You don't belong to any private Chat room.\n"
    Send_Message(msg,key,client.socket, force=True)