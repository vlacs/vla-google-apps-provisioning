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
        ous (if configured; see config.py for format)
        groups (if configured; see config.py for format)

        When finished, enter one blank line after the last whenchanged value.
        """
        while True:
            user = {}
            for field in ['username', 'firstname', 'lastname', 'password_hash', 'password_hash_function', 'whenchanged']:
                user[field] = sys.stdin.readline().rstrip(os.linesep)
                if len(user[field]) == 0:
                    if field == 'username' and len(self.users):
                        break
                    else:
                        sys.exit()
            # lowercase the username and drop the google domain in case it's an email address
            user['username'] = user['username'].lower().replace(('@' + config.google_apps_domain).lower(), '')
            assert user['username'].count('@') == 0

            # 'now' is a special case of whenchanged
            if user['whenchanged'] == 'now':
                user['whenchanged'] = int(time.time())

            # 'none' is a special case of password_hash_function
            if user['password_hash_function'].lower() == 'none':
                user['password_hash_function'] = None
                user['password_hash'] = None

            if config.stdin_ous:
                user['ous'] = sys.stdin.readline().rstrip(os.linesep).split(';')
            if config.stdin_groups:
                user['groups'] = filter(None, sys.stdin.readline().rstrip(os.linesep).split(';'))

            self.users.append(user)
        print self.users
        return
