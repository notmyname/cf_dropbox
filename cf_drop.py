#!/usr/bin/env python2.7

import sys
import os
from optparse import OptionParser
from urllib import quote

sys.path.insert(0, '/Library/Python/2.7/site-packages')

import cloudfiles

import cf_auth

default_domain = os.environ.get('DROPBOX_DOMAIN_NAME')

usage = 'Usage: %prog [options] path1 [path2 [...]]'
parser = OptionParser(usage=usage)
parser.add_option('-D', '--domain', dest='domain', default=default_domain,
                  help='Domain to use instead of the container\'s public URI')
parser.add_option('-l', '--list', dest='list', default=None,
                action='store_true', help='Show your dropbox\'s listing')
parser.add_option('-P', '--purge', dest='purge', default=None,
                action='store_true', help='Purge the objects')
parser.add_option('-d', '--delete', dest='delete', default=None,
                action='store_true', help='Delete the objects')

options, args = parser.parse_args()

DROPBOX_CONTAINER_NAME = os.environ.get('DROPBOX_CONTAINER_NAME', 'dropbox')

conn = cloudfiles.get_connection(username=cf_auth.username,
                                 api_key=cf_auth.apikey)

container = conn.get_container(DROPBOX_CONTAINER_NAME)

if options.list:
    listing = container.list_objects_info()
    for o in listing:
        print o['name']
    sys.exit(0)

container_url = options.domain if options.domain else container.public_uri()
if not container_url.startswith('http://'):
    container_url = 'http://' + container_url

for filename in args:
    try:
        object_name = filename.replace(' ', '_')
        obj = container.create_object(object_name)
        if options.purge:
            obj.purge_from_cdn()
        elif options.delete:
            container.delete_object(object_name)
        else:
            obj.metadata['original-name'] = quote(filename)
            obj.load_from_filename(filename)
    except cloudfiles.errors.ResponseError, err:
        print >>sys.stderr, err
    else:
        if options.purge:
            print 'Purged',
        elif options.delete:
            print 'Deleted',
        print container_url + '/' + object_name
