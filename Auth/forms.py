from django import forms

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
    

class codeForm(forms.Form):
    code = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'code', 'name': 'code', 'placeholder': 'Enter code'}) )