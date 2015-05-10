import json, socket, sys

sys.path.append('/opt/marcopolo/')
from marco_conf.utils import Node

TIMEOUT = 4000

class Marco(object):
  def __init__(self):
    self.marco_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    self.marco_socket.settimeout(TIMEOUT*2/1000.0)
  
  def request_for(self, service):
    if sys.version_info[0] > 2:
      self.marco_socket.sendto(bytes(json.dumps({"Command": "Request-for", "Params":service}), 'utf-8'), ('127.0.1.1', 1338))
    else:
      self.marco_socket.sendto(bytes(json.dumps({"Command": "Request-for", "Params":service}).encode('utf-8')), ('127.0.1.1', 1338))

    error = None
    try:
      data, address = self.marco_socket.recvfrom(4096)
    except socket.timeout:
      error = True
    if error:
      raise MarcoTimeOutException('No connection to the resolver')

    error_parse = None
    try:
      nodes_arr = json.loads(data.decode('utf-8'))
    except ValueError:
      error_parse = True
    
    if error_parse:
      raise MarcoInternalError("Internal parsing error")
    
    nodes = set()
    for node_arr in nodes_arr:
      node = Node()
      node.address = node_arr["Address"]
      node.services = []
      node.services += node_arr["Params"]
      nodes.add(node)
    return nodes


  def marco(self, max_nodes=None, exclude=[], timeout=None):
    if sys.version_info[0] < 3:
      self.marco_socket.sendto(bytes(json.dumps({"Command": "Marco", 
                                                 "max_nodes": max_nodes,
                                                 "exclude":exclude,
                                                 "timeout":timeout}).encode('utf-8')), ('127.0.1.1', 1338))
    else:
      self.marco_socket.sendto(bytes(json.dumps({"Command": "Marco", 
                                                 "max_nodes": max_nodes,
                                                 "exclude":exclude,
                                                 "timeout":timeout}), 'utf-8'), ('127.0.1.1', 1338))
    
    
    error = None
    try:
      data = self.marco_socket.recv(4096)
    except socket.timeout:
      error = True
    if error:
      raise MarcoTimeOutException("No connection to the resolver")

    error_parse = None
    try:
      nodes = json.loads(data.decode('utf-8'))
    except ValueError:
      error_parse = True
    
    if error_parse:
      raise MarcoInternalError("Internal parsing error")
    
    return nodes


  def services(node, timeout=None):
    if sys.version_info[0] < 3:
      self.marco_socket.sendto(bytes(json.dumps({"Command": "Services",
                                                 "node": node,
                                                 "timeout":timeout}).encode('utf-8')), ('127.0.1.1', conf.POLOPORT))
    else:
      self.marco_socket.sendto(bytes(json.dumps({"Command": "Services",
                                                 "node": node,
                                                 "timeout":timeout}), 'utf-8'), ('127.0.1.1', conf.POLOPORT))

    error = None
    try:
      data = self.marco_socket.recv(4096)
    except socket.timeout:
      error = True
    
    if error:
      raise MarcoTimeOutException("No connection to the resolver")

    error_parse = None
    try:
      services_list = json.loads(data.decode('utf-8'))
    except ValueError:
      error_parse = True
    
    if error_parse:
      raise MarcoInternalError("Internal parsing error")
    
    return services_list

class MarcoTimeOutException(Exception):
  pass

class MarcoInternalError(Exception):
  pass

#Todo: see sphinx