import unittest
import bencode
abc = bencode.bdecode(open('hello.txt.torrent', 'rb').read())
str2 = "announce";
print abc
print abc['info']['length']
print abc['announce']
