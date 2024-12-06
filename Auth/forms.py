import re
from django import forms
from django.contrib.auth.models import User

passwordLength = 15
emailLength = 50
nameLength = 50
addressLength = 200
password_regex = re.compile(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d).{8,}$')


class loginForm(forms.Form):
    email = forms.EmailField(max_length=emailLength, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'email', 'name': 'email', 'placeholder': 'Enter email'}))
    password = forms.CharField(max_length=passwordLength, required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'password', 'name': 'password', 'placeholder': 'Enter password'}))
    
    class Meta:
        model = User
        fields = ('email',)

    def clean(self):
        return super(loginForm, self).clean()

class registerForm(forms.Form):
    gender_choices = (
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Prefer not to say', 'Prefer not to say'),
    )
    email = forms.EmailField(max_length=emailLength, required=True, widget=forms.TextInput(attrs={
                             'class': 'form-control', 'id': 'email', 'name': 'email', 'placeholder': 'Enter email'}))
    password = forms.CharField(max_length=passwordLength, required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'password', 'name': 'password', 'placeholder': 'Enter password'}))
    confirm_password = forms.CharField(max_length=passwordLength, required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'confirm_password', 'name': 'confirm_password', 'placeholder': 'Enter password again'}))
    first_name = forms.CharField(max_length=nameLength, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'first_name', 'name': 'first_name', 'placeholder': 'Enter first name'}))
    last_name = forms.CharField(max_length=nameLength, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'last_name', 'name': 'last_name', 'placeholder': 'Enter last name'}))
    gender = forms.ChoiceField(choices=gender_choices, required=True, widget=forms.Select(
        attrs={'class': 'form-control', 'id': 'gender', 'name': 'gender'}))
    address = forms.CharField(max_length=addressLength, required=True, widget=forms.TextInput(
        attrs={'class': 'form-control', 'id': 'address', 'name': 'address', 'placeholder': 'Enter address'}))

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if not password_regex.match(password):
            raise forms.ValidationError(
                "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, and one digit."
            )

        return password


class codeForm(forms.Form):
    code = forms.CharField(max_length=8, required=True, widget=forms.TextInput(attrs={
                           'class': 'form-control', 'id': 'code', 'name': 'code', 'placeholder': 'Enter code'}))


class ChangePassword(forms.ModelForm):
    old_password = forms.CharField(max_length=passwordLength, required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'old_password', 'name': 'old_password', 'placeholder': 'Enter old password'}))
    new_password = forms.CharField(max_length=passwordLength, required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'new_password', 'name': 'new_password', 'placeholder': 'Enter new password'}))
    confirm_password = forms.CharField(max_length=passwordLength, required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'confirm_password', 'name': 'confirm_password', 'placeholder': 'Confirm new password'}))

    class Meta:
        model = User
        fields = ('old_password', 'new_password', 'confirm_password',)

    def clean(self):
        cleaned_data = super(ChangePassword, self).clean()
        new_password = cleaned_data.get('new_password')
        confirm_password = cleaned_data.get('confirm_password')
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise forms.ValidationError(
                    'New password and confirm password do not match.')
        return cleaned_data

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')

        if not password_regex.match(new_password):
            raise forms.ValidationError(
                "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, and one digit."
            )

        return new_password


class ResetPasswordForm(forms.ModelForm):
    email = forms.EmailField(max_length=emailLength, required=True, widget=forms.TextInput(attrs={
                             'class': 'form-control', 'id': 'email', 'name': 'email', 'placeholder': 'Enter email'}))

    class Meta:
        model = User
        fields = ('email',)

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        return cleaned_data


class NewPasswordForm(forms.Form):
    password = forms.CharField(max_length=passwordLength, required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'password', 'name': 'password', 'placeholder': 'Enter new password'}))
    confirm_password = forms.CharField(max_length=passwordLength, required=True, widget=forms.PasswordInput(
        attrs={'class': 'form-control', 'id': 'confirm_password', 'name': 'confirm_password', 'placeholder': 'Confirm new password'}))

    def check_password(self):
        cleaned_data = super(NewPasswordForm, self).clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        if password and confirm_password:
            if password != confirm_password:
                return False
        return cleaned_data

    def clean_password(self):
        if not password_regex.match(self.cleaned_data.get('password')):
            raise forms.ValidationError(
                "Password must be at least 8 characters long and include at least one uppercase letter, one lowercase letter, and one digit."
            )
        return self.cleaned_data.get('password')
