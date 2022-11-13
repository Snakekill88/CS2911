from socket import *
# import the "regular expressions" module
import re


def get_http_resource(url, file_name):
    """
    Get an HTTP resource from a server
           Parse the URL and call function to actually make the request.

    :param url: full URL of the resource to get
    :param file_name: name of file in which to store the retrieved resource

    (do not modify this function)
    """

    # Parse the URL into its component parts using a regular expression.
    url_match = re.search('http://([^/:]*)(:\d*)?(/.*)', url)
    url_match_groups = url_match.groups() if url_match else []
    #    print 'url_match_groups=',url_match_groups
    if len(url_match_groups) == 3:
        host_name = url_match_groups[0]
        host_port = int(url_match_groups[1][1:]) if url_match_groups[1] else 80
        host_resource = url_match_groups[2]
        print('host name = {0}, port = {1}, resource = {2}'.format(host_name, host_port, host_resource))
        status_string = do_http_exchange(host_name.encode(), host_port, host_resource.encode(), file_name)
        print('get_http_resource: URL="{0}", status="{1}"'.format(url, status_string))
    else:
        print('get_http_resource: URL parse failed, request not sent')


# Write Helper functions here

def read_until(socket, delimiter):
    l = len(delimiter)
    data = socket.recv(l)
    while data[-l:] != delimiter:
        data += socket.recv(1)
    return data.decode('ascii')


def read_until_utf(socket, delimiter):
    l = len(delimiter)
    data = socket.recv(l)
    while data[-l:] != delimiter:
        data += socket.recv(1)
    return data.decode('utf8')


# Write Helper functions here

def do_http_exchange(host, port, resource, file_name):
    """
    Get an HTTP resource from a server

    :param bytes host: the ASCII domain name or IP address of the server machine (i.e., host) to connect to
    :param int port: port number to connect to on server host
    :param bytes resource: the ASCII path/name of resource to get. This is everything in the URL after the domain name,
           including the first /.
    :param file_name: string (str) containing name of file in which to store the retrieved resource
    :return: the status code
    :rtype: int
    """
    address = (host, port)
    sock = socket(AF_INET, SOCK_STREAM)
    sock.connect(address)

    f = open(file_name, "wb")
    bytes = b'GET ' + resource + b' HTTP/1.1\r\nHost: ' + host + b'\r\n\r\n'
    sock.sendall(bytes)
    # Send the request to the host

    # Receive the response for the host
    response_line = read_until(sock, b'\r\n').split(' ')
    ret = response_line[1]
    if ret == "200":
        headers = read_until(sock, b'\r\n\r\n').split('\r\n')
        for s in headers:
            print(s)
            if s.__contains__("Content-Length:"):
                l = int(s[15:])
                s = sock.recv(l)
                f.write(s)
                f.close()
                break
            elif s == "Transfer-Encoding: chunked":
                n = -1
                while n != 0:
                    n = int(read_until_utf(sock, b'\r\n'), 16)
                    temp = b''
                    i = 0
                    while i < n:
                        temp += sock.recv(1)
                        i+=1

                    sock.recv(2)
                    f.write(temp)
                f.close()
                break

    return ret


if __name__ == '__main__':
    """
    Tests the client on a variety of resources
    """

    # These resource request should result in "Content-Length" data transfer
    get_http_resource('http://www.httpvshttps.com/check.png', 'check.png')

    # this resource request should result in "chunked" data transfer
    get_http_resource('http://www.httpvshttps.com/', 'index.html')

    # If you find fun examples of chunked or Content-Length pages, please share them with us!
