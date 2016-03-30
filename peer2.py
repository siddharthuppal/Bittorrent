import sys
import socket
import bencode
import hashlib
import requests
import urllib
from message import *
from torrent import Torrent
import binascii
from message import *
#from protocol import *
from twisted.internet.protocol import Protocol, ClientFactory
from twisted.internet import reactor
from sys import stdout



'''class BittorrentProtocol(Protocol):
    def dataReceived(self,data):
        stdout.write(data)
        #parse data
        #if certain type of data, do something
        
class BittorrentFactory(ClientFactory):
    def startedConnecting(self,connector):
        print 'Started to connect.'

    def buildProtocol(self,addr):
        print 'Connected.'
        return BittorrentProtocol()
        #handshake

    def clientConnectionLost(self,connector,reason):
        print 'Lost connection. Reason: ', reason
        #reconnect?
        
    def clientConnectionFailed(self,connector,reason):
        print 'Connection failed. Reason: ', reason
'''


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
    r = requests.get(torrentObj.announce_url, params=torrentObj.param_dict)
    peers = parse_response_from_tracker(r)
    return peers, torrentObj


def deal_with_incoming_message(msg):
    msg_type = determine_msg_type(msg)
    if msg_type == "bitfield":
        bitf_obj = bitfield(msg)  #do something with this abject
    elif msg_type == "piece":
        piece_obj = piece(msg) #store this piece info somewhere and gradually build up obj
    elif msg_type == "port":
        port_obj = port(msg)  #change the port we are sending to; implement when dealing with incoming requests 
    elif msg_type == "request":
        request_obj = request(msg)   #do something with this when dealing with incoming requests
    elif msg_type == "cancel":
        cancel_obj = cancel(msg)   #do something with this when dealing with incoming requests

def decode_handshake(response, torrentObj):
    handshake = Handshake(response)
    print 'handshake received: ' + repr(repr(handshake))
    other = response[68:]
    expected_peer_id = torrentObj.peer_id
    expected_info_hash = torrentObj.info_hash
    #print expected_info_hash
    #print torrentObj.info_hash
    if (expected_info_hash != handshake.info_hash):
        raise Exception('info_hash does not match expected.  Info hash expected: ' + repr(expected_info_hash) + '. Info hash found: ' + repr(handshake.info_hash))
        #instead of throwing exception, we should send a cancel message
#protocol indicates that we should check the peer_id too and that we should have gotten
 #this from the tracker.
 
    return other


def handshake(peer,torrentObj):
    info_hash = torrentObj.info_hash
    peer_id = torrentObj.peer_id
    handshake = Handshake(info_hash, peer_id)
    #pstr = 'BitTorrent protocol'
    #pstrlen = chr(19)
    #reserved = '\x00\x00\x00\x00\x00\x00\x00\x00'
    #handshake = pstrlen+pstr+reserved+info_hash+peer_id
    print 'handshake sent: '+ repr(repr(handshake))
    hostandport = peer.split(':') 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((hostandport[0],int(hostandport[1])))
    s.send(str(handshake))
    #hostname = socket.gethostname()
    #s_send = socket.socket()
    #hostandport = peer.split(':')
    #s_send.connect((hostandport[0],int(hostandport[1])),)
    #s_send.sendall(str(handshake))
    print "sent handshake to " + hostandport[0]+':'+hostandport[1]
    #response = s_send.recv(2000)
    data = s.recv(len(handshake))
    print 'response: '+repr(data)
    
    #print 'response: '+repr(response)
    response2 = s.recv(2000)
    print 'response 2: '+repr(response2)
    #decode_handshake(response+response2, torrentObj)
    #decode_handshake(data, torrentObj)
    
    s.close()
    return data + response2

    #return response+response2

def decode_messages_in_loop(response):
    print 'other: ' + repr(response)
 #   message, response = determine_msg_type(response)
    message, response = parse_message_from_response(response)
    
    print "other message type: " + repr(message.__class__.__name__) 
    print "any extra after other: "+ repr(response)
    print "message: " + repr(message) 




def main(torrentFile):
    f = open(torrentFile, 'r')
    #peer = []
    metainfo = bencode.bdecode(f.read())
    f.close()
    #f2 = open('/Users/kristenwidman/Documents/Programs/Bittorrenter/metainfo.txt','w')
    #f2.write(str(metainfo))
    peers, torrentObj = get_peers(metainfo)
    print peers
    peer=peers[2]
    #peer=''.join(peers)
    print peer
#    handshake(peer, torrentObj)
    response = handshake(peer, torrentObj)
    other = decode_handshake(response, torrentObj)
    decode_messages_in_loop(other)  #also need to add further responses received from peer
 

    #f2.close()

if __name__ == "__main__":
    #main("test.torrent")
    main("kl.torrent")

