# import base64
# import hashlib
# from Crypto.Cipher import AES
# from django.conf import settings
#
#
# # ############################################################
# # - BLOCK_SIZE is the boundary to which we round our data to.
# # - PADDING is the character that we use to padd the data.
# _BLOCK_SIZE = 32
# _PADDING = '@'
#
# # generate the secret key
# _ENCRYPT_KEY = settings.ENCRYPT_KEY
#
# # one-liner to sufficiently pad the text to be encrypted
# # Data to be encrypted should be on 16, 24 or 32 byte boundaries.
# # So if you have 'hi', it needs to be padded with 30 more characters
# # to make it 32 bytes long. Similarly if something is 33 bytes long,
# # 31 more bytes are to be added to make it 64 bytes long which falls
# # on 32 boundaries.
# _pad = lambda s: s + (_BLOCK_SIZE - len(s) % _BLOCK_SIZE) * _PADDING
#
# # create a cipher object using the secret
# _cipher = AES.new(_pad(_ENCRYPT_KEY)[:32])
#
# # Encrypts the given data with given secret key.
# EncodeAES = lambda s: None if s is None else base64.b64encode(_cipher.encrypt(_pad(s))).decode()
#
# # Decrypts the given data with given key.
# DecodeAES = lambda e: None if e is None else _cipher.decrypt(base64.b64decode(e.encode())).decode().rstrip(_PADDING)
#
# Hash = lambda s: None if s is None else hashlib.sha256(s.encode()).hexdigest()
#
# MD5_Hash = lambda s: None if s is None else hashlib.md5(s.encode()).hexdigest()

import base64
import hashlib
from Crypto import Random
from Crypto.Cipher import AES
from django.conf import settings

# ############################################################
# - BLOCK_SIZE is the boundary to which we round our data to.
# - PADDING is the character that we use to padd the data.


Hash = lambda s: None if s is None else hashlib.sha256(s.encode()).hexdigest()

__key__ = hashlib.sha256(b'16-character key').digest()

_INITIALIZATION_VECTOR = settings.INITIALIZATION_VECTOR


def EncodeAES(raw):
    BS = AES.block_size
    pad = lambda s: s + (BS - len(s) % BS) * chr(BS - len(s) % BS)

    raw = base64.b64encode(pad(raw).encode('utf8'))
    iv = bytes(_INITIALIZATION_VECTOR, 'utf-8')[:AES.block_size]
    cipher = AES.new(key=__key__, mode=AES.MODE_CFB, iv=iv)
    return base64.b64encode(iv + cipher.encrypt(raw)).decode('utf8')


def DecodeAES(enc):
    unpad = lambda s: s[:-ord(s[-1:])]

    enc = base64.b64decode(enc)
    iv = enc[:AES.block_size]
    cipher = AES.new(__key__, AES.MODE_CFB, iv)
    return unpad(base64.b64decode(cipher.decrypt(enc[AES.block_size:])).decode('utf8'))
