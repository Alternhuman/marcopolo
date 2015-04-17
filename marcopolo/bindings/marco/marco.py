import json, socket, sys

sys.path.append('/opt/marcopolo/')
from marco_conf.utils import Node

TIMEOUT = 4000

class Marco(object):
  def __init__(self):
    self.marco_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    self.marco_socket.settimeout(TIMEOUT/1000.0)
  def request_for(self, service):
    self.marco_socket.sendto(bytes(json.dumps({"Command": "Request-for", "Params":service}), 'utf-8'), ('127.0.1.1', 1338))
    error = None
    try:
      data = self.marco_socket.recv(4096)
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

class MarcoTimeOutException(Exception):
  pass

"""if __name__ == "__main__":
  marco_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
  marco_socket.settimeout(TIMEOUT/1000.0)

  print([n.address[0] for n in request_for("statusmonitor")])
  marco = Marco()
  print([n.address[0] for n in marco.request_for("statusmonitor")])"""