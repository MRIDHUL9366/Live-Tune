from django.urls import path
from . import views

urlpatterns = [
    path('vendor-module', views.vendor_registration, name='vendor-module'),
    path('vendor_login', views.vendor_login, name='vendor_login'),
    path('vendor_dashboard', views.vendor_dashboard, name='vendor_dashboard'),
    path('vendor_logout', views.vendor_logout, name='vendor_logout'),
    path('profile_setting', views.profile_setting, name='profile_setting'),
    #artist_management_section
    path('artist_management', views.artist_management, name='artist_management'),
    path('edit_artist/<int:artist_id>/', views.edit_artist, name='edit_artist'),
    path('delete_artist/<int:artist_id>/', views.delete_artist, name='delete_artist'),
    #manage_performance
    path('vendor_service', views.vendor_service, name='vendor_service'),
    path('vendor_delete/<int:service_id>/', views.delete_performance, name='vendor_delete'),
    #manage_vendor_service
    path("manage_vendor_service", views.manage_vendor_service, name="manage_vendor_service"),
    #manage_bookings
    path('manage_bookings', views.manage_bookings, name="manage_bookings"),
    path('accept-booking/<int:booking_id>/', views.accept_booking, name='accept_booking'),
    path('reject-booking/<int:booking_id>/', views.reject_booking, name='reject_booking'),
    #vendor_payment_details
    path('vendor_payment_details', views.vendor_payment_details, name='vendor_payment_details'),
    path('Customer_Feedback', views.Customer_Feedback, name="Customer_Feedback")






]