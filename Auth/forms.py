from django import forms

class loginForm(forms.Form):
    username = forms.EmailField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'username', 'name': 'username', 'placeholder': 'Enter username'}))
    password = forms.CharField(max_length=100, required=True, widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'password', 'name': 'password', 'placeholder': 'Enter password'}))

class codeForm(forms.Form):
    code = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'code', 'name': 'code', 'placeholder': 'Enter code'}) )