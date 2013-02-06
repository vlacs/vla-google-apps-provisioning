#!/usr/bin/python
"""
Read a data source (such as Active Directory) and use the VLACS
provisioning lib to provision and update Google Apps accounts.

You'll need to create a config.py file in this directory to configure this
script to work for your network. You can use config-dist.py as an example to
guide you.

This script matches accounts from a local data source with Google accounts by
ASSUMING that the local account usernames == the Google usernames. If the
datasource yields email addresses that match your Google Apps domain, the
@domain part will be stripped. For example:
  * "username@yourdomain.com" will be treated as "username"
  * "username@someotherdomain.com" will be treated as an error
  * "username" will be treated as "username"

Copyright (C) 2011 VLACS (author: Matt Oquist <moquist@majen.net>)
Copyright (C) 2011 Matt Oquist <moquist@majen.net>
Copyright (C) 2011 Oyster River Cooperative School District http://orcsd.org

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
import vlagoogleprovisionlib
import config

def newpw(length):
    return hashlib.md5(str(random.random())).hexdigest()[0:length]

def usage():
    print """
provision.py
    Provision Google apps user accounts based on accounts that exist in a local data source.
    You MUST have edited config.py in the directory where this script lives prior to using this script.

    -h, --help
        Print this message.

    -s, --suspend
        Suspend all Google accounts that do not exist in the local source (as it is currently configured).
        Keep in mind that if you remove an OU from your list in config.py, all the accounts under it will disappear from the perspective of this script. Use --suspend with caution!

        The default is to print a message and otherwise ignore these accounts.

    -u, --forceupdate=USERNAME
        Force the account that has the specified username to be updated next time this script runs.
    """

dodelete = False
dosuspend = False
# process options
argv = sys.argv
opts, args = getopt.getopt(argv[1:], "dhsu:", ["delete", "help", "suspend", "forceupdate=", ])
for option, arg in opts:
    if option in ("-h", "--help"):
        usage()
        sys.exit()
    elif option in ("-d", "--delete"):
        dodelete = True
        print "Deletion not supported quite yet...\n"
        sys.exit()
        if config.datasource == 'datasource-stdin':
            print "-d,--delete may not be used with datasource-stdin."
            sys.exit()
    elif option in ("-s", "--suspend"):
        dosuspend = True
        if config.datasource == 'datasource-stdin':
            print "-s,--suspend may not be used with datasource-stdin."
            sys.exit()
    elif option in ("-u", "--forceupdate"):
        try :
            update_history = shelve.open(config.updatehistory_file)
            update_history.__delitem__(arg)
            update_history.close()
            print "user '%s' set for update next run" % arg
        except bsddb._bsddb.DBNotFoundError :
            print "user '%s' not found in update history (already set to update)" % arg
        sys.exit()


gservice = vlagoogleprovisionlib.gservice_init(config.google_admin_email, config.google_apps_domain, config.google_admin_pw)
googleaccounts = vlagoogleprovisionlib.AllAccounts(gservice)
print "%s Google accounts (starting)" % len(googleaccounts.allaccounts)

# Fetch all local accounts.
datasource = __import__(config.datasource)
datasource = getattr(datasource, 'DataSource')
datasource = datasource(config)
datasource.getusers(config)

ouhandler = False
if config.replicate_ous:
    ouhandler = vlagoogleprovisionlib.OUHandler(config.google_admin_email, config.google_apps_domain, config.google_admin_pw)

# ##################################################################
# Create and update google accouns from local data.
googlenewcount = 0
googleupdcount = 0
update_history = shelve.open(config.updatehistory_file)
newaccountslog = open(config.newaccountslogfile, 'a')
usernames = []
for localaccount in datasource.users:
    usernames.append(localaccount['username'])
    sys.stdout.write("%s %s %s: " % (localaccount['firstname'], localaccount['lastname'], localaccount['username']))
    googleaccount = googleaccounts.exists(localaccount['username'])
    if googleaccount:
        sys.stdout.write("exists")
        if (googleaccount.login.suspended == 'true'):
            gservice.RestoreUser(localaccount['username'])
            sys.stdout.write(", un-suspending")

        try:
            if localaccount['username'] not in update_history:
                update_history[localaccount['username']] = 0
            if update_history[localaccount['username']] >= localaccount['whenchanged']:
                sys.stdout.write(", no update (last update %s).\n" % localaccount['whenchanged'])
            else:
                sys.stdout.write(" and needs update (lastupdate was %s, new update from %s)..." % (update_history[localaccount['username']], localaccount['whenchanged']))
                if localaccount['password_hash']:
                    googleaccount.login.password = localaccount['password_hash']
                    googleaccount.login.hash_function_name = localaccount['password_hash_function']
                    sys.stdout.write(" using hashed password...")

                googleaccount.name.family_name = localaccount['lastname']
                googleaccount.name.given_name = localaccount['firstname']
                if vlagoogleprovisionlib.updateuser_safe(gservice, localaccount['username'], googleaccount) :
                    if ouhandler and 'ous' in localaccount:
                        try:
                            ouhandler.ensure_updateorguser(localaccount['username'], localaccount['ous'])
                        except Exception, inst:
                            sys.stdout.write("%s(%s): ensure_updateorguser exception: %s:%s" % (localaccount['username'], localaccount['ous'], type(inst), inst))
                            continue
                    update_history[localaccount['username']] = localaccount['whenchanged']
                    sys.stdout.write("updated.\n")
                    googleupdcount += 1
                else :
                    sys.stdout.write("NOT updated (google admin?).\n")
                sys.stdout.write("\n")
        except vlagoogleprovisionlib.gdata.apps.service.AppsForYourDomainException:
            sys.stdout.write("error: AppsForYourDomainException during update!\n")
            continue

    else:
        try:
            sys.stdout.write("creating...")
            if localaccount['password_hash']:
                password = localaccount['password_hash']
                sys.stdout.write(" using hashed password...")
            else:
                password = newpw(config.newpwlen)
                localaccount['password_hash_function'] = None
                newaccountslog.write("%s: %s\n" % (localaccount['username'], password))

            gservice.CreateUser(localaccount['username'], localaccount['lastname'], localaccount['firstname'], password, localaccount['password_hash_function'])
            if ouhandler and 'ous' in localaccount:
                try:
                    ouhandler.ensure_updateorguser(localaccount['username'], localaccount['ous'])
                except Exception, inst:
                    sys.stdout.write("%s(%s): ensure_updateorguser exception: %s:%s" % (localaccount['username'], localaccount['ous'], type(inst), inst))
                    continue
            update_history[localaccount['username']] = localaccount['whenchanged']
            sys.stdout.write("done\n")
            googlenewcount += 1
        except vlagoogleprovisionlib.gdata.apps.service.AppsForYourDomainException:
            sys.stdout.write("error: AppsForYourDomainException during creation!\n")
            continue
newaccountslog.close()
update_history.close()

# ################################################
# Find Google accounts that are missing locally and perhaps suspend or delete them.
missingcount = 0
suspendedcount = 0
missingaccountslogfile = open(config.missingaccountslogfile, 'w')
for account in googleaccounts.get():
    username = account.login.user_name
    if username not in usernames and account.login.admin == 'false':
        sys.stdout.write("%s missing from local source" % username)
        missingaccountslogfile.write("%s\n" % username)
        missingcount += 1
        if (account.login.suspended == 'true'):
            sys.stdout.write(": already suspended")
        elif (dosuspend):
            sys.stdout.write(": suspending...")
            vlagoogleprovisionlib.suspenduser_safe(gservice, username)
            suspendedcount += 1
            sys.stdout.write(" done.")
        sys.stdout.write("\n")
missingaccountslogfile.close()

print "%s local accounts altogether" % datasource.count
print "%s new google accounts" % googlenewcount
print "%s updated google accounts" % googleupdcount
print "%s google accounts missing from local source (%s suspended just now)" % (missingcount, suspendedcount)

