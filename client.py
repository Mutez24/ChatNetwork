import socket

# Import threading libraries
import threading
import queue
import time

def read_kbd_input(inputQueue):
    print('Ready for keyboard input:')
    while (True):
        
        # Receive keyboard input from user.
        input_str = input()
        
        # Enqueue this input string.
        inputQueue.put(input_str)
        

def main():
	inputQueue = queue.Queue()
	inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
	inputThread.start()

	hote = "localhost"
	port = 12800

	connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	connexion_avec_serveur.connect((hote, port))
	connexion_avec_serveur.settimeout(0.05)

	msg_a_envoyer = b""
	while msg_a_envoyer != b"#Exit":
		if (inputQueue.qsize() > 0):			
			msg_a_envoyer = inputQueue.get()			
			msg_a_envoyer = msg_a_envoyer.encode()			
			connexion_avec_serveur.send(msg_a_envoyer)
				
		try:			
			msg_recu = connexion_avec_serveur.recv(1024)
			msg_recu = msg_recu.decode()

			if (msg_recu == "Closing"): #ce message ne peut pas être envoyé par un client car un message envoyé par un client contient au minimum le username et un chevron
				break		
			print(msg_recu) # Là encore, peut planter s'il y a des accents
		except socket.timeout:	
			pass
		
	print("Fermeture de la connexion")
	connexion_avec_serveur.close()

if (__name__ == '__main__'): 
    main()
