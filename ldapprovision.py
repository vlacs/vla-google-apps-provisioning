#!/usr/bin/python
"""
Read an Active Directory (or other LDAP directory?) and use the VLACS
provisioning lib to provision and update Google Apps accounts.

You'll need to create an ldapconfig.py file in this directory to configure this
script to work for your network. You can use ldapconfig-dist.py as an example to
guide you.

Usage example:
   $ ldapprovision.py [ --delete ] [ --suspend ]

This script matches LDAP & Google accounts by ASSUMING that ldap's
sAMAccountName == the google username. If you feel like implementing a step of
indirection there so you can use some other configurable LDAP attribute instead,
feel free. Patches are welcome -- just don't make it confusing for folks to
configure!

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
import getopt
import hashlib
import ldap
import vlagoogleprovision
import ldapconfig

def newpw(length):
    return hashlib.md5(str(random.random())).hexdigest()[0:length]

dodelete = False
dosuspend = False
# process options
argv = sys.argv
opts, args = getopt.getopt(argv[1:], "ds", ["delete", "suspend", ])
for option, arg in opts:
    if option in ("-d", "--delete"):
        dodelete = True
        print "Deletion not supported quite yet...\n"
        sys.exit()
    elif option in ("-s", "--suspend"):
        dosuspend = True


gservice = vlagoogleprovision.gservice_init(ldapconfig.google_admin_email, ldapconfig.google_apps_domain, ldapconfig.google_admin_pw)
googleaccounts = vlagoogleprovision.AllAccounts(gservice)
print "%s Google accounts (starting)" % len(googleaccounts.allaccounts)

# ##################################################################
# Find LDAP accounts that are missing (or need an update) in Google.
ldapusers = []
ldapcount = 0
googlenewcount = 0
googleupdcount = 0
newaccountslog = open(ldapconfig.newaccountslogfile, 'a')
for dn in ldapconfig.search_dns:
    # Lots of google create operations may take so long the LDAP connection will time out. So establish it every time.
    l = ldap.initialize('ldap://' + ldapconfig.ldap_host)
    l.simple_bind_s(ldapconfig.ldap_binddn, ldapconfig.ldap_pw)
    data = l.search_s(dn, ldap.SCOPE_SUBTREE, '(objectclass=organizationalperson)')
    for ldapuser in data:
        ldapcount += 1
        ldapuser = ldapuser[1]
        try:
            (firstname, lastname, username) = (ldapuser['givenName'][0], ldapuser['sn'][0], ldapuser['sAMAccountName'][0].lower())
            #sys.stdout.write("%s %s %s: " % (ldapuser['givenName'][0], ldapuser['sn'][0], ldapuser['sAMAccountName'][0]))
        except KeyError:
            continue
        ldapusers.append(username)
        sys.stdout.write("%s %s %s: " % (firstname, lastname, username))
        googleaccount = googleaccounts.exists(username)
        if googleaccount:
            sys.stdout.write("exists")
            if (googleaccount.login.suspended == 'true'):
                gservice.RestoreUser(username)
                sys.stdout.write(", un-suspending")
            if googleaccount.name.family_name == lastname and googleaccount.name.given_name == firstname:
                sys.stdout.write(", no update.\n")
            else:
                sys.stdout.write(" and needs update...")
                googleaccount.name.family_name = lastname
                googleaccount.name.given_name = firstname
                gservice.UpdateUser(username, googleaccount)
                sys.stdout.write("updated.\n")
                googleupdcount += 1
        else:
            password = newpw(ldapconfig.newpwlen)
            sys.stdout.write("creating...")
            gservice.CreateUser(username, lastname, firstname, password)
            newaccountslog.write("%s: %s\n" % (username, password))
            sys.stdout.write("done\n")
            googlenewcount += 1
    l.unbind()
    newaccountslog.close()

# ################################################
# Find Google accounts that are missing from LDAP and perhaps suspend or delete them.
missingcount = 0
suspendedcount = 0
missingaccountslogfile = open(ldapconfig.missingaccountslogfile, 'w')
for account in googleaccounts.get():
    username = account.login.user_name
    if username not in ldapusers and account.login.admin == 'false':
        sys.stdout.write("%s missing from LDAP" % username)
        missingaccountslogfile.write("%s\n" % username)
        missingcount += 1
        if (account.login.suspended == 'true'):
            sys.stdout.write(": already suspended")
        elif (dosuspend):
            sys.stdout.write(": suspending...")
            vlagoogleprovision.suspenduser_safe(gservice, username)
            suspendedcount += 1
            sys.stdout.write(" done.")
        sys.stdout.write("\n")
missingaccountslogfile.close()

print "%s LDAP accounts altogether" % ldapcount
print "%s new google accounts" % googlenewcount
print "%s updated google accounts" % googleupdcount
print "%s google accounts missing from LDAP (%s suspended just now)" % (missingcount, suspendedcount)

