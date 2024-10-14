import os
import dj_database_url
from .settings import *

DEBUG = False

SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['productnest-prod-e7a7c2e04fb9.herokuapp.com']

DATABASES = {
    'default': dj_database_url.config()
}