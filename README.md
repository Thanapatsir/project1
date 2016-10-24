**Project1: speedy downloader**
---------------------------

The filename 'srget' is the most up-to-date version
===================

Remark:<br 
1. If not connection given, the program will assume 5 connections as noted in the assignment

2. if user wish to run the normal download, please run the previous version of 'srget' as submitted in checkpoint2
3. user must parse the right inputs as bellow, (any other than that will not be accepted)
>./srget -o output file -c http://someurl.domain[:port]/path/to/file
./srget -o output file -c numConn http://someurl.domain[:port]/path/to/file

Features:
1. command-line HTTP downloader
2. Concurrent downloader
3. Concurrent resume
4. Concurrent handle KeyboardInterrupt,ConnectionError (if occurred, user must re-initiate to resume)
5. System will assign appropriate partition according to the file size
