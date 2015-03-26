from os.path import dirname, join
config_dir = dirname(__file__)

PORT = 5666
CERT_FILE = join(config_dir, 'malote.pem')
KEY_FILE = join(config_dir, 'malote.key')
MINION_CERT_FILE = join(config_dir, 'minion.pem')
COOKIE_SIGN_KEY = '8uogiue8 rxhce rxihpcuru eoitrao0'
PASSWORD = 'gato'
