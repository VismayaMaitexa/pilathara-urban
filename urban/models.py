from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, null=False)
    skills = models.CharField(max_length=30, null=False)
    work_experience = models.CharField(max_length=20)
    city = models.CharField(max_length=25, null=False)
    service_rate = models.CharField(max_length=30)
    status = models.CharField(max_length=20, default='Pending')
    profile_pic = models.FileField(
        upload_to='profile_files',
        default='profile_files/default.pdf',
        null=True,
        blank=True
    )
    is_approved = models.BooleanField(default=False)
    @property
    def get_name(self):
        return f"{self.user.first_name} {self.user.last_name}"

    def __str__(self):
        return self.get_name

class Services(models.Model):
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE)
    service_pic = models.ImageField(upload_to='service_pic', null=True, blank=True)
    skills = models.CharField(max_length=40, null=False)
    city = models.CharField(max_length=25)
    service_rate = models.CharField(max_length=25)
    phone = models.PositiveBigIntegerField()

    def __str__(self):
        return f"{self.skills} by {self.worker.get_name}"



# Create your models here.

class Consumer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True, blank=True)  # Optional relationship
    phone = models.CharField(max_length=20, null=False)
    city = models.CharField(max_length=25, null=False)
    profile_pic = models.ImageField(upload_to='profile_pic', null=True, blank=True)
    status = models.CharField(max_length=20,default='Pending')

    def get_name(self):
        return self.user.first_name+" "+self.user.last_name
    
    def __str__(self):
        return self.user.username


class Booking(models.Model):
    STATUS = (
        ('Order Confirmed', 'Order Confirmed'),
        ('Delivered', 'Delivered'),
    )
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE, null=True)
    service = models.ForeignKey(Services, on_delete=models.CASCADE, null=True)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True)  # Add this line
    name = models.CharField(max_length=100, null=True)  # Add this line
    email = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=500, null=True)
    mobile = models.CharField(max_length=20, null=True)
    order_date = models.DateField(auto_now_add=True, null=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS)

# models.py

# models.py
class Payment(models.Model):
    booking = models.ForeignKey('Booking', on_delete=models.CASCADE)  # Link to the booking
    worker = models.ForeignKey('Worker', on_delete=models.CASCADE, null=True)  # Use the worker from the booking
    amount = models.DecimalField(max_digits=10, decimal_places=2)  # Amount paid
    card_number = models.CharField(max_length=16)  # Credit card number (for demo only)
    account_holder_name = models.CharField(max_length=100)  # Account holder name
    cvv = models.CharField(max_length=3)  # CVV code
    expiry_date = models.DateField()  # Expiry date
    status = models.CharField(max_length=20, default='Pending')  # Payment status
    created_at = models.DateTimeField(auto_now_add=True)  # Timestamp

    def __str__(self):
        return f"Payment for {self.booking} - {self.amount}"

    def save(self, *args, **kwargs):
        if not self.worker and self.booking:  # Set worker automatically if not set
            self.worker = self.booking.worker
        super().save(*args, **kwargs)

    def is_paid(self):
        payment = Payment.objects.filter(booking=self.booking, status='Completed').first()
        return payment is not None

class Chatmodel(models.Model):
    message=models.TextField()
    consumer = models.ForeignKey(Consumer, on_delete=models.CASCADE, null=True)
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, null=True) 
    sender=models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)

    def __str__(self):
        return self.consumer.user.username 
