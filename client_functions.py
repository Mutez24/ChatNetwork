# Import sockets libraries
import socket
import select

EXIT_CLIENT = "#Exit" #Command used by clients to leave

def Check_client_functions(msg_recu, client):
    return