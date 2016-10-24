**Project1: speedy downloader**
---------------------------

The filename 'srget' is the most up-to-date version
===================

Remark:<br/>
1. If not connection given, the program will assume 5 connections as noted in the assignment<br/>
2. if user wish to run the normal download, please run the previous version of 'srget' as submitted in checkpoint2<br/>
3. user must parse the right inputs as bellow, (any other than that will not be accepted)<br/>
>./srget -o output file -c http://someurl.domain[:port]/path/to/file<br/>
>./srget -o output file -c numConn http://someurl.domain[:port]/path/to/file<br/>

Features:<br/>
1. command-line HTTP downloader<br/>
2. Concurrent downloader<br/>
3. Concurrent resume<br/>
4. Concurrent handle KeyboardInterrupt,ConnectionError (if occurred, user must re-initiate to resume)<br/>
5. System will assign appropriate partition according to the file size<br/>
