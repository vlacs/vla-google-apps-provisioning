import ldap
import re

class DataSource:
    usernames = []
    users = []
    count = 0
    def getusers(self, config):
        l = ldap.initialize('ldap://' + config.ldap_host)
        l.simple_bind_s(config.ldap_binddn, config.ldap_pw)
        for searchbase in config.ldap_search_bases:
            data = l.search_s(searchbase, ldap.SCOPE_SUBTREE, '(objectclass=organizationalperson)')
            for ldapuser in data:
                self.count += 1
                ldapuser = ldapuser[1]
                try:
                    # lowercase the username
                    # drop the timezone portion of whenChanged (example: '20110526184938.0Z' -> '20110526184938'
                    firstname = ldapuser[config.ldap_attrs['firstname']][0]
                    lastname = ldapuser[config.ldap_attrs['lastname']][0]
                    username = ldapuser[config.ldap_attrs['username']][0]
                    whenchanged = ldapuser[config.ldap_attrs['whenchanged']][0].split('.')[0]

                    ous = ['/']
                    if 'ous' in config.ldap_attrs:
                        ous = ldap.explode_dn(ldapuser[config.ldap_attrs['ous']][0].lower())
                        ous = map(lambda x: x[3:], filter(lambda x: re.match('ou=', x), ous))
                        ous.reverse()
                    #sys.stdout.write("%s %s %s: " % (ldapuser['givenName'][0], ldapuser['sn'][0], ldapuser['sAMAccountName'][0]))
                except KeyError, inst:
                    print "exception: %s:%s" % (type(inst), inst)
                    print ldapuser
                    continue

                password_hash = None
                password_hash_function = None
                try:
                    password_hash = ldapuser[config.ldap_password_hash_attribute][0]
                    password_hash_function = config.password_hash_function # Just to make sure this is set.
                except KeyError:
                    pass
                except AttributeError:
                    pass

                self.users.append({'username': username, 'firstname': firstname, 'lastname': lastname, 'ous': ous, 'password_hash': password_hash, 'password_hash_function': password_hash_function, 'whenchanged': whenchanged})
        l.unbind()
        return

