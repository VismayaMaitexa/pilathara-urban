from django.shortcuts import render
from django.shortcuts import render,redirect
from . import forms
from . import models
from django.contrib.auth.models import User
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from . models import Worker,Consumer,Chatmodel
from .forms import PaymentForm,WorkerUserForm,WorkerForm
from django.http import HttpResponse

# from . forms import ServiceForm

# Create your views here.
def worker_signup_view(request):
    userform = WorkerUserForm()
    workerform = WorkerForm()
    mydict = {'userform': userform, 'workerform': workerform}

    if request.method == 'POST':
        userform = WorkerUserForm(request.POST)
        workerform = WorkerForm(request.POST, request.FILES)  # Pass request.FILES
        if userform.is_valid() and workerform.is_valid():
            user = userform.save()
            user.set_password(user.password)
            user.save()
            worker = workerform.save(commit=False)
            worker.user = user
            worker.save()
            my_patient_group = Group.objects.get_or_create(name='WORKER')
            my_patient_group[0].user_set.add(user)
            return HttpResponseRedirect('workerlogin')

    return render(request, 'worker/worker_signup.html', context=mydict)

def worker_dashboard_view(request):
    serviceform = forms.ServiceForm()
    worker = models.Worker.objects.get(user_id=request.user.id)  # Get the worker associated with the logged-in user
    
    payments = models.Payment.objects.filter(booking__worker=worker, status='Completed')

    if request.method == 'POST':
        serviceform = forms.ServiceForm(request.POST, request.FILES)
        if serviceform.is_valid():
            services = serviceform.save(commit=False)
            services.worker = worker  # Assign the worker to the service
            services.save()
            return HttpResponseRedirect('services')

    return render(request, 'worker/worker_dashboard.html', {
        'serviceform': serviceform,
        'worker': worker,
        'payments': payments,  # Pass the payments list to the template
    })

def worker_profile_view(request):
    worker = models.Worker.objects.get(user_id=request.user.id)
    return render(request,'worker/profile.html',{'worker':worker})

def services_view(request):
    worker = models.Worker.objects.get(user_id=request.user.id)
    services = models.Services.objects.filter(worker=worker)
    return render(request,'worker/services.html',{'worker':worker, 'services':services})

def update_services_view(request, pk):
    service = get_object_or_404(models.Services, id=pk)
    if request.method == 'POST':
        serviceform = forms.ServiceForm(request.POST, request.FILES, instance=service)
        if serviceform.is_valid():
            serviceform.save()
            return redirect('services')  # Redirect to the services list
    else:
        serviceform = forms.ServiceForm(instance=service)
    
    return render(request, 'worker/update_service.html', {'serviceform': serviceform, 'service': service})

def delete_service_view(request,pk):
    services = models.Services.objects.get(id=pk)
    services.delete()
    return redirect('services')

def bookings_view(request):
    # Get the worker associated with the logged-in user
    worker = models.Worker.objects.filter(user=request.user).first()
    
    if not worker:
        return render(request, 'worker/bookings.html', {'data': []})

    # Get the services offered by the worker
    worker_services = models.Services.objects.filter(worker=worker)

    # Fetch bookings for the services provided by the worker
    bookings = models.Booking.objects.filter(service__in=worker_services)

    booked_services = []
    booked_bys = []

    for booking in bookings:
        booked_service = booking.service
        booked_by = models.Consumer.objects.filter(id=booking.consumer.id).first()

        booked_services.append(booked_service)
        booked_bys.append(booked_by)

    # Zip the booked services, consumers, and bookings together for rendering
    data = zip(booked_services, booked_bys, bookings)

    return render(request, 'worker/bookings.html', {'data': data})

def approve_booking_view(request,pk):
    booking = models.Booking.objects.get(id=pk)
    booking.status = 'Approved'
    booking.save()
    return redirect('bookings')

def reject_booking_view(request,pk):
    booking = models.Booking.objects.get(id=pk)
    booking.status = 'Rejected'
    booking.save()
    return redirect('bookings')


from django.shortcuts import render,redirect,reverse
from django.contrib.auth.models import User
from django.shortcuts import render, get_object_or_404

