import random
import math
from socket import *

# Use these named constants as you write your code
MAX_PRIME = 0b11111111  # The maximum value a prime number can have
MIN_PRIME = 0b11000001  # The minimum value a prime number can have
PUBLIC_EXPONENT = 17  # The default public exponent

LISTEN_ON_INTERFACE = 'localhost'
TCP_PORT = 42069


def main():
    """Provide the user with a variety of encryption-related actions"""
    # Get chosen operation from the user.
    while True:
        action = input(
            "Choose an option from the menu below:\n"
            "(1-CK) create_keys\n"
            "(2-CC) compute_checksum\n"
            "(3-VC) verify_checksum\n"
            "(4-EM) encrypt_message\n"
            "(5-DM) decrypt_message\n"
            "(6-BK) break_key\n"
            "(7-RM) receive an encrypted message through TCP\n"
            "(8-SM) send an encrypted message through TCP\n"
            "Please enter the option you want:\n"
        )
        # Execute the chosen operation.
        if action in ["1", "CK", "ck", "create_keys"]:
            create_keys_interactive()
        elif action in ["2", "CC", "cc", "compute_checksum"]:
            compute_checksum_interactive()
        elif action in ["3", "VC", "vc", "verify_checksum"]:
            verify_checksum_interactive()
        elif action in ["4", "EM", "em", "encrypt_message"]:
            encrypt_message_interactive()
        elif action in ["5", "DM", "dm", "decrypt_message"]:
            decrypt_message_interactive()
        elif action in ["6", "BK", "bk", "break_key"]:
            break_key_interactive()
        elif action in ["7", "RM", "rm", "receive_message"]:
            reveive_message_through_tcp()
        elif action in ["8", "SM", "Sm", "send_message"]:
            send_message_through_tcp()
        else:
            print("Unknown action: '{0}'".format(action))
            break


def reveive_message_through_tcp():
    print('tcp_receive (server): listen_port={0}'.format(LISTEN_ON_INTERFACE))
    address = (LISTEN_ON_INTERFACE, TCP_PORT)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.bind(address)
    sock.listen(1)
    comm, addr = sock.accept()

    (e,d,n) = create_keys()
    size = math.ceil((len(str(hex(n))) - 2) / 2)
    print(size)
    s = int.to_bytes(size, 2, 'big')
    comm.sendall(s)
    print(n)
    comm.sendall(int.to_bytes(n, size, 'big'))
    comm.sendall(b'\r\n')
    size = math.ceil((len(str(hex(e))) - 2) / 2)
    s = int.to_bytes(size, 2, 'big')
    comm.sendall(s)
    comm.sendall(int.to_bytes(e, size, 'big'))
    comm.sendall(b'\r\n')
    size = get_bytes(comm, 2)
    print(int.from_bytes(size, 'big'))
    size = int.from_bytes(size, 'big')
    get_bytes(comm, 2)
    mes = b""
    i = 0
    while i < size:
        decode_bytes = comm.recv(1)
        mes += decode_bytes
        i += 1
    print("message:" + str(mes))
    message = ""
    for i in range(0, len(mes), 4):
        enc_string = mes[i: i + 4]
        enc = int(enc_string, 16)
        dec = apply_key(get_private_key((e,d,n)), enc)
        if dec >= 0 and dec < 256:
            message += chr(dec)
        else:
            message += "_"
    print("Decrypted message:", message)
    comm.send(b'A')
    comm.close()


def send_message_through_tcp():
    print('tcp_receive (server): listen_port={0}'.format(LISTEN_ON_INTERFACE))
    address = (LISTEN_ON_INTERFACE, TCP_PORT)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(address)
    s = int.from_bytes(get_bytes(sock, 2), 'big')
    print(s)
    n = int.from_bytes(get_bytes(sock, s), 'big')
    print(n)
    print(get_bytes(sock, 2))
    s = int.from_bytes(get_bytes(sock, 2), 'big')
    print(s)
    e = int.from_bytes(get_bytes(sock, s), 'big')
    print(e)
    print(get_bytes(sock, 2))
    message = input("Please enter the message to be encrypted: ")
    encrypted = ""
    for c in message:
        encrypted += "{0:04x}".format(apply_key((e, n), ord(c)))
    s = encrypted.__len__()
    print(s)
    sock.sendall(int.to_bytes(s, 2, 'big'))
    sock.sendall(b'\r\n')
    print(encrypted)

    sock.sendall(encrypted.encode())
    sock.sendall(b'\r\n')
    if get_bytes(sock, 1) == b'A':
        sock.close()


