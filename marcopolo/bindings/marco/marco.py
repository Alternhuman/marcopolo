import json, socket, sys

sys.path.append('/opt/marcopolo/')
from marco_conf.utils import Node

TIMEOUT = 4000

class Marco(object):
  def __init__(self):
    self.marco_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    self.marco_socket.settimeout(TIMEOUT*2/1000.0)
  
  def request_for(self, service, node=None, max_nodes=None, exclude=[], params={}, timeout=None):
    """
    **C: struct node * request_for(const char * service)**

    **C++: std::vector<std::string> request_for(wchar_t* service)**

    **Java: ArrayList<Nodo> request_for(String service)**

    Request all nodes offering a service.
    
    :param string service: The name of the service to look for

    :param string node: If defined, the function acts as a probe to check if the given node has the service.

    :param int timeout:  If set to an integer, the resolver will override its local timeout parameter and use this instead for the resolving process.

    Please note that the function will block the execution of the thread until the timeout in the Marco configuration file is triggered. Though this should not be a problem for most application, it is worth knowing.
    
    :returns: A list of nodes offering the requested service.

    :rvalue: set()

    :raise:
      :MarcoTimeOutException: If no connection can be made to the local resolver (probably due a failure start of the daemon).

    """
    error = None
    try:
      if sys.version_info[0] > 2:
        self.marco_socket.sendto(bytes(json.dumps({"Command": "Request-for", 
                                                 "Params":service, 
                                                 "node":node, 
                                                 "max_nodes":max_nodes, 
                                                 "exclude":exclude, 
                                                 "params":params, 
                                                 "timeout":timeout}), 'utf-8'), ('127.0.1.1', 1338))
      else:
        self.marco_socket.sendto(bytes(json.dumps({"Command": "Request-for", 
                                                "Params":service, 
                                                "node":node, 
                                                "max_nodes":max_nodes, 
                                                "exclude":exclude, 
                                                "params":params, 
                                                "timeout":timeout}).encode('utf-8')), ('127.0.1.1', 1338))
    except ValueError as e:
      error = True
    if error:
      raise MarcoTimeOutException("Bad parameters")

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
      node.params = node_arr["Params"]

      nodes.add(node)
    return nodes


  def marco(self, max_nodes=None, exclude=[], params={}, timeout=None, retries=0):
    """
    **C struct node * marco(int timeout)**

    **C++ std::vector<node> marco(int timeout)**

    **Java ArrayList<Node> marco(int timeout)**

    Sends a `marco` message to all nodes, which reply with a Polo message. Upon receiving all responses (those which arrived before the timeout), a collection of the response information is returned.
    
    :param int max_nodes: Maximum number of nodes to be returned. If set to `None`, no limit is applied.

    :param list exclude: List of nodes to be excluded from the returned ValueError.

    :param int timeout: If set, overrides the default timeout value.

    :param int retries: If set to a value greater than 0, retries the *retries* times if the first attempt is unsuccessful

    :returns: A list of all responding nodes.
    """

    if sys.version_info[0] < 3:
      self.marco_socket.sendto(bytes(json.dumps({"Command": "Marco", 
                                                 "max_nodes": max_nodes,
                                                 "exclude":exclude,
                                                 "params":params,
                                                 "timeout":timeout}).encode('utf-8')), ('127.0.1.1', 1338))
    else:
      self.marco_socket.sendto(bytes(json.dumps({"Command": "Marco", 
                                                 "max_nodes": max_nodes,
                                                 "exclude":exclude,
                                                 "params":params,
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
    
    nodes_set = set()
    for node in nodes:
      n = Node()
      n.address = node["Address"]
      n.params = node["Params"]
      nodes_set.add(n)

    return nodes_set

  def request_one_for(self, exclude=[], timeout=None):
    """
    Returns one node picked at random from the responses (more precisely, the first replying node) or the one which first satisfies the given exclusion criteria. This function is equivalent to ``request_for`` with max_nodes=1

    :param list exclude: List of nodes not to be included in the response.

    :param int timeout: If set, overrides the default timeout value.

    :returns: The picked node

    :rvalue: Node
    """

  def services(self, node, timeout=None):
    """
    Returns all the services available in the node identified by the given ``node``. In the event that the node does not reply to the response, a exception will be raised.
    
    **C struct service * services(char * node, int timeout)**

    **C++ std::vector<service> services(std::string node, int timeout)**

    **Java ArrayList<Service> services(string node, int timeout)**

    :param string node: The node to ask

    :param int timeout: If set, overrides the default timeout value.

    :returns: A list of the services offered by a node.

    :rvalue: set()

  """

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

  def request_multi(self, services, max_nodes=None, exclude=[], params={}, timeout=None):
    pass

class MarcoTimeOutException(Exception):
  pass

class MarcoInternalError(Exception):
  pass

#Todo: see sphinx