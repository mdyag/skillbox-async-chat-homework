#
# Серверное приложение для соединений
#
import asyncio
from asyncio import transports


class ServerProtocol(asyncio.Protocol):
    login: str = None
    server: 'Server'
    transport: transports.Transport
    logins: list = [] #
    history: list = []  # --

    def __init__(self, server: 'Server'):
        self.server = server

    def data_received(self, data: bytes):

        print(data)
        decoded = data.decode()

        if self.login is not None:
            self.send_message(decoded)
            self.history.append(self.login + ":" + decoded)  # --
            while len(self.history) > 11:  # --
                self.history.pop(0)  # --
        else:
            if decoded.startswith("login:"):
                self.login = decoded.replace("login:", "").replace("\r\n", "")
                if self.logins.count(self.login) > 0: #
                    print("Такой пользователь уже есть") #
                    self.transport.write( #
                    f"Логин {self.login} занят, попробуйте другой\n".encode() #
                    )  #
                    import time #
                    time.sleep(3) #
                    self.connection_lost(excemption) #
                else:#
                    self.logins.append(self.login) #
                    self.transport.write( #
                    f"Привет, {self.login}!\n".encode() #
                    ) #
                    self.send_history(self.history) #--
            else:
                self.transport.write("Неправильный логин\n".encode())

    def connection_made(self, transport: transports.Transport):
        self.server.clients.append(self)
        self.transport = transport
        print("Пришел новый клиент")

    def connection_lost(self, excemption): #
        self.logins.remove(self.login)  #
        self.server.clients.remove(self)
        print("Клиент вышел")

    def send_message(self, content: str):
        message = f"{self.login}: {content}\n"

        for user in self.server.clients:
            user.transport.write(message.encode())

    def send_history(self, history): #--

        for msg in self.history: #--
            self.transport.write(msg.encode()) #--

class Server:
    clients: list

    def __init__(self):
        self.clients = []

    def build_protocol(self):
        return ServerProtocol(self)

    async def start(self):
        loop = asyncio.get_running_loop()

        coroutine = await loop.create_server(
            self.build_protocol,
            '127.0.0.1',
            8888
        )

        print("Сервер запущен ...")

        await coroutine.serve_forever()


process = Server()

try:
    asyncio.run(process.start())
except KeyboardInterrupt:
    print("Сервер остановлен вручную")
