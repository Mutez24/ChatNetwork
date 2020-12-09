class Client:

    '''
    #* Classe permettant de définir un client

    #? username : username du client
    #? IP : IP du client
    #? port : port de l'IP du client
    #? socket : socket utilisée par le client
    '''
    def __init__(self,username, IP, port, socket):
        self.username = username
        self.IP = IP
        self.port = port
        self.socket = socket
        self.room = "public"


    '''
    #* Fonction static afin de pouvoir l'utiliser sans avoir à définir de Client
    #* Permet, à partir d'une liste de clients, d'obtenir la liste des sockets qu'ils utilisent

    #? liste_client : liste de clients dont on veut les sockets
    '''
    @staticmethod
    def Liste_Sockets (liste_client):
        result = []
        for element in liste_client:
            result.append(element.socket)
        return result


    '''
    #* Fonction static afin de pouvoir l'utiliser sans avoir à définir de Client
    #* Permet à partir de la liste de tous les clients, de retrouver ceux ayant une socket correspondante aux éléments
    #* d'une liste de sockets

    #? liste_client : liste de tous les clients
    #? liste_sockets : liste des sockets dont on veut retrouver les clients
    '''
    @staticmethod
    def Liste_Sockets_Avec_Info(liste_sockets, liste_client):
        result = []
        for socket in liste_sockets:
            for element in liste_client:
                if (socket == element.socket):
                    result.append(element)
                    break
        return result

    '''
    #* Méthode qui récupère une liste de rooms auxquelles le client appartient

    #? self : le client en question 
    #? Rooms : liste des rooms existantes
    '''
    def List_Rooms(self, Rooms):
        list_rooms=[]
        for room in Rooms:
            if self in room.clients:
                    list_rooms.append(room)
        return list_rooms


    '''
    #* Méthode qui récupère une liste de noms de clients et qui renvoient la liste des clients associée

    #? list_names : liste de noms 
    #? clients_connectes : liste des clients connectés
    '''
    @staticmethod
    def List_Clients(list_names, clients_connectes):
        list_clients=[]
        for client in clients_connectes:
            if client.username in list_names:
                list_clients.append(client)
        return list_clients


    '''
    #* Méthode qui check si le client rentré en paramètre est bien connecté 

    #? client_name : nom d'un client
    #? clients_connectes : liste des clients connectés
    '''
    @staticmethod
    def Check_Client_Connected(client_name, clients_connectes):
        exist=False
        for client in clients_connectes:
            if client_name==client.username:
                exist=True
                break
        return exist


    '''
    #* Méthode qui récupère toutes les informations d'un client à partir de son nom

    #? client_name : nom d'un client
    #? clients_connectes : liste des clients connectés
    '''
    @staticmethod
    def Get_Client(client_name, clients_connectes):
        for client in clients_connectes:
            if client_name==client.username:
                return client

