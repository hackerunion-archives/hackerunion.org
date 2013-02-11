import os

BRANDING = 'Hacker Union'
TAGLINE = 'Hacker Union'

KEYWORDS = 'put,keywords,here,at,some,point'
DESCRIPTION = 'Just do it.'

TWITTER = "petri"
LOGIN_REDIRECT_URL = "/"

EMAIL_FORMAT = '%s@hackerunion.org'

#
# Notifications
#

DEFAULT_EMAIL = EMAIL_FORMAT % "no-reply"
NOTIFICATION_EMAIL = DEFAULT_EMAIL 
ERROR_EMAILS = [ os.environ.get('PETRI_OWNER_EMAIL', '') ]

#
# Validation
#

THREAD_ID_LEN = 100
WHERE_MAX_LEN = 200
WHERE_MIN_LEN = 3
TITLE_MAX_LEN = 140
COLOR_MAX_LEN = 9
APPLICATION_MAX_LEN = 2000
APPLICATION_MIN_LEN = 50
TITLE_SNIPPET_LEN = 35

#
# Mentorship
#

MAX_MENTEES = 9

# Plz make sure this is divisible by 2.
INVITATION_CODE_LENGTH = 16
POSTAL_CODE_MAX_LEN = 16

#
# Tags
#

TAG_MAX_LEN = 50

#
# Mailing list integration
#

DISCUSS_LIST_FORMAT = r'talk.%s' 
OFFICIAL_LIST_FORMAT = r'leadership.%s' 
ANNOUNCE_LIST_FORMAT = r'announce.%s' 

#
# Email integration
#

INTERNAL_EMAIL_HEADER = r'X-From-Petri'

#
# Pagination
#

MAX_BULLETINS = 25
