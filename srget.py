import socket
import os
import sys
import urlparse

def make_http_req(host,obj):
	return ("GET {o} HTTP/1.1\r\nHost: {h}\r\nConnection: close\r\n\r\n"). format(o=obj,h=host)


num_bytes_recv = 0
if len(sys.argv)==4:
	
	file_name = str(sys.argv[2])
	url_object = urlparse.urlparse(sys.argv[3])
	path = url_object.path
	url = sys.argv[3]
	url2 = url[7:]
	if url_object.port==None:
		url3 = url2.find("/")
	else:
		url3 = url2.find(":")
	host_name = url2[:url3]

	rq = make_http_req(host_name,path)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if url_object.port==None:
		s.connect((host_name, 80))
	else:
		s.connect((host_name, url_object.port))
	s.send(rq)


	result = s.recv(8192)
	num_bytes_recv += len(result)
	index = result.find('\r\n\r\n')
	result_wo_header = result[index+4:]
	print result
	data = ""
	with open(file_name, 'wb') as f:
		data+=result_wo_header
		while True:#(len(result) > 0):
			print "number of byte recieve : ",num_bytes_recv
			result = s.recv(8192)
			if not result: 
				break
			num_bytes_recv+=len(result)
			data+=result
		f.write(data)	
	print "download complete"

	s.close()
elif len(sys.argv)==5:
	print "not support yet, coming soon"
	
