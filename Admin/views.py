from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login
from vendor.models import *
from .models import *
from user.models import *
from decimal import Decimal
from django.db.models import Sum
from collections import defaultdict



def main_home(request):
    all_vendors = Vendor.objects.prefetch_related('user__vendorserviceprice_set').all()
    return render(request, "main_home.html", {'all_vendors': all_vendors})

def about_livetune(request):
    return render(request, "about_livetune.html")



def admin_register(request):
    if request.method == "POST":
        username = request.POST.get("username")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm-password")

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return render(request, 'admin_registration.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return render(request, 'admin_registration.html')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered!")
            return render(request, 'admin_registration.html')

        # Create new admin user
        user = User.objects.create_user(username=username, email=email, password=password)
        user.is_staff = 1  # Mark as admin (but not superuser)
        user.save()

        messages.success(request, "Admin registered successfully! You can now log in.")
        return redirect(Admin_Login)  # Redirect to login page after success

    return render(request, 'admin_registration.html')


def Admin_Login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:  # Ensuring only admins can log in
            login(request, user)
            messages.success(request, "Admin login successful!")
            return redirect(admin_dashboard)  # Change this to your admin dashboard URL name
        else:
            messages.error(request, "Invalid credentials or not an admin!")

    return render(request, "admin_login.html")

def logout(request):
    return render(request, "main_home.html")

def home_service(request):
    home_service = Service.objects.all()
    return render(request, "home_service.html", {'home_service': home_service})

def admin_dashboard(request):
    vendors = Vendor.objects.all()
    total_vendors = Vendor.objects.count()
    total_users = User_profile.objects.count()
    total_bookings = Booking.objects.count()
    latest_bookings = Booking.objects.order_by('-booking_date')[:4]  # Get latest booking
    total_amount = AdminEarnings.objects.get(id=1)
    notification = AdminNotification.objects.all().order_by('-created_at')
    total_monthly_earnings = MonthlyEarnings.objects.all()

    # Initialize earnings dictionary for each month (default to 0)
    monthly_earnings_dict = defaultdict(int)

    # Aggregate total earnings month-wise
    for earning in total_monthly_earnings:
        month_index = earning.date.month - 1  # Convert month (1-12) to index (0-11)
        monthly_earnings_dict[month_index] += int(float(earning.amount))  # Convert properly

    # Convert dictionary to a list with 12 months, ensuring missing months default to 0
    monthly_earnings = [monthly_earnings_dict[i] for i in range(12)]

    context = {
        'vendors': vendors,
        'total_vendors': total_vendors,
        'total_users': total_users,
        'total_bookings': total_bookings,
        'latest_booking': latest_bookings,  # Pass latest booking
        'total_amount': total_amount,
        "notification": notification,
        'monthly_earnings': monthly_earnings  # Pass the calculated monthly earnings
    }

    return render(request, "admin_dashboard.html", context)



#manage_vendor approval and rejection
def manage_vendor(request):
    vendors = Vendor.objects.all()
    return render(request, "manage_vendors.html", {'vendors':vendors})

def approve_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.approval = "Approved"
    vendor.save()
    AdminNotification.objects.create(message=f"Approved {vendor.group_name}")
    return redirect('manage_vendor')

def reject_vendor(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    vendor.approval = "Rejected"
    vendor.save()
    AdminNotification.objects.create(message=f"Reject {vendor.group_name}")
    return redirect('manage_vendor')

def service_view(request, vendor_id):
    vendor = Vendor.objects.get(id= vendor_id)
    vendor_service =VendorServicePrice.objects.filter(vendor_id = vendor.user_id)
    return render(request, "vendor_service_view.html", {'vendor_service': vendor_service})

#End vendor approval and rejection section
#Start service management section

def service_management(request):
    services = Service.objects.all()
    return render(request, "service_management.html",{'services':services})

def add_service(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        photo = request.FILES.get('photo')  # Handling file upload

        # Save data to the database
        Service.objects.create(name=name, description=description, photo=photo)
        AdminNotification.objects.create(message=f"Add new  service{name}")

        return redirect('service_management')

    return render(request, 'add_services.html')


def edit_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)

    if request.method == 'POST':
        service.name = request.POST.get('name', service.name)
        service.description = request.POST.get('description', service.description)

        if 'image' in request.FILES:  # If user uploads a new image
            service.photo = request.FILES['image']


        service.save()
        AdminNotification.objects.create(message=f"Edit {service.name} service")
        return redirect('service_management')  # Change to your service listing page

    return render(request, "edit_service.html", {'service': service})



def delete_service(request,service_id):
    service = Service.objects.get(id = service_id)
    AdminNotification.objects.create(message=f"Delete {service.name} service")
    service.delete()
    return redirect('service_management')

#Start service management section

def manage_users(request):
    users = User_profile.objects.all()
    return render(request, "manage_users.html",{'users':users})


def manage_booking(request):
    bookings = Booking.objects.all()  # Fetch all booking records
    return render(request, "manage-bookings.html", {"bookings": bookings})

def payment_refund(request):
    paid_bookings = Booking.objects.filter(payment_approval="Paid")
    cancel_bookings = CancelledBooking.objects.all()

    # Fetch the existing AdminEarnings object (assuming there is only one record)
    total_amount, created = AdminEarnings.objects.get_or_create(id=1)  # Change this logic as needed

    # Calculate earnings from Paid Bookings
    total_paid_commission = paid_bookings.aggregate( total_commission=Sum('commission_amount')    )['total_commission'] or Decimal('0.00')

    # Calculate earnings from Cancelled Bookings
    total_cancel_commission = cancel_bookings.aggregate(total_commission=Sum('commission_amount'))['total_commission'] or Decimal('0.00')

    # Update the existing AdminEarnings values
    total_amount.booking_earnings = total_paid_commission
    total_amount.cancel_earnings = total_cancel_commission
    total_amount.total_earnings = total_paid_commission + total_cancel_commission  # Sum of both earnings
    total_amount.save()


    context = {
        "bookings": paid_bookings,
        "cancel_bookings": cancel_bookings,
        "total_amount":total_amount
    }

    return render(request, "payment_refund.html", context)



def payment_approved(request, booking_id):
    if request.method == "POST":
        booking_approval = get_object_or_404(Booking, id=booking_id)

        # Update the booking status
        booking_approval.admin_approval = "Release"
        booking_approval.save()
        messages.success(request, f"Payment  Released successfully.")

        return redirect("payment_refund")




def add_announcement(request):
    if request.method == "POST":
        title = request.POST.get("title")
        message = request.POST.get("message")

        if title and message:  # Ensure fields are filled
            AdminAnnouncement.objects.create(title=title, message=message)

            # Keep only the latest 3 announcements, delete older ones
            announcements = AdminAnnouncement.objects.all().order_by("-created_at")
            if announcements.count() > 3:
                for announcement in announcements[3:]:  # Delete older announcements beyond the latest 3
                    announcement.delete()

            AdminNotification.objects.create(message="New announcement added")
            return redirect("add_announcement")  # Redirect to clear form and update the page

    # Fetch the latest 3 announcements
    announcements = AdminAnnouncement.objects.all().order_by("-created_at")[:3]

    return render(request, "add_announcement.html", {"announcements": announcements})




def monthly_chart(request):
    monthly_chart = MonthlyEarnings.objects.all()
    return render(request, "monthly_chart.html",{"monthly_chart":monthly_chart})