import socket
import os
import sys
import urlparse
import time
def make_http_req(host,obj):
	return ("GET {o} HTTP/1.1\r\nHost: {h}\r\n\r\n"). format(o=obj,h=host)

if len(sys.argv)==4:
	
	file_name = str(sys.argv[2])
	url_object = urlparse.urlparse(sys.argv[3])


	url = sys.argv[3]
	url2 = url[7:]
	if url_object.port==None:
		url3 = url2.find("/")

	else:
		url3 = url2.find(":")
	host_name = url2[:url3]


	path = url_object.path
		

	rq = make_http_req(host_name,path)

	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

	if url_object.port==None:
		s.connect((host_name, 80))
	else:
		s.connect((host_name, url_object.port))
	start = time.time()	
	s.send(rq)

	result = s.recv(8192)

	index = result.find('\r\n\r\n')
	result_wo_header = result[index+4:]
	file2write = open(file_name, 'w')
	file2write.write(result_wo_header)

	while (len(result) > 0):
	    result = s.recv(8192)
	    file2write.write(result)
	end = time.time()
	print"time complex: ",(end - start)
	print "dont recieveing"
elif len(sys.argv)==5:
	print "not support yet, coming soon"
	
