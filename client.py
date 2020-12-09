import socket

# Import librairies thread
import threading
import queue
import time

#Import composants pour le cyphering
from cyphering import *
key = "salut"

# Import os
import os


'''
#* Fonction permettant d'enregistrer dans une queue les caractères tapés par le client dans la console
#* On l'utilise dans un thread pour permettre au client d'écrire à tout moment

#? inputQueue : Queue utilisée pour sauvegarder les inputs du client 
'''
def read_kbd_input(inputQueue):
    print('Ready for keyboard input:')
    while (True):
        
        # Reçoit l'input clavier
        input_str = input()
        
        # Le met dans la queue
        inputQueue.put(input_str)


'''
#* Fonction permettant d'envoyer un fichier au serveur

#? filename : nom de sauvegarde du fichier
#? filesize : taille du fichier en byte
#? connexion_avec_serveur : socket serveur
'''
def send_file(filename, filesize, connexion_avec_serveur):
	# Début de l'envoi du fichier
	sum_bytes=0
	percent=0
	with open(filename, "rb") as f:
		while(True):
			# Lecture des bytes du fichier
			bytes_read = f.read(1024)
			if not bytes_read:
				# Transfert des données terminés
				break
			
			sum_bytes+= len(bytes_read)
			percent = (int) (sum_bytes/filesize)*100
			print("", end=f"\r {filename} envoyé : {percent} %")
			connexion_avec_serveur.send(bytes_read)
			# Envoi et mise à jour du pourcentage
		print()


'''
#* Fonction permettant d'obtenir filename, filesize et générer un message pour le serveur pour l'upload d'un fichier
#* Renvoi un filesize "" si le fichier est introuvable

#? msg_a_envoyer : Message sous la forme #TrfU <filename>
'''
def Check_file_size (msg_a_envoyer):
	filename=""
	filesize = ""
	try:
		filename = msg_a_envoyer.split(' ',1)[1]
		filesize = os.path.getsize(filename)
		msg_a_envoyer = "#TrfU {}<>{}".format(filename,filesize)
	except:
		print("Error with your file")
		
	return msg_a_envoyer,filename,filesize


'''
#* Fonction permettant de sauvegarder un fichier envoyé par le serveur dans le cas d'un Download

#? msg_recu : "Error with file" en cas d'erreur, sinon <filename><><filesize>
'''
def save_file(msg_recu, connexion_avec_serveur):
	#Dans msg_recu il n'y a que ce qu'il y a après le #TrfD
	if(msg_recu == "Error with file"):
		print(msg_recu)
	else:
		filename, filesize = msg_recu.split("<>")
		filesize =  int(filesize)
		try: 
			# Création d'un dossier pour sauvegarder les fichiers DL depuis le server
			os.makedirs("Files_Downloaded_from_server")
		except:
			# Dossier déjà existant
			pass
		filename_for_save = "Files_Downloaded_from_server/" + filename
		Send_Message("OK DOWNLOAD", key, connexion_avec_serveur)
		# Alerte le serveur que le client est prêt à recevoir la data du fichier
		sum_bytes=0
		percent=0
		with open(filename_for_save, "wb") as f:
			while(True):
            # Enregistrement du fichier
				try:
					percent = (int) (sum_bytes/filesize)*100
					print("", end=f"\r {filename} envoyé par Serveur reçu: {percent} %")
					connexion_avec_serveur.settimeout(0.5)
					# On augmente le timeout pour laisser plus de temps au server pour nous envoyer la data
					bytes_read = connexion_avec_serveur.recv(1024) 
					# On laisse cette version du recv pour éviter des problèmes lors du chiffrement
					sum_bytes+= len(bytes_read)
					
				except :
					connexion_avec_serveur.settimeout(0.05)
					# On remet à jour le timeout
					break  
            # On écrit le file qu'on reçoit
				f.write(bytes_read)
		print()

	

def main():
	# Création de la queue pour enregistrer les input et lancement du thread associé
	inputQueue = queue.Queue()
	inputThread = threading.Thread(target=read_kbd_input, args=(inputQueue,), daemon=True)
	inputThread.start()

	# Définition de la cible de la socket
	hote = "localhost"
	port = 12800

	# Création de la connexion et déclaration du timeout, il nous évite de rester bloqués à attendre un input

	try:
		connexion_avec_serveur = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		connexion_avec_serveur.connect((hote, port))
		connexion_avec_serveur.settimeout(0.05)
	except ConnectionRefusedError:
		print("Erreur Serveur")
		return 
		#Sortir du main


	msg_a_envoyer = ""

	# #Exit nous sert de message de sortie
	while msg_a_envoyer != b"#Exit":

		# S'il y a quelque chose dans la queue d'input
		if (inputQueue.qsize() > 0):			
			msg_a_envoyer = inputQueue.get()

			#* Si le msg commence par #TrfU, c'est qu'on veut faire un Upload de fichier
			#* Donc on doit récupérer les infos sur le fichier, les communiquer au server,
			#* Attendre son feu vert puis lui envoyer la data

			if(msg_a_envoyer.split(' ')[0] == "#TrfU"):
				msg_a_envoyer,filename,filesize = Check_file_size(msg_a_envoyer)
				if(filesize != ""): 
					# Si le fichier existe bien, on attend que le serveur nous dise qu'il est prêt à le recevoir
					# Pour cela on attend qu'il nous envoie "OK UPLOAD"
					Send_Message(msg_a_envoyer, key, connexion_avec_serveur)
					serveur_ready = False
					recu = ""
					# On attend que le serveur soit prêt
					while(not serveur_ready):
						try:
							recu = Receive_Message(key, connexion_avec_serveur)
						except:
							pass
						if(recu == "OK UPLOAD"): serveur_ready=True # Serveur prêt
					# Quand le serveur est prêt, on lance le thread d'envoi de fichier
					threading.Thread(target=send_file, args=(filename,filesize,connexion_avec_serveur,)).start()
			else:
				# Si l'on ne souhaite pas faire d'Upload de fichier, on peut envoyer le message tel quel
				Send_Message(msg_a_envoyer, key, connexion_avec_serveur)		
				
				
		try:	
			msg_recu = Receive_Message(key, connexion_avec_serveur)

			#! Message envoyés par le serveur
			#! Un msg ayant cette forme exacte provient forcément du server
			#! S'il venait d'un client, il y aurait le préfixe <username> et un chevron
			if (msg_recu == "Server shutdown" or msg_recu == "You were kicked by server"): 
				# On doit fermer notre client, on affiche donc le msg et on break du while principal
				print(msg_recu)
				break
			if (msg_recu.split(' ')[0] == "#TrfD"): 
				# Si on s'apprête à recevoir des données fichier, on lance la fonction de save_file
				save_file(msg_recu.split(' ',1)[1], connexion_avec_serveur)
			else:
				print(msg_recu)
		except socket.timeout:	
			# Si on ne reçoit rien pendant un certain temps (0.05) on relance la boucle
			# On évite ainsi de rester bloqués dans le recv, ce qui nous emêcherait d'écrire plusieurs messages
			# avant une réception
			pass
		except ConnectionResetError :
			# Cette erreur est soulevée quand le serveur se déconnecte intempestivement
			break
		
	print("Fermeture de la connexion")
	connexion_avec_serveur.close()

if (__name__ == '__main__'): 
    main()
