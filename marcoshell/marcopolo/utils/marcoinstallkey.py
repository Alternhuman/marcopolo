#!/usr/bin/env python
# -*- coding: utf-8 -*-
#This is a simple utility to deploy a public key to a set of willing nodes
#without the hassle of previously knowing their IPs/hostnames or doing one
#at the time

#import marco
import argparse

#The arguments are pretty much the same as the ssh-copy-id command

parser = argparse.ArgumentParser(description="Adds new key to willing nodes")
parser.add_argument('-i', metavar="identity_file", type=str, nargs='?', help="""Use only the key(s) contained in identity_file (rather than look‐
             ing for identities via ssh-add(1) or in the default_ID_file).  If
             the filename does not end in .pub this is added.  If the filename
             is omitted, the default_ID_file is used.

             Note that this can be used to ensure that the keys copied have
             the comment one prefers and/or extra options applied, by ensuring
             that the key file has these set as preferred before the copy is
             attempted.""")
parser.add_argument('-p', metavar="port", type=int, nargs='?')
parser.add_argument('-o', metavar="ssh_option", type=str, nargs='?')


args = parser.parse_args()
print(args)
"""def whereis(program):
    for path in os.environ.get('PATH', '').split(':'):
        if os.path.exists(os.path.join(path, program)) and \
           not os.path.isdir(os.path.join(path, program)):
            return os.path.join(path, program)
    return None"""

