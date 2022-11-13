from socket import *
import os
import math

TFTP_PORT = 69
TFTP_HOST = 'localhost'
TFTP_BLOCK_SIZE = 512
MAX_UDP_PACKET_SIZE = 65536


# Helper functions
def get_file_block_count(filename):
    """
    Determines the number of TFTP blocks for the given file
    :param filename: THe name of the file
    :return: The number of TFTP blocks for the file or -1 if the file does not exist
    """
    try:
        # Use the OS call to get the file size
        #   This function throws an exception if the file doesn't exist
        file_size = os.stat(filename).st_size
        return math.ceil(file_size / TFTP_BLOCK_SIZE)
    except:
        return -1


def get_file_block(filename, block_number):
    """
    Get the file block data for the given file and block number
    :param filename: The name of the file to read
    :param block_number: The block number (1 based)
    :return: The data contents (as a bytes object) of the file block
    """
    file = open(filename, 'rb')
    block_byte_offset = (block_number - 1) * TFTP_BLOCK_SIZE
    file.seek(block_byte_offset)
    block_data = file.read(TFTP_BLOCK_SIZE)
    file.close()
    return block_data


def put_file_block(filename, block_data, block_number):
    """
    Writes a block of data to the given file
    :param filename: The name of the file to save the block to
    :param block_data: The bytes object containing the block data
    :param block_number: The block number (1 based)
    :return: Nothing
    """
    file = open(filename, 'wb')
    block_byte_offset = (block_number - 1) * TFTP_BLOCK_SIZE
    file.seek(block_byte_offset)
    file.write(block_data)
    file.close()


def socket_setup(host, port):
    """
    Sets up a UDP socket to listen on the TFTP port
    :return: The created socket
    """
    s = socket(AF_INET, SOCK_DGRAM)
    s.bind((host, port))
    return s


def get_op_code(message):
    return message[:2]


def get_filename(message):
    message = message[2:]
    index = message.index(b'\x00')
    return message[:index]


def get_mode(message):
    message = message[2:]
    index = message.index(b'\x00')
    message = message[index + 1:]
    index = message.index(b'\x00')
    return message[:index]


def get_block_num(message):
    return message[2:]


def get_error_message(message):
    return message[4:-1].decode('ASCII')


def send(data_socket, filename, address, block_count):
    block_data = get_file_block(filename, block_count)
    data_socket.sendto(b'\x00\x03' + block_count.to_bytes(2, "big") + block_data, address)


def start_server(host, port):
    rec_socket = socket_setup(host, port)
    print("connected")
    message = rec_socket.recvfrom(MAX_UDP_PACKET_SIZE)
    print(message)
    address = message[1]
    data = message[0]
    op_code = get_op_code(data)
    file = get_filename(data).decode('ASCII')
    mode = get_mode(data)
    if int.from_bytes(op_code, "big", signed=True) == 1:
        file_block_count = get_file_block_count(file)
        print(file)
        print(file_block_count)
        block_count = 1
        while block_count <= file_block_count:
            send(rec_socket, file, address, block_count)
            new_message = rec_socket.recvfrom(MAX_UDP_PACKET_SIZE)
            new_data = new_message[0]
            address = new_message[1]
            # chekc the ack
            block_count += 1
            new_op_code = get_op_code(new_data)
            if False and int.from_bytes(new_op_code, "big", signed=True) == 4:
                block_num = get_block_num(new_message)
                if block_num != block_count.to_bytes(2, 'big'):
                    block_count -= 1
                block_count += 1
            elif False and int.from_bytes(new_op_code, "big", signed=True) == 5:
                print(get_error_message(new_message))
                break
    else:
        print("not valid opcode")
    rec_socket.close()
    print("closing connection")


if __name__ == '__main__':
    start_server(TFTP_HOST, TFTP_PORT)
