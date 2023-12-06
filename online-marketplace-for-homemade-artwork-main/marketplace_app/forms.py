import datetime
import re
from typing import Any
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from marketplace_app.models import Login, User, Category, Item, ShippingAddress, Payment, Feedback
import datetime
from django.core.validators import MinLengthValidator, MaxLengthValidator, RegexValidator


class DateInput(forms.DateInput):
    input_type = 'date'


class TimeInput(forms.TimeInput):
    input_type = 'time'


def phone_number_validator(value):
    if not re.compile(r'^[7-9]\d{9}$').match(value):
        raise ValidationError('This is Not a Valid Phone Number')


class LoginRegister(UserCreationForm):
    username = forms.CharField()
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, )
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, )

    class Meta:
        model = Login
        fields = ('username', 'password1', 'password2')


class UserRegister(forms.ModelForm):
    contact_no = forms.CharField(validators=[phone_number_validator])

    class Meta:
        model = User
        fields = ('name', 'contact_no', 'email', 'address',)


class AddCategory(forms.ModelForm):
    class Meta:
        model = Category
        fields = '__all__'


class AddItem(forms.ModelForm):
    class Meta:
        model = Item
        fields = ('product_name', 'price', 'category', 'description', 'instock', 'image',)
        widgets = {
            'image': forms.FileInput(attrs={'class': 'form-control'})
        }
    def clean_instock(self):
        instock = self.cleaned_data.get('instock')
        if instock < 0:
            raise forms.ValidationError("stock cannot be negative.")
        return instock   
    def clean_price(self):
        price = self.cleaned_data.get('price')
        if price is not None and price < 0:
            raise forms.ValidationError("price cannot be negative.")
        return price




class CheckoutForm(forms.ModelForm):
    class Meta:
        model = ShippingAddress
        fields = ('address', 'city', 'district', 'state', 'pincode',)


MONTH_CHOICES = (
    ('January', 'January'),
    ('February ', 'February '),
    ('March ', 'March '),
    ('April ', 'April '),
    ('May ', 'May '),
    ('June ', 'June '),
    ('July ', 'July '),
    ('August ', 'August '),
    ('September ', 'September '),
    ('October ', 'October '),
    ('November ', 'November '),
    ('December ', 'December '),
)



def current_year():
    return datetime.date.today().year

def year_choices():
    return [(r, r) for r in range(2023, datetime.date.today().year + 20)]




class PaymentForm(forms.ModelForm):
    card_no = forms.CharField(validators=[RegexValidator(regex='^.{16}$', message='Please Enter a Valid Card No')])
    card_cvv = forms.CharField(validators=[RegexValidator(regex='^.{3}$', message='Please Enter a Valid CVV')])
    expiry_month = forms.ChoiceField(choices=MONTH_CHOICES)
    expiry_year = forms.TypedChoiceField(coerce=int, choices=year_choices, initial=current_year)

    class Meta:
        model = Payment
        fields = ('card_no', 'card_cvv', 'expiry_month', 'expiry_year')


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ('subject', 'feedback', 'date',)
        widgets = {
            'feedback': forms.Textarea(),
            'date': DateInput(),
        }

    def clean_date(self):
        date = self.cleaned_data['date']

        if date != datetime.date.today():
            raise forms.ValidationError("Invalid Date")
        return date


class UserProfileUpdate(forms.ModelForm):
    contact_no = forms.CharField(validators=[phone_number_validator])

    class Meta:
        model = User
        fields = ('name', 'contact_no', 'email', 'address',)


class AcceptOrder(forms.Form):
    expected_delivery_date = forms.DateField(widget=DateInput)

    def clean_expected_delivery_date(self):
        date = self.cleaned_data['expected_delivery_date']

        if date < datetime.date.today():
            raise forms.ValidationError("Invalid Date")
        return date
