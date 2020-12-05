import socket

# Import threading libraries
import threading
import queue
import time

from cyphering import *
key = "salut"

# Import files
import os

def read_kbd_input(inputQueue):
    print('Ready for keyboard input:')
    while (True):
        
        # Receive keyboard input from user.
        input_str = input()
        
        # Enqueue this input string.
        inputQueue.put(input_str)

def send_file(filename, filesize, connexion_avec_serveur):
	#start sending file
	sum_bytes=0
	percent=0
	with open(filename, "rb") as f:
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
			print("", end=f"\r {filename} envoyé : {percent} %")
			connexion_avec_serveur.sendall(bytes_read)
			# update the progress bar

def Check_file_size (msg_a_envoyer):

	try:
		filename = msg_a_envoyer.split(' ',1)[1]
		filesize = os.path.getsize(filename)
		msg_a_envoyer = "#TrfU {}<>{}".format(filename,filesize)
		msg_a_envoyer = msg_a_envoyer.encode()
	except:
		print("Error with your file")
		
	return msg_a_envoyer,filename,filesize

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
			#Fct check character + si ok encryption
			if(msg_a_envoyer.split(' ')[0] == "#TrfU"):
				msg_a_envoyer,filename,filesize = Check_file_size(msg_a_envoyer)
				Send_Message(msg_a_envoyer, key, connexion_avec_serveur)
				#connexion_avec_serveur.send(msg_a_envoyer)
				serveur_ready = False
				recu = ""
				while(not serveur_ready):
					try:
						recu = Receive_Message(key, connexion_avec_serveur).decode()
						#recu = connexion_avec_serveur.recv(1024).decode()
					except:
						pass
					if(recu == "OK"): serveur_ready=True
				threading.Thread(target=send_file, args=(filename,filesize,connexion_avec_serveur,)).start()
			else:
				msg_a_envoyer = msg_a_envoyer.encode()	
				Send_Message(msg_a_envoyer, key, connexion_avec_serveur)		
				#connexion_avec_serveur.send(msg_a_envoyer)
				
		try:	
			msg_recu = Receive_Message(key, connexion_avec_serveur)		
			#msg_recu = connexion_avec_serveur.recv(1024)
			msg_recu = msg_recu.decode()

			if (msg_recu == "Server shutdown" or msg_recu == "You were kicked by server"): #ce message ne peut pas être envoyé par un client car un message envoyé par un client contient au minimum le username et un chevron
				print(msg_recu)
				break		
			print(msg_recu) # Là encore, peut planter s'il y a des accents
		except socket.timeout:	
			pass
		
	print("Fermeture de la connexion")
	connexion_avec_serveur.close()

if (__name__ == '__main__'): 
    main()
