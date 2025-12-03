from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate, login
from .models import *
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from vendor.models import *
from decimal import Decimal
from django.db.models import Q
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from django.db.models import Avg



def user_registration(request):
    if request.method == "POST":
        name = request.POST.get("Name")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        username = request.POST.get("username")
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, "Passwords do not match!")
            return redirect('user-module')

        # Check if username or email already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken!")
            return redirect('user-module')

        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already taken!")
            return redirect('user-module')

        if User_profile.objects.filter(phone=phone).exists():
            messages.error(request, "Phone number already registered!")
            return redirect('user-module')

        # Create user with hashed password
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,  # Automatically hashes password
            first_name=name
        )
        # Create user profile
        User_profile.objects.create(user=user, phone=phone)

        messages.success(request, "Registration successful! Please log in.")
        return redirect('User_Login')
    return render(request, "user_registration.html")


def User_Login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # Check if the user has a linked User_profile
            try:
                if user.user_profile.user_type == 3:  # Regular user
                    login(request, user)
                    return redirect('user_homepage')
                else:
                    messages.error(request, "Access Denied! Only regular users are allowed to log in.")
                    return redirect('User_Login')

            except User_profile.DoesNotExist:
                messages.error(request, "User profile not found! Contact support.")
                return redirect('User_Login')

        else:
            messages.error(request, "Invalid username or password!")
            return redirect('User_Login')

    return render(request, 'user_login.html')



def user_logout(request):
    return redirect('main_home')


def user_homepage(request):
    query = request.GET.get('q', '').strip()

    if query:
        terms = query.split()
        q_objects = Q()

        for term in terms:
            # Search each term in group name OR service name
            q_objects |= Q(group_name__icontains=term)
            q_objects |= Q(user__vendorserviceprice__service__name__icontains=term)

        all_vendors = Vendor.objects.filter(q_objects).distinct()
    else:
        all_vendors = Vendor.objects.all()

    return render(request, "user_main_homepage.html", {'all_vendors': all_vendors, 'query': query})



#edit_user

@login_required
def edit_user_profile(request):
    user = request.user
    user_details, created = User_profile.objects.get_or_create(user=user)

    if request.method == "POST":
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        email = request.POST.get('email')
        username = request.POST.get('username')
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        # Update user details
        user.first_name = name
        user.email = email
        user.username = username
        user_details.phone = phone

        # Handle password change
        if old_password and new_password and confirm_password:
            if user.check_password(old_password):
                if new_password == confirm_password:
                    user.set_password(new_password)
                    messages.success(request, "Password updated successfully.")
                else:
                    messages.error(request, "New passwords do not match.")
            else:
                messages.error(request, "Old password is incorrect.")

        user.save()
        user_details.save()
        messages.success(request, "Profile updated successfully.")
        return redirect('user_homepage')

    context = {
        'name': user.first_name,
        'email': user.email,
        'username': user.username,
        'phone': user_details.phone
    }
    return render(request, "edit_user.html", context)


#Booking section

def user_vendor_view(request, vendor_id):
    selected_vendor = get_object_or_404(Vendor, id=vendor_id)
    service_select = VendorServicePrice.objects.filter(vendor = selected_vendor.user_id)
    performance = PerformanceManagement.objects.filter(vendor=vendor_id)
    artist = Artist.objects.filter(vendor=vendor_id)
    review = UserReview.objects.filter(vendor=vendor_id)
    context = {
        "selected_vendor": selected_vendor,
        "service_select": service_select,
        "performance": performance,
        "artist": artist,
        "review": review,
    }
    return render(request, "user_performance_view.html", context)



def book_now(request, vendor_id):
    vendor = get_object_or_404(Vendor, id=vendor_id)
    user = request.user
    service = VendorServicePrice.objects.filter(vendor=vendor.user_id)

    if request.method == "POST":
        event_name = request.POST.get("event_name")
        venue_address = request.POST.get("venue_address")
        service_package_id = request.POST.get("service_package")
        num_people = request.POST.get("num_people")
        custom_people = request.POST.get("customPeople")
        event_duration = request.POST.get("event_duration")
        booking_date = request.POST.get("booking_date")
        total_cost = request.POST.get("Total_cost")

        # Convert total_cost to Decimal to avoid precision errors
        total_cost = Decimal(total_cost)

        # ✅ Take custom value if available, otherwise take the selected one
        final_num_people = custom_people if custom_people else num_people

        # ✅ Fetch the selected service package
        service_package = get_object_or_404(VendorServicePrice, id=service_package_id)

        # ✅ Check if the user has already booked this service with the same vendor
        existing_booking = Booking.objects.filter(
            user=user, vendor=vendor, select_service=service_package
        ).exists()

        if existing_booking:
            messages.warning(request, "You have already booked this service with this vendor!")
            return redirect("book_now", vendor_id=vendor.id)

        # ✅ Calculate Commission and Vendor Amount
        commission_percentage = Decimal("0.10")  # 10%
        commission_amount = total_cost * commission_percentage  # 10% of total amount
        vendor_amount = total_cost - commission_amount  # Remaining 90% for vendor

        # ✅ Save Booking if no existing booking found
        booking = Booking.objects.create(
            user=user,
            vendor=vendor,
            select_service=service_package,
            num_people=final_num_people,  # Save the final value
            event_name=event_name,
            venue_address=venue_address,
            event_date=booking_date,
            event_hours=event_duration,
            total_amount=total_cost,
            commission_amount=commission_amount,  # Save calculated commission
            vendor_amount=vendor_amount,  # Save calculated vendor amount
            vendor_approval="pending",
            payment_approval="pending",
            admin_approval="pending",

        )
        formatted_date = datetime.strptime(booking_date, "%Y-%m-%dT%H:%M").date()
        monthly_chart = MonthlyEarnings.objects.create(
            user = user,
            vendor = vendor,
            amount = commission_amount,
            date = formatted_date,
            status = "Booked",
            booking = booking
        )

        messages.success(request, "Your booking has been confirmed successfully!")
        return redirect("user_booking_details")

    context = {
        "vendor": vendor,
        "user": user,
        "service": service
    }
    return render(request, "book_now.html", context)



