#  coding: utf-8 
import socketserver
from os import listdir
from os.path import isfile, join

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
    
          
    def handle(self):
        self.dir_path = "www"
        self.encoding = "utf-8"
        
        self.data = self.request.recv(1024).strip()
        print ("Got a request of: %s\n" % self.data)
        #self.request.sendall(bytearray("OK",'utf-8'))
        

        # 1.a get all files in ./www
             # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory
        www_files = [f for f in listdir(self.dir_path) if isfile(join(self.dir_path, f))]    
        
        #self.request.sendall(bytearray("The following are links in ./www:\n", self.encoding))
        #for afile in www_files:
        #    afile += '\n'
        #    self.request.sendall(bytearray(afile, self.encoding))
        

        # parse entire request, get vars with pertinent data first
        data_list = self.data.split()
        url_method = data_list[0]
        url_path = data_list[1]
        url_protocol = data_list[2]

        # if a GET request is served [method-pass-protocol]
        if url_method == "GET":
            pass

        
            # check if url in www_files (might have to split it again...)


        # a GET request is not served, return a 405 code
        else:
            self.request.sendall(b"HTTP/1.1 405 Method Not Allowed\r\n")
            
        
        
        
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
