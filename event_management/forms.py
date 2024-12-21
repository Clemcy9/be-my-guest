from django import forms
from .models import Guest, Event

class CreateEventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = '__all__'

        widgets = {
            'name': forms.DateInput(attrs={
                'class':'form-control',
                'placeholder':'Event Name'
            }),
            'flier': forms.FileInput(attrs={
                'class':'form-control',
                'type':'file'
            }),
            'expected_no_of_guests': forms.DateInput(attrs={
                'class':'form-control',
                'placeholder':'number of invitee'
            }),
            'venue': forms.DateInput(attrs={
                'class':'form-control',
                'placeholder':'venue'
            }),
            'date': forms.DateInput(attrs={
                'class':'form-control',
                'type':'date'
            }),
        }


class AddGuestForm(forms.ModelForm):
    class Meta:
        model = Guest
        # fields = '__all__'
        exclude = ['event']




"""

@login_required
@transaction.atomic
def save_rooms(request, property_id):
    property = get_object_or_404(Property, id=property_id)
    rooms = property.rooms.all()
    no_of_rms = property.number_of_rooms
    print(f'[property-save_rooms] property is {property}')
    
    RoomFormSet = modelformset_factory(AddRentedRoom, form=AddRentedRoomForm, extra=0, max_num=no_of_rms)

    if request.method == 'POST':
        room_formset = RoomFormSet(request.POST, queryset=AddRentedRoom.objects.filter(room__in=rooms))
        if room_formset.is_valid():
            print(f'[view-save_rooms] formset cleaned data is :{room_formset.cleaned_data}')
            room_formset.save()
            return redirect(reverse('property_detail', args=[property_id]))
        else:
            for form in room_formset:
                print(f'form errors: {form.errors}')
            print(f'non-field errors: {room_formset.non_form_errors()}')
            return render(request, 'property/add_property.html', {'room_formset': room_formset, 'property': property})
    else:
        print(f'no. of rooms are {no_of_rms}')
        room_formset = RoomFormSet(queryset=AddRentedRoom.objects.filter(room__in=rooms))
        return render(request, 'property/add_property.html', {'room_formset': room_formset, 'property': property})

"""