def get_bytes(comm, x):
    ret = b''
    while x > 0:
        ret += comm.recv(1)
        x -= 1
    return ret


def get_public_key(key_pair):
    """
    Pulls the public key out of the tuple structure created by
    create_keys()

    :param key_pair: (e,d,n)
    :return: (e,n)
    """

    return (key_pair[0], key_pair[2])


def get_private_key(key_pair):
    """
    Pulls the private key out of the tuple structure created by
    create_keys()

    :param key_pair: (e,d,n)
    :return: (d,n)
    """

    return (key_pair[1], key_pair[2])


def create_keys_interactive():
    """
    Create new public keys

    :return: the private key (d, n) for use by other interactive methods
    """

    key_pair = create_keys()
    pub = get_public_key(key_pair)
    priv = get_private_key(key_pair)
    print("Public key: ")
    print(pub)
    print("Private key: ")
    print(priv)
    return priv


def compute_checksum_interactive():
    """
    Compute the checksum for a message, and encrypt it
    """

    priv = create_keys_interactive()
    message = input("Please enter the message to be checksummed: ")
    hash = compute_checksum(message)
    print("Hash:", "{0:04x}".format(hash))
    cipher = apply_key(priv, hash)
    print("Encrypted Hash:", "{0:04x}".format(cipher))


def verify_checksum_interactive():
    """
    Verify a message with its checksum, interactively
    """

    pub = enter_public_key_interactive()
    message = input("Please enter the message to be verified: ")
    recomputed_hash = compute_checksum(message)

    string_hash = input("Please enter the encrypted hash (in hexadecimal): ")
    encrypted_hash = int(string_hash, 16)
    decrypted_hash = apply_key(pub, encrypted_hash)
    print("Recomputed hash:", "{0:04x}".format(recomputed_hash))
    print("Decrypted hash: ", "{0:04x}".format(decrypted_hash))
    if recomputed_hash == decrypted_hash:
        print("Hashes match -- message is verified")
    else:
        print("Hashes do not match -- has tampering occured?")


def encrypt_message_interactive():
    """
    Encrypt a message
    """

    message = input("Please enter the message to be encrypted: ")
    pub = enter_public_key_interactive()
    encrypted = ""
    for c in message:
        encrypted += "{0:04x}".format(apply_key(pub, ord(c)))
    print("Encrypted message:", encrypted)


def decrypt_message_interactive(priv=None):
    """
    Decrypt a message
    """

    encrypted = input("Please enter the message to be decrypted: ")
    if priv is None:
        priv = enter_key_interactive("private")
    message = ""
    for i in range(0, len(encrypted), 4):
        enc_string = encrypted[i: i + 4]
        enc = int(enc_string, 16)
        dec = apply_key(priv, enc)
        if dec >= 0 and dec < 256:
            message += chr(dec)
        else:
            print("Warning: Could not decode encrypted entity: " + enc_string)
            print("         decrypted as: " + str(dec) + " which is out of range.")
            print("         inserting _ at position of this character")
            message += "_"
    print("Decrypted message:", message)


def break_key_interactive():
    """
    Break key, interactively
    """

    pub = enter_public_key_interactive()
    priv = break_key(pub)
    print("Private key:")
    print(priv)
    decrypt_message_interactive(priv)


def enter_public_key_interactive():
    """
    Prompt user to enter the public modulus.

    :return: the tuple (e,n)
    """

    print("(Using public exponent = " + str(PUBLIC_EXPONENT) + ")")
    string_modulus = input("Please enter the modulus (decimal): ")
    modulus = int(string_modulus)
    return (PUBLIC_EXPONENT, modulus)


