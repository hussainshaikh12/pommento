from django import forms
from .models import Site
from django.forms import ModelForm


class SiteForm(forms.Form):
    template_name = "core/forms/core.html"
    title = forms.CharField(
        max_length=255,
        label="Site title",
        error_messages={"required": "You need to enter title."},
        help_text="Your site title",
        widget=forms.TextInput(),
        required=True,
    )

class CommetForm(forms.Form):
    template_name = "core/forms/comment-form.html"
    name = forms.CharField(
        max_length=255,
        label="Name",
        error_messages={"required": "You need to enter name."},
        help_text="Enter your name",
        widget=forms.TextInput(),
        required=True,
    )
    email = forms.EmailField(
        label="Email",
        error_messages={"required": "You need to enter email."},
        help_text="Enter your email",
        widget=forms.EmailInput(),
        required=True,
    )
    comment = forms.CharField(
        help_text="Enter your comment",
        widget=forms.Textarea(),
        required=True,
    )