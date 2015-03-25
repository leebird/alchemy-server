import sys
import os


def django_init():
    sys.path.append('/home/leebird/Projects/alchemy-server')
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alchemy_django.settings")

    import django
    django.setup()