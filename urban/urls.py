from django.urls import path,include
from . import views
from django.contrib.auth.views import LoginView

urlpatterns = [
    path('',views.home_view,name='home'),

    path('register',views.register_view,name='register'),
    path('login',views.login_view,name='login'),

    path('adminlogin', LoginView.as_view(template_name='owner/admin_login.html'),name='adminlogin'),

    path('afterlogin',views.afterlogin_view,name='afterlogin'),
    path('accounts/profile/',views.afterlogin_view,name='accounts/profile/'),

    path('admin-dashboard',views.admin_dashboard_view,name='admin-dashboard'),

    path('worker-request',views.worker_request_view,name='worker-request'),
    path('approve-worker/<int:pk>',views.approve_worker_view,name='approve-worker'),
    path('admin-approve-worker',views.admin_approve_worker,name='admin-approve-worker'),
    path('reject-worker/<int:pk>',views.reject_worker_view,name='reject-worker'),

    path('manage-worker',views.manage_worker_view,name='manage-worker'),
    path('update-worker/<int:pk>',views.update_worker_view,name='update-worker'),
    path('delete-worker/<int:pk>',views.delete_worker_view,name='delete-worker'),

    path('manage-consumer',views.manage_consumer_view,name='manage-consumer'),
    path('update-consumer/<int:pk>',views.update_consumer_view,name='update-consumer'),
    path('delete-consumer/<int:pk>',views.delete_consumer_view,name='delete-consumer'),
    path('workerlogin',LoginView.as_view(template_name='worker/worker_login.html'),name='workerlogin'),
    path('worker-signup',views.worker_signup_view,name='worker-signup'),

    path('worker-dashboard',views.worker_dashboard_view,name='worker-dashboard'),
    path('worker-profile',views.worker_profile_view,name='worker-profile'),

    path('services',views.services_view,name='services'),
    path('update-service/<int:pk>',views.update_services_view,name='update-service'),
    path('delete-service/<int:pk>',views.delete_service_view,name='delete-service'),

    path('bookings',views.bookings_view,name='bookings'),
    path('approve-booking/<int:pk>',views.approve_booking_view,name='approve-booking'),
    path('reject-booking/<int:pk>',views.reject_booking_view,name='reject-booking'),
    path('consumerlogin',LoginView.as_view(template_name='consumer/consumer_login.html'),name='consumerlogin'),
    path('consumer-signup',views.consumer_signup_view,name='consumer-signup'),

    path('consumer-dashboard',views.consumer_dashboard_view,name='consumer-dashboard'),
    path('consumer-profile',views.consumer_profile_view,name='consumer-profile'),
    path('search',views.search_view,name='search'),

    path('add-to-cart/<int:pk>',views.add_to_cart_view,name='add-to-cart'),
    path('cart',views.cart_view,name='cart'),
    path('remove-service-from-cart/<int:pk>',views.remove_service_from_cart,name='remove-service-from-cart'),
    path('consumer-address', views.consumer_address_view,name='consumer-address'),
    path('payment', views.payment_view,name='payment'),

    path('payment-success', views.payment_success_view,name='payment-success'),

    path('my-bookings',views.my_bookings_view,name='my-bookings'),
    path('delete-booking/<int:pk>',views.delete_booking_from_mybookings,name='delete-booking'),
    path('consumerlogin',LoginView.as_view(template_name='consumer/consumer_login.html'),name='consumerlogin'),
    path('consumer-signup',views.consumer_signup_view,name='consumer-signup'),

    path('consumer-dashboard',views.consumer_dashboard_view,name='consumer-dashboard'),
    path('consumer-profile',views.consumer_profile_view,name='consumer-profile'),
    path('search',views.search_view,name='search'),

    path('add-to-cart/<int:pk>',views.add_to_cart_view,name='add-to-cart'),
    path('cart',views.cart_view,name='cart'),
    path('remove-service-from-cart/<int:pk>',views.remove_service_from_cart,name='remove-service-from-cart'),
    
    # path('consumer-address',views.consumer_address_view,name='consumer-address'),
    # path('payment-success',views.payment_success_view,name='payment-success'),
    path('consumer-address', views.consumer_address_view,name='consumer-address'),
    path('payment-success', views.payment_success_view,name='payment-success'),

    path('my-bookings',views.my_bookings_view,name='my-bookings'),
    path('delete-booking/<int:pk>',views.delete_booking_from_mybookings,name='delete-booking'),

    path('amountpay<int:booking_id>/',views.amountpay_view,name='amountpay'),
    path('pay-success/<int:id>/',views.paysuccess_view,name='pay-success'),
    path('view-payment/',views.view_payment_details,name='view-payment'),
    path('singlepayment/',views.singlepayment_view,name='singlepayment'),
    path('payment-details/<int:worker_id>/',views.worker_payment_details,name='payment_details'),
    path('chat/<int:rec_id>/',views.chat,name='chat'),
    path('chat_message/<int:receiverid>/',views.chat_message,name='chat_message'),
]