# Create your views here.


def home_view(request):
    return render(request,'owner/home.html')

def register_view(request):
    return render(request,'owner/register.html')

def login_view(request):
    return render(request,'owner/login.html')

def is_consumer(user):
    return user.groups.filter(name='CONSUMER').exists()

def is_worker(user):
    return user.groups.filter(name='WORKER').exists()


# def afterlogin_view(request):
#     if is_consumer(request.user):
#         return redirect('consumer-dashboard')
#     elif is_worker(request.user):
#         account_approval = wmodels.Worker.objects.filter(user_id=request.user.id).first()
#         if account_approval and account_approval.status:  # Check if the worker is approved
#             return redirect('worker-dashboard')
#         else:
#             return render(request, 'owner/waiting_for_approval.html')  # Show waiting page if not approved
#     else:
#         return redirect('admin-dashboard')


def afterlogin_view(request):
    if is_consumer(request.user):
        return redirect('consumer-dashboard')
    elif is_worker(request.user):
        account_approval = wmodels.Worker.objects.filter(user_id=request.user.id).first()
        if account_approval:
            if account_approval.is_approved:  # Check if the worker is approved
                return redirect('worker-dashboard')  # Worker is approved, redirect to dashboard
            else:
                return render(request, 'owner/waiting_for_approval.html')  # Worker is not approved, show waiting page
        else:
            # If no worker profile exists for the user, handle it (you might want to show an error or redirect)
            return redirect('some_error_page')  # Handle this case as appropriate
    else:
        return redirect('admin-dashboard')   
def admin_dashboard_view(request):
    consumer_count = Consumer.objects.count()
    
    # Count workers by approval status
    approved_worker_count = Worker.objects.filter(status='Confirmed').count()
    not_approved_worker_count = Worker.objects.filter(status='Pending').count()
    
    # Pass data to the template
    context = {
        'consumer_count': consumer_count,
        'approved_worker_count': approved_worker_count,
        'not_approved_worker_count': not_approved_worker_count,
    }
    return render(request, 'owner/admin_dashboard.html', context)
def worker_request_view(request):
    workers = wmodels.Worker.objects.filter(is_approved=False)
    return render(request, 'owner/worker_request.html', {'worker': workers})

# def approve_worker_view(request, pk):
#     worker = wmodels.Worker.objects.get(id=pk)
#     worker.is_approved = True  # Set is_approved to True
#     worker.save()
#     return redirect('admin-approve-worker')

def admin_approve_worker(request):
    workers = wmodels.Worker.objects.all()  # Fetch all workers including approved
    return render(request, 'owner/manage_worker.html', {'worker': workers})

# def reject_worker_view(request, pk):
#     worker = wmodels.Worker.objects.get(id=pk)
#     user = User.objects.get(id=worker.user_id)
#     worker.delete()
#     user.delete()
#     return redirect('worker-request')


def approve_worker_view(request, pk):
    worker = wmodels.Worker.objects.get(id=pk)
    worker.is_approved = True  # Set is_approved to True when admin approves the worker
    worker.save()
    return redirect('admin-approve-worker')  # Redirect to admin worker approval page

def reject_worker_view(request, pk):
    worker = wmodels.Worker.objects.get(id=pk)
    user = User.objects.get(id=worker.user_id)
    worker.delete()  # Delete worker record
    user.delete()  # Delete the user associated with the worker
    return redirect('worker-request')  # Redirect to a page showing worker requests

def manage_worker_view(request):
    workers = wmodels.Worker.objects.filter(is_approved=True)
    return render(request, 'owner/manage_worker.html', {'worker': workers})

def update_worker_view(request, pk):
    worker = get_object_or_404(wmodels.Worker, id=pk)
    user = get_object_or_404(User, id=worker.user_id)
    
    if request.method == 'POST':
        workerForm = forms.WorkerForm(request.POST, request.FILES, instance=worker)
        userform = forms.WorkerUserForm(request.POST, instance=user)

        if workerForm.is_valid() and userform.is_valid():
            userform.save()  # Save the updated user instance
            workerForm.save()  # Save the updated worker instance
            return redirect('manage-worker')
        else:
            print(workerForm.errors)  # Debugging line
            print(userform.errors)  # Debugging line
    else:
        userform = forms.WorkerUserForm(instance=user)
        workerForm = forms.WorkerForm(instance=worker)

    return render(request, 'owner/update_worker.html', {
        'workerform': workerForm,
        'userform': userform
    })
