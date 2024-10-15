import os
import dj_database_url
from .settings import *


SECRET_KEY = os.environ['SECRET_KEY']

ALLOWED_HOSTS = ['https://swiftbuy-b3ea3a489c05.herokuapp.com/']

DATABASES = {
    'default': dj_database_url.config()
}

DEBUG = False