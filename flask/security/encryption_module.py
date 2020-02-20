import base64
import hashlib

from Crypto import Random
from Crypto.Cipher import AES

KEY = "sg"


class AESCipher:
    def __init__(self):
        self.bs = 32
        self.key = hashlib.sha256(AESCipher.str_to_bytes(KEY)).digest()

    @staticmethod
    def str_to_bytes(data):
        u_type = type(b''.decode('utf8'))
        if isinstance(data, u_type):
            return data.encode('utf8')
        return data

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * AESCipher.str_to_bytes(chr(self.bs - len(s) % self.bs))

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, raw):
        raw = self._pad(AESCipher.str_to_bytes(raw))
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self.enc_convert(base64.b64encode(iv + cipher.encrypt(raw)).decode('utf-8'))

    def decrypt(self, enc):
        enc = self.dec_convert(enc)
        try:
            enc = base64.b64decode(enc)
        except:
            return 0

        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return self._unpad(cipher.decrypt(enc[AES.block_size:])).decode('utf-8')

    def enc_convert(self, url):
        url = url.replace('+', '-')
        url = url.replace('/', '_')
        return url

    def dec_convert(self, url):
        url = url.replace('-', '+')
        url = url.replace('_', '/')
        return url

    def extract_password(self, pw):
        password = ""
        salt = ""
        salt += pw[1] + pw[2] + pw[3]
        for i in range(0, len(pw)):
            if i != 1 and i != 2 and i != 3:
                password += pw[i]
        return password, salt

    def origin_password(self, pw, salt):
        password = ""
        for i in range(0, len(pw)):
            if i == 1:
                for j in range(0, 3):
                    password += salt[j]
            password += pw[i]
        return password

#test = AESCipher()
#a = test.extract_password("GdetBNer2DJahzYaG3gFiOZFO-D_gVIC9PuodI_cVtrdjuYxKZV4zRAMFurD3Rni")
#print(test.origin_password(a[0], a[1]))
#print(test.decrypt("GdetBNer2DJahzYaG3gFiOZFO-D_gVIC9PuodI_cVtrdjuYxKZV4zRAMFurD3Rni"))
#print(test.decrypt("ZQCi4xYLeYpK2y8R_fEa7G0wq0yaPNUWW7qFBpVliyzXVdvnIdfwsKWIzJn6oj0z"))