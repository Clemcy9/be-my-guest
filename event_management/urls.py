from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from .views import add_guest,add_guests, create_event,view_guest, download_invites

app_name = 'event_management'

urlpatterns = [
    path('', create_event, name='create_event'),
    path('add_guests/<int:event_id>', add_guests, name='add_guests'),
    path('add_guest/', add_guest, name='add_guest'),
    path('view_guest/<int:guest_id>', view_guest, name='view_guest'),
    path('download_invite/<str:zip_filename>', download_invites, name='download_invites'),
] 