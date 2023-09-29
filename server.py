#  coding: utf-8 
import socketserver
import os


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
    '''
    REFERENCES:
    # https://stackoverflow.com/questions/3207219/how-do-i-list-all-files-of-a-directory  (see usage of the variable 'all files')
    # https://stackoverflow.com/questions/7585435/best-way-to-convert-string-to-bytes-in-python-3 (see usage of byte string b" before status code)
    # https://pythonexamples.org/python-check-if-path-is-file-or-directory/ (os.path.isfile) and (os.path.isdir)
    # https://stackoverflow.com/questions/45188708/how-to-prevent-directory-traversal-attack-from-python-code       [see: (4)]
    '''
    
    def handle(self):
        self.dir_path = "/www"
        self.encoding = "utf-8"
        url_method = ""
        url_path = ""
        url_protocol = ""
        
        # receive data, split it
        self.data = self.request.recv(1024).strip().decode(self.encoding)
        data_list = self.data.split()
        # check if the request contains all the required information
        try:
            url_method = data_list[0]
            url_path = data_list[1]
            url_protocol = data_list[2] # redundant, but used for checking
            
        # not in the specs, but I made it anyways because I can't read    
        except Exception:
            self.return_400_bad_request()
            return
        
        # if a GET request is served [method-path-protocol]
        if url_method == "GET":
            # check if we are in a directory
            if url_path[0] == "/":
                
                # check if we are in ./www
                # verify that the file exists
                full_path = f"{os.getcwd()}{self.dir_path}{url_path}"
                
                if os.path.exists(full_path):
                    
                    # checking for directory traversal attack (4)
                    root_path = os.path.abspath(os.path.join(self.dir_path, url_path.strip("/"))) 
                    if not root_path.startswith(os.path.abspath(self.dir_path)): 
                        self.return_404_not_found()
                    
                    
                    # check if its a directory, then redirect with a 301 (because we are missing a backslash)
                    if url_path[-1] != "/" and os.path.isdir(full_path):
                        self.return_301_moved_permanently(url_path)
                        return
                    
                    # check if its a directory, then send a 200
                    elif url_path[-1] == "/" and os.path.isdir(full_path):
                        full_path += "index.html" # redirection hardcode nonsense
                        mime_type = self.get_mime_type(full_path)
                        self.return_200_success(mime_type, full_path)
                        return 
                        
                    # not a directory, must be a file, verify, then send a 200   
                    elif os.path.isfile(full_path):
                        # get mime_type
                        mime_type = self.get_mime_type(url_path)
                        self.return_200_success(mime_type, full_path)
                        return
                    
                    # not a directory, not a file, not a redirect, this should never be executed
                    # this is being left in here for debugging purposes            
                    else:
                        self.return_406_unacceptable()
                        return
            
                # requested file is not in our list, return a 404
                else:
                    self.return_404_not_found()
                    return
                    
            return

        # a GET request is not served, return a 405 code
        else:
            self.return_405_method_not_allowed()
            return
        
    
    def get_mime_type(self, url_path):
        '''
        deduce the mime_type from the url_path
        '''
        mime_type = ""
        file_extension = ""
        try:
            split =  url_path.split(".")
            file_extension = split[-1]
        except Exception:
            pass
        
        if file_extension == "css":
            mime_type = "text/css"
        elif file_extension == "html" or file_extension == ".htm":
            mime_type = "text/html"
        else:
            mime_type = "text/plain"
            
        return mime_type
    
    def return_406_unacceptable(self):
        '''
        used as a debugging code
        '''
        status = "HTTP/1.1 406 Not Acceptable"
        self.request.sendall(bytearray(status, self.encoding))
    
    def return_200_success(self, mime_type, full_path):        
        status = "HTTP/1.1 200 OK\r\n"
        data = self.display_data(full_path)
        status += f"Content-Type: {mime_type}; charset={self.encoding}\r\n\r\n{data}"
        self.request.sendall(bytearray(status, self.encoding))
    
    def return_404_not_found(self):
        status = b"HTTP/1.1 404 File Not Found\r\n"
        self.request.sendall(status)
    
    def return_301_moved_permanently(self, file_path):
        file_path += "/"
        status = f"HTTP/1.1 301 Moved Permanently\r\nLocation: {file_path}\r\nContent-type: text/plain; charset={self.encoding}\r\n"
        self.request.sendall(bytearray(status, self.encoding))
    
    def return_405_method_not_allowed(self):
        status = b"HTTP/1.1 405 Method Not Allowed\r\n"
        self.request.sendall(status)
    
    def return_400_bad_request(self):
        status = b"HTTP/1.1 400 Bad Request\r\n"
        self.request.sendall(status)
    
    def display_data(self, full_path):
        data = ""
        with open(full_path, "r") as my_file:
            data = my_file.read()
            return data
        

if __name__ == "__main__":
    HOST, PORT = "localhost", 8080

    socketserver.TCPServer.allow_reuse_address = True
    # Create the server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
