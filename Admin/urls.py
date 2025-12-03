from django.urls import path
from . import views

urlpatterns = [
    path('', views.main_home, name='main_home'),
    path('admin_register', views.admin_register, name='admin_register'),
    path('Admin_Login', views.Admin_Login, name="Admin_Login"),
    path('admin_dashboard', views.admin_dashboard, name="admin_dashboard"),
    path('home_service', views.home_service, name='home_service'),
    path('about_livetune', views.about_livetune, name="about_livetune"),
    path('logout', views.logout, name="logout"),
    #vendor_management_section
    path('manage_vendor', views.manage_vendor, name="manage_vendor"),
    path("approve_vendor/<int:vendor_id>/", views.approve_vendor, name="approve_vendor"),
    path("reject_vendor/<int:vendor_id>/", views.reject_vendor, name="reject_vendor"),
    path('service_view/<int:vendor_id>/', views.service_view, name='service_view'),
    #service_management_section
    path('service_management', views.service_management, name='service_management'),
    path('add_service', views.add_service, name='add_service'),
    path('edit_service/<int:service_id>/', views.edit_service, name='edit_service'),
    path('delete_service/<int:service_id>/', views.delete_service, name='delete_service'),
    path('manage_users', views.manage_users, name='manage_users'),
    path('manage_booking', views.manage_booking, name='manage_booking'),
    path('payment_refund', views.payment_refund, name='payment_refund'),
    path('payment_approved/<int:booking_id>/', views.payment_approved, name="payment_approved"),
    #announcement_section
    path("add_announcement", views.add_announcement, name="add_announcement"),
    path('monthly_chart', views.monthly_chart, name="monthly_chart"),


]