from django import forms
from django.contrib.auth.models import User

class UpdateProfileForm(forms.Form):
    gender_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Non-binary', 'Non-binary'),
    )
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'first_name', 'name': 'first_name', 'placeholder': 'Enter first name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'last_name', 'name': 'last_name', 'placeholder': 'Enter last name'}))
    gender = forms.ChoiceField(choices=gender_choices, required=True, widget=forms.Select(attrs={'class': 'form-control', 'id': 'gender', 'name': 'gender'}))

