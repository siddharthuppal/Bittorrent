import sys
import socket
import bencode
import hashlib
import requests
import urllib
from torrent import Torrent
from Tkinter import *
from tkFileDialog import askopenfilename
import sys
import unittest
import bencode

def connect(handshake,peers,torrentObj):
        number_connections = 0
        k=len(peers)

        for peer in peers:
            if number_connections < k:
                hostandport = peer.split(':')
                print hostandport[0] + ':' + hostandport[1]
                bittorrent_factory = BittorrentFactory(torrentObj)
                reactor.connectTCP(hostandport[0], int(hostandport[1]),bittorrent_factory)
                number_connections += 1

def parse_response_from_tracker(r):
    '''Input: http response from our request to the tracker
       Output: a list of peer_ids
       Takes the http response from the tracker and parses the peer ids from the 
       response. This involves changing the peer string from unicode (binary model)
       to a network(?) model(x.x.x.x:y). From the spec: 'First 4 bytes are the IP address and
       last 2 bytes are the port number'
    '''
    response = bencode.bdecode(r.content)
    print response
    peers = response['peers']
    #print peers
    #print [str(ord(x))+x for x in peers]


    i=1
    peer_address = ''
    peer_list = []
    for c in peers:
        if i%6 == 5:
            port_large = ord(c)*256
        elif i%6 == 0:
            port_small = ord(c)
            port = port_large+port_small
            peer_address += ':'+str(port)
            peer_list.append(peer_address)
            peer_address = ''
        elif i%6 == 4:
            peer_address += str(ord(c))
        else:
            peer_address += str(ord(c))+'.'
        i += 1
    return peer_list

def get_peers(metainfo):
    '''Input: metainfo file (.torrent file)
       Output: a list of peer_ids (strings) returned from the tracker
       Calls methods to send an http request to the tracker, parse the returned
       result message and return a list of peer_ids
    '''
    torrentObj = Torrent(metainfo)
    #http://pow7.com:80/announce
    #socket.create_connection(('pow7.com', 80 ), timeout=2)
    r = requests.get(torrentObj.announce_url, params=torrentObj.param_dict)
    #print 'r.content: '+r.content
    #print 'r.text: '+r.text
    peers = parse_response_from_tracker(r)
    return peers, torrentObj

def handshake(peer,torrentObj):
    '''Input: ip:port of a peer with the torrent files of interest
       Output: <fill this in>
       <fill this in>
    '''
    pstrlen = chr(19)
    pstr = "BitTorrent protocol"
    reserved = '\x00\x00\x00\x00\x00\x00\x00\x00' 
    info_hash = torrentObj.info_hash 
    peer_id = torrentObj.peer_id
    handshake = pstrlen+pstr+reserved+info_hash+peer_id
    return handshake
    
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
    #abc = bencode.bdecode(open(file, 'rb').read())
    #print abc
    #return file   

def main(torrentFile):
    f = open(torrentFile, 'r')
    metainfo = bencode.bdecode(f.read())
    f.close()
    peers, torrentObj = get_peers(metainfo)
    print peers
    k=len(peers)
    print k
    handske=handshake(peers, torrentObj)
    connect(handske,peers,torrentObj)

    reactor.run()



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
    #main("kl.torrent")

