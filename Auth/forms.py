from django import forms

class codeForm(forms.Form):
    code = forms.CharField(max_length=6, required=True, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'code', 'name': 'code', 'placeholder': 'Enter code'}) )