import socket
import threading
import sys

#class client_handler(threading.Thread):

if __name__ == '__main__':
	tcp_port = sys.argv[1]
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_ip = socket.gethostbyname("localhost")
	s.bind((server_ip, int(tcp_port)))
	s.listen(1)
	client_conn, client_addr = s.accept()
	# recevie the tcp payload
	data = client_conn.recv(8192)
	# split the payload to HTTP initial line and header
	request, header = data.split('\r\n', 1)
	# modify the HTTP version
	list_request = list(request)
	list_request[len(list_request) - 1] = '0'
	forward_request = "".join(list_request)

	list_headers = header.split('\r\n')
	host_port = list_headers[0]
	
	



