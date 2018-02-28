import socket
import threading
import sys

#class client_handler(threading.Thread):


def connect_to_server(forward_port, forward_host):
	sock = socket.socket(socket.AF_INET, # Internet
	                    socket.SOCK_STREAM) # TCP
	
	forward_ip = socket.gethostbyname(forward_host.strip())
	print forward_host.strip()
	print forward_ip
	print forward_port
	sock.connect((forward_host.strip(), forward_port))
	#sock.send(forward_request)
	result = sock.recv(8192)
	strings = bytes(result)
	print strings
	# status, headers = strings.split('\r\n', 1)
	# print status

def nonconnect_to_server(forward_port, forward_host, forward_request):
	sock = socket.socket(socket.AF_INET, # Internet
	                    socket.SOCK_STREAM) # TCP
	
	forward_ip = socket.gethostbyname(forward_host.strip())
	print forward_host.strip()
	print forward_ip
	print forward_port
	sock.connect((forward_host.strip(), forward_port))
	sock.send(forward_request)
	result = sock.recv(8192)
	strings = bytes(result)

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
	
	http_version_idx = strings.find('HTTP/1.1')
	connection_idx = strings.find('keep-alive')
	print 'conn idx', connection_idx
	forward_request = strings[0:http_version_idx + 7] + '0' + strings[http_version_idx + 8:connection_idx] + 'close' + strings[connection_idx + 10:]
	print strings
	print '----------------------------------'
	# split the payload to HTTP initial line and header
	request, headers = strings.split('\r\n', 1)
	# modify the HTTP version
	forward_port = 80
	forward_host = ""
	list_headers = headers.split('\r\n')
	for header in list_headers:
		if header.lower().startswith('host:'):
			host_port = header.split(':')
			if(len(host_port) == 3):
				forward_port = int(host_port[2])
			forward_host = host_port[1]
	print forward_request
	print '-------------------------'

	request_word = request.split(' ')[0]
	if request_word == 'CONNECT':
		connect_to_server(forward_port, forward_host)
	else:
		nonconnect_to_server(forward_port, forward_host, forward_request)
	
	s.close()
