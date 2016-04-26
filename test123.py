import unittest
import urllib2
abc = urllib2.urlopen("http://google.com").read()
print abc
