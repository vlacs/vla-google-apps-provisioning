import psycopg2, psycopg2.extensions, psycopg2.extras

class DataSourceDB:
    users = []
    count = 0

    def __init__(self):
        self.db = psycopg2.connect(host = DBHOST, database = DBNAME, user = DBUSER, password = DBPASS)

    def db_execute(q, *args) :
        cur = db.cursor(cursor_factory=psycopg2.extras.DictCursor)
        cur.execute(q.replace("prefix_", PREFIX), *args)
        return cur

    def getusers(self, config):
        sql = "SELECT %s, %s, %s, %s FROM %s" % (config.db_field_username, config.db_field_password, config.db_field_firstname, config.db_field_lastname, config.db_table)
        cur = self.db_execute(sql)
        for user in data:
            self.count += 1
            user = user[1]
            try:
                # lowercase the username
                # drop the timezone portion of whenChanged (example: '20110526184938.0Z' -> '20110526184938'
                (firstname, lastname, username, whenchanged) = (user['givenName'][0], user['sn'][0], user['sAMAccountName'][0].lower(), user['whenChanged'][0].split('.')[0])
                #sys.stdout.write("%s %s %s: " % (user['givenName'][0], user['sn'][0], user['sAMAccountName'][0]))
            except KeyError:
                continue

            password_hash = None
            password_hash_function = None
            try:
                password_hash = user[config.ldap_password_hash_attribute][0]
                password_hash_function = config.password_hash_function # Just to make sure this is set.
            except KeyError:
                pass
            except AttributeError:
                pass

            self.users.append({'username': username, 'firstname': firstname, 'lastname': lastname, 'password_hash': password_hash, 'password_hash_function': password_hash_function, 'whenchanged': whenchanged})
        return

