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
	return_message = ""
	try:
		sock.connect((forward_host.strip(), forward_port))
		return_message = "HTTP/1.0 200 OK\r\n\r\n"
		client_socket.send(str.encode(return_message))
	except Exception:
		return_message = "HTTP/1.0 502 Bad Gateway\r\n\r\n"
		client_socket.send(str.encode(return_message))

	#sock.send(forward_request)
	#result = sock.recv(8192)
	#strings = bytes(result)
	#print strings
	# status, headers = strings.split('\r\n', 1)
	# print status

def nonconnect_to_server(forward_port, forward_host, forward_request, client_socket):
	sock = socket.socket(socket.AF_INET, # Internet
	                    socket.SOCK_STREAM) # TCP
	
	forward_ip = socket.gethostbyname(forward_host.strip())
	print forward_host.strip()
	print forward_ip
	print forward_port
	sock.connect((forward_host.strip(), forward_port))
	sock.send(forward_request)

	max_bytes = 1024
	result = sock.recv(max_bytes)
	strings = bytes(result)
	print "-------------------------------------------------"
	print strings

	content_len_index = strings.find("Content-Length")
	content_length = 0
	if (content_len_index != -1):
		content_len_end_index = strings.find('\r\n', content_len_index)
		content_len_start_index = strings.find(':', content_len_index)
		content_length = int(strings[content_len_start_index + 1 : content_len_end_index])
		print "-------------------------------------------------"
		print content_length

	while (content_length > 0):
		client_socket.send(result)
		result = sock.recv(max_bytes)
		content_length -= max_bytes

	if (not strings == None):
		client_socket.send(result)



if __name__ == '__main__':
	tcp_port = sys.argv[1]
	
	server_ip = socket.gethostbyname("localhost")
	while 1:
		client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		client_socket.bind((server_ip, int(tcp_port)))
		client_socket.listen(1)
		client_conn, client_addr = client_socket.accept()
		
		# recevie the tcp payload
		data = client_conn.recv(8192)

		strings = bytes(data)
		
		http_version_idx = strings.find('HTTP/1.1')
		connection_idx = strings.find('keep-alive')
		print 'conn idx', connection_idx
		header_end_idx = strings.find('\r\n\r\n')
		forward_request = strings[0:http_version_idx + 7] + '0' + strings[http_version_idx + 8:connection_idx] + 'close' + strings[connection_idx + 10:]
		forward_request_header = strings[0:http_version_idx + 7] + '0' + strings[http_version_idx + 8:connection_idx] + 'close' + strings[connection_idx + 10: connection_idx]
		print "**************"
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
			nonconnect_to_server(forward_port, forward_host, forward_request, client_conn)
			
		client_socket.close()
