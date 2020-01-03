"""
Django settings for mehalsgmues project.

"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '8cd-j&jo=-#ecd1jjulp_s*7y$n4tad(0d_g)l=6@n^r8fg3rn'

DEBUG = os.environ.get("JUNTAGRICO_DEBUG", 'True') == 'True'

ALLOWED_HOSTS = ['admin.mehalsgmues.ch', 'localhost', 'my.mehalsgmues.ch', 'mehalsgmues-dev.herokuapp.com']


# Admin Settings
ADMINS = (
    ('Admin', os.environ.get('MEHALSGMUES_ADMIN_EMAIL')),
)
MANAGERS = ADMINS
SERVER_EMAIL = "server@mehalsgmues.ch"


# Application definition

INSTALLED_APPS = [
    'juntagrico',
    'juntagrico_pg',
    # 'juntagrico_crowdfunding',
    'juntagrico_proactive',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.admin',
    # 'report_builder',
    'crispy_forms',
    'impersonate',
    'mehalsgmues',
]

ROOT_URLCONF = 'mehalsgmues.urls'

if os.environ.get('DATABASE_URL'):  # on heroku
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.config(default=os.environ.get('DATABASE_URL'))
    }
else:  # local settings
    DATABASES = {
        'default': {
            'ENGINE': os.environ.get('JUNTAGRICO_DATABASE_ENGINE', 'django.db.backends.sqlite3'),
            'NAME': os.environ.get('JUNTAGRICO_DATABASE_NAME', 'mehalsgmues.db'),
            'USER': os.environ.get('JUNTAGRICO_DATABASE_USER'),  # 'junatagrico',
            # The following settings are not used with sqlite3:
            'PASSWORD': os.environ.get('JUNTAGRICO_DATABASE_PASSWORD'),  # 'junatagrico',
            # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
            'HOST': os.environ.get('JUNTAGRICO_DATABASE_HOST'),  # 'localhost',
            'PORT': os.environ.get('JUNTAGRICO_DATABASE_PORT', False),  # '', # Set to empty string for default.
        }
    }

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.contrib.messages.context_processors.messages',
            ],
            'loaders': [
                'django.template.loaders.filesystem.Loader',
                'django.template.loaders.app_directories.Loader'
            ],
            'debug': True
        },
    },
]

WSGI_APPLICATION = 'mehalsgmues.wsgi.application'


LANGUAGE_CODE = 'de'

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

USE_TZ = True
TIME_ZONE = 'UTC'

DATE_INPUT_FORMATS = ['%d.%m.%Y', ]

AUTHENTICATION_BACKENDS = (
    'juntagrico.util.auth.AuthenticateWithEmail',
    'django.contrib.auth.backends.ModelBackend'
)


MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
]

EMAIL_HOST = os.environ.get('JUNTAGRICO_EMAIL_HOST')
EMAIL_HOST_USER = os.environ.get('JUNTAGRICO_EMAIL_USER')
EMAIL_HOST_PASSWORD = os.environ.get('JUNTAGRICO_EMAIL_PASSWORD')
EMAIL_PORT = int(os.environ.get('JUNTAGRICO_EMAIL_PORT', '25'))
EMAIL_USE_TLS = os.environ.get('JUNTAGRICO_EMAIL_TLS', 'False') == 'True'
EMAIL_USE_SSL = os.environ.get('JUNTAGRICO_EMAIL_SSL', 'False') == 'True'

SESSION_SERIALIZER = 'django.contrib.sessions.serializers.PickleSerializer'

WHITELIST_EMAILS = []


def whitelist_email_from_env(var_env_name):
    email = os.environ.get(var_env_name)
    if email:
        WHITELIST_EMAILS.append(email)


if DEBUG is True:
    for key in os.environ.keys():
        if key.startswith("JUNTAGRICO_EMAIL_WHITELISTED"):
            whitelist_email_from_env(key)

STATIC_ROOT = os.path.join(BASE_DIR, 'static')
STATIC_URL = '/static/'

IMPERSONATE = {
    'REDIRECT_URL': '/my/profile',
}

LOGIN_REDIRECT_URL = "/my/home"

VOCABULARY = {
    'subscription': 'Ernteanteil',
    'subscription_pl': 'Ernteanteile'
}
ORGANISATION_NAME = "meh als gmües"
ORGANISATION_LONG_NAME = "meh als gmües"
ORGANISATION_ADDRESS = {
    "name": "Genossenschaft meh als gmües",
    "street": "Dialogweg",
    "number": "6",
    "zip": "8050",
    "city": "Zürich",
    "extra": "c/o Verein MIR"
}
ORGANISATION_PHONE = ''
ORGANISATION_BANK_CONNECTION = {
    "PC": "",
    "IBAN": "CH80 0900 0000 6170 9835 0",
    "BIC": "POFICHBEXXX",
    "NAME": "PostFinance AG",
    "ESR": ""
}
INFO_EMAIL = "info@mehalsgmues.ch"
SERVER_URL = "www.mehalsgmues.ch"
ADMINPORTAL_NAME = "my.mehalsgmues"
ADMINPORTAL_SERVER_URL = "my.mehalsgmues.ch"
BUSINESS_REGULATIONS = "https://mehalsgmues.ch/betriebsreglement"
BYLAWS = "https://mehalsgmues.ch/statutenpdf"
STYLE_SHEET = "/static/css/mehalsgmues.css"
FAVICON = "/static/img/favicon_mag.ico"
FAQ_DOC = ""
EXTRA_SUB_INFO = ""
ACTIVITY_AREA_INFO = ""
SHARE_PRICE = "250"
PROMOTED_JOB_TYPES = []
PROMOTED_JOBS_AMOUNT = 20
DEPOT_LIST_GENERATION_DAYS = [1, 2, 3, 4, 5, 6, 7]
BILLING = False
BUSINESS_YEAR_START = {"day": 1, "month": 4}
BUSINESS_YEAR_CANCELATION_MONTH = 1
IMAGES = {
    'status_100': '/static/img/indicators/status_100.png',
    'status_75': '/static/img/indicators/status_75.png',
    'status_50': '/static/img/indicators/status_50.png',
    'status_25': '/static/img/indicators/status_25.png',
    'status_0': '/static/img/indicators/single_empty.png',
    'single_full': '/static/img/indicators/single_full.png',
    'single_empty': '/static/img/indicators/single_empty.png',
    'single_core': '/static/img/indicators/single_full.png',
    'core': '/static/img/indicators/single_full.png'
}
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
EMAILS = {
    'welcome': 'mag_mails/welcome_mail.txt',
    'co_welcome': 'mag_mails/welcome_added_mail.txt'
}

CRISPY_TEMPLATE_PACK = 'bootstrap4'

DISCOURSE_BASE_URL = os.environ.get('DISCOURSE_BASE_URL')
DISCOURSE_SSO_SECRET = os.environ.get('DISCOURSE_SSO_SECRET')
