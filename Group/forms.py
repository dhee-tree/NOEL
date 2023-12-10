from django import forms
from .models import SantaGroup

class createGroup(forms.ModelForm):
    class Meta:
        model = SantaGroup
        fields = ['group_name']
        widgets = {
            'group_name': forms.TextInput(attrs={'class': 'form-control', 'id': 'group_name', 'name': 'group_name', 'placeholder': 'Enter group name'}),
        }

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form) 