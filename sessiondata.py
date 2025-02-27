import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "MODLI.settings")  # Replace with your actual settings module
django.setup()

from django.contrib.sessions.models import Session
from django.utils.timezone import now

session_key = "uoadptczyj8f64xeszp26aapjkxszwgz"  # Replace with the actual session key
try:
    session = Session.objects.get(session_key=session_key, expire_date__gte=now())
    session_data = session.get_decoded()
    print(session_data)
except Session.DoesNotExist:
    print("Session does not exist or has expired.")
    