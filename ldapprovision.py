#!/usr/bin/python
"""
Read an Active Directory (or other LDAP directory?) and use the VLACS
provisioning lib to provision and update Google Apps accounts.

You'll need to create an ldapconfig.py file in this directory to configure this
script to work for your network. You can use ldapconfig-dist.py as an example to
guide you.

Copyright (C) 2011 Matt Oquist <moquist@majen.net>

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
import hashlib
import ldap
import vlagoogleprovision
import ldapconfig

def newpw(length) :
    return hashlib.md5(str(random.random())).hexdigest()[0:length]

gservice = vlagoogleprovision.gservice_init(ldapconfig.google_admin_email, ldapconfig.google_apps_domain, ldapconfig.google_admin_pw)
googleaccounts = vlagoogleprovision.AllAccounts(gservice)
print "%s Google accounts (starting)" % len(googleaccounts.allaccounts)
ldapcount = 0
googlenewcount = 0
for dn in ldapconfig.search_dns :
    # Lots of google create operations may take so long the LDAP connection will time out. So establish it every time.
    l = ldap.initialize('ldap://' + ldapconfig.ldap_host)
    l.simple_bind_s(ldapconfig.ldap_binddn, ldapconfig.ldap_pw)
    data = l.search_s(dn, ldap.SCOPE_SUBTREE, '(objectclass=organizationalperson)')
    for ldapuser in data :
        ldapcount += 1
        ldapuser = ldapuser[1]
        (firstname, lastname, username) = (ldapuser['givenName'][0], ldapuser['sn'][0], ldapuser['sAMAccountName'][0].lower())
        #sys.stdout.write("%s %s %s: " % (ldapuser['givenName'][0], ldapuser['sn'][0], ldapuser['sAMAccountName'][0]))
        sys.stdout.write("%s %s %s: " % (firstname, lastname, username))
        googleaccount = googleaccounts.accountexists(username)
        if googleaccount:
            sys.stdout.write("exists (no update performed)\n")
            # This doesn't really work, and the update isn't implemented.
            #ldapupdated = ldapuser['whenChanged'][0][:14] # ex: 20080311011620.0Z -> 20080311011620
            #googleupdated =  re.sub('[^\d]', '', googleaccount.updated.text)[:14] # ex: 1970-01-01T00:00:00.000Z -> 19700101000000
            #if googleupdated < ldapupdated:
            #    sys.stdout.write(" (needs update (not yet implemented): %s %s)" % (googleupdated, ldapupdated))
            #sys.stdout.write("\n")
        else:
            password = newpw(ldapconfig.newpwlen)
            sys.stdout.write("creating...")
            vlagoogleprovision.createuser(gservice, username, lastname, firstname, password)
            newaccountslog = open(ldapconfig.newaccountslogfile, 'a')
            newaccountslog.write("%s: %s\n" % (username, password))
            newaccountslog.close()
            sys.stdout.write("done\n")
            googlenewcount += 1
    l.unbind()


print "%s LDAP accounts altogether" % ldapcount
print "%s new google accounts" % googlenewcount

