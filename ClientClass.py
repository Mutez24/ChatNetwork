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

