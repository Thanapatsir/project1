import socket
import os
import sys
import urlparse
import os.path

def make_http_req(host,obj):
	return ("GET {o} HTTP/1.1\r\nHost: {h}\r\nConnection: close\r\n\r\n"). format(o=obj,h=host)
def make_resume_req(host,obj,_byte):
    return ("GET {o} HTTP/1.1\r\n"+ "Host: {h}\r\n"+"Connection: close\r\n"+"Range: {b}\r\n\r\n"). format(o=obj,h=host,b=_byte)

def index_finder(str_,word):
	return str_.find(word)
def clean_up(file_name):
	dirr = os.getcwd()
	return os.remove(dirr+"/"+file_name)

def check_input():
	if len(sys.argv)==4:
		return True
	else:
		print "invalid input"
		return False
def check_file_exist(file_name):
	dirr = os.getcwd()
	if os.path.isfile(dirr+"/"+file_name)==True: #and os.path.isfile(dirr+"/"+file_name+"_tail.txt")==True:
		return True
	else:
		return False





def get_resume_info(): #return true if it can be resume
	result_list = ""
	with open(sys.argv[2]+"_tail.txt", 'r') as f:
		for line in f:
			result_list += line
	return result_list #0=content_length 1=accept-range 2=identifier 3=content wrote

def resume_download(part_file_content): #resume_download(content_length,accept_range,identifier,content_wrote)


	file_name = str(sys.argv[2])
	url_object = urlparse.urlparse(sys.argv[3])
	path = url_object.path
	url = sys.argv[3]
	url2 = url[7:]
	url3 = url2.find("/")
	host_name = url2[:url3]

	""" EXTRACT INPUT VARIABLE """
	L_slice = ""
	R_slice = ""
	tail = ""


	L_slice = part_file_content[index_finder(part_file_content,'Content-Length:'):]
	R_slice = L_slice.find('\r\n')
	content_length = L_slice[L_slice.find(': ')+2:R_slice]	

	L_slice = part_file_content[index_finder(part_file_content,'Content-Wrote:'):]
	R_slice = L_slice.find('\r\n')
	content_wrote = L_slice[L_slice.find(': ')+2:R_slice]


	if index_finder(part_file_content,'ETag:') != -1:
		L_slice = part_file_content[index_finder(part_file_content,'ETag:'):]
		R_slice = L_slice.find('\r\n')
		etag = L_slice[L_slice.find(': ')+2:R_slice]
	else:
		etag = -1

	if index_finder(part_file_content,'Last-Modified:') != -1:
		L_slice = part_file_content[index_finder(part_file_content,'Last-Modified:'):]
		R_slice = L_slice.find('\r\n')
		last_mod = L_slice[L_slice.find(': ')+2:R_slice]
	else:
		last_mod = -1



	""" MAKE CONNECTION """  
	rq = make_resume_req(host_name,path,str("bytes="+content_wrote+"-"))
	#rq = make_resume_req(host_name,path,"bytes=0-")
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if url_object.port==None:
		s.connect((host_name, 80))
	else:
		s.connect((host_name, url_object.port))

	s.send(rq) 

	""" RECV FIRST DATA WITHOUT HEADER """


	header = ""
	tail = ""
	tail_index = 0     #use for seek to get to content
	L_slice = ""
	R_slice = ""

	while "\r\n\r\n" not in header:

		result = s.recv(1)
		header += result



	if etag or last_mod in header:
		print "etag or last_mod = same, proceed to resume"


	# L_slice = header[index_finder(header,'Content-Length:'):]
	# R_slice = L_slice.find('\r\n')
	# tail += L_slice[:R_slice]
	# tail += '\r\n'
	tail+= 'Content-Length: '+content_length+"\r\n"


	L_slice = header[index_finder(header,'Accept-Ranges: bytes'):]
	R_slice = L_slice.find('\r\n')
	tail += L_slice[:R_slice]
	tail += '\r\n'
	

	if index_finder(header,'ETag:') != -1:
		L_slice = header[index_finder(header,'ETag:'):]
		R_slice = L_slice.find('\r\n')
		tail += L_slice[:R_slice]
		tail += '\r\n'

	if index_finder(header,'Last-Modified:') != -1:
		L_slice = header[index_finder(header,'Last-Modified:'):]
		R_slice = L_slice.find('\r\n')
		tail += L_slice[:R_slice]
		tail += '\r\n'
	else:
		print "Etag and content_length not found, cant resume, need re download"






	""" RECV THE REST OF CONTENT """

	num_bytes_recv = int(content_wrote)


	with open(file_name, 'a+') as f:
		while True: # counter<10 is a tester that terminate at 10th loop
			result = s.recv(2048)
			if not result: 
				break
			f.write(result)
			num_bytes_recv+=len(result)
			print "number of byte recieve : ",num_bytes_recv


	with open(file_name+"_tail.txt", 'wb') as f:
		to_write = "Content-Wrote: "+str(num_bytes_recv)
		f.write(tail+to_write+"\r\n")


	
	if int(num_bytes_recv) == int(content_length):
		clean_up(file_name+"_tail.txt")
		print "download complete"
	else:
		print "part of file is missing due to connection drop, pls resume"



	s.close()


