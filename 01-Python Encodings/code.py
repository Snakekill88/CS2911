#
# Write a function that takes an int and returns a string
# of the binary representation as given by the bin() function
# do not use bin()
#


def int_bits(x):
    ret = ""
    if x < 0:
        ret += "-"
        x = -x
    ret += "0b"
    temp = ""
    while x // 2 > 0:
        y = x % 2
        temp = temp + str(y)
        x = x // 2
    if x == 1:
        temp += "1"
    else:
        temp += "0"
    temp = temp[::-1]
    ret += temp
    return ret


#
# Write a function that takes an ascii string and returns a string of
# the underyling binary representation stored by the computer
# as byte length chunks
# ex: 'Hi' -> '01101000 01101001'
#
def str_bits(x):
    string = list(x)
    ret = ""
    for ch in string:
        temp = int_bits_asci(ord(ch))
        ret += str(temp) + " "
    return ret[0:-1]


# takes in an int and turns it to binary like bin but omits the 0b and puts in byte form
def int_bits_asci(x):
    ret = ""
    if x < 0:
        ret += "-"
        x = -x
    temp = ""
    while x // 2 > 0:
        y = x % 2
        temp = temp + str(y)
        x = x // 2
    if x == 1:
        temp += "1"
    else:
        temp += "0"
    while len(temp) < 8:
        temp += "0"
    temp = temp[::-1]
    ret += temp
    return ret


#
# Write a function that takes a bytes object and returns a string of
# the underyling binary representation stored by the computer
# as byte length chunks
# ex: b'Hi' -> '01001000 01101001'
# ex: b'\x48\x69' -> '01001000 01101001'
#
def bytes_bits(x):
    ret = ''
    t = list(x)
    for ch in t:
        temp = int_bits_asci(ch)
        ret += temp + " "
    return ret[:-1]


#
# Write a function that takes an int and returns a string
# of the hex representation
#
def int_hex(x):
    return hex(x)


#
# Write a function that takes an ascii string and returns a string of
# the underyling hex representation stored by the computer
# as byte length chunks
# ex: 'Hi' -> '0x4869'
#
def str_hex(x):
    string = list(x)
    ret = "0x"
    for ch in string:
        temp = int_hex(ord(ch))
        ret += str(temp)[2:]
    return ret


#
# Write a function that takes a bytes object and returns a string of
# the underyling hex representation stored by the computer
# ex: b'Hi' -> '0x4869'
# ex: b'\x48\x69' -> '0x4869'
#
def bytes_hex(x):
    t = list(x)
    ret = "0x"
    for byte in t:
        t = str(hex(byte))
        ret += t[2] + t[3]
    return ret
    pass


#
# Take a binary string -- '0b...' -- and convert to an int
#
def bin_int(x):
    ret = 0
    temp = list(x)
    i = len(temp) - 1
    while i > 0:
        if temp[i] == "1":
            ret += 2 ** ((len(temp) - 1) - i)
        i -= 1
    if temp[0] == "-":
        ret = -ret
    return ret


#
# Take a bytes object -- b'...' and convert to an int
# Make sure you use big endian and signed conversion
#
def bytes_int(x):
    return int.from_bytes(x, "big", signed=True)


#
# Take an int and convert to bytes object
# Make sure you use big endian and signed conversion
#
def int_bytes(x):
    neg = False
    if x < 0:
        x = -x
        neg = True
    len = 0
    temp = True
    t = x
    while temp:
        if t / 256 < 1:
            temp = False
        len += 1
        t = t/256
    if neg:
        x = -x
    return x.to_bytes(len, byteorder='big', signed=True)


#
# Take an int and convert to bytes object
#
def str_bytes(x):
    return bytes(x, 'utf-8')


#
# Take an int and convert to bytes object
#
def bytes_str(x):
    return x.decode('utf-8')
