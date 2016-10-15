import socket
import os
import sys
import urlparse
import cStringIO
#python srget.py -o image.jpg -c [number con] url
# file_name = str(sys.argv[2])
# url_object = urlparse.urlparse(sys.argv[3])
# path = url_object.path
# url = sys.argv[3]
# url2 = url[7:]
# url3 = url2.find("/")
# host_name = url2[:url3]
class HttpDownload(object):
    def __init__(self,out_file_name,num_con,url):
        import urlparse
        import socket as skt
        self.num_con = num_con
        self.file_name = out_file_name
        self.url_obj = urlparse.urlparse(url)
        self.path = urlparse.urlparse(url).path
        self.host_name = urlparse.urlparse(url).hostname
        self.port = str(urlparse.urlparse(url).port)
        self.NL = "\r\n"
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    def make_http_req(self):
        return ("GET {p} HTTP/1.1\r\n"+ "Host: {h}\r\n"+"Connection: close\r\n\r\n").format(p=self.path,h=self.host_name)

    def make_resume_req(self,byte_range):
        return ("GET {p} HTTP/1.1\r\n"+ "Host: {h}\r\n"+"Connection: close\r\n"+"Range: bytes={b}-\r\n\r\n").format(p=self.path,h=self.host_name,b=byte_range)

    def connect(self,default=80):
    	s.connect((host_name, default))

    def send_http_rq(self):
        rq = self.make_http_req()
        return self.s.send(rq)

    def send_resume_rq(self):
        rq = self.make_resume_req()
        return self.s.send(rq)

    def header_recv(self,mode): #return recv header in string
        a = mode
        header = ""
        while "\r\n\r\n" not in header:
    		result = self.s.recv(1)
    		header += result
        return header
    def content_recv(self,mode): #take mode argument (new or resume)
        if mode == "new":
            m = "wb"
        elif new_download == "resume":
            m = "a+"

        num_bytes_recv = int(content_wrote)
    	with open(self.file_name, m) as f:
    		while True: # counter<10 is a tester that terminate at 10th loop
    			result = s.recv(2048)
    			if not result:
    				break
    			f.write(result)
    			num_bytes_recv+=len(result)
        with open(self.file_name+'_part.txt','wb')


    	return num_bytes_recv
    def write_tail()

    def main(self):
        self.connect()
        self.send_http_rq()
        self.header_recv(new) #return header ()
        self.content_recv(new) #this will write to content and return num_bytes_recv
        self.



    def extract_all(self):
        temp_string = ""
        temp_string += "Filename: "+self.file_name+self.NL
        temp_string += "Path: "+self.path+self.NL
        temp_string += "Host_name: "+self.host_name+self.NL
        temp_string += "Port: "+self.port+self.NL
        print temp_string
        return temp_string




HttpDownload("out_file.jpg","5",
            "https://yt3.ggpht.com/-v0soe-ievYE/AAAAAAAAAAI/A"+
            "AAAAAAAAAA/OixOH_h84Po/s900-c-k-no"+
            "-mo-rj-c0xffffff/photo.jpg").extract_all()
