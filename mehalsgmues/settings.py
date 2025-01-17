"""
Django settings for mehalsgmues project.

"""

import os
from datetime import timedelta


# Build paths inside the project like this: os.path.join(BASE_DIR, ...)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SECRET_KEY = os.environ.get('JUNTAGRICO_SECRET_KEY')

DEBUG = os.environ.get("JUNTAGRICO_DEBUG", 'True') == 'True'

ALLOWED_HOSTS = ['.mehalsgmues.ch', 'localhost']


# Admin Settings
ADMINS = (
    ('Admin', os.environ.get('MEHALSGMUES_ADMIN_EMAIL')),
)
MANAGERS = ADMINS
SERVER_EMAIL = "server@mehalsgmues.ch"


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'mehalsgmues',
    'juntagrico_assignment_request',
    'juntagrico_godparent',
    'mapjob',
    'activityprofile',
    'juntagrico_pg',
    # 'juntagrico_crowdfunding',
    'juntagrico_calendar',
    #'juntagrico_polling',
    'juntagrico',
    'fontawesomefree',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'adminsortable2',
    # 'report_builder',
    'crispy_forms',
    'impersonate',
    'oauth2_provider',
    'corsheaders',
    'qr_code',
    'shortener',
    'multiselectfield',
    'ckeditor',
    'polymorphic',
    'django_admin_shell',
    'import_export'
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
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.i18n',
                'django.template.context_processors.media',
                'django.template.context_processors.static',
                'django.template.context_processors.tz',
                'django.template.context_processors.request',
                'django.contrib.messages.context_processors.messages',
            ],
            'debug': DEBUG
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
TIME_ZONE = 'Europe/Zurich'

DATE_INPUT_FORMATS = ['%d.%m.%Y', ]

AUTHENTICATION_BACKENDS = (
    'juntagrico.util.auth.AuthenticateWithEmail',
    'django.contrib.auth.backends.ModelBackend',
    'oauth2_provider.backends.OAuth2Backend',
)


MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'impersonate.middleware.ImpersonateMiddleware',
    'oauth2_provider.middleware.OAuth2TokenMiddleware',
    'django.contrib.sites.middleware.CurrentSiteMiddleware'
]

CORS_ORIGIN_ALLOW_ALL = False

CORS_ORIGIN_WHITELIST = (
    'https://cloud.mehalsgmues.ch',
)

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

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.ManifestStaticFilesStorage",
    },
}

LOCALE_PATHS = ('locale',)

IMPERSONATE = {
    'REDIRECT_URL': '/my/profile',
}

LOGIN_REDIRECT_URL = "/my/home"

VOCABULARY = {
    'subscription': 'Ernteanteil',
    'subscription_pl': 'Ernteanteile',
    'member': 'Person',
    'member_pl': 'Personen'
}
ORGANISATION_NAME = "meh als gmües"
ORGANISATION_NAME_CONFIG = {"type": "Genossenschaft", "gender": "f"}
ORGANISATION_LONG_NAME = "meh als gmües"
ORGANISATION_ADDRESS = {
    "name": "Genossenschaft meh als gmües",
    "street": "Reckenholzstrasse",
    "number": "150",
    "zip": "8046",
    "city": "Zürich"
}
ORGANISATION_PHONE = ''
ORGANISATION_WEBSITE = {
    "name": "mehalsgmues.ch",
    "url": "https://mehalsgmues.ch"
}
ORGANISATION_BANK_CONNECTION = {
    "PC": "",
    "IBAN": "CH80 0900 0000 6170 9835 0",
    "BIC": "POFICHBEXXX",
    "NAME": "PostFinance AG",
    "ESR": ""
}
CONTACTS = {
    'general': "info@mehalsgmues.ch",
    'for_members': "mitglied@mehalsgmues.ch",
    'for_subscription': "mitglied@mehalsgmues.ch",
    'for_shares': "buchhaltung@mehalsgmues.ch",
}
CONTACTS['technical'] = os.environ.get('MEHALSGMUES_IT_EMAIL', CONTACTS['general'])
BUSINESS_REGULATIONS = "https://mehalsgmues.ch/betriebsreglement"
BYLAWS = "https://mehalsgmues.ch/statutenpdf"
FAQ_DOC = "https://mehalsgmues.ch/mitmachen/faq"
STYLES = {'static': ['css/mehalsgmues.css']}
SCRIPTS = {'template': 'mag/js/page.html'}
EXTRA_SUB_INFO = ""
ACTIVITY_AREA_INFO = ""
ENABLE_SHARES = True
SHARE_PRICE = "250"
PROMOTED_JOB_TYPES = []
PROMOTED_JOBS_AMOUNT = 20
DEPOT_LIST_GENERATION_DAYS = []
BILLING = False
BUSINESS_YEAR_START = {"day": 1, "month": 4}
BUSINESS_YEAR_CANCELATION_MONTH = 1
MEMBERSHIP_END_MONTH = 3
MEMBERSHIP_END_NOTICE_PERIOD = 2

