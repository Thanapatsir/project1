import urllib2
url = "http://teacherstechtoolbox.com/wp-content/uploads/2015/12/Code.jpg"

file_name = url.split('/')[-1]
socket = urllib2.urlopen(url)
file2write = open(file_name, 'wb')
meta = socket.info()
file_size_total = int(meta.getheaders("Content-Length")[0])
print "Downloading: %s Bytes: %s" % (file_name, file_size_total)
file_size_buffer = 0
while True:
	buffer = socket.read(8192)
	if not buffer:
		break
	file_size_buffer += len(buffer)
	file2write.write(buffer)
	print file_size_buffer
file2write.close()