def delete_worker_view(request,pk):
    worker=wmodels.Worker.objects.get(id=pk)
    user=User.objects.get(id=worker.user_id)
    worker.delete()
    user.delete()
    return redirect('manage-worker')

def manage_consumer_view(request):
    consumer = models.Consumer.objects.all()
    return render(request,'owner/manage_consumer.html',{'consumer':consumer})

def update_consumer_view(request, pk):
    consumer = get_object_or_404(models.Consumer, id=pk)
    user = get_object_or_404(User, id=consumer.user_id)
    
    if request.method == 'POST':
        consumerform = forms.ConsumerForm(request.POST, request.FILES, instance=consumer)
        userform = forms.ConsumerUserForm(request.POST, request.FILES, instance=user)  # Note: should use 'user' instead of 'consumer'

        if consumerform.is_valid() and userform.is_valid():
            user = userform.save()  # Save the user instance
            consumer = consumerform.save(commit=False)
            consumer.user = user  # Associate the user with the consumer
            consumer.save()
            return redirect('manage-consumer')
    else:
        userform = forms.ConsumerUserForm(instance=user)  # Initialize user form with user instance
        consumerform = forms.ConsumerForm(instance=consumer)  # Initialize consumer form with consumer instance

    return render(request, 'owner/update_consumer.html', {
        'consumerform': consumerform, 
        'consumer': consumer, 
        'userform': userform
    })

def delete_consumer_view(request,pk):
    is_consumer=models.Consumer.objects.get(id=pk)
    user=User.objects.get(id=is_consumer.user_id)
    is_consumer.delete()
    user.delete()
    return redirect('manage-consumer')

from django.shortcuts import render,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect,Http404
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from . models import Booking
# Create your views here.

def consumer_signup_view(request):
    userform=forms.ConsumerUserForm()
    consumerform=forms.ConsumerForm()
    mydict={'userform':userform,'consumerform':consumerform}
    if request.method == 'POST':
        userform=forms.ConsumerUserForm(request.POST)
        consumerform=forms.ConsumerForm(request.POST,request.FILES)
        if userform.is_valid() and consumerform.is_valid():
            user=userform.save()
            user.set_password(user.password)
            user.save()
            consumer=consumerform.save(commit=False)
            consumer.user=user
            consumer.save()
            my_consumer_group = Group.objects.get_or_create(name='CONSUMER')
            my_consumer_group[0].user_set.add(user)
        return HttpResponseRedirect('consumerlogin')
    return render(request,'consumer/consumer_signup.html',context=mydict)

def consumer_dashboard_view(request):
    services = wmodels.Services.objects.all()
    
    bookings = Booking.objects.filter(user=request.user)

    payments = models.Payment.objects.filter(booking__in=bookings)

    return render(request, 'consumer/consumer_dashboard.html', {
        'services': services,
        'payments': payments  # Pass payments to the template
    })
def consumer_profile_view(request):
    consumer = models.Consumer.objects.get(user_id=request.user.id)
    return render(request,'consumer/profile.html',{'consumer':consumer})
def search_view(request):
    # Safely get 'query' from GET parameters
    query = request.GET.get('query', '').strip()  # Get and trim the search query
    
    services = []
    if query:
        # Perform a case-insensitive search if query is not empty
        services = wmodels.Services.objects.filter(skills__icontains=query)
    
    # Check for service count in cart
    service_count_in_cart = 0
    service_ids = request.COOKIES.get('service_ids', '')
    if service_ids:
        counter = service_ids.split('|')
        service_count_in_cart = len(set(counter))

    # Message to show in the template
    word = "Searched Result:" if query else "No search query provided"

    # Pass the context to the template
    context = {
        'services': services,
        'word': word,
        'service_count_in_cart': service_count_in_cart
    }

    return render(request, 'consumer/consumer_dashboard.html', context)

