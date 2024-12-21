import zipfile
import os 
from io import BytesIO

from PIL import Image
import qrcode
from django.conf import settings

from django.core.mail import EmailMessage

from django.db import models
from user_management.models import User
from django.utils.timezone import now
# Create your models here.

class Event(models.Model):
    name = models.CharField(max_length=250, blank=False, null=False)
    owner = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)
    is_one_time_pass_event = models.BooleanField(default=False)
    flier = models.ImageField(upload_to='event_flier/')
    expected_no_of_guests = models.IntegerField(help_text='this value affect no of unique qr coded flier', default=1)
    date = models.DateTimeField()
    venue = models.CharField(max_length=255)

class EventAgent(models.Model):
    agent = models.ForeignKey(to=User, on_delete=models.CASCADE, null=True, blank=True)

class Guest(models.Model):
    name = models.CharField(max_length=255)
    event = models.ForeignKey(to=Event, on_delete=models.CASCADE, null=True, blank=True)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=15)

class SignUpGuest(models.Model):
    user = models.OneToOneField(to=User, on_delete=models.CASCADE)
    guest = models.OneToOneField(to=Guest, on_delete=models.CASCADE)

class CheckInLog(models.Model):
    guest = models.OneToOneField(to=Guest, on_delete=models.CASCADE)
    is_check_in = models.BooleanField(default=False)
    check_in_time = models.DateTimeField(default=now)

class GeneratedInvite(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE, null=True, blank=True)
    no_of_guest = models.IntegerField()
    invite_zip_download_url = models.URLField(max_length=100, blank=True, null=True)

# uses buffer memory and has option for direct file
def generate_zip(images, zipname):
    print(f'[models-generate_zip] called, images:{images}')
    zip_buffer = BytesIO()

    if not zipname:
        with zipfile.ZipFile(zip_buffer, 'w') as zip_file:
            for image_path in images:
                filename = os.path.basename(image_path)
                zip_file.write(image_path, arcname=filename)

                zip_buffer.seek(0)
            return zip_buffer
    else:
        zip_path = os.path.join(settings.MEDIA_ROOT,'generated_zips/'+zipname)
        with zipfile.ZipFile(zip_path, 'w') as zip_file:
            for image_path in images:
                filename = os.path.basename(image_path)
                zip_file.write(image_path, arcname=filename)

            return zip_path
        
def send_email_with_zip(user_email, zip_buffer):
    email = EmailMessage(
        subject="zipped Invites cards",
        body="This email contains invite cards sent as a compressed zip",
        from_email="melcatauto@gmail.com",
        to=user_email,
    )    
    
    email.attach('invites.zip', zip_buffer.read(), 'application/zip')
    email.send()

# this function will return file name of generate images, the name can now be put into a list which 
# will be sent to generate_zip()
def generate_qrcode(main_flier, url_link, guest_name):
    
    # Step 1: Generate the QR code
    qr = qrcode.QRCode(
        version=1,  # Controls the size of the QR Code. Higher number = bigger QR.
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # High error correction level
        box_size=10,  # Size of each box in the QR grid
        border=4,  # Border thickness (minimum is 4 for QR codes)
    )
    qr.add_data(url_link)  # Add your data here
    qr.make(fit=True)

    # Create the QR code image
    qr_code_image = qr.make_image(fill_color="black", back_color="white").convert("RGBA")
    pic3 = qr_code_image.resize((240,240))
    pic3 = pic3.convert("RGBA")

    pic1 = Image.open(os.path.join(settings.MEDIA_ROOT, main_flier).strip('/'))
    w,h = pic1.size
    position = (w-530,h-380)

    pic1.paste(pic3,position)

    # save image with guest surname
    location = 'media/generated_invites/'
    image_name = location + guest_name.split('.')[-1].strip().replace(' ','_')+'.'+main_flier.split('.')[-1]
    pic1.save(image_name)
    return image_name
 