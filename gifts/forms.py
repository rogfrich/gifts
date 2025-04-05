from django import forms
from .models import Wish

class WishForm(forms.ModelForm):
    class Meta:
        model = Wish
        fields = ['title', 'detail', 'link']
        widgets = {
            'title': forms.TextInput(attrs={'placeholder': 'Enter the title of your wish'}),
            'detail': forms.Textarea(attrs={'placeholder': 'Give a bit more detail about your wish'}),
            'link': forms.TextInput(attrs={'placeholder': 'Enter a link to your wish'}),
        }

class DeleteWishConfirmationForm(forms.Form):
    pass