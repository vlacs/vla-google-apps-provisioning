#!/usr/bin/python
"""
You'll need to create a config.py file in this directory to configure this
script to work for your network. You can use config-dist.py as an example to
guide you.

Usage example:
   $ test.py [ --datasource <DataSourceLDAP | DataSourceDB> ] --function <function name>

Copyright (C) 2011 VLACS (author: Matt Oquist <moquist@majen.net>)
Copyright (C) 2011 Matt Oquist <moquist@majen.net>
Copyright (C) 2011 Oyster River Cooperative School District http://orcsd.org
Copyright (C) 2012 SAU16 http://sau16.org

This program is free software; you can redistribute it and/or
modify it under the terms of the GNU General Public License
as published by the Free Software Foundation; either version 2
of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program; if not, write to the Free Software
Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
"""

import sys
import random
import re
import bsddb
import getopt
import hashlib
import shelve
from pprint import pprint
import vlagoogleprovisionlib
import config

# process options
argv = sys.argv
opts, args = getopt.getopt(argv[1:], "t:", ["testname=", ])
for option, arg in opts:
    if option in ("-t", "--testname"):
        testname = arg
        print "testname: %s" % arg

datasource = __import__(config.datasource)
datasource = getattr(datasource, 'DataSource')
datasource = datasource()

if testname == 'getusers' :
    datasource.getusers(config)
    for localaccount in datasource.users:
        print localaccount

sys.exit()


