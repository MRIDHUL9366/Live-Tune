from django.db import models
from django.contrib.auth.models import User
from Admin.models import *
from vendor.models import *

class User_profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, unique=True)
    user_type = models.IntegerField(default=3)


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    select_service = models.ForeignKey(VendorServicePrice, on_delete=models.CASCADE)
    num_people = models.PositiveIntegerField()
    event_name = models.CharField(max_length=255)  # 🔹 Now a simple CharField
    venue_address = models.TextField()
    event_date = models.DateTimeField()
    event_hours = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    booking_date = models.DateTimeField(auto_now_add=True)
    vendor_approval = models.CharField(max_length = 2500, null =True, blank = True)
    payment_approval = models.CharField(max_length=2500, null=True, blank=True)
    admin_approval = models.CharField(max_length=2500, null=True, blank=True)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    vendor_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)



    def __str__(self):
        return f"Booking for {self.event_name} by {self.user.username}"




class CancelledBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    select_service = models.ForeignKey(VendorServicePrice, on_delete=models.CASCADE)
    num_people = models.PositiveIntegerField()
    event_name = models.CharField(max_length=255)
    venue_address = models.TextField()
    event_date = models.DateTimeField()
    event_hours = models.PositiveIntegerField()
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    commission_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    user_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    booking_date = models.DateTimeField()
    cancelled_date = models.DateTimeField(auto_now_add=True)  # Stores when the booking was canceled

    def __str__(self):
        return f"Cancelled: {self.event_name} - {self.user.username}"


class UserReview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField()
    review = models.TextField()

    def __str__(self):
        return f"{self.user.username} - {self.vendor.name} ({self.rating})"


class MonthlyEarnings(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="monthly_user")
    vendor = models.ForeignKey(Vendor, on_delete=models.CASCADE, related_name="monthly_vendor")
    booking = models.ForeignKey(Booking, on_delete=models.SET_NULL, null=True, blank=True, related_name="monthly_booking")  # ✅ Allow NULL
    amount = models.CharField(max_length=150)
    date = models.DateField()
    status = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.status}"
