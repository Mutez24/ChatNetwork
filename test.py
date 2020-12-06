from RoomClass import *

EXIT_CLIENT = "#Exit" #Command used by clients to leave

def Client_Exit (msg):
    print(msg)

def Client_Test (msg):
    print("Bonjour")
options = {
        "#Exit" : Client_Exit,
        "#Hello" : Client_Test
    }
def Check_client_functions(msg_recu):
    commande = msg_recu.split(' ')[0]
    options[commande]("yo")

def TestRoom():
    new_room=Room("elite","clem")
    print(new_room.clients)

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

def check_for_slashN(msg):
    msg_split = msg.split(' ')
    for i in range(len(msg_split)):
        if(msg_split[i]=="i"):
            msg_split[i] = "\n"
    return " ".join(msg_split)

if __name__ == '__main__':
    mot = "\n ijili \n slaut \nsalot"
    key = "dfhetede"
    print("mot : {}".format(mot))
    encrypt=PolyEncryption(mot,key)
    print("mot crypté : {}".format(encrypt))
    decrypt=PolyDecryption(encrypt,key)
    print("mot decrypté 1 : {}".format(decrypt))
    decrypt = check_for_slashN(decrypt)
    print("mot decrypté 2 : {}".format(decrypt))

    msg = "i salut toi"
    new_msg = check_for_slashN(msg)
    print("new msg : {}".format(new_msg))

