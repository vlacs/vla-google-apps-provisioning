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
        sql = "SELECT %s, %s, %s, %s, %s FROM %s" % (config.db_field_username, config.db_field_password, config.db_field_firstname, config.db_field_lastname, config.db_field_whenupdated, config.db_table)
        cur = self.db_execute(sql)
        for user in cur:
            self.count += 1
            try:
                firstname = user[config.db_field_firstname]
                lastname = user[config.db_field_lastname]

                # lowercase the username
                username = user[config.db_field_username].lower()

                # drop the google domain from username, in case it's an email address
                username = username.replace('@' + config.google_apps_domain, '')
                assert username.count('@') == 0

                whenchanged = user[config.db_field_whenupdated]
                #print "%s %s: %s, %s" % (firstname, lastname, username, whenchanged)

            except KeyError, inst:
                print "exception: %s:%s" % (type(inst), inst)
                print ldapuser
                continue
            except AssertionError, inst:
                print "exception: %s:%s" % (type(inst), inst)
                print ldapuser
                continue

            password_hash = None
            password_hash_function = None
            try:
                password_hash = user[config.db_field_password]
                password_hash_function = config.password_hash_function # Just to make sure this is set.
            except KeyError:
                pass

            self.users.append({'username': username, 'firstname': firstname, 'lastname': lastname, 'password_hash': password_hash, 'password_hash_function': password_hash_function, 'whenchanged': whenchanged})
        return

