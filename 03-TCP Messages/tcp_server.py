import sqlite3
from socket import *
import struct
import time
import sys

# Port number definitions
# (May have to be adjusted if they collide with ports in use by other programs/services.)
TCP_PORT = 23724

# Address to listen on when acting as server.
# The address '' means accept any connection for our 'receive' port from any network interface
# on this system (including 'localhost' loopback connection).
LISTEN_ON_INTERFACE = 'localhost'


def tcp_receive(listen_on, listen_port):
    """
    - Listen for a TCP connection on a designated "listening" port
    - Accept the connection, creating a connection socket
    - Print the address and port of the sender
    - Repeat until a zero-length message is received:
      - Receive a message, saving it to a text-file (1.txt for first file, 2.txt for second file, etc.)
      - Send a single-character response 'A' to indicate that the upload was accepted.
    - Send a 'Q' to indicate a zero-length message was received.
    - Close data connection.

    :param int listen_port: Port number on the server to listen on
    """

    print('tcp_receive (server): listen_port={0}'.format(listen_port))
    address = (listen_on, listen_port)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(address)
    sock.listen(1)
    comm, addr = sock.accept()
    print("connected")
    f = open("output.txt", "a")
    while True:
        ret = ""

        lines = int.from_bytes(get_bytes(comm, 4), "big", signed=True)
        if lines == 0:
            print("no more lines sent, disconnecting")
            comm.send('Q'.encode())
            break
        print("printing " + str(lines) + " lines")
        comm.send('A'.encode())
        while lines > 0:
            ch = chr(int.from_bytes(comm.recv(1), "big", signed=True))
            ret += ch
            if ch == '\n':
                lines -= 1
        f.write(ret)
    f.close()


def get_bytes(comm, x):
    ret = b''
    while x > 0:
        ret += comm.recv(1)
        x -= 1
    return ret


if __name__ == '__main__':
    tcp_receive(LISTEN_ON_INTERFACE, TCP_PORT)
