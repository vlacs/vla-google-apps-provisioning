import ldap

class DataSource:
    usernames = []
    users = []
    count = 0
    def getusers(self, config):
        l = ldap.initialize('ldap://' + config.ldap_host)
        l.simple_bind_s(config.ldap_binddn, config.ldap_pw)
        for dn in config.ldap_search_dns:
            data = l.search_s(dn, ldap.SCOPE_SUBTREE, '(objectclass=organizationalperson)')
            for ldapuser in data:
                count += 1
                ldapuser = ldapuser[1]
                try:
                    # lowercase the username
                    # drop the timezone portion of whenChanged (example: '20110526184938.0Z' -> '20110526184938'
                    (firstname, lastname, username, whenchanged) = (ldapuser['givenName'][0], ldapuser['sn'][0], ldapuser['sAMAccountName'][0].lower(), ldapuser['whenChanged'][0].split('.')[0])
                    #sys.stdout.write("%s %s %s: " % (ldapuser['givenName'][0], ldapuser['sn'][0], ldapuser['sAMAccountName'][0]))
                except KeyError:
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

                self.users.append({'username': username, 'firstname': firstname, 'lastname': lastname, 'password_hash': password_hash, 'password_hash_function': password_hash_function, 'whenchanged': whenchanged})
        l.unbind()
        return