from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages

def consumer_address_view(request):
    # Check whether services are present in the cart
    service_in_cart = False
    if 'service_ids' in request.COOKIES:
        service_ids = request.COOKIES['service_ids']
        if service_ids != "":
            service_in_cart = True

    # Count the number of services in the cart
    if 'service_ids' in request.COOKIES:
        service_ids = request.COOKIES['service_ids']
        counter = service_ids.split('|')
        service_count_in_cart = len(set(counter))
    else:
        service_count_in_cart = 0

    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            # Get address data from the form
            name = addressForm.cleaned_data['name']
            mobile = addressForm.cleaned_data['mobile']
            address = addressForm.cleaned_data['address']

            # Save consumer details in the Booking model
            consumer = Booking.objects.create(name=name, mobile=mobile, address=address)

            # Store the consumer ID in session for future use
            request.session['consumer_id'] = consumer.id

            # Calculate total service cost
            total = 0
            if 'service_ids' in request.COOKIES:
                service_ids = request.COOKIES['service_ids']
                if service_ids != "":
                    service_id_in_cart = service_ids.split('|')
                    services = wmodels.Services.objects.filter(id__in=service_id_in_cart)
                    for s in services:
                        total += float(s.service_rate)

            # Proceed to the payment page with the total amount
            response = render(request, 'consumer/payment.html', {'total': total})
            response.set_cookie('name', name)
            response.set_cookie('mobile', mobile)
            response.set_cookie('address', address)
            return response

    return render(request, 'consumer/consumer_address.html', {
        'addressForm': addressForm,
        'service_in_cart': service_in_cart,
        'service_count_in_cart': service_count_in_cart
    })


def payment_success_view(request):
    consumer = models.Consumer.objects.get(id=request.user.id)
    services = None
    name = None
    mobile = None
    address = None

    if 'service_ids' in request.COOKIES:
        service_ids = request.COOKIES['service_ids']
        if service_ids:
            service_id_in_cart = service_ids.split('|')
            services = wmodels.Services.objects.filter(id__in=service_id_in_cart)

    # Accessing customer details from cookies
    if 'name' in request.COOKIES:
        name = request.COOKIES['name']
    if 'mobile' in request.COOKIES:
        mobile = request.COOKIES['mobile']
    if 'address' in request.COOKIES:
        address = request.COOKIES['address']

    # Check if services is not None or empty before iterating
    if services:
        for service in services:
            models.Booking.objects.get_or_create(
                consumer=consumer,
                service=service,
                status='Pending',
                name=name,
                mobile=mobile,
                address=address,
            )

    # Deleting cookies after order is placed
    response = render(request, 'consumer/payment_success.html')
    response.delete_cookie('service_ids')
    response.delete_cookie('name')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response


def my_bookings_view(request):
    # Get the consumer associated with the logged-in user
    consumer = models.Consumer.objects.get(user_id=request.user.id)
    
    # Fetch all bookings for the logged-in consumer
    bookings = models.Booking.objects.filter(consumer=consumer)
    
    booked_services = []
    
    for booking in bookings:
        # Fetch the service associated with each booking
        booked_service = booking.service  # Directly access the service related to the booking
        booked_services.append(booked_service)

    # Zip the booked services and bookings together for rendering
    data = zip(booked_services, bookings)

    return render(request, 'consumer/my_bookings.html', {'data': data})

def delete_booking_from_mybookings(request,pk):
    consumer = models.Consumer.objects.get(user_id=request.user.id)

    # Get the booking object to delete
    booking = get_object_or_404(models.Booking, id=pk, consumer=consumer)

    # Delete the booking
    booking.delete()
    
    # Show a success message
    messages.success(request, "Booking deleted successfully.")

    # Redirect back to the My Bookings page
    return redirect('my-bookings') 


# def customer_address_view(request):
#     # this is for checking whether product is present in cart or not
#     # if there is no product in cart we will not show address form
#     product_in_cart=False
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         if product_ids != "":
#             product_in_cart=True
#     #for counter in cart
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         counter=product_ids.split('|')
#         product_count_in_cart=len(set(counter))
#     else:
#         product_count_in_cart=0

