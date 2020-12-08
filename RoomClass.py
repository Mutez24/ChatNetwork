class Room:

    def __init__(self,name, admin, clients=[]):
        self.name = name
        self.admin = admin
        self.clients = clients
        self.clients.append(admin) 

    #méthode qui vérifie si le nom d'une chat room existe ou non.
    #Si le nom room_name n'est pas déjà utilisé, alors la fonction renvoie False.
    #Sinon, elle renvoie True.
    @staticmethod
    def Check_Name(room_name, Rooms):
        exist=False
        for room in Rooms:
            if room_name==room.name:
                exist=True
                break
        return exist

    #Méthode qui vérifie si le nom d'une chat room n'est pas le même que le nom d'un client.
    #Si le nom room_name est déjà utilisé par un utilisateur, alors la fonction renvoie False.
    #Sinon, elle renvoie True.
    #Cette fonction est nécessaire car si on autorise une room à avoir le même nom qu'un username,
    #alors on s'expose à des erreurs lorsque l'on veut communiquer en privée avec cette personne qui 
    #a le même nom que la room. En effet, étant donné que les destinataires des messages sont choisis
    #grâce à l'attribut room de Client, alors le programme ne fera pas la distinction entre le client
    #et la chatroom lors de l'envoi du message ce qui conduira à des erreurs.
    @staticmethod
    def Check_Name_With_Clients(room_name, clients_connectes):
        valid=True
        for client in clients_connectes:
            if client.username==room_name:
                valid=False
                break
        return valid

    #Méthode complémentaire à Check_Name et Check_Name_With_Clients qui cette fois-ci renvoie 
    # la room à partir du room name et non un booléen.
    @staticmethod
    def Get_Room(room_name, Rooms):
        for room in Rooms:
            if room_name==room.name:
                return room

    #Méthode qui vérifie si client appartient bien à une room à partir de son username.
    #S'il y appartient, alors on renvoie True.
    #Sinon, elle renvoie True.
    def Check_Client(self, client_name):
        exist=False
        for client in self.clients:
            if client.username==client_name:
                exist=True
                break
        return exist 

    #Méthode complémentaire à Check_Client qui cette fois-ci renvoie le client à partir du username
    #et non un booléen.
    def Get_Client(self, client_name):
        for client in self.clients:
            if client.username==client_name:
                return client

   
