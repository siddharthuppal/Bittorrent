import unittest
import sys
import socket
import bencode
import hashlib
import random
import string
import requests
import urllib
import urllib2



local_port = 59696
peer_id_start = '-KB1000-'


proxy = urllib2.ProxyHandler({'ip':'10.175.96.118'})
opener = urllib2.build_opener(proxy)
urllib2.install_opener(opener)





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
	'downloaded':downloaded, 'left':left,'no_peer_id':no_peer_id, 'event':event}
	return param_dict

def get_peers(metainfo):
	announce_url = metainfo['announce']
 	parameter_list = get_parameters(metainfo)
 	c1=announce_url
 	c2=urllib.urlencode(parameter_list)
 	c3=c1+ "?"+c2
 	print c3
 	r=urllib2.urlopen(c3).read()
 	#r = requests.get(announce_url, params=parameter_list)
 	print r
 	print "the tk\n"
 	print r.url
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
 

if __name__ == "__main__":
	abc = bencode.bdecode(open('kl.torrent', 'rb').read())
	get_peers(abc)
