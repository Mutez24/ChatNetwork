'''
• Client function (command line):
#! 1) #Help (list command)
#! 2) #Exit (client exit)
#TODO VALOT 3) #ListU (list of users in a server)
#TODO Rémi 4) #ListF (list of files in a server)
#TODO Rémi 5) #TrfU (Upload file transfer to a server)
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

#! Commandes clients
EXIT_CLIENT = "#Exit" #Command used by clients to leave
HELP_CLIENT = "#Help" #Command used by clients to get help
#TODO TOUJOURS mettre les 3 mêmes paramètres dans chaque fonction même si on ne se sert pas des 3
#TODO En effet les appels de fonctions sont définis par défaut avec ces paramètres dans la fonction Check_client_functions

def Client_Exit (client,msg_recu, clients_connectes):
    if(msg_recu == EXIT_CLIENT):
        msg_client="'{}' left the chat".format(client.username)
        print("{} @{}:{} | '{}' has left the chat \n".format(datetime.now(), client.IP, client.port, client.username)) 

        for element in clients_connectes:
            if (client != element):
                element.socket.send(msg_client.encode())
        clients_connectes.remove(client)
        client.socket.close()
    
    else :
        raise Exception
        
def Client_Help (client,msg_recu, clients_connectes):
    if(msg_recu == HELP_CLIENT):
        msg = "You can find a list of available commands below : \n \n \
        #Help (list command) \n \
        #Exit (exit chat) \n \
        #ListF (list of files in a server) \n \
        #ListU (list of users in a server) \n \
        #TrfU (Upload file transfer to a server) \n \
        #TrfD (transfer Download file to a server) \n \
        #Private <user> (private chat with another user) \n \
        #Public (back to the public) \n \
        #Ring <user> (notification if the user is logged in)"

        client.socket.send(msg.encode())
    else:
        raise Exception





options = {
        EXIT_CLIENT : Client_Exit,
        HELP_CLIENT : Client_Help
    }

def Check_client_functions(msg_recu, client, clients_connectes):
    commande = msg_recu.split(' ')[0]

    try:
        options[commande](client,msg_recu, clients_connectes)
    except :
        msg = b"Command not found, try using #Help"
        client.socket.send(msg)
    

