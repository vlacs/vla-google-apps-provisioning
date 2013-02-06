#!/usr/bin/python
"""
Set a google apps user's password from the command line.

You'll need to create a config.py file in this directory to configure this
script to work for your network. You can use config-dist.py as an example to
guide you.

Copyright (C) 2013 VLACS <moquist@vlacs.org>

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
import re
import getopt
import getpass
import shelve
import vlagoogleprovisionlib
import config

def usage():
    print """
google-passwd.py [options] <username>
    Set a google apps user's password.
    You MUST have edited config.py in the directory where this script lives prior to using this script.

    -h, --help
        Print this message.

    -f, --function=hash_function
        Use the specific hash function. At this time Google supports: MD5, SHA-1

    -o, --override-admin
        Change the user's password even if the user account has admin privileges.
    """

# process options
argv = sys.argv
do_override = False
hash_function = None
opts, args = getopt.getopt(argv[1:], "fho", ["function", "help", "override-admin", ])
for option, arg in opts:
    if option in ("-h", "--help"):
        usage()
        sys.exit()
    elif option in ("-o", "--override"):
        do_override = True
    elif option in ("-f", "--function"):
        hash_function = arg

if len(args) > 1:
    print "Too many arguments. Please submit exactly one username.\n";
    usage()
    sys.exit(1)

username = args[0]

gservice = vlagoogleprovisionlib.gservice_init(config.google_admin_email, config.google_apps_domain, config.google_admin_pw)
user = gservice.RetrieveUser(username)
print "Fetched user account (%s)" % username

if (user.login.admin == 'true'):
    if do_override:
        print "%s is an admin, got override argument so continuing anyway" % username
    else:
        print "%s is an admin, no override argument so halting now" % username
        sys.exit()

password1 = 1
password2 = 2
while password1 != password2:
    password1 = getpass.getpass("Please enter %s's new password: " % username)
    password2 = getpass.getpass("Please re-enter %s's new password: " % username)
    if password1 != password2:
        print "Passwords do not match. Please try again.\n"

user.login.password = password1
user.login.hash_function_name = None

if hash_function:
    user.login.hash_function_name = hash_function

gservice.UpdateUser(username, user)
sys.exit()




