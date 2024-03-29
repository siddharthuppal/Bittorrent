import unittest
import sys
import socket
import bencode
import hashlib
import random
import string
import requests
import urllib

local_port = 59696
peer_id_start = '-KB1000-'


def length_of_file(metainfo):
	info = metainfo['info'] 
	length = 0
	if 'length' in info:
		length = info['length']
	else:
		files = info['files']
		for i in files:
			length += i['length']
	return length

def generate_peer_id():
    N = 20 - len(peer_id_start) 
    end = ''.join(random.choice(string.ascii_lowercase + string.digits) for x in range(N))
    peer_id = peer_id_start + end
    return peer_id


def get_parameters(metainfo):
	info = metainfo['info'] 
	print info
	sha_info=hashlib.sha1(bencode.bencode(info))
	info_hash = sha_info.digest()
    peer_id=generate_peer_id()
    uploaded=0
    downloaded=0
    left=length_of_file(metainfo)
  #  compact=1
    no_peer_id=0
    event="started"
    param_dict = {'info_hash':info_hash, 'peer_id':peer_id, 'port':local_port, 'uploaded':uploaded, 
	    'downloaded':downloaded, 'left':left, 'compact':compact, 'no_peer_id':no_peer_id, 'event':event}
    return param_dict

def get_peers(metainfo):
	announce_url = metainfo['announce']
 	parameter_list = get_parameters(metainfo)
 	r = requests.get(announce_url, params=parameter_list)
 	#torrentObj = Torrent(metainfo)
 	#r = requests.get(torrentObj.announce_url, params=torrentObj.param_dict)
 	peers = parse_response_from_tracker(r)
 	return peers, torrentObj

def parse_response_from_tracker(r):
	response = bencode.bdecode(r.text)
	print response
	response = bencode.bdecode(r.content)
	peers = response['peers']
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
	print str(peer_list)
	return peer_list
 


abc = bencode.bdecode(open('try.torrent', 'rb').read())
str2 = "announce";

#print abc
#print abc['comment']


n=len(abc['info']['files']);
n1=length_of_file(abc)

print "length of file " + str(n1)

id1=generate_peer_id()
print id1

#k=0
#for i in range(n):
#	print abc['info']['files'][i]['path']
#	k=k+abc['info']['files'][i]['length']
	
#print k
#print abc['info']['piece length']
#print abc['info']['name']

#print abc['info']['pieces']


print abc['creation date']
print abc['announce-list']
print abc['announce']

