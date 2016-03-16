import unittest
import bencode
print bencode.bdecode(open('abc.torrent', 'rb').read())
