from django import forms

from .models import ContactMessage


class ContactForm(forms.ModelForm):
    # honeypot
    # Humans never see this field. Simple form-filling bots often complete every
    # input they find, which lets us discard those submissions without a CAPTCHA.
    website = forms.CharField(
        required=False,
        label="",
        widget=forms.HiddenInput(attrs={"autocomplete": "off", "tabindex": "-1"}),
    )

    class Meta:
        model = ContactMessage
        fields = ["name", "email", "message"]
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "placeholder": "Your name",
                    "autocomplete": "name",
                    "maxlength": "100",
                }
            ),
            "email": forms.EmailInput(
                attrs={
                    "placeholder": "you@example.com",
                    "autocomplete": "email",
                }
            ),
            "message": forms.Textarea(
                attrs={
                    "placeholder": "What would you like to talk about?",
                    "rows": 6,
                    "maxlength": "5000",
                }
            ),
        }

    def clean_website(self):
        value = self.cleaned_data.get("website", "")
        if value:
            raise forms.ValidationError("Please try submitting the form again.")
        return value

    def clean_message(self):
        message = self.cleaned_data["message"].strip()
        if len(message) > 5000:
            raise forms.ValidationError("Please keep your message under 5000 characters.")
        return message
