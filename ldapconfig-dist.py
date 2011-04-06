# This script will create new passwords for new Google accounts.
# What is the path/name of the file where you'd like those new username/password pairs stored?
newaccountslogfile = '/root/google-new-accounts.txt'

#######################################################################
# LDAP config

# What is the name or IP address of your LDAP server?
ldap_host = '192.168.0.1'

# We need a DN to bind to your LDAP server. Which one can we use?
ldap_binddn = 'CN=Super LDAP User,OU=Your Domain,DC=com'

# What is the password for the above DN?
ldap_pw = 'ldappy secret'

# Which chunks of your LDAP tree contain users we should provision in Google?
search_dns = (
        'OU=Staff,OU=Users,OU=Some Folks,OU=Your Domain,DC=com',
        'OU=2011 (Seniors),OU=Students,OU=Users,OU=Academic,OU=Some School,OU=Your Domain,DC=com',
        'OU=2012 (Juniors),OU=Students,OU=Users,OU=Academic,OU=Some School,OU=Your Domain,DC=com',
        'OU=2013 (Sophmores),OU=Students,OU=Users,OU=Academic,OU=Some School,OU=Your Domain,DC=com',
        'OU=2014 (Freshman),OU=Students,OU=Users,OU=Academic,OU=Some School,OU=Your Domain,DC=com',
        'OU=Staff,OU=Users,OU=Academic,OU=Some School,OU=Your Domain,DC=com',
        )
#######################################################################

# How many characters long do you want newly created, random passwords to be?
newpwlen = 8

#######################################################################
# GOOGLE config

# What is the email address of an administrative user in your Google apps domain?
google_admin_email = 'someuser@yourdomain.com'

# What is the password of the google_admin_email user in google?
google_admin_pw = 'googley secret'

# What is the name of your Google Apps domain?
google_apps_domain = 'yourdomain.com'
#######################################################################
