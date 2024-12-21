import os
from threading import Thread
from django.conf import settings
from django.http import Http404, FileResponse
from django.shortcuts import render, HttpResponsePermanentRedirect, redirect
from django.forms import modelformset_factory

from .models import Event, Guest, SignUpGuest, generate_qrcode, generate_zip
from .forms import AddGuestForm, CreateEventForm

# Event - create, read, update, delete

# Guest - Add -single
#             -multiple
#       - Read - all guests per event (authorization required)
#              - individual guest via qr code
#       - Update
#       - Delete

# # create worker thread
# image_maker = Thread(target=generate_qrcode, daemon=True, args=[])

def create_event(request):
    form = CreateEventForm()
    if request.method == 'POST':
        form = CreateEventForm(request.POST, request.FILES)
        if form.is_valid():
            instance = form.save()
            return redirect('event_management:add_guests',instance.id)
        else:
            print(f'form errors: {form.errors}')
    else:
        return render(request, 'event/create_event.html', {'form':form})

def add_guest(request):
    form = AddGuestForm()
    if request.method == 'POST':
        form = AddGuestForm(data=request.POST)
        if form.is_valid:
            form.save()
            return render(request, 'guests/add_guest.html')
    else:

        return render(request, 'guests/add_guest.html',{'form':form})

def add_guests(request, event_id):
    event = Event.objects.get(id=event_id)
    form = AddGuestForm()
    GuestFormset = modelformset_factory(Guest, AddGuestForm,extra=event.expected_no_of_guests)
    if request.method == 'POST':
        # data = request.POST.copy() #request.POST can't be directly mutilated hence we copy it
        # data['event'] = event
        formset = GuestFormset(data=request.POST)
        if formset.is_valid:
            print(f'errors in formset: {formset.errors}')
            instances = formset.save(commit=False)
            # list to hold images
            images = []
            for instance in instances:
                # if not image_maker.is_alive():
                #         image_maker.start()
                #         print(f'[tasks-get_messages] sms_msg thread started')
                instance.event = event
                instance.save()
                print(f'[view-add_guest] image_url:{instance.event.flier.url}')
                image =generate_qrcode(
                    instance.event.flier.url,
                    'https://google.com?MyGodIsAwesome'+'/'+str(instance.id),
                    instance.name
                )
                images.append(image)
            generate_zip(images,event.name +'.zip')

            return redirect('event_management:download_invites',instance.event.name)
    else:
        guest_formset = GuestFormset(queryset=Guest.objects.none())
        return render(request, 'guests/add_guest.html',{'formset':guest_formset})

def view_guest(request, guest_id):
    guest = Guest.objects.get(id=guest_id)
    image = guest.event.flier
    return render(request, 'guests/view_guest.html', {'guest':guest,'image':image})

# edit events with guest
def edit_event(request, event_id):
    event = Event.objects.get(id=event_id)
    form = AddGuestForm()
    GuestFormset = modelformset_factory(Guest, AddGuestForm,extra=event.expected_no_of_guests)
    if request.method == 'POST':
        # data = request.POST.copy() #request.POST can't be directly mutilated hence we copy it
        # data['event'] = event
        formset = GuestFormset(data=request.POST)
        if formset.is_valid:
            print(f'errors in formset: {formset.errors}')
            instances = formset.save(commit=False)
            for instance in instances:
                instance.event = event
                instance.save()
            return render(request, 'guests/add_guest.html')
    else:
        guest_formset = GuestFormset(queryset=Guest.objects.filter(id=event_id))
        return render(request, 'guests/add_guest.html',{'formset':guest_formset})

def download_invites(request, zip_filename):
    zip_path = os.path.join(settings.MEDIA_ROOT,'generated_zips/' + zip_filename+'.zip')
    print(f'[views-download_invites] zip_path:{zip_path}')
    if not os.path.exists(zip_path):
        raise Http404("file not found")
    
    return FileResponse(open(zip_path, 'rb'), as_attachment=True, filename=zip_filename)