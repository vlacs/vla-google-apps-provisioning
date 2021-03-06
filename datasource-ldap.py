import ldap
import re

class DataSource:
    usernames = []
    users = []
    count = 0

    def __init__(self, config):
        pass

    def getusers(self, config):
        l = ldap.initialize('ldap://' + config.ldap_host)
        l.simple_bind_s(config.ldap_binddn, config.ldap_pw)
        for searchbase in config.ldap_search_bases:
            try:
                data = l.search_s(searchbase, ldap.SCOPE_SUBTREE, '(objectclass=organizationalperson)')
                self.getusers_searchbase(config, data)
            except Exception, inst:
                print "\n%s: searchbase exception: %s:%s" % (searchbase, type(inst), inst)
                pass
        l.unbind()
        return

    def getusers_searchbase(self, config, data):
        for ldapuser in data:
            self.count += 1
            ldapuser = ldapuser[1]
            try:
                firstname = ldapuser[config.ldap_attrs['firstname']][0]
                lastname = ldapuser[config.ldap_attrs['lastname']][0]
                username = ldap_get_username(config.ldap_attrs['username'], config.google_apps_domain, ldapuser)

                if 'userAccountControl' in config.ldap_attrs and config.ldap_exclude_disabled:
                    # AD uses the second bit of userAccountControl to indicate a disabled account.
                    if 2 & int(ldapuser[config.ldap_attrs['userAccountControl']][0]):
                        print "disabled: %s %s,%s" % (username, lastname, firstname)
                        continue


                # drop the timezone portion of whenChanged (example: '20110526184938.0Z' -> '20110526184938'
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
            except AssertionError, inst:
                print "exception: %s:%s" % (type(inst), inst)
                print ldapuser
                continue
            except Exception, inst:
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
        return

def ldap_get_username(username_attrs, google_apps_domain, ldapuser):
    if username_attrs.__class__.__name__ == 'str':
        # Ensure we have a list.
        username_attrs = [username_attrs]
    for attr in username_attrs:
        if attr in ldapuser:
            username = ldapuser[attr][0].lower()
            # drop the google domain from username, in case it's an email address
            username = username.replace('@' + google_apps_domain, '')
            if len(username) and username.count('@') == 0:
                return username
    raise Exception('no username found')


