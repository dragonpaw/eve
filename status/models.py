#from django.db import models
import socket
import re
import urllib

starting_pattern = re.compile(r'Starting up\.\.\.\((\d+)\ sec\.\)')
motd_url = 'http://www.eve-online.com/motd.asp?server='

# Create your models here.
class Tranquility:
    
    def __init__(self):
        self.ip = '87.237.38.200'
        self.port = 26000
        self.status = ''
        self.users = 0
        self.motd = ''
    
    def update_status(self):
        s = socket.socket()
        s.settimeout(5)
        try:
            # Connecting...
            s.connect((self.ip, self.port))
            # We're actually reading the in-game protocol header.
            data = s.recv(100)
            s.close()
            #length = len(data)
            #print 'Received: %d bytes.' % length
            #for x in xrange(0,length):
            #    print '%d: %s' % (x, repr(data[x]))
                
            # Detect the server state.
            match = starting_pattern.search(data) 
            if match:
                secs = int(match.group(1))
                if secs >= 0:
                    self.status = 'Starting up, %s secs remaining.' % secs
                else:
                    self.status = 'Start up imminent.'
            else:
                self.status = 'Online'
            
            # How many people are logged in?
            length_code = ord(data[19]) 
            if length_code == 4:
                self.users = (   ord(data[23]) * 256**3 
                               + ord(data[22]) * 256**2
                               + ord(data[21]) * 256 
                               + ord(data[20]) )
            elif length_code == 5:
                self.users = ( ord(data[21]) * 256 + ord(data[20]) )
            elif length_code == 6:
                self.status = 'Online (Questionable)'
                self.users = ord(data[20])
            else:
                self.status = 'Online (Login Disabled)'
                self.users = 0
        except:
            # Assume that all errors mean that the server is offline.
            self.status = 'Offline'
            self.users = 0
            
        try:
            # Now for the MOTD.
            handle = urllib.urlopen(motd_url + self.ip)
            self.motd = handle.read()
            # Let's make it readable.
            self.motd = re.sub(r'MOTD\s+', '', self.motd)
            self.motd = re.sub(r'</?center>', '', self.motd)
            self.motd = re.sub(r'shellexec:', '', self.motd)
        except:
            self.motd = 'Unable to query server MOTD.'
