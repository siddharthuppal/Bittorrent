import sys
import select,errno
import socket
import bencode
import hashlib
import requests
import urllib
from message import *
from torrent import Torrent
from bitarray import bitarray
from Tkinter import *
from tkFileDialog import askopenfilename
#import binascii
import message 
from sys import stdout
import struct

handshaken=[]

class Peer(object):
    """
    This object contains the information needed about the peer.
    self.ip - The IP address of this peer.
    self.port - Port number for this peer.
    self.choked - sets if the peer is choked or not.
    self.bitField - What pieces the peer has.
    self.socket - Socket object
    self.bufferWrite - Buffer that needs to be sent out to the Peer. When we 
                       instantiate a Peer object, it is automatically filled 
                       with a handshake message.
    self.bufferRead - Buffer that needs to be read and parsed on our end.
    self.handshake - If we sent out a handshake.
    """
    def __init__(self, ip, port, socket):
        self.ip = ip
        self.port = port
        self.choked = False
        self.bitField = None
        self.interested = False
        self.peer_interested    = False
        self.peer_choked        = True
        self.socket = socket
        self.bufferWrite = ''
        self.bufferRead = ''
        self.handshake = False
    def fileno(self):
        return self.socket.fileno()

def parse_response_from_tracker(r):
    response = bencode.bdecode(r.text)
    peers = response['peers']
    x=len(peers)
    length=0
    peer_ip_and_port_dict={}
    while length<x:
        ip=''
        port=0
        for k in peers[length:4+length]:
            ip=ip + str(ord(k)) + (".")
            length=length+1
        port=ord(peers[length])*256+ord(peers[length+1])
        length=length+2
        peer_ip_and_port_dict[ip[:-1]]=port  
    print peer_ip_and_port_dict
    return peer_ip_and_port_dict      


def get_peers(metainfo):
    '''Input: metainfo file (.torrent file)
       Output: a list of peer_ids (strings) returned from the tracker
       Calls methods to send an http request to the tracker, parse the returned
       result message and return a list of peer_ids
    '''
    torrentObj = Torrent(metainfo)
    r = requests.get(torrentObj.announce_url, params=torrentObj.param_dict)
    peers = parse_response_from_tracker(r)
    return peers, torrentObj



def run(sockets,torrentObj):
    info_hash = torrentObj.info_hash
    peer_id = torrentObj.peer_id
    handshake = Handshake(info_hash, peer_id)
    sock2task = dict([(s, i + 1) for i, s in enumerate(sockets)])
    sockets = list(sockets) # make a copy, tuple to list
     # we go around this loop until we've gotten all the poetry
     # from all the sockets. This is the 'reactor loop'.


    for sock in sockets:
        try:
            sock.socket.send(str(handshake))
            print "handshaking was sent " + str(sock.ip) + ":" +str(sock.port)
        except socket.error:
            sockets.remove(sock)
            print "socket closed as handshaking was not sent " + str(sock.ip) + ":" +str(sock.port) + "\n"
            sock.socket.close()
    print "\n"

    while sockets:     # this select call blocks until one or more of the
         # sockets is ready for read I/O
        
             #sock.send(maketheshake(infohash,peer_id))
         
        #print sockets
        rlist, _, _ = select.select(sockets, [], [])  # rlist is the list of sockets with data ready to read
        
      
        for sock in rlist:
            print "Peer ready to read data "+ str(sock.ip) + ":" +str(sock.port)

        
        for sock in rlist:
            data = ''
            while True:
                try:
                    sock.bufferRead += sock.socket.recv(1024)
                    #print repr(sock.bufferRead)
                    '''
                    if new_data[28:48]==infohash:
                        sock.peerid=new_data[48:68]
                        sock.handshakerecv=new_data
                        print "success! %d" % sock2task[sock]
                    '''
                except socket.error, e:
                    if e.args[0] == errno.EWOULDBLOCK:
                        pass
                    elif e.args[0] == errno.EPIPE: 
                        pass
                    elif e.args[0] == 35:
                        print"resources"
                    break
                    raise
                #else:
                #dReceived(sock,torrentObj)   
                     
                if sock.bufferRead:
                    #y=raw_input("yolo?")
                    dReceived(sock,torrentObj)
                else:
                    print "no input from the peer \n"
                    break        
            #task_num = sock2task[sock]
            sockets.remove(sock)
            sock.socket.close()
            #print 'Task %d finished' % task_num
            

           
            '''
            if not k:
                sockets.remove(sock)
                sock.socket.close()
                print 'Task %d finished' % task_num
            else:
                print "hi"
            '''    
    print "handshaken peers are\n"
    for sock in handshaken:
        print str(sock.ip) + ":" +str(sock.port)

