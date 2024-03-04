import environ
from django.core.management.utils import get_random_secret_key

env = environ.Env(SECRET_KEY=(str, get_random_secret_key()), DEBUG=(bool, False))
