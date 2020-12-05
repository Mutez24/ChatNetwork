# Import sockets libraries
import socket

def PolyEncryption(to_encrypt, key):
    encrypted = ""
    size=len(key)
    for i in range (len(to_encrypt)):
        new_ascii= ord(to_encrypt[i])+ord(key[i%size])
        if(new_ascii>127):
            new_ascii=32 + new_ascii%127
        encrypted+=(chr(new_ascii))
    return encrypted
        
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

def Send_Message(msg_encode, key, socket):
    msg = msg_encode.decode()
    #Si le message est trop long on retourne un message d'erreur
    if (len(msg)>280):
        print("Your message is too long to be sent (over 280 character)")
    #Sinon on l'envoie
    else:
        msg_crypted = PolyEncryption(msg, key)
        #Pour montrer que ca fonctionne bien
        #print("message crypté envoyé :{}".format(msg_crypted))
        msg_to_send = msg_crypted.encode()
        socket.send(msg_to_send)
    

def Receive_Message(key, socket):
    msg = socket.recv(1024)
    msg = msg.decode()
    #Pour montrer que ca fonctionne bien
    #print("message crypté recu : {}".format(msg))
    msg_decrypted = PolyDecryption(msg, key)
    final_msg = msg_decrypted.encode()
    return final_msg

if __name__ == '__main__':
    encrypt=PolyEncryption("Clement","cle")
    print(encrypt)
    decrypt=PolyDecryption(encrypt,"cle")
    print(decrypt)