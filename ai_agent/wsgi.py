"""
WSGI config for ai_agent project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ai_agent.settings') # Make sure this matches your project structure

application = get_wsgi_application()
# Vercel expects the app object to be called 'app' by default in wsgi.py
# If using the vercel.json config above pointing directly to wsgi.py,
# 'application' is usually fine, but renaming to 'app' can sometimes help.
# app = application
