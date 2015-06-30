from __future__ import with_statement
from __future__ import absolute_import
from twisted.internet.protocol import DatagramProtocol, Protocol, Factory

from io import open
import os
from os import makedirs, path
from os.path import isfile

import json, logging, re
import pwd, grp, stat

import socket
import six

from marcopolo.marco_conf import utils
from marcopolo.polo import conf, tokenprovider

def sanitize_path(path_str):
    """
    Prevents unwanted directory traversing and other bash vulnerabilities.

    :param str path_str: The path to be sanitized.

    :returns: The sanitized path.

    :rtype: str
    """
    return path.normpath("/"+path_str).lstrip('/')


class PoloBindingSSLFactory(Factory):
    def __init__(self, secret, offered_services, user_services, multicast_addrs):
        
        self.secret = secret
        self.offered_services = offered_services
        self.user_services = user_services
        self.multicast_addrs = multicast_addrs

    def buildProtocol(self, addr):
        p =  self.protocol(self.secret, self.offered_services, self.user_services, self.multicast_addrs)
        p.factory = self
        return p

class PoloBindingSSL(Protocol):

    def __init__(self, secret, offered_services, user_services, multicast_groups=conf.MULTICAST_ADDRS, verify_regexp=conf.VERIFY_REGEXP):
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

        self.secret = secret
        self.offered_services = offered_services
        self.user_services = user_services
        self.verify = re.compile(verify_regexp)#re.compile('^([\d\w]+):([\d\w]+)$')
        self.multicast_groups = multicast_groups
        
        self.router = {}
        self.router["Register"] = self.publish_service_wrapper
        self.router["Publish"] = self.publish_service_wrapper
        self.router["Unpublish"] = self.unpublish_service_wrapper
        self.router["Request-token"] = self.request_token_service_wrapper

    def startProtocol(self):
        """
        Starts the binding and adds an entry in the log file
        """
        logging.info("Starting binding")

    def connectionMade(self):
        print("A connection was made!")

    def dataReceived(self, datagram):
        """
        Receives datagrams from bindings, and verifies the `Command` field.
        It emits a response based on the value (if necessary)

        :param bytes datagram: The byte stream with the message
        """
        
             
        datos = datagram.decode('utf-8')
        logging.debug("Datagram received: %s" % datos)
    
        try:
            datos_dict = json.loads(datos)
        except ValueError:
            self.write_error("Malformed JSON")
            logging.debug("Malformed JSON")
            return
        
        if datos_dict.get("Command", None) is None:
            self.write_error("Missing command")
            logging.debug("Missing command")
            return
        
        command = datos_dict["Command"]
        
        method = self.router.get(command, self.unknown_command_handler)

        method(command, datos_dict.get("Args", {}))
 
    def request_token(self, uid):
        pw_user = pwd.getpwuid(uid)
        if pw_user == None:
            self.write_error("User not found")
            return

        polo_dir = os.path.join(pw_user.pw_dir, ".polo")
        
        if not os.path.exists(polo_dir):
            os.mkdir(polo_dir)
            os.chown(polo_dir, pw_user.pw_uid, pw_user.pw_gid)

        if not os.path.isfile(os.path.join(polo_dir, "token")):
            try:
                f = open(os.path.join(polo_dir, "token"), 'wb')
                os.fchmod(f.fileno(), stat.S_IRUSR | stat.S_IWUSR | stat.S_IRUSR)
                os.fchown(f.fileno(), pw_user.pw_uid, pw_user.pw_gid)
                f.write(tokenprovider.create_token(uid, self.secret))
                f.close()
            except Exception as e:
                self.write_error(str(e))
                return
            self.write_ok(0)
        else:
            self.write_ok(1)

    def write_ok(self, status):
        """
        Creates and sends an OK message

        :param int status: The status code
        """
        json_str = json.dumps({"OK":status})
        self.transport.write(json_str.encode('utf-8'))

    def write_error(self, error):
        """
        Creates and sends an Error message

        :param str error: The error reason
        """
        logging.debug(error)
        self.transport.write(json.dumps({"Error": error}).encode('utf-8'))

    def publish_service_wrapper(self, command, args):
        """
        A wrapper for the :method:publish_service method

        :param str command: The command that triggered the function

        :param dict args: The arguments to pass to :method:publish_service
        """
        logging.debug("Publish service")
        self.publish_service(args.get("service", ''), 
                            args.get("token", ""),
                            multicast_groups=args.get("multicast_groups", conf.MULTICAST_ADDRS),
                            permanent=args.get("permanent", False),
                            root=args.get("root", False))

    def unpublish_service_wrapper(self, command, args):
        """
        A wrapper for the :method:unpublish_service method

        :param str command: The command that triggered the function

        :param dict args: The arguments to pass to :method:unpublish_service
        """
        logging.debug("Unpublish service")
        self.unpublish_service(args.get("service", ''),
                                args.get("token", ""),
                                multicast_groups=args.get("multicast_groups", set()),
                                delete_file=args.get("delete_file", False)
                                )

    def request_token_service_wrapper(self, command, args):
        """
        A wrapper for the :method:request_token method

        :param str command: The command that triggered the function

        :param dict args: The arguments to pass to :method:request_token
        """
        self.request_token(args.get("uid", -1))

    def unknown_command_handler(self, command, args):
        """
        Handles all unkown commands

        :param str command: The command that triggered the function

        :param dict args: The arguments that were passed
        """
        self.transport.write(self.write_error("Malformed request. Commands missing"))

    def publish_service(self, service, token, multicast_groups=conf.MULTICAST_ADDRS, permanent=False, root=False):
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
        if len(str(token)) == 0:
            self.write_error("Need a token")
            return

        uid = tokenprovider.decrypt_token(token, self.secret)
        try:
            if uid is None or int(uid) < 0:
                self.write_error("Bad token. Could not find user")
                return
        except ValueError as e:
            self.write_error("Bad token")
            return

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
            self.write_error("The name of the service %s is invalid: %s" % (service, reason))
            return
        
        error = False
        faulty_ip = ''
        #The IP addresses must be represented in valid dot notation and belong to the range 224-239
        for ip in multicast_groups:
            #The IP must be a string
            error, faulty_ip, reason = utils.verify_ip(ip, multicast_groups)

            if error == True:
                logging.debug(reason)
                try:
                    self.write_error("Invalid multicast group address '%s': %s" % (str(faulty_ip), reason))
                except Exception:
                    self.write_error("Invalid multicast group address")
                return
        
        if type(permanent) is not bool:
            logging.debug("Permanent must be boolean")
            self.write_error("permanent must be boolean")
            return
        
        if type(root) is not bool:
            self.write_error("root must be boolean")
            return
        
        #UID verification
        user = self.validate_user(uid)
        if user is None:
            self.write_error("wrong user")
            return
        
        #Final entry with all service parameters
        service_dict = {}
        service_dict["id"] = service
        #TODOservice_dict["params"] ={} Add parameters
        service_dict["groups"] = multicast_groups
        
        #Root service
        error = False
        error_reason = ""

        if (len(multicast_groups) < 1):
            multicast_groups = conf.MULTICAST_ADDRS

        if root is True:
            if not self.is_superuser(user):
                self.write_error("Permission denied")
                return
            
            for group in multicast_groups:
                #Only root or members of the `marcopolo` group can publish root services
                
                if service in [s['id'] for s in self.offered_services[group]]:
                    error_reason = "Service %s already exists" % service
                    error = True
                    continue
                
                if permanent is True:

                    services_dir = path.join(conf.CONF_DIR, conf.SERVICES_DIR)
                    if not path.exists(services_dir):
                        makedirs(services_dir)
                        os.chown(services_dir, 0, grp.getgrnam(conf.GROUP_NAME).gr_gid)

                    service_file = sanitize_path(service)
                    if path.isfile(path.join(services_dir, service_file)):
                        error_reason = "Permanent service %s already exists" % service
                        error = True
                        continue

                    try:
                        f = open(path.join(services_dir, service_file), 'w')
                        f.write(json.dumps(service_dict))
                        os.fchown(f.fileno(), user.pw_uid, user.pw_gid)
                        f.close()
                        service_dict["file"] = service_file
                    except Exception as e:
                        error_reason = "Could not write file"
                        error = True
                        continue

                
                self.offered_services[group].append({"id":service, "permanent":permanent})
            else:
                service_dict["permanent"] = permanent
                if not error:
                    self.write_ok(service)
                else:
                    self.write_error(error_reason)
            return

        else:
            error = False
            for group in multicast_groups:
                
                if self.user_services[group].get(user.pw_name, None):
                    if service in [s['id'] for s in  self.user_services[group][user.pw_name]]:
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
                        self.write_error("Could not write service file %s" % str(e))
                        error = True
                        return

                if self.user_services[group].get(user.pw_name, None) is None:
                    self.user_services[group][user.pw_name] = []

                self.user_services[group][user.pw_name].append({"id":service, "permanent":permanent})
                logging.debug("Publishing user service %s in group %s" % (service, group))
            else:
                if not error:
                    self.write_ok(user.pw_name+":"+service)
                else:
                    self.write_error("Service already exists")
    
    def unpublish_service(self, service, token, multicast_groups=conf.MULTICAST_ADDRS, delete_file=False):
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
        logging.debug("Unpublishing service")
        if len(str(token)) == 0:

            self.write_error("Bad token")
            return

        uid = tokenprovider.decrypt_token(token, self.secret)
        try:
            if uid is None or int(uid) < 0:
                self.write_error("Bad token")
                return
        except ValueError as e:
            self.write_error("Bad token")
            return

        if len(multicast_groups) < 1:
            multicast_groups = conf.MULTICAST_ADDRS
        #Determine whether it is a root or a user service
        #The IP addresses must be represented in valid dot notation and belong to the range 224-239
        error = False
        reason = ""
        
        for ip in multicast_groups:
            #The IP must be a string
            error, faulty_ip, reason = utils.verify_ip(ip, multicast_groups)
            print(error, ip)
            if error == True:
                logging.debug(reason)
                try:
                    self.write_error("Invalid multicast group address '%s': %s" % (str(faulty_ip), reason))
                except Exception:
                    self.write_error("Invalid multicast group address")
                return

        if error != False:
            self.write_error("Invalid multicast group address '%s': %s" % (str(faulty_ip), reason))
            return
        
        if len(set(multicast_groups) - (set(conf.MULTICAST_ADDRS) & set(multicast_groups))) > 0:
            self.write_error("The group %s is not available" % multicast_groups[0])
            return

        user = self.validate_user(uid)

        if user is None:
            self.write_error("wrong user")
            return
        
        if self.verify.match(service):
            #user service
            try:
                user, service_name = self.verify.match(service).groups()
                user_pwd = pwd.getpwnam(user)
            except (IndexError, ValueError):
                self.write_error("Invalid formatting")
                return
            if user_pwd is None:
                self.write_error("Invalid user")
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
                                self.write_error("Could not find service file")
                        try:
                            self.user_services[group][user].remove(match)
                        except ValueError:
                            pass
                    else:
                        self.write_error("Could not find service")
                        return
                else:
                    self.write_error("Could not find service")
                    return
            else:
                self.write_ok(0)
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
                                        self.write_error("Internal error during processing of file")
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
                                            self.write_error("Internal error during processing of file")
                                    else:
                                        f.seek(0, 0)
                                        f.truncate()
                                        json.dump(file_dict, f)

                        else:
                            self.write_error("Could not find service file")
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
                                        self.write_error("Internal error during processing of file")
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
                            self.write_error("Could not find service")
                            return
                try:
                    self.offered_services[group].remove(match)
                except ValueError as e:
                    pass
            else:
                try:
                    self.write_ok(0)
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