#     addressForm = forms.AddressForm()
#     if request.method == 'POST':
#         addressForm = forms.AddressForm(request.POST)
#         if addressForm.is_valid():
#             # here we are taking address, email, mobile at time of order placement
#             # we are not taking it from customer account table because
#             # these thing can be changes
#             email = addressForm.cleaned_data['Email']
#             mobile=addressForm.cleaned_data['Mobile']
#             address = addressForm.cleaned_data['Address']
#             #for showing total price on payment page.....accessing id from cookies then fetching  price of product from db
#             total=0
#             if 'product_ids' in request.COOKIES:
#                 product_ids = request.COOKIES['product_ids']
#                 if product_ids != "":
#                     product_id_in_cart=product_ids.split('|')
#                     products=models.Product.objects.all().filter(id__in = product_id_in_cart)
#                     print(products)
#                     for p in products:
#                         total=total+p.price

#             response = render(request, 'consumer/payment.html',{'total':total})
#             response.set_cookie('email',email)
#             response.set_cookie('mobile',mobile)
#             response.set_cookie('address',address)
#             return response
#     return render(request,'consumer/consumer_address.html',{'addressForm':addressForm,'product_in_cart':product_in_cart,'product_count_in_cart':product_count_in_cart})




# # here we are just directing to this view...actually we have to check whther payment is successful or not
# #then only this view should be accessed
# def payment_success_view(request):
#     # Here we will place order | after successful payment
#     # we will fetch customer  mobile, address, Email
#     # we will fetch product id from cookies then respective details from db
#     # then we will create order objects and store in db
#     # after that we will delete cookies because after order placed...cart should be empty
#     customer=models.Customer.objects.get(user_id=request.user.id)
#     products=None
#     email=None
#     mobile=None
#     address=None
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         if product_ids != "":
#             product_id_in_cart=product_ids.split('|')
#             products=models.Product.objects.all().filter(id__in = product_id_in_cart)
#             # Here we get products list that will be ordered by one customer at a time

#     # these things can be change so accessing at the time of order...
#     if 'email' in request.COOKIES:
#         email=request.COOKIES['email']
#     if 'mobile' in request.COOKIES:
#         mobile=request.COOKIES['mobile']
#     if 'address' in request.COOKIES:
#         address=request.COOKIES['address']

#     # here we are placing number of orders as much there is a products
#     # suppose if we have 5 items in cart and we place order....so 5 rows will be created in orders table
#     # there will be lot of redundant data in orders table...but its become more complicated if we normalize it
#     for product in products:
#         models.Orders.objects.get_or_create(customer=customer,product=product,status='Pending',email=email,mobile=mobile,address=address)

#     # after order placed cookies should be deleted
#     response = render(request,'consumer/payment_success.html')
#     response.delete_cookie('product_ids')
#     response.delete_cookie('email')
#     response.delete_cookie('mobile')
#     response.delete_cookie('address')
#     return response

from django.shortcuts import render,reverse
from . import forms,models
from django.db.models import Sum,Q
from django.contrib.auth.models import Group
from django.http import HttpResponseRedirect,Http404
from django.contrib.auth.decorators import login_required,user_passes_test
from django.conf import settings
from datetime import date, timedelta
from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from . models import Booking
# Create your views here.

def consumer_signup_view(request):
    userform=forms.ConsumerUserForm()
    consumerform=forms.ConsumerForm()
    mydict={'userform':userform,'consumerform':consumerform}
    if request.method == 'POST':
        userform=forms.ConsumerUserForm(request.POST)
        consumerform=forms.ConsumerForm(request.POST,request.FILES)
        if userform.is_valid() and consumerform.is_valid():
            user=userform.save()
            user.set_password(user.password)
            user.save()
            consumer=consumerform.save(commit=False)
            consumer.user=user
            consumer.save()
            my_consumer_group = Group.objects.get_or_create(name='CONSUMER')
            my_consumer_group[0].user_set.add(user)
        return HttpResponseRedirect('consumerlogin')
    return render(request,'consumer/consumer_signup.html',context=mydict)

