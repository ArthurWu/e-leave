import os, sys

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'

sys.path.append("C:\Python25\Lib\site-packages\django")
sys.path.append(os.path.dirname(__file__))

import django.core.handlers.wsgi
application = django.core.handlers.wsgi.WSGIHandler()
