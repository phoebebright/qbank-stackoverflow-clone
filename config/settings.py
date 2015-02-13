"""
Django settings for Qbase project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
BASE_DIR = os.path.dirname(os.path.dirname(__file__))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '_4*2bdpg(0f=v&0w4u63l4$*$$i1aigz4yg5ayn86x0kx#51&^'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

TEMPLATE_DEBUG = True

ALLOWED_HOSTS = []


# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'django.contrib.sites',
    # 'allauth',
    # 'allauth.account',
    # 'allauth.socialaccount',
    # 'allauth.socialaccount.providers.facebook',
    # 'allauth.socialaccount.providers.twitter',
    #'theme',
    'questionapp',
    'multiprofile',
    #'bootstrap3',
    "taggit",
    # "badger",
)

SITE_ID = 1

TEMPLATE_CONTEXT_PROCESSORS = (
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.media",
    'django.core.context_processors.request',
    'django.core.context_processors.static',
    'django.contrib.messages.context_processors.messages',

    # "allauth.account.context_processors.account",
    # "allauth.socialaccount.context_processors.socialaccount",

    "questionapp.context_processors.get_quser",
)


MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    # 'badger.middleware.RecentBadgeAwardsMiddleware',

)


AUTHENTICATION_BACKENDS = (

    # Needed to login by username in Django admin, regardless of `allauth`
        "multiprofile.auth_backends.MultiModelBackend",


    # # `allauth` specific authentication methods, such as login by e-mail
    # "allauth.account.auth_backends.AuthenticationBackend",

)


ROOT_URLCONF = 'config.urls'

WSGI_APPLICATION = 'Qbase.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'qbase',                      # Or path to database file if using sqlite3.
        'USER': 'qbase',                      # Not used with sqlite3.
        'PASSWORD': '8773322',                  # Not used with sqlite3.
        'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
        'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
    }
}

TIME_ZONE = 'Europe/Dublin'
LANGUAGE_CODE = 'en-gb'
USE_I18N = False
USE_L10N = False
SITE_ID = 1



# Absolute path to the directory that holds media.
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

STATIC_ROOT = os.path.join(BASE_DIR, 'shared_static')
STATIC_URL = '/shared_static/'


# Additional locations of static files
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'questionapp/static'),
)

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
#    'django.contrib.staticfiles.finders.DefaultStorageFinder',
)


TEMPLATE_DIRS = (
    os.path.join(BASE_DIR,  'templates'),
    os.path.join(BASE_DIR,  'questionapp/templates'),
)

# auth and allauth settings
LOGIN_REDIRECT_URL = '/'
SOCIALACCOUNT_QUERY_EMAIL = True
SOCIALACCOUNT_PROVIDERS = {
    'facebook': {
        'SCOPE': ['email', 'publish_stream'],
        'METHOD': 'js_sdk'  # instead of 'oauth2'
    }
}


MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'


BADGER_TEMPLATE_BASE = 'badger'


PROFILE_MODELS = ['questionapp.models.QUser',]

# minimum points before action can be taken
MIN_POINTS = {
    "VOTE_UP" : 15,
    "FLAG_OFFENSIVE" : 15,
    "POST_IMAGES" : 15,
    "LEAVE_COMMENTS" : 50,
    "VOTE_DOWN" : 25,
    "CLOSE_OWN_QUESTIONS": 15,
    "CLOSE_OTHER_QUESTIONS" : 50,
    "RETAG_OTHER_QUESTIONS" : 25,
    "EDIT_COMMUNITY_WIKI_POSTS" : 25,
    "EDIT_OTHER_POSTS" : 25,
    "DELETE_COMMENTS" : 25,
    "VIEW_OFFENSIVE_FLAGS" : 25,
    "LOCK_POSTS" : 25,
    }

AWARD_POINTS = {
    "ACCEPT_ANSWER" : 2,
    "MY_ANSWER_ACCEPTED" : 15,
    "ASK_QUESTION" : 15,
    "VOTE_ANSWER_UP" : 3,
    "VOTE_ANSWER_DOWN" :  -1,
    "MY_ANSWER_VOTE_ANSWER_UP" : 10,
    "MY_ANSWER_VOTE_ANSWER_DOWN" : -2,
    "VOTE_QUESTION_UP" : 3,
    "VOTE_QUESTION_DOWN" :  -1,
    "MY_QUESTION_VOTE_QUESTION_UP" : 5,
    "MY_QUESTION_VOTE_QUESTION_DOWN" : -2,
    "VOTE_COMMENT_UP" : 1,
    "VOTE_COMMENT_DOWN" :  -1,
    "MY_COMMENT_VOTE_COMMENT_UP" : 1,
    "MY_COMMENT_VOTE_COMMENT_DOWN" : -1,

}
try:
    from settings_local import *
except ImportError:
    pass