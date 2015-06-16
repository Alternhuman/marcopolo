from Crypto.Cipher import AES # encryption library
import base64
import string, random
import six

BLOCK_SIZE = 32
#http://stackoverflow.com/q/17534919/2628463
# the character used for padding--with a block cipher such as AES, the value
# you encrypt must be a multiple of BLOCK_SIZE in length.  This character is
# used to ensure that your value is always a multiple of BLOCK_SIZE
PADDING = '#'
# one-liner to sufficiently pad the text to be encrypted

pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * PADDING
# one-liners to encrypt/encode and decrypt/decode a string
# encrypt with AES, encode with base64
EncodeAES = lambda c, s: base64.b64encode(c.encrypt(pad(s)))
DecodeAES = lambda c, e: c.decrypt(base64.b64decode(e)).rstrip(PADDING)


def generate_secret(BLOCK_SIZE=32):
    if BLOCK_SIZE not in  (16, 24, 32):
        raise ValueError("BLOCK_SIZE must be 16, 24 or 32")
    return ''.join(random.choice(string.digits + string.ascii_letters) for _ in range(BLOCK_SIZE))
    

def create_token(uid, secret):
    if not isinstance(uid, int):
        raise ValueError("uid must be integer")

    uid = str(uid)

    # create a cipher object using the random secret
    cipher = AES.new(secret)
    return unicode(EncodeAES(cipher, uid))
    

def decrypt_token(token, secret):
    if not isinstance(token, six.string_types):
        token = str(token)

    cipher = AES.new(secret)
    # decode the encoded string
    return int(DecodeAES(cipher, token))