def dReceived(sock,torrentObj):
        data = handData(sock)
        while(data != None):
            if(data[1:20].lower() == "bittorrent protocol"): 
                # The message is a Handshake Message
                parseHandshake(sock,data,torrentObj)
            else:
                parseNonHandshakeMessage(data,sock)
            if(canSendRequest(sock)):
                print "you can send the request\n"
            else:
                #print "you can't send the request\n"
                print '\n'
                #generate_next_request()    #Send Request for next block
            data = handData(sock)
        

def handData(sock):
        buffer1 = sock.bufferRead
        message = ""
        if(buffer1[1:20].lower() == "bittorrent protocol"): 
            message += buffer1[:68]
            sock.bufferRead = buffer1[68:]
            print "handshaking done " + repr(message)
            return message
        # If the message in queue is not a Handshake Message, then the first 4 bytes represent the lenght of the message.
        message_length = bytes_to_number(sock.bufferRead[:4]) + 4
        if(len(sock.bufferRead) >= message_length):
            message = sock.bufferRead[:message_length]
            sock.bufferRead = sock.bufferRead[message_length:]
            return message
        return None

def parseHandshake(sock,data,torrentObj):
        # If the Info Hash matches the torrent's info hash, add the peer to the successful handshake set
        #print "in parseHandshake"
        handshake_response_data = message.Handshake(data)
        handshake_info_hash     = handshake_response_data.info_hash
        #print "peer's infohash" + repr(handshake_info_hash)
        #print "our infohash" + repr(torrentObj.info_hash)
        if handshake_info_hash == torrentObj.info_hash:
            handshaken.append(sock)
            print "the infohash has matched"
            # Check if Should we be interested or not 
            k=message.Interested()
            print "interested message send by us " +repr(k)
            #print  "lalal"
            #y=raw_input("there?")
            sock.socket.send(str(k))
            sock.bufferRead += data[68:]


        else :
            print "not matched"
           
        return 


def parseNonHandshakeMessage(data,sock):
        bytestring = data
        if (bytestring[0:4] == '\x00\x00\x00\x00'): 
            # Its a Keep Alive message #
            message_obj = message.KeepAlive(response=bytestring)
        else:
            message_obj  = {
              0: lambda: message.Choke(response=bytestring),
              1: lambda: message.Unchoke(response=bytestring),
              2: lambda: message.Interested(response=bytestring),
              3: lambda: message.Interested(response=bytestring),
              4: lambda: message.Have(response=bytestring),
              5: lambda: message.Bitfield(response=bytestring),
              6: lambda: message.Request(response=bytestring),
              7: lambda: message.Piece(response=bytestring),
              8: lambda: message.Cancel(response=bytestring),
              9: lambda: message.Port(response=bytestring),
            }[    struct.unpack('!b',data[4])[0]   ]()     # The 5th byte in 'data' is the message type/id 
        process_message(message_obj,sock)




