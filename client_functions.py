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
        pass
    
    else :
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
    