def consumer_dashboard_view(request):
    services = wmodels.Services.objects.all()
    return render(request,'consumer/consumer_dashboard.html',{'services':services})


def consumer_profile_view(request):
    consumer = models.Consumer.objects.get(user_id=request.user.id)
    return render(request,'consumer/profile.html',{'consumer':consumer})

def search_view(request):
    query = request.GET['query']
    services = wmodels.Services.objects.all().filter(skills=query)
    if 'service_ids' in request.COOKIES:
        service_ids = request.COOKIES['service_ids']
        counter=service_ids.split('|')
        service_count_in_cart=len(set(counter))
    else:
        service_count_in_cart=0

    # word variable will be shown in html when user click on search button
    word="Searched Result :"

    if request.user.is_authenticated:
        return render(request,'consumer/consumer_dashboard.html',{'services':services,'word':word,'service_count_in_cart':service_count_in_cart})
    return render(request,'consumer/consumer_dashboard.html',{'services':services,'word':word,'service_count_in_cart':service_count_in_cart})




def add_to_cart_view(request, pk):
    services = wmodels.Services.objects.all()
    if 'service_ids' in request.COOKIES:
        service_ids = request.COOKIES['service_ids']
        counter = service_ids.split('|')
        service_count_in_cart = len(set(counter))
    else:
        service_count_in_cart = 0
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('consumerlogin'))
    if 'service_ids' in request.COOKIES:
        service_ids = request.COOKIES['service_ids']
        if service_ids == "":
            service_ids = str(pk)
        else:
            service_ids += "|" + str(pk)
    else:
        service_ids = str(pk)
    response = render(request, 'consumer/consumers_dashboard.html', {
        'services': services,
        'service_count_in_cart': service_count_in_cart + 1 
    })
    response.set_cookie('service_ids', service_ids)
    service = models.Services.objects.get(id=pk)
    print(f"Service added to cart: {service.skills}")  
    return response


def cart_view(request):
    #for cart counter
    if 'service_ids' in request.COOKIES:
        service_ids = request.COOKIES['service_ids']
        counter=service_ids.split('|')
        service_count_in_cart=len(set(counter))
    else:
        service_count_in_cart=0

    # fetching product details from db whose id is present in cookie
    services=None
    total=0
    if 'service_ids' in request.COOKIES:
        service_ids = request.COOKIES['service_ids']
        if service_ids != "":
            service_id_in_cart=service_ids.split('|')
            services=wmodels.Services.objects.all().filter(id__in = service_id_in_cart)

            #for total price shown in cart
            for s in services:
                total += float(s.service_rate)
    return render(request,'consumer/cart.html',{'services':services,'total':total,'service_count_in_cart':service_count_in_cart})

def remove_service_from_cart(request,pk):
    if 'service_ids' in request.COOKIES:

        service_ids = request.COOKIES['service_ids']
        counter=service_ids.split('|')
        service_count_in_cart=len(set(counter))
    else:
        service_count_in_cart=0

    # removing product id from cookie
    total=0
    if 'service_ids' in request.COOKIES:
        service_ids = request.COOKIES['service_ids']
        service_id_in_cart=service_ids.split('|')
        service_id_in_cart=list(set(service_id_in_cart))
        service_id_in_cart.remove(str(pk))
        services=wmodels.Services.objects.all().filter(id__in = service_id_in_cart)
        #for total price shown in cart after removing product
        for s in services:
            total += float(s.service_rate)

        #  for update coookie value after removing product id in cart
        value=""
        for i in range(len(service_id_in_cart)):
            if i==0:
                value=value+service_id_in_cart[0]
            else:
                value=value+"|"+service_id_in_cart[i]
        response = render(request, 'consumer/cart.html',{'services':services,'total':total,'service_count_in_cart':service_count_in_cart})
        if value=="":
            response.delete_cookie('service_ids')
        response.set_cookie('service_ids',value)
        return response
    

# def cart_view(request):
#     #for cart counter
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         counter=product_ids.split('|')
#         product_count_in_cart=len(set(counter))
#     else:
#         product_count_in_cart=0

