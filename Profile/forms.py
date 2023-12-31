from django import forms
from django.contrib.auth.models import User

class UpdateProfileForm(forms.Form):
    gender_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Prefer not to say', 'Prefer not to say'),
    )
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'first_name', 'name': 'first_name', 'placeholder': 'Enter first name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'last_name', 'name': 'last_name', 'placeholder': 'Enter last name'}))
    gender = forms.ChoiceField(choices=gender_choices, required=True, widget=forms.Select(attrs={'class': 'form-control', 'id': 'gender', 'name': 'gender'}))
    address = forms.CharField(max_length=200, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'address', 'name': 'address', 'placeholder': 'Enter address'}))