def new_download():	
	""" DECLARE VARIABLE """
	file_name = str(sys.argv[2])
	url_object = urlparse.urlparse(sys.argv[3])
	path = url_object.path
	url = sys.argv[3]
	url2 = url[7:]
	url3 = url2.find("/")
	host_name = url2[:url3]

	""" MAKE CONNECTION """
	rq = make_http_req(host_name,path)
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	if url_object.port==None:
		s.connect((host_name, 80))
	else:
		s.connect((host_name, url_object.port))

	s.send(rq) 

	""" RECV FIRST DATA WITHOUT HEADER """
	
	header = ""
	tail = ""
	tail_index = 0     #use for seek to get to content
	L_slice = ""
	R_slice = ""

	while "\r\n\r\n" not in header:
		result = s.recv(1)
		header += result


	L_slice = header[index_finder(header,'Content-Length:'):]
	R_slice = L_slice.find('\r\n')
	content_length = L_slice[:R_slice]
	tail += content_length
	tail += '\r\n'


	L_slice = header[index_finder(header,'Accept-Ranges: bytes'):]
	R_slice = L_slice.find('\r\n')
	tail += L_slice[:R_slice]
	tail += '\r\n'
	

	if index_finder(header,'ETag:') != -1:
		L_slice = header[index_finder(header,'ETag:'):]
		R_slice = L_slice.find('\r\n')
		tail += L_slice[:R_slice]
		tail += '\r\n'

	if index_finder(header,'Last-Modified:') != -1:
		L_slice = header[index_finder(header,'Last-Modified:'):]
		R_slice = L_slice.find('\r\n')
		tail += L_slice[:R_slice]
		tail += '\r\n'
	else:
		print "Etag and content_length not found, cant resume, need re download"



		


	""" RECV THE REST OF CONTENT """
	num_bytes_recv = 0

	
	with open(file_name, 'wb') as f:
		while True: # counter<10 is a tester that terminate at 10th loop
			result = s.recv(2048)
			if not result: 
				break
			f.write(result)
			num_bytes_recv+=len(result)

			print "number of byte recieve : ",num_bytes_recv

	with open(file_name+"_tail.txt", 'wb') as f:
		to_write = "Content-Wrote: "+str(num_bytes_recv)
		f.write(tail+to_write+"\r\n")

	content_length = content_length[16:]
	print num_bytes_recv,content_length	
	if int(num_bytes_recv) == int(content_length):
		clean_up(file_name+"_tail.txt")
		print "download complete"
	else:
		print "part of file is missing due to connection drop, pls resume"


	s.close()


def main():
	if check_input() == True:
		print "input accepted"
		if check_file_exist(sys.argv[2]):
			print "downloadfile exist, now checking if it can resume"
			if check_file_exist(sys.argv[2]+"_tail.txt"):
				if 'Accept-Ranges: bytes' not in get_resume_info():
					print "this server doesnt support accept-range: bytes, you must re-download the whole thing"#0=content_length 1=accept-range 2=identifier 3=content wrote
				else:	
					print "hey this server support resume, lets resume"
	
					resume_download(get_resume_info())
				
			else:
				print "part file is missing, download is done"
			
		else:
			print "no such file exist"
			print "proceed to downloading"
			new_download()
main()
		