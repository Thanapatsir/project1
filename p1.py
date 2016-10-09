import urllib2
url = "http://teacherstechtoolbox.com/wp-content/uploads/2015/12/Code.jpg"

file_name = url.split('/')[-1]
socket = urllib2.urlopen(url)
file2write = open(file_name, 'wb')
while True:
    buffer = socket.read(8192)
    if not buffer:
        break
    file2write.write(buffer)


file2write.close()