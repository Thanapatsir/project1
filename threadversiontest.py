#!/usr/bin/env python
import socket
import os
import sys
import urlparse
import threading
import time


def make_resume_req(host, obj, _byte):
    return ("GET {o} HTTP/1.1\r\n" + "Host: {h}\r\n" + "Connection: close\r\n" + "Range: {b}\r\n\r\n"). format(o=obj, h=host, b=_byte)


def make_http_req(host, obj):
    return ("GET {o} HTTP/1.1\r\nHost: {h}\r\nConnection: close\r\n\r\n"). format(o=obj, h=host)


def check_file_exist(file_name):
    dirr = os.getcwd()
    # and os.path.isfile(dirr+"/"+file_name+"_tail.txt")==True:
    if os.path.isfile(dirr + "/" + file_name) == True:
        return True
    else:
        return False


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
    print rq
    header = ""
    while "\r\n\r\n" not in header:
        result = s.recv(1)
        header += result
    L_slice = header[header.find("Content-Length: ") + 16:]
    R_slice = L_slice.find('\r\n')
    content_length = L_slice[:R_slice]
    return content_length


def part_download(file_name, url, b_start, b_end, meta_array, index):

    # host_name = url_obj.hostname

    host_name, port, path = parser(url)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.settimeout(5)
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
    except Exception:
        print"connect error"
        meta_array[index] = False
    """ get the header """
    header = ""
    try:
        while "\r\n\r\n" not in header:
            s.settimeout(5)
            result = s.recv(1)
            header += result
    except Exception:
        print"error conencting"
        meta_array[index] = False

    L_slice = header[header.find("Content-Length: ") + 16:]
    R_slice = L_slice.find('\r\n')
    content_length = L_slice[:R_slice]

    bytes_recv = 0
    try:
        with open(file_name, 'a+') as f:
            while True:  # counter<10 is a tester that terminate at 10th loop
                s.settimeout(5)
                result = s.recv(BUFF_SIZE)
                if not result:
                    break
                f.write(result)
                bytes_recv += len(result)
        meta_array[index] = True
        # print "number of byte recieve : ", bytes_recv
    except IOError:
        print"writing progress interrupt"
        meta_array[index] = False
    except socket.timeout:
        print("timeout error")
        meta_array[index] = False
    except socket.error:
        print("socket error occured: ")
        meta_array[index] = False
    except Exception as m:
        print m
        meta_array[index] = False
    s.close()


def combine_file(files, outfile):  # files = array of file name
    dirr = os.getcwd()
    with open(outfile, 'a+') as f:
        for fname in files:
            with open(fname) as infile:
                for line in infile:
                    f.write(line)
            os.remove(dirr + "/" + fname)
    print"combine successful"


def remove_file(files):
    dirr = os.getcwd()
    return os.remove(dirr + "/" + files)


def resume_allocator(out_file, url, chunk_range, chunk_dividier_size, thread_status_table, connection):
    content_length = (chunk_range[1] - chunk_range[0]) + 1
    initial_content_length = chunk_range[1]
    #(chunk_range[1] - chunk_range[0]) + 1
    each = int(content_length) // int(connection)
    #f_name = [file_name + str(x) for x in range(connection)]
    start_range = [chunk_range[0]] + [chunk_range[0] +
                                      (each * x) for x in range(connection) if x > 0]
    end_range = [x + each - 1 for x in start_range[:-1]] + [chunk_range[1]]

    result_range = []
    threads = []
    chunk_divider_table = [None] * connection
    try:

        for i, j in zip(start_range, end_range):
            result_range.append([i, j])
        for i, j, k in zip(result_range, range(connection), thread_status_table):
            t = threading.Thread(target=thread_allocator, args=(
                file_name, url, i, connection, thread_status_table))

            chunk_divider_table[j] = i
            print "sending big thread : ", i
            t.start()

            t.join()
            for o in thread_status_table:
                if o == False:
                    print"error found, breaking loop"
                    with open('thread_meta.txt', "wb+") as f:
                        strr1 = str(i[0]) + "," + str(initial_content_length)
                        f.write(strr1)

                    my_dir = os.getcwd()
                    for fname in os.listdir(my_dir):
                        if fname.startswith("part"):
                            os.remove(os.path.join(my_dir, fname))
                    return
    except Exception as m:
        print "Big thread exception handle"
        print m


def thread_allocator(file_name, url, chunk_range, connection, meta_array):
    content_length = (chunk_range[1] - chunk_range[0]) + 1
    #content_length = chunk_range[1]
    each = int(content_length) // int(connection)
    f_name = ["part_" + file_name + str(x) for x in range(connection)]
    start_range = [chunk_range[0]] + [chunk_range[0] +
                                      (each * x) for x in range(connection) if x > 0]
    end_range = [x + each - 1 for x in start_range[:-1]] + [chunk_range[1]]
    threads = []
    try:
        for i, j, k, l in zip(f_name, start_range, end_range, range(len(meta_array))):
            t = threading.Thread(target=part_download, args=(
                str(i), url, str(j), str(k), meta_array, l))
            threads.append(t)
            print ("sending small thread : ({a}, {b})").format(a=j, b=k)
            t.start()
        for t in threads:
            t.join()
    except:
        print"small thread exception handle"
    print meta_array

    counter = 0

    for i in range(len(meta_array)):
        if meta_array[i]:
            counter += 1

    if counter == connection:
        combine_file(f_name, file_name)
        print "combine successful"
    else:
        print "part of file is missing"

BUFF_SIZE = 2048
url = "http://10.27.8.20:8080/hugefile.qqq"
content_length = get_content_length(url)  # change it to range
content_range = [0, int(content_length) - 1]
connection = 5
file_name = "para.mp4"
print content_length

thread_status = [None] * connection

if check_file_exist('thread_meta.txt'):
    # extrac meta file"
    result = []
    with open('thread_meta.txt', "rb") as fp:
        for i in fp.readlines():
            tmp = i.split(",")
            print"tmp:", tmp
            result.append(int(tmp[0]))
            result.append(int(tmp[1]))
            #result.append((eval(tmp[0]), eval(tmp[1])))
    print result
    chunk_range = result
    resume_allocator(file_name, url, chunk_range, 2, thread_status, connection)
else:
    resume_allocator(file_name, url, content_range, 2, thread_status,
                     connection)  # 5 is the slice piece
