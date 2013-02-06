import os, sys, time

class DataSource:
    users = []
    count = 0

    def __init__(self, config):
        pass

    def getusers(self, config):
        print """
        Please enter each of these fields, for each account, one field per line:

        username
        firstname
        lastname
        password or password_hash
        password_hash_function {MD5 | SHA-1 | none}
        whenchanged (either 'now' or a UNIX timestamp is good here)

        When finished, enter one blank line after the last whenchanged value.
        """
        while True:
            username = sys.stdin.readline().rstrip(os.linesep)
            if len(username) == 0:
                if len(self.users):
                    break
                else:
                    # We got no data.
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
            password_hash_function = sys.stdin.readline().rstrip(os.linesep)
            if len(password_hash_function) == 0:
                sys.exit()
            whenchanged = sys.stdin.readline().rstrip(os.linesep)
            if len(whenchanged) == 0:
                sys.exit()

            # drop the google domain from username, in case it's an email address
            username = username.replace('@' + config.google_apps_domain, '')
            assert username.count('@') == 0

            # 'now' is a special case of whenchanged
            if whenchanged == 'now':
                whenchanged = int(time.time())

            # 'none' is a special case of password_hash_function
            if password_hash_function.lower() == 'none':
                password_hash_function = None
                password_hash = None
            else:
                password_hash = password

            self.users.append({'username': username, 'firstname': firstname, 'lastname': lastname, 'password': password, 'password_hash': password_hash, 'password_hash_function': password_hash_function, 'whenchanged': whenchanged, })

        print self.users
        return

