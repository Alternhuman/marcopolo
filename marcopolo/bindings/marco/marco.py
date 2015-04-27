import json, socket, sys

sys.path.append('/opt/marcopolo/')
from marco_conf.utils import Node

TIMEOUT = 4000

class Marco(object):
  def __init__(self):
    self.marco_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    self.marco_socket.settimeout(TIMEOUT*2/1000.0)
  
  def request_for(self, service):
    self.marco_socket.sendto(bytes(json.dumps({"Command": "Request-for", "Params":service}), 'utf-8'), ('127.0.1.1', 1338))

    error = None
    try:
      data, address = self.marco_socket.recvfrom(4096)
    except socket.timeout:
      error = True
    if error:
      raise MarcoTimeOutException('No connection to the resolver')

    nodes_arr = json.loads(data.decode('utf-8'))

    nodes = set()
    for node_arr in nodes_arr:
      node = Node()
      node.address = node_arr["Address"]
      node.services = []
      node.services += node_arr["Params"]
      nodes.add(node)
    return nodes


  def marco(self):
    self.marco_socket.sendto(bytes(json.dumps({"Command": "Marco"}), 'utf-8'), ('127.0.1.1', 1338))
    try:
      data = self.marco_socket.recv(4096)
    except socket.timeout:
      if args.shell:
        print("")
      else:
        print("No response from resolver")
      exit(1)
    nodes = json.loads(data.decode('utf-8'))

    return nodes
class MarcoTimeOutException(Exception):
  pass

#Todo: see sphinx