"""
WSGI config for e_service project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/wsgi/
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'e_service.settings')

_application = get_wsgi_application()

def application(environ, start_response):
    # This forces the generator to evaluate into a single byte string
    # preventing mod_wsgi from accidentally printing the list brackets.
    response = _application(environ, start_response)
    return [b"".join(response)]