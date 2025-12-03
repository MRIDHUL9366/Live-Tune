from django.db import models
from django.utils.timezone import now
from django.contrib.auth.models import User

class Service(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    photo = models.ImageField(upload_to='service_photos/', blank=True, null=True)


class AdminAnnouncement(models.Model):
    title = models.CharField(max_length=255)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class AdminEarnings(models.Model):
    booking_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank= True)  # Commission from bookings
    cancel_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, null=True, blank= True)   # Commission from cancellations
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, editable=False)  # Auto-updated total


    def save(self, *args, **kwargs):
        # Total earnings = Booking Earnings + Cancel Earnings
        self.total_earnings = self.booking_earnings + self.cancel_earnings
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Total Earnings: {self.total_earnings}"


class AdminNotification(models.Model):
    message = models.TextField()
    created_at = models.DateTimeField(default=now)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # Save the new notification

        # Keep only the latest 4 notifications
        notifications = AdminNotification.objects.order_by('-created_at')
        if notifications.count() > 4:
            notifications.last().delete()