SUB_OVERVIEW_FORMAT = {
    'delimiter': ', ',
    'format': '{amount:.0f}\xa0{type}',
    'part_format': '{type} - CHF {price}'
}

FROM_FILTER = {
    'filter_expression': r'.*@mehalsgmues\.ch',
    'replacement_from': 'server@mehalsgmues.ch'
}

CRISPY_TEMPLATE_PACK = 'bootstrap4'

DISCOURSE_BASE_URL = os.environ.get('DISCOURSE_BASE_URL')
DISCOURSE_SSO_SECRET = os.environ.get('DISCOURSE_SSO_SECRET')
DISCOURSE_API_KEY = os.environ.get('DISCOURSE_API_KEY')

TELEGRAM_GROUP_LINK = os.environ.get('TELEGRAM_GROUP_LINK')

CKEDITOR_CONFIGS = {
    'default': {
        'toolbar': 'Custom',
        'toolbar_Custom': [
            ['Bold', 'Italic', 'Underline'],
            ['NumberedList', 'BulletedList', '-', 'Outdent', 'Indent', '-', 'JustifyLeft', 'JustifyCenter', 'JustifyRight', 'JustifyBlock'],
            ['Link', 'Unlink'],
            ['RemoveFormat', 'Source']
        ]
    },
}

SHARE_PROGRESS_GOAL = os.environ.get('SHARE_PROGRESS_GOAL')
SHARE_PROGRESS_OFFSET = os.environ.get('SHARE_PROGRESS_OFFSET')
SHARE_PROGRESS_BASELINE = os.environ.get('SHARE_PROGRESS_BASELINE')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '[%(asctime)s] %(levelname)s %(message)s'}
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        '': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}

MAILER_RICHTEXT_OPTIONS = {
    'valid_styles': {
        '*': 'color,text-align,font-size,font-weight,font-style,font-family,text-decoration'
    },
    'plugins': 'link lists code',
    'toolbar': "undo redo | bold italic | alignleft aligncenter alignright alignjustify | outdent indent | "
               "bullist numlist | link | fontselect fontsizeselect | code",
}

SUBSCRIPTION_PROGRESS_GOAL = 320

GODPARENT_CONTACT = os.environ.get('GODPARENT_CONTACT')
GODPARENT_SHOW_MENU = True
GODPARENT_MEMBERSHIP_DURATION_LIMIT = timedelta(weeks=52)

ADMIN_SHELL_ONLY_DEBUG_MODE = False

OAUTH2_PROVIDER = {
    "PKCE_REQUIRED": False
}

IMPORT_EXPORT_EXPORT_PERMISSION_CODE = 'view'

DEFAULT_DEPOTLIST_GENERATORS = ['mehalsgmues.utils.depot_list.mag_depot_list_generation']

BIKE_CODE_HOST = os.environ.get('BIKE_CODE_HOST')
BIKE_CODE_USERNAME = os.environ.get('BIKE_CODE_USERNAME')
BIKE_CODE_PASSWORD = os.environ.get('BIKE_CODE_PASSWORD')
BIKE_CODE_JOB_TYPE = 22

WP_USER = os.environ.get('WP_USER')
WP_PASSWORD = os.environ.get('WP_PASSWORD')
