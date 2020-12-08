class Client:


    def __init__(self,username, IP, port, socket):
        self.username = username
        self.IP = IP
        self.port = port
        self.socket = socket
        self.room = "public"
        
    @staticmethod
    def Liste_Sockets (liste_client):
        result = []
        for element in liste_client:
            result.append(element.socket)
        return result

    @staticmethod
    def Liste_Sockets_Avec_Info(liste_sockets, liste_client):
        result = []
        for socket in liste_sockets:
            for element in liste_client:
                if (socket == element.socket):
                    result.append(element)
                    break
        return result

    def List_Rooms(self, Rooms):
        list_rooms=[]
        for room in Rooms:
            if self in room.clients:
                    list_rooms.append(room)
        return list_rooms

    #Méthode qui récupère une liste de noms de clients et qui renvoient la liste des clients associée
    @staticmethod
    def List_Clients(list_names, clients_connectes):
        list_clients=[]
        for client in clients_connectes:
            if client.username in list_names:
                list_clients.append(client)
        return list_clients

    @staticmethod
    def Check_Client_Connected(client_name, clients_connectes):
        exist=False
        for client in clients_connectes:
            if client_name==client.username:
                exist=True
                break
        return exist

    @staticmethod
    def Get_Client(client_name, clients_connectes):
        for client in clients_connectes:
            if client_name==client.username:
                return client

