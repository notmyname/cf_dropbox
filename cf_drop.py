#!/usr/bin/env python

import sys
import os

import cloudfiles

import cf_auth

if len(sys.argv) < 2:
    print >>sys.stderr, 'Usage: %s path [...]' % sys.argv[0]
    sys.exit(1)

DROPBOX_CONTAINER_NAME = os.environ.get('DROPBOX_CONTAINER_NAME', 'dropbox')

conn = cloudfiles.get_connection(username=cf_auth.username,
                                 api_key=cf_auth.apikey)
# make sure we have the container
container = conn.create_container(DROPBOX_CONTAINER_NAME)
# make sure the container is public
container.make_public()
container_url = container.public_uri()

for filename in sys.argv[1:]:
    try:
        object_name = filename.replace(' ', '_')
        obj = container.create_object(object_name)
        obj.load_from_filename(filename)
    except cloudfiles.errors.ResponseError, err:
        print >>sys.stderr, err
    else:
        print container_url + '/' + object_name