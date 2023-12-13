import re
from django import forms
from django.contrib.auth.models import User


class loginForm(forms.Form):
    username = forms.EmailField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username', 'name': 'username', 'placeholder': 'Enter username'}))
    password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password', 'name': 'password', 'placeholder': 'Enter password'}))

class registerForm(forms.Form):
    gender_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Non-binary', 'Non-binary'),
    )
    email = forms.EmailField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'email', 'name': 'email', 'placeholder': 'Enter email'}))
    password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password', 'name': 'password', 'placeholder': 'Enter password'}))
    confirm_password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'confirm_password', 'name': 'confirm_password', 'placeholder': 'Enter password again'}))
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'first_name', 'name': 'first_name', 'placeholder': 'Enter first name'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'last_name', 'name': 'last_name', 'placeholder': 'Enter last name'}))
    gender = forms.ChoiceField(choices=gender_choices, required=True, widget=forms.Select(attrs={'class': 'form-control', 'id': 'gender', 'name': 'gender'}))
    
    def clean_password(self):
        password = self.cleaned_data.get('password')

        password_regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$')

        if not password_regex.match(password):
            raise forms.ValidationError(
                "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, and one digit."
            )

        return password

class codeForm(forms.Form):
    code = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'code', 'name': 'code', 'placeholder': 'Enter code'}) )


class ChangePassword(forms.ModelForm):
    old_password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'old_password', 'name': 'old_password', 'placeholder': 'Enter old password'}))
    new_password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'new_password', 'name': 'new_password', 'placeholder': 'Enter new password'}))
    confirm_password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'confirm_password', 'name': 'confirm_password', 'placeholder': 'Confirm new password'}))

    class Meta:
        model = User
        fields = ('old_password', 'new_password', 'confirm_password',)

    def clean(self):
        cleaned_data = super(ChangePassword, self).clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError('New password and confirm password do not match.')
        return cleaned_data

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')

        password_regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$')

        if not password_regex.match(new_password):
            raise forms.ValidationError(
                "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, and one digit."
            )

        return new_password