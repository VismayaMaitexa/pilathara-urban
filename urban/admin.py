from django.contrib import admin

from .models import Consumer,Booking,Payment,Worker,Chatmodel

# Register your models here.

admin.site.register(Consumer)
admin.site.register(Booking)
admin.site.register(Payment)
admin.site.register(Worker)
admin.site.register(Chatmodel)
