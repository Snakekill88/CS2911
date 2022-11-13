from socket import *
import struct
import time
import sys

# Port number definitions
# (May have to be adjusted if they collide with ports in use by other programs/services.)
TCP_PORT = 12100

# Address of the 'other' ('server') host that should be connected to for 'send' operations.
# When connecting on one system, use 'localhost'
# When 'sending' to another system, use its IP address (or DNS name if it has one)
# OTHER_HOST = '155.92.x.x'
OTHER_HOST = "localhost"


def tcp_send(server_host, server_port):
    """
    - Send multiple messages over a TCP connection to a designated host/port
    - Receive a one-character response from the 'server'
    - Print the received response
    - Close the socket

    :param str server_host: name of the server host machine
    :param int server_port: port number on server to send to
    """
    print('tcp_send: dst_host="{0}", dst_port={1}'.format(server_host, server_port))
    tcp_socket = socket(AF_INET, SOCK_STREAM)
    tcp_socket.connect((server_host, server_port))

    num_lines = int(input("Enter the number of lines you want to send (0 to exit):"))

    while num_lines != 0:
        print("Now enter all the lines of your message")
        # This client code does not completely conform to the specification.
        #
        # In it, I only pack one byte of the range, limiting the number of lines this
        # client can send.
        #
        # While writing tcp_receive, you will need to use a different approach to unpack to meet the specification.
        #
        # Feel free to upgrade this code to handle a higher number of lines, too.
        lines_bytes = num_lines.to_bytes(4, "big")
        for i in range(4):
            tcp_socket.sendall(lines_bytes[i: i + 1])
            time.sleep(0.25)  # Just to mess with your servers. :-)

        # Enter the lines of the message. Each line will be sent as it is entered.
        for line_num in range(0, num_lines):
            line = input("")
            tcp_socket.sendall(line.encode() + b"\n")

        print("Done sending. Awaiting reply.")
        response = tcp_socket.recv(1)
        if response == b"A":  # Note: == in Python is like .equals in Java
            print("File accepted.")
        else:
            print("Unexpected response:", response)

        num_lines = int(
            input("Enter the number of lines you want to send (0 to exit):")
        )

    tcp_socket.sendall(b"\x00\x00")
    time.sleep(
        1
    )  # Just to mess with your servers. :-)  Your code should work with this line here.
    tcp_socket.sendall(b"\x00\x00")
    response = tcp_socket.recv(1)
    if response == b"Q":  # Reminder: == in Python is like .equals in Java
        print("Server closing connection, as expected.")
    else:
        print("Unexpected response:", response)

    tcp_socket.close()


if __name__ == "__main__":
    tcp_send(OTHER_HOST, TCP_PORT)
