import unittest
import bencode
abc = bencode.bdecode(open('try.torrent', 'rb').read())
str2 = "announce";
print abc
print abc['comment']


n=len(abc['info']['files']);

for i in range(n):
	print abc['info']['files'][i]['path']
	print abc['info']['files'][i]['length']
	

print abc['info']['piece length']
print abc['info']['name']

#print abc['info']['pieces']


print abc['creation date']
print abc['announce-list']
print abc['announce']
