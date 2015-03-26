from os.path import dirname, join
config_dir = dirname(__file__)

MALOTE_ADDR = 'localhost'
MALOTE_PORT = 5666

ASSETS_DIR = '/tmp/bomba_descomprimida'

PORT = 5665
CERT_FILE = join(config_dir, 'minion.pem')
KEY_FILE = join(config_dir, 'minion.key')
MALOTE_CERT_FILE = join(config_dir, 'malote.pem')
