import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from datetime import datetime

class AESAlgorithm(object):

    def __init__(self, private_key): 
        self.bs = 32
        self.key = hashlib.sha256(private_key.encode()).digest()

    def encrypt(self, raw_string):
        raw_string = self.padding(raw_string)
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw_string))

    def decrypt(self, encrypted_string):
        encrypted_string = base64.b64decode(encrypted_string)
        iv = encrypted_string[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.unpadding(cipher.decrypt(encrypted_string[AES.block_size:])).decode('utf-8')

    def padding(self, s):
        return s + (self.bs - len(s) % self.bs) * chr(self.bs - len(s) % self.bs)

    @staticmethod
    def unpadding(s):
        return s[:-ord(s[len(s)-1:])]


#aes_algo = AESAlgorithm("rohit123")
#encrypted_text = aes_algo.encrypt("Rohit Pawar")
#print(encrypted_text)
#print(aes_algo.decrypt(encrypted_text))
