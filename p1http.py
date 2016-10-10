import socket
import os
import sys

def make_http_req(host):
	return ("GET / HTTP/1.1\r\nHost: {h}\r\n\r\n"). format(h=host)

if len(sys.argv)==4:
	file_name = str(sys.argv[2])
	host_name = sys.argv[3]

	rq = make_http_req(host_name)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	s.connect((host_name, 80))
	s.send(rq)
	result = s.recv(8192)

	# L_index = result.find('Content-Length: ')
	# R_index = result.find('\r\n\r\n')
	# file_size = result[L_index+16:R_index]

	file2write = open(file_name, 'w')

	while (len(result) > 0):
	    print(result)
	    file2write.write(result)
	    result = s.recv(8192)
	    

	print "dont recieveing"
elif len(sys.argv)==5:
	print "not support yet, coming soon"
	