def enter_key_interactive(key_type):
    """
    Prompt user to enter the exponent and modulus of a key

    :param key_type: either the string 'public' or 'private' -- used to prompt the user on how
                     this key is interpretted by the program.
    :return: the tuple (e,n)
    """
    string_exponent = input("Please enter the " + key_type + " exponent (decimal): ")
    exponent = int(string_exponent)
    string_modulus = input("Please enter the modulus (decimal): ")
    modulus = int(string_modulus)
    return (exponent, modulus)


def compute_checksum(string):
    """
    Compute simple hash

    Given a string, compute a simple hash as the sum of characters
    in the string.

    (If the sum goes over sixteen bits, the numbers should "wrap around"
    back into a sixteen bit number.  e.g. 0x3E6A7 should "wrap around" to
    0xE6A7)

    This checksum is similar to the internet checksum used in UDP and TCP
    packets, but it is a two's complement sum rather than a one's
    complement sum.

    :param str string: The string to hash
    :return: the checksum as an integer
    """

    total = 0
    for c in string:
        total += ord(c)
    total %= 0x8000  # Guarantees checksum is only 4 hex digits
    # How many bytes is that?
    #
    # Also guarantees that that the checksum will
    # always be less than the modulus.
    return total


# ---------------------------------------
# Do not modify code above this line
# ---------------------------------------

# Remeber to use the named constants as you write your code
# MAX_PRIME = 0b11111111  The maximum value a prime number can have
# MIN_PRIME = 0b11000001  The minimum value a prime number can have
# PUBLIC_EXPONENT = 17  The default public exponent

def generate_primes(l, h):
    assert l >= 1
    assert h > l
    primes = []
    for x in range(l, h + 1):
        prime = True
        for y in range(2, x):
            if x % y == 0:
                prime = False
                break
        if prime:
            primes.append(x)
    return primes


def isprime(num):
    if num > 1:
        # Iterate from 2 to n / 2
        for i in range(2, int(num / 2) + 1):
            # If num is divisible by any number between
            # 2 and n / 2, it is not prime
            if (num % i) == 0:
                return False

        else:
            return True
    else:
        return False


def gcd(p, q):
    while q != 0:
        p, q = q, p % q
    return p


def is_coprime(x, y):
    return gcd(x, y) == 1


def compute_e(co_prime):
    i = 2
    while i < co_prime:
        if is_coprime(i, co_prime):
            return i
        i += 1
    return -1


x, y = 0, 1


def gcdExtended(a, b):
    global x, y
    if (a == 0):
        x = 0
        y = 1
        return b
    gcd = gcdExtended(b % a, a)
    x1 = x
    y1 = y
    x = y1 - (b // a) * x1
    y = x1

    return gcd


def invmod(a, m):
    g = gcdExtended(a, m)
    return (x % m + m) % m


def create_keys():
    """
    Create the public and private keys.

    :return: the keys as a three-tuple: (e,d,n)
    """
    e = PUBLIC_EXPONENT
    primes = generate_primes(1, 255)
    p = primes[random.randint(0, len(primes))]
    q = primes[random.randint(0, len(primes))]
    n = p * q
    co = math.lcm(p - 1, q - 1)

    d = invmod(e, co)
    return (e, d, n)


def apply_key(key, m):
    exp = key[0]
    n = key[1]
    ret = pow(m, exp) % n

    """
    Apply the key, given as a tuple (e,n) or (d,n) to the message.
    

    This can be used both for encryption and decryption.

    :param tuple key: (e,n) or (d,n)
    :param int m: the message as a number 1 < m < n (roughly)
    :return: the message with the key applied. For example,
             if given the public key and a message, encrypts the message
             and returns the ciphertext.
    """

    return ret


def break_key(pub):
    e, n = pub
    n = n
    p_q_not_found = True
    p = 0
    q = 0
    i = 2
    while p_q_not_found:
        if n % i == 0:
            p = i
            q = n // p
            p_q_not_found = False
        i += 1
    co = math.lcm(p - 1, q - 1)
    d = invmod(e, co)
    return (d, n)


if __name__ == "__main__":
    main()
