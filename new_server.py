import asyncio
import yaml
import os
import yaml
import time

def update(file, data):
    with open(file, 'w') as f:
        f.write(data)


class Storage():
    def __init__(self):
        self.users_login = {}
        self.msgs = {}
        self.online = set()
        self.all = set()
        if os.path.exists("MSGS"):
            with open("MSGS") as f:
                self.msgs = yaml.load(f.read())
        else:
            with open("MSGS", 'w') as f:
                f.write(yaml.dump({}))
            self.msgs = {}

        if os.path.exists("USERS"):
            with open("USERS") as f:
                self.all = yaml.load(f.read())
        else:
            with open("USERS", 'w') as f:
                self.all = set()
                f.write(yaml.dump(self.all))
        if os.path.exists("PASSWORDS"):
            with open("PASSWORDS") as f:
                self.users_login = yaml.load(f.read())
        else:
            with open("PASSWORDS", 'w') as f:
                f.write(yaml.dump({}))
            self.users_login = {}

    def user_connection(self, loging):
        if list(loging.items())[0] in list(self.users_login.items()):
            self.online.add(list(loging.items())[0][0])
            return "logon successful\x0c"
        elif list(loging.keys())[0] in list(self.users_login.keys()):
            return "Password is wrong or user already existed.\x0c"
        else:
            self.all.add(list(loging.items())[0][0])
            update("USERS", yaml.dump(self.all))
            self.users_login.update(loging)
            update("PASSWORDS",yaml.dump(self.users_login))

            return "logon successful\x0c"
    def get_messages(self,name1, name2):
        try:
            data = self.msgs[(name1, name2)]
        except:
            return "No messages"
        string = ""
        for i in data:
            string+= i[0] + ": " + i[1] + '\n'
        return string[:-1]

"""sorry for this"""
"contact me with "

class EchoServerClientProtocol(asyncio.Protocol):
    storage = Storage()
    all_users = {}
    def __init__(self):
        super().__init__()
        self.login = None

    def __del__(self):
        self.storage.online.discard(self.login)
        print(self.login, ' disconnected')
    def connection_made(self, transport):
        self.transport = transport

    @classmethod
    def received(cls):
        for i in cls.storage.online:
            try:

                temp = cls.storage.all.copy()
                temp.discard(i)
                data = ("people " + yaml.dump(temp) + '\x0c').encode()
                print(cls.all_users[i])
                print(cls.all_users)
                cls.all_users[i].write(data)
            except KeyError as w:
                print(w)


    def conn(self):
        temp = self.storage.all.copy()
        temp.discard(self.login)
        self.transport.write(("people "+ yaml.dump(temp) + '\x0c').encode())
    def data_received(self, data):
        data = data.decode()
        if data.startswith("login "):
            logon = yaml.load(data[6:-1])
            self.login = list(logon.keys())[0]

            self.all_users[self.login] = self.transport
            print(self.login + " connected")
            self.transport.write(self.storage.user_connection(logon).encode())
            self.storage.online.add(self.login)
            self.conn()
            self.received()
        elif data.startswith("msg"):
            l = yaml.load(data[4:-1])

            """l[0] - who will get msg 
            l[1] - what message he gets"""
            self.storage.msgs.setdefault((self.login,l[0]), [])
            self.storage.msgs[(self.login, l[0])].append(("You", l[1]))
            self.storage.msgs.setdefault((l[0],self.login), [])
            self.storage.msgs[(l[0], self.login)].append((self.login, l[1]))
            update("MSGS", yaml.dump(self.storage.msgs))
            '''{[1,2]:[[1, hello], [2, well hi!!]]}'''
            #self.all_users[l[0]] = (("msg "+ self.login + "\x0c").encode())

            """send notice to user that he has new message"""
            """wrong method of saving msgs!!! fix it !!! May be dict of pairs like (sender, reciever) = [(who, message), (who, message)]"""
        elif data.startswith("dialog"):
            data_ = data[7:-1]

            msgs = self.storage.get_messages(self.login, data_)

            #msgs = "No messages"
            self.transport.write(("msgs "+ msgs + "\x0c").encode())
        elif data.startswith("online"):
            string = 'online:'
            for i in list(self.storage.online):
                string += " " + i
            string+='\x0c'
            self.transport.write(string.encode())
        elif data.startswith("offline"):
            string = 'offline:'
            for i in list(self.storage.all - self.storage.online):
                string += " " + i
            string+='\x0c'
            self.transport.write(string.encode())





loop = asyncio.get_event_loop()
coro = loop.create_server(
    EchoServerClientProtocol,
    '127.0.0.1', 4444
)
server = loop.run_until_complete(coro)
#try:
loop.run_forever()
#except KeyboardInterrupt:
 #   pass

server.close()
loop.run_until_complete(server.wait_closed())
loop.close()