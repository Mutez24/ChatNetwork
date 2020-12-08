import os
'''
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
    # mot = "\n ijili \n slaut \nsalot"
    # key = "dfhetede"
    # print("mot : {}".format(mot))
    # encrypt=PolyEncryption(mot,key)
    # print("mot crypté : {}".format(encrypt))
    # decrypt=PolyDecryption(encrypt,key)
    # print("mot decrypté 1 : {}".format(decrypt))
    # decrypt = check_for_slashN(decrypt)
    # print("mot decrypté 2 : {}".format(decrypt))

    # msg = "i salut toi"
    # new_msg = check_for_slashN(msg)
    # print("new msg : {}".format(new_msg))

    # msg2 = "salut \n toi \n"
    # print("msg2 :{}".format(msg2))
    # msg2_split = msg2.split("\n")
    # for i in range(len(msg2_split)):
    #     print("element {} : .{}.".format(i, msg2_split[i]))
    # print(msg2_split[i] == "")

    # msg2_reformer = "\n".join(msg2_split)
    # #if (msg2_split[len(msg2_split)-1] ==""):
    # #   msg2_reformer = msg2_reformer + "\n"
    # print("msg2 reformer :{}".format(msg2_reformer))
    
    cle = "salut"
    msg_a_crypter = "salut \n toi"
    print("msg : {}".format(msg_a_crypter))
    msg_a_crypter_split = msg_a_crypter.split("\n")
    for i in range(len(msg_a_crypter_split)):
        msg_a_crypter_split[i]=PolyEncryption(msg_a_crypter_split[i],cle)
    msg_a_crypter_join = "\n".join(msg_a_crypter_split)
    print("message crypé : {}".format(msg_a_crypter_join))

    msg_to_decrypt_split = msg_a_crypter_join.split("\n")
    for i in range(len(msg_to_decrypt_split)):
        msg_to_decrypt_split[i]=PolyDecryption(msg_to_decrypt_split[i],cle)
    msg_decrypter_join = "\n".join(msg_to_decrypt_split)
    print("message decrypté : {}".format(msg_decrypter_join))

'''


