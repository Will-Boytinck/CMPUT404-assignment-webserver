#  coding: utf-8 
import socketserver
from os import listdir
from os.path import isfile, join
import os
import pathlib


# Copyright 2023 Abram Hindle, Eddie Antonio Santos, William Boytinck
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    # TODO: Run unix2dos on runner.sh (TEST ON LAB MACHINES)
          
    def handle(self):
        self.dir_path = "www"
        self.encoding = "utf-8"
        url_method = ""
        url_path = ""
        url_protocol = ""
        mime_type = ""
        
        self.data = self.request.recv(1024).strip().decode(self.encoding)
        
        # get all files in ./www
        # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
        www_files = [os.path.join(dirpath,f) for (dirpath, dirnames, filenames) in os.walk(self.dir_path) for f in filenames]
        data_list = self.data.split()
        # check if the request contains all the required information
        try:
            url_method = data_list[0]
            url_path = data_list[1]
            url_protocol = data_list[2]
        # not in the specs, but I made it anyways because I can't read    
        except Exception:
            self.return_400_bad_request()
            return
        # update our file path    
        file_path = self.dir_path + url_path     
        # if a GET request is served [method-path-protocol]

        if url_method == "GET":
            # path not in ./www, return a 404 
            if url_path.strip("www") not in www_files: # TODO: this is broken
                print("TEST-A",url_path)
                self.return_404_not_found()
                return
            # not a file, return a 301 / fix directory edgecase
            if url_path[-1] == "/":
                 mime_type = "text/html;"
                 file_path += mime_type
                 self.return_301_moved_permanently(file_path);
            # determine mime_type
            if pathlib.Path(url_path).suffix == ".css":
                mime_type = "text/css;"
            elif pathlib.Path(url_path).suffix == ".html":
                mime_type = "text/html;"
            # tests seem good, return file contents 
            with open(file_path, 'r') as my_file:
                data = my_file.read()
                self.return_200_success(mime_type, data)
                my_file.close()
            
            return

        # a GET request is not served, return a 405 code
        else:
            self.return_405_method()
            return
        
        
    def return_200_success(self, mime_type, data):        
        status = "HTTP/1.1 200 OK\r\n"
        status += f"Content-Type: {mime_type}; charset={self.encoding}\r\n"
        status += f"Content-Length: {len(data)}\r\n"
        self.request.sendall(status.encode(self.encoding))
        self.request.sendall(data.encode(self.encoding))
    
    
    def return_404_not_found(self):
        status = b"HTTP/1.1 404 File Not Found\r\n"
        self.request.sendall(status)
    
    def return_301_moved_permanently(self, file_path):
        status = b"HTTP/1.1 301 Moved Permanently\r\n"
        self.request.sendall(status)
        self.request.sendall(b"Location: %s/\r\n" % file_path + '/')
    
    def return_405_method(self):
        status = b"HTTP/1.1 405 Method Not Allowed\r\n"
        self.request.sendall(status)
    
    def return_400_bad_request(self):
        status = b"HTTP/1.1 400 Bad Request\r\n"
        self.request.sendall(status)
    
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
