from django.contrib import admin
from .models import Event, EventAgent, Guest, SignUpGuest, CheckInLog
# Register your models here.

admin.site.register([Event,EventAgent,Guest, SignUpGuest, CheckInLog])