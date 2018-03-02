import socket
import threading
import sys
import select

class Client_handler(threading.Thread):

	def __init__(self, proxy_socket, client_conn):
		threading.Thread.__init__(self)
		self.proxy_socket = proxy_socket
		self.client_conn = client_conn

	def handle_header(self):
		# recevie the tcp payload
		data = client_conn.recv(8192)

		strings = bytes(data)
		
		http_version_idx = strings.find('HTTP/1.1')
		connection_idx = strings.find('keep-alive')
		second_connection_idx = strings.find('keep-alive', connection_idx + 10)
		print 'conn idx', connection_idx
		header_end_idx = strings.find('\r\n\r\n')
		forward_request = strings[0:http_version_idx + 7] + '0' + strings[http_version_idx + 8:connection_idx] + 'close' 
		if second_connection_idx == -1:
			forward_request = forward_request + strings[connection_idx + 10:]
		else :
			forward_request = forward_request + strings[connection_idx + 10: second_connection_idx] + 'close' + strings[connection_idx + 10:]
		# forward_request_header = strings[0:http_version_idx + 7] + '0' + strings[http_version_idx + 8:connection_idx] + 'close' + strings[connection_idx + 10: connection_idx]
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
			self.connect_to_server(forward_port, forward_host, data)
		else:
			self.nonconnect_to_server(forward_port, forward_host, forward_request)

	def connect_to_server(self, forward_port, forward_host, data):
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
			print return_message
			self.client_conn.send(str.encode(return_message))
		except Exception:
			return_message = "HTTP/1.0 502 Bad Gateway\r\n\r\n"
			print return_message
			self.client_conn.send(str.encode(return_message))
			sock.close()
			return

		self.client_conn.settimeout(0.5)
		sock.settimeout(0.5)
		max_bytes = 8192
		from_client = True
		client_timeout = False
		server_timeout = False
		while 1:
			if from_client:
				try:
					client_result = self.client_conn.recv(max_bytes)
					client_timeout = False
					print "recv from client"
					sock.send(client_result)
					print "send to server"
				except socket.timeout:
					from_client = not from_client
					client_timeout = True
					continue
				else:
					if len(client_result) == 0:
						sock.close()
						break
			else:
				try:
					server_result = sock.recv(max_bytes)
					server_timeout = False
					print "recv form server"
					self.client_conn.send(server_result)
					print "send to client"
				except socket.timeout:
					from_client = not from_client
					server_timeout = True
					continue
				else:
					if len(server_result) == 0:
						sock.close()
						break
		print "out while loop"
		sock.close()


	def nonconnect_to_server(self, forward_port, forward_host, forward_request):
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
			self.client_conn.send(result)
			result = sock.recv(max_bytes)
			content_length -= max_bytes

		if (not strings == None):
			self.client_conn.send(result)

		sock.close()



if __name__ == '__main__':
	tcp_port = sys.argv[1]
	
	server_ip = socket.gethostbyname("localhost")
	proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	proxy_socket.bind((server_ip, int(tcp_port)))
	proxy_socket.listen(1)
	while 1:
		client_conn, client_addr = proxy_socket.accept()
		handler = Client_handler(proxy_socket, client_conn)
		handler.handle_header()
			
	proxy_socket.close()
