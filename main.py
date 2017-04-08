import os
import struct
import sys
from xmlrpclib import ServerProxy
import urllib
import gzip
from time import sleep

OS_SERVER = 'http://api.opensubtitles.org/xml-rpc'
OS_UA = 'OSTestUserAgentTemp'
HTTP_OK = '200'

def main():
    print('WELCOME TO THE SUBTITLE DOWNLOADER')
    filePath = (raw_input('Please input the movie/tv show file path: ')).strip()
    filePath = filePath.replace('\\', '')
    if(os.name == 'nt'):
        filePath = filePath.replace('"', '')
    hashed = hashFile(filePath)
    xmlrpc = ServerProxy(OS_SERVER,allow_none=True)
    data = attemptConnection(xmlrpc)
    
    result = xmlrpc.SearchSubtitles(data.get('token'),[{'sublanguageid':'eng','moviehash': hashed, 
                                                        'moviebytesize': os.path.getsize(filePath)}])
    fileDestination = os.path.dirname(filePath)
    if(result.get('status') == '503 Service Unavailable'):
        print("OpenSubtitles' server seems to be down, please try again later.")
        sys.exit()
    
    number_of_subs = len(result.get('data'))
    if(number_of_subs == 0):
        print("Sorry no subtitles are available!")
        sys.exit()
    print("There are " + str(len(number_of_subs)) + " available subtitles.")
    if(number_of_subs != 1):
        index = raw_input('Please input the index(starting at 0) of subtitles you want to download: ')
        #input validation
        while(not index.isdigit()):
            index = raw_input('Please input a valid integer for the index:')
        index = int(index)
        while(index > (len(result.get('data'))-1) or index < 0):
            index = int(raw_input('Index is invalid! Please input a valid index: '))
    #downloading and renaming sub
    urllib.URLopener().retrieve(result.get('data')[index].get('SubDownloadLink'), fileDestination + 'sub.gz')
    f = gzip.open(fileDestination + 'sub.gz', 'rb')
    file_content = f.read()
    f.close()
    fileExtension = filePath.rfind('.')
    srtDestination = filePath[:fileExtension]
    out = file(srtDestination + '.srt','wb')
    out.write(file_content)
    out.close()
    os.remove(fileDestination + 'sub.gz')
    print('Subtitles downloaded!')
    
# hash function obtained from http://trac.opensubtitles.org/projects/opensubtitles/wiki/HashSourceCodes
def hashFile(name): 
    try: 
                 
        longlongformat = '<q'  # little-endian long long
        bytesize = struct.calcsize(longlongformat) 
                    
        f = open(name, "rb") 
                    
        filesize = os.path.getsize(name) 
        hash = filesize 
                    
        if filesize < 65536 * 2: 
            return "SizeError" 
                 
        for x in range(65536 / bytesize): 
            buffer = f.read(bytesize) 
            (l_value,) = struct.unpack(longlongformat, buffer)  
            hash += l_value 
            hash = hash & 0xFFFFFFFFFFFFFFFF  # to remain as 64bit number  
                         
    
        f.seek(max(0, filesize - 65536), 0) 
        for x in range(65536 / bytesize): 
            buffer = f.read(bytesize) 
            (l_value,) = struct.unpack(longlongformat, buffer)  
            hash += l_value 
            hash = hash & 0xFFFFFFFFFFFFFFFF 
                 
        f.close() 
        returnedhash = "%016x" % hash 
        return returnedhash 
    
    except(IOError): 
        return "IOError"


def attemptConnection(xmlrpc):
    data = xmlrpc.LogIn('','','en',OS_UA)
    retryCounter = 0
    while(data.get('status').split()[0] != HTTP_OK and retryCounter < 3):
        print('Connection refused,  HTTP Code: ' + data.get('status').split()[0])
        print('Retrying!')
        sleep(5)
        data = xmlrpc.LogIn('','','en',OS_UA)
        retryCounter += 1
    if(retryCounter == 3):
        print('Failed to connect')
        sys.exit()
    return data

if __name__ == '__main__':
    main()