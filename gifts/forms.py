import logging

from django import forms
from django.contrib.auth.forms import PasswordResetForm

from .models import Wish

logger = logging.getLogger(__name__)


class WishForm(forms.ModelForm):
    class Meta:
        model = Wish
        fields = ["title", "detail", "link"]
        labels = {
            "title": "Title *",
        }  # Overrides the default label for the title field to add an asterisk to mark it as required
        widgets = {
            "title": forms.TextInput(
                attrs={"placeholder": "Enter the title of your wish", "required": "required"}
            ),
            "detail": forms.Textarea(
                attrs={"placeholder": "Give a bit more detail about your wish"}
            ),
            "link": forms.TextInput(attrs={"placeholder": "Enter a link to your wish"}),
        }


class DeleteWishConfirmationForm(forms.Form):
    pass

class LoggingPasswordResetForm(PasswordResetForm):
    def save(self, *args, **kwargs):
        email = self.cleaned_data["email"]
        logger.info("password_reset.request_received email=%s", email)

        try:
            result = super().save(*args, **kwargs)
        except Exception:
            logger.exception("password_reset.processing_failed email=%s", email)
            raise

        logger.info("password_reset.request_processed email=%s", email)
        return result
    
