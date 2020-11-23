# Import threading libraries
import threading
import queue
import time

# Import sockets libraries
import socket
import select



def read_kbd_input(inputQueue):
    print('Ready for keyboard input:')
    while (True):
        # Receive keyboard input from user.
        input_str = input()
        
        # Enqueue this input string.
        # Note: Lock not required here since we are only calling a single Queue method, not a sequence of them 
        # which would otherwise need to be treated as one atomic operation.
        inputQueue.put(input_str)

def main():

    #! Set up socket variables
    hote = ''
    port = 12800
    connexion_principale = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    connexion_principale.bind((hote, port))
    connexion_principale.listen(5)
    clients_connectes = []
    serveur_lance = True


    EXIT_COMMAND = "exit" # Command to exit this program

    #Keyboard input queue to pass data from the thread reading the keyboard inputs to the main thread.
    inputQueue = queue.Queue()

    # Create & start a thread to read keyboard inputs.
    # Set daemon to True to auto-kill this thread when all other non-daemonic threads are exited. This is desired since
    # this thread has no cleanup to do, which would otherwise require a more graceful approach to clean up then exit.
    inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
    inputThread.start()

    print("Le serveur écoute à présent sur le port {}".format(port))

    #TODO Main loop
    while (serveur_lance):

        # Read keyboard inputs
        if (inputQueue.qsize() > 0):
            input_str = inputQueue.get()
            print("input_str = {}".format(input_str))

            if (input_str == EXIT_COMMAND):
                print("Exiting serial terminal.")
                break # exit the while loop
            
            # Insert your code here to do whatever you want with the input_str.

        #! The rest of your program goes here.
        
        # On va vérifier que de nouveaux clients ne demandent pas à se connecter
        # Pour cela, on écoute la connexion_principale en lecture
        # On attend maximum 50ms
        connexions_demandees, wlist, xlist = select.select([connexion_principale], [], [], 0.05)
        
        for connexion in connexions_demandees:
            connexion_avec_client, infos_connexion = connexion.accept()
            # On ajoute le socket connecté à la liste des clients
            clients_connectes.append(connexion_avec_client)
        
        # Maintenant, on écoute la liste des clients connectés
        # Les clients renvoyés par select sont ceux devant être lus (recv)
        # On attend là encore 50ms maximum
        # On enferme l'appel à select.select dans un bloc try
        # En effet, si la liste de clients connectés est vide, une exception
        # Peut être levée
        clients_a_lire = []
        try:
            clients_a_lire, wlist, xlist = select.select(clients_connectes,[], [], 0.05)
        except select.error:
            pass
        else:
            # On parcourt la liste des clients à lire
            for client in clients_a_lire:
                # Client est de type socket
                msg_recu = client.recv(1024)
                # Peut planter si le message contient des caractères spéciaux
                msg_recu = msg_recu.decode()
                print("Reçu {}".format(msg_recu))
                client.send(b"5 / 5")
                if msg_recu == "fin":
                    serveur_lance = False
        # Sleep for a short time to prevent this thread from sucking up all of your CPU resources on your PC.
        time.sleep(0.01) 
    
    print("Fermeture des connexions")
    for client in clients_connectes:
        client.close()
    connexion_principale.close()
    print("End.")

# If you run this Python file directly (ex: via `python3 this_filename.py`), do the following:
if (__name__ == '__main__'): 
    main()