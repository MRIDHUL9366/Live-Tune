from django.urls import path
from . import views

urlpatterns = [
    path('user-module', views.user_registration, name='user-module'),
    path('User_Login', views.User_Login, name='User_Login'),
    path('user_homepage', views.user_homepage, name='user_homepage'),
    path('user_logout', views.user_logout, name='user_logout'),
    path('edit_user', views.edit_user_profile, name='edit_user'),
    #booking_section
    path('user_vendor_view/<int:vendor_id>', views.user_vendor_view, name='user_vendor_view'),
    path('book_now/<int:vendor_id>', views.book_now, name='book_now'),
    path('user_booking_details', views.user_booking_details, name="user_booking_details"),
    path('user_payment/<int:booking_id>', views.user_payment, name='user_payment'),
    path('user_booking_cancel/<int:booking_id>', views.user_booking_cancel, name='user_booking_cancel'),
    path('Refund', views.user_cancellation_details, name="Refund"),
    path('generate_pdf/<int:booking_id>/', views.generate_pdf, name="generate_pdf"),
    path('User_Feedback', views.User_Feedback, name="User_Feedback"),

]