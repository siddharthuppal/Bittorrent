import unittest
import bencode
abc = bencode.bdecode(open('hello.txt.torrent', 'rb').read())
print abc
