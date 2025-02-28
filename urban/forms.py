from django import forms
from django.contrib.auth.models import User
from . import models


class WorkerUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','username','password']
        widgets = {
            'password':forms.PasswordInput()
        }

class WorkerForm(forms.ModelForm):
    class Meta:
        model=models.Worker
        fields=['phone','skills','work_experience','city','service_rate','profile_pic']


class ServiceForm(forms.ModelForm):
    class Meta:
        model=models.Services
        fields=['service_pic','skills','city','service_rate','phone']

from django import forms
from django.contrib.auth.models import User
from . import models

class ConsumerUserForm(forms.ModelForm):
    class Meta:
        model=User
        fields=['first_name','last_name','username','password']
        widgets= {
            'password':forms.PasswordInput()
        }

class ConsumerForm(forms.ModelForm):
    class Meta:
        model=models.Consumer
        fields=['profile_pic','phone','city']









class AddressForm(forms.Form):
    name = forms.CharField(max_length=30, required=True)
    mobile = forms.CharField(max_length=10, required=True)  # Change to CharField
    address = forms.CharField(max_length=500, required=True)

# forms.py

from django import forms
from .models import Payment

# class PaymentForm(forms.ModelForm):
#     class Meta:
#         model = Payment
#         fields = ['amount', 'card_number', 'account_holder_name', 'cvv', 'expiry_date','worker']
#         widgets = {
#             'amount': forms.NumberInput(attrs={'placeholder': 'Amount'}),
#             'card_number': forms.TextInput(attrs={'placeholder': 'Card Number'}),
#             'account_holder_name': forms.TextInput(attrs={'placeholder': 'Account Holder Name'}),
#             'cvv': forms.PasswordInput(attrs={'placeholder': 'CVV'}),
#             'expiry_date': forms.DateInput(attrs={'placeholder': 'Expiry Date (YYYY-MM-DD)', 'type': 'date'}),
#         }


from .models import Payment, Booking

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['booking', 'amount', 'card_number', 'account_holder_name', 'cvv', 'expiry_date']

    def __init__(self, *args, **kwargs):
        super(PaymentForm, self).__init__(*args, **kwargs)
        if self.instance and self.instance.booking:
            self.fields['worker'].initial = self.instance.booking.worker
