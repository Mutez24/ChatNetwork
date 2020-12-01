'''
• Server function (command line):
#! 1) #Help (list command)
#! 2) #Exit (server shutdown)
#! 3) #Kill <user>
#! 4) #ListU (list of users in a server)
5) #ListF (list of files in a server)
#! 6) #Private <user> (private chat with another user)
#! 7) #Alert <all users>
'''
# Import sockets libraries
import socket

#Import display libraries
from datetime import datetime


#! Commandes serveur
EXIT_SERVER = "#Exit" #Command used by server to shutdown
HELP_SERVER = "#Help" #Command used by server to get help
KILL_SERVER = "#Kill" #Command used by server to kill user terminal
LISTU_SERVER = "#ListU" #Command used by the server to display all the connected users
ALERT_SERVER = "#Alert" #Command used by the server to send a message to all users
PRIVATE_SERVER = "#Private" ##Command used by the server to send a message to a particular user

def Server_Exit(input_server, clients_connectes,connexion_principale,connexions_demandees):
    if(input_server == EXIT_SERVER):
        print("Server closing...")
        for client in clients_connectes:
            client.socket.send(b"Server shutdown")
            client.socket.close()
        
        ''' test pour close les users qui sont en train de se connecter ou creer un compte quand le serveur shutdown. Si fonctionne pas retirer connexion_demandees 
        for client in connexions_demandees:
            client.socket.send(b"Server shutdown")
            client.socket.close()
        '''
        connexion_principale.close()
        return ("exit", "")

    else :
        raise Exception

def Server_Kill(input_server, clients_connectes,connexion_principale,connexions_demandees):
    client_connected_existed = False
    if(len(input_server.split(' ')) == 2): #on peut se permettre de verifier s'il n'y a que deux termes car le username ne peut pas contenir d'espace (regle qu'on a fixée)
        for client in clients_connectes:
            if (client.username == input_server.split(' ')[1]):
                client_connected_existed = True
                client.socket.send(b"You were kicked by server")
                client.socket.close()
                clients_connectes.remove(client)
                print("User '{}' was kicked by server at {} from @{}:{}".format(client.username, datetime.now(), client.IP, client.port))

                for client_not_kicked in clients_connectes:
                    if (client_not_kicked != client):
                        msg = "User '{}' was kicked by server".format(input_server.split(' ')[1])
                        client_not_kicked.socket.send(msg.encode())
    
    if (len(input_server.split(' ')) == 1):
        print("Please write a client name after the command")

    if (not client_connected_existed and len(input_server.split(' ')) != 1):
        print("Client not connected or not existing")

def Server_Help(input_server, clients_connectes,connexion_principale,connexions_demandees):
    msg = "You can find a list of available commands below : \n \n \
    #Help (list command) \n \
    #Exit (server shutdown) \n \
    #Kill <user> (kick <user> from server) \n \
    #ListU (list of users in a server) \n \
    #ListF (list of files in a server) \n \
    #Private <user> (private chat with another user) \n \
    #Alert <msg> (send msg to all users)"

    print(msg)

def Server_ListU(input_server, clients_connectes,connexion_principale,connexions_demandees):
    print("The following users are connected to the server :")
    for client in clients_connectes:
        print("   - User '{}' from @{}:{}".format(client.username, client.IP, client.port))

def Server_Alert(input_server, clients_connectes,connexion_principale,connexions_demandees):
    if(len(input_server.split(' ')) != 1): #si l'input c'est pas seulement #Alert car dans ce cas il n'y a pas de message
        msg =""
        for word in input_server.split(' '):
            msg+= word + " "
        msg = msg.lstrip(input_server.split(' ')[0]) #On retire la #command
        msg = "MESSAGE FROM SERVER :" +msg

        for client in clients_connectes:
            client.socket.send(msg.encode())

    else:
        print("There is nothing to send. If you want to send something, write a message after the command")


def Server_Private(input_server, clients_connectes,connexion_principale,connexions_demandees):
    client_connected_existed = False
    if(len(input_server.split(' ')) == 2): #on peut se permettre de verifier s'il n'y a que deux termes car le username ne peut pas contenir d'espace (regle qu'on a fixée)
        for client in clients_connectes:
            if (client.username == input_server.split(' ')[1]):
                client_connected_existed = True
                client_name = input_server.split(' ')[1]
        
        return ("private_conv", client_name)
    
    if (len(input_server.split(' ')) == 1):
        print("Please write a client name after the command")

    if (not client_connected_existed and len(input_server.split(' ')) != 1):
        print("Client not connected or not existing")

    


options = {
        EXIT_SERVER : Server_Exit,
        KILL_SERVER : Server_Kill,
        HELP_SERVER : Server_Help,
        LISTU_SERVER : Server_ListU,
        ALERT_SERVER : Server_Alert,
        PRIVATE_SERVER : Server_Private,
    }

def Check_server_functions(input_server, clients_connectes,connexion_principale,connexions_demandees):
    commande = input_server.split(' ')[0]

    try:
        return options[commande](input_server, clients_connectes,connexion_principale,connexions_demandees)
    except :
        msg = "Command not found, try using #Help"
        print(msg)
