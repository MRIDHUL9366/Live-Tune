from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.models import User
from .models import *
from Admin.models import *
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from user.models import *
from django.db.models import Avg




def vendor_registration(request):
    service_select = Service.objects.all()

    if request.method == 'POST':
        vendor_name = request.POST.get('vendor_name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        username = request.POST.get('username')
        group_name = request.POST.get('group_name')
        address = request.POST.get('address')
        selected_services = request.POST.getlist('service')  # List of selected service IDs
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        group_photo = request.FILES.get('group_photo')

        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('vendor-module')

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('vendor-module')

        # Create User
        user = User.objects.create_user(username=username, email=email, password=password)
        user.save()

        # Create Vendor
        vendor = Vendor.objects.create(
            user=user,
            vendor_name=vendor_name,
            phone=phone,
            group_name=group_name,
            address=address,
            group_photo=group_photo,
            approval='pending'
        )

        # Save selected services in VendorServicePrice
        for service_id in selected_services:
            service = Service.objects.get(id=service_id)  # Fetch service by ID
            VendorServicePrice.objects.create(
                vendor=user,  # ForeignKey to User
                service=service  # ForeignKey to Service
            )

        messages.success(request, "Vendor registered successfully!")
        return redirect('vendor_login')

    return render(request, "vendor_registration.html", {'service_select': service_select})



def vendor_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        print(password)

        user = authenticate(request, username=username, password=password)

        if user is not None:
            try:
                vendor = Vendor.objects.get(user=user)

                if vendor.approval == "pending":
                    return render(request, "approval.html", {"status": "pending"})  # Show pending message

                elif vendor.approval == "Rejected":
                    return render(request, "approval.html", {"status": "rejected"})  # Show rejected message

                login(request, user)
                messages.success(request, "Login successful!")
                return redirect("vendor_dashboard")  # Redirect to vendor dashboard

            except Vendor.DoesNotExist:
                messages.error(request, "You are not registered as a vendor!")
                return redirect("vendor_login")

        else:
            messages.error(request, "Invalid username or password!")

    return render(request, "vendor_login.html")


def vendor_logout(request):
    return redirect('main_home')


def vendor_dashboard(request):
    user = request.user
    vendor = Vendor.objects.get(user_id = user.id)

    announcements = AdminAnnouncement.objects.all().order_by("-created_at")[:3]
    recent_bookings = Booking.objects.filter(vendor=vendor.id).order_by('-booking_date')[:4]  # Get 2 recent bookings for this vendor
    return render(request, "vendor_dashboard.html", {"recent_bookings": recent_bookings,"announcements":announcements})


@login_required
def profile_setting(request):
    user = request.user
    vendor_details, created = Vendor.objects.get_or_create(user=user)
    all_services = Service.objects.all()

    # Get selected services for the vendor
    selected_services = set(
        VendorServicePrice.objects.filter(vendor=user).values_list("service__id", flat=True)
    )

    if request.method == "POST":
        vendor_name = request.POST.get("vendor_name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        username = request.POST.get("username")
        group_name = request.POST.get("group_name")
        address = request.POST.get("address")
        selected_service_ids = set(map(int, request.POST.getlist("service")))  # Convert to set of IDs
        profile_picture = request.FILES.get("profile_picture")

        new_password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Update User Model
        user.email = email
        user.username = username
        user.save()

        # Update Vendor Model
        vendor_details.vendor_name = vendor_name
        vendor_details.phone = phone
        vendor_details.group_name = group_name
        vendor_details.address = address

        if profile_picture:
            vendor_details.group_photo = profile_picture

        vendor_details.save()  # Save changes to the Vendor model

        # Handle Password Change (Only if a new password is provided)
        if new_password and confirm_password:
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
            else:
                user.set_password(new_password)  # Update password
                user.save()
                messages.success(request, "Password changed successfully. Please log in again.")
                return redirect("vendor_dashboard")

        # Update Vendor Services without deleting all previous records
        existing_services = set(selected_services)

        # Find services to remove
        services_to_remove = existing_services - selected_service_ids
        VendorServicePrice.objects.filter(vendor=user, service__id__in=services_to_remove).delete()

        # Find services to add
        services_to_add = selected_service_ids - existing_services
        for service_id in services_to_add:
            service = Service.objects.get(id=service_id)
            VendorServicePrice.objects.create(vendor=user, service=service)

        messages.success(request, "Profile updated successfully!")
        return redirect("vendor_dashboard")

    context = {
        "vendor_name": vendor_details.vendor_name,
        "phone": vendor_details.phone,
        "email": user.email,
        "username": user.username,
        "group_name": vendor_details.group_name,
        "address": vendor_details.address,
        "selected_services": selected_services,  # Service IDs
        "all_services": all_services,
        "group_photo": vendor_details.group_photo
    }
    return render(request, "vendor_profile_edit.html", context)



#Artist_management_section
def artist_management(request):
    vendor = Vendor.objects.get(user=request.user)
    artist = Artist.objects.filter(vendor = vendor.id)

    if request.method == "POST":
        artist_name = request.POST.get("artist_name")
        instrument = request.POST.get("instrument")
        rate = request.POST.get("rate")
        photo = request.FILES.get("photo")

        if artist_name and instrument and rate:  # Ensure required fields are filled
            artist = Artist.objects.create(
                vendor=vendor,
                artist_name=artist_name,
                instrument_name=instrument,
                price=rate,
                artist_photo=photo
            )
            artist.save()
            return redirect("artist_management")  # Redirect to avoid form resubmission

    context = {
        'vendor':vendor,
        'artist':artist
    }
    return render(request, "artist_management.html", context)


def edit_artist(request, artist_id):
    # Fetch the artist instance
    artist_edit = get_object_or_404(Artist, id=artist_id)

    if request.method == "POST":
        # Get form data
        artist_name = request.POST.get("name")
        instrument_name = request.POST.get("instrument")
        price = request.POST.get("price")
        artist_photo = request.FILES.get("image")  # Get uploaded image if any

        # Update artist details
        artist_edit.artist_name = artist_name
        artist_edit.instrument_name = instrument_name
        artist_edit.price = price

        # Update image only if a new one is uploaded
        if artist_photo:
            artist_edit.artist_photo = artist_photo

        artist_edit.save()  # Save changes

        return redirect("artist_management")  # Redirect after saving

    return render(request, "edit_artist.html", {"artist_edit": artist_edit})


def delete_artist(request, artist_id):
    artist = get_object_or_404(Artist, id=artist_id)
    artist.delete()
    return redirect("artist_management")

#manage_service_section

def vendor_service(request):
    vendor = Vendor.objects.get(user=request.user)
    performance = PerformanceManagement.objects.filter(vendor=vendor)

    if request.method == 'POST':
        event = request.POST.get('event')
        performance_media = request.FILES.get('performance')  # File upload (image/video)
        youtube_url = request.POST.get('youtube_url')  # Get YouTube link

        if event:
            performance_entry = PerformanceManagement(
                vendor=vendor,
                event=event,
                performance=performance_media if performance_media else None,  # Store file if uploaded
                youtube_url=youtube_url if youtube_url else None  # Store YouTube link if provided
            )
            performance_entry.save()
            messages.success(request, "Performance saved successfully!")
            return redirect('vendor_service')
        else:
            messages.error(request, "Please fill all required fields.")

    context = {
        'vendor': vendor,
        'performance': performance
    }
    return render(request, 'manage_vendor_performance.html', context)


def delete_performance(request, service_id):
    service = get_object_or_404(PerformanceManagement, id=service_id)
    service.delete()
    return redirect("vendor_service")

#manage_vender_service
@login_required
def manage_vendor_service(request):
    user = request.user
    vendor_services = VendorServicePrice.objects.filter(vendor= user.id)
    if request.method == "POST":
        service_id = request.POST.get("service")
        price_10_members = request.POST.get("price_10_members")
        price_15_members = request.POST.get("price_15_members")
        price_20_members = request.POST.get("price_20_members")
        price_per_person = request.POST.get("price_per_person")

        if not service_id:
            messages.error(request, "Please select a service.")
            return redirect("manage_vendor_service")

        selected_service = get_object_or_404(Service, id=service_id)

        # Fixing query issue using get_or_create
        vendor_service, created = VendorServicePrice.objects.get_or_create(vendor=user, service=selected_service)

        vendor_service.price_10_members = price_10_members or 0
        vendor_service.price_15_members = price_15_members or 0
        vendor_service.price_20_members = price_20_members or 0
        vendor_service.price_per_person = price_per_person or 0
        vendor_service.save()

        messages.success(request, "Service pricing updated successfully!")
        return redirect("manage_vendor_service")

    return render(request, "vendor_provide_service.html", {"vendor_services": vendor_services})


def manage_bookings(request):
    vendor = Vendor.objects.get(user_id = request.user.id)
    bookings = Booking.objects.filter(vendor_id =vendor.id )
    return render(request, "manage_bookings.html", {"bookings": bookings})



def accept_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.vendor_approval = "Accepted"
    booking.save()
    messages.success(request, "Booking has been accepted.")
    return redirect('manage_bookings')

def reject_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    booking.vendor_approval = "Rejected"
    booking.save()
    messages.error(request, "Booking has been rejected.")
    return redirect('manage_bookings')


def vendor_payment_details(request):
    vendor = Vendor.objects.get(user_id = request.user.id)
    paid_bookings = Booking.objects.filter(payment_approval="Paid", vendor_id = vendor.id)
    cancel_bookings = CancelledBooking.objects.filter(vendor_id= vendor.id)
    context = {
        "paid_bookings": paid_bookings,
        "cancel_bookings": cancel_bookings
    }
    return render(request, "vendor_payment_details.html", context)



def Customer_Feedback(request):
    vendor = Vendor.objects.get(user_id=request.user.id)
    customer_feedback = UserReview.objects.filter(vendor=vendor)

    # Get or create VendorFeedback entry
    vendor_feedback, created = VendorFeedback.objects.get_or_create(vendor=vendor)

    # Calculate average rating (if reviews exist)
    average_rating = customer_feedback.aggregate(avg_rating=Avg('rating'))['avg_rating']

    if average_rating is not None:
        vendor_feedback.total_review = round(average_rating, 2)  # Keep 2 decimal places
        vendor_feedback.save()

    return render(request, "Customer_Feedback.html",{"customer_feedback": customer_feedback, "vendor_feedback": vendor_feedback})