def user_booking_details(request):
    user_booking = Booking.objects.filter(user = request.user)
    return render(request,"user_booking_details.html",{'user_booking':user_booking})


def user_payment(request, booking_id):
    # Fetch the booking instance
    user_booking = get_object_or_404(Booking, id=booking_id)

    # Check if vendor approval is pending
    if user_booking.vendor_approval != "Accepted":
        messages.warning(request, "Payment cannot be made until vendor approval is received.")
        return redirect("user_booking_details")

    # If approved, update payment status to 'Paid'
    user_booking.payment_approval = "Paid"
    user_booking.save()

    messages.success(request, "Your booking has been confirmed and payment is successful!")
    return redirect("user_booking_details")

# add this cancel section
def user_booking_cancel(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Ensure both values are datetime objects for accurate comparison
    event_datetime = timezone.make_aware(
        datetime.combine(booking.event_date, datetime.min.time())
    )

    # Check if the event is at least 24 hours away
    if event_datetime - timezone.now() < timedelta(days=1):
        messages.error(request, "You can only cancel a booking at least 24 hours before the event.")
        return redirect("user_booking_details")

    # Get MonthlyEarnings entry safely
    monthly_earning = MonthlyEarnings.objects.filter(booking=booking).first()

    if booking.payment_approval == "pending":
        if monthly_earning:
            monthly_earning.delete()
        booking.delete()
        messages.error(request, "No service fee was deducted.")
        return redirect("user_booking_details")

    # Calculate commission & user amount
    commission_amount = booking.total_amount * Decimal('0.05')  # 5% of total amount
    user_amount = booking.total_amount - commission_amount

    # Move data to CancelledBooking
    CancelledBooking.objects.create(
        user=booking.user,
        vendor=booking.vendor,
        select_service=booking.select_service,
        num_people=booking.num_people,
        event_name=booking.event_name,
        venue_address=booking.venue_address,
        event_date=booking.event_date,
        event_hours=booking.event_hours,
        total_amount=booking.total_amount,
        booking_date=booking.booking_date,
        commission_amount=commission_amount,
        user_amount=user_amount
    )

    # Update MonthlyEarnings instead of deleting
    if monthly_earning:
        monthly_earning.amount = commission_amount
        monthly_earning.status = "Cancel"
        monthly_earning.save()

    # Delete the booking
    booking.delete()

    messages.success(request, "Your booking has been successfully canceled.")
    return redirect("user_booking_details")


def user_cancellation_details(request):
    cancellation_details = CancelledBooking.objects.filter(user = request.user)
    return render(request,"payment_confirm.html",{'cancellation_details':cancellation_details})


def generate_pdf(request, booking_id):
    booking = get_object_or_404(CancelledBooking, id=booking_id)

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="booking_{booking_id}.pdf"'

    # Create the PDF document
    pdf = SimpleDocTemplate(response, pagesize=letter)
    elements = []
    styles = getSampleStyleSheet()

    # Title
    title = Paragraph("<b>Booking Cancellation Statement</b>", styles['Title'])
    elements.append(title)

    # Booking Details Table
    data = [
        ["Field", "Details"],
        ["User", booking.user.first_name],
        ["Event Name", booking.event_name],
        ["Service", booking.select_service.service.name],
        ["Vendor", booking.vendor.vendor_name],
        ["Group", booking.vendor.group_name],
        ["Booking Date", booking.booking_date.strftime("%Y-%m-%d")],
        ["Cancellation Date", booking.cancelled_date.strftime("%Y-%m-%d")],
        ["Total Amount Paid", f"₹{booking.total_amount}"],
        ["Cancellation Charge", f"₹{booking.commission_amount}"],
        ["User Refund", f"₹{booking.user_amount}"],
    ]

    table = Table(data, colWidths=[2.5 * inch, 3 * inch])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))

    elements.append(table)

    # Build PDF
    pdf.build(elements)

    return response


def User_Feedback(request):
    # Fetching bookings where the user has paid
    feed_back = Booking.objects.filter(user_id=request.user.id, payment_approval="Paid")

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")
        vendor_id = request.POST.get("vendor")  # Vendor ID from the form

        if not rating or not comment or not vendor_id:
            messages.error(request, "All fields are required.")
            return redirect("User_Feedback")

        try:
            vendor = Vendor.objects.get(id=vendor_id)
        except Vendor.DoesNotExist:
            messages.error(request, "Invalid Vendor.")
            return redirect("User_Feedback")

        # Save the review
        UserReview.objects.create(
            user=request.user,
            vendor=vendor,
            rating=int(rating),
            review=comment
        )
        customer_feedback = UserReview.objects.filter(vendor=vendor)
        # Get or create VendorFeedback entry
        vendor_feedback, created = VendorFeedback.objects.get_or_create(vendor=vendor)

        # Calculate average rating (if reviews exist)
        average_rating = customer_feedback.aggregate(avg_rating=Avg('rating'))['avg_rating']

        if average_rating is not None:
            vendor_feedback.total_review = round(average_rating, 2)  # Keep 2 decimal places
            vendor_feedback.save()

        messages.success(request, "Your Review has been submitted successfully.")
        return redirect("User_Feedback")

    return render(request, "User_Feedback.html", {"feed_back": feed_back})
