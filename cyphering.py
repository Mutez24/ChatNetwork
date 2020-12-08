# Import sockets libraries
import socket


#* Fonction qui permet de crypter un string à partir d'une clé
#* Prend en paramètre le string à crypter et la clé
#* Retourne le string crypté

def PolyEncryption(to_encrypt, key):
    encrypted = ""
    size=len(key)
    for i in range (len(to_encrypt)):
        new_ascii= ord(to_encrypt[i])+ord(key[i%size])
        if(new_ascii>127):
            new_ascii=32 + new_ascii%127
        encrypted+=(chr(new_ascii))
    return encrypted
        

#* Fonction qui permet de décrypter un string à partir d'une clé
#* Prend en paramètre le string à décrypter et la clé
#* Retourne le string décrypté

def PolyDecryption(to_decrypt, key):
    decrypted = ""
    size=len(key)
    for i in range (len(to_decrypt)):
        old_ascii= ord(to_decrypt[i])-ord(key[i%size])
        if(old_ascii<32):
            diff=32-old_ascii
            old_ascii=127-diff
        decrypted+=(chr(old_ascii))
    return decrypted     


#* Fonction qui permet de gérer les envoie de messages (remplace la fonction socket.send de la librairie socket)
#* Permet de faire l'encryption du message et la vérification de taille du message
#* Prend en paramètre le string à envoyer, la clé de cryptage, la socket à qui on envoie le message
#* et le paramètre force qui permet de forcer l'envoie d'un message si celui-ci fait plus de 280 caractères

def Send_Message(msg_encode, key, socket, force= False):
    #Si le message est trop long on retourne un message d'erreur
    if (len(msg_encode)>280 and not force):
        print("Your message is too long to be sent (over 280 character)")
    #Sinon on l'envoie
    else:
        # On split le message pour gérer les "\n" car il ne fonctionne pas à l'encryption
        msg_a_crypter_split = msg_encode.split("\n")
        for i in range(len(msg_a_crypter_split)):
            msg_a_crypter_split[i]=PolyEncryption(msg_a_crypter_split[i],key)
        msg_crypter_join = "\n".join(msg_a_crypter_split)
        # Une fois le message crypter, on l'encode pour l'envoyer avec la fonction .send
        msg_to_send = msg_crypter_join.encode()
        socket.send(msg_to_send)
    

#* Fonction qui permet de gérer les messages recu (remplace la fonction socket.recv de la librairie socket)
#* Permet de faire la decrytption du message envoyé
#* Prend en paramètre la clé de cryptage et la socket qui recoit le message
#* Retourne le message recu (en byte)

def Receive_Message(key, socket):
    # On recoit le message
    msg = socket.recv(2000)
    msg = msg.decode()
    # On split le message pour gérer les "\n" car il ne fonctionne pas à l'encryption
    msg_to_decrypt_split = msg.split("\n")
    for i in range(len(msg_to_decrypt_split)):
        msg_to_decrypt_split[i]=PolyDecryption(msg_to_decrypt_split[i],key)
    msg_decrypter_join = "\n".join(msg_to_decrypt_split)
    # On encode le message avant de le return pour repecter le format
    final_msg = msg_decrypter_join.encode()
    return final_msg

if __name__ == '__main__':
    encrypt=PolyEncryption("Clement","cle")
    print(encrypt)
    decrypt=PolyDecryption(encrypt,"cle")
    print(decrypt)