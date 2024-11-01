"""
Client and server using classes
"""

import logging
import socket

import const_cs
from context import lab_logging

lab_logging.setup(stream_level=logging.INFO)  # init loging channels for the lab

# pylint: disable=logging-not-lazy, line-too-long

class Server:
    """ The server """
    _logger = logging.getLogger("vs2lab.lab1.clientserver.Server")
    _serving = True
    _phonebook = {
        "Alice": "1234",
        "Bob": "5678",
        "Charlie": "9012",
        "David": "3456",
        "Eve": "7890",
        "Frank": "1357",
        "Grace": "2468",
        "Heidi": "9753",
        "Ivan": "8642"
    }

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # prevents errors due to "addresses in use"
        self.sock.bind((const_cs.HOST, const_cs.PORT))
        self.sock.settimeout(3)  # time out in order not to block forever
        self._logger.info("Server bound to socket " + str(self.sock))

    def serve(self):
        """ Serve echo """
        self.sock.listen(1)
        while self._serving:  # as long as _serving (checked after connections or socket timeouts)
            try:
                # pylint: disable=unused-variable
                (connection, address) = self.sock.accept()  # returns new socket and address of client
                while True:  # forever
                    data = connection.recv(1024)  # receive data from client
                    if not data:
                        break  # stop if client stopped
                    data = data.decode('ascii')
                    if data == "getAll":
                        data = ""
                        for name, number in self._phonebook.items():
                            data += f"{name}: {number}\n"
                    elif data.startswith("get "):
                        name = data.split(" ")[1]
                        data = self._phonebook.get(name, "Not found")
                    else:
                        data += "*"
                    connection.send(data.encode('ascii'))
                connection.close()  # close the connection
            except socket.timeout:
                pass  # ignore timeouts
        self.sock.close()
        self._logger.info("Server down.")


class Client:
    """ The client """
    logger = logging.getLogger("vs2lab.a1_layers.clientserver.Client")

    def __init__(self):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((const_cs.HOST, const_cs.PORT))
        self.logger.info("Client connected to socket " + str(self.sock))

    def call(self, msg_in="Hello, world"):
        """ Call server """
        self.sock.send(msg_in.encode('ascii'))  # send encoded string as data
        data = self.sock.recv(1024)  # receive the response
        msg_out = data.decode('ascii')
        print(msg_out)  # print the result
        self.sock.close()  # close the connection
        self.logger.info("Client down.")
        return msg_out
    
    def get_phonebook(self):
        """ Get phonebook from server """
        self.sock.send("getAll".encode('ascii'))
        data = self.sock.recv(1024)
        phonebook = data.decode('ascii')
        print(f"Phonebook: \n{phonebook}")
        return phonebook
    
    def get_number(self, name):
        """ Get number from server """
        self.sock.send(f"get {name}".encode('ascii'))
        data = self.sock.recv(1024)
        number = data.decode('ascii')
        print(f"{name}: {number}")
        return number

    def close(self):
        """ Close socket """
        self.sock.close()
