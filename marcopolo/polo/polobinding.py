from __future__ import with_statement
from __future__ import absolute_import
from twisted.internet.protocol import DatagramProtocol

from io import open
import os
from os import makedirs, path
from os.path import isfile

import json, logging
import pwd, grp
import re

import socket
import six

from marcopolo.polo import conf

def sanitize_path(path_str):
    """
    Prevents unwanted directory traversing and other bash vulnerabilities.

    :param str path_str: The path to be sanitized.

    :returns: The sanitized path.

    :rtype: str
    """
    return path.normpath("/"+path_str).lstrip('/')

class PoloBinding(DatagramProtocol):

    def __init__(self, offered_services={}, user_services={}, multicast_groups=conf.MULTICAST_ADDRS, verify_regexp=conf.VERIFY_REGEXP):
        """
        Creates the ``PoloBinding`` instance with the data structures to work with.
        If defined, the ``offered_services`` and ``user_services`` variables will be treated 
        as references to a dictionaries (i.e. the values will be modified, but the object reference 
        will never be altered).
        
        :param dict offered_services: A dictionary which comprises all the dictionaries \
        passed to the ``offered_services`` param in the Polo instances. That way the services \
        can be altered by both parties
        
        :param dict user_services: A dictionary of all the user services dictionaries (the key is multicast
            group and the value is the list of user dictionaries passed to the param ``user_services``.
        
        :param str multicast_group: The IPv4 address of the multicast group to join to. **Important**: The multicast_addr is not validated until the reactor is started.
        
        :param str verify_regexp: Regular expression used to verify an user service.
        """
        #super(PoloBinding, self).__init__()
        self.offered_services = offered_services
        self.user_services = user_services
        self.verify = re.compile(verify_regexp)#re.compile('^([\d\w]+):([\d\w]+)$')
        self.multicast_groups = multicast_groups


    def startProtocol(self):
        """
        Starts the binding and adds an entry in the log file
        """
        logging.info("Starting binding")

    def datagramReceived(self, datagram, address):
        """
        Receives datagrams from bindings, and verifies the `Command` field.
        It emits a response based on the value (if necessary)

        :param bytes datagram: The byte stream with the message

        :param tuple address: A tuple with the requesting address and port
        """
        logging.debug("Datagram received")        
        datos = datagram.decode('utf-8')
        try:
            datos_dict = json.loads(datos)
        except ValueError:
            self.transport.write(json.dumps({"Error":"Malformed JSON"}).encode('utf-8'), address)
            logging.debug("Malformed JSON")
        
        if datos_dict.get("Command") is None:
            self.transport.write(json.dumps({"Error":"Missing command"}).encode('utf-8'), address)
            logging.debug("Missing command")
            return
        command = datos_dict["Command"]
        if command == 'Register':
            logging.debug("Register service")
            args = datos_dict.get("Args", {})
            self.publish_service(address,
                                args.get("service", ''), 
                                args.get("uid", -1),
                                multicast_groups=args.get("multicast_groups", conf.MULTICAST_ADDRS),
                                permanent=args.get("permanent", False),
                                root=args.get("root", False))
        elif command == 'Unpublish':
            args = datos_dict.get("Args", {})
            self.unpublish_service(address,
                                    args.get("service", ''),
                                    args.get("uid", -1),
                                    multicast_groups=args.get("multicast_groups", set()),
                                    delete_file=args.get("delete_file", False)
                                    )
            
        else:
            #If any of the previous conditions is satisfied, the request is considered malformed
            self.transport.write(self.write_error("Malformed request. Commands missing").encode('utf-8'), address)
        
    def write_error(self, error):
        """
        Creates an `Error` return value

        :returns: A JSON-encoded string
        :rtype: str
        """
        return json.dumps({"Error": error})

    def publish_service(self, address, service, uid, multicast_groups=conf.MULTICAST_ADDRS, permanent=False, root=False):
        """
        Registers a service during execution time.

        :param tuple address: A tuple with the requesting address and port
        
        :param str service: Indicates the unique identifier of the service.
        
            If `root` is true, the published service will have the same identifier as the value of the parameter. Otherwise, the name of the user will be prepended (`<user>:<service>`).
        
        :param int uid: The unique user identifier

        :param set multicast_groups: Indicates the groups where the service shall be published.
        
            Note that the groups must be defined in the polo.conf file, or otherwise the method will throw an exception.
        
        :param bool permanent: If set to true a file will be created and the service will be permanently offered until the file is deleted.
        
        :param bool root: Stores the file in the marcopolo configuration directory.
        
            This feature is only available to privileged users, by default root and users in the marcopolo group.
        """

        error = False # Python does not allow throwing an exception insided an exception, so we use a flag
        reason = ""
        #Verification of services
        if not isinstance(service, six.string_types):
            error = True
            reason = "Service must be a string"

        #The service must be something larger than 1 character
        if service is None or len(service) < 1:
            error = True
            reason = "Must be larger than 1"

        if error:
            logging.debug(error)
            self.transport.write(self.write_error("The name of the service %s is invalid: %s" % (service, reason)).encode('utf-8'), address)
            return
        error = False
        faulty_ip = ''
        #The IP addresses must be represented in valid dot notation and belong to the range 224-239
        for ip in multicast_groups:
            #The IP must be a string
            if not isinstance(ip, six.string_types):
                error = True
                faulty_ip = ip
                reason = "IP must be a string"
                break

            #Instead of parsing we ask the socket module
            try:
                socket.inet_aton(ip)
            except socket.error:
                error = True
                faulty_ip = ip
                reason = "Wrong IP format"
                break
            
            try:
                first_byte = int(re.search(r"\d{3}", ip).group(0))
                if first_byte < 224 or first_byte > 239:
                    error = True
                    faulty_ip = ip
            except (AttributeError, ValueError):
                error = True
                faulty_ip = ip
                reason = "IP is not of class D"
                break

            if ip not in self.multicast_groups:
                error = True
                faulty_ip = ip
                reason = "The instance is not a member of this group"
                break

        if error:
            logging.debug(reason)
            try:
                self.transport.write(self.write_error("Invalid multicast group address '%s': %s" % (str(faulty_ip), reason)).encode('utf-8'), address)
            except Exception:
                self.transport.write(self.write_error("Invalid multicast group address").encode('utf-8'), address)
            return
        
        if type(permanent) is not bool:
            logging.debug("Permanent must be boolean")
            self.transport.write(self.write_error("permanent must be boolean").encode('utf-8'), address)
            return
        
        if type(root) is not bool:
            return self.transport.write(self.write_error("root must be boolean").encode('utf-8'), address)

        #UID verification
        user = self.validate_user(uid)
        if user is None:
            self.transport.write(self.write_error("wrong user").encode('utf-8'), address)
            return
        
        #Final entry with all service parameters
        service_dict = {}
        service_dict["id"] = service
        #TODOservice_dict["params"] ={} Add parameters
        service_dict["groups"] = multicast_groups
        
        #Root service
        error = None
        error_reason = ""
        if root is True:
            if not self.is_superuser(user):
                self.transport.write(self.write_error("Permission denied").encode('utf-8'), address)
                return
            
            for group in multicast_groups:
                #Only root or members of the `marcopolo` group can publish root services
                
                if service in [s['id'] for s in self.offered_services[group]]:
                    error_reason = self.write_error("Service %s already exists" % service)
                    #self.transport.write(self.write_error("Service %s already exists" % service).encode('utf-8'), address)
                    error = True
                    continue
                
                if permanent is True:

                    services_dir = path.join(conf.CONF_DIR, conf.SERVICES_DIR)
                    if not path.exists(services_dir):
                        makedirs(services_dir)
                        os.chown(services_dir, 0, grp.getgrnam(conf.GROUP_NAME).gr_gid)

                    service_file = sanitize_path(service)
                    if path.isfile(path.join(services_dir, service_file)):
                        error_reason = self.write_error("Permanent service %s already exists" % service)
                        #self.transport.write(self.write_error("Permanent service %s already exists" % service).encode('utf-8'), address)
                        error = True
                        continue

                    try:
                        f = open(path.join(services_dir, service_file), 'w')
                        f.write(json.dumps(service_dict))
                        os.fchown(f.fileno(), user.pw_uid, user.pw_gid)
                        f.close()
                        service_dict["file"] = service_file
                    except Exception as e:
                        error_reason = self.write_error("Could not write file")
                        #self.transport.write(self.write_error("Could not write file").encode('utf-8'), address)
                        error = True
                        continue

                
                self.offered_services[group].append({"id":service, "permanent":permanent})
            else:
                service_dict["permanent"] = permanent
                
                if not error:
                    self.transport.write(json.dumps({"OK":service}).encode('utf-8'), address)
                else:
                    self.transport.write(error_reason.encode('utf-8'), address)
            return

        else:
            error = False
            for group in multicast_groups:
                
                if self.user_services[group].get(user.pw_name, None):
                    if service in [s['id'] for s in  self.user_services[group][user.pw_name]]:
                        self.transport.write(self.write_error("Service already exists").encode('utf-8'), address)
                        error = True
                        continue

                folder = user.pw_dir
                deploy_folder = path.join(folder, conf.POLO_USER_DIR)
                
                if permanent is True:
                    if not path.exists(deploy_folder):
                        makedirs(deploy_folder)
                        os.chown(deploy_folder, user.pw_uid, user.pw_gid)
                    
                    service_file = sanitize_path(service)
                    if path.isfile(path.join(deploy_folder, service_file)):
                        self.transport.write(self.write_error("Service already exists").encode('utf-8'), address)
                        #TODO: if unpublished and not deleted, this will be true
                        error = True
                        continue
                    
                    try:
                        f = open(path.join(deploy_folder, service_file), 'w')
                        f.write(json.dumps(service_dict))
                        os.fchown(f.fileno(), user.pw_uid, user.pw_gid)
                        f.close()
                    except Exception as e:
                        logging.debug(e)
                        self.transport.write(self.write_error("Could not write service file").encode('utf-8'), address)
                        error = True
                        continue

                if self.user_services[group].get(user.pw_name, None) is None:
                    self.user_services[group][user.pw_name] = []

                self.user_services[group][user.pw_name].append({"id":service, "permanent":permanent})
                logging.debug("Publishing user service %s in group %s" % (service, group))
            else:
                if not error:
                    self.transport.write(json.dumps({"OK":user.pw_name+":"+service}).encode('utf-8'), address)

    def unpublish_service(self, address, service, uid, multicast_groups=conf.MULTICAST_ADDRS, delete_file=False):
        """
        Removes a service from the offered services structures and all associated files, upon request.

        :param tuple address: A tuple with the requesting address and port.

        :param str service: The id of the service to delete.

        :param int uid: The uid of the requesting user.

        :param list multicast_groups: The list of multicast_groups to delete the service from.\
         If not defined, the service is removed from all groups.

        :param bool delete_file: If set to ``True`` and the service is of type permanent,\
         the service file is deleted. If the service is not permanent the parameter is ignored. 
        """
        if len(multicast_groups) < 1:
            multicast_groups = conf.MULTICAST_ADDRS
        #Determine whether it is a root or a user service
        #The IP addresses must be represented in valid dot notation and belong to the range 224-239
        error = None
        reason = ""
        for ip in multicast_groups:
            #The IP must be a string
            if not isinstance(ip, six.string_types):
                error = True
                faulty_ip = ip
                reason = "IP must be a string"
                break
            
            #Instead of parsing we ask the socket module
            try:
                socket.inet_aton(ip)
            except socket.error:
                error = True
                faulty_ip = ip
                reason = "Wrong IP format"
                break
            
            try:
                first_byte = int(re.search(r"\d{3}", ip).group(0))
                if first_byte < 224 or first_byte > 239:
                    error = True
                    faulty_ip = ip
            except (AttributeError, ValueError):
                error = True
                faulty_ip = ip
                reason = "IP is not of type multicast"
                break

            if ip not in self.multicast_groups:
                error = True
                faulty_ip = ip
                reason = "The instance is not a member of this group"
                break

        if error is not None:
            self.transport.write(self.write_error("Invalid multicast group address '%s': %s" % (str(faulty_ip), reason)).encode('utf-8'), address)
            return
        #self.transport

        if len(set(multicast_groups) - (set(conf.MULTICAST_ADDRS) & set(multicast_groups))) > 0:
            self.transport.write(self.write_error("The group %s is not available" % multicast_groups[0]).encode('utf-8'), address)
            return

        user = self.validate_user(uid)

        if user is None:
            self.transport.write(self.write_error("wrong user").encode('utf-8'), address)
            return
        
        if self.verify.match(service):
            #user service
            try:
                user, service_name = self.verify.match(service).groups()
                user_pwd = pwd.getpwnam(user)
            except (IndexError, ValueError):
                self.transport.write(self.write_error("Invalid formatting").encode('utf-8'), address)
                return
            if user_pwd is None:
                self.transport.write(self.write_error("Invalid user").encode('utf-8'), address)
                return
            for group in multicast_groups:
                if self.user_services[group].get(user, None) is not None:
                    match = next((s for s in self.user_services[group][user] if s['id'] == service_name), None)
                    if match:
                        is_permanent = match.get("permanent", False)
                        
                        if delete_file and is_permanent:
                            folder = user_pwd.pw_dir
                            deploy_folder = path.join(folder, conf.POLO_USER_DIR)
                            if path.exists(deploy_folder) and isfile(path.join(deploy_folder, service_name)):
                                
                                try:
                                    os.remove(path.join(deploy_folder, service_name))
                                except Exception as e:
                                    pass
                            else:
                                self.transport.write(self.write_error("Could not find service file").encode('utf-8'), address)
                        try:
                            self.user_services[group][user].remove(match)
                        except ValueError:
                            pass
                    else:
                        self.transport.write(self.write_error("Could not find service").encode('utf-8'), address)
                        return
                else:
                    self.transport.write(self.write_error("Could not find service").encode('utf-8'), address)
                    return
            else:
                self.transport.write(json.dumps({"OK":service}).encode('utf-8'), address)
                return
        else:
            #root service
            error_str = ""
            for group in multicast_groups:
                match = next((s for s in self.offered_services[group] if s['id'] == service), None)
                if match:
                    is_permanent = match.get("permanent", False)
                    
                    if delete_file and is_permanent:
                        folder = path.join(conf.CONF_DIR, conf.SERVICES_DIR)
                    
                        if path.exists(folder) and isfile(path.join(folder, service)):
                            with open(path.join(folder, service), 'r+') as f:
                                file_dict = json.load(f)
                                if len(file_dict.get("groups", [])) == 0:
                                    try:
                                        f.close()
                                        os.remove(path.join(folder, service))
                                    except Exception as e:
                                        self.transport.write(self.write_error("Internal error during processing of file").encode('utf-8'), address)
                                else:
                                    groups = file_dict.get("groups", [])
                                    if len(groups) > 0:
                                        try:
                                            groups.remove(group)
                                        except ValueError:
                                            pass
                                    
                                    if len(groups) == 0:
                                        try:
                                            f.close()
                                            os.remove(path.join(folder, service))
                                        except Exception as e:
                                            self.transport.write(self.write_error("Internal error during processing of file").encode('utf-8'), address)
                                    else:
                                        f.seek(0, 0)
                                        f.truncate()
                                        json.dump(file_dict, f)

                        else:
                            self.transport.write(self.write_error("Could not find service file").encode('utf-8'), address)
                    try:
                        self.offered_services[group].remove(match)
                    except ValueError:
                        pass
                else:
                    if delete_file:
                        folder = path.join(conf.CONF_DIR, conf.SERVICES_DIR)
                        if path.exists(folder) and isfile(path.join(folder, service)):
                            with open(path.join(folder, service), 'r+') as f:
                                file_dict = json.load(f)
                                if len(file_dict.get("groups", [])) < 1:
                                    try:
                                        f.close()
                                        os.remove(path.join(folder, service))
                                    except Exception as e:
                                        self.transport.write(self.write_error("Internal error during processing of file").encode('utf-8'), address)
                                else:
                                    groups = file_dict.get("groups", [])
                                    if len(groups) > 0:
                                        try:
                                            groups.remove(group)
                                        except ValueError:
                                            pass
                                    f.seek(0, 0)
                                    f.truncate()
                                    json.dump(file_dict, f)
                    
                        else:
                            self.transport.write(self.write_error("Could not find service").encode('utf-8'), address)
                            return
                try:
                    self.offered_services[group].remove(match)
                except ValueError as e:
                    pass
            else:
                try:
                    self.transport.write(json.dumps({"OK":0}).encode('utf-8'), address)
                except ValueError:
                    pass
    
    def validate_user(self, uid):
        """
        Returns a `pwd` structure if the uid is present in the passwd database.
        Otherwise `None` is returned
        
        :param string uid: The user identifier of the service

        """

        if type(uid) != type(0):
            return None

        if uid < 0:
            return None
        try:
            user = pwd.getpwuid(uid)
        except KeyError:
            return None
        return user

    def is_superuser(self, user):
        """
        Returns `True` if the user is a 'superuser' (it is root or it a member of the `marcopolo` group)
        
        :param string user: `pwd` structure with all the information from the user
        
        """
        
        groups = [g.gr_name for g in grp.getgrall() if user.pw_name in g.gr_mem]
        gid = user.pw_gid
        groups.append(grp.getgrgid(gid).gr_name)
        
        return 'marcopolo' in groups or user.pw_uid == 0
