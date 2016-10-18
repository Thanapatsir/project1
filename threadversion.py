#!/usr/bin/env python
import socket
import os
import sys
import urlparse
import Queue
import threading
import random
import time
import json


def make_resume_req(host, obj, _byte):
    return ("GET {o} HTTP/1.1\r\n" + "Host: {h}\r\n" + "Connection: close\r\n" + "Range: {b}\r\n\r\n"). format(o=obj, h=host, b=_byte)


def make_http_req(host, obj):
    return ("GET {o} HTTP/1.1\r\nHost: {h}\r\nConnection: close\r\n\r\n"). format(o=obj, h=host)

meta = dict()
BUFF_SIZE = 2048
lock = threading.Lock()


def parser(url):
    url_obj = urlparse.urlparse(url)
    path = url_obj.path
    port = url_obj.port
    host_name = url_obj.hostname
    return host_name, port, path


def get_content_length(url):
    host_name, port, path = parser(url)
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if not port:
        s.connect((host_name, 80))
        rq = make_http_req(host_name, path)
    else:
        s.connect((host_name, port))
        rq = make_http_req(host_name, path)
    s.send(rq)
    header = ""
    while "\r\n\r\n" not in header:
        result = s.recv(1)
        header += result
    L_slice = header[header.find("Content-Length: ") + 16:]
    R_slice = L_slice.find('\r\n')
    content_length = L_slice[:R_slice]
    return content_length


def part_download(file_name, url, b_start, b_end):

    url_obj = urlparse.urlparse(url)
    path = url_obj.path
    port = url_obj.port
    host_name = url_obj.hostname

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    if not port:
        s.connect((host_name, 80))
    else:
        s.connect((host_name, port))
    if b_end == "-":

        rq = make_resume_req(host_name, path, "bytes=" +
                             b_start + "-")  # b start and end
    else:
        rq = make_resume_req(host_name, path, "bytes=" +
                             b_start + "-" + b_end)  # b start and end

    s.send(rq)

    """ get the header """
    header = ""
    while "\r\n\r\n" not in header:
        result = s.recv(1)
        header += result

    L_slice = header[header.find("Content-Length: ") + 16:]
    R_slice = L_slice.find('\r\n')
    content_length = L_slice[:R_slice]

    bytes_recv = 0
    try:
        with lock:
            with open(file_name, 'a+') as f:
                while True:  # counter<10 is a tester that terminate at 10th loop
                    s.settimeout(5)
                    result = s.recv(BUFF_SIZE)
                    if not result:
                        break
                    f.write(result)
                    bytes_recv += len(result)

                # print "number of byte recieve : ", bytes_recv
    except IOError:
        print"writing progress interrupt"
        sys.exit(1)
    except socket.timeout:
        print("timeout error")
    except socket.error:
        print("socket error occured: ")

    finally:
        print bytes_recv, content_length
        if int(bytes_recv) == int(content_length):
            # write done! to meta so T1:done
            meta[file_name] = "done"

        else:
            # write T1:bytes_recv-b_end
            meta[file_name] = (
                "request:{a}-{b} recv:{c}").format(a=b_start, b=b_end, c=bytes_recv)
        # with open('meta_data.pkl', 'wb') as f:
        #     pickle.dump(meta, f)
        print"gonna write now"
        with lock:
            with open('meta_data.txt', 'wb+') as f:
                f.write(str(meta))

        s.close()
    print "--------------------------------------------"


def combine_file(files, outfile):  # files = array of file name
    dirr = os.getcwd()
    with open(outfile, 'wb+') as f:
        for fname in files:
            with open(fname) as infile:
                for line in infile:
                    f.write(line)
            os.remove(dirr + "/" + fname)
    print"combine successful"

def resume_allocator(meta_file):
    # with open(meta_file,'rb') as f:
    #     json.loads
    #
    pass

# connection = how many thread
def thread_allocator(file_name, url, content_length, connection):
    start = time.time()
    each = int(content_length) // int(connection)
    f_name = range(connection)
    start_range = [0] + [x * (each) + 1 for x in range(connection) if x > 0]
    end_range = [x * each for x in range(1, connection + 1)]
    threads = []
    for i, j, k in zip(f_name, start_range, end_range):
        if i == int(connection) - 1:
            t = threading.Thread(target=part_download, args=(
                file_name + str(i), url, str(j), str(content_length)))
            t.start()
            threads.append(t)
        else:
            t = threading.Thread(target=part_download, args=(
                file_name + str(i), url, str(j), str(k)))
            t.start()
            threads.append(t)
    for t in threads:
        t.join()

    file_genarator = [file_name + str(x) for x in f_name]
    combine_file(file_genarator, file_name)
    elapsed = time.time() - start
    print elapsed

    # combine_file(["z.pdf0","z.pdf1","z3.pdf2"],"z.pdf")


url = "http://10.27.8.20:8080/bigfile.xyz"
content_length = get_content_length(url)
print content_length
thread_allocator("para.zip", url, content_length, 5)
