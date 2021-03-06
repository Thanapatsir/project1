#!/usr/bin/env python
import socket
import os
import sys
import urlparse
import os.path

file_name = str(sys.argv[2])
url_object = urlparse.urlparse(sys.argv[3])
path = url_object.path
port = url_object.port
host_name = url_object.hostname
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


def make_http_req(host, obj):
    return ("GET {o} HTTP/1.1\r\nHost: {h}\r\nConnection: close\r\n\r\n"). format(o=obj, h=host)


def make_resume_req(host, obj, _byte):
    return ("GET {o} HTTP/1.1\r\n" + "Host: {h}\r\n" + "Connection: close\r\n" + "Range: {b}\r\n\r\n"). format(o=obj, h=host, b=_byte)


def clean_up(file_name):
    dirr = os.getcwd()
    return os.remove(dirr + "/" + file_name)


def check_input():
    if len(sys.argv) == 4:
        return True
    else:
        print "invalid input"
        return False


def check_file_exist(file_name):
    dirr = os.getcwd()
    # and os.path.isfile(dirr+"/"+file_name+"_tail.txt")==True:
    if os.path.isfile(dirr + "/" + file_name) == True:
        return True
    else:
        return False


def get_resume_info():  # return true if it can be resume
    result_list = ""
    with open(sys.argv[2] + "_tail.txt", 'r') as f:
        for line in f:
            result_list += line
    return result_list  # 0=content_length 1=accept-range 2=identifier 3=content wrote


def start_connection(port=80):

    return s.connect((host_name, port))


# mode either 'resume' 'new' and if hav port
def connector(mode, port=80, content_wrote=None):
    start_connection(port)
    if mode == 'resume':
        rq = make_resume_req(host_name, path, str(
            "bytes=" + content_wrote + "-"))
    elif mode == 'new':
        rq = make_http_req(host_name, path)
    else:
        print "invalid input, pls check"
        sys.exit(1)
    return s.send(rq)


def index_finder(str_, word):
    return str_.find(word)


def get_tail_value(tail_file, key):
    L_slice = tail_file[index_finder(tail_file, key):]
    R_slice = L_slice.find('\r\n')
    return L_slice[L_slice.find(': ') + 2:R_slice]


# find they 'content-length: xxxx' both key and value
def get_tail_key_value(tail_file, key):

    L_slice = tail_file[index_finder(tail_file, key):]
    R_slice = L_slice.find('\r\n')
    return L_slice[:R_slice]


# resume_download(content_length,accept_range,identifier,content_wrote)
def resume_download(part_file_content):

    tail = ""
    content_length = get_tail_value(part_file_content, 'Content-Length')
    content_wrote = get_tail_value(part_file_content, 'Content-Wrote')

    if index_finder(part_file_content, 'ETag:') != -1:

        etag = get_tail_value(part_file_content, 'ETag:')
    else:
        etag = -1

    if index_finder(part_file_content, 'Last-Modified:') != -1:

        last_mod = get_tail_value(part_file_content, 'Last-Modified:')
    else:
        last_mod = -1

    """ MAKE CONNECTION """
    try:
        connector('resume', 80, content_wrote)
    except socket.timeout:
        print("timeout error")
    except socket.error:
        print("socket error occured: ")

    """ RECV FIRST DATA WITHOUT HEADER """

    header = ""
    tail = ""

    while "\r\n\r\n" not in header:

        result = s.recv(1)
        header += result

    if etag or last_mod in header:
        print "etag or last_mod = same, proceed to resume"

    tail += 'Content-Length: ' + content_length + "\r\n"

    if index_finder(header, 'ETag:') != -1:

        tail += get_tail_key_value(header, 'ETag:') + '\r\n'

    if index_finder(header, 'Last-Modified:') != -1:

        tail += get_tail_key_value(header, 'Last-Modified:') + '\r\n'
    else:
        print "Etag and content_length not found, cant resume, need re download"

    """ RECV THE REST OF CONTENT """

    num_bytes_recv = int(content_wrote)

    counter = 0
    try:
        with open(file_name, 'a+') as f:
            while True:  # counter<10 is a tester that terminate at 10th loop
                s.settimeout(5)
                result = s.recv(2048)
                if not result:
                    break
                f.write(result)
                num_bytes_recv += len(result)

                print "number of byte recieve : ", num_bytes_recv
    except IOError:
        print"writing progress interrupt"
        sys.exit(1)
    except socket.timeout:
        print("timeout error")
    except socket.error:
        print("socket error occured: ")

    finally:
        with open(file_name + "_tail.txt", 'wb') as f:
            to_write = "Content-Wrote: " + str(num_bytes_recv)
            f.write(tail + to_write + "\r\n")

        if int(num_bytes_recv) == int(content_length):
            clean_up(file_name + "_tail.txt")
            print "download complete"
        else:
            print "part of file is missing due to connection drop, pls resume"

        s.close()


def new_download():
    """ DECLARE VARIABLE """

    """ MAKE CONNECTION """
    try:
        connector("new", 80, None)

    except socket.timeout:
        print("timeout error")
    except socket.error:
        print("socket error occured: ")

    """ RECV FIRST DATA WITHOUT HEADER """

    header = ""
    tail = ""

    while "\r\n\r\n" not in header:
        result = s.recv(1)
        header += result
    print "header is : ", header

    content_length = get_tail_key_value(header, 'Content-Length:')
    tail += content_length + "\r\n"

    if index_finder(header, 'ETag:') != -1:
        tail += get_tail_key_value(header, 'ETag:') + '\r\n'

    if index_finder(header, 'Last-Modified:') != -1:
        tail += get_tail_key_value(header, 'Last-Modified:') + '\r\n'

    else:
        print "Etag and content_length not found, cant resume, need re download"

    """ RECV THE REST OF CONTENT """
    num_bytes_recv = 0

    counter = 0
    try:

        with open(file_name, 'wb') as f:
            while True:  # is a tester that terminate at 10th loop
                s.settimeout(5)
                result = s.recv(2048)
                if not result:
                    break
                f.write(result)
                num_bytes_recv += len(result)

                print "number of byte recieve : ", num_bytes_recv
    except IOError:
        print"writing progress interrupt"
        sys.exit(1)
    except socket.timeout:
        print("timeout error")
    except socket.error:
        print("socket error occured: ")

    finally:

        with open(file_name + "_tail.txt", 'wb') as f:
            to_write = "Content-Wrote: " + str(num_bytes_recv)
            f.write(tail + to_write + "\r\n")

        content_length = content_length[16:]
        print num_bytes_recv, content_length
        if int(num_bytes_recv) == int(content_length):
            clean_up(file_name + "_tail.txt")
            print "download complete"
        else:
            print "part of file is missing due to connection drop, pls resume"

        s.close()


def main():

    if check_input() == True:
        print "input accepted"
        if check_file_exist(sys.argv[2]):
            print "downloadfile exist, now checking if it can resume"
            if check_file_exist(sys.argv[2] + "_tail.txt"):

                # 0=content_length 1=accept-range 2=identifier 3=content wrote
                print "this server doesnt support accept-range: bytes, you must re-download the whole thing"

                print "hey this server support resume, lets resume"

                resume_download(get_resume_info())

            else:
                print "part file is missing, download is done"

        else:
            print "no such file exist"
            print "proceed to downloading"
            new_download()

main()
