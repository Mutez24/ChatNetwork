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
			print()
			
def Check_file_size (msg_a_envoyer):
	filename=""
	filesize = ""
	try:
		filename = msg_a_envoyer.split(' ',1)[1]
		filesize = os.path.getsize(filename)
		msg_a_envoyer = "#TrfU {}<>{}".format(filename,filesize)
		msg_a_envoyer = msg_a_envoyer.encode()
	except:
		print("Error with your file")
		
	return msg_a_envoyer,filename,filesize

def save_file(msg_recu, connexion_avec_serveur):
	#Dans msg_recu il n'y a que ce qu'il y a après le #TrfD
	if(msg_recu == "Error with file"):
		print(msg_recu)
	else:
		filename, filesize = msg_recu.split("<>")
		filesize =  int(filesize)
		filename_for_save = "Download_Server/" + filename
		Send_Message(b"OK DOWNLOAD", key, connexion_avec_serveur)
		sum_bytes=0
		percent=0
		with open(filename_for_save, "wb") as f:
			while(True):
            # read 1024 bytes from the socket (receive)
				try:
					percent = (int) (sum_bytes/filesize)*100
					print("", end=f"\r {filename} envoyé par Serveur reçu: {percent} %")
					connexion_avec_serveur.settimeout(0.5)
					bytes_read = connexion_avec_serveur.recv(1024) #On laisse l'ancien recv à cause des problèmes de chiffrement
					sum_bytes+= len(bytes_read)
					
				except :
					connexion_avec_serveur.settimeout(0.05)
					break  
            # write to the file the bytes we just received
				f.write(bytes_read)
		print()

	

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
				if(filesize != ""): #Check if file really exists
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
						if(recu == "OK UPLOAD"): serveur_ready=True
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
			if (msg_recu.split(' ')[0] == "#TrfD"): #Si on s'apprête à recevoir des données fichier
				save_file(msg_recu.split(' ',1)[1], connexion_avec_serveur)
			else:
				print(msg_recu) # Là encore, peut planter s'il y a des accents
		except socket.timeout:	
			pass
		
	print("Fermeture de la connexion")
	connexion_avec_serveur.close()

if (__name__ == '__main__'): 
    main()
