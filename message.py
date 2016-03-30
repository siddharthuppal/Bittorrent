def number_to_bytes(number):  #returns a number 4 bytes long
     if number < 255:
         length = '\x00\x00\x00' + chr(number)
     elif number < 256**2:
         length = '\x00\x00' + chr((number)/256) + chr((number) % 256)
     elif number < 256**3:
         length = ('\x00'+ chr((number)/256**2) + chr(((number) % 256**2) / 256) +
             chr(((number) % 256**2) % 256))
     else:
         length = (chr((number)/256**3) + chr(((number)%256**3)/256**2) + chr((((number)%256**3)%256**2)/256) + chr((((number)%256**3)%256**2)%256))
     return length
 
def bytes_to_number(bytestring):  #assumed to be 4 bytes long
     number = 0
     i = 3
     for byte in bytestring:
         number += ord(byte) * 256**i
         i -= 1
     return number
 
def parse_message_from_response(response):
     if len(response) < 4:  #don't have full message
         return None, response
     length = bytes_to_number(response[0:4]) + 4  #length indicated by the first 4 bytes + 4 for those first 4 bytes
     bytestring = response[:length]
     if len(response) < length:   #don't have full message, so send back and wait to be combined with rest of message
         return None, response
     elif response[0:4] == '\x00\x00\x00\x00':  #no msg_id
         message_obj = KeepAlive(response=bytestring)
     else:
         result = {
           '\x00': lambda: Choke(response=bytestring),
           '\x01': lambda: Unchoke(response=bytestring),
           '\x02': lambda: Interested(response=bytestring),
           '\x03': lambda: NotInterested(response=bytestring),
           '\x04': lambda: Have(response=bytestring),
           '\x05': lambda: Bitfield(response=bytestring),
           '\x06': lambda: Request(response=bytestring),
           '\x07': lambda: Piece(response=bytestring),
           '\x08': lambda: Cancel(response=bytestring),
           '\x09': lambda: Port(response=bytestring),
         }[response[4]]()     #response[4] is the msg_id
         message_obj = result
         #print repr(message_obj)
     response = response[length:]
     return message_obj, response
 
class Handshake(object):
     """Represents a handshake object"""
     def __init__(self,*args):
         if len(args) == 1: self.__setup1(*args)
         elif len(args) == 2: self.__setup2(*args)  
         
     def __setup1(self,payload):
         self.pstrlen = payload[0]
         self.pstr = payload[1:20]  #assuming that pstrlen will be 19; might not be true (if in another protocol)
         self.reserved = payload[20:28]
         self.info_hash = payload[28:48]
         self.peer_id = payload[48:68]
 
     def __setup2(self,info_hash,peer_id):
         self.pstrlen = chr(19)
         self.pstr = "BitTorrent protocol"
         self.reserved = "\x00\x00\x00\x00\x00\x00\x00\x00"
         #self.reserved = "00000000"
         self.info_hash = info_hash
         self.peer_id = peer_id

 
     def __repr__(self):
         return self.pstrlen+self.pstr+self.reserved+self.info_hash+self.peer_id
 
     def __len__(self):
         return 49+ord(self.pstrlen)


class Message(object):
     """This is for everything but Handshake
         If you subclass this, you should provide class attributes for:
         protocol_args     (if not implemented, will use base class - [])
         protocol_extended (if not implemented, will use base class - None)
         msg_id (this should be a single byte)
     """
     protocol_args = []
     protocol_extended = None
 
     def __init__(self,**kwargs):
         if 'response' in kwargs:
             self.__setup_from_bytestring(kwargs['response'])
         elif set(self.protocol_args + ([self.protocol_extended] if self.protocol_extended else [])) == set(kwargs.keys()):
             self.__setup_from_args(kwargs)
         else:
             print 'stuff from message class', set(self.protocol_args + [self.protocol_extended] if self.protocol_extended else [])
             print 'kwargs', set(kwargs.keys())
             raise Exception("Bad init values")
 
     def __setup_from_bytestring(self, bytestring):
         self.msg_length = bytestring[0:4]
         if len(bytestring) > 4:
             msg_id = bytestring[4]
         else:
             msg_id = ''
         assert self.msg_id == msg_id, "Message ID's do not match."
         payload = bytestring[5:]
         for arg_name in self.protocol_args:
             setattr(self, arg_name, payload[:4])
             payload = payload[4:]
         if self.protocol_extended:
             setattr(self, self.protocol_extended, payload)
 
     def __setup_from_args(self, kwargs):
         for arg_name in self.protocol_args:
             setattr(self, arg_name, kwargs[arg_name])
         if self.protocol_extended:
             setattr(self, self.protocol_extended, kwargs[self.protocol_extended])
         if isinstance(self, KeepAlive):
             self.msg_length = number_to_bytes(sum([len(x) for x in kwargs.values()]))
         else:
             self.msg_length = number_to_bytes(sum([len(x) for x in kwargs.values()]) + 1)
 
     def __repr__(self):
         s = ''
         s += self.msg_length
         s += self.msg_id
         for arg_name in self.protocol_args:
             getattr(self, arg_name)
         if self.protocol_extended:
             getattr(self, self.protocol_extended)
         return repr(s)
 
     def __len__(self):
         return bytes_to_number(self.msg_length) + 4
 
 
class KeepAlive(Message):
     msg_id = ''
 
class Choke(Message):
     msg_id = '\x00'
 
class Unchoke(Message):
     msg_id = '\x01'
 
class Interested(Message):
     msg_id = '\x02'
 
class NotInterested(Message):
     msg_id = '\x03'
 
class Have(Message):
     protocol_args = ['index']
     msg_id = '\x04'
 
class Bitfield(Message):
     protocol_extended = 'bitfield'
     msg_id = '\x05'
 
class Request(Message):
     protocol_args = ['index','begin','length']
     msg_id = '\x06'
     
class Piece(Message):
     protocol_args = ['index','begin']
     protocol_extended = 'block'
     msg_id = '\x07'
 
class Cancel(Message):   
     protocol_args = ['index','begin','length']
     msg_id = '\x08'
 
class Port(Message):
     protocol_extended = 'listen_port'
     msg_id = '\x09'