#     # fetching product details from db whose id is present in cookie
#     products=None
#     total=0
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         if product_ids != "":
#             product_id_in_cart=product_ids.split('|')
#             products=models.Product.objects.all().filter(id__in = product_id_in_cart)

#             #for total price shown in cart
#             for p in products:
#                 total=total+p.price
#     return render(request,'consumer/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})


# def remove_service_from_cart(request,pk):
#     #for counter in cart
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         counter=product_ids.split('|')
#         product_count_in_cart=len(set(counter))
#     else:
#         product_count_in_cart=0

#     # removing product id from cookie
#     total=0
#     if 'product_ids' in request.COOKIES:
#         product_ids = request.COOKIES['product_ids']
#         product_id_in_cart=product_ids.split('|')
#         product_id_in_cart=list(set(product_id_in_cart))
#         product_id_in_cart.remove(str(pk))
#         products=models.Product.objects.all().filter(id__in = product_id_in_cart)
#         #for total price shown in cart after removing product
#         for p in products:
#             total=total+p.price

#         #  for update coookie value after removing product id in cart
#         value=""
#         for i in range(len(product_id_in_cart)):
#             if i==0:
#                 value=value+product_id_in_cart[0]
#             else:
#                 value=value+"|"+product_id_in_cart[i]
#         response = render(request, 'consumer/cart.html',{'products':products,'total':total,'product_count_in_cart':product_count_in_cart})
#         if value=="":
#             response.delete_cookie('product_ids')
#         response.set_cookie('product_ids',value)
#         return response


from django.shortcuts import render, redirect
from . import forms, models as wmodels
from .models import Booking
from django.shortcuts import render, redirect
from . import forms
from .models import Booking, Services  # Ensure to import your models

def consumer_address_view(request):
    # Check whether services are present in the cart
    service_in_cart = 'service_ids' in request.COOKIES and request.COOKIES['service_ids'] != ""
    
    # Count the number of services in the cart
    service_count_in_cart = 0
    if service_in_cart:
        service_ids = request.COOKIES['service_ids']
        counter = service_ids.split('|')
        service_count_in_cart = len(set(counter))

    addressForm = forms.AddressForm()
    if request.method == 'POST':
        addressForm = forms.AddressForm(request.POST)
        if addressForm.is_valid():
            # Get address data from the form
            name = addressForm.cleaned_data['name']
            mobile = addressForm.cleaned_data['mobile']
            address = addressForm.cleaned_data['address']

            # Save consumer details in the Booking model
            consumer = Booking.objects.create(name=name, mobile=mobile, address=address)

            # Store the consumer ID in session for future use
            request.session['consumer_id'] = consumer.id

            # Calculate total service cost
            total = 0
            if service_in_cart:
                service_id_in_cart = request.COOKIES['service_ids'].split('|')
                services = Services.objects.filter(id__in=service_id_in_cart)
                for s in services:
                    total += float(s.service_rate)

            # Set cookies for the consumer details
            response = redirect('payment')  # Assuming 'payment' is the name of the payment URL
            response.set_cookie('name', name)
            response.set_cookie('mobile', mobile)
            response.set_cookie('address', address)

            return response  # Redirect to payment page

        else:
            print(addressForm.errors)  # Log errors for debugging

    return render(request, 'consumer/consumer_address.html', {
        'addressForm': addressForm,
        'service_in_cart': service_in_cart,
        'service_count_in_cart': service_count_in_cart
    })




from django.shortcuts import render, get_object_or_404



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from . import models

@login_required
def payment_success_view(request):
    print(f"Authenticated user: {request.user}")  # Debugging line

    try:
        consumer = get_object_or_404(models.Consumer, user=request.user)
    except ValueError as e:
        print(f"Error retrieving consumer: {e}")  # Debugging line
        return redirect('error-page')  # Redirect to an error page or handle the error

    services = None
    name = request.COOKIES.get('name')
    mobile = request.COOKIES.get('mobile')
    address = request.COOKIES.get('address')

    service_ids = request.COOKIES.get('service_ids')
    if service_ids:
        service_id_in_cart = service_ids.split('|')
        services = wmodels.Services.objects.filter(id__in=service_id_in_cart)

    if services:
        for service in services:
            models.Booking.objects.get_or_create(
                consumer=consumer,
                service=service,
                status='Pending',
                name=name,
                mobile=mobile,
                address=address,
            )

    response = render(request, 'consumer/payment_success.html')
    response.delete_cookie('service_ids')
    response.delete_cookie('name')
    response.delete_cookie('mobile')
    response.delete_cookie('address')
    return response

