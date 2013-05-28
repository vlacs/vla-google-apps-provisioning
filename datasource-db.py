# ATM this only supports postgres.

import psycopg2, psycopg2.extensions, psycopg2.extras

class DataSource:
    users = []
    count = 0

    def __init__(self, config):
        self.db = psycopg2.connect(host = config.db_host, database = config.db_name, user = config.db_username, password = config.db_pw)

    def db_execute(self, q, *args) :
        cur = self.db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(q, *args)
        return cur

    def getusers(self, config):
        sql = ', '.join(config.db_fields.values())
        sql = "SELECT " + sql + " FROM " + config.db_table
        cur = self.db_execute(sql)
        for row in cur:
            self.count += 1
            try:
                user = {}
                for key in config.db_fields:
                    if key == 'password': continue
                    user[key] = row[config.db_fields[key]]

                # lowercase the username and drop the google domain in case it's an email address
                user['username'] = user['username'].lower().replace(('@' + config.google_apps_domain).lower(), '')
                assert user['username'].count('@') == 0

                if 'ous' in config.db_fields:
                    user['ous'] = user['ous'].split(';')
            except KeyError, inst:
                print "exception: %s:%s" % (type(inst), inst)
                print row
                continue
            except AssertionError, inst:
                print "exception: %s:%s" % (type(inst), inst)
                print row
                continue

            user['password_hash'] = None
            user['password_hash_function'] = None
            try:
                user['password_hash'] = user[config.db_fields['password']]
                user['password_hash_function'] = config.password_hash_function # Just to make sure this is set.
            except KeyError:
                pass

            self.users.append(user)
        return
