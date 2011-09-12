#!/usr/bin/python
"""
This program provisions Google Apps accounts. You can use it as a module for
another program, or you can run it as a standalone program.

This is really just a snapshot of the evolution of our provisioning script at
VLACS. There's nothing brilliant here -- in fact, some of it is a bit
embarrassing and we'll hopefully be continuing to clean this up. But maybe
somebody else will find it useful even as it is...so here you go.

If you run it as a standalone program, it expects the following four lines of
input on stdin:
   1. username
   2. firstname
   3. lastname
   4. password

Usage example:
   $ vlagoogleprovision.py
   mohair
   Madeline
   O'Hare
   lk2j3ro8gf
   $

Copyright (C) 2008-2011 VLACS http://vlacs.org

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

import os
import sys
import getopt
import re
import gdata.apps.service

myname = 'vlagoogleprovision.py'

class Usage(Exception):
    def __init__(self, msg):
        self.msg = msg


class AllAccounts:
    def __init__(self, gservice):
        allaccounts = gservice.RetrieveAllUsers()
        self.allaccounts = {}
        for u in allaccounts.entry:
            self.allaccounts[u.login.user_name.lower()] = u
    def exists(self, username):
        if username in self.allaccounts:
            return self.allaccounts[username]
        else:
            return False
    def get(self):
        for un in self.allaccounts.keys():
            yield self.allaccounts[un]


def gservice_init(email, domain, password):
    gservice = gdata.apps.service.AppsService(email=email, domain=domain, password=password)
    gservice.ProgrammaticLogin()
    return gservice


def gservice_init_fromconf():
    from config_google import adminemail, domain, adminpw
    return gservice_init(adminemail, domain, adminpw)


# Ensure that a user account is not admin before we'll update it.
def updateuser_safe(gservice, username, googleaccount):
    try:
        user = gservice.RetrieveUser(username)
        if (user.login.admin != 'true'):
            gservice.UpdateUser(username, googleaccount)
            return True
    except:
        pass
    return False

# Ensure that a user account is not admin before we'll suspend it.
def suspenduser_safe(gservice, username):
    try:
        user = gservice.RetrieveUser(username)
        if (user.login.admin != 'true'):
            gservice.SuspendUser(username)
            return True
    except:
        pass
    return False

# Ensure that a user account (1) is not admin and (2) has been suspended before we'll delete it.
def deleteuser_safe(gservice, username):
    try:
        user = gservice.RetrieveUser(username)
        if (user.login.suspended == 'true'):
            gservice.DeleteUser(username)
            return True
    except:
        pass
    return False

def provision(gservice, username, firstname, lastname, password, stripnums):
    """
    stripnums is boolean; if true the numbers are stripped from the end of each
    input username to check if that username already exists in google without
    the numeric suffix. A nickname will be created from each such match that is
    found. For example: if jsmith27 is input and jsmith exists, jsmith27 will be
    set as a nickname for jsmith and password changes 
    """

    global myname

    username = username.lower()

    # create the account if it doesn't exist
    # add nickname username<num>@ if username@ exists
    username_old = username
    if stripnums:
        # This is ugly, but we gave our first set of users email usernames
        # in first-initial+lastname format, and VSA /always/ appends
        # a number.
        # In order to remain sane we're now using the same usernames VSA
        # assigns, but we still have to account for these other pre-existing
        # accounts.
        username_old = re.sub('^([^0-9]*)[0-9]*$', r"\1", username)

    foundaccount = 0
    nickname = ''
    try:
        user_entry = gservice.RetrieveUser(username)
        print "%s: found exact %s" % (myname, username)
        foundaccount = 1
    except:
        try:
            user_entry = gservice.RetrieveUser(username_old)
            # We found the same username without any numbers appended.
            print "%s: found old %s" % (myname, username_old)
            foundaccount = 1
            nickname = username # assign the VSA username as a nickname for this account
            username = username_old
        except:
            pass

    if not foundaccount:
        print "%s: creating account: %s" % (myname, username)
        try:
            gservice.CreateUser(username, lastname, firstname, password)
            pass
        except Exception, inst:
            print "%s: account creationg exception: %s:%s" % (myname, type(inst), inst)
    else:
        print "%s: updating %s: fname(%s), lname(%s), password(secret)" % (myname, username, firstname, lastname)
        user_entry.name.given_name = firstname
        user_entry.login.family_name = lastname
        user_entry.login.password = password

        try:
            gservice.UpdateUser(username, user_entry)
            pass
        except Exception, inst:
            print "%s: password update exception: %s:%s" % (myname, type(inst), inst)

        if nickname.__len__() > 0:
            try:
                gservice.RetrieveNickname(nickname)
                pass
            except:
                print "%s: adding new nick: %s for %s" % (myname, nickname, username)
                try:
                    gservice.CreateNickname(username, nickname)
                    pass
                except Exception, inst:
                    print "%s: nickname add exception: %s:%s" % (myname, type(inst), inst)

def main(argv=None):
    """
    main() executes this module as a standalone program.
    """

    global myname
    stripnums = 1
    operation = 'provision'

    if argv is None:
        argv = sys.argv
    try:
        try:
            opts, args = getopt.getopt(argv[1:], "hs", ["help", "stripnums", ])
        except getopt.error, msg:
             raise Usage(msg)

        # process options
        for option, arg in opts:
            if option in ("-h", "--help"):
                print __doc__
                self.die()
            elif option in ("-s", "--stripnums"):
                stripnums = 0
            elif option in ("-o", "--operation"):
                operation = arg

        gservice = gservice_init_fromconf()
        while True:
            username = sys.stdin.readline().rstrip(os.linesep)
            # If we're suspending or deleting, we already have enough data.
            if (operation == 'suspend'):
              suspenduser_safe(gservice, username)
            elif (operation == 'delete'):
              deleteuser_safe(gservice, username)

            # We must be provisioning.
            if len(username) == 0:
                sys.exit()
            firstname = sys.stdin.readline().rstrip(os.linesep)
            if len(firstname) == 0:
                sys.exit()
            lastname = sys.stdin.readline().rstrip(os.linesep)
            if len(lastname) == 0:
                sys.exit()
            password = sys.stdin.readline().rstrip(os.linesep)
            if len(password) == 0:
                sys.exit()
            provision(gservice, username, firstname, lastname, password, stripnums)

    except Usage, err:
        print >>sys.stderr, err.msg
        print >>sys.stderr, "for help use --help"
        return 2

if __name__ == "__main__":
    sys.exit(main())