def my_bookings_view(request):
    consumer = models.Consumer.objects.get(user_id=request.user.id)
    
    # Fetch all bookings for the logged-in consumer
    bookings = models.Booking.objects.filter(consumer=consumer)
    
    booked_services = []
    
    for booking in bookings:
        # Fetch the service associated with each booking
        booked_service = booking.service  # Directly access the service related to the booking
        booked_services.append(booked_service)

    # Zip the booked services and bookings together for rendering
    data = zip(booked_services, bookings)

    return render(request, 'consumer/my_bookings.html', {'data': data})

def payment_view(request):
    return render(request,'consumer/payment.html')


from django.shortcuts import render, get_object_or_404, redirect
from .models import Booking, Payment, Worker, Consumer
from .forms import PaymentForm
from django.contrib.auth.decorators import login_required

def amountpay_view(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.method == "POST":
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.booking = booking
            payment.save()
            return redirect('singlepayment')
    else:
        form = PaymentForm()
    return render(request, 'consumer/amountpay.html', {
        'form': form,
        'booking': booking
    })

def paysuccess_view(request, id):   
    booking = get_object_or_404(Booking, id=id)
    payment = Payment.objects.filter(booking=booking).first()
    if not payment:
        return render(request, 'consumer/success.html', {
            'message': 'No payment details found for this order'
        })
    return render(request, 'consumer/success.html', {
        'payment': payment,
        'booking': booking
    })

@login_required
def view_payment_details(request, user_id):
    payments = Payment.objects.filter(booking__user_id=user_id)
    if not payments.exists():
        return render(request, 'consumer/payment_details.html', {
            'message': 'No payment details found for this user'
        })
    return render(request, 'consumer/payment_details.html', {
        'payments': payments
    })

@login_required
def singlepayment_view(request):
    consumer = get_object_or_404(Consumer, user=request.user)
    user_bookings = Booking.objects.filter(consumer=consumer)
    payments = Payment.objects.filter(booking__in=user_bookings)
    return render(request, 'consumer/singlepayment.html', {
        'payments': payments
    })

@login_required
def worker_payment_details(request, worker_id):
    worker = get_object_or_404(Worker, id=worker_id)
    payments = Payment.objects.filter(worker=worker)
    return render(request, 'worker/payment_details.html', {
        'worker': worker,
        'payments': payments
    })



def chat(request,rec_id):
    if Worker.objects.filter(user=request.user).exists():
            message=Chatmodel.objects.filter(worker__user=request.user,consumer__id=rec_id)
            template='worker/workerchat.html'
    else:
        message=Chatmodel.objects.filter(consumer__user=request.user,worker__id=rec_id)
        template='consumer/chat.html'

    messages_with_dynamic_value = []

    for msg in message:
        messages_with_dynamic_value.append({
            'message': msg,
            'dynamic_value': True if msg.sender==request.user else False
        })
    return render(request,template,{'message':messages_with_dynamic_value,'rec_id':rec_id,})
 


def chat_message(request,receiverid):
    if request.method=='POST':
        message=request.POST.get('message')
        print(request.user)
        user=request.user
        worker=None
        consumer=None
        try:
            worker=Worker.objects.get(user=user)
            print(worker,receiverid,'test')
            consumer=get_object_or_404(Consumer,id=receiverid)
            Chatmodel.objects.create(message=message,worker=worker,consumer=consumer,sender=worker.user)
        except Exception as e:
            print(e,'sadfa')
            consumer=Consumer.objects.get(user=user)
            worker=get_object_or_404(Worker,id=receiverid)
            Chatmodel.objects.create(message=message,worker=worker,consumer=consumer,sender=consumer.user)
    return redirect('chat',rec_id=receiverid)   
     
    