# This script will create new passwords for new Google accounts.
# What is the path/name of the file where you'd like those new username/password pairs stored?
newaccountslogfile = '/root/google-new-accounts.txt'
missingaccountslogfile = '/root/google-missing-accounts.txt'

# Persistent storage
# Where do we keep persistent data needed by ldapconfig.py?
updatehistory_file = '/root/google-updatehistory.shelf'

# Stock options: datasource-ldap, datasource-db
# new files may be added with new options, see datasource-ldap.py and datasource-db.py for examples
datasource = 'datasource-db'

# How many characters long do you want newly created, random passwords to be?
newpwlen = 8

# If we are going to send hashed passwords to Gogole, what hash are we using?
# This could contain (for example): SHA-1, MD5, or None (for plaintext passwords)
password_hash_function = 'MD5'

#######################################################################
# GOOGLE config

# What is the email address of an administrative user in your Google apps domain?
google_admin_email = 'someuser@yourdomain.com'

# What is the password of the google_admin_email user in google?
google_admin_pw = 'googley secret'

# What is the name of your Google Apps domain?
google_apps_domain = 'yourdomain.com'
#######################################################################





#######################################################################
# DataSourceLDAP: config

## What is the name or IP address of your LDAP server?
#ldap_host = '192.168.0.1'
#
## We need a DN to bind to your LDAP server. Which one can we use?
#ldap_binddn = 'CN=Super LDAP User,OU=Your Domain,DC=com'
#
## What is the password for the above DN?
#ldap_pw = 'ldappy secret'
#
## Is there are password hash we should use when possible? If so, what is the
## name of the LDAP attribute containing the hash?
#ldap_password_hash_attribute = 'division'
#
## Which chunks of your LDAP tree contain users we should provision in Google?
#ldap_search_bases = (
#        'OU=Staff,OU=Users,OU=Some Folks,OU=Your Domain,DC=com',
#        'OU=2011 (Seniors),OU=Students,OU=Users,OU=Academic,OU=Some School,OU=Your Domain,DC=com',
#        'OU=2012 (Juniors),OU=Students,OU=Users,OU=Academic,OU=Some School,OU=Your Domain,DC=com',
#        'OU=2013 (Sophmores),OU=Students,OU=Users,OU=Academic,OU=Some School,OU=Your Domain,DC=com',
#        'OU=2014 (Freshman),OU=Students,OU=Users,OU=Academic,OU=Some School,OU=Your Domain,DC=com',
#        'OU=Staff,OU=Users,OU=Academic,OU=Some School,OU=Your Domain,DC=com',
#        )
#######################################################################

#######################################################################
# DataSourceDB: config

## What type of DB are we using?
## Anything python supports can (theoretically) be used, perhaps with some modifications to dblib.py.
## Currently this is ignored!
## db_type = 'postgres'

## What is the name or IP address of your LDAP server?
#db_host = '192.168.0.1'
#
## What is the name your database?
#db_name = 'somedatabase'
#
## We need a name to conect to the DB server. Which one can we use?
#db_username = 'dbusername'
#
## What is the password for the above username?
#db_pw = 'db secret'
#
## Which table should be queried for users?
#db_table = 'user'
#
## Which field in the db_table has usernames to be matched with google?
#db_field_username = 'username'
#
## Which field in the db_table has passwords to be sent to google?
#db_field_password = 'password'
#
## Which field in the db_table has first names to be sent to google?
#db_field_firstname = 'firstname'
#
## Which field in the db_table has last names to be sent to google?
#db_field_lastname = 'lastname'
#
## Which field in the db_table indicates when the user was last updated?
#db_field_whenupdated = 'datemodified'
#######################################################################


