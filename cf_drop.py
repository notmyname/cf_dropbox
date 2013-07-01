#!/usr/bin/env python

import sys
import os
from optparse import OptionParser
from urllib import quote

import cloudfiles

import cf_auth

usage = 'Usage: %prog [options] path1 [path2 [...]]'
parser = OptionParser(usage=usage)
parser.add_option('-D', '--domain', dest='domain', default=None,
                  help='Domain to use instead of the container\'s public URI')
parser.add_option('-l', '--list', dest='list', default=None,
                action='store_true', help='Show your dropbox\'s listing')
parser.add_option('-P', '--purge', dest='purge', default=None,
                action='store_true', help='Purge the objects')

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
        else:
            obj.load_from_filename(filename)
            obj.metadata['Original-Name'] = quote(filename)
            obj.sync_metadata()
    except cloudfiles.errors.ResponseError, err:
        print >>sys.stderr, err
    else:
        if options.purge:
            print 'Purged',
        print container_url + '/' + object_name
