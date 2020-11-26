# Import sockets libraries
import socket
import select

# Import display library
from datetime import datetime

EXIT_CLIENT = "#Exit" #Command used by clients to leave

def Client_Exit (client,msg_recu, clients_connectes):
    if(msg_recu == "#Exit"):
        msg_client="'{}' left the chat".format(client.username)
        print("{} @{}:{} | '{}' has left the chat \n".format(datetime.now(), client.IP, client.port, client.username)) 

        for element in clients_connectes:
            if (client != element):
                element.socket.send(msg_client.encode())
        clients_connectes.remove(client)
        client.socket.close()
    
    else :
        raise Exception
        






options = {
        EXIT_CLIENT : Client_Exit
    }

def Check_client_functions(msg_recu, client, clients_connectes):
    commande = msg_recu.split(' ')[0]

    try:
        options[commande](client,msg_recu, clients_connectes)
    except :
        msg = b"Command not found, try using #Help"
        client.socket.send(msg)
    