def process_message(message_obj,sock):
        #fmt = 'Peer : {:16s} || {:35s}'
        #print fmt
        if isinstance(message_obj, message.Choke):
            print "choke"
            sock.choked = True
        elif isinstance(message_obj, message.Unchoke):
            print "unchoke"
            sock.choked = False
        elif isinstance(message_obj, message.Interested):
            print "interested"
            sock.peer_interested = True
        elif isinstance(message_obj, message.NotInterested):  
            print "notinterested"
            sock.peer_interested = False
        elif isinstance(message_obj, message.Have):
            piece_index = message.bytes_to_number(message_obj.index)
            print "the client" + str(sock.ip) + ":" + str(sock.port) + "have piece no. " + str(piece_index)

        elif isinstance(message_obj, message.Bitfield):
            #k=convert_to_binary(message_obj)            
            print str("Peer :") + str(sock.ip) + " || " + "Bitfield"
            #print k
            Bitarray = bitarray()
            Bitarray.frombytes(message_obj.bitfield)
            print Bitarray
            y=raw_input("there")

            
        elif isinstance(message_obj, message.Request):
            print "request"
        elif isinstance(message_obj, message.Cancel):
            print "cancel"
        elif isinstance(message_obj, message.Port):
            print "port message"

'''
def convert_to_binary(message_obj):
    qwe = ''.join(str(ord(c)) for c in message_obj)
    i = int(qwe, 16)
    x='{0:08b}'.format(i)
    return x
'''
def canSendRequest(sock):
        if sock.interested and not sock.choked:
            print sock.interested
            print sock.choked
            return True
        return False


def connect(address):    
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    try:
        sock.connect(address)
    except socket.error:
        print "not connected to " + str(address)        
        #print address   
        return None
    sock.setblocking(0)  
    s1= Peer(address[0],address[1],sock)
    print "connected to " + str(address)
    return s1 


def main(torrentFile):
    f = open(torrentFile, 'r')
    metainfo = bencode.bdecode(f.read())
    f.close()
    peers, torrentObj = get_peers(metainfo)
    p=[ (k,v) for k,v in peers.iteritems()]
    per=map(connect,p)
    print "\n"
    sock=[x for x in per if x is not None]
    run(sock,torrentObj)
    #for s in sock:
     #   print s.handshake

def donothing():
   filewin = Toplevel(root)
   button = Button(filewin, text="Do nothing button")
   button.pack()

def quit_handler():
    print "program is quitting!"
    sys.exit(0)

def open_file_handler():
    file= askopenfilename()
    main(file)

    
if __name__ == "__main__":
    
    root = Tk()
    menubar = Menu(root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="New", command=donothing)
    filemenu.add_command(label="Add Torrent File", command=open_file_handler)
    filemenu.add_command(label="Save", command=donothing)
    filemenu.add_command(label="Save as...", command=donothing)
    filemenu.add_command(label="Close", command=quit_handler)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=root.quit)
    menubar.add_cascade(label="File", menu=filemenu)
    editmenu = Menu(menubar, tearoff=0)
    editmenu.add_command(label="Undo", command=donothing)
    editmenu.add_separator()
    editmenu.add_command(label="Cut", command=donothing)
    editmenu.add_command(label="Copy", command=donothing)
    editmenu.add_command(label="Paste", command=donothing)
    editmenu.add_command(label="Delete", command=donothing)
    editmenu.add_command(label="Select All", command=donothing)
    menubar.add_cascade(label="Edit", menu=editmenu)
    helpmenu = Menu(menubar, tearoff=0)
    helpmenu.add_command(label="Help Index", command=donothing)
    helpmenu.add_command(label="About...", command=donothing)
    menubar.add_cascade(label="Help", menu=helpmenu)
    open_file = Button(root, command=open_file_handler, padx=100, text="OPEN FILE")
    open_file.pack()
    quit_button = Button(root, command=quit_handler, padx=100, text="QUIT")
    quit_button.pack()

    root.config(menu=menubar)
    root.mainloop()
