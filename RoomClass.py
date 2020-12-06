class Room:

    def __init__(self,name, admin, clients=[]):
        self.name = name
        self.admin = admin
        self.clients = clients
        self.clients.append(admin) 