from django import forms


class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'name', 'name': 'name', 'placeholder': 'Enter your name.'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'id': 'email', 'name': 'email', 'placeholder': 'Enter your email address.'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 5, 'cols': 20, 'class': 'form-control', 'id': 'message', 'name': 'message', 'placeholder': 'Enter your message here.', 'required': True}))

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)
