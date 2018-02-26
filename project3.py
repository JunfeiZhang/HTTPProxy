import socket
import threading
import sys

#class client_handler(threading.Thread):


def connect(forward_port, forward_host, forward_request):
	

if __name__ == '__main__':
	tcp_port = sys.argv[1]
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	server_ip = socket.gethostbyname("localhost")
	s.bind((server_ip, int(tcp_port)))
	s.listen(1)
	client_conn, client_addr = s.accept()
	# recevie the tcp payload
	data = client_conn.recv(8192)
	strings = bytes(data)
	# split the payload to HTTP initial line and header
	request, headers = strings.split('\r\n', 1)
	# modify the HTTP version
	list_request = list(request)
	list_request[len(list_request) - 1] = '0'
	forward_request = "".join(list_request).join('\r\n')
	forward_port = 80
	forward_host = ""
	list_headers = headers.split('\r\n')
	for header in list_headers:
		if header.startswith('Host:'):
			host_port = header.split(':')
			if(len(host_port) == 3):
				forward_port = host_port[2]
			forward_host = host_port[1]
			forward_request += header + '\r\n'
		elif header.startswith('Connection:'):
			connection = header
			forward_request += 'Connection: close\r\n' 
		else:
			forward_request += header + '\r\n'
	print forward_request

	connect(forward_port, forward_host, forward_request)
	
	s.close()
