from django.db import models
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import URLValidator
from Admin.models import Service

class Vendor(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    vendor_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15)
    group_name = models.CharField(max_length=255)
    address = models.TextField()
    service = models.CharField(max_length=255, null=True, blank=True)
    approval = models.CharField(null = True, max_length=255)
    group_photo = models.ImageField(upload_to='vendors/', null=True, blank=True)


    def __str__(self):
        return self.vendor_name


class Artist(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)  # Corrected ForeignKey
    artist_name = models.CharField(max_length=255)  # Artist name
    instrument_name = models.CharField(max_length=255)  # Instrument model name
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Price of the instrument
    artist_photo = models.ImageField(upload_to='instrument_photos/', null=True, blank=True)  # Instrument photo

    def __str__(self):
        return f"{self.instrument_name} - {self.artist}"


def validate_media_file(value):
    """ Validate if the uploaded file is either an image or a video """
    valid_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.mp4', '.mov', '.avi', '.mkv', '.webm')
    if not value.name.lower().endswith(valid_extensions):
        raise ValidationError('Invalid file format! Allowed: JPG, PNG, GIF, MP4, MOV, AVI, MKV, WEBM.')

class PerformanceManagement(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    event = models.CharField(max_length=255)  # Event name

    # File upload for images/videos
    performance = models.FileField(
        upload_to='performance/',
        null=True,
        blank=True,
        validators=[validate_media_file]
    )

    # Field for YouTube URL
    youtube_url = models.URLField(null=True, blank=True, validators=[URLValidator()])

    def is_youtube_video(self):
        """ Returns True if a YouTube URL is provided """
        return bool(self.youtube_url and ("youtube.com" in self.youtube_url or "youtu.be" in self.youtube_url))

    def __str__(self):
        return f"{self.event} - {self.vendor}"



class VendorServicePrice(models.Model):
    vendor = models.ForeignKey(User, on_delete=models.CASCADE)  # Linking to the vendor (user)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)  # Linking to the Service model
    price_10_members = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_15_members = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_20_members = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    price_per_person = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def __str__(self):
        return f"{self.vendor.username} - {self.service.name}"



class VendorEarnings(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="earnings")
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.vendor.name} - {self.amount}"



class VendorFeedback(models.Model):
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="feedback")
    total_review = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